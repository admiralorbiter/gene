"""Comprehensive Preflight Tests for EpistemicIR v2.1, Renderer, and Context Compiler."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
import hashlib
from gene.experiments.epistemic_ir import (
    EpistemicState,
    PremiseNode,
    PrivilegeLevel,
    QueryContract,
    RuleAntecedent,
    RuleSpec,
    SupportEnvironment,
    validate_ir_consistency,
)
from gene.experiments.epistemic_renderer import EpistemicRenderer
from gene.experiments.transformations import (
    PermutationTransform,
    RoleEquivarianceTransform,
    SupportAugmentationTransform,
)
from gene.experiments.context_compiler import EpistemicContextCompiler


def build_canonical_recombinant_fixture() -> tuple[EpistemicState, QueryContract]:
    """AB + DE -> PROTO_X7 canonical recombinant support fixture."""
    premises = {
        "occ_A": PremiseNode(
            occurrence_id="occ_A",
            semantic_claim_id="claim_velora_nerin_manager",
            predicate="has_role",
            subject="Nerin",
            entity="VELORA",
            role="manager",
            root_ids=["R1"],
        ),
        "occ_B": PremiseNode(
            occurrence_id="occ_B",
            semantic_claim_id="claim_velora_nerin_reports_s1",
            predicate="reports_to",
            subject="Nerin",
            entity="VELORA",
            target_value="sector lead S1",
            root_ids=["R1"],
        ),
        "occ_D": PremiseNode(
            occurrence_id="occ_D",
            semantic_claim_id="claim_velora_vael_sector_lead",
            predicate="has_role",
            subject="Vael",
            entity="VELORA",
            role="sector_lead",
            root_ids=["R2"],
        ),
        "occ_E": PremiseNode(
            occurrence_id="occ_E",
            semantic_claim_id="claim_velora_vael_reports_s2",
            predicate="reports_to",
            subject="Vael",
            entity="VELORA",
            target_value="sector lead S2",
            root_ids=["R2"],
        ),
        "occ_F": PremiseNode(
            occurrence_id="occ_F",
            semantic_claim_id="claim_velora_corin_duty",
            predicate="neutral_fact",
            subject="Corin",
            entity="VELORA",
            root_ids=["R3"],
        ),
    }

    rules = {
        "rule_1": RuleSpec(
            rule_id="rule_1",
            antecedents=[
                RuleAntecedent(predicate="has_role", subject_role="manager"),
                RuleAntecedent(predicate="reports_to", target_value="sector lead S1"),
            ],
            consequent_predicate="station_operates_protocol",
            consequent_protocol="PROTO_X7",
        ),
        "rule_2": RuleSpec(
            rule_id="rule_2",
            antecedents=[
                RuleAntecedent(predicate="has_role", subject_role="sector_lead"),
                RuleAntecedent(predicate="reports_to", target_value="sector lead S2"),
            ],
            consequent_predicate="station_operates_protocol",
            consequent_protocol="PROTO_X7",
        ),
    }

    envs = [
        SupportEnvironment(
            path_id="path_AB",
            rule_id="rule_1",
            required_semantic_claim_ids=["claim_velora_nerin_manager", "claim_velora_nerin_reports_s1"],
        ),
        SupportEnvironment(
            path_id="path_DE",
            rule_id="rule_2",
            required_semantic_claim_ids=["claim_velora_vael_sector_lead", "claim_velora_vael_reports_s2"],
        ),
    ]

    query = QueryContract(
        target_station="VELORA",
        target_predicate="station_operates_protocol",
        query_question="Based on authorized rules and evidence, what protocol is authorized for station VELORA?",
        allow_unknown=True,
        output_schema_json='{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}',
    )

    state = EpistemicState(
        premises=premises,
        rules=rules,
        support_environments=envs,
        invalidated_roots=[],
    )
    EpistemicRenderer.render_state(state)
    return state, query


def test_ir_self_consistency_validator():
    state, query = build_canonical_recombinant_fixture()
    errors = validate_ir_consistency(state, query)
    assert errors == [], f"Valid state produced errors: {errors}"

    # Corrupt a rule_id in a support environment
    corrupt_state = state.model_copy(deep=True)
    corrupt_state.support_environments[0].rule_id = "nonexistent_rule"
    corrupt_errors = validate_ir_consistency(corrupt_state, query)
    assert any("references unregistered rule" in e for e in corrupt_errors)

    # Corrupt a required semantic claim ID
    corrupt_state2 = state.model_copy(deep=True)
    corrupt_state2.support_environments[0].required_semantic_claim_ids.append("phantom_claim")
    corrupt_errors2 = validate_ir_consistency(corrupt_state2, query)
    assert any("requires semantic claim phantom_claim" in e for e in corrupt_errors2)


def test_dynamic_structural_rule_rendering_after_role_swap():
    """Verify that swapping manager <-> sector_lead dynamically re-renders BOTH premises AND rules."""
    state, query = build_canonical_recombinant_fixture()

    swapped_state, swapped_query = RoleEquivarianceTransform.swap_role_slots(
        state, query, "manager", "sector_lead"
    )

    # Premises re-rendered
    assert "Nerin is sector lead of VELORA." in swapped_state.premises["occ_A"].rendered_text
    assert "Vael is manager of VELORA." in swapped_state.premises["occ_D"].rendered_text

    # Rules re-rendered dynamically from antecedents
    assert "If a person is sector lead of a station and reports to sector lead S1" in swapped_state.rules["rule_1"].rendered_text
    assert "If a person is manager of a station and reports to sector lead S2" in swapped_state.rules["rule_2"].rendered_text

    # Compiler output contains swapped rules
    compiler = EpistemicContextCompiler(pipeline=PrivilegeLevel.RAW_SERIALIZATION)
    ctx = compiler.compile(swapped_state, swapped_query)
    assert "If a person is sector lead of a station and reports to sector lead S1" in ctx.prompt
    assert "If a person is manager of a station and reports to sector lead S2" in ctx.prompt


def test_state_hash_vs_equiv_hash_distinction():
    """Prove that state_hash changes under duplicate copies, while equiv_hash remains invariant."""
    state, query = build_canonical_recombinant_fixture()
    h_state_orig = state.compute_state_hash()
    h_equiv_orig = state.compute_equiv_hash()

    # Add 2 duplicate occurrences of A
    state_multi = state.model_copy(deep=True)
    state_multi.premises["occ_A_copy2"] = PremiseNode(
        occurrence_id="occ_A_copy2",
        semantic_claim_id="claim_velora_nerin_manager",
        predicate="has_role",
        subject="Nerin",
        entity="VELORA",
        role="manager",
        root_ids=["R1"],
    )
    state_multi.premises["occ_A_copy3"] = PremiseNode(
        occurrence_id="occ_A_copy3",
        semantic_claim_id="claim_velora_nerin_manager",
        predicate="has_role",
        subject="Nerin",
        entity="VELORA",
        role="manager",
        root_ids=["R1"],
    )
    EpistemicRenderer.render_state(state_multi)

    h_state_multi = state_multi.compute_state_hash()
    h_equiv_multi = state_multi.compute_equiv_hash()

    # State hashes MUST differ (occurrences changed)
    assert h_state_orig != h_state_multi
    # Equivalence hashes MUST be identical (semantic entitlement unchanged)
    assert h_equiv_orig == h_equiv_multi


def test_compiled_context_provenance_and_merge_groups():
    """Verify that CompiledContext carries full provenance and records merged occurrences."""
    state, query = build_canonical_recombinant_fixture()
    state.premises["occ_A_copy2"] = PremiseNode(
        occurrence_id="occ_A_copy2",
        semantic_claim_id="claim_velora_nerin_manager",
        predicate="has_role",
        subject="Nerin",
        entity="VELORA",
        role="manager",
        root_ids=["R1"],
    )
    EpistemicRenderer.render_state(state)

    compiler = EpistemicContextCompiler(pipeline=PrivilegeLevel.GENEALOGICAL_NORMALIZATION)
    ctx = compiler.compile(state, query)

    assert "occ_A" in ctx.emitted_occurrence_ids
    assert "occ_A_copy2" not in ctx.emitted_occurrence_ids
    assert "occ_A_copy2" in ctx.merged_occurrence_groups.get("occ_A", [])
    assert ctx.drop_or_merge_reasons.get("occ_A_copy2") == "merged_into_occ_A_same_lineage_claim"


def test_support_augmentation_produces_truthful_substates():
    """Verify that SupportAugmentationTransform produces truthful subselected EpistemicStates."""
    state, query = build_canonical_recombinant_fixture()

    chain = SupportAugmentationTransform.generate_augmentation_chain(
        state, base_support_path_id="path_AB", augment_occurrence_ids=["occ_D", "occ_E", "occ_F"]
    )

    assert len(chain) == 4
    # Step 0: Minimal AB
    sub0, label0 = chain[0]
    assert len(sub0.premises) == 2
    assert sub0.is_formally_entitled()
    assert len(sub0.get_surviving_support_environments()) == 1

    # Step 1: ABD
    sub1, label1 = chain[1]
    assert len(sub1.premises) == 3
    assert sub1.is_formally_entitled()
    assert len(sub1.get_surviving_support_environments()) == 1

    # Step 2: ABDE (Second path becomes active!)
    sub2, label2 = chain[2]
    assert len(sub2.premises) == 4
    assert sub2.is_formally_entitled()
    assert len(sub2.get_surviving_support_environments()) == 2

    # Step 3: ABDEF (Neutral distractor F added)
    sub3, label3 = chain[3]
    assert len(sub3.premises) == 5
    assert sub3.is_formally_entitled()
    assert len(sub3.get_surviving_support_environments()) == 2
