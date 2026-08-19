"""Unit tests for hardened Experiment 0 metric calculations."""

from __future__ import annotations

import json
from gene.evaluation.causality import CausalRunner
from gene.evaluation.claims import EvaluatedClaim
from gene.evaluation.metrics import MetricsCalculator, format_rate
from gene.ollama_client import CallSpec
from gene.persistence.db import Database
from gene.worlds.oracle import TruthStatus


def test_metrics_calculation():
    db = Database(":memory:")
    run_id = "run_metric_test"
    spec = CallSpec(model_name="test_model", system_prompt="sys", user_prompt="usr")

    with db.conn:
        db.conn.execute(
            """
            INSERT INTO worlds (world_id, world_seed, world_version, canonical_json, created_at, validation_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("w_1", 42, "v1", "{}", "2026-08-19T00:00:00Z", "hash_w1"),
        )
        db.conn.execute(
            """
            INSERT INTO runs (run_id, experiment_name, experiment_version, condition, world_id, started_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, "exp0", "v1", "clean", "w_1", "2026-08-19T00:00:00Z", "completed"),
        )
        db.conn.execute(
            """
            INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("call_1", run_id, 0, "task_1", spec.model_dump_json(), "resp", 100, 20, 50.0, "2026-08-19T00:00:01Z"),
        )
        db.conn.execute(
            """
            INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("node_c1", run_id, "w_1", 1, "derived", "text", "2026-08-19T00:00:02Z"),
        )
        db.conn.execute(
            """
            INSERT INTO claims (claim_id, node_id, subject, predicate, object, parse_status, truth_status, infection_status, oracle_evidence_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "claim_1",
                "node_c1",
                "VELORA",
                "manager",
                "NERIN",
                "success",
                "true",
                "clean",
                json.dumps({
                    "task_id": "task_1",
                    "reasoning_depth": 0,
                    "target_subject": "VELORA",
                    "target_predicate": "manager",
                    "target_object": "NERIN",
                    "valid_support_paths": [["fact_p1"]],
                }),
            ),
        )
        db.conn.execute(
            """
            INSERT INTO reported_support_edges (parent_node_id, child_node_id, call_id, reported_role)
            VALUES (?, ?, ?, ?)
            """,
            ("fact_p1", "node_c1", "call_1", "support"),
        )
        db.conn.execute(
            """
            INSERT INTO causal_tests (causal_test_id, parent_node_id, child_node_id, original_call_id, intervention_type, outcome, score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("ct_1", "fact_p1", "node_c1", "call_1", "remove", "strong", 1.0),
        )

    metrics = MetricsCalculator.compute_exp0_metrics(db, run_id)

    assert metrics.total_calls == 1
    assert metrics.total_claims == 1
    assert metrics.structured_output_success_rate == 1.0
    assert metrics.task_truth_accuracy == 1.0
    assert metrics.reported_lineage_precision == 1.0
    assert metrics.reported_lineage_recall == 1.0
    assert metrics.causal_validation_rate == 1.0
    assert metrics.avg_latency_ms == 50.0
    assert metrics.d0 is not None
    assert metrics.d0.total_claims == 1
    assert metrics.d0.task_truth_accuracy == 1.0

    db.close()


def test_metrics_stratification_and_indeterminates():
    db = Database(":memory:")
    run_id = "run_strat_test"
    spec = CallSpec(model_name="test_model", system_prompt="sys", user_prompt="usr")

    with db.conn:
        db.conn.execute(
            "INSERT INTO worlds (world_id, world_seed, world_version, canonical_json, created_at, validation_hash) VALUES (?, ?, ?, ?, ?, ?)",
            ("w_1", 42, "v1", "{}", "2026-08-19T00:00:00Z", "hash_w1"),
        )
        db.conn.execute(
            "INSERT INTO runs (run_id, experiment_name, experiment_version, condition, world_id, started_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, "exp0", "v1", "clean", "w_1", "2026-08-19T00:00:00Z", "completed"),
        )
        db.conn.execute(
            "INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("call_d0", run_id, 0, "task_d0", spec.model_dump_json(), "resp", "2026-08-19T00:00:01Z"),
        )
        db.conn.execute(
            "INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("call_d1", run_id, 0, "task_d1", spec.model_dump_json(), "resp", "2026-08-19T00:00:02Z"),
        )
        db.conn.execute(
            "INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("node_d0", run_id, "w_1", 1, "derived", "text", "2026-08-19T00:00:01Z"),
        )
        db.conn.execute(
            "INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("node_d1", run_id, "w_1", 1, "derived", "text", "2026-08-19T00:00:02Z"),
        )

        # Claim 1: D0 task
        db.conn.execute(
            """
            INSERT INTO claims (claim_id, node_id, subject, predicate, object, parse_status, truth_status, infection_status, oracle_evidence_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "claim_d0",
                "node_d0",
                "VELORA",
                "manager",
                "NERIN",
                "success",
                "true",
                "clean",
                json.dumps({"task_id": "task_d0", "reasoning_depth": 0, "target_subject": "VELORA", "target_predicate": "manager", "target_object": "NERIN", "valid_support_paths": [["fact_p1"]]}),
            ),
        )

        # Claim 2: D1 task
        db.conn.execute(
            """
            INSERT INTO claims (claim_id, node_id, subject, predicate, object, parse_status, truth_status, infection_status, oracle_evidence_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "claim_d1",
                "node_d1",
                "VELORA",
                "uses_protocol",
                "PROTOCOL_GREEN",
                "success",
                "true",
                "clean",
                json.dumps({"task_id": "task_d1", "reasoning_depth": 1, "target_subject": "VELORA", "target_predicate": "uses_protocol", "target_object": "PROTOCOL_GREEN", "valid_support_paths": [["fact_p1", "fact_p2", "rule_r1"]]}),
            ),
        )

        # Reported edges
        db.conn.execute("INSERT INTO reported_support_edges VALUES (?, ?, ?, ?)", ("fact_p1", "node_d0", "call_d0", "support"))
        db.conn.execute("INSERT INTO reported_support_edges VALUES (?, ?, ?, ?)", ("fact_p1", "node_d1", "call_d1", "support"))
        db.conn.execute("INSERT INTO reported_support_edges VALUES (?, ?, ?, ?)", ("fact_p2", "node_d1", "call_d1", "support"))

        # Causal tests:
        # D0: reported fact_p1 -> strong
        db.conn.execute("INSERT INTO causal_tests (causal_test_id, parent_node_id, child_node_id, original_call_id, intervention_type, outcome, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        ("ct_d0_1", "fact_p1", "node_d0", "call_d0", "remove", "strong", 1.0))
        # D1: reported fact_p1 -> strong, reported fact_p2 -> indeterminate!
        db.conn.execute("INSERT INTO causal_tests (causal_test_id, parent_node_id, child_node_id, original_call_id, intervention_type, outcome, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        ("ct_d1_1", "fact_p1", "node_d1", "call_d1", "remove", "strong", 1.0))
        db.conn.execute("INSERT INTO causal_tests (causal_test_id, parent_node_id, child_node_id, original_call_id, intervention_type, outcome, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        ("ct_d1_2", "fact_p2", "node_d1", "call_d1", "remove", "indeterminate", 0.0))

    metrics = MetricsCalculator.compute_exp0_metrics(db, run_id)

    # D0: 1 tested reported parent, 1 determinate, 1 validated -> 100% determinate, 100% conservative
    assert metrics.d0.reported_parents_attempted == 1
    assert metrics.d0.reported_parents_determinate == 1
    assert metrics.d0.reported_parents_indeterminate == 0
    assert metrics.d0.reported_parent_necessity_rate_determinate == 1.0
    assert metrics.d0.reported_parent_necessity_rate_conservative == 1.0

    # D1: 2 tested reported parents, 1 determinate, 1 indeterminate, 1 validated -> 100% determinate (1/1), 50% conservative (1/2)
    assert metrics.d1.reported_parents_attempted == 2
    assert metrics.d1.reported_parents_determinate == 1
    assert metrics.d1.reported_parents_indeterminate == 1
    assert metrics.d1.reported_parent_necessity_rate_determinate == 1.0
    assert metrics.d1.reported_parent_necessity_rate_conservative == 0.5

    # Overall: 3 attempted, 2 determinate, 1 indeterminate, 2 validated -> 100% determinate (2/2), 66.67% conservative (2/3)
    assert metrics.overall.reported_parents_attempted == 3
    assert metrics.overall.reported_parents_determinate == 2
    assert metrics.overall.reported_parents_indeterminate == 1
    assert metrics.overall.reported_parent_necessity_rate_determinate == 1.0
    assert abs(metrics.overall.reported_parent_necessity_rate_conservative - (2.0 / 3.0)) < 1e-5

    # Format rate handles None properly
    assert format_rate(None) == "N/A"
    assert format_rate(1.0) == "100.00%"

    db.close()


def test_noop_instability_strictness():
    """Verify that malformed output in noop replay is classified as strong instability."""
    orig = EvaluatedClaim(
        claim_id="c_orig",
        subject="AERIS",
        predicate="uses_protocol",
        object="PROTOCOL_GREEN",
        parse_status="success",
        truth_status=TruthStatus.TRUE,
        infection_status="clean",
        reported_parent_ids=[],
    )
    cf_malformed = EvaluatedClaim(
        claim_id="c_cf",
        subject="UNKNOWN",
        predicate="unknown",
        object="UNKNOWN",
        parse_status="malformed_json",
        truth_status=TruthStatus.UNSUPPORTED,
        infection_status="unresolved",
        reported_parent_ids=[],
    )

    outcome, score, details = CausalRunner._classify_causal_outcome(orig, cf_malformed, "noop")
    assert outcome == "strong"
    assert score == 1.0
    assert "parse_failure" in details.get("instability_reason", "")

