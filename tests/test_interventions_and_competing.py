"""Deterministic unit and invariant tests for interventions, D1-C micro-worlds, and Schema v2 evaluation."""

import pytest
from gene.evaluation.claims import ClaimEvaluator, StructuredAnswer, StructuredResponse
from gene.evaluation.interventions import (
    CounterfactualOracle,
    InterventionSpec,
    InterventionType,
    apply_intervention,
    compose_interventions,
)
from gene.worlds.competing import generate_d1_c_world
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.renderer import NaturalLanguageRenderer


def test_d1_c_rendering_semantics():
    """Verify that manager(STATION, PERSON) renders as 'PERSON serves as the station manager of STATION.'"""
    bundle = generate_d1_c_world(world_seed=0, rotation_idx=0, rule_perm_idx=0, ecology="C")
    fact_a_text = NaturalLanguageRenderer.render_fact(bundle.fact_a)
    assert "serves as the station manager of" in fact_a_text
    # Station is Velora, Manager is Nerin
    assert fact_a_text == "Nerin serves as the station manager of Velora."

    fact_b_text = NaturalLanguageRenderer.render_fact(bundle.fact_b)
    assert fact_b_text == "Nerin directly reports to Kira."


def test_rotations_and_rule_permutations():
    """Verify that all 3 rotations and 6 rule permutations yield valid forward derivations."""
    for rot in range(3):
        for perm in range(6):
            bundle = generate_d1_c_world(world_seed=42, rotation_idx=rot, rule_perm_idx=perm, ecology="C")
            oracle = Oracle(bundle.world)
            res = oracle.evaluate_triple(bundle.task.target_fact.subject, "uses_protocol", bundle.target_protocol)
            assert res == TruthStatus.TRUE, f"Failed for rotation {rot}, perm {perm}"


def test_knockouts_drop_derivation():
    """Verify that knocking out Fact A, Fact B, or the active rule drops deduction to UNSUPPORTED."""
    bundle = generate_d1_c_world(world_seed=42, rotation_idx=0, rule_perm_idx=0, ecology="C")
    target_subj = bundle.task.target_fact.subject

    # 1. Knockout Fact A
    ko_a = [iv for iv in bundle.interventions if iv.intervention_id == "ko_fact_a"][0]
    cf_oracle_a = CounterfactualOracle(bundle.world, ko_a)
    assert cf_oracle_a.counterfactual_oracle.evaluate_triple(target_subj, "uses_protocol", bundle.target_protocol) == TruthStatus.UNSUPPORTED

    # 2. Knockout Fact B
    ko_b = [iv for iv in bundle.interventions if iv.intervention_id == "ko_fact_b"][0]
    cf_oracle_b = CounterfactualOracle(bundle.world, ko_b)
    assert cf_oracle_b.counterfactual_oracle.evaluate_triple(target_subj, "uses_protocol", bundle.target_protocol) == TruthStatus.UNSUPPORTED

    # 3. Knockout Active Rule
    ko_r = [iv for iv in bundle.interventions if iv.intervention_id == "ko_rule_active"][0]
    cf_oracle_r = CounterfactualOracle(bundle.world, ko_r)
    assert cf_oracle_r.counterfactual_oracle.evaluate_triple(target_subj, "uses_protocol", bundle.target_protocol) == TruthStatus.UNSUPPORTED


def test_knockout_foil_preserves_derivation():
    """Verify that knocking out an inactive foil rule preserves the target derivation."""
    bundle = generate_d1_c_world(world_seed=42, rotation_idx=0, rule_perm_idx=0, ecology="C")
    ko_foil = [iv for iv in bundle.interventions if iv.intervention_id == "ko_rule_foil"][0]
    cf_oracle = CounterfactualOracle(bundle.world, ko_foil)
    assert cf_oracle.counterfactual_oracle.evaluate_triple(bundle.task.target_fact.subject, "uses_protocol", bundle.target_protocol) == TruthStatus.TRUE


def test_directional_mutations():
    """Verify that mutating Fact B redirects deduction to competing rules."""
    bundle = generate_d1_c_world(world_seed=0, rotation_idx=0, rule_perm_idx=0, ecology="C")
    target_subj = bundle.task.target_fact.subject

    # Kira -> Tal -> PROTO_Q2
    mut_tal = [iv for iv in bundle.interventions if iv.intervention_id == "mut_redirect_tal"][0]
    cf_tal = CounterfactualOracle(bundle.world, mut_tal)
    assert cf_tal.counterfactual_oracle.evaluate_triple(target_subj, "uses_protocol", "PROTO_Q2") == TruthStatus.TRUE
    assert cf_tal.counterfactual_oracle.evaluate_triple(target_subj, "uses_protocol", "PROTO_X7") == TruthStatus.FALSE

    # Kira -> Mira -> PROTO_M9
    mut_mira = [iv for iv in bundle.interventions if iv.intervention_id == "mut_redirect_mira"][0]
    cf_mira = CounterfactualOracle(bundle.world, mut_mira)
    assert cf_mira.counterfactual_oracle.evaluate_triple(target_subj, "uses_protocol", "PROTO_M9") == TruthStatus.TRUE
    assert cf_mira.counterfactual_oracle.evaluate_triple(target_subj, "uses_protocol", "PROTO_X7") == TruthStatus.FALSE


def test_unmatched_mutation_abstention():
    """Verify that an unmapped mutation (Kira -> Soren) produces no deduction in either rule."""
    bundle = generate_d1_c_world(world_seed=0, rotation_idx=0, rule_perm_idx=0, ecology="C")
    target_subj = bundle.task.target_fact.subject

    mut_soren = [iv for iv in bundle.interventions if iv.intervention_id == "mut_unmatched_soren"][0]
    cf_soren = CounterfactualOracle(bundle.world, mut_soren)
    for proto in ["PROTO_X7", "PROTO_Q2", "PROTO_M9"]:
        assert cf_soren.counterfactual_oracle.evaluate_triple(target_subj, "uses_protocol", proto) == TruthStatus.UNSUPPORTED


def test_compositional_rescue_chain():
    """Verify sequential causal rescue: S0(X7) -> S1(Q2) -> S2(X7)."""
    bundle = generate_d1_c_world(world_seed=0, rotation_idx=0, rule_perm_idx=0, ecology="C")
    target_subj = bundle.task.target_fact.subject

    # S0: Clean baseline
    s0_world = bundle.world
    assert Oracle(s0_world).evaluate_triple(target_subj, "uses_protocol", "PROTO_X7") == TruthStatus.TRUE

    # S1: Mutation Kira -> Tal
    mut_tal = [iv for iv in bundle.interventions if iv.intervention_id == "mut_redirect_tal"][0]
    s1_world = apply_intervention(s0_world, mut_tal)
    assert Oracle(s1_world).evaluate_triple(target_subj, "uses_protocol", "PROTO_Q2") == TruthStatus.TRUE
    assert Oracle(s1_world).evaluate_triple(target_subj, "uses_protocol", "PROTO_X7") == TruthStatus.FALSE

    # S2: Rescue Tal -> Kira
    rescue_kira = [iv for iv in bundle.interventions if iv.intervention_id == "rescue_tal_to_kira"][0]
    s2_world = apply_intervention(s1_world, rescue_kira)
    assert Oracle(s2_world).evaluate_triple(target_subj, "uses_protocol", "PROTO_X7") == TruthStatus.TRUE
    assert Oracle(s2_world).evaluate_triple(target_subj, "uses_protocol", "PROTO_Q2") == TruthStatus.FALSE


def test_control_distractor_oracle_removes_target():
    """Verify that CounterfactualOracle removes distractor targets from its world."""
    bundle = generate_d1_c_world(world_seed=42, rotation_idx=0, rule_perm_idx=0, ecology="C")
    ko_distractor = [iv for iv in bundle.interventions if iv.intervention_id == "ko_distractor_fact"][0]
    cf = CounterfactualOracle(bundle.world, ko_distractor)
    distractor_id = ko_distractor.target_node_ids[0]
    # Check that distractor fact is not in counterfactual world facts
    assert not any(f.fact_id == distractor_id for f in cf.counterfactual_world.facts)


def test_claim_evaluator_preserves_raw_inconsistency():
    """Verify that detection-to-action inconsistency is flagged as is_contract_consistent=False and not altered."""
    bundle = generate_d1_c_world(world_seed=42, rotation_idx=0, rule_perm_idx=0, ecology="C")
    oracle = Oracle(bundle.world)

    # Inconsistent response: claims insufficient evidence, but still outputs Proto X7
    raw_inconsistent = {
        "evidence_status": "insufficient",
        "answer": {
            "subject": "VELORA",
            "predicate": "uses_protocol",
            "object": "Proto X7"
        },
        "parent_memory_ids": []
    }

    claim = ClaimEvaluator.evaluate_response(
        raw_text="",
        parsed_json=raw_inconsistent,
        oracle=oracle,
    )

    # Must preserve raw values
    assert claim.raw_object == "Proto X7"
    assert claim.object == "PROTO_X7"  # Lexical normalization only!
    assert claim.raw_evidence_status == "insufficient"
    # Inconsistency must be detected!
    assert claim.is_contract_consistent is False
