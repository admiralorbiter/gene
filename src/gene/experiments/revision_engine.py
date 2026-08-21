"""GENE Exploration Round 5: Support-First Epistemic Revision Engine.

Implements reference entitlement semantics Ent*(c, I), resilience signatures rho(c) = (|S(c)|, kappa(c)),
candidate lossy memory representation policies, root-expanded DAG dependency tracking,
and stale cached-parent baselines.
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
    RETRACTION_REQUIRED = "RETRACTION_REQUIRED"  # Lost all valid justification


class ReferenceRevisionResult(BaseModel):
    """Ground-truth entitlement result evaluated under reference semantics Ent*(c, I)."""
    target_claim: str
    status: EntitlementStatus
    is_entitled: bool
    initial_supports: list[list[str]]
    surviving_supports: list[list[str]]
    initial_support_count: int
    surviving_support_count: int
    initial_kappa: int
    surviving_kappa: int
    initial_rho: tuple[int, int]  # (|S|, kappa)
    surviving_rho: tuple[int, int]  # (|S'|, kappa')
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
    init_count = len(init_active)
    init_rho = (init_count, init_kappa)
    
    # Engine after invalidation
    engine_post = MinimalSupportEngine()
    for s in support_family:
        engine_post.add_support_set(claim_name, set(s))
    for inv in inval_set:
        engine_post.invalidate_ancestor(inv)
        
    surv_active = [sorted(list(s)) for s in engine_post.active_support_sets(claim_name)]
    surv_kappa = engine_post.epistemic_resilience(claim_name)
    surv_count = len(surv_active)
    surv_rho = (surv_count, surv_kappa)
    is_entitled = surv_count > 0
    
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
        initial_support_count=init_count,
        surviving_support_count=surv_count,
        initial_kappa=init_kappa,
        surviving_kappa=surv_kappa,
        initial_rho=init_rho,
        surviving_rho=surv_rho,
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
    invalidated_items: set[str] | list[str],
    reference: ReferenceRevisionResult,
    policy_name: str = "lineage_quarantine",
) -> PolicyRevisionResult:
    """Evaluate lineage quarantine policy: claim is quarantined if ANY of its ancestral roots is tainted."""
    inval_set = set(invalidated_items)
    
    # 1. Identify all tainted ancestral roots from the invalidation set
    tainted_roots = set()
    for item in inval_set:
        if item in lineage_map:
            tainted_roots.add(lineage_map[item])
        else:
            tainted_roots.add(item)  # Item is itself a root ID
            
    # 2. Find all ancestral roots for all premises participating in S(c)
    all_premises = set().union(*[set(s) for s in support_family])
    claim_roots = {lineage_map.get(p, p) for p in all_premises}
    
    # 3. Claim is tainted if its roots intersect the tainted roots
    is_tainted = bool(claim_roots & tainted_roots)
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
            "claim_roots": sorted(list(claim_roots)),
            "tainted_roots": sorted(list(tainted_roots)),
            "hit_roots": sorted(list(claim_roots & tainted_roots)),
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
    """Multi-tier derivation graph with root-expanded support computation and stale-baseline contrast."""
    nodes: dict[str, DAGNode]

    def compute_root_supports(self, node_id: str) -> list[set[str]]:
        """Recursively expand direct parent dependencies into minimal root assumption sets."""
        node = self.nodes[node_id]
        if node.is_root or not node.direct_parent_supports:
            return [{node_id}]
        
        root_support_sets: list[set[str]] = []
        for direct_conjunct in node.direct_parent_supports:
            # direct_conjunct is e.g. ["G1", "E"]
            parent_root_options = [self.compute_root_supports(p) for p in direct_conjunct]
            
            import itertools
            for combo in itertools.product(*parent_root_options):
                merged_root_env = set().union(*combo)
                root_support_sets.append(merged_root_env)
                
        # Minimize the root support sets (remove supersets)
        minimized: list[set[str]] = []
        for s in root_support_sets:
            if not any(prior < s for prior in root_support_sets if prior != s):
                if s not in minimized:
                    minimized.append(s)
                    
        return minimized

    def evaluate_cascade_reference(
        self,
        invalidated_roots: set[str] | list[str],
    ) -> dict[str, RevisionImpact]:
        """Evaluate exact ground-truth network impact via root-expanded support algebra."""
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
                impact_map[node_id] = RevisionImpact.METADATA_UPDATE_ONLY
                
        return impact_map

    def evaluate_cascade_stale_cached(
        self,
        invalidated_roots: set[str] | list[str],
        stale_cached_nodes: set[str],
    ) -> dict[str, RevisionImpact]:
        """Evaluate revision where intermediate nodes in stale_cached_nodes present stale alive status."""
        inval_set = set(invalidated_roots)
        impact_map: dict[str, RevisionImpact] = {}
        
        # 1. Evaluate roots (G0)
        for node_id, node in self.nodes.items():
            if node.is_root:
                if node_id in inval_set:
                    impact_map[node_id] = RevisionImpact.RETRACTION_REQUIRED
                else:
                    impact_map[node_id] = RevisionImpact.UNAFFECTED
                    
        # 2. Evaluate intermediate and downstream nodes in topological dependency order
        # For our G0 -> G1 -> G2 DAG:
        for node_id, node in self.nodes.items():
            if node.is_root:
                continue
                
            # Compute actual status of this node from its roots
            root_supports = self.compute_root_supports(node_id)
            actual_ref = evaluate_reference_entitlement(
                [sorted(list(s)) for s in root_supports],
                inval_set,
                claim_name=node_id,
            )
            
            # Non-root nodes check their immediate parents:
            # A parent p is perceived as available iff:
            # - p is in stale_cached_nodes (stale cache treats it as alive), OR
            # - impact_map[p] is not RETRACTION_REQUIRED
            parent_conjuncts = node.direct_parent_supports
            perceived_surviving_conjuncts = 0
            for conj in parent_conjuncts:
                conj_valid = True
                for p in conj:
                    parent_actual_impact = impact_map.get(p, RevisionImpact.UNAFFECTED)
                    parent_is_retracted = (parent_actual_impact == RevisionImpact.RETRACTION_REQUIRED)
                    parent_is_stale = (p in stale_cached_nodes)
                    
                    # If parent is retracted and NOT stale-cached, conjunct is broken!
                    if parent_is_retracted and not parent_is_stale:
                        conj_valid = False
                        break
                if conj_valid:
                    perceived_surviving_conjuncts += 1
                    
            if perceived_surviving_conjuncts == 0:
                impact_map[node_id] = RevisionImpact.RETRACTION_REQUIRED
            elif perceived_surviving_conjuncts < len(parent_conjuncts) or actual_ref.status == EntitlementStatus.DEGRADED:
                impact_map[node_id] = RevisionImpact.METADATA_UPDATE_ONLY
            else:
                impact_map[node_id] = RevisionImpact.UNAFFECTED
                
        return impact_map
