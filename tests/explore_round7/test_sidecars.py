"""Unit tests for Thread D Disaggregated Sidecars."""

from gene.benchmarks.ingress_sidecars.candidate_miss import run_candidate_miss_assay
from gene.benchmarks.ingress_sidecars.role_distractor import run_role_distractor_assay
from gene.benchmarks.ingress_sidecars.paired_authority import run_paired_authority_assay
from gene.benchmarks.ingress_sidecars.live_counterbalancing_plan import generate_candidate_permutations_plan


def test_candidate_miss_sidecar():
    res = run_candidate_miss_assay()
    assert res["pass"] is True
    assert res["novel_status"] == "DEFER"
    assert res["miss_status"] == "REJECT"


def test_role_distractor_sidecar():
    res = run_role_distractor_assay()
    assert res["pass"] is True
    assert res["role_distractor_status"] == "ADMIT"
    assert res["true_ambiguity_status"] == "DEFER"


def test_paired_authority_sidecar():
    res = run_paired_authority_assay()
    assert res["pass"] is True
    assert res["results"]["PLATFORM_ATTESTED"] == "ADMIT"
    assert res["results"]["USER_DIRECT"] == "ADMIT"
    assert res["results"]["THIRD_PARTY_QUOTED"] == "REJECT"
    assert res["results"]["MODEL_DERIVED"] == "REJECT"


def test_live_counterbalancing_schedule():
    plan = generate_candidate_permutations_plan()
    assert len(plan) == 16
    positions = [p["gold_slot_position"] for p in plan]
    # Each of the 4 slots must appear exactly 4 times
    for slot in [0, 1, 2, 3]:
        assert positions.count(slot) == 4
