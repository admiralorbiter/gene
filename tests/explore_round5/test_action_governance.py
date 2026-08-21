"""Unit and Property Tests for Exploration Round 5 Stage 5B Action Governance Engine (Hardened v3)."""

import itertools
import random
import pytest
from gene.experiments.action_governance import (
    minimize_antichain,
    project_lineage_support,
    compute_policy_binary_entitlement,
    compute_policy_scalar_resilience,
    compute_policy_tuple_resilience,
    compute_policy_lineage_projected,
    evaluate_policy_axioms,
)
from gene.experiments.revision_engine import evaluate_reference_entitlement


def test_minimize_antichain_exact_and_property_testing() -> None:
    """Verify exact antichain minimization (elimination of strict supersets and duplicates)."""
    # 1. Direct superset elimination: {{R1}, {R1, R2}} -> {{R1}}
    sets1 = [{"R1"}, {"R1", "R2"}]
    min1 = minimize_antichain(sets1)
    assert min1 == [{"R1"}]

    # 2. Complex superset elimination
    sets2 = [{"R1", "R2"}, {"R2", "R3"}, {"R1", "R2", "R3"}]
    min2 = minimize_antichain(sets2)
    assert set(frozenset(s) for s in min2) == {frozenset({"R1", "R2"}), frozenset({"R2", "R3"})}

    # 3. Duplicate elimination
    sets3 = [{"R1"}, {"R1"}, {"R2"}]
    min3 = minimize_antichain(sets3)
    assert set(frozenset(s) for s in min3) == {frozenset({"R1"}), frozenset({"R2"})}

    # 4. Property test against brute-force oracle on random families
    roots = ["R1", "R2", "R3", "R4"]
    rng = random.Random(42)
    for _ in range(50):
        # Generate random family of 3-6 subsets
        n_sets = rng.randint(3, 6)
        family = []
        for _ in range(n_sets):
            k = rng.randint(1, 3)
            family.append(set(rng.sample(roots, k)))

        # Run minimize_antichain
        res = minimize_antichain(family)

        # Brute force oracle check:
        # a) No element in res is a strict superset of another in res
        for s1 in res:
            for s2 in res:
                assert not (s2 < s1), f"Antichain property violated: {s2} is strict subset of {s1}"

        # b) Every original set is covered by at least one set in res
        for orig in family:
            is_covered = any(s <= orig for s in res)
            assert is_covered, f"Original set {orig} was dropped without being covered by antichain"


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

    # 3. Superset Branch: S(C) = {AB, ABC} where A,B <- R1, C <- R2
    # Projects to {{R1}, {R1, R2}} -> S_L = {{R1}}, kappa_L = 1
    supports_superset = [["A", "B"], ["A", "B", "C"]]
    lin_superset = {"A": "R1", "B": "R1", "C": "R2"}
    res_superset = project_lineage_support(supports_superset, lin_superset)
    assert res_superset.support_family_roots == [["R1"]]
    assert res_superset.kappa_l == 1
    assert res_superset.rho_l == (1, 1)


def test_hierarchy_of_representation_incompleteness() -> None:
    """Systematically prove the hierarchy: binary -> kappa -> rho -> |Roots| -> rho_L -> S_L."""
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

    # Collision 5: rho_L = (|S_L|, kappa_L) is itself lossy relative to full S_L(c)
    # S_L,1 = {{R1}} vs S_L,2 = {{R1, R2}} -> both have rho_L = (1, 1).
    lin_state_1 = project_lineage_support([["A"]], {"A": "R1"})
    lin_state_2 = project_lineage_support([["A", "B"]], {"A": "R1", "B": "R2"})
    assert lin_state_1.rho_l == lin_state_2.rho_l == (1, 1)
    # But under intervention do(R2=0), S_L,1 survives while S_L,2 is destroyed!
    ref_s1 = evaluate_reference_entitlement([["R1"]], ["R2"], "C")
    ref_s2 = evaluate_reference_entitlement([["R1", "R2"]], ["R2"], "C")
    assert ref_s1.is_entitled is True
    assert ref_s2.is_entitled is False  # Proves rho_L is lossy and S_L(c) is the canonical state!


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
