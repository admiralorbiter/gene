"""Preflight tests for Track B3: Monoculture Multiverse."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.multiverse_generator import MultiverseGenerator
from scripts.explore_round3.run_track_b3_multiverse import get_balanced_replay_subsets


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
    """Verify that machine-diff between matched treatment/control isolates strictly root tokens."""
    gen = MultiverseGenerator()
    
    # Compare independent vs monoculture holding station, token, order constant
    c_indep = gen.build_prompt("VELORA", "independent", "M4_majority", "forward")
    c_mono = gen.build_prompt("VELORA", "monoculture", "M4_majority", "forward")

    diff = gen.compute_machine_diff(c_indep.prompt, c_mono.prompt)
    diff_text = "".join(diff)

    # Both must have 5 docs
    assert len(c_indep.raw_docs) == len(c_mono.raw_docs) == 5
    # The diff should isolate ONLY root_R2 and root_R3 changing to root_R1
    assert "-- DOC_02: Source root_R2" in diff_text
    assert "+- DOC_02: Source root_R1" in diff_text
    assert "-- DOC_03: Source root_R3" in diff_text
    assert "+- DOC_03: Source root_R1" in diff_text
    # Zero phrasing differences
    assert "field log" not in diff_text
    assert "Archive relay" not in diff_text


def test_multiverse_replay_subsets_four_factor_balance():
    """Machine-check that exact-replay and seed-perturb subsets have count == 2 across all 4 factors."""
    gen = MultiverseGenerator()
    cells = gen.generate_all_16_cells()
    exact_sub, perturb_sub = get_balanced_replay_subsets(cells)

    for subset_name, sub in [("exact", exact_sub), ("perturb", perturb_sub)]:
        assert len(sub) == 4, f"{subset_name} subset length != 4"
        
        # 1. Station balance (2 VELORA, 2 KESTREL)
        st_counts = {st: sum(1 for c in sub if c.station == st) for st in ["VELORA", "KESTREL"]}
        assert st_counts == {"VELORA": 2, "KESTREL": 2}, f"{subset_name} station counts unbalanced: {st_counts}"

        # 2. Root structure balance (2 independent, 2 monoculture)
        rs_counts = {rs: sum(1 for c in sub if c.root_structure == rs) for rs in ["independent", "monoculture"]}
        assert rs_counts == {"independent": 2, "monoculture": 2}, f"{subset_name} root structure counts unbalanced: {rs_counts}"

        # 3. Token mapping balance (2 M4_majority, 2 Q7_majority)
        tm_counts = {tm: sum(1 for c in sub if c.token_mapping == tm) for tm in ["M4_majority", "Q7_majority"]}
        assert tm_counts == {"M4_majority": 2, "Q7_majority": 2}, f"{subset_name} token mapping counts unbalanced: {tm_counts}"

        # 4. Doc order balance (2 forward, 2 interleaved)
        do_counts = {do: sum(1 for c in sub if c.doc_order == do) for do in ["forward", "interleaved"]}
        assert do_counts == {"forward": 2, "interleaved": 2}, f"{subset_name} doc order counts unbalanced: {do_counts}"
