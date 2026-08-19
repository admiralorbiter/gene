"""Hardened metrics engine for target-specific accuracy, path-level lineage, and unconfounded causal rates."""

from __future__ import annotations

import json
from typing import Any
from pydantic import BaseModel, Field
from gene.persistence.db import Database


class Exp0Metrics(BaseModel):
    """Aggregate metrics for Experiment 0 lineage observability."""
    total_calls: int = 0
    total_claims: int = 0
    structured_output_success_rate: float = 0.0
    task_truth_accuracy: float = 0.0
    reported_lineage_precision: float = 0.0
    reported_lineage_recall: float = 0.0
    causal_validation_rate: float = 0.0
    hidden_causal_parent_rate: float = 0.0
    causal_tests_indeterminate_rate: float = 0.0
    avg_latency_ms: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    raw_counts: dict[str, Any] = Field(default_factory=dict)


class MetricsCalculator:
    """Computes target-specific accuracy, path-level recall, precision, and unconfounded causal support rates."""

    @classmethod
    def compute_exp0_metrics(cls, db: Database, run_id: str) -> Exp0Metrics:
        """Calculate complete Experiment 0 metrics from SQLite tables with strict scientific definitions."""
        # 1. Calls and token stats
        calls = db.conn.execute("SELECT * FROM calls WHERE run_id = ?", (run_id,)).fetchall()
        total_calls = len(calls)
        latencies = [c["latency_ms"] for c in calls if c["latency_ms"] is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        tot_prompt_tokens = sum(c["prompt_tokens"] or 0 for c in calls)
        tot_comp_tokens = sum(c["completion_tokens"] or 0 for c in calls)

        # 2. Claims and target-specific accuracy
        claims = db.conn.execute(
            """
            SELECT c.* FROM claims c
            JOIN memory_nodes m ON c.node_id = m.node_id
            WHERE m.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        total_claims = len(claims)

        success_claims = [c for c in claims if c["parse_status"] == "success"]
        struct_success_rate = len(success_claims) / total_claims if total_claims > 0 else 0.0

        # Target-specific truth evaluation
        target_correct_count = 0
        task_recalls: list[float] = []

        for cl in claims:
            ev = json.loads(cl["oracle_evidence_json"]) if cl["oracle_evidence_json"] else {}
            target_subj = ev.get("target_subject")
            target_pred = ev.get("target_predicate")
            target_obj = ev.get("target_object")

            if (
                cl["parse_status"] == "success"
                and cl["truth_status"] == "true"
                and cl["subject"] == target_subj
                and cl["predicate"] == target_pred
                and cl["object"] == target_obj
            ):
                target_correct_count += 1

            # Path-level recall calculation for this claim
            valid_paths = ev.get("valid_support_paths", [])
            # Fetch reported parent IDs for this node
            reported_rows = db.conn.execute(
                "SELECT parent_node_id FROM reported_support_edges WHERE child_node_id = ?",
                (cl["node_id"],),
            ).fetchall()
            reported_ids = {r["parent_node_id"] for r in reported_rows}

            if not valid_paths:
                task_recalls.append(1.0 if not reported_ids else 0.0)
            else:
                best_path_recall = 0.0
                for path in valid_paths:
                    if not path:
                        best_path_recall = max(best_path_recall, 1.0)
                    else:
                        covered = len(set(path) & reported_ids)
                        best_path_recall = max(best_path_recall, covered / len(path))
                task_recalls.append(best_path_recall)

        task_truth_acc = target_correct_count / total_claims if total_claims > 0 else 0.0
        lineage_recall = sum(task_recalls) / len(task_recalls) if task_recalls else 1.0

        # 3. Lineage Precision
        reported_edges = db.conn.execute(
            """
            SELECT r.parent_node_id, r.child_node_id, c.oracle_evidence_json
            FROM reported_support_edges r
            JOIN claims c ON r.child_node_id = c.node_id
            JOIN memory_nodes m ON c.node_id = m.node_id
            WHERE m.run_id = ?
            """,
            (run_id,),
        ).fetchall()

        total_reported_edges = len(reported_edges)
        valid_reported_edges = 0

        for r in reported_edges:
            p_id = r["parent_node_id"]
            ev = json.loads(r["oracle_evidence_json"]) if r["oracle_evidence_json"] else {}
            valid_paths = ev.get("valid_support_paths", [])
            is_valid = any(p_id in path for path in valid_paths)
            if is_valid:
                valid_reported_edges += 1

        precision = (
            valid_reported_edges / total_reported_edges if total_reported_edges > 0 else 1.0
        )

        # 4. Unconfounded Causal Validation Rates (Separate Denominators)
        # Fetch all causal tests for this run
        causal_tests = db.conn.execute(
            """
            SELECT ct.*, c.request_json
            FROM causal_tests ct
            JOIN calls c ON ct.original_call_id = c.call_id
            WHERE c.run_id = ? AND ct.intervention_type != 'noop'
            """,
            (run_id,),
        ).fetchall()

        # Fetch set of reported pairs
        reported_pairs = {
            (r["parent_node_id"], r["child_node_id"]) for r in reported_edges
        }

        tested_reported_count = 0
        validated_reported_count = 0

        tested_distractor_count = 0
        hidden_causal_count = 0

        indeterminate_count = 0

        for ct in causal_tests:
            outcome = ct["outcome"]
            pair = (ct["parent_node_id"], ct["child_node_id"])

            if outcome == "indeterminate":
                indeterminate_count += 1
                continue

            if pair in reported_pairs:
                tested_reported_count += 1
                if outcome in ("strong", "partial"):
                    validated_reported_count += 1
            else:
                tested_distractor_count += 1
                if outcome in ("strong", "partial"):
                    hidden_causal_count += 1

        causal_val_rate = (
            validated_reported_count / tested_reported_count if tested_reported_count > 0 else 0.0
        )
        hidden_causal_rate = (
            hidden_causal_count / tested_distractor_count if tested_distractor_count > 0 else 0.0
        )
        total_tested = len(causal_tests)
        indet_rate = (
            indeterminate_count / total_tested if total_tested > 0 else 0.0
        )

        return Exp0Metrics(
            total_calls=total_calls,
            total_claims=total_claims,
            structured_output_success_rate=struct_success_rate,
            task_truth_accuracy=task_truth_acc,
            reported_lineage_precision=precision,
            reported_lineage_recall=lineage_recall,
            causal_validation_rate=causal_val_rate,
            hidden_causal_parent_rate=hidden_causal_rate,
            causal_tests_indeterminate_rate=indet_rate,
            avg_latency_ms=avg_latency,
            total_prompt_tokens=tot_prompt_tokens,
            total_completion_tokens=tot_comp_tokens,
            raw_counts={
                "total_reported_edges": total_reported_edges,
                "valid_reported_edges": valid_reported_edges,
                "target_correct_claims": target_correct_count,
                "tested_reported_parents": tested_reported_count,
                "validated_reported_parents": validated_reported_count,
                "tested_unreported_distractors": tested_distractor_count,
                "hidden_causal_distractors": hidden_causal_count,
                "indeterminate_causal_tests": indeterminate_count,
            },
        )
