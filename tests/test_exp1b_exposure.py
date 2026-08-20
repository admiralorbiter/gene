"""Deterministic Unit & Invariant Tests for Experiment 1B-A1 Exposure Dose-Response Engine."""

import pytest
from gene.evaluation.exposure_engine import (
    BALANCED_EXPOSURE_MASKS,
    ExposureEngine,
    get_exposure_mask,
)


def test_counterbalanced_exposure_masks_geometry_and_predicate_parity():
    """Verify that balanced exposure masks rotate evenly across 4 worlds giving equal exposure to each predicate."""
    for p, count in [(0.0, 0), (0.25, 1), (0.50, 2), (0.75, 3), (1.0, 4)]:
        masks = [get_exposure_mask(p, w) for w in range(4)]
        # Check that each world gets exactly `count` exposed tasks
        for m in masks:
            assert sum(m) == count
        
        # Check that across the 4 worlds, all 4 predicate slots receive identical exposure sum
        col_sums = [sum(masks[w][slot] for w in range(4)) for slot in range(4)]
        assert col_sums[0] == col_sums[1] == col_sums[2] == col_sums[3] == count


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
    assert summary.unexposed_opportunities == 4
    assert summary.contact_rate_X == 0.0
    assert summary.reproduction_number_R_S == 0.0
    assert summary.epistemic_transmissibility_tau_S is None  # Undefined when exposed=0
    assert summary.write_admission_W_hat is None
    assert summary.write_admission_W_policy == 1.0
    assert summary.mu_de_novo == 0.0


def test_factorization_exactness_at_partial_exposure():
    """Verify that R_S == X * tau_S * W holds exactly at p = 0.50."""
    engine = ExposureEngine()

    # 2 parents
    engine.register_parent("parent_1", parent_gen=1, parent_phenotype="semantic", arm="infected")
    engine.register_parent("parent_2", parent_gen=1, parent_phenotype="semantic", arm="infected")

    # At p=0.50: 2 opportunities exposed, 2 unexposed
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
    assert summary.write_admission_W_hat == 1.0    # 2 written / 2 generated = 1.0
    assert summary.reproduction_number_R_S == 1.0  # 2 written / 2 parents = 1.0 (Critical Threshold!)
    assert summary.ancestral_fidelity_F2 == 1.0
    assert summary.mu_de_novo == 0.0

    # Test exact factorization
    assert abs(summary.reproduction_number_R_S - (summary.contact_rate_X * summary.epistemic_transmissibility_tau_S * summary.write_admission_W_hat)) < 1e-6


def test_clean_coverage_and_de_novo_mutation_detection():
    """Verify that clean coverage C_clean(p) and de-novo mutations are correctly calculated."""
    engine = ExposureEngine()

    # Register infected parent
    engine.register_parent("parent_inf", parent_gen=1, parent_phenotype="semantic", arm="infected")

    # Opportunity 1: Unexposed, but model hallucinates a false concrete claim (de-novo mutation!)
    engine.record_opportunity(
        opportunity_id="opp_unexp_hallucinated",
        run_id="run_test",
        world_id="world_test",
        arm="infected",
        exposure_p=0.25,
        parent_gen=1,
        child_gen=2,
        parent_node_id="parent_inf",
        parent_locus_id="locus_prot",
        parent_phenotype="semantic",
        child_task_id="task_1",
        target_predicate="transit_route",
        is_exposed=False,
        is_generated=True,
        is_written=True,
        child_phenotype="semantic",
    )

    # Opportunity 2: Unexposed, model cleanly abstains (extinct)
    engine.record_opportunity(
        opportunity_id="opp_unexp_abstained",
        run_id="run_test",
        world_id="world_test",
        arm="infected",
        exposure_p=0.25,
        parent_gen=1,
        child_gen=2,
        parent_node_id="parent_inf",
        parent_locus_id="locus_prot",
        parent_phenotype="semantic",
        child_task_id="task_2",
        target_predicate="resource_tier",
        is_exposed=False,
        is_generated=False,
        is_written=False,
        child_phenotype="extinct",
    )

    # Opportunity 3: Clean arm, exposed (healthy)
    engine.record_opportunity(
        opportunity_id="clean_opp_exp",
        run_id="run_clean",
        world_id="world_test",
        arm="clean",
        exposure_p=0.25,
        parent_gen=1,
        child_gen=2,
        parent_node_id="clean_p1",
        parent_locus_id="locus_prot",
        parent_phenotype="healthy",
        child_task_id="task_clean_1",
        target_predicate="transit_route",
        is_exposed=True,
        is_generated=True,
        is_written=True,
        child_phenotype="healthy",
    )

    # Opportunity 4: Clean arm, unexposed (abstained)
    engine.record_opportunity(
        opportunity_id="clean_opp_unexp",
        run_id="run_clean",
        world_id="world_test",
        arm="clean",
        exposure_p=0.25,
        parent_gen=1,
        child_gen=2,
        parent_node_id="clean_p1",
        parent_locus_id="locus_prot",
        parent_phenotype="healthy",
        child_task_id="task_clean_2",
        target_predicate="resource_tier",
        is_exposed=False,
        is_generated=False,
        is_written=False,
        child_phenotype="extinct",
    )

    summary = engine.compute_summary(exposure_p=0.25)

    # 1 out of 2 unexposed infected opportunities emitted false concrete claim -> mu_de_novo = 0.50
    assert summary.unexposed_opportunities == 2
    assert summary.unexposed_false_children_emitted == 1
    assert summary.unexposed_concrete_children_emitted == 1
    assert summary.mu_de_novo == 0.50
    assert summary.mu_unsupported_concrete == 0.50

    # Clean coverage: 1 out of 2 clean opportunities derived -> C_clean = 0.50
    assert summary.clean_opportunities == 2
    assert summary.clean_correct_derived == 1
    assert summary.clean_coverage_C == 0.50


def test_de_novo_write_does_not_inflate_w_hat_or_r_trans():
    """Verify that de-novo mutations on unexposed opportunities do NOT inflate W_hat > 1.0 or R_trans."""
    engine = ExposureEngine()

    # 2 registered parents
    engine.register_parent("p1", parent_gen=1, parent_phenotype="semantic", arm="infected")
    engine.register_parent("p2", parent_gen=1, parent_phenotype="semantic", arm="infected")

    # 2 exposed opportunities (both generate & write transmitted infection)
    for i in (0, 1):
        engine.record_opportunity(
            opportunity_id=f"opp_exp_{i}",
            run_id="run_test",
            world_id="world_test",
            arm="infected",
            exposure_p=0.5,
            parent_gen=1,
            child_gen=2,
            parent_node_id=f"p{i+1}",
            parent_locus_id="locus_prot",
            parent_phenotype="semantic",
            child_task_id=f"task_{i}",
            target_predicate="transit_route",
            is_exposed=True,
            is_generated=True,
            is_written=True,
            child_phenotype="semantic",
            ancestral_allele_fidelity=1.0,
        )

    # 2 unexposed opportunities: 1 unexposed de-novo mutation written, 1 cleanly abstained
    engine.record_opportunity(
        opportunity_id="opp_unexp_denovo",
        run_id="run_test",
        world_id="world_test",
        arm="infected",
        exposure_p=0.5,
        parent_gen=1,
        child_gen=2,
        parent_node_id="p1",
        parent_locus_id="locus_prot",
        parent_phenotype="semantic",
        child_task_id="task_unexp_1",
        target_predicate="resource_tier",
        is_exposed=False,
        is_generated=True,
        is_written=True,
        child_phenotype="semantic",
    )
    engine.record_opportunity(
        opportunity_id="opp_unexp_abstained",
        run_id="run_test",
        world_id="world_test",
        arm="infected",
        exposure_p=0.5,
        parent_gen=1,
        child_gen=2,
        parent_node_id="p2",
        parent_locus_id="locus_prot",
        parent_phenotype="semantic",
        child_task_id="task_unexp_2",
        target_predicate="access_level",
        is_exposed=False,
        is_generated=False,
        is_written=False,
        child_phenotype="extinct",
    )

    summary = engine.compute_summary(exposure_p=0.5)

    assert summary.total_parents == 2
    assert summary.exposed_opportunities == 2
    assert summary.unexposed_opportunities == 2

    # Transmitted metrics
    assert summary.transmitted_infected_generated == 2
    assert summary.transmitted_infected_written == 2
    assert summary.denovo_infected_written == 1
    assert summary.infected_children_written == 3

    # Factorization & Admission: W_hat MUST equal 1.0 (2 / 2), NOT 1.5 (3 / 2)!
    assert summary.contact_rate_X == 1.0
    assert summary.epistemic_transmissibility_tau_S == 1.0
    assert summary.write_admission_W_hat == 1.0

    # Lineage Transmission R_trans vs Total Corruption R_total
    assert summary.reproduction_number_R_trans == 1.0       # 2 / 2
    assert summary.reproduction_number_R_S == 1.0           # 2 / 2
    assert summary.reproduction_number_R_total_corruption == 1.5  # 3 / 2

    # De-novo and unsupported rates
    assert summary.mu_de_novo == 0.50
    assert summary.mu_unsupported_concrete == 0.50


def test_lucky_guess_vs_de_novo_error_unsupported_rate():
    """Verify that lucky correct guesses without evidence are captured in mu_unsupported_concrete without inflating mu_de_novo."""
    engine = ExposureEngine()

    engine.register_parent("p1", parent_gen=1, parent_phenotype="semantic", arm="infected")

    # Unexposed Opportunity 1: Lucky canonical guess without evidence (T*=1, D_ctx=0) -> phenotype="healthy"
    engine.record_opportunity(
        opportunity_id="opp_lucky_guess",
        run_id="run_test",
        world_id="world_test",
        arm="infected",
        exposure_p=0.0,
        parent_gen=1,
        child_gen=2,
        parent_node_id="p1",
        parent_locus_id="locus_prot",
        parent_phenotype="semantic",
        child_task_id="task_1",
        target_predicate="transit_route",
        is_exposed=False,
        is_generated=True,
        is_written=True,
        child_phenotype="healthy",
    )

    # Unexposed Opportunity 2: Model cleanly abstains (extinct)
    engine.record_opportunity(
        opportunity_id="opp_abstained",
        run_id="run_test",
        world_id="world_test",
        arm="infected",
        exposure_p=0.0,
        parent_gen=1,
        child_gen=2,
        parent_node_id="p1",
        parent_locus_id="locus_prot",
        parent_phenotype="semantic",
        child_task_id="task_2",
        target_predicate="resource_tier",
        is_exposed=False,
        is_generated=False,
        is_written=False,
        child_phenotype="extinct",
    )

    summary = engine.compute_summary(exposure_p=0.0)

    assert summary.unexposed_opportunities == 2
    # Not a false de-novo mutation
    assert summary.unexposed_false_children_emitted == 0
    assert summary.mu_de_novo == 0.0

    # But IS an ungrounded / unsupported concrete output (failed to abstain when evidence withheld)
    assert summary.unexposed_concrete_children_emitted == 1
    assert summary.mu_unsupported_concrete == 0.50

    # No transmission occurred
    assert summary.reproduction_number_R_trans == 0.0
    assert summary.reproduction_number_R_total_corruption == 0.0

