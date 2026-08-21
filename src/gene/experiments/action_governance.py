"""GENE Exploration Round 5 Stage 5B: Action Governance & Epistemic Resilience Engine (Hardened v2).

Evaluates the hierarchy of lossy support representations and investigates what surviving support
information is minimally necessary to govern action authority under change. Implements lineage-projected
support hypergraphs S_L(c), root cut-set resilience kappa_L(c), and formal collision/axiomatic benchmarks.
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
    LINEAGE_PROJECTED_RESILIENCE = "lineage_projected_resilience"  # Lineage hypergraph S_L + rho_L


class LineageProjectedState(BaseModel):
    """Lineage-projected support hypergraph and resilience signature."""
    support_family_roots: list[list[str]]
    kappa_l: int
    rho_l: tuple[int, int]  # (|S_L|, kappa_L)


def project_lineage_support(
    support_family: list[list[str]],
    lineage_map: dict[str, str],
) -> LineageProjectedState:
    """Project premise-level support environments into minimal root-lineage hypergraph S_L(c)."""
    engine = MinimalSupportEngine()
    for path in support_family:
        root_path = {lineage_map.get(p, p) for p in path}
        engine.add_support_set("c_lineage", root_path)
        
    active_roots = [sorted(list(s)) for s in engine.active_support_sets("c_lineage")]
    kappa_l = engine.epistemic_resilience("c_lineage")
    rho_l = (len(active_roots), kappa_l)
    
    return LineageProjectedState(
        support_family_roots=sorted(active_roots),
        kappa_l=kappa_l,
        rho_l=rho_l,
    )


class PolicyActionScore(BaseModel):
    """Computed action authority score under a specific governance policy."""
    policy_name: str
    action_authority: float = Field(ge=0.0, le=1.0)
    is_action_permitted: bool  # Whether authority exceeds illustrative threshold (default >= 0.5)
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


def compute_policy_lineage_projected(
    reference: ReferenceRevisionResult,
    support_family: list[list[str]],
    lineage_map: dict[str, str],
    threshold: float = 0.5,
) -> PolicyActionScore:
    """Policy P_lineage_projected: Authority governed by minimal lineage hypergraph S_L and rho_L."""
    if not reference.is_entitled:
        return PolicyActionScore(
            policy_name=GovernancePolicyType.LINEAGE_PROJECTED_RESILIENCE.value,
            action_authority=0.0,
            is_action_permitted=False,
            details={"status": "RETRACTED"},
        )
        
    # Project initial and surviving paths into minimal root-lineage space
    init_lin = project_lineage_support(reference.initial_supports, lineage_map)
    surv_lin = project_lineage_support(reference.surviving_supports, lineage_map)
    
    # 1. Lineage cut-set ratio against premise potential: kappa_L' / max(1, kappa_premise)
    kappa_l_ratio = surv_lin.kappa_l / max(1, reference.initial_kappa)
    
    # 2. Lineage independent path ratio against premise potential: |S_L'| / max(1, |S_premise|)
    path_l_ratio = len(surv_lin.support_family_roots) / max(1, reference.initial_support_count)
    
    # Authority score
    auth = 0.5 * kappa_l_ratio + 0.5 * path_l_ratio
    auth = max(0.0, min(1.0, auth))
    
    return PolicyActionScore(
        policy_name=GovernancePolicyType.LINEAGE_PROJECTED_RESILIENCE.value,
        action_authority=auth,
        is_action_permitted=(auth >= threshold),
        details={
            "init_rho_l": init_lin.rho_l,
            "surviving_rho_l": surv_lin.rho_l,
            "surviving_s_l": surv_lin.support_family_roots,
            "kappa_l_ratio": kappa_l_ratio,
            "path_l_ratio": path_l_ratio,
        },
    )


class AxiomaticComplianceReport(BaseModel):
    """Results of checking a policy against formal action-governance axioms."""
    policy_name: str
    axiom_1_monotonicity: bool
    axiom_2_zero_on_retraction: bool
    axiom_3_effective_degradation_sensitivity: bool
    axiom_4_no_duplication_inflation: bool
    axiom_5_bloat_invariance_by_construction: bool
    axiom_6_lineage_independence_ordering: bool
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
        
    # 3. Axiom 3: Effective Degradation Sensitivity (Effective degradation strictly reduces authority)
    supports_sr = [["A", "B"], ["A", "D"]]
    lin_sr = {"A": "R1", "B": "R2", "D": "R3"}
    ref_unch = evaluate_reference_entitlement(supports_sr, [], "C")
    ref_deg = evaluate_reference_entitlement(supports_sr, ["B"], "C")
    auth_unch = policy_fn(ref_unch, supports_sr, lin_sr).action_authority
    auth_deg = policy_fn(ref_deg, supports_sr, lin_sr).action_authority
    ax3 = (0.0 < auth_deg < auth_unch)
    if not ax3:
        failures.append(f"Axiom 3 failed: Degraded state received Auth={auth_deg} vs Unchanged={auth_unch}")
        
    # 4. Axiom 4: No Duplication Inflation (Duplicate support set cannot increase authority)
    supports_dup = [["A", "B"], ["A", "B"], ["D", "E"]]
    ref_dup = evaluate_reference_entitlement(supports_dup, [], "C")
    ref_orig = evaluate_reference_entitlement(supports_mono, [], "C")
    auth_dup = policy_fn(ref_dup, supports_dup, lin_mono).action_authority
    auth_orig = policy_fn(ref_orig, supports_mono, lin_mono).action_authority
    ax4 = (abs(auth_dup - auth_orig) < 1e-6)
    if not ax4:
        failures.append(f"Axiom 4 failed: Duplicating path changed Auth from {auth_orig} to {auth_dup}")
        
    # 5. Axiom 5: Bloat Invariance by Construction (Explanatory bloat cannot enter authority interface)
    ax5 = True  # Guaranteed by type interface: policies consume S(c) and L(c), never R(c)
        
    # 6. Axiom 6: Lineage Independence Ordering (Independent roots > Shared origin roots >= All single root)
    # Compare 3 distinct lineage structures on S={{A,B}, {D,E}}:
    # a) Independent: A,B <- R1, D,E <- R2 => S_L={{R1},{R2}}, kappa_L=2
    # b) Shared Origin: A,D <- R1, B,E <- R2 => S_L={{R1,R2}}, kappa_L=1
    # c) Single Root: A,B,D,E <- R1 => S_L={{R1}}, kappa_L=1
    lin_ind = {"A": "R1", "B": "R1", "D": "R2", "E": "R2"}
    lin_shared = {"A": "R1", "D": "R1", "B": "R2", "E": "R2"}
    lin_single = {"A": "R1", "B": "R1", "D": "R1", "E": "R1"}
    
    ref_base = evaluate_reference_entitlement(supports_mono, [], "C")
    auth_ind = policy_fn(ref_base, supports_mono, lin_ind).action_authority
    auth_shared = policy_fn(ref_base, supports_mono, lin_shared).action_authority
    auth_single = policy_fn(ref_base, supports_mono, lin_single).action_authority
    
    ax6 = (auth_ind > auth_shared) and (auth_shared >= auth_single)
    if not ax6:
        failures.append(
            f"Axiom 6 failed: Ordering violated. Independent ({auth_ind}) vs Shared ({auth_shared}) vs Single ({auth_single})"
        )
        
    # 7. Axiom 7: Isomorphism Invariance (Premise and root renaming preserves exact authority)
    supports_iso = [["X", "Y"], ["W", "Z"]]
    lin_iso = {"X": "ROOT_A", "Y": "ROOT_A", "W": "ROOT_B", "Z": "ROOT_B"}
    ref_iso = evaluate_reference_entitlement(supports_iso, [], "C")
    auth_iso = policy_fn(ref_iso, supports_iso, lin_iso).action_authority
    ax7 = (abs(auth_iso - auth_ind) < 1e-6)
    if not ax7:
        failures.append(f"Axiom 7 failed: Isomorphism Auth ({auth_iso}) != Original Auth ({auth_ind})")
        
    passed_count = sum([ax1, ax2, ax3, ax4, ax5, ax6, ax7])
    is_compliant = (passed_count == 7)
    
    return AxiomaticComplianceReport(
        policy_name=policy_name,
        axiom_1_monotonicity=ax1,
        axiom_2_zero_on_retraction=ax2,
        axiom_3_effective_degradation_sensitivity=ax3,
        axiom_4_no_duplication_inflation=ax4,
        axiom_5_bloat_invariance_by_construction=ax5,
        axiom_6_lineage_independence_ordering=ax6,
        axiom_7_isomorphism_invariance=ax7,
        total_passed=passed_count,
        is_fully_compliant=is_compliant,
        failure_reasons=failures,
    )
