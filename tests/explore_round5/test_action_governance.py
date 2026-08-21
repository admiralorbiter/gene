"""Unit and Property Tests for Exploration Round 5 Stage 5B Action Governance Engine."""

import pytest
from gene.experiments.action_governance import (
    compute_policy_binary_entitlement,
    compute_policy_scalar_resilience,
    compute_policy_tuple_resilience,
    compute_policy_lineage_aware_geometry,
    evaluate_policy_axioms,
)


def test_binary_entitlement_policy_axioms() -> None:
    """Verify that binary entitlement fails degradation sensitivity (Axiom 3) and lineage discounting (Axiom 6)."""
    report = evaluate_policy_axioms(compute_policy_binary_entitlement, "binary_entitlement")
    assert report.axiom_1_monotonicity is True
    assert report.axiom_2_zero_on_retraction is True
    assert report.axiom_3_degradation_sensitivity is False  # Blind to degradation
    assert report.axiom_4_no_duplication_inflation is True
    assert report.axiom_5_bloat_invariance is True
    assert report.axiom_6_lineage_independence_discounting is False  # Blind to lineage
    assert report.axiom_7_isomorphism_invariance is True
    assert report.total_passed == 5
    assert report.is_fully_compliant is False


def test_scalar_resilience_policy_axioms() -> None:
    """Verify that scalar cut-set resilience fails on shared-root degradation (Axiom 3) and lineage (Axiom 6)."""
    report = evaluate_policy_axioms(compute_policy_scalar_resilience, "scalar_resilience_kappa")
    assert report.axiom_1_monotonicity is True
    assert report.axiom_2_zero_on_retraction is True
    # Shared root (2,1) -> (1,1) preserves kappa=1, so scalar resilience fails Axiom 3!
    assert report.axiom_3_degradation_sensitivity is False
    assert report.axiom_4_no_duplication_inflation is True
    assert report.axiom_5_bloat_invariance is True
    assert report.axiom_6_lineage_independence_discounting is False
    assert report.axiom_7_isomorphism_invariance is True
    assert report.total_passed == 5
    assert report.is_fully_compliant is False


def test_tuple_resilience_policy_axioms() -> None:
    """Verify that tuple resilience rho=(|S|, kappa) fixes degradation sensitivity but fails lineage (Axiom 6)."""
    report = evaluate_policy_axioms(compute_policy_tuple_resilience, "tuple_resilience_rho")
    assert report.axiom_1_monotonicity is True
    assert report.axiom_2_zero_on_retraction is True
    assert report.axiom_3_degradation_sensitivity is True  # Captures (2,1) -> (1,1) via |S| drop!
    assert report.axiom_4_no_duplication_inflation is True
    assert report.axiom_5_bloat_invariance is True
    assert report.axiom_6_lineage_independence_discounting is False  # Blind to root overlap
    assert report.axiom_7_isomorphism_invariance is True
    assert report.total_passed == 6
    assert report.is_fully_compliant is False


def test_lineage_aware_geometry_policy_axioms() -> None:
    """Verify that lineage-aware support geometry satisfies ALL 7 formal governance axioms."""
    report = evaluate_policy_axioms(compute_policy_lineage_aware_geometry, "lineage_aware_geometry")
    assert report.axiom_1_monotonicity is True
    assert report.axiom_2_zero_on_retraction is True
    assert report.axiom_3_degradation_sensitivity is True
    assert report.axiom_4_no_duplication_inflation is True
    assert report.axiom_5_bloat_invariance is True
    assert report.axiom_6_lineage_independence_discounting is True  # Dissects root diversity!
    assert report.axiom_7_isomorphism_invariance is True
    assert report.total_passed == 7
    assert report.is_fully_compliant is True
    assert len(report.failure_reasons) == 0
