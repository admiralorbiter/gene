"""Preflight tests for Track H: Coalition Causality & Overdetermination."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.coalition_causality import CoalitionCausalityEngine


def test_track_h_recombinant_support_11_points():
    """AB + DE -> C: Verify formal survival across all 11 key lattice intervention points."""
    engine = CoalitionCausalityEngine()

    # 1. Baseline (0 knockouts) -> Survives
    r0 = engine.evaluate_intervention("redundant_independent", set())
    assert r0.formal_support_survives is True
    assert r0.expected_claim == "PROTO_X7"

    # 2. Four Single Knockouts ({A}, {B}, {D}, {E}) -> ALL SURVIVE via alternate path!
    for single in [{"A"}, {"B"}, {"D"}, {"E"}]:
        res = engine.evaluate_intervention("redundant_independent", single)
        assert res.formal_support_survives is True
        assert res.expected_claim == "PROTO_X7"

    # 3. Two Path-Isolation Knockouts ({A, B} -> DE survives; {D, E} -> AB survives)
    r_ab = engine.evaluate_intervention("redundant_independent", {"A", "B"})
    assert r_ab.formal_support_survives is True
    assert r_ab.surviving_formal_paths == [["D", "E"]]

    r_de = engine.evaluate_intervention("redundant_independent", {"D", "E"})
    assert r_de.formal_support_survives is True
    assert r_de.surviving_formal_paths == [["A", "B"]]

    # 4. Four Cross-Path Minimal Hitting Sets ({A,D}, {A,E}, {B,D}, {B,E}) -> ALL DIE!
    for hitting_pair in [{"A", "D"}, {"A", "E"}, {"B", "D"}, {"B", "E"}]:
        res = engine.evaluate_intervention("redundant_independent", hitting_pair)
        assert res.formal_support_survives is False
        assert res.expected_claim == "UNKNOWN"


def test_track_h_extract_minimal_causal_coalitions():
    """Verify that simulated behavioral results recover S_C = {{A, B}, {D, E}}."""
    engine = CoalitionCausalityEngine()

    # Perfect formal simulator results
    behavioral_results = {
        (): "PROTO_X7",
        ("A",): "PROTO_X7",
        ("B",): "PROTO_X7",
        ("D",): "PROTO_X7",
        ("E",): "PROTO_X7",
        ("A", "B"): "PROTO_X7",
        ("D", "E"): "PROTO_X7",
        ("A", "D"): "UNKNOWN",
        ("A", "E"): "UNKNOWN",
        ("B", "D"): "UNKNOWN",
        ("B", "E"): "UNKNOWN",
    }

    s_c = engine.extract_minimal_causal_coalitions("redundant_independent", behavioral_results)
    assert len(s_c) == 2
    assert {"A", "B"} in s_c
    assert {"D", "E"} in s_c
