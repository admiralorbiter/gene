"""Unit tests for hardened Experiment 0 metric calculations."""

from __future__ import annotations

import json
from gene.evaluation.metrics import MetricsCalculator
from gene.ollama_client import CallSpec
from gene.persistence.db import Database


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

    db.close()
