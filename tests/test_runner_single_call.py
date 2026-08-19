"""Unit tests for SingleCallRunner and audit logging with CallSpec."""

from __future__ import annotations

from gene.experiments.runner import SingleCallRunner
from gene.ollama_client import FakeOllamaClient
from gene.persistence.db import Database
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.tasks import TaskGenerator
from gene.worlds.schema import World


def test_single_call_runner_flow(golden_world: World):
    db = Database(":memory:")
    oracle = Oracle(golden_world)
    tasks = TaskGenerator.generate_d0_tasks(golden_world, oracle)
    task = tasks[0]

    client = FakeOllamaClient(
        canned_responses={
            task.prompt: {
                "answer": {
                    "subject": task.target_fact.subject,
                    "predicate": task.target_fact.predicate,
                    "object": task.target_fact.object,
                },
                "parent_memory_ids": [task.target_fact.fact_id],
                "confidence": 0.99,
                "explanation": "Extracted from source memory.",
            }
        }
    )

    runner = SingleCallRunner(db=db, client=client)
    run_id = runner.create_run(world=golden_world, condition="clean")
    assert run_id.startswith("run_")

    call_result, evaluated_claim, call_id, node_id = runner.execute_task(
        run_id=run_id,
        world=golden_world,
        task=task,
        oracle=oracle,
        generation=1,
    )

    assert evaluated_claim.parse_status == "success"
    assert evaluated_claim.truth_status == TruthStatus.TRUE
    assert evaluated_claim.infection_status == "clean"

    cursor = db.conn.execute("SELECT * FROM calls WHERE run_id = ?", (run_id,))
    call_row = cursor.fetchone()
    assert call_row is not None
    assert call_row["task_id"] == task.task_id
    assert call_row["request_json"] is not None

    cursor = db.conn.execute("SELECT * FROM memory_nodes WHERE run_id = ?", (run_id,))
    node_row = cursor.fetchone()
    assert node_row is not None
    assert node_row["created_by_call_id"] == call_row["call_id"]

    cursor = db.conn.execute("SELECT * FROM claims WHERE node_id = ?", (node_row["node_id"],))
    claim_row = cursor.fetchone()
    assert claim_row is not None
    assert claim_row["truth_status"] == "true"

    db.close()
