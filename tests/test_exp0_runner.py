"""Unit and pipeline tests for Exp0LineageExperiment."""

from __future__ import annotations

from pathlib import Path
import tempfile
from gene.config import ExperimentConfig
from gene.experiments.exp0_lineage import Exp0LineageExperiment
from gene.ollama_client import FakeOllamaClient
from gene.persistence.db import Database
from gene.worlds.schema import World


def test_exp0_pipeline_run(golden_world: World):
    db = Database(":memory:")
    fake_client = FakeOllamaClient()
    cfg = ExperimentConfig(experiment_name="test_exp0", world_seed=42)

    exp = Exp0LineageExperiment(db=db, client=fake_client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_id, metrics, output_dir = exp.run_world(
            world=golden_world,
            output_base_dir=tmpdir,
            perform_causal_tests=True,
        )

        assert run_id.startswith("run_")
        assert metrics.total_calls > 0
        assert metrics.total_claims > 0

        # Verify all 10 artifact files exist in output_dir
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
            p = Path(output_dir) / fname
            assert p.exists(), f"File {fname} not found in {output_dir}"

    db.close()
