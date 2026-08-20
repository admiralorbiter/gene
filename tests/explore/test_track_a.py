import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore.run_track_a_recovery import simulate_policies_deterministic, build_track_a_prompt


def test_track_a_preflight_invariants():
    """Verify deterministic state transitions and cost metrics."""
    policies = simulate_policies_deterministic()
    assert "root_overwrite" in policies
    assert "lineage_repair" in policies
    assert "revalidate_on_use" in policies

    # Root overwrite retains stale hysteresis
    assert policies["root_overwrite"]["hysteresis_H_g1"] == 1.0
    assert policies["root_overwrite"]["repair_coverage_C_repair"] == 0.0

    # Lineage repair eliminates hysteresis and restores coverage at cost K=3
    assert policies["lineage_repair"]["hysteresis_H_g1"] == 0.0
    assert policies["lineage_repair"]["repair_coverage_C_repair"] == 1.0
    assert policies["lineage_repair"]["nodes_recomputed_K_repair"] == 3

    # Revalidate-on-use achieves same recovery at lower on-demand cost K=1
    assert policies["revalidate_on_use"]["hysteresis_H_g1"] == 0.0
    assert policies["revalidate_on_use"]["repair_coverage_C_repair"] == 1.0
    assert policies["revalidate_on_use"]["nodes_recomputed_K_repair"] == 1.0


def test_track_a_prompt_generation():
    """Verify prompt formatting and schema enforcement."""
    p_proto = build_track_a_prompt("VELORA", "root_overwrite", "protocol")
    assert "VELORA" in p_proto
    assert "PROTOCOL_NAME_OR_UNKNOWN" in p_proto
    assert "mem_proto_stale" in p_proto

    p_route = build_track_a_prompt("KESTREL", "lineage_repair", "route")
    assert "KESTREL" in p_route
    assert "ROUTE_NAME_OR_UNKNOWN" in p_route
    assert "mem_proto_repaired" in p_route
