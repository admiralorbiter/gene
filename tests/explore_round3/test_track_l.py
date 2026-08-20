"""Preflight tests for Track L: Independence Laundering."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.independence_laundering import IndependenceLaunderingEngine


def test_independence_laundering_cascade():
    """Verify progressive inflation of perceived roots across transformation stages."""
    engine = IndependenceLaunderingEngine()
    cascade = engine.generate_cascade("VELORA", "PROTO_ALPHA")

    assert len(cascade) == 4
    assert cascade[0].stage_name == "G0_True_Root"
    assert cascade[0].true_root_count == 1
    assert cascade[0].perceived_root_count == 1.0

    assert cascade[3].stage_name == "G3_Fully_Laundered_Consensus"
    assert cascade[3].true_root_count == 1
    assert cascade[3].perceived_root_count == 4.0
    assert cascade[3].inflation_ratio == 4.0
