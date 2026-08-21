"""Test suite for Thread B Stateful 120-World Benchmark (Stage 7A.1)."""

from gene.benchmarks.ingress_120.generator import generate_120_worlds
from gene.benchmarks.ingress_120.oracle import BenchmarkOracle
from gene.benchmarks.ingress_120.evaluator import run_benchmark_120_all_arms


def test_120_worlds_generator_geometry():
    worlds = generate_120_worlds()
    assert len(worlds) == 120
    case_ids = [w.case_id for w in worlds]
    assert len(case_ids) == len(set(case_ids)), "Case IDs must be strictly unique"

    for b_cond in ["EXACT_CANONICAL", "SURFACE_ALIAS", "CANDIDATE_COLLISION", "ROLE_DISTRACTOR", "NOVEL_ENTITY"]:
        count = sum(1 for w in worlds if w.binding_condition == b_cond)
        assert count == 24

    # Verify baseline occurrence exists for every case
    for w in worlds:
        assert w.baseline_occurrence.subject == "Server_Node_1"
        assert w.baseline_occurrence.t_knowledge == 1


def test_oracle_classification_consistency():
    worlds = generate_120_worlds()
    admissible_count = 0
    inadmissible_count = 0

    for w in worlds:
        exp = BenchmarkOracle.evaluate_case(w)
        if exp.is_admissible_ground_truth:
            admissible_count += 1
            assert exp.expected_admission_status == "ADMIT"
        else:
            inadmissible_count += 1
            assert exp.expected_admission_status in ("DEFER", "REJECT")

    assert admissible_count == 36
    assert inadmissible_count == 84


def test_comparative_arms_execution_and_orthogonal_failure_modes():
    results = run_benchmark_120_all_arms()

    a0 = results["A0_Top1_Blind_Write"]
    a1 = results["A1_Canonicalize_Only"]
    a2 = results["A2_Candidate_Aware"]
    a3 = results["A3_Authority_Aware"]
    a4 = results["A4_Full_GENE_Ingress"]

    # A0 and A1 fail on both ambiguity and authority
    assert a0["world_pass_rate"] == 70 / 120
    assert a1["world_pass_rate"] == 70 / 120
    assert a0["fdar_global"] == 60 / 84
    assert a0["fdar_ambiguity_conditional_authorized"] == 1.0
    assert a0["fdar_authority_conditional_resolved"] == 1.0

    # A2 fixes candidate ambiguity/novelty (UPR=100%, FDAR_novel=0%) but fails on unauthorized promotion
    assert a2["world_pass_rate"] == 90 / 120
    assert a2["upr_rate"] == 1.0
    assert a2["fdar_novel"] == 0.0
    assert a2["fdar_authority_conditional_resolved"] == 1.0  # 36/36 = 100% conditional failure on resolved unauthorized claims

    # A3 fixes authority gating (FDAR_authority=0%) but collapses ambiguity
    assert a3["world_pass_rate"] == 110 / 120
    assert a3["fdar_authority_unconditional"] == 0.0
    assert a3["fdar_ambiguity_conditional_authorized"] == 1.0  # 12/12 = 100% conditional collapse on authorized collisions
    assert a3["upr_rate"] == 0.0

    # A4 combines both mechanisms, achieving 100% WorldPass, FDAR=0%, SAC=100%, UPR=100%
    assert a4["world_pass_rate"] == 1.0
    assert a4["fdar_global"] == 0.0
    assert a4["sac_rate"] == 1.0
    assert a4["upr_rate"] == 1.0
