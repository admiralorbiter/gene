"""Unit test suite for Exploration Round 5 Stage 5A Revision Engine (Hardened)."""

import pytest
from gene.experiments.revision_engine import (
    EntitlementStatus,
    RevisionImpact,
    DAGNode,
    RevisionDAG,
    evaluate_reference_entitlement,
    evaluate_policy_naive_conjunction,
    evaluate_policy_lineage_quarantine,
)


def closed_form_oracle(supports: list[set[str]], inval: set[str]) -> bool:
    """Independent mathematical definition of entitlement: exists S_i disjoint from I."""
    return any(not (s & inval) for s in supports)


def test_closed_form_oracle_property_testing() -> None:
    """Property-test MinimalSupportEngine against an independent set-theoretic oracle."""
    import itertools
    all_atoms = ["A", "B", "C", "D", "E", "F"]
    support_family = [["A", "B", "C"], ["A", "D", "E"], ["B", "D", "F"]]
    supports_sets = [set(s) for s in support_family]
    
    # Test all 2^6 = 64 invalidation subsets
    for r in range(len(all_atoms) + 1):
        for combo in itertools.combinations(all_atoms, r):
            inval_set = set(combo)
            expected_bool = closed_form_oracle(supports_sets, inval_set)
            ref_res = evaluate_reference_entitlement(support_family, inval_set, "C")
            assert ref_res.is_entitled == expected_bool


def test_resilience_signature_rho_and_kappa_counterexample() -> None:
    """Verify that support degradation does NOT necessarily lower kappa (rho: (2,1) -> (1,1))."""
    # Shared root topology: S(C) = {{A, B}, {A, D}}
    # Initially: |S| = 2, kappa = 1 (A alone destroys all support)
    supports = [["A", "B"], ["A", "D"]]
    
    ref_init = evaluate_reference_entitlement(supports, [], "C")
    assert ref_init.initial_rho == (2, 1)
    
    # Invalidate B: AB path destroyed, AD survives
    ref_b = evaluate_reference_entitlement(supports, ["B"], "C")
    assert ref_b.status == EntitlementStatus.DEGRADED
    assert ref_b.is_entitled is True
    assert ref_b.surviving_supports == [["A", "D"]]
    assert ref_b.initial_rho == (2, 1)
    assert ref_b.surviving_rho == (1, 1)
    # Proof that kappa does not change (1 -> 1), but |S| drops (2 -> 1)!
    assert ref_b.initial_kappa == 1
    assert ref_b.surviving_kappa == 1
    assert ref_b.surviving_support_count == 1


def test_incremental_distractor_bloat_failure() -> None:
    """Verify that invalidating an irrelevant explanatory distractor F falsely retracts bloated memory."""
    supports = [["A", "B"], ["D", "E"]]
    
    # Invalidate ONLY the distractor F (not in any minimal support set)
    ref_f = evaluate_reference_entitlement(supports, ["F"], "C")
    assert ref_f.status == EntitlementStatus.UNCHANGED
    assert ref_f.is_entitled is True
    
    # Flat union R = {A,B,D,E} is unaffected by F -> survives (CORRECT)
    pol_union = evaluate_policy_naive_conjunction(["A", "B", "D", "E"], ["F"], ref_f, "flat_union")
    assert pol_union.predicted_entitled is True
    assert pol_union.is_false_retraction is False
    
    # Bloated union R = {A,B,D,E,F} hits F -> FALSE RETRACTION!
    pol_bloat = evaluate_policy_naive_conjunction(["A", "B", "D", "E", "F"], ["F"], ref_f, "bloated_union")
    assert pol_bloat.predicted_entitled is False
    assert pol_bloat.is_false_retraction is True


def test_root_level_lineage_quarantine_isolation() -> None:
    """Verify lineage quarantine under root-level invalidations across independent vs shared geometries."""
    supports = [["A", "B"], ["D", "E"]]
    
    # Independent roots: A,B <- R1; D,E <- R2
    lin_map_ind = {"A": "R1", "B": "R1", "D": "R2", "E": "R2"}
    
    # Invalidate root R2:
    # Premise invalidations: {D, E}
    ref_r2 = evaluate_reference_entitlement(supports, ["D", "E"], "C")
    assert ref_r2.status == EntitlementStatus.DEGRADED
    assert ref_r2.is_entitled is True  # Survives via AB (R1)
    
    # Lineage quarantine: tainted by R2 -> FALSE RETRACTION!
    pol_lin = evaluate_policy_lineage_quarantine(supports, lin_map_ind, ["R2"], ref_r2)
    assert pol_lin.predicted_entitled is False
    assert pol_lin.is_false_retraction is True
    
    # Shared origin roots: A,D <- R1; B,E <- R2
    lin_map_shared = {"A": "R1", "D": "R1", "B": "R2", "E": "R2"}
    # Invalidate root R1: Premise invalidations: {A, D}
    ref_r1 = evaluate_reference_entitlement(supports, ["A", "D"], "C")
    assert ref_r1.status == EntitlementStatus.RETRACTED
    assert ref_r1.is_entitled is False
    
    # Lineage quarantine correctly retracts
    pol_lin_shared = evaluate_policy_lineage_quarantine(supports, lin_map_shared, ["R1"], ref_r1)
    assert pol_lin_shared.predicted_entitled is False
    assert pol_lin_shared.is_correct_entitlement is True


def test_dag_root_expansion_vs_stale_cached_baseline() -> None:
    """Verify that root expansion prevents stale-cached zombie derivations in DAG cascades."""
    # G0: Roots A, B, D, E, F
    # G1: M1 <= {A, B} or {D, E}
    # G2: Final <= {M1, F}
    dag = RevisionDAG(
        nodes={
            "A": DAGNode(node_id="A", is_root=True),
            "B": DAGNode(node_id="B", is_root=True),
            "D": DAGNode(node_id="D", is_root=True),
            "E": DAGNode(node_id="E", is_root=True),
            "F": DAGNode(node_id="F", is_root=True),
            "M1": DAGNode(node_id="M1", direct_parent_supports=[["A", "B"], ["D", "E"]]),
            "Final": DAGNode(node_id="Final", direct_parent_supports=[["M1", "F"]]),
        }
    )
    
    # Case 1: Invalidate A and D (all root paths to M1 destroyed)
    # Ground truth reference:
    # - M1: RETRACTED
    # - Final: RETRACTED (lost M1)
    ref_impact = dag.evaluate_cascade_reference(["A", "D"])
    assert ref_impact["M1"] == RevisionImpact.RETRACTION_REQUIRED
    assert ref_impact["Final"] == RevisionImpact.RETRACTION_REQUIRED
    
    # Stale-cached baseline: Suppose M1 is cached as valid/alive
    stale_impact = dag.evaluate_cascade_stale_cached(["A", "D"], stale_cached_nodes={"M1"})
    # Stale baseline falsely keeps Final alive because it checks immediate parent M1 from cache!
    assert stale_impact["Final"] == RevisionImpact.UNAFFECTED  # Stale Zombie Survival!
