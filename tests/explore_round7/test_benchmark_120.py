"""Test suite for Thread B 120-World Benchmark & Comparative Arms."""

from gene.benchmarks.ingress_120.generator import generate_120_worlds
from gene.benchmarks.ingress_120.oracle import BenchmarkOracle
from gene.benchmarks.ingress_120.evaluator import run_benchmark_120_all_arms


def test_120_worlds_generator_geometry():
    worlds = generate_120_worlds()
    assert len(worlds) == 120
    case_ids = [w.case_id for w in worlds]
    assert len(case_ids) == len(set(case_ids)), "Case IDs must be strictly unique"

    # Verify balance: 24 of each binding condition (5 x 24 = 120)
    for b_cond in ["EXACT_CANONICAL", "SURFACE_ALIAS", "CANDIDATE_COLLISION", "ROLE_DISTRACTOR", "NOVEL_ENTITY"]:
        count = sum(1 for w in worlds if w.binding_condition == b_cond)
        assert count == 24


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

    assert admissible_count + inadmissible_count == 120
    # Admissible cases: 3 binding conditions (EXACT, ALIAS, ROLE) x 4 modes x 3 temp x 1 direct source = 36 cases
    assert admissible_count == 36
    assert inadmissible_count == 84


def test_comparative_arms_execution_and_a4_mastery():
    results = run_benchmark_120_all_arms()

    a0 = results["A0_Top1_Blind_Write"]
    a1 = results["A1_Canonicalize_Only"]
    a2 = results["A2_Candidate_Aware"]
    a3 = results["A3_Authority_Aware"]
    a4 = results["A4_Full_GENE_Ingress"]

    # A0 and A1 suffer catastrophic FDAR (blind writes)
    assert a0["fdar_global"] >= 0.50
    assert a1["fdar_global"] >= 0.50

    # A2 fixes ambiguity/novelty collapse but suffers unauthorized promotion
    assert a2["fdar_novel"] == 0.0
    assert a2["fdar_ambiguity"] == 0.0
    assert a2["fdar_authority"] >= 0.50

    # A3 fixes authority promotion but suffers ambiguity/novelty collapse
    assert a3["fdar_authority"] == 0.0
    assert a3["fdar_ambiguity"] >= 0.50

    # A4 achieves 100% WorldPass rate, FDAR = 0.0%, and SAC = 100.0%
    assert a4["world_pass_rate"] == 1.0
    assert a4["fdar_global"] == 0.0
    assert a4["sac_rate"] == 1.0
    assert a4["upr_rate"] == 1.0
