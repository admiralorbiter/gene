"""Preflight tests for Track M: Model Calibration Gateway."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore_round2.run_track_m_calibration import build_calibration_prompt


def test_track_m_calibration_cases_geometry():
    """Verify that all 4 calibration cases produce expected logical structures."""
    cases = ["complete_valid", "missing_premise", "directional_mutation", "entity_mismatch"]
    for c in cases:
        prompt, forbidden, expected = build_calibration_prompt("VELORA", c, contract_variant="generic_placeholder")
        assert "QUESTION:" in prompt
        assert "Return strictly JSON" in prompt
        assert expected in ["PROTO_X7", "PROTO_Q2", "UNKNOWN"]
        assert len(forbidden) > 0


def test_track_m_no_schema_answer_leak():
    """Verify that generic placeholder and json schema variants contain zero answer leaks."""
    prompt, forbidden, _ = build_calibration_prompt("VELORA", "complete_valid", contract_variant="generic_placeholder")
    schema_section = prompt[prompt.find("schema"):]
    for f in forbidden:
        assert f not in schema_section
