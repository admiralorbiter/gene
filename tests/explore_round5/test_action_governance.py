"""Unit and Property Tests for Exploration Round 5 Stage 5B Action Governance Engine (Hardened v2)."""

import pytest
from gene.experiments.action_governance import (
    project_lineage_support,
    compute_policy_binary_entitlement,
    compute_policy_scalar_resilience,
    compute_policy_tuple_resilience,
    compute_policy_lineage_projected,
    evaluate_policy_axioms,
)
from gene.experiments.revision_engine import evaluate_reference_entitlement


def test_lineage_projected_support_hypergraph_minimization() -> None:
    """Verify exact projection and minimization from premise support S(c) to root lineage S_L(c)."""
    supports = [["A", "B"], ["D", "E"]]
    
    # 1. Genuinely Independent Ancestry: A,B <- R1; D,E <- R2
    lin_ind = {"A": "R1", "B": "R1", "D": "R2", "E": "R2"}
    res_ind = project_lineage_support(supports, lin_ind)
    # S_L = {{R1}, {R2}}, kappa_L = 2
    assert res_ind.support_family_roots == [["R1"], ["R2"]]
    assert res_ind.kappa_l == 2
    assert res_ind.rho_l == (2, 2)
    
    # 2. Shared Origin Ancestry: A,D <- R1; B,E <- R2
    lin_shared = {"A": "R1", "D": "R1", "B": "R2", "E": "R2"}
    res_shared = project_lineage_support(supports, lin_shared)
    # Path AB -> {R1, R2}, Path DE -> {R1, R2} => S_L = {{R1, R2}}, kappa_L = 1
    assert res_shared.support_family_roots == [["R1", "R2"]]
    assert res_shared.kappa_l == 1
    assert res_shared.rho_l == (1, 1)
    
    # 3. All-Single-Root Ancestry: A,B,D,E <- R1
    lin_single = {"A": "R1", "B": "R1", "D": "R1", "E": "R1"}
    res_single = project_lineage_support(supports, lin_single)
    # S_L = {{R1}}, kappa_L = 1
    assert res_single.support_family_roots == [["R1"]]
    assert res_single.kappa_l == 1
    assert res_single.rho_l == (1, 1)


def test_representation_incompleteness_collisions() -> None:
    """Systematically prove that Binary, kappa, rho, and Root Count all suffer lossy collisions."""
    supports = [["A", "B"], ["D", "E"]]
    lin_ind = {"A": "R1", "B": "R1", "D": "R2", "E": "R2"}
    lin_shared = {"A": "R1", "D": "R1", "B": "R2", "E": "R2"}
    
    # Collision 1: Binary entitlement collapses Entitled and Degraded
    ref_unch = evaluate_reference_entitlement(supports, [], "C")
    ref_deg = evaluate_reference_entitlement(supports, ["D"], "C")
    score_bin_unch = compute_policy_binary_entitlement(ref_unch, supports, lin_ind).action_authority
    score_bin_deg = compute_policy_binary_entitlement(ref_deg, supports, lin_ind).action_authority
    assert score_bin_unch == score_bin_deg == 1.0  # Binary collision!
    
    # Collision 2: Scalar kappa collapses shared-root degradation (2,1) -> (1,1)
    supports_sr = [["A", "B"], ["A", "D"]]
    ref_sr_unch = evaluate_reference_entitlement(supports_sr, [], "C")
    ref_sr_deg = evaluate_reference_entitlement(supports_sr, ["B"], "C")
    score_kap_unch = compute_policy_scalar_resilience(ref_sr_unch, supports_sr, lin_ind).action_authority
    score_kap_deg = compute_policy_scalar_resilience(ref_sr_deg, supports_sr, lin_ind).action_authority
    assert score_kap_unch == score_kap_deg == 1.0  # Kappa collision!
    
    # Collision 3 & 4: Rho and Global Root Count collapse Independent vs Shared-Origin Ancestry
    score_rho_ind = compute_policy_tuple_resilience(ref_unch, supports, lin_ind).action_authority
    score_rho_shared = compute_policy_tuple_resilience(ref_unch, supports, lin_shared).action_authority
    assert score_rho_ind == score_rho_shared == 1.0  # Rho cannot distinguish lineage independence!
    
    # Proof that Lineage-Projected Policy resolves the collision:
    score_lin_ind = compute_policy_lineage_projected(ref_unch, supports, lin_ind).action_authority
    score_lin_shared = compute_policy_lineage_projected(ref_unch, supports, lin_shared).action_authority
    assert score_lin_ind > score_lin_shared  # Lineage projection distinguishes independent from shared!
    assert score_lin_ind == 1.0
    assert score_lin_shared < 1.0


def test_axiomatic_compliance_scorecards() -> None:
    """Test all 4 policies against the 7 formal action-governance axioms."""
    rep_bin = evaluate_policy_axioms(compute_policy_binary_entitlement, "binary_entitlement")
    rep_kap = evaluate_policy_axioms(compute_policy_scalar_resilience, "scalar_resilience_kappa")
    rep_rho = evaluate_policy_axioms(compute_policy_tuple_resilience, "tuple_resilience_rho")
    rep_lin = evaluate_policy_axioms(compute_policy_lineage_projected, "lineage_projected_resilience")
    
    assert rep_bin.total_passed == 5
    assert rep_kap.total_passed == 5
    assert rep_rho.total_passed == 6
    assert rep_lin.total_passed == 7
    assert rep_lin.is_fully_compliant is True


def test_exhaustive_monotonicity_across_benchmark() -> None:
    """Exhaustively verify Axiom 1 (Monotonicity) across all subset pairs in the 368-case benchmark."""
    from scripts.explore_round5.run_stage_5b_action_governance import run_stage_5b_benchmark
    cases, _ = run_stage_5b_benchmark()
    
    # Index cases by (topology, lineage, frozenset(inval))
    case_map = {}
    for c in cases:
        key = (c["topology"], c["lineage_geometry"], frozenset(c["invalidated_assumptions"]))
        case_map[key] = c["action_scores"]["lineage_projected_resilience"]["action_authority"]
        
    # Check all pairs where subset I1 is contained in subset I2
    for (topo, lin, inv1), auth1 in case_map.items():
        for (topo2, lin2, inv2), auth2 in case_map.items():
            if topo == topo2 and lin == lin2 and inv1.issubset(inv2):
                assert auth2 <= (auth1 + 1e-6), f"Monotonicity violated: {inv1} ({auth1}) vs {inv2} ({auth2})"

