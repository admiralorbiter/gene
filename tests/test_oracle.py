"""Unit and invariant tests for forward-chaining deterministic oracle with rule inclusion."""

from __future__ import annotations

from gene.worlds.oracle import Oracle, TruthStatus, WorldValidator
from gene.worlds.schema import Fact, World, compute_fact_id


def test_golden_world_closure(golden_world: World):
    oracle = Oracle(golden_world)

    # 3 source facts + 2 derived facts = 5 closure facts
    assert len(oracle.closure_facts) == 5

    # Check derived green protocol fact
    green_id = compute_fact_id("VELORA", "uses_protocol", "PROTOCOL_GREEN")
    assert green_id in oracle.closure_facts
    assert oracle.closure_facts[green_id].source_type == "derived"


def test_golden_world_minimal_support_paths_includes_rules(golden_world: World):
    oracle = Oracle(golden_world)

    # Source fact support should be just itself
    f1_id = compute_fact_id("VELORA", "manager", "NERIN")
    f1_paths = oracle.get_support_paths(f1_id)
    assert f1_paths == [[f1_id]]

    # Derived green fact requires {manager(VELORA, NERIN), reports_to(NERIN, TAL), RULE_GOLDEN_GREEN}
    f2_id = compute_fact_id("NERIN", "reports_to", "TAL")
    green_id = compute_fact_id("VELORA", "uses_protocol", "PROTOCOL_GREEN")
    green_paths = oracle.get_support_paths(green_id)
    expected_support = sorted([f1_id, f2_id, "RULE_GOLDEN_GREEN"])
    assert green_paths == [expected_support]


def test_oracle_truth_evaluation(golden_world: World):
    oracle = Oracle(golden_world)

    # True derived claim
    assert oracle.evaluate_triple("VELORA", "uses_protocol", "PROTOCOL_GREEN") == TruthStatus.TRUE

    # True source claim
    assert oracle.evaluate_triple("VELORA", "manager", "NERIN") == TruthStatus.TRUE

    # Contradictory functional claim (manager is NERIN, not SOREN)
    assert oracle.evaluate_triple("VELORA", "manager", "SOREN") == TruthStatus.FALSE

    # Completely unmentioned fact
    assert oracle.evaluate_triple("UNKNOWN_STATION", "manager", "NERIN") == TruthStatus.UNSUPPORTED


def test_world_validator(golden_world: World):
    errors = WorldValidator.validate_world(golden_world)
    assert errors == []
