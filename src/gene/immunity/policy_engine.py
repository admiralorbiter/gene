"""Epistemic Immunity Policy Engine for Experiment 1B-C.

Implements delayed-adjudication candidate filtering policies and exact 4-state
analytic risk signal probability weighting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal
import itertools
import random


PolicyName = Literal[
    "baseline",
    "uniform_thinning",
    "random_family_quarantine",
    "node_only_quarantine",
    "lineage_quarantine",
    "oracle_upper_bound",
]


@dataclass(frozen=True)
class PolicyNode:
    """Lightweight immutable node representation for immunity filtering."""
    node_id: str
    locus_id: str
    generation: int
    parent_ids: tuple[str, ...] = ()
    is_root: bool = False
    family_id: str | None = None
    is_infected_allele: bool = False
    text: str = ""


@dataclass
class PolicyEvaluationResult:
    """Outcome of filtering a candidate pool under a specific policy and signal state."""
    policy: PolicyName
    signal_state: tuple[int, int]  # (S_H, S_I)
    retained_node_ids: set[str]
    quarantined_node_ids: set[str]
    retained_count: int
    quarantined_count: int


def get_analytic_state_weights(tpr: float, fpr: float) -> dict[tuple[int, int], float]:
    """Compute exact joint probability distribution over the 4 root signal states (S_H, S_I).

    Assumes conditional independence: P(S_H, S_I) = P(S_H) * P(S_I).

    States:
      (0, 0): Healthy negative (true neg), Infected negative (false neg)
      (1, 0): Healthy positive (false pos), Infected negative (false neg)
      (0, 1): Healthy negative (true neg), Infected positive (true pos)
      (1, 1): Healthy positive (false pos), Infected positive (true pos)
    """
    return {
        (0, 0): (1.0 - fpr) * (1.0 - tpr),
        (1, 0): fpr * (1.0 - tpr),
        (0, 1): (1.0 - fpr) * tpr,
        (1, 1): fpr * tpr,
    }


class EpistemicPolicyEngine:
    """Deterministic policy engine for delayed-adjudication memory candidate filtering."""

    @staticmethod
    def find_all_descendants(nodes: list[PolicyNode], flagged_node_ids: set[str]) -> set[str]:
        """Find all transitive descendants of flagged nodes using parent_ids links."""
        quarantined = set(flagged_node_ids)
        changed = True
        
        while changed:
            changed = False
            for n in nodes:
                if n.node_id not in quarantined:
                    # If any parent is quarantined, this node is also quarantined
                    if any(pid in quarantined for pid in n.parent_ids):
                        quarantined.add(n.node_id)
                        changed = True
        return quarantined

    @classmethod
    def apply_policy(
        cls,
        policy: PolicyName,
        nodes: list[PolicyNode],
        root_signals: dict[str, bool],
        clean_root_id: str,
        infected_root_id: str,
        signal_state: tuple[int, int],
        seed: int = 42,
    ) -> PolicyEvaluationResult:
        """Apply a specified quarantine or thinning policy to a candidate pool."""
        all_ids = {n.node_id for n in nodes}
        node_map = {n.node_id: n for n in nodes}

        if policy == "baseline":
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=all_ids,
                quarantined_node_ids=set(),
                retained_count=len(all_ids),
                quarantined_count=0,
            )

        if policy == "oracle_upper_bound":
            # Perfect ground-truth root flag: infected root is flagged, clean root is never flagged
            flagged_roots = {infected_root_id} if infected_root_id in node_map else set()
            quarantined = cls.find_all_descendants(nodes, flagged_roots)
            retained = all_ids - quarantined
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=retained,
                quarantined_node_ids=quarantined,
                retained_count=len(retained),
                quarantined_count=len(quarantined),
            )

        # Extract currently flagged roots under external risk signal
        flagged_roots = {
            n.node_id for n in nodes
            if n.is_root and root_signals.get(n.node_id, False)
        }

        if policy == "node_only_quarantine":
            # Only the flagged root nodes are removed; descendants survive and shed the flag
            quarantined = set(flagged_roots)
            retained = all_ids - quarantined
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=retained,
                quarantined_node_ids=quarantined,
                retained_count=len(retained),
                quarantined_count=len(quarantined),
            )

        if policy == "lineage_quarantine":
            # Flagged roots and all transitive descendants are quarantined
            quarantined = cls.find_all_descendants(nodes, flagged_roots)
            retained = all_ids - quarantined
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=retained,
                quarantined_node_ids=quarantined,
                retained_count=len(retained),
                quarantined_count=len(quarantined),
            )

        if policy == "random_family_quarantine":
            # Control for cluster/family topology:
            # First compute how many nodes lineage quarantine would drop in this state
            lin_res = cls.apply_policy("lineage_quarantine", nodes, root_signals, clean_root_id, infected_root_id, signal_state)
            m = lin_res.quarantined_count
            if m == 0:
                return PolicyEvaluationResult(
                    policy=policy,
                    signal_state=signal_state,
                    retained_node_ids=all_ids,
                    quarantined_node_ids=set(),
                    retained_count=len(all_ids),
                    quarantined_count=0,
                )
            
            # Select a random family of nodes to quarantine
            families = {}
            for n in nodes:
                fid = n.family_id or n.node_id
                families.setdefault(fid, []).append(n.node_id)
            
            rng = random.Random(seed + signal_state[0] * 100 + signal_state[1] * 10)
            family_keys = sorted(list(families.keys()))
            chosen_family = rng.choice(family_keys)
            family_nodes = set(families[chosen_family])
            
            # If family size doesn't equal m, adjust deterministically to match m
            if len(family_nodes) > m:
                quarantined = set(sorted(list(family_nodes))[:m])
            elif len(family_nodes) < m:
                remainder = sorted(list(all_ids - family_nodes))
                quarantined = family_nodes | set(remainder[:m - len(family_nodes)])
            else:
                quarantined = family_nodes

            retained = all_ids - quarantined
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=retained,
                quarantined_node_ids=quarantined,
                retained_count=len(retained),
                quarantined_count=len(quarantined),
            )

        if policy == "uniform_thinning":
            # Per-state matched candidate drop count:
            # Drop exactly m eligible nodes uniformly at random from the candidate pool
            lin_res = cls.apply_policy("lineage_quarantine", nodes, root_signals, clean_root_id, infected_root_id, signal_state)
            m = lin_res.quarantined_count
            if m == 0:
                return PolicyEvaluationResult(
                    policy=policy,
                    signal_state=signal_state,
                    retained_node_ids=all_ids,
                    quarantined_node_ids=set(),
                    retained_count=len(all_ids),
                    quarantined_count=0,
                )
            
            rng = random.Random(seed + signal_state[0] * 100 + signal_state[1] * 10)
            sorted_nodes = sorted(list(all_ids))
            quarantined = set(rng.sample(sorted_nodes, min(m, len(sorted_nodes))))
            retained = all_ids - quarantined
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=retained,
                quarantined_node_ids=quarantined,
                retained_count=len(retained),
                quarantined_count=len(quarantined),
            )

        raise ValueError(f"Unknown policy: {policy}")
