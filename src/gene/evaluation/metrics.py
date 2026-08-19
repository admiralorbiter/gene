"""Hardened metrics engine for target-specific accuracy, path-level lineage, and unconfounded causal rates."""

from __future__ import annotations

import json
from typing import Any
from pydantic import BaseModel, Field
from gene.persistence.db import Database


def format_rate(val: float | None) -> str:
    """Format a float rate as a percentage or 'N/A' if None."""
    if val is None:
        return "N/A"
    return f"{val:.2%}"


class Exp0StratifiedMetrics(BaseModel):
    """Metrics stratified by reasoning depth (D0, D1, or combined)."""
    reasoning_depth: int | None = None
    total_claims: int = 0
    structured_output_success_rate: float | None = 0.0
    task_truth_accuracy: float | None = 0.0
    reported_lineage_precision: float | None = 0.0
    reported_lineage_recall: float | None = 0.0

    # Causal necessity (Cnec) on reported parents
    reported_parents_attempted: int = 0
    reported_parents_determinate: int = 0
    reported_parents_indeterminate: int = 0
    reported_parents_validated: int = 0
    reported_parent_necessity_rate_determinate: float | None = None
    reported_parent_necessity_rate_conservative: float | None = None

    # Hidden required causality (HR)
    unreported_required_attempted: int = 0
    unreported_required_determinate: int = 0
    unreported_required_indeterminate: int = 0
    unreported_required_validated: int = 0
    unreported_required_causal_rate_determinate: float | None = None
    unreported_required_causal_rate_conservative: float | None = None

    # Distractor influence (HD)
    distractors_attempted: int = 0
    distractors_determinate: int = 0
    distractors_indeterminate: int = 0
    distractors_validated: int = 0
    unreported_distractor_influence_rate_determinate: float | None = None
    unreported_distractor_influence_rate_conservative: float | None = None

    # No-op (sham) baseline instability (S0)
    noop_attempted: int = 0
    noop_unstable_count: int = 0
    noop_parse_failed_count: int = 0
    noop_answer_shifted_count: int = 0
    noop_instability_rate: float | None = None

    # Indeterminates summary in this stratum
    total_causal_tests: int = 0
    total_indeterminate_tests: int = 0
    causal_tests_indeterminate_rate: float | None = None

    @property
    def reported_parent_necessity_rate(self) -> float:
        """Alias for determinate necessity rate, defaulting to 0.0 if empty."""
        return self.reported_parent_necessity_rate_determinate if self.reported_parent_necessity_rate_determinate is not None else 0.0

    @property
    def unreported_required_causal_rate(self) -> float:
        """Alias for determinate HR rate, defaulting to 0.0 if empty."""
        return self.unreported_required_causal_rate_determinate if self.unreported_required_causal_rate_determinate is not None else 0.0

    @property
    def unreported_distractor_influence_rate(self) -> float:
        """Alias for determinate HD rate, defaulting to 0.0 if empty."""
        return self.unreported_distractor_influence_rate_determinate if self.unreported_distractor_influence_rate_determinate is not None else 0.0


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

    # Top-level direct counts
    total_causal_tests: int = 0
    total_noop_tests: int = 0
    total_reported_parent_tests: int = 0
    total_unreported_required_tests: int = 0
    total_distractor_tests: int = 0
    total_indeterminate_tests: int = 0

    # Stratified metrics
    d0: Exp0StratifiedMetrics | None = None
    d1: Exp0StratifiedMetrics | None = None
    overall: Exp0StratifiedMetrics | None = None

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
    def _compute_stratum(
        cls,
        claims: list[dict[str, Any]],
        reported_edges: list[dict[str, Any]],
        causal_tests: list[dict[str, Any]],
        reasoning_depth: int | None = None,
    ) -> Exp0StratifiedMetrics:
        """Calculate metrics for a specific subset of claims and their causal tests."""
        total_claims = len(claims)
        if total_claims == 0:
            return Exp0StratifiedMetrics(reasoning_depth=reasoning_depth)

        # 1. Structure & Truth Accuracy
        success_claims = [c for c in claims if c["parse_status"] == "success"]
        struct_success_rate = len(success_claims) / total_claims if total_claims > 0 else None

        target_correct_count = 0
        task_recalls: list[float] = []

        claim_ids = {c["node_id"] for c in claims}
        edges_for_stratum = [r for r in reported_edges if r["child_node_id"] in claim_ids]
        reported_by_child: dict[str, set[str]] = {}
        for r in edges_for_stratum:
            reported_by_child.setdefault(r["child_node_id"], set()).add(r["parent_node_id"])

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

            valid_paths = ev.get("valid_support_paths", [])
            reported_ids = reported_by_child.get(cl["node_id"], set())

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

        task_truth_acc = target_correct_count / total_claims if total_claims > 0 else None
        lineage_recall = sum(task_recalls) / len(task_recalls) if task_recalls else None

        # 2. Precision
        total_reported_edges = len(edges_for_stratum)
        valid_reported_edges = 0
        for r in edges_for_stratum:
            p_id = r["parent_node_id"]
            ev = json.loads(r["oracle_evidence_json"]) if r["oracle_evidence_json"] else {}
            valid_paths = ev.get("valid_support_paths", [])
            if any(p_id in path for path in valid_paths):
                valid_reported_edges += 1

        precision = (
            valid_reported_edges / total_reported_edges if total_reported_edges > 0 else 1.0
        )

        # 3. Causal Interventions Categorized First
        reported_pairs = {
            (r["parent_node_id"], r["child_node_id"]) for r in edges_for_stratum
        }

        tests_for_stratum = [t for t in causal_tests if t["child_node_id"] in claim_ids]

        # Category counters
        rep_attempted = 0
        rep_determinate = 0
        rep_indeterminate = 0
        rep_validated = 0

        unrep_req_attempted = 0
        unrep_req_determinate = 0
        unrep_req_indeterminate = 0
        unrep_req_validated = 0

        dist_attempted = 0
        dist_determinate = 0
        dist_indeterminate = 0
        dist_validated = 0

        noop_attempted = 0
        noop_unstable = 0
        noop_parse_failed = 0
        noop_answer_shifted = 0

        total_indet_count = 0

        for ct in tests_for_stratum:
            intervention_type = ct["intervention_type"]
            outcome = ct["outcome"]
            pair = (ct["parent_node_id"], ct["child_node_id"])
            details = json.loads(ct["comparison_json"]) if ct.get("comparison_json") else {}

            if intervention_type == "noop":
                noop_attempted += 1
                if outcome in ("strong", "partial"):
                    noop_unstable += 1
                    reason = details.get("instability_reason", "")
                    if "parse_failure" in reason:
                        noop_parse_failed += 1
                    else:
                        noop_answer_shifted += 1
                continue

            # Identify category first
            ev = json.loads(ct["oracle_evidence_json"]) if ct.get("oracle_evidence_json") else {}
            valid_paths = ev.get("valid_support_paths", [])
            is_required_parent = any(ct["parent_node_id"] in path for path in valid_paths)

            if pair in reported_pairs:
                cat = "reported"
            elif is_required_parent:
                cat = "unreported_required"
            else:
                cat = "distractor"

            # Check outcome
            is_indet = (outcome == "indeterminate")
            is_valid_shift = (outcome in ("strong", "partial"))

            if is_indet:
                total_indet_count += 1

            if cat == "reported":
                rep_attempted += 1
                if is_indet:
                    rep_indeterminate += 1
                else:
                    rep_determinate += 1
                    if is_valid_shift:
                        rep_validated += 1
            elif cat == "unreported_required":
                unrep_req_attempted += 1
                if is_indet:
                    unrep_req_indeterminate += 1
                else:
                    unrep_req_determinate += 1
                    if is_valid_shift:
                        unrep_req_validated += 1
            elif cat == "distractor":
                dist_attempted += 1
                if is_indet:
                    dist_indeterminate += 1
                else:
                    dist_determinate += 1
                    if is_valid_shift:
                        dist_validated += 1

        # Rates computation
        rep_nec_determinate = (
            rep_validated / rep_determinate if rep_determinate > 0 else None
        )
        rep_nec_conservative = (
            rep_validated / rep_attempted if rep_attempted > 0 else None
        )

        unrep_req_determinate_rate = (
            unrep_req_validated / unrep_req_determinate if unrep_req_determinate > 0 else None
        )
        unrep_req_conservative_rate = (
            unrep_req_validated / unrep_req_attempted if unrep_req_attempted > 0 else None
        )

        dist_determinate_rate = (
            dist_validated / dist_determinate if dist_determinate > 0 else None
        )
        dist_conservative_rate = (
            dist_validated / dist_attempted if dist_attempted > 0 else None
        )

        noop_instab_rate = (
            noop_unstable / noop_attempted if noop_attempted > 0 else None
        )

        total_causal = len(tests_for_stratum)
        total_indet_rate = (
            total_indet_count / total_causal if total_causal > 0 else None
        )

        return Exp0StratifiedMetrics(
            reasoning_depth=reasoning_depth,
            total_claims=total_claims,
            structured_output_success_rate=struct_success_rate,
            task_truth_accuracy=task_truth_acc,
            reported_lineage_precision=precision,
            reported_lineage_recall=lineage_recall,
            reported_parents_attempted=rep_attempted,
            reported_parents_determinate=rep_determinate,
            reported_parents_indeterminate=rep_indeterminate,
            reported_parents_validated=rep_validated,
            reported_parent_necessity_rate_determinate=rep_nec_determinate,
            reported_parent_necessity_rate_conservative=rep_nec_conservative,
            unreported_required_attempted=unrep_req_attempted,
            unreported_required_determinate=unrep_req_determinate,
            unreported_required_indeterminate=unrep_req_indeterminate,
            unreported_required_validated=unrep_req_validated,
            unreported_required_causal_rate_determinate=unrep_req_determinate_rate,
            unreported_required_causal_rate_conservative=unrep_req_conservative_rate,
            distractors_attempted=dist_attempted,
            distractors_determinate=dist_determinate,
            distractors_indeterminate=dist_indeterminate,
            distractors_validated=dist_validated,
            unreported_distractor_influence_rate_determinate=dist_determinate_rate,
            unreported_distractor_influence_rate_conservative=dist_conservative_rate,
            noop_attempted=noop_attempted,
            noop_unstable_count=noop_unstable,
            noop_parse_failed_count=noop_parse_failed,
            noop_answer_shifted_count=noop_answer_shifted,
            noop_instability_rate=noop_instab_rate,
            total_causal_tests=total_causal,
            total_indeterminate_tests=total_indet_count,
            causal_tests_indeterminate_rate=total_indet_rate,
        )

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

        # 2. Claims
        claims_rows = db.conn.execute(
            """
            SELECT c.* FROM claims c
            JOIN memory_nodes m ON c.node_id = m.node_id
            WHERE m.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        claims = [dict(c) for c in claims_rows]
        total_claims = len(claims)

        # 3. Reported edges
        reported_edges_rows = db.conn.execute(
            """
            SELECT r.parent_node_id, r.child_node_id, c.oracle_evidence_json
            FROM reported_support_edges r
            JOIN claims c ON r.child_node_id = c.node_id
            JOIN memory_nodes m ON c.node_id = m.node_id
            WHERE m.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        reported_edges = [dict(r) for r in reported_edges_rows]

        # 4. Causal tests
        causal_tests_rows = db.conn.execute(
            """
            SELECT ct.*, c.request_json, cl.oracle_evidence_json
            FROM causal_tests ct
            JOIN calls c ON ct.original_call_id = c.call_id
            LEFT JOIN claims cl ON ct.child_node_id = cl.node_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        causal_tests = [dict(t) for t in causal_tests_rows]

        # Separate by reasoning depth
        d0_claims = []
        d1_claims = []
        for cl in claims:
            ev = json.loads(cl["oracle_evidence_json"]) if cl["oracle_evidence_json"] else {}
            rd = ev.get("reasoning_depth")
            if rd == 0:
                d0_claims.append(cl)
            elif rd == 1:
                d1_claims.append(cl)
            else:
                # Fallback: if task_id has d0 or d1
                tid = ev.get("task_id", "")
                if "_d0_" in tid:
                    d0_claims.append(cl)
                elif "_d1_" in tid:
                    d1_claims.append(cl)
                else:
                    d0_claims.append(cl)

        overall_stratum = cls._compute_stratum(claims, reported_edges, causal_tests, reasoning_depth=None)
        d0_stratum = cls._compute_stratum(d0_claims, reported_edges, causal_tests, reasoning_depth=0)
        d1_stratum = cls._compute_stratum(d1_claims, reported_edges, causal_tests, reasoning_depth=1)

        total_causal = len(causal_tests)
        total_noop = sum(1 for t in causal_tests if t["intervention_type"] == "noop")
        total_rep = overall_stratum.reported_parents_attempted
        total_unrep_req = overall_stratum.unreported_required_attempted
        total_dist = overall_stratum.distractors_attempted
        total_indet = overall_stratum.total_indeterminate_tests

        return Exp0Metrics(
            total_calls=total_calls,
            total_claims=total_claims,
            structured_output_success_rate=overall_stratum.structured_output_success_rate or 0.0,
            task_truth_accuracy=overall_stratum.task_truth_accuracy or 0.0,
            reported_lineage_precision=overall_stratum.reported_lineage_precision or 0.0,
            reported_lineage_recall=overall_stratum.reported_lineage_recall or 0.0,
            reported_parent_necessity_rate=overall_stratum.reported_parent_necessity_rate,
            unreported_required_causal_rate=overall_stratum.unreported_required_causal_rate,
            unreported_distractor_influence_rate=overall_stratum.unreported_distractor_influence_rate,
            noop_instability_rate=overall_stratum.noop_instability_rate or 0.0,
            causal_tests_indeterminate_rate=overall_stratum.causal_tests_indeterminate_rate or 0.0,
            avg_latency_ms=avg_latency,
            total_prompt_tokens=tot_prompt_tokens,
            total_completion_tokens=tot_comp_tokens,
            total_causal_tests=total_causal,
            total_noop_tests=total_noop,
            total_reported_parent_tests=total_rep,
            total_unreported_required_tests=total_unrep_req,
            total_distractor_tests=total_dist,
            total_indeterminate_tests=total_indet,
            d0=d0_stratum,
            d1=d1_stratum,
            overall=overall_stratum,
            raw_counts={
                "total_reported_edges": len(reported_edges),
                "valid_reported_edges": int(round((overall_stratum.reported_lineage_precision or 0.0) * len(reported_edges))),
                "tested_reported_parents": overall_stratum.reported_parents_attempted,
                "determinate_reported_parents": overall_stratum.reported_parents_determinate,
                "indeterminate_reported_parents": overall_stratum.reported_parents_indeterminate,
                "validated_reported_parents": overall_stratum.reported_parents_validated,
                "tested_unreported_required_parents": overall_stratum.unreported_required_attempted,
                "determinate_unreported_required_parents": overall_stratum.unreported_required_determinate,
                "indeterminate_unreported_required_parents": overall_stratum.unreported_required_indeterminate,
                "validated_unreported_required_parents": overall_stratum.unreported_required_validated,
                "tested_unreported_distractors": overall_stratum.distractors_attempted,
                "determinate_unreported_distractors": overall_stratum.distractors_determinate,
                "indeterminate_unreported_distractors": overall_stratum.distractors_indeterminate,
                "distractor_causal_influence_count": overall_stratum.distractors_validated,
                "total_noop_tests": overall_stratum.noop_attempted,
                "unstable_noop_tests": overall_stratum.noop_unstable_count,
                "noop_parse_failed_count": overall_stratum.noop_parse_failed_count,
                "noop_answer_shifted_count": overall_stratum.noop_answer_shifted_count,
                "indeterminate_causal_tests": overall_stratum.total_indeterminate_tests,
            },
        )

