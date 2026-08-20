"""Unit tests for Track D: Cross-Model Sentinel Replication."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore.run_track_d_model_sentinel import build_sentinel_prompts


def test_sentinel_prompts_completeness():
    """Verify that all 8 sentinel prompts are well-formed and cover the 4 pairs."""
    prompts = build_sentinel_prompts("VELORA")
    assert len(prompts) == 8

    # Pair 1: Semantic Inheritance
    assert "sentinel_1_clean" in prompts
    assert "sentinel_1_mutated" in prompts
    assert "Kira" in prompts["sentinel_1_clean"]
    assert "Tal" in prompts["sentinel_1_mutated"]

    # Pair 2: Retrieval Gate
    assert "sentinel_2_complete" in prompts
    assert "sentinel_2_broken" in prompts
    assert "protocol(VELORA, PROTO_X7)" in prompts["sentinel_2_complete"]
    assert "protocol(VELORA, PROTO_X7)" not in prompts["sentinel_2_broken"]

    # Pair 3: Pseudo-path
    assert "sentinel_3_wrong_route" in prompts
    assert "sentinel_3_zero_route" in prompts

    # Pair 4: Proofreading Gate
    assert "sentinel_4_valid_cert" in prompts
    assert "sentinel_4_cross_binding" in prompts
    assert "KESTREL" in prompts["sentinel_4_cross_binding"]
