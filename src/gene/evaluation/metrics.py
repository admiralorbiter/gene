"""Hardened metrics engine for target-specific accuracy, path-level lineage, and unconfounded causal rates."""

from __future__ import annotations

import json
from typing import Any
from pydantic import BaseModel, Field
from gene.persistence.db import Database


class Exp0Metrics(BaseModel):
    """Aggregate metrics for Experiment 0 lineage observability and causal validation."""
    total_calls: int = 0
    total_claims: int = 0
    structured_output_success_rate: float = 0.0
    task_truth_accuracy: float = 0.0
    reported_lineage_precision: float = 0.0
    reported_lineage_recall: float = 0.0
    reported_parent_necessity_rate: float = 0.0
    unreported_required_causal_rate: float = 0.0
    unreported_distractor_influence_rate: float = 0.0
    noop_instability_rate: float = 0.0
    causal_tests_indeterminate_rate: float = 0.0
    avg_latency_ms: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    raw_counts: dict[str, Any] = Field(default_factory=dict)

    @property
    def causal_validation_rate(self) -> float:
        """Alias for reported_parent_necessity_rate."""
        return self.reported_parent_necessity_rate

    @property
    def hidden_causal_parent_rate(self) -> float:
        """Alias for unreported_required_causal_rate."""
        return self.unreported_required_causal_rate


class MetricsCalculator:
    """Computes target-specific accuracy, path-level recall, precision, and separated causal metrics."""

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

        # 4. Causal Metrics (Separate Denominators & Controls)
        all_causal_tests = db.conn.execute(
            """
            SELECT ct.*, c.request_json, cl.oracle_evidence_json
            FROM causal_tests ct
            JOIN calls c ON ct.original_call_id = c.call_id
            LEFT JOIN claims cl ON ct.child_node_id = cl.node_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()

        reported_pairs = {
            (r["parent_node_id"], r["child_node_id"]) for r in reported_edges
        }

        # 4a. No-op (sham) instability rate S0
        noop_tests = [t for t in all_causal_tests if t["intervention_type"] == "noop"]
        noop_unstable_count = sum(1 for t in noop_tests if t["outcome"] in ("strong", "partial"))
        noop_instability = (
            noop_unstable_count / len(noop_tests) if noop_tests else 0.0
        )

        # 4b. Non-noop tests
        intervention_tests = [t for t in all_causal_tests if t["intervention_type"] != "noop"]

        tested_reported_count = 0
        validated_reported_count = 0

        tested_unreported_required_count = 0
        validated_unreported_required_count = 0

        tested_distractor_count = 0
        hidden_distractor_causal_count = 0

        indeterminate_count = 0

        for ct in intervention_tests:
            outcome = ct["outcome"]
            pair = (ct["parent_node_id"], ct["child_node_id"])

            if outcome == "indeterminate":
                indeterminate_count += 1
                continue

            ev = json.loads(ct["oracle_evidence_json"]) if ct["oracle_evidence_json"] else {}
            valid_paths = ev.get("valid_support_paths", [])
            is_required_parent = any(ct["parent_node_id"] in path for path in valid_paths)

            if pair in reported_pairs:
                # Reported parent test -> Counterfactual necessity
                tested_reported_count += 1
                if outcome in ("strong", "partial"):
                    validated_reported_count += 1
            elif is_required_parent:
                # Unreported required parent test -> True Hidden Causal Parent (HR)
                tested_unreported_required_count += 1
                if outcome in ("strong", "partial"):
                    validated_unreported_required_count += 1
            else:
                # Unreported distractor test -> Distractor influence control (HD)
                tested_distractor_count += 1
                if outcome in ("strong", "partial"):
                    hidden_distractor_causal_count += 1

        rep_necessity_rate = (
            validated_reported_count / tested_reported_count if tested_reported_count > 0 else 0.0
        )
        unrep_required_rate = (
            validated_unreported_required_count / tested_unreported_required_count if tested_unreported_required_count > 0 else 0.0
        )
        distractor_influence_rate = (
            hidden_distractor_causal_count / tested_distractor_count if tested_distractor_count > 0 else 0.0
        )
        total_interventions = len(intervention_tests)
        indet_rate = (
            indeterminate_count / total_interventions if total_interventions > 0 else 0.0
        )

        return Exp0Metrics(
            total_calls=total_calls,
            total_claims=total_claims,
            structured_output_success_rate=struct_success_rate,
            task_truth_accuracy=task_truth_acc,
            reported_lineage_precision=precision,
            reported_lineage_recall=lineage_recall,
            reported_parent_necessity_rate=rep_necessity_rate,
            unreported_required_causal_rate=unrep_required_rate,
            unreported_distractor_influence_rate=distractor_influence_rate,
            noop_instability_rate=noop_instability,
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
                "tested_unreported_required_parents": tested_unreported_required_count,
                "validated_unreported_required_parents": validated_unreported_required_count,
                "tested_unreported_distractors": tested_distractor_count,
                "distractor_causal_influence_count": hidden_distractor_causal_count,
                "total_noop_tests": len(noop_tests),
                "unstable_noop_tests": noop_unstable_count,
                "indeterminate_causal_tests": indeterminate_count,
            },
        )
