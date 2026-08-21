"""Unit test suite for Exploration Round 5 Stage 5A Revision Engine (Hardened)."""

import json
from pathlib import Path
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
from scripts.explore_round5.run_stage_5a_revision_assay import (
    run_subassay_5a1_local_what_if,
    run_subassay_5a2_network_then_what,
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
    
    for r in range(len(all_atoms) + 1):
        for combo in itertools.combinations(all_atoms, r):
            inval_set = set(combo)
            expected_bool = closed_form_oracle(supports_sets, inval_set)
            ref_res = evaluate_reference_entitlement(support_family, inval_set, "C")
            assert ref_res.is_entitled == expected_bool


def test_resilience_signature_rho_and_kappa_counterexample() -> None:
    """Verify that support degradation does NOT necessarily lower kappa (rho: (2,1) -> (1,1))."""
    supports = [["A", "B"], ["A", "D"]]
    
    ref_init = evaluate_reference_entitlement(supports, [], "C")
    assert ref_init.initial_rho == (2, 1)
    
    ref_b = evaluate_reference_entitlement(supports, ["B"], "C")
    assert ref_b.status == EntitlementStatus.DEGRADED
    assert ref_b.is_entitled is True
    assert ref_b.surviving_supports == [["A", "D"]]
    assert ref_b.initial_rho == (2, 1)
    assert ref_b.surviving_rho == (1, 1)
    assert ref_b.initial_kappa == 1
    assert ref_b.surviving_kappa == 1
    assert ref_b.surviving_support_count == 1


def test_tri_path_shared_premise_degradation() -> None:
    """Verify that in recombinant tri-path S={ABC, ADE, BDF}, dropping C leaves ADE, BDF with kappa: 2 -> 1."""
    supports = [["A", "B", "C"], ["A", "D", "E"], ["B", "D", "F"]]
    ref_init = evaluate_reference_entitlement(supports, [], "C")
    assert ref_init.initial_rho == (3, 2)
    
    # Invalidate C -> surviving {ADE, BDF} share D -> kappa drops to 1
    ref_c = evaluate_reference_entitlement(supports, ["C"], "C")
    assert ref_c.status == EntitlementStatus.DEGRADED
    assert ref_c.surviving_rho == (2, 1)
    assert ref_c.surviving_kappa == 1


def test_incremental_distractor_bloat_failure() -> None:
    """Verify that invalidating an irrelevant explanatory distractor F falsely retracts bloated memory."""
    supports = [["A", "B"], ["D", "E"]]
    
    ref_f = evaluate_reference_entitlement(supports, ["F"], "C")
    assert ref_f.status == EntitlementStatus.UNCHANGED
    assert ref_f.is_entitled is True
    
    pol_union = evaluate_policy_naive_conjunction(["A", "B", "D", "E"], ["F"], ref_f, "flat_union")
    assert pol_union.predicted_entitled is True
    assert pol_union.is_false_retraction is False
    
    pol_bloat = evaluate_policy_naive_conjunction(["A", "B", "D", "E", "F"], ["F"], ref_f, "bloated_union")
    assert pol_bloat.predicted_entitled is False
    assert pol_bloat.is_false_retraction is True


def test_root_level_lineage_quarantine_isolation() -> None:
    """Verify lineage quarantine under root-level invalidations across independent vs shared geometries."""
    supports = [["A", "B"], ["D", "E"]]
    
    # Independent roots: A,B <- R1; D,E <- R2
    lin_map_ind = {"A": "R1", "B": "R1", "D": "R2", "E": "R2"}
    ref_r2 = evaluate_reference_entitlement(supports, ["D", "E"], "C")
    assert ref_r2.status == EntitlementStatus.DEGRADED
    assert ref_r2.is_entitled is True
    
    pol_lin = evaluate_policy_lineage_quarantine(supports, lin_map_ind, ["R2"], ref_r2)
    assert pol_lin.predicted_entitled is False
    assert pol_lin.is_false_retraction is True
    
    # Shared origin roots: A,D <- R1; B,E <- R2
    lin_map_shared = {"A": "R1", "D": "R1", "B": "R2", "E": "R2"}
    ref_r1 = evaluate_reference_entitlement(supports, ["A", "D"], "C")
    assert ref_r1.status == EntitlementStatus.RETRACTED
    assert ref_r1.is_entitled is False
    
    pol_lin_shared = evaluate_policy_lineage_quarantine(supports, lin_map_shared, ["R1"], ref_r1)
    assert pol_lin_shared.predicted_entitled is False
    assert pol_lin_shared.is_correct_entitlement is True


def test_dag_staleness_factorial_and_root_expansion() -> None:
    """Verify DAG cascades across staleness regimes."""
    dag = RevisionDAG(
        nodes={
            "A": DAGNode(node_id="A", is_root=True),
            "B": DAGNode(node_id="B", is_root=True),
            "D": DAGNode(node_id="D", is_root=True),
            "E": DAGNode(node_id="E", is_root=True),
            "F": DAGNode(node_id="F", is_root=True),
            "G": DAGNode(node_id="G", is_root=True),
            "M1": DAGNode(node_id="M1", direct_parent_supports=[["A", "B"], ["D", "E"]]),
            "M2": DAGNode(node_id="M2", direct_parent_supports=[["D", "F"], ["E", "G"]]),
            "FinalGoal": DAGNode(node_id="FinalGoal", direct_parent_supports=[["M1", "M2"]]),
        }
    )
    
    # Invalidate A, D, E -> all paths broken for M1 and M2
    ref = dag.evaluate_cascade_reference(["A", "D", "E"])
    assert ref["FinalGoal"] == RevisionImpact.RETRACTION_REQUIRED
    
    stale = dag.evaluate_cascade_stale_cached(["A", "D", "E"], stale_cached_nodes={"M1", "M2"})
    assert stale["FinalGoal"] == RevisionImpact.UNAFFECTED  # Zombie survival!


def test_all_reported_probabilities_bounded() -> None:
    """Verify that every calculated metric rate is strictly bounded in [0, 1]."""
    _, summary_5a1 = run_subassay_5a1_local_what_if()
    
    for p_key, p_stat in summary_5a1["overall_policy_comparison"].items():
        assert 0.0 <= p_stat["accuracy"] <= 1.0
        assert 0.0 <= p_stat["autoimmunity_rate_on_degraded"] <= 1.0
        assert 0.0 <= p_stat["autoimmunity_rate_on_unchanged"] <= 1.0
        assert 0.0 <= p_stat["autoimmunity_rate_on_entitled"] <= 1.0

    for topo_name, topo_data in summary_5a1["by_topology"].items():
        for p_key, p_stat in topo_data["policy_metrics"].items():
            assert 0.0 <= p_stat["accuracy"] <= 1.0
            assert 0.0 <= p_stat["autoimmunity_on_degraded"] <= 1.0
            assert 0.0 <= p_stat["autoimmunity_on_unchanged"] <= 1.0
            assert 0.0 <= p_stat["autoimmunity_on_entitled"] <= 1.0


def test_transition_counts_sum_to_exact_denominator() -> None:
    """Verify that all transition matrix counts sum exactly to total local cases (368)."""
    _, summary_5a1 = run_subassay_5a1_local_what_if()
    total_transitions = sum(summary_5a1["rho_transition_matrix"].values())
    assert total_transitions == summary_5a1["total_cases"] == 368


def test_manifest_and_summary_consistency() -> None:
    """Verify that persisted summary JSON and artifacts manifest match computed results."""
    summary_path = Path("data/exploration_round5_stage5a_summary.json")
    manifest_path = Path("data/exploration_round5_artifacts.json")
    if not (summary_path.exists() and manifest_path.exists()):
        pytest.skip("Summary or manifest not found on disk.")
        
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
        
    s_5a1 = summary_data["subassay_5a1"]
    m_5a1 = manifest_data["subassay_5a1_local_what_if"]
    
    assert s_5a1["total_cases"] == m_5a1["total_cases"] == 368
    assert s_5a1["oracle_breakdown"]["degraded"] == m_5a1["degraded_cases"] == 104
    assert s_5a1["oracle_breakdown"]["unchanged"] == m_5a1["unchanged_cases"] == 16
    assert s_5a1["oracle_breakdown"]["total_entitled"] == m_5a1["entitled_cases"] == 120
    assert s_5a1["overall_policy_comparison"]["flat_union"]["autoimmunity_rate_on_degraded"] == m_5a1["flat_union_autoimmunity_on_degraded"] == 1.0

