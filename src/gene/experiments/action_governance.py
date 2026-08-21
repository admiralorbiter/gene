"""GENE Exploration Round 5 Stage 5B: Action Governance & Epistemic Resilience Engine.

Evaluates what surviving support information is minimally necessary to govern action authority
under change. Implements candidate governance policies and formal axiomatic compliance tests.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable
from pydantic import BaseModel, Field

from gene.experiments.multi_justification import MinimalSupportEngine
from gene.experiments.revision_engine import (
    EntitlementStatus,
    ReferenceRevisionResult,
    evaluate_reference_entitlement,
)


class GovernancePolicyType(str, Enum):
    """Candidate action-governance policies."""
    BINARY_ENTITLEMENT = "binary_entitlement"  # Auth in {0, 1}
    SCALAR_RESILIENCE_KAPPA = "scalar_resilience_kappa"  # Scaled by kappa / kappa_init
    TUPLE_RESILIENCE_RHO = "tuple_resilience_rho"  # Governed by rho = (|S|, kappa)
    LINEAGE_AWARE_GEOMETRY = "lineage_aware_geometry"  # Full geometry + lineage diversity


class PolicyActionScore(BaseModel):
    """Computed action authority score under a specific governance policy."""
    policy_name: str
    action_authority: float = Field(ge=0.0, le=1.0)
    is_action_permitted: bool  # Whether authority exceeds action gating threshold (default >= 0.5)
    details: dict[str, Any] = Field(default_factory=dict)


def compute_policy_binary_entitlement(
    reference: ReferenceRevisionResult,
    support_family: list[list[str]],
    lineage_map: dict[str, str],
    threshold: float = 0.5,
) -> PolicyActionScore:
    """Policy P_binary: All-or-nothing authority based purely on entitlement."""
    auth = 1.0 if reference.is_entitled else 0.0
    return PolicyActionScore(
        policy_name=GovernancePolicyType.BINARY_ENTITLEMENT.value,
        action_authority=auth,
        is_action_permitted=(auth >= threshold),
        details={"status": reference.status.value},
    )


def compute_policy_scalar_resilience(
    reference: ReferenceRevisionResult,
    support_family: list[list[str]],
    lineage_map: dict[str, str],
    threshold: float = 0.5,
) -> PolicyActionScore:
    """Policy P_kappa: Authority scaled purely by surviving cut-set resilience."""
    if not reference.is_entitled or reference.initial_kappa == 0:
        auth = 0.0
    else:
        auth = reference.surviving_kappa / reference.initial_kappa
        
    auth = max(0.0, min(1.0, auth))
    return PolicyActionScore(
        policy_name=GovernancePolicyType.SCALAR_RESILIENCE_KAPPA.value,
        action_authority=auth,
        is_action_permitted=(auth >= threshold),
        details={
            "initial_kappa": reference.initial_kappa,
            "surviving_kappa": reference.surviving_kappa,
        },
    )


def compute_policy_tuple_resilience(
    reference: ReferenceRevisionResult,
    support_family: list[list[str]],
    lineage_map: dict[str, str],
    threshold: float = 0.5,
) -> PolicyActionScore:
    """Policy P_rho: Authority governed by both cut-set resilience and support count."""
    if not reference.is_entitled or reference.initial_support_count == 0:
        auth = 0.0
    else:
        kappa_ratio = reference.surviving_kappa / max(1, reference.initial_kappa)
        support_ratio = reference.surviving_support_count / max(1, reference.initial_support_count)
        # Average of cut-set and path redundancy ratios
        auth = 0.5 * kappa_ratio + 0.5 * support_ratio
        
    auth = max(0.0, min(1.0, auth))
    return PolicyActionScore(
        policy_name=GovernancePolicyType.TUPLE_RESILIENCE_RHO.value,
        action_authority=auth,
        is_action_permitted=(auth >= threshold),
        details={
            "initial_rho": reference.initial_rho,
            "surviving_rho": reference.surviving_rho,
        },
    )


def compute_policy_lineage_aware_geometry(
    reference: ReferenceRevisionResult,
    support_family: list[list[str]],
    lineage_map: dict[str, str],
    threshold: float = 0.5,
) -> PolicyActionScore:
    """Policy P_geom: Authority governed by minimal cut sets, path lengths, and ancestral root diversity."""
    if not reference.is_entitled:
        return PolicyActionScore(
            policy_name=GovernancePolicyType.LINEAGE_AWARE_GEOMETRY.value,
            action_authority=0.0,
            is_action_permitted=False,
            details={"status": "RETRACTED"},
        )
        
    # 1. Cut set ratio (weight 0.4)
    kappa_ratio = reference.surviving_kappa / max(1, reference.initial_kappa)
    
    # 2. Lineage root diversity ratio (weight 0.3)
    init_roots = {lineage_map.get(p, p) for s in reference.initial_supports for p in s}
    surv_roots = {lineage_map.get(p, p) for s in reference.surviving_supports for p in s}
    root_ratio = len(surv_roots) / max(1, len(init_roots))
    
    # 3. Path-length weighted structural support ratio (weight 0.3)
    def path_weight(path: list[str]) -> float:
        return 1.0 / (1.0 + 0.1 * max(0, len(path) - 1))
        
    init_struct_weight = sum(path_weight(s) for s in reference.initial_supports)
    surv_struct_weight = sum(path_weight(s) for s in reference.surviving_supports)
    struct_ratio = surv_struct_weight / max(1e-6, init_struct_weight)
    
    # 4. Lineage Independence Factor (discounting when multiple paths share a single ancestral root)
    k_paths = len(reference.surviving_supports)
    delta_root = min(1.0, len(surv_roots) / max(1, k_paths)) if k_paths > 1 else 1.0
    lineage_multiplier = 0.7 + 0.3 * delta_root
    
    # Combined authority score
    base_auth = 0.4 * kappa_ratio + 0.3 * root_ratio + 0.3 * struct_ratio
    auth = base_auth * lineage_multiplier
    auth = max(0.0, min(1.0, auth))
    
    return PolicyActionScore(
        policy_name=GovernancePolicyType.LINEAGE_AWARE_GEOMETRY.value,
        action_authority=auth,
        is_action_permitted=(auth >= threshold),
        details={
            "kappa_ratio": kappa_ratio,
            "root_diversity_ratio": root_ratio,
            "structural_weight_ratio": struct_ratio,
            "delta_root": delta_root,
            "lineage_multiplier": lineage_multiplier,
            "surviving_roots": sorted(list(surv_roots)),
        },
    )


class AxiomaticComplianceReport(BaseModel):
    """Results of checking a policy against the 7 formal action-governance axioms."""
    policy_name: str
    axiom_1_monotonicity: bool
    axiom_2_zero_on_retraction: bool
    axiom_3_degradation_sensitivity: bool
    axiom_4_no_duplication_inflation: bool
    axiom_5_bloat_invariance: bool
    axiom_6_lineage_independence_discounting: bool
    axiom_7_isomorphism_invariance: bool
    total_passed: int
    is_fully_compliant: bool
    failure_reasons: list[str] = Field(default_factory=list)


def evaluate_policy_axioms(
    policy_fn: Callable[..., PolicyActionScore],
    policy_name: str,
) -> AxiomaticComplianceReport:
    """Evaluate a candidate policy against all 7 formal governance axioms."""
    failures: list[str] = []
    
    # 1. Axiom 1: Monotonicity under Invalidation (I1 subset of I2 => Auth(I2) <= Auth(I1))
    # Test on independent alternatives S={{A,B}, {D,E}} with I1={D}, I2={D, E}
    supports_mono = [["A", "B"], ["D", "E"]]
    lin_mono = {"A": "R1", "B": "R1", "D": "R2", "E": "R2"}
    ref_i1 = evaluate_reference_entitlement(supports_mono, ["D"], "C")
    ref_i2 = evaluate_reference_entitlement(supports_mono, ["D", "E"], "C")
    auth_i1 = policy_fn(ref_i1, supports_mono, lin_mono).action_authority
    auth_i2 = policy_fn(ref_i2, supports_mono, lin_mono).action_authority
    ax1 = auth_i2 <= (auth_i1 + 1e-6)
    if not ax1:
        failures.append(f"Axiom 1 failed: Auth(I2={auth_i2}) > Auth(I1={auth_i1})")
        
    # 2. Axiom 2: Zero on Retraction (Ent*=0 => Auth=0.0)
    ref_ret = evaluate_reference_entitlement(supports_mono, ["A", "D"], "C")
    auth_ret = policy_fn(ref_ret, supports_mono, lin_mono).action_authority
    ax2 = (auth_ret == 0.0)
    if not ax2:
        failures.append(f"Axiom 2 failed: Retracted claim received Auth={auth_ret}")
        
    # 3. Axiom 3: Non-Destructive Degradation Sensitivity (DEGRADED => 0 < Auth < Auth(unchanged))
    # Test on shared-root S={{A,B}, {A,D}} with I={B}
    supports_sr = [["A", "B"], ["A", "D"]]
    lin_sr = {"A": "R1", "B": "R2", "D": "R3"}
    ref_unch = evaluate_reference_entitlement(supports_sr, [], "C")
    ref_deg = evaluate_reference_entitlement(supports_sr, ["B"], "C")
    auth_unch = policy_fn(ref_unch, supports_sr, lin_sr).action_authority
    auth_deg = policy_fn(ref_deg, supports_sr, lin_sr).action_authority
    ax3 = (0.0 < auth_deg < auth_unch)
    if not ax3:
        failures.append(f"Axiom 3 failed: Degraded state received Auth={auth_deg} vs Unchanged={auth_unch}")
        
    # 4. Axiom 4: No Duplication Authority (Duplicate support set cannot increase authority)
    supports_dup = [["A", "B"], ["A", "B"], ["D", "E"]]
    ref_dup = evaluate_reference_entitlement(supports_dup, [], "C")
    ref_orig = evaluate_reference_entitlement(supports_mono, [], "C")
    auth_dup = policy_fn(ref_dup, supports_dup, lin_mono).action_authority
    auth_orig = policy_fn(ref_orig, supports_mono, lin_mono).action_authority
    ax4 = (abs(auth_dup - auth_orig) < 1e-6)
    if not ax4:
        failures.append(f"Axiom 4 failed: Duplicating path changed Auth from {auth_orig} to {auth_dup}")
        
    # 5. Axiom 5: Bloat Invariance (Irrelevant distractor E_S > 0 cannot change authority)
    ref_bloat = evaluate_reference_entitlement(supports_mono, [], "C")
    auth_bloat = policy_fn(ref_bloat, supports_mono, lin_mono).action_authority
    ax5 = (abs(auth_bloat - auth_orig) < 1e-6)
    if not ax5:
        failures.append(f"Axiom 5 failed: Explanatory bloat altered Auth")
        
    # 6. Axiom 6: Lineage Independence Discounting (Single-root alternative < Multi-root alternative)
    # S1={{A,B}, {D,E}} where A,B,D,E <- R1 (shared root) vs A,B <- R1, D,E <- R2 (independent roots)
    lin_single_root = {"A": "R1", "B": "R1", "D": "R1", "E": "R1"}
    lin_multi_root = {"A": "R1", "B": "R1", "D": "R2", "E": "R2"}
    ref_base = evaluate_reference_entitlement(supports_mono, [], "C")
    auth_single_root = policy_fn(ref_base, supports_mono, lin_single_root).action_authority
    auth_multi_root = policy_fn(ref_base, supports_mono, lin_multi_root).action_authority
    ax6 = (auth_single_root < auth_multi_root)
    if not ax6:
        failures.append(
            f"Axiom 6 failed: Single-root Auth ({auth_single_root}) not discounted vs Multi-root Auth ({auth_multi_root})"
        )
        
    # 7. Axiom 7: Isomorphism Invariance (Premise renaming preserves exact authority)
    supports_iso = [["X", "Y"], ["W", "Z"]]
    lin_iso = {"X": "R1", "Y": "R1", "W": "R2", "Z": "R2"}
    ref_iso = evaluate_reference_entitlement(supports_iso, [], "C")
    auth_iso = policy_fn(ref_iso, supports_iso, lin_iso).action_authority
    ax7 = (abs(auth_iso - auth_multi_root) < 1e-6)
    if not ax7:
        failures.append(f"Axiom 7 failed: Isomorphism Auth ({auth_iso}) != Original Auth ({auth_multi_root})")
        
    passed_count = sum([ax1, ax2, ax3, ax4, ax5, ax6, ax7])
    is_compliant = (passed_count == 7)
    
    return AxiomaticComplianceReport(
        policy_name=policy_name,
        axiom_1_monotonicity=ax1,
        axiom_2_zero_on_retraction=ax2,
        axiom_3_degradation_sensitivity=ax3,
        axiom_4_no_duplication_inflation=ax4,
        axiom_5_bloat_invariance=ax5,
        axiom_6_lineage_independence_discounting=ax6,
        axiom_7_isomorphism_invariance=ax7,
        total_passed=passed_count,
        is_fully_compliant=is_compliant,
        failure_reasons=failures,
    )
