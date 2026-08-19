"""Comprehensive calibration verification suite across all 5 reference organisms."""

from __future__ import annotations

import tempfile
from gene.config import ExperimentConfig
from gene.experiments.exp0_lineage import Exp0LineageExperiment
from gene.ollama_client import FalseCitationClient, HiddenParentClient, HonestClient, StochasticClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator
from gene.worlds.schema import Fact, Rule, World


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


def test_redundant_support_client_calibration():
    """RedundantSupportClient proves mathematically that valid ancestry != counterfactual necessity."""
    db = Database(":memory:")
    client = HonestClient()

    # Hand-built world with 2 independent complete derivation paths for PROTOCOL_GREEN
    fact_mgr = Fact(subject="AERIS", predicate="manager", object="NERIN")
    fact_sup = Fact(subject="NERIN", predicate="reports_to", object="KIRA")
    rule_sup = Rule(
        rule_id="RULE_SUP",
        antecedents=[("?station", "manager", "?person"), ("?person", "reports_to", "KIRA")],
        consequent=("?station", "uses_protocol", "PROTOCOL_GREEN"),
        description="Supervisor protocol rule",
    )
    fact_loc = Fact(subject="AERIS", predicate="located_in", object="CYGNUS")
    rule_loc = Rule(
        rule_id="RULE_LOC",
        antecedents=[("?station", "located_in", "CYGNUS")],
        consequent=("?station", "uses_protocol", "PROTOCOL_GREEN"),
        description="Sector protocol rule",
    )

    world = World(
        world_id="world_redundant",
        world_seed=42,
        entities={"stations": ["AERIS"], "people": ["NERIN", "KIRA"], "sectors": ["CYGNUS"]},
        facts=[fact_mgr, fact_sup, fact_loc],
        rules=[rule_sup, rule_loc],
    )
    cfg = ExperimentConfig(experiment_name="test_redundant", world_seed=42)
    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_id, metrics, _ = exp.run_world(world=world, output_base_dir=tmpdir, perform_causal_tests=True)

        # 1. Honest derivation succeeds with full valid ancestry reported
        assert metrics.task_truth_accuracy == 1.0
        assert metrics.reported_lineage_precision == 1.0
        assert metrics.reported_lineage_recall == 1.0

        # 2. When reported parent fact_sup is ablated, alternative path (fact_loc + rule_loc) survives!
        # Thus reported parent necessity rate < 1.0
        assert metrics.overall is not None
        assert metrics.overall.reported_parent_necessity_rate_determinate < 1.0

    db.close()


def test_deterministic_organisms_100_procedural_worlds():
    """Verify exact mathematical invariants across 100 procedural worlds across all calibration organisms."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. 25 Worlds HonestClient
        db_honest = Database(":memory:")
        exp_honest = Exp0LineageExperiment(db=db_honest, client=HonestClient())
        for i in range(25):
            seed = 1000 + i * 7
            world = WorldGenerator.generate(seed=seed)
            _, m, _ = exp_honest.run_world(world=world, world_seed=seed, output_base_dir=tmpdir, perform_causal_tests=True)
            assert m.task_truth_accuracy == 1.0
            assert m.reported_lineage_precision == 1.0
            assert m.reported_lineage_recall == 1.0
            assert m.reported_parent_necessity_rate == 1.0
            assert m.unreported_distractor_influence_rate == 0.0
            assert m.noop_instability_rate == 0.0
        db_honest.close()

        # 2. 25 Worlds HiddenParentClient
        db_hidden = Database(":memory:")
        exp_hidden = Exp0LineageExperiment(db=db_hidden, client=HiddenParentClient())
        for i in range(25):
            seed = 2000 + i * 7
            world = WorldGenerator.generate(seed=seed)
            _, m, _ = exp_hidden.run_world(world=world, world_seed=seed, output_base_dir=tmpdir, perform_causal_tests=True)
            assert m.task_truth_accuracy == 1.0
            assert m.reported_lineage_precision == 1.0
            assert m.unreported_required_causal_rate == 1.0
            assert m.unreported_distractor_influence_rate == 0.0
            assert m.noop_instability_rate == 0.0
        db_hidden.close()

        # 3. 25 Worlds FalseCitationClient
        db_false = Database(":memory:")
        exp_false = Exp0LineageExperiment(db=db_false, client=FalseCitationClient())
        for i in range(25):
            seed = 3000 + i * 7
            world = WorldGenerator.generate(seed=seed)
            _, m, _ = exp_false.run_world(world=world, world_seed=seed, output_base_dir=tmpdir, perform_causal_tests=True)
            assert m.task_truth_accuracy == 1.0
            assert m.reported_lineage_precision == 0.0
            assert m.reported_parent_necessity_rate == 0.0
            assert m.unreported_required_causal_rate == 1.0
            assert m.unreported_distractor_influence_rate == 0.0
            assert m.noop_instability_rate == 0.0
        db_false.close()

        # 4. 25 Worlds StochasticClient
        db_stoch = Database(":memory:")
        exp_stoch = Exp0LineageExperiment(db=db_stoch, client=StochasticClient(flip_probability=1.0))
        for i in range(25):
            seed = 4000 + i * 7
            world = WorldGenerator.generate(seed=seed)
            _, m, _ = exp_stoch.run_world(world=world, world_seed=seed, output_base_dir=tmpdir, perform_causal_tests=True)
            assert m.noop_instability_rate > 0.0
        db_stoch.close()

