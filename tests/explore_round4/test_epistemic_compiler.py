"""Tests for EpistemicIR v2, EpistemicRenderer, Transformations, and Compiler Passes."""

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
    RuleSpec,
    SupportEnvironment,
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
    }

    rules = {
        "rule_manager_s1": RuleSpec(
            rule_id="rule_manager_s1",
            antecedent_predicates=["has_role(P, manager, VELORA)", "reports_to(P, sector_lead_S1)"],
            consequent_predicate="station_operates_protocol(VELORA, PROTO_X7)",
        ),
        "rule_sector_lead_s2": RuleSpec(
            rule_id="rule_sector_lead_s2",
            antecedent_predicates=["has_role(P, sector_lead, VELORA)", "reports_to(P, sector_lead_S2)"],
            consequent_predicate="station_operates_protocol(VELORA, PROTO_X7)",
        ),
    }

    envs = [
        SupportEnvironment(
            path_id="path_AB",
            rule_id="rule_manager_s1",
            required_semantic_claim_ids=["claim_velora_nerin_manager", "claim_velora_nerin_reports_s1"],
        ),
        SupportEnvironment(
            path_id="path_DE",
            rule_id="rule_sector_lead_s2",
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


def test_epistemic_state_formal_entitlement():
    state, query = build_canonical_recombinant_fixture()
    assert state.is_formally_entitled()
    assert len(state.get_surviving_support_environments()) == 2

    # Invalidate root R1 -> path_AB collapses, path_DE survives
    state.invalidated_roots.append("R1")
    surviving = state.get_surviving_support_environments()
    assert len(surviving) == 1
    assert surviving[0].path_id == "path_DE"
    assert state.is_formally_entitled()

    # Invalidate root R2 -> both collapse
    state.invalidated_roots.append("R2")
    assert not state.is_formally_entitled()


def test_semantic_lineage_deduplication_preserves_distinct_facts_from_same_root():
    """Regression Test: Prove that A and B sharing root R1 are BOTH preserved, while duplicate copies collapse."""
    state, query = build_canonical_recombinant_fixture()

    # Add 3 duplicate paraphrases of A from root R1
    state.premises["occ_A_copy2"] = PremiseNode(
        occurrence_id="occ_A_copy2",
        semantic_claim_id="claim_velora_nerin_manager",
        predicate="has_role",
        subject="Nerin",
        entity="VELORA",
        role="manager",
        root_ids=["R1"],
    )
    state.premises["occ_A_copy3"] = PremiseNode(
        occurrence_id="occ_A_copy3",
        semantic_claim_id="claim_velora_nerin_manager",
        predicate="has_role",
        subject="Nerin",
        entity="VELORA",
        role="manager",
        root_ids=["R1"],
    )
    EpistemicRenderer.render_state(state)

    assert len(state.premises) == 6  # 3 copies of A, 1 B, 1 D, 1 E

    compiler = EpistemicContextCompiler(pipeline=PrivilegeLevel.GENEALOGICAL_NORMALIZATION)
    ctx = compiler.compile(state, query)

    # Must preserve ALL 4 distinct semantic claims (A, B, D, E)
    assert set(ctx.included_semantic_claim_ids) == {
        "claim_velora_nerin_manager",
        "claim_velora_nerin_reports_s1",
        "claim_velora_vael_sector_lead",
        "claim_velora_vael_reports_s2",
    }
    # Deduplicated copies of A should collapse to 1 line with occurrence count
    assert "Root R1 (3 cited occurrences): Nerin is manager of VELORA." in ctx.prompt
    assert "- Root R1: Nerin reports to sector lead S1." in ctx.prompt


def test_compiler_canonical_permutation_invariance_deterministic_proof():
    """Zero-Compute Proof: Canonical support block compiler yields 100% identical SHA256 prompt hashes across all 24 permutations."""
    state, query = build_canonical_recombinant_fixture()
    compiler = EpistemicContextCompiler(pipeline=PrivilegeLevel.TOPOLOGY_AWARE_GROUPING)

    all_perms = PermutationTransform.generate_all_permutations(state)
    assert len(all_perms) == 24

    hashes = set()
    for perm in all_perms:
        ctx = compiler.compile(state, query, occurrence_order=perm)
        prompt_hash = hashlib.sha256(ctx.prompt.encode("utf-8")).hexdigest()
        hashes.add(prompt_hash)

    # Exactly 1 unique prompt hash across all 24 permutations!
    assert len(hashes) == 1, "Canonical compiler failed permutation invariance!"


def test_role_equivariance_structural_swap_and_anonymization():
    state, query = build_canonical_recombinant_fixture()

    # 1. Structural Swap manager <-> sector_lead
    swapped_state, swapped_query = RoleEquivarianceTransform.swap_role_slots(
        state, query, "manager", "sector_lead"
    )
    assert swapped_state.premises["occ_A"].role == "sector_lead"
    assert "Nerin is sector lead of VELORA." in swapped_state.premises["occ_A"].rendered_text
    assert swapped_state.premises["occ_D"].role == "manager"
    assert "Vael is manager of VELORA." in swapped_state.premises["occ_D"].rendered_text
    assert swapped_state.is_formally_entitled()

    # 2. Structural Anonymization to opaque tokens
    anon_state, anon_query = RoleEquivarianceTransform.anonymize_roles(
        state, query, {"manager": "ROLE_Q7", "sector_lead": "ROLE_M2"}
    )
    assert anon_state.premises["occ_A"].role == "ROLE_Q7"
    assert "Nerin is ROLE Q7 of VELORA." in anon_state.premises["occ_A"].rendered_text
    assert anon_state.is_formally_entitled()

    # 3. Entity Rotation VELORA -> KESTREL
    rot_state, rot_query = RoleEquivarianceTransform.rotate_station_entity(
        state, query, "VELORA", "KESTREL"
    )
    assert rot_query.target_station == "KESTREL"
    assert "KESTREL" in rot_state.premises["occ_A"].rendered_text
    assert rot_state.is_formally_entitled()


def test_all_compiler_pipelines_privilege_audit():
    state, query = build_canonical_recombinant_fixture()

    for pipeline in [
        PrivilegeLevel.RAW_SERIALIZATION,
        PrivilegeLevel.TOPOLOGY_AWARE_GROUPING,
        PrivilegeLevel.GENEALOGICAL_NORMALIZATION,
        PrivilegeLevel.PROOF_CARRYING_CERTIFICATE,
    ]:
        compiler = EpistemicContextCompiler(pipeline=pipeline)
        ctx = compiler.compile(state, query)
        assert ctx.privilege_level == pipeline
        assert len(ctx.compiler_passes) >= 2
        assert "AUTHORIZATION RULES:" in ctx.prompt
        assert "QUESTION: Based on authorized rules" in ctx.prompt
        assert len(ctx.source_ir_hash) == 64
