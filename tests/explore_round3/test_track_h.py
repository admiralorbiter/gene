"""Preflight tests for Track H: Coalition Causality & Overdetermination."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.coalition_causality import CoalitionCausalityEngine


def test_track_h_recombinant_support_16_points():
    """AB + DE -> C: Verify formal survival across all 2^4 = 16 lattice points."""
    engine = CoalitionCausalityEngine()
    results = engine.generate_full_lattice("redundant_independent")
    assert len(results) == 16

    for r in results:
        active = set(r.active_parents)
        path1_ok = ("A" in active) and ("B" in active)
        path2_ok = ("D" in active) and ("E" in active)
        expected_survives = path1_ok or path2_ok
        assert r.formal_support_survives == expected_survives
        if expected_survives:
            assert r.expected_claim == "PROTO_X7"
        else:
            assert r.expected_claim == "UNKNOWN"


def test_track_h_extract_minimal_causal_coalitions():
    """Verify that simulated behavioral results recover S_C = {{A, B}, {D, E}}."""
    engine = CoalitionCausalityEngine()

    # Generate full 16-point simulated behavioral map
    results = engine.generate_full_lattice("redundant_independent")
    behavioral_results = {
        tuple(r.knocked_out_parents): r.expected_claim for r in results
    }

    s_c = engine.extract_minimal_causal_coalitions("redundant_independent", behavioral_results)
    assert len(s_c) == 2
    assert {"A", "B"} in s_c
    assert {"D", "E"} in s_c
