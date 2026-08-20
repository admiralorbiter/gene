"""Preflight tests for Track B3: Monoculture Multiverse."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.multiverse_generator import MultiverseGenerator


def test_multiverse_generator_16_cells():
    """Verify that all 16 cells are strictly constructed with N=5 docs."""
    gen = MultiverseGenerator()
    cells = gen.generate_all_16_cells()
    assert len(cells) == 16

    for cell in cells:
        assert len(cell.raw_docs) == 5
        assert "QUESTION:" in cell.prompt
        assert "Return strictly JSON" in cell.prompt
        assert cell.majority_protocol in ["PROTO_M4", "PROTO_Q7"]
        assert cell.minority_protocol in ["PROTO_M4", "PROTO_Q7"]
        assert cell.majority_protocol != cell.minority_protocol


def test_multiverse_machine_diff_purity():
    """Verify that machine-diff between matched treatment/control isolates only root tokens."""
    gen = MultiverseGenerator()
    
    # Compare independent vs monoculture holding station, token, order constant
    c_indep = gen.build_prompt("VELORA", "independent", "M4_majority", "forward")
    c_mono = gen.build_prompt("VELORA", "monoculture", "M4_majority", "forward")

    diff = gen.compute_machine_diff(c_indep.prompt, c_mono.prompt)
    diff_text = "".join(diff)

    # Both must have 5 docs
    assert len(c_indep.raw_docs) == len(c_mono.raw_docs) == 5
    # The diff should isolate the source phrasing differences in docs 2 and 3
    assert "root_R2" in diff_text or "root_R3" in diff_text
    assert "field log" in diff_text or "Archive relay" in diff_text
