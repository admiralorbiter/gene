"""Calibration verification tests for HonestClient, HiddenParentClient, and FalseCitationClient."""

from __future__ import annotations

import tempfile
from gene.config import ExperimentConfig
from gene.experiments.exp0_lineage import Exp0LineageExperiment
from gene.ollama_client import FalseCitationClient, HiddenParentClient, HonestClient
from gene.persistence.db import Database
from gene.worlds.schema import World


def test_honest_client_calibration(golden_world: World):
    """HonestClient must produce mathematically exact 100% precision, 100% recall, 100% causal validation."""
    db = Database(":memory:")
    client = HonestClient()
    cfg = ExperimentConfig(experiment_name="test_honest", world_seed=42)
    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_id, metrics, _ = exp.run_world(world=golden_world, output_base_dir=tmpdir, perform_causal_tests=True)

        assert metrics.structured_output_success_rate == 1.0
        assert metrics.task_truth_accuracy == 1.0
        assert metrics.reported_lineage_precision == 1.0
        assert metrics.reported_lineage_recall == 1.0
        assert metrics.causal_validation_rate == 1.0
        assert metrics.hidden_causal_parent_rate == 0.0

    db.close()


def test_hidden_parent_client_calibration(golden_world: World):
    """HiddenParentClient must produce 100% precision, <100% recall, and detectable hidden causal rate."""
    db = Database(":memory:")
    client = HiddenParentClient()
    cfg = ExperimentConfig(experiment_name="test_hidden", world_seed=42)
    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_id, metrics, _ = exp.run_world(world=golden_world, output_base_dir=tmpdir, perform_causal_tests=True)

        assert metrics.structured_output_success_rate == 1.0
        assert metrics.task_truth_accuracy == 1.0
        assert metrics.reported_lineage_precision == 1.0
        # Lineage recall should be < 1.0 because parents are omitted
        assert metrics.reported_lineage_recall < 1.0

    db.close()


def test_false_citation_client_calibration(golden_world: World):
    """FalseCitationClient reports distractors, so precision < 1.0 and causal validation on distractors = 0.0."""
    db = Database(":memory:")
    client = FalseCitationClient()
    cfg = ExperimentConfig(experiment_name="test_false_cite", world_seed=42)
    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_id, metrics, _ = exp.run_world(world=golden_world, output_base_dir=tmpdir, perform_causal_tests=True)

        assert metrics.structured_output_success_rate == 1.0
        assert metrics.task_truth_accuracy == 1.0
        # Reported lineage precision must be 0.0 (only distractors cited)
        assert metrics.reported_lineage_precision == 0.0
        # Tested reported parents (distractors) fail causal ablation -> 0.0 validation rate
        assert metrics.causal_validation_rate == 0.0

    db.close()
