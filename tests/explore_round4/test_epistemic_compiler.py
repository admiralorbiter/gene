"""Comprehensive Preflight Tests for EpistemicIR v2.2, Proof Validator, Renderer, and Compiler."""

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
    ProvenanceStatus,
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
            parent_occurrence_ids=["founder_01"],
            citations=["doc_f01"],
        ),
        "occ_B": PremiseNode(
            occurrence_id="occ_B",
            semantic_claim_id="claim_velora_nerin_reports_s1",
            predicate="reports_to",
            subject="Nerin",
            entity="VELORA",
            target_value="sector lead S1",
            root_ids=["R1"],
            parent_occurrence_ids=["founder_02"],
            citations=["doc_f02"],
        ),
        "occ_D": PremiseNode(
            occurrence_id="occ_D",
            semantic_claim_id="claim_velora_vael_sector_lead",
            predicate="has_role",
            subject="Vael",
            entity="VELORA",
            role="sector_lead",
            root_ids=["R2"],
            parent_occurrence_ids=["founder_03"],
            citations=["doc_f03"],
        ),
        "occ_E": PremiseNode(
            occurrence_id="occ_E",
            semantic_claim_id="claim_velora_vael_reports_s2",
            predicate="reports_to",
            subject="Vael",
            entity="VELORA",
            target_value="sector lead S2",
            root_ids=["R2"],
            parent_occurrence_ids=["founder_04"],
            citations=["doc_f04"],
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


def test_ir_proof_rule_structural_correspondence_validator():
    state, query = build_canonical_recombinant_fixture()
    errors = validate_ir_consistency(state, query)
    assert errors == [], f"Valid state produced errors: {errors}"

    # Corrupt support environment to point to premises that do NOT satisfy rule_1
    corrupt_state = state.model_copy(deep=True)
    corrupt_state.support_environments[0].required_semantic_claim_ids = [
        "claim_velora_vael_sector_lead",  # Sector lead does NOT satisfy manager rule!
        "claim_velora_nerin_reports_s1",
    ]
    corrupt_errors = validate_ir_consistency(corrupt_state, query)
    assert any("failed to satisfy all antecedents" in e or "does not match any available antecedent" in e for e in corrupt_errors)


def test_state_hash_parentage_and_citations_sensitivity():
    """Prove that changing parentage or citations mutates H_state."""
    state, query = build_canonical_recombinant_fixture()
    h_orig = state.compute_state_hash()

    # Mutate parent_occurrence_ids
    state_mut = state.model_copy(deep=True)
    state_mut.premises["occ_A"].parent_occurrence_ids = ["different_parent_99"]
    h_mut1 = state_mut.compute_state_hash()
    assert h_orig != h_mut1

    # Mutate citations
    state_mut2 = state.model_copy(deep=True)
    state_mut2.premises["occ_A"].citations = ["different_doc_99"]
    h_mut2 = state_mut2.compute_state_hash()
    assert h_orig != h_mut2


def test_provenance_conservation_invariant_across_all_pipelines():
    """Prove that every source occurrence is emitted, merged, or dropped exactly once."""
    state, query = build_canonical_recombinant_fixture()
    # Add duplicate copy of A
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

    for pipeline in [
        PrivilegeLevel.RAW_SERIALIZATION,
        PrivilegeLevel.TOPOLOGY_AWARE_GROUPING,
        PrivilegeLevel.GENEALOGICAL_NORMALIZATION,
        PrivilegeLevel.PROOF_CARRYING_CERTIFICATE,
    ]:
        compiler = EpistemicContextCompiler(pipeline=pipeline)
        ctx = compiler.compile(state, query)
        assert ctx.verify_provenance_conservation(), f"Pipeline {pipeline} violated provenance conservation!"


def test_substate_ir_consistency_validation():
    """Prove that subselected states pass validation with allow_partial_substate=True."""
    state, query = build_canonical_recombinant_fixture()
    chain = SupportAugmentationTransform.generate_augmentation_chain(
        state, base_support_path_id="path_AB", augment_occurrence_ids=["occ_D"]
    )
    sub0, label0 = chain[0]
    # In AB substate, path_DE is inactive because its claims are missing
    errors = validate_ir_consistency(sub0, query, allow_partial_substate=True)
    assert errors == []


def test_unknown_provenance_first_class_status():
    """Prove that unknown_untracked provenance is valid and renders properly."""
    state, query = build_canonical_recombinant_fixture()
    state.premises["occ_unknown"] = PremiseNode(
        occurrence_id="occ_unknown",
        semantic_claim_id="claim_ambient_whisper",
        predicate="station_operates_protocol",
        subject="Station",
        entity="VELORA",
        target_value="PROTO_X7",
        root_ids=[],
        provenance_status=ProvenanceStatus.UNKNOWN_UNTRACKED,
    )
    EpistemicRenderer.render_state(state)

    errors = validate_ir_consistency(state, query)
    assert errors == []

    compiler = EpistemicContextCompiler(pipeline=PrivilegeLevel.PROOF_CARRYING_CERTIFICATE)
    ctx = compiler.compile(state, query)
    assert "Root=ambient" in ctx.prompt
