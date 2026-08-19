"""Metrics calculations for Experiment 0 (Lineage Observability) and Experiment 1."""

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
    """Computes lineage precision, recall, causal support rates, and execution statistics."""

    @classmethod
    def compute_exp0_metrics(cls, db: Database, run_id: str) -> Exp0Metrics:
        """Calculate complete Experiment 0 metrics from SQLite tables."""
        # 1. Calls and token stats
        calls = db.conn.execute("SELECT * FROM calls WHERE run_id = ?", (run_id,)).fetchall()
        total_calls = len(calls)
        latencies = [c["latency_ms"] for c in calls if c["latency_ms"] is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        tot_prompt_tokens = sum(c["prompt_tokens"] or 0 for c in calls)
        tot_comp_tokens = sum(c["completion_tokens"] or 0 for c in calls)

        # 2. Claims and parsing stats
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
        true_claims = [c for c in claims if c["truth_status"] == "true"]
        struct_success_rate = len(success_claims) / total_claims if total_claims > 0 else 0.0
        truth_acc = len(true_claims) / total_claims if total_claims > 0 else 0.0

        # 3. Lineage Precision & Recall
        # Fetch reported edges and compare against oracle_evidence_json in claims
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

        # Also track oracle required edges
        oracle_required_edges_set = set()
        reported_edges_set = set()

        for r in reported_edges:
            p_id = r["parent_node_id"]
            c_id = r["child_node_id"]
            reported_edges_set.add((p_id, c_id))

            ev = json.loads(r["oracle_evidence_json"]) if r["oracle_evidence_json"] else {}
            valid_paths = ev.get("valid_support_paths", [])

            # Check if p_id appears in any valid support path
            is_valid = any(p_id in path for path in valid_paths)
            if is_valid:
                valid_reported_edges += 1

            for path in valid_paths:
                for req_p in path:
                    oracle_required_edges_set.add((req_p, c_id))

        precision = (
            valid_reported_edges / total_reported_edges if total_reported_edges > 0 else 1.0
        )

        matched_required = sum(
            1 for edge in oracle_required_edges_set if edge in reported_edges_set
        )
        recall = (
            matched_required / len(oracle_required_edges_set)
            if oracle_required_edges_set
            else 1.0
        )

        # 4. Causal validation rates
        causal_tests = db.conn.execute(
            """
            SELECT ct.* FROM causal_tests ct
            JOIN calls c ON ct.original_call_id = c.call_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()

        total_causal = len(causal_tests)
        strong_or_partial = 0
        hidden_causal = 0
        indeterminate = 0

        for ct in causal_tests:
            outcome = ct["outcome"]
            parent_id = ct["parent_node_id"]
            child_id = ct["child_node_id"]

            if outcome == "indeterminate":
                indeterminate += 1
            elif outcome in ("strong", "partial"):
                if (parent_id, child_id) in reported_edges_set:
                    strong_or_partial += 1
                else:
                    hidden_causal += 1

        causal_val_rate = (
            strong_or_partial / total_causal if total_causal > 0 else 0.0
        )
        hidden_rate = (
            hidden_causal / total_causal if total_causal > 0 else 0.0
        )
        indet_rate = (
            indeterminate / total_causal if total_causal > 0 else 0.0
        )

        return Exp0Metrics(
            total_calls=total_calls,
            total_claims=total_claims,
            structured_output_success_rate=struct_success_rate,
            task_truth_accuracy=truth_acc,
            reported_lineage_precision=precision,
            reported_lineage_recall=recall,
            causal_validation_rate=causal_val_rate,
            hidden_causal_parent_rate=hidden_rate,
            causal_tests_indeterminate_rate=indet_rate,
            avg_latency_ms=avg_latency,
            total_prompt_tokens=tot_prompt_tokens,
            total_completion_tokens=tot_comp_tokens,
            raw_counts={
                "total_reported_edges": total_reported_edges,
                "valid_reported_edges": valid_reported_edges,
                "oracle_required_edges": len(oracle_required_edges_set),
                "matched_required_edges": matched_required,
                "total_causal_tests": total_causal,
                "strong_or_partial_causal": strong_or_partial,
                "hidden_causal": hidden_causal,
                "indeterminate_causal": indeterminate,
            },
        )
