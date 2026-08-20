"""Unit tests for Track B: Epistemic Monoculture vs Independent Roots."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore.run_track_b_monoculture import calculate_effective_roots, simulate_monoculture_preflight, build_track_b_prompt


def test_calculate_effective_roots():
    """Verify N_eff = 1 / sum(p_r^2) calculation."""
    # Single root with 4 memories -> N_eff = 1.0
    assert calculate_effective_roots({"root_1": 4}) == 1.0

    # 4 independent roots with 1 memory each -> N_eff = 4.0
    assert calculate_effective_roots({"r1": 1, "r2": 1, "r3": 1, "r4": 1}) == 4.0

    # 2 roots: 1 root has 3 memories, 1 root has 1 memory -> p1=0.75, p2=0.25 -> sum_sq = 0.5625 + 0.0625 = 0.625 -> N_eff = 1.6
    assert abs(calculate_effective_roots({"r1": 3, "r2": 1}) - 1.6) < 1e-9


def test_monoculture_preflight_conditions():
    """Verify preflight condition structures and ratios."""
    preflight = simulate_monoculture_preflight()
    assert "monoculture" in preflight
    assert "diverse_roots" in preflight
    assert "inverted_diversity" in preflight

    # Monoculture has N_eff_X = 1.0 and N_eff_Y = 1.0 despite 3:1 raw ratio
    assert preflight["monoculture"]["n_eff_x"] == 1.0
    assert preflight["monoculture"]["n_eff_y"] == 1.0

    # Inverted diversity has N_eff_Y = 2.0 > N_eff_X = 1.0 despite 3:2 raw count in favor of X
    assert preflight["inverted_diversity"]["n_eff_y"] == 2.0
    assert preflight["inverted_diversity"]["n_eff_x"] == 1.0


def test_prompt_generation_track_b():
    """Verify prompt formatting and schema enforcement."""
    p_mono = build_track_b_prompt("VELORA", "monoculture")
    assert "VELORA" in p_mono
    assert "Station Director Kira" in p_mono
    assert "adjudicated_protocol" in p_mono

    p_inv = build_track_b_prompt("KESTREL", "inverted_diversity")
    assert "KESTREL" in p_inv
    assert "report_05" in p_inv
