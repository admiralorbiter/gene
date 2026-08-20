"""Preflight tests for Track L: Independence Laundering."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.independence_laundering import IndependenceLaunderingEngine


def test_independence_laundering_cascade():
    """Verify progressive inflation of perceived roots across transformation stages and 4-root control."""
    engine = IndependenceLaunderingEngine()
    cascade = engine.generate_cascade("VELORA", "PROTO_ALPHA")

    assert len(cascade) == 5
    assert cascade[0].stage_name == "G0_True_1_Root"
    assert cascade[0].true_root_count == 1
    assert cascade[0].reference_naive_count == 1

    assert cascade[3].stage_name == "G3_Fully_Laundered_Consensus"
    assert cascade[3].true_root_count == 1
    assert cascade[3].reference_naive_count == 4

    assert cascade[4].stage_name == "G_True_4_Roots_Control"
    assert cascade[4].true_root_count == 4
    assert cascade[4].reference_naive_count == 4
