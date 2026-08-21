"""Tests for Round 7 Ingress Sidecars (Stage 7A.3)."""

from gene.benchmarks.ingress_sidecars.candidate_miss import run_candidate_miss_assay
from gene.benchmarks.ingress_sidecars.role_distractor import run_role_distractor_assay
from gene.benchmarks.ingress_sidecars.paired_authority import run_paired_authority_assay
from gene.benchmarks.ingress_sidecars.live_counterbalancing_plan import generate_candidate_permutations_plan
from gene.benchmarks.ingress_sidecars.probe_separation import run_probe_separation_assay


def test_candidate_miss_sidecar():
    res = run_candidate_miss_assay()
    assert res["pass"] is True


def test_role_distractor_sidecar():
    res = run_role_distractor_assay()
    assert res["pass"] is True


def test_paired_authority_sidecar():
    res = run_paired_authority_assay()
    assert res["pass"] is True


def test_live_counterbalancing_schedule():
    schedule = generate_candidate_permutations_plan()
    assert len(schedule) == 16


def test_probe_separation_8_worlds_sidecar():
    res = run_probe_separation_assay()
    assert res["n_worlds"] == 8
    assert res["has_decoupled_governance_raw"] is True
    assert res["has_decoupled_premise_raw"] is True
    assert res["has_decoupled_causal_raw"] is True
    assert res["has_redundant_rescue_raw"] is True
    for w_id, corr in res["correctness_profiles"].items():
        assert corr == (1, 1, 1, 1), f"World {w_id} correctness profile {corr} != (1,1,1,1)"

