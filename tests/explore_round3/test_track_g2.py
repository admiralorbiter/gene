"""Preflight tests for Track G2: Clean Non-Destructive Support Immunity."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore_round3.run_track_g2_immunity import (
    apply_governance_retrieval,
    build_track_g2_governance_prompt,
)


def test_track_g2_zero_auxiliary_count_leak():
    """Verify that Track G2 prompt schema contains no auxiliary numeric counts or answer leaks."""
    prompt, _, _ = build_track_g2_governance_prompt("VELORA", "support_aware_independent_preservation")
    schema_section = prompt[prompt.find("schema"):]
    assert "surviving_paths_count" not in schema_section
    assert "0" not in schema_section
    assert "1" not in schema_section


def test_track_g2_governance_5_arms_exactness():
    """Verify all 5 governance conditions produce exact formal expectations and dynamic rule bindings."""
    # 1. Independent baseline -> PROTO_X7 (rule 2 binds to S2)
    p1, _, e1 = build_track_g2_governance_prompt("VELORA", "baseline_independent")
    assert e1 == "PROTO_X7"
    assert "reports_to(person, S2)" in p1
    assert "MEM_01" in p1 and "MEM_03" in p1

    # 2. Shared baseline -> PROTO_X7 (rule 2 dynamically binds to S1, forming true AX+AY)
    p2, _, e2 = build_track_g2_governance_prompt("VELORA", "baseline_shared")
    assert e2 == "PROTO_X7"
    assert "reports_to(person, S1)" in p2
    assert "MEM_01" in p2 and "MEM_03" in p2

    # 3. Naive Lineage Quarantine -> Autoimmunity -> UNKNOWN
    p3, _, e3 = build_track_g2_governance_prompt("VELORA", "naive_lineage_quarantine")
    assert e3 == "UNKNOWN"
    assert "MEM_QUARANTINED" in p3

    # 4. Support-Aware Independent Preservation -> Preserved -> PROTO_X7
    p4, _, e4 = build_track_g2_governance_prompt("VELORA", "support_aware_independent_preservation")
    assert e4 == "PROTO_X7"
    assert "MEM_03: Vael is sector lead" in p4
    assert "MEM_01" not in p4  # Path 1 pruned!

    # 5. Support-Aware Shared Collapse -> Correct Collapse -> UNKNOWN
    p5, _, e5 = build_track_g2_governance_prompt("VELORA", "support_aware_shared_collapse")
    assert e5 == "UNKNOWN"
    assert "MEM_INACTIVATED" in p5
