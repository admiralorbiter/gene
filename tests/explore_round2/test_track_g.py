"""Preflight tests for Track G: Multi-Justification & Epistemic Recombination."""

import pytest
from gene.experiments.multi_justification import MinimalSupportEngine


def test_geometry_1_single_path():
    """AB -> C: Invalidation of A destroys C."""
    engine = MinimalSupportEngine()
    engine.add_support_set("AUTH_ALPHA", {"A", "B"})

    assert engine.claim_survives("AUTH_ALPHA") is True
    assert engine.epistemic_resilience("AUTH_ALPHA") == 1
    assert engine.minimal_cut_sets("AUTH_ALPHA") == {frozenset({"A"}), frozenset({"B"})}

    affected = engine.invalidate_ancestor("A")
    assert "AUTH_ALPHA" in affected
    assert engine.claim_survives("AUTH_ALPHA") is False
    assert engine.epistemic_resilience("AUTH_ALPHA") == 0


def test_geometry_2_redundant_independent_support():
    """AB + DE -> C: Invalidation of A preserves C through DE."""
    engine = MinimalSupportEngine()
    engine.add_support_set("AUTH_ALPHA", {"A", "B"})
    engine.add_support_set("AUTH_ALPHA", {"D", "E"})

    assert engine.claim_survives("AUTH_ALPHA") is True
    assert engine.epistemic_resilience("AUTH_ALPHA") == 2
    # Cuts must hit both {A, B} and {D, E}
    cuts = engine.minimal_cut_sets("AUTH_ALPHA")
    assert frozenset({"A", "D"}) in cuts
    assert frozenset({"A", "E"}) in cuts
    assert frozenset({"B", "D"}) in cuts
    assert frozenset({"B", "E"}) in cuts

    # Invalidate A
    engine.invalidate_ancestor("A")
    assert engine.claim_survives("AUTH_ALPHA") is True  # Non-destructive survival!
    assert engine.active_support_sets("AUTH_ALPHA") == {frozenset({"D", "E"})}
    assert engine.epistemic_resilience("AUTH_ALPHA") == 1


def test_geometry_3_shared_root_apparent_redundancy():
    """AX + AY -> C: Apparent redundancy shares root A; invalidating A destroys C."""
    engine = MinimalSupportEngine()
    engine.add_support_set("AUTH_ALPHA", {"A", "X"})
    engine.add_support_set("AUTH_ALPHA", {"A", "Y"})

    assert engine.epistemic_resilience("AUTH_ALPHA") == 1
    # Minimal cut of size 1 is {A}
    assert frozenset({"A"}) in engine.minimal_cut_sets("AUTH_ALPHA")

    engine.invalidate_ancestor("A")
    assert engine.claim_survives("AUTH_ALPHA") is False  # Both paths destroyed


def test_geometry_4_recombinant_support():
    """AI + BH -> C: Invalidation of infected root I preserves clean path BH."""
    engine = MinimalSupportEngine()
    engine.add_support_set("PROTO_X7", {"A", "INFECTED_ROOT"})
    engine.add_support_set("PROTO_X7", {"B", "HEALTHY_ROOT"})

    # Invalidate infected root
    engine.invalidate_ancestor("INFECTED_ROOT")
    assert engine.claim_survives("PROTO_X7") is True
    assert engine.active_support_sets("PROTO_X7") == {frozenset({"B", "HEALTHY_ROOT"})}
