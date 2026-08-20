"""End-to-End Smoke Tests for Round 4 Runners, Property Invariants, and Unification."""

import sys
import tempfile
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
import sqlite3
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
from gene.experiments.evaluators_round4 import (
    evaluate_conformance_k_a,
    evaluate_conformance_k_l,
    evaluate_conformance_k_s,
    parse_round4_model_output,
)
from scripts.explore_round4.run_track_r import run_track_r
from scripts.explore_round4.run_track_p import run_track_p
from scripts.explore_round4.run_track_m import run_track_m
from scripts.explore_round4.run_track_c import run_track_c


class FakeRound4OllamaClient:
    """Deterministic Fake Client for Smoke Tests."""
    def __init__(self, fixed_protocol: str = "PROTO_X7"):
        self.fixed_protocol = fixed_protocol
        self.calls = []

    def chat(self, messages: list[dict[str, str]], model: str = "gemma3:12b") -> str:
        prompt = messages[0]["content"]
        self.calls.append(prompt)
        return f'{{"station": "VELORA", "protocol": "{self.fixed_protocol}", "reported_support_path": "path_AB", "perceived_independent_roots": 1, "evidence_status": "sufficient"}}'


def test_first_order_variable_unification_and_minimality():
    """Prove that cross-person binding errors and non-minimal premise sets are rejected."""
    # 1. Cross-person binding error: Nerin is manager, but Vael reports to S1
    premises_cross = {
        "occ_A": PremiseNode(
            occurrence_id="occ_A",
            semantic_claim_id="claim_velora_nerin_manager",
            predicate="has_role",
            subject="Nerin",
            entity="VELORA",
            role="manager",
            root_ids=["R1"],
        ),
        "occ_B_cross": PremiseNode(
            occurrence_id="occ_B_cross",
            semantic_claim_id="claim_velora_vael_reports_s1",
            predicate="reports_to",
            subject="Vael",  # DIFFERENT PERSON!
            entity="VELORA",
            target_value="sector lead S1",
            root_ids=["R1"],
        ),
    }

    rule = RuleSpec(
        rule_id="rule_1",
        antecedents=[
            RuleAntecedent(predicate="has_role", subject_var="P", entity_var="S", subject_role="manager"),
            RuleAntecedent(predicate="reports_to", subject_var="P", entity_var="S", target_value="sector lead S1"),
        ],
        consequent_predicate="station_operates_protocol",
        consequent_entity_var="S",
        consequent_protocol="PROTO_X7",
    )

    envs = [
        SupportEnvironment(
            path_id="path_cross",
            rule_id="rule_1",
            required_semantic_claim_ids=["claim_velora_nerin_manager", "claim_velora_vael_reports_s1"],
        ),
    ]

    state_cross = EpistemicState(premises=premises_cross, rules={"rule_1": rule}, support_environments=envs)
    errors_cross = validate_ir_consistency(state_cross)
    assert any("variable unification error" in e for e in errors_cross), "Validator failed to catch cross-person binding error!"

    # 2. Minimality violation: adding extra claim F to required claims of an AB rule
    premises_cross["occ_F"] = PremiseNode(
        occurrence_id="occ_F",
        semantic_claim_id="claim_velora_corin_duty",
        predicate="neutral_fact",
        subject="Corin",
        entity="VELORA",
        root_ids=["R3"],
    )
    envs_non_minimal = [
        SupportEnvironment(
            path_id="path_non_minimal",
            rule_id="rule_1",
            required_semantic_claim_ids=["claim_velora_nerin_manager", "claim_velora_vael_reports_s1", "claim_velora_corin_duty"],
        ),
    ]
    state_non_minimal = EpistemicState(premises=premises_cross, rules={"rule_1": rule}, support_environments=envs_non_minimal)
    errors_min = validate_ir_consistency(state_non_minimal)
    assert any("violates minimality" in e for e in errors_min), "Validator failed to catch minimality violation!"


def test_typed_equivalence_property_invariants():
    """Property tests for H_perm, H_rep, and H_alpha."""
    from scripts.explore_round4.run_track_p import build_velora_track_p_base
    state, query = build_velora_track_p_base()

    # 1. H_perm property: invariant under all permutations
    h_perm_base = state.compute_permutation_equiv_hash()
    all_perms = PermutationTransform.generate_all_permutations(state)
    for perm in all_perms:
        perm_state = state.subselect_occurrences(perm)
        assert perm_state.compute_permutation_equiv_hash() == h_perm_base

    # 2. H_rep property: invariant under copy multiplication from same root
    h_rep_base = state.compute_reproduction_equiv_hash()
    state_copy = state.model_copy(deep=True)
    state_copy.premises["occ_A_copy2"] = PremiseNode(
        occurrence_id="occ_A_copy2",
        semantic_claim_id="claim_velora_nerin_manager",
        predicate="has_role",
        subject="Nerin",
        entity="VELORA",
        role="manager",
        root_ids=["R1"],
    )
    assert state_copy.compute_reproduction_equiv_hash() == h_rep_base

    # Negative H_rep property: different root MUST change H_rep!
    state_diff_root = state.model_copy(deep=True)
    state_diff_root.premises["occ_A_copy2"] = PremiseNode(
        occurrence_id="occ_A_copy2",
        semantic_claim_id="claim_velora_nerin_manager",
        predicate="has_role",
        subject="Nerin",
        entity="VELORA",
        role="manager",
        root_ids=["R_DIFFERENT"],
    )
    assert state_diff_root.compute_reproduction_equiv_hash() != h_rep_base

    # 3. H_alpha property: invariant under opaque role renaming
    h_alpha_base = state.compute_alpha_equiv_hash()
    anon_state, anon_query = RoleEquivarianceTransform.anonymize_roles(
        state, query, {"manager": "ROLE_Q7", "sector_lead": "ROLE_M2"}
    )
    assert anon_state.compute_alpha_equiv_hash() == h_alpha_base


def test_smoke_all_round4_runners_end_to_end():
    """End-to-end fake-client smoke test proving 1 call -> 1 parse -> 1 eval -> 1 persist for all 4 tracks."""
    client = FakeRound4OllamaClient(fixed_protocol="PROTO_X7")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_smoke_r4.db")

        # Track R
        evals_r = run_track_r(client, db_path, max_calls=1)
        assert len(evals_r) == 1
        assert evals_r[0].k_a == 1
        assert evals_r[0].k_role is not None

        # Track P
        evals_p = run_track_p(client, db_path, max_calls=1)
        assert len(evals_p) == 1
        assert evals_p[0].k_a == 1
        assert evals_p[0].k_i is not None

        # Track M
        evals_m = run_track_m(client, db_path, max_calls=1)
        assert len(evals_m) == 1
        assert evals_m[0].k_a == 1
        assert evals_m[0].k_mono is not None

        # Track C
        evals_c = run_track_c(client, db_path, max_calls=1)
        assert len(evals_c) == 1
        assert evals_c[0].k_a == 1
        assert evals_c[0].k_s == 1  # path_AB is valid in eco_entitled

        # Verify SQLite table content
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM round4_conformance_evaluations")
        total_rows = cur.fetchone()[0]
        assert total_rows == 4
        conn.close()
