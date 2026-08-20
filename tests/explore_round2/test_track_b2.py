"""Preflight tests for Track B2: Monoculture Hardening."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore_round2.run_track_b2_monoculture import build_track_b2_prompt


def test_track_b2_doc_count_invariance():
    """Verify that every condition produces exactly 5 retrieved reports."""
    conditions = ["concur_X", "conflict_roots_Y", "concur_Y", "conflict_roots_X"]
    for cond in conditions:
        prompt, forbidden = build_track_b2_prompt("VELORA", cond)
        # Count memory lines
        mem_lines = [l for l in prompt.split("\n") if l.startswith("- DOC_")]
        assert len(mem_lines) == 5, f"Condition {cond} had {len(mem_lines)} docs instead of 5"


def test_track_b2_zero_prompt_steering():
    """Verify that prompt contains NO leading instructions regarding independent sources."""
    conditions = ["concur_X", "conflict_roots_Y", "concur_Y", "conflict_roots_X"]
    for cond in conditions:
        prompt, _ = build_track_b2_prompt("VELORA", cond)
        prompt_lower = prompt.lower()
        assert "independent source" not in prompt_lower
        assert "corroboration" not in prompt_lower
        assert "reliability" not in prompt_lower
        assert "evaluate sources" not in prompt_lower


def test_track_b2_no_lexical_answer_leak():
    """Verify that target answers and opaque root IDs do not leak into schema examples."""
    prompt, forbidden = build_track_b2_prompt("VELORA", "concur_X")
    schema_section = prompt[prompt.find("schema"):]
    for f in forbidden:
        assert f not in schema_section
