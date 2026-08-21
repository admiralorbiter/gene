"""Unit test suite for Exploration Round 5 Stage 5A Revision Engine."""

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


def test_reference_entitlement_tripartite_states() -> None:
    """Test UNCHANGED, DEGRADED, and RETRACTED states on independent alternative support."""
    # S(C) = {{A, B}, {D, E}}
    supports = [["A", "B"], ["D", "E"]]
    
    # 1. No invalidations -> UNCHANGED
    res_unchanged = evaluate_reference_entitlement(supports, [], "C")
    assert res_unchanged.status == EntitlementStatus.UNCHANGED
    assert res_unchanged.is_entitled is True
    assert res_unchanged.initial_kappa == 2
    assert res_unchanged.surviving_kappa == 2
    assert len(res_unchanged.surviving_supports) == 2
    
    # 2. Invalidate D -> DEGRADED (survives via AB, kappa: 2 -> 1)
    res_degraded = evaluate_reference_entitlement(supports, ["D"], "C")
    assert res_degraded.status == EntitlementStatus.DEGRADED
    assert res_degraded.is_entitled is True
    assert res_degraded.initial_kappa == 2
    assert res_degraded.surviving_kappa == 1
    assert res_degraded.surviving_supports == [["A", "B"]]
    
    # 3. Invalidate A and D -> RETRACTED (both paths broken, kappa: 2 -> 0)
    res_retracted = evaluate_reference_entitlement(supports, ["A", "D"], "C")
    assert res_retracted.status == EntitlementStatus.RETRACTED
    assert res_retracted.is_entitled is False
    assert res_retracted.initial_kappa == 2
    assert res_retracted.surviving_kappa == 0
    assert len(res_retracted.surviving_supports) == 0


def test_lossy_representation_failures() -> None:
    """Verify undercomplete failure (single witness) and overinclusive failure (flat union)."""
    supports = [["A", "B"], ["D", "E"]]
    
    # Case 1: Invalidate D
    ref_d = evaluate_reference_entitlement(supports, ["D"], "C")
    assert ref_d.is_entitled is True  # Survives via AB
    
    # Flat union R = {A,B,D,E} suffers FALSE RETRACTION on do(D=0)
    pol_union_d = evaluate_policy_naive_conjunction(["A", "B", "D", "E"], ["D"], ref_d, "flat_union")
    assert pol_union_d.predicted_entitled is False
    assert pol_union_d.is_false_retraction is True
    
    # Single witness R = {A,B} correctly survives do(D=0)
    pol_wit_d = evaluate_policy_naive_conjunction(["A", "B"], ["D"], ref_d, "single_witness")
    assert pol_wit_d.predicted_entitled is True
    assert pol_wit_d.is_false_retraction is False
    
    # Case 2: Invalidate A
    ref_a = evaluate_reference_entitlement(supports, ["A"], "C")
    assert ref_a.is_entitled is True  # Survives via DE
    
    # Single witness R = {A,B} suffers FALSE RETRACTION on do(A=0)
    pol_wit_a = evaluate_policy_naive_conjunction(["A", "B"], ["A"], ref_a, "single_witness")
    assert pol_wit_a.predicted_entitled is False
    assert pol_wit_a.is_false_retraction is True


def test_lineage_quarantine_autoimmunity() -> None:
    """Verify that lineage quarantine induces epistemic autoimmunity when a root is tainted."""
    supports = [["A", "B"], ["D", "E"]]
    lineage_map = {"A": "R1", "B": "R1", "D": "R2", "E": "R2"}
    
    # Root R2 is tainted
    ref = evaluate_reference_entitlement(supports, ["R2"], "C")
    assert ref.is_entitled is True  # Survives via AB (R1)
    
    # Lineage quarantine marks C as dead because R2 is an ancestor of premise D
    pol_lin = evaluate_policy_lineage_quarantine(supports, lineage_map, ["R2"], ref)
    assert pol_lin.predicted_entitled is False
    assert pol_lin.is_false_retraction is True


def test_isomorphism_invariance() -> None:
    """Verify that permuting premise names preserves exact entitlement status and resilience."""
    supports_1 = [["A", "B"], ["D", "E"]]
    inval_1 = ["A"]
    res_1 = evaluate_reference_entitlement(supports_1, inval_1, "C")
    
    # Permutation pi: A->X, B->Y, D->Z, E->W
    supports_2 = [["X", "Y"], ["Z", "W"]]
    inval_2 = ["X"]
    res_2 = evaluate_reference_entitlement(supports_2, inval_2, "C")
    
    assert res_1.status == res_2.status
    assert res_1.is_entitled == res_2.is_entitled
    assert res_1.initial_kappa == res_2.initial_kappa
    assert res_1.surviving_kappa == res_2.surviving_kappa
    assert len(res_1.surviving_supports) == len(res_2.surviving_supports)


def test_dag_root_expansion_and_cascades() -> None:
    """Verify root-level support expansion in G0 -> G1 -> G2 cascades."""
    # G0: Roots A, B, D, E, F
    # G1: Node M1 <= {A, B} or {D, E}
    # G2: Node Final <= {M1, F}
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
    
    # Expand root supports for Final
    root_supports = dag.compute_root_supports("Final")
    # Expected: {A, B, F} and {D, E, F}
    assert len(root_supports) == 2
    assert { "A", "B", "F" } in root_supports
    assert { "D", "E", "F" } in root_supports
    
    # Invalidate D:
    # - M1: DEGRADED -> METADATA_UPDATE_ONLY
    # - Final: DEGRADED (survives via ABF) -> METADATA_UPDATE_ONLY
    # - D: RETRACTION_REQUIRED
    impact = dag.evaluate_cascade_impact(["D"])
    assert impact["D"] == RevisionImpact.RETRACTION_REQUIRED
    assert impact["M1"] == RevisionImpact.METADATA_UPDATE_ONLY
    assert impact["Final"] == RevisionImpact.METADATA_UPDATE_ONLY
    assert impact["A"] == RevisionImpact.UNAFFECTED
    
    # Invalidate F:
    # - Final: all root paths ({A,B,F}, {D,E,F}) hit F -> RETRACTION_REQUIRED
    # - M1: unaffected by F -> UNAFFECTED
    impact_f = dag.evaluate_cascade_impact(["F"])
    assert impact_f["Final"] == RevisionImpact.RETRACTION_REQUIRED
    assert impact_f["M1"] == RevisionImpact.UNAFFECTED
