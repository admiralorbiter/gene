"""Unit tests for counterfactual causal runner."""

from __future__ import annotations

import json
from gene.evaluation.causality import CausalRunner
from gene.ollama_client import FakeOllamaClient
from gene.persistence.db import Database
from gene.worlds.oracle import Oracle
from gene.worlds.schema import World


def test_causal_runner_parent_removal(golden_world: World):
    db = Database(":memory:")
    db.save_world(golden_world)
    oracle = Oracle(golden_world)

    run_id = "run_causal_test"
    with db.conn:
        db.conn.execute(
            """
            INSERT INTO runs (run_id, experiment_name, experiment_version, condition, world_id, started_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, "exp0", "v1", "clean", golden_world.world_id, "2026-08-19T00:00:00Z", "running"),
        )

        orig_prompt = "Available Memories:\n[fact_01] Nerin is manager of Velora.\n[fact_02] Nerin reports to Tal.\n\nQuestion: Which security protocol does Velora operate under?"
        db.conn.execute(
            """
            INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "call_orig_1",
                run_id,
                1,
                "task_uses_protocol",
                json.dumps({"messages": [{"role": "user", "content": orig_prompt}]}),
                '{"answer": {"subject": "VELORA", "predicate": "uses_protocol", "object": "PROTOCOL_GREEN"}, "parent_memory_ids": ["fact_01", "fact_02"]}',
                "2026-08-19T00:00:01Z",
            ),
        )
        db.conn.execute(
            """
            INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "fact_02",
                run_id,
                golden_world.world_id,
                0,
                "source",
                "Nerin reports to Tal.",
                "2026-08-19T00:00:00Z",
                "node_c1",
                run_id,
                golden_world.world_id,
                1,
                "derived",
                "Velora uses Green protocol",
                "2026-08-19T00:00:02Z",
            ),
        )
        db.conn.execute(
            """
            INSERT INTO claims (claim_id, node_id, subject, predicate, object, parse_status, truth_status, infection_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("claim_c1", "node_c1", "VELORA", "uses_protocol", "PROTOCOL_GREEN", "success", "true", "clean"),
        )

    # When fact_02 is removed, FakeClient returns UNKNOWN protocol (simulating removal effect)
    fake_client = FakeOllamaClient(
        canned_responses={
            "[fact_01] Nerin is manager of Velora.\n\nQuestion": {
                "answer": {
                    "subject": "VELORA",
                    "predicate": "uses_protocol",
                    "object": "UNKNOWN_PROTOCOL",
                },
                "parent_memory_ids": ["fact_01"],
                "confidence": 0.5,
                "explanation": "Missing supervisor reporting link.",
            }
        }
    )

    runner = CausalRunner(db=db, client=fake_client)
    res = runner.replay_intervention(
        original_call_id="call_orig_1",
        child_node_id="node_c1",
        target_parent_id="fact_02",
        intervention_type="remove",
        oracle=oracle,
        world=golden_world,
        seed=42,
    )

    assert res.outcome == "strong"
    assert res.score == 1.0
    assert res.counterfactual_claim.object == "UNKNOWN_PROTOCOL"

    # Verify causal_tests table entry
    cursor = db.conn.execute("SELECT * FROM causal_tests WHERE causal_test_id = ?", (res.causal_test_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row["outcome"] == "strong"

    db.close()
