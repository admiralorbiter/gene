"""Epistemic Immunity Policy Engine for Experiment 1B-C.

Implements delayed-adjudication candidate filtering policies and exact 4-state
analytic risk signal probability weighting across 7 distinct control and intervention treatments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal
import itertools
import random


PolicyName = Literal[
    "baseline",
    "signal_blind_uniform_thinning",
    "signal_conditioned_uniform_thinning",
    "generation_matched_thinning",
    "random_family_quarantine",
    "node_only_quarantine",
    "lineage_quarantine",
    "oracle_upper_bound",
    "uniform_thinning",  # Backwards-compatible alias for signal_conditioned_uniform_thinning
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
    policy: str
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
        policy: str,
        nodes: list[PolicyNode],
        root_signals: dict[str, bool],
        clean_root_id: str,
        infected_root_id: str,
        signal_state: tuple[int, int],
        seed: int = 42,
        fixed_thinning_budget: int = 3,
    ) -> PolicyEvaluationResult:
        """Apply a specified quarantine or thinning policy to a candidate pool."""
        all_ids = {n.node_id for n in nodes}
        node_map = {n.node_id: n for n in nodes}

        # 1. Baseline: no filtering
        if policy == "baseline":
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=all_ids,
                quarantined_node_ids=set(),
                retained_count=len(all_ids),
                quarantined_count=0,
            )

        # 2. Oracle Upper Bound: perfect ground-truth root flag
        if policy == "oracle_upper_bound":
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

        # 3. Signal-Blind Uniform Thinning: fixed candidate drop budget without detector signal
        if policy == "signal_blind_uniform_thinning":
            m = min(fixed_thinning_budget, len(all_ids))
            rng = random.Random(seed)
            sorted_nodes = sorted(list(all_ids))
            quarantined = set(rng.sample(sorted_nodes, m))
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

        # 4. Node-Only Quarantine: flagged root removed; descendants survive and shed the flag
        if policy == "node_only_quarantine":
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

        # 5. Lineage Quarantine: flagged roots and all transitive descendants are quarantined
        if policy == "lineage_quarantine":
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

        # Reference lineage quarantine outcome to determine state-matched drop counts
        lin_res = cls.apply_policy("lineage_quarantine", nodes, root_signals, clean_root_id, infected_root_id, signal_state)
        m_total = lin_res.quarantined_count

        # 6. Signal-Conditioned Uniform Thinning: matched total drop count without lineage knowledge
        if policy in ("signal_conditioned_uniform_thinning", "uniform_thinning"):
            if m_total == 0:
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
            quarantined = set(rng.sample(sorted_nodes, min(m_total, len(sorted_nodes))))
            retained = all_ids - quarantined
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=retained,
                quarantined_node_ids=quarantined,
                retained_count=len(retained),
                quarantined_count=len(quarantined),
            )

        # 7. Generation-Matched Thinning: matched G2 drop count chosen from generation 2 nodes
        if policy == "generation_matched_thinning":
            # Count how many G2 nodes lineage quarantine removed
            lin_g2_quarantined = {
                n.node_id for n in nodes
                if n.node_id in lin_res.quarantined_node_ids and n.generation == 2
            }
            m_g2 = len(lin_g2_quarantined)

            if m_g2 == 0:
                return PolicyEvaluationResult(
                    policy=policy,
                    signal_state=signal_state,
                    retained_node_ids=all_ids,
                    quarantined_node_ids=set(),
                    retained_count=len(all_ids),
                    quarantined_count=0,
                )

            g2_nodes = sorted([n.node_id for n in nodes if n.generation == 2])
            rng = random.Random(seed + signal_state[0] * 100 + signal_state[1] * 10)
            quarantined = set(rng.sample(g2_nodes, min(m_g2, len(g2_nodes))))
            retained = all_ids - quarantined
            return PolicyEvaluationResult(
                policy=policy,
                signal_state=signal_state,
                retained_node_ids=retained,
                quarantined_node_ids=quarantined,
                retained_count=len(retained),
                quarantined_count=len(quarantined),
            )

        # 8. Random Family Quarantine: matched cluster shape chosen at random
        if policy == "random_family_quarantine":
            if m_total == 0:
                return PolicyEvaluationResult(
                    policy=policy,
                    signal_state=signal_state,
                    retained_node_ids=all_ids,
                    quarantined_node_ids=set(),
                    retained_count=len(all_ids),
                    quarantined_count=0,
                )
            
            families = {}
            for n in nodes:
                fid = n.family_id or n.node_id
                families.setdefault(fid, []).append(n.node_id)
            
            rng = random.Random(seed + signal_state[0] * 100 + signal_state[1] * 10)
            family_keys = sorted(list(families.keys()))
            chosen_family = rng.choice(family_keys)
            family_nodes = set(families[chosen_family])
            
            if len(family_nodes) > m_total:
                quarantined = set(sorted(list(family_nodes))[:m_total])
            elif len(family_nodes) < m_total:
                remainder = sorted(list(all_ids - family_nodes))
                quarantined = family_nodes | set(remainder[:m_total - len(family_nodes)])
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

        raise ValueError(f"Unknown policy: {policy}")
