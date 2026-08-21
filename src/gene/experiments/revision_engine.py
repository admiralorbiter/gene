"""GENE Exploration Round 5: Support-First Epistemic Revision Engine.

Implements reference entitlement semantics Ent*(c, I), resilience degradation kappa(c),
candidate lossy memory representation policies, and root-expanded DAG dependency tracking.
Composes the underlying MinimalSupportEngine from gene.experiments.multi_justification.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from gene.experiments.multi_justification import MinimalSupportEngine


class EntitlementStatus(str, Enum):
    """Tripartite ground-truth entitlement status under assumption invalidation."""
    UNCHANGED = "UNCHANGED"
    DEGRADED = "DEGRADED"
    RETRACTED = "RETRACTED"


class RevisionImpact(str, Enum):
    """Granular network impact classification for a downstream belief under change."""
    UNAFFECTED = "UNAFFECTED"
    METADATA_UPDATE_ONLY = "METADATA_UPDATE_ONLY"  # Entitled, but S' or kappa changed
    REDERIVATION_REQUIRED = "REDERIVATION_REQUIRED"  # Broken active derivation path
    RETRACTION_REQUIRED = "RETRACTION_REQUIRED"  # Lost all valid justification


class RevisionCase(BaseModel):
    """Definition of a single local revision scenario."""
    case_id: str
    target_claim: str
    support_family: list[list[str]]  # Minimal support environments S(c)
    reported_representations: dict[str, list[str]]  # representation_name -> evidence_list
    lineage_map: dict[str, str]  # premise_id -> root_origin_id
    invalidated_assumptions: list[str]  # Invalidation set I
    all_assumptions: list[str]


class ReferenceRevisionResult(BaseModel):
    """Ground-truth entitlement result evaluated under reference semantics Ent*(c, I)."""
    target_claim: str
    status: EntitlementStatus
    is_entitled: bool
    initial_supports: list[list[str]]
    surviving_supports: list[list[str]]
    initial_kappa: int
    surviving_kappa: int
    invalidated_assumptions: list[str]


class PolicyRevisionResult(BaseModel):
    """Evaluation result for a specific candidate memory revision policy."""
    policy_name: str
    predicted_entitled: bool
    is_false_retraction: bool  # Policy killed claim when Ent* is entitled (Autoimmunity)
    is_missed_retraction: bool  # Policy kept claim when Ent* is retracted (Corruption)
    is_correct_entitlement: bool
    concordant_with_oracle: bool
    details: dict[str, Any] = Field(default_factory=dict)


def evaluate_reference_entitlement(
    support_family: list[list[str]],
    invalidated_assumptions: set[str] | list[str],
    claim_name: str = "c",
) -> ReferenceRevisionResult:
    """Compute exact ground-truth entitlement Ent*(c, I) using MinimalSupportEngine."""
    inval_set = set(invalidated_assumptions)
    
    # Engine before invalidation
    engine_init = MinimalSupportEngine()
    for s in support_family:
        engine_init.add_support_set(claim_name, set(s))
    
    init_active = [sorted(list(s)) for s in engine_init.active_support_sets(claim_name)]
    init_kappa = engine_init.epistemic_resilience(claim_name)
    
    # Engine after invalidation
    engine_post = MinimalSupportEngine()
    for s in support_family:
        engine_post.add_support_set(claim_name, set(s))
    for inv in inval_set:
        engine_post.invalidate_ancestor(inv)
        
    surv_active = [sorted(list(s)) for s in engine_post.active_support_sets(claim_name)]
    surv_kappa = engine_post.epistemic_resilience(claim_name)
    is_entitled = len(surv_active) > 0
    
    # Determine tripartite status
    all_premises = set().union(*[set(s) for s in support_family])
    if not (all_premises & inval_set):
        status = EntitlementStatus.UNCHANGED
    elif is_entitled:
        status = EntitlementStatus.DEGRADED
    else:
        status = EntitlementStatus.RETRACTED
        
    return ReferenceRevisionResult(
        target_claim=claim_name,
        status=status,
        is_entitled=is_entitled,
        initial_supports=sorted(init_active),
        surviving_supports=sorted(surv_active),
        initial_kappa=init_kappa,
        surviving_kappa=surv_kappa,
        invalidated_assumptions=sorted(list(inval_set)),
    )


def evaluate_policy_naive_conjunction(
    reported_evidence: list[str],
    invalidated_assumptions: set[str] | list[str],
    reference: ReferenceRevisionResult,
    policy_name: str = "naive_conjunction",
) -> PolicyRevisionResult:
    """Evaluate flat conjunctive dependency policy: claim lives iff R(c) intersect I == empty."""
    inval_set = set(invalidated_assumptions)
    rep_set = set(reported_evidence)
    
    # Policy predicts alive iff no reported item is invalidated
    predicted_entitled = not bool(rep_set & inval_set)
    
    is_false_retraction = (not predicted_entitled) and reference.is_entitled
    is_missed_retraction = predicted_entitled and (not reference.is_entitled)
    is_correct = (predicted_entitled == reference.is_entitled)
    
    return PolicyRevisionResult(
        policy_name=policy_name,
        predicted_entitled=predicted_entitled,
        is_false_retraction=is_false_retraction,
        is_missed_retraction=is_missed_retraction,
        is_correct_entitlement=is_correct,
        concordant_with_oracle=is_correct,
        details={
            "reported_evidence": sorted(list(rep_set)),
            "hit_invalidated": sorted(list(rep_set & inval_set)),
        }
    )


def evaluate_policy_lineage_quarantine(
    support_family: list[list[str]],
    lineage_map: dict[str, str],
    invalidated_assumptions: set[str] | list[str],
    reference: ReferenceRevisionResult,
    policy_name: str = "lineage_quarantine",
) -> PolicyRevisionResult:
    """Evaluate lineage quarantine policy: claim lives iff NO ancestor root is tainted."""
    inval_set = set(invalidated_assumptions)
    
    # Find all ancestral roots for any premise participating in S(c)
    all_premises = set().union(*[set(s) for s in support_family])
    ancestral_roots = {lineage_map.get(p, p) for p in all_premises}
    
    # Tainted if any premise OR its root is in invalidation set
    is_tainted = bool(all_premises & inval_set) or bool(ancestral_roots & inval_set)
    predicted_entitled = not is_tainted
    
    is_false_retraction = (not predicted_entitled) and reference.is_entitled
    is_missed_retraction = predicted_entitled and (not reference.is_entitled)
    is_correct = (predicted_entitled == reference.is_entitled)
    
    return PolicyRevisionResult(
        policy_name=policy_name,
        predicted_entitled=predicted_entitled,
        is_false_retraction=is_false_retraction,
        is_missed_retraction=is_missed_retraction,
        is_correct_entitlement=is_correct,
        concordant_with_oracle=is_correct,
        details={
            "ancestral_roots": sorted(list(ancestral_roots)),
            "is_tainted": is_tainted,
        }
    )


class DAGNode(BaseModel):
    """Represents a node in a multi-tier derivation DAG."""
    node_id: str
    is_root: bool = False
    # Direct parent rule conjuncts: each inner list is a valid minimal parent set
    direct_parent_supports: list[list[str]] = Field(default_factory=list)


class RevisionDAG(BaseModel):
    """Multi-tier derivation graph with root-expanded support computation."""
    nodes: dict[str, DAGNode]

    def compute_root_supports(self, node_id: str) -> list[set[str]]:
        """Recursively expand direct parent dependencies into minimal root assumption sets."""
        node = self.nodes[node_id]
        if node.is_root or not node.direct_parent_supports:
            return [{node_id}]
        
        root_support_sets: list[set[str]] = []
        for direct_conjunct in node.direct_parent_supports:
            # direct_conjunct is e.g. ["G1", "E"]
            # Get root supports for each parent in the conjunct
            parent_root_options = [self.compute_root_supports(p) for p in direct_conjunct]
            
            # Cartesian product across the conjunct
            import itertools
            for combo in itertools.product(*parent_root_options):
                # combo is e.g. ({A, B}, {E})
                merged_root_env = set().union(*combo)
                root_support_sets.append(merged_root_env)
                
        # Minimize the root support sets (remove supersets)
        minimized: list[set[str]] = []
        for s in root_support_sets:
            # Check if any strict subset is already present
            if not any(prior < s for prior in root_support_sets if prior != s):
                if s not in minimized:
                    minimized.append(s)
                    
        return minimized

    def evaluate_cascade_impact(
        self,
        invalidated_roots: set[str] | list[str],
    ) -> dict[str, RevisionImpact]:
        """Evaluate exact network impact for all nodes under root invalidation."""
        inval_set = set(invalidated_roots)
        impact_map: dict[str, RevisionImpact] = {}
        
        for node_id, node in self.nodes.items():
            if node.is_root:
                if node_id in inval_set:
                    impact_map[node_id] = RevisionImpact.RETRACTION_REQUIRED
                else:
                    impact_map[node_id] = RevisionImpact.UNAFFECTED
                continue
                
            root_supports = self.compute_root_supports(node_id)
            ref = evaluate_reference_entitlement(
                [sorted(list(s)) for s in root_supports],
                inval_set,
                claim_name=node_id,
            )
            
            if ref.status == EntitlementStatus.UNCHANGED:
                impact_map[node_id] = RevisionImpact.UNAFFECTED
            elif ref.status == EntitlementStatus.RETRACTED:
                impact_map[node_id] = RevisionImpact.RETRACTION_REQUIRED
            elif ref.status == EntitlementStatus.DEGRADED:
                # Check if currently active direct parent support was broken
                # For simplicity in 5A, if entitled but degraded, classified as metadata update
                impact_map[node_id] = RevisionImpact.METADATA_UPDATE_ONLY
                
        return impact_map
