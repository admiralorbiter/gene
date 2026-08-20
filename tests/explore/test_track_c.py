"""Unit tests for Track C: Transformation Depth and Causal Provenance Decay."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore.run_track_c_provenance_depth import simulate_depth_closure, build_track_c_prompt


def test_depth_closure_preflight():
    """Verify 6-step deterministic symbolic closure for Kira and Tal."""
    clean = simulate_depth_closure("KIRA")
    mut = simulate_depth_closure("TAL")

    # Depth 1: Protocol
    assert clean[1]["derived_value"] == "PROTO_X7"
    assert mut[1]["derived_value"] == "PROTO_Q2"

    # Depth 2: Clearance
    assert clean[2]["derived_value"] == "CLEAR_LVL_1"
    assert mut[2]["derived_value"] == "CLEAR_LVL_2"

    # Depth 3: Route
    assert clean[3]["derived_value"] == "ROUTE_ALPHA"
    assert mut[3]["derived_value"] == "ROUTE_BETA"

    # Depth 4: Access Tier
    assert clean[4]["derived_value"] == "TIER_PRIORITY"
    assert mut[4]["derived_value"] == "TIER_RESTRICTED"

    # Depth 5: Audit Mode
    assert clean[5]["derived_value"] == "AUDIT_EXPEDITE"
    assert mut[5]["derived_value"] == "AUDIT_MANDATORY"


def test_prompt_generation_track_c():
    """Verify prompt formatting up to depth G5."""
    p_g1 = build_track_c_prompt("VELORA", 1, "KIRA")
    assert "G1" in p_g1
    assert "protocol" in p_g1

    p_g5 = build_track_c_prompt("KESTREL", 5, "TAL")
    assert "G5" in p_g5
    assert "audit_mode" in p_g5
    assert "inspection_cycle" in p_g5
