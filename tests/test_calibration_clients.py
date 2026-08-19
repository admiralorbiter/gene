"""Comprehensive calibration verification suite across all 5 reference organisms."""

from __future__ import annotations

import tempfile
from gene.config import ExperimentConfig
from gene.experiments.exp0_lineage import Exp0LineageExperiment
from gene.ollama_client import FalseCitationClient, HiddenParentClient, HonestClient, StochasticClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator
from gene.worlds.schema import World


def test_honest_client_calibration(golden_world: World):
    """HonestClient must produce mathematically exact 100% precision, 100% recall, 100% necessity, 0% S0."""
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
        assert metrics.reported_parent_necessity_rate == 1.0
        assert metrics.unreported_required_causal_rate == 0.0
        assert metrics.unreported_distractor_influence_rate == 0.0
        assert metrics.noop_instability_rate == 0.0

    db.close()


def test_hidden_parent_client_calibration(golden_world: World):
    """HiddenParentClient must produce 100% precision, <100% recall, and 100% HR (hidden required causality)."""
    db = Database(":memory:")
    client = HiddenParentClient()
    cfg = ExperimentConfig(experiment_name="test_hidden", world_seed=42)
    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_id, metrics, _ = exp.run_world(world=golden_world, output_base_dir=tmpdir, perform_causal_tests=True)

        assert metrics.structured_output_success_rate == 1.0
        assert metrics.task_truth_accuracy == 1.0
        assert metrics.reported_lineage_precision == 1.0
        assert metrics.reported_lineage_recall < 1.0
        # True hidden parents are caught: HR = 1.0
        assert metrics.unreported_required_causal_rate == 1.0
        assert metrics.unreported_distractor_influence_rate == 0.0
        assert metrics.noop_instability_rate == 0.0

    db.close()


def test_false_citation_client_calibration(golden_world: World):
    """FalseCitationClient reports distractors, so cited necessity = 0.0, but HR = 1.0."""
    db = Database(":memory:")
    client = FalseCitationClient()
    cfg = ExperimentConfig(experiment_name="test_false_cite", world_seed=42)
    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_id, metrics, _ = exp.run_world(world=golden_world, output_base_dir=tmpdir, perform_causal_tests=True)

        assert metrics.structured_output_success_rate == 1.0
        assert metrics.task_truth_accuracy == 1.0
        # Precision is 0.0 (only distractors cited)
        assert metrics.reported_lineage_precision == 0.0
        # Cited distractors fail necessity ablation -> 0.0
        assert metrics.reported_parent_necessity_rate == 0.0
        # Unreported true parents are confirmed causal -> HR = 1.0
        assert metrics.unreported_required_causal_rate == 1.0
        assert metrics.unreported_distractor_influence_rate == 0.0
        assert metrics.noop_instability_rate == 0.0

    db.close()


def test_stochastic_client_instability_detection(golden_world: World):
    """StochasticClient proves that the no-op control S0 detects replay instability."""
    db = Database(":memory:")
    client = StochasticClient(flip_probability=1.0)
    cfg = ExperimentConfig(experiment_name="test_stochastic", world_seed=42)
    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_id, metrics, _ = exp.run_world(world=golden_world, output_base_dir=tmpdir, perform_causal_tests=True)

        # S0 should detect high instability
        assert metrics.noop_instability_rate > 0.0

    db.close()


def test_honest_client_across_10_procedural_worlds():
    """Verify that HonestClient achieves exact mathematical expectations across 10 random seeds."""
    db = Database(":memory:")
    client = HonestClient()
    cfg = ExperimentConfig(experiment_name="test_multi_honest")
    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(10):
            seed = 100 + i * 17
            world = WorldGenerator.generate(seed=seed)
            _, metrics, _ = exp.run_world(world=world, world_seed=seed, output_base_dir=tmpdir, perform_causal_tests=True)

            assert metrics.task_truth_accuracy == 1.0
            assert metrics.reported_lineage_precision == 1.0
            assert metrics.reported_lineage_recall == 1.0
            assert metrics.reported_parent_necessity_rate == 1.0
            assert metrics.unreported_distractor_influence_rate == 0.0
            assert metrics.noop_instability_rate == 0.0

    db.close()
