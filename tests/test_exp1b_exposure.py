"""Deterministic Unit & Invariant Tests for Experiment 1B-A1 Exposure Dose-Response Engine."""

import pytest
from gene.evaluation.exposure_engine import EXPOSURE_MASKS, ExposureEngine


def test_balanced_exposure_masks_geometry():
    """Verify that balanced exposure masks produce exact target contact proportions."""
    assert sum(EXPOSURE_MASKS[0.00]) == 0
    assert sum(EXPOSURE_MASKS[0.25]) == 1
    assert sum(EXPOSURE_MASKS[0.50]) == 2
    assert sum(EXPOSURE_MASKS[0.75]) == 3
    assert sum(EXPOSURE_MASKS[1.00]) == 4


def test_opportunity_tracker_unbiased_denominator_at_zero_exposure():
    """Verify that semantic parents with 0 exposures remain in the denominator to prevent R_S upward bias."""
    engine = ExposureEngine()

    # Register 2 semantic G1 parents
    engine.register_parent("parent_1", parent_gen=1, parent_phenotype="semantic", arm="infected")
    engine.register_parent("parent_2", parent_gen=1, parent_phenotype="semantic", arm="infected")

    # Record 4 unexposed opportunities (p=0.0)
    for i in range(4):
        p_id = "parent_1" if i < 2 else "parent_2"
        engine.record_opportunity(
            opportunity_id=f"opp_{i}",
            run_id="run_test",
            world_id="world_test",
            arm="infected",
            exposure_p=0.0,
            parent_gen=1,
            child_gen=2,
            parent_node_id=p_id,
            parent_locus_id="locus_prot",
            parent_phenotype="semantic",
            child_task_id=f"task_{i}",
            target_predicate="transit_route",
            is_exposed=False,
            is_generated=False,
            is_written=False,
            child_phenotype="extinct",
        )

    summary = engine.compute_summary(exposure_p=0.0)

    assert summary.total_parents == 2
    assert summary.exposed_opportunities == 0
    assert summary.contact_rate_X == 0.0
    assert summary.reproduction_number_R_S == 0.0
    assert summary.epistemic_transmissibility_tau_S is None  # Undefined when exposed=0


def test_factorization_exactness_at_partial_exposure():
    """Verify that R_S == X * tau_S * W holds exactly at p = 0.50."""
    engine = ExposureEngine()

    # 2 parents
    engine.register_parent("parent_1", parent_gen=1, parent_phenotype="semantic", arm="infected")
    engine.register_parent("parent_2", parent_gen=1, parent_phenotype="semantic", arm="infected")

    # At p=0.50: 2 opportunities exposed, 2 unexposed
    # Parent 1: 1 exposed (produces infected child), 1 unexposed
    # Parent 2: 1 exposed (produces infected child), 1 unexposed
    for i in range(4):
        p_id = "parent_1" if i < 2 else "parent_2"
        is_exp = (i in (0, 2))
        is_gen = is_exp
        is_wri = is_gen
        engine.record_opportunity(
            opportunity_id=f"opp_{i}",
            run_id="run_test",
            world_id="world_test",
            arm="infected",
            exposure_p=0.5,
            parent_gen=1,
            child_gen=2,
            parent_node_id=p_id,
            parent_locus_id="locus_prot",
            parent_phenotype="semantic",
            child_task_id=f"task_{i}",
            target_predicate="transit_route",
            is_exposed=is_exp,
            is_generated=is_gen,
            is_written=is_wri,
            child_node_id=f"child_{i}" if is_wri else None,
            child_phenotype="semantic" if is_exp else "extinct",
            ancestral_allele_fidelity=1.0 if is_exp else None,
        )

    summary = engine.compute_summary(exposure_p=0.5)

    assert summary.total_parents == 2
    assert summary.exposed_opportunities == 2
    assert summary.contact_rate_X == 1.0       # 2 exposures / 2 parents = 1.0
    assert summary.epistemic_transmissibility_tau_S == 1.0 # 2 generated / 2 exposed = 1.0
    assert summary.write_admission_W == 1.0    # 2 written / 2 generated = 1.0
    assert summary.reproduction_number_R_S == 1.0  # 2 written / 2 parents = 1.0 (Critical Threshold!)
    assert summary.ancestral_fidelity_F2 == 1.0

    # Test exact factorization
    assert abs(summary.reproduction_number_R_S - (summary.contact_rate_X * summary.epistemic_transmissibility_tau_S * summary.write_admission_W)) < 1e-6


def test_clean_cognitive_utility_and_abstention():
    """Verify that clean utility U_clean(p) accurately reflects task accuracy and masked abstention."""
    engine = ExposureEngine()

    # At p=0.25: 1 task exposed (healthy derived), 3 tasks unexposed (correctly abstained)
    for i in range(4):
        is_exp = (i == 0)
        engine.record_opportunity(
            opportunity_id=f"clean_opp_{i}",
            run_id="run_clean",
            world_id="world_test",
            arm="clean",
            exposure_p=0.25,
            parent_gen=1,
            child_gen=2,
            parent_node_id="clean_p1",
            parent_locus_id="locus_prot",
            parent_phenotype="healthy",
            child_task_id=f"task_{i}",
            target_predicate="transit_route",
            is_exposed=is_exp,
            is_generated=is_exp,
            is_written=is_exp,
            child_phenotype="healthy" if is_exp else "extinct",
        )

    summary = engine.compute_summary(exposure_p=0.25)

    assert summary.clean_opportunities == 4
    assert summary.clean_correct_derived == 1
    assert summary.clean_abstained_when_masked == 3
    assert summary.clean_utility_U == 0.25  # 1 / 4 = 25% cognitive utility
