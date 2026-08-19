"""Unit tests for lineage graph construction and run artifact export."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
from gene.memory.lineage import LineageRecorder
from gene.persistence.db import Database
from gene.worlds.schema import World


def test_lineage_graph_and_export(golden_world: World):
    db = Database(":memory:")
    db.save_world(golden_world)

    run_id = "run_test_lineage"
    with db.conn:
        db.conn.execute(
            """
            INSERT INTO runs (
                run_id, experiment_name, experiment_version, condition, world_id,
                started_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, "exp0", "v1", "clean", golden_world.world_id, "2026-08-19T00:00:00Z", "running"),
        )
        db.conn.execute(
            """
            INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("call_01", run_id, 0, "task_1", "{}", "resp", "2026-08-19T00:00:01Z"),
        )
        db.conn.execute(
            """
            INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "node_p1", run_id, golden_world.world_id, 0, "source", "Parent memory", "2026-08-19T00:00:00Z",
                "node_c1", run_id, golden_world.world_id, 1, "derived", "Child memory", "2026-08-19T00:00:02Z",
            ),
        )
        db.conn.execute(
            """
            INSERT INTO claims (claim_id, node_id, subject, predicate, object, parse_status, truth_status, infection_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("claim_01", "node_c1", "VELORA", "uses_protocol", "GREEN", "success", "true", "clean"),
        )

    LineageRecorder.record_exposure_edges(db, [("node_p1", "node_c1", "call_01", 0, 0)])
    LineageRecorder.record_reported_support_edges(db, [("node_p1", "node_c1", "call_01", "support")])

    # Build Graph
    graph = LineageRecorder.build_lineage_graph(db, run_id)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 2

    # Export Artifacts
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = LineageRecorder.export_run_artifacts(
            db=db,
            run_id=run_id,
            world=golden_world,
            output_dir=tmpdir,
            metrics={"test_metric": 1.0},
        )

        expected_files = [
            "manifest.json",
            "world.json",
            "mutation.json",
            "calls.jsonl",
            "memory_nodes.jsonl",
            "claims.csv",
            "exposure_edges.csv",
            "reported_support_edges.csv",
            "causal_tests.csv",
            "metrics.json",
            "lineage.graphml",
        ]
        for fname in expected_files:
            assert (Path(out_dir) / fname).exists(), f"Missing expected artifact: {fname}"

    db.close()
