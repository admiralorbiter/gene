"""Preflight tests for Track H: Coalition Causality & Overdetermination."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.coalition_causality import CoalitionCausalityEngine


def test_track_h_single_path_lattice():
    """AB -> C: Any single knockout destroys C."""
    engine = CoalitionCausalityEngine()
    
    # 0 knockouts
    r0 = engine.evaluate_intervention("single_path", set())
    assert r0.formal_support_survives is True
    assert r0.expected_claim == "PROTO_X7"

    # Single knockout A
    rA = engine.evaluate_intervention("single_path", {"A"})
    assert rA.formal_support_survives is False
    assert rA.expected_claim == "UNKNOWN"

    # Single knockout B
    rB = engine.evaluate_intervention("single_path", {"B"})
    assert rB.formal_support_survives is False
    assert rB.expected_claim == "UNKNOWN"


def test_track_h_redundant_support_overdetermination():
    """AB + DE -> C: Single knockout masks effect; coalition knockout {A,D} destroys C."""
    engine = CoalitionCausalityEngine()

    # Single knockout A -> DE survives!
    rA = engine.evaluate_intervention("redundant_independent", {"A"})
    assert rA.formal_support_survives is True
    assert rA.expected_claim == "PROTO_X7"
    assert rA.surviving_formal_paths == [["D", "E"]]

    # Single knockout D -> AB survives!
    rD = engine.evaluate_intervention("redundant_independent", {"D"})
    assert rD.formal_support_survives is True
    assert rD.expected_claim == "PROTO_X7"
    assert rD.surviving_formal_paths == [["A", "B"]]

    # Minimal Hitting Coalition Knockout {A, D} -> Both paths die!
    rAD = engine.evaluate_intervention("redundant_independent", {"A", "D"})
    assert rAD.formal_support_survives is False
    assert rAD.expected_claim == "UNKNOWN"
    assert len(rAD.surviving_formal_paths) == 0


def test_track_h_shared_root_collapse():
    """AX + AY -> C: Knockout of shared root A destroys both apparent paths."""
    engine = CoalitionCausalityEngine()

    rA = engine.evaluate_intervention("shared_root", {"A"})
    assert rA.formal_support_survives is False
    assert rA.expected_claim == "UNKNOWN"

    # Knockout of X alone -> AY survives!
    rX = engine.evaluate_intervention("shared_root", {"X"})
    assert rX.formal_support_survives is True
    assert rX.expected_claim == "PROTO_X7"
