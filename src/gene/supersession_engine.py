"""Temporal Supersession and Epistemic State Transition Algebra (Stage 6A).

Implements the deterministic formal engine for tracking temporal validity,
implicit supersession, expiration, contradiction isolation, and dynamic
antichain-minimized support hypergraphs S_t(c) and S_L,t(c) under natural change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Discrete temporal change event types."""
    ADD = "ADD"
    SUPERSEDES = "SUPERSEDES"
    RETRACT = "RETRACT"
    EXPIRES = "EXPIRES"
    CONTRADICTS = "CONTRADICTS"
    RESOLVE_CONFLICT = "RESOLVE_CONFLICT"


@dataclass(frozen=True)
class TemporalFact:
    """A ground factual proposition with temporal and lineage metadata."""
    fact_id: str
    subject: str
    predicate: str
    obj: str
    asserted_at: int = 0
    roots: frozenset[str] = field(default_factory=frozenset)
    expires_at: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def triple(self) -> tuple[str, str, str]:
        return (self.subject, self.predicate, self.obj)


@dataclass(frozen=True)
class TemporalRule:
    """Horn derivation rule: Head <= Body_1, ..., Body_k."""
    rule_id: str
    head: tuple[str, str, str]
    body: tuple[tuple[str, str, str], ...]
    roots: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class TemporalEvent:
    """An immutable event recording a state transition at timestamp t."""
    event_id: str
    event_type: EventType
    timestamp: int
    target_fact_id: str
    secondary_fact_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


def compute_antichain(sets: set[frozenset[str]]) -> set[frozenset[str]]:
    """Strict subset elimination: keep only minimal sets under set inclusion."""
    if not sets:
        return set()
    antichain: set[frozenset[str]] = set()
    sorted_sets = sorted(sets, key=len)
    for s in sorted_sets:
        if not any(other < s for other in antichain):
            antichain.add(s)
    return antichain


def compute_cut_set_size(support_sets: set[frozenset[str]]) -> int:
    """Compute exact minimal cut-set size kappa (minimum elements hitting all sets)."""
    if not support_sets:
        return 0
    if frozenset() in support_sets:
        return 0

    all_elements: set[str] = set()
    for s in support_sets:
        all_elements.update(s)

    elem_list = sorted(all_elements)
    n = len(elem_list)

    # Breadth-first search for minimal hitting set
    from itertools import combinations
    for k in range(1, n + 1):
        for combo in combinations(elem_list, k):
            combo_set = set(combo)
            if all(bool(s & combo_set) for s in support_sets):
                return k
    return n


class SupersessionEngine:
    """Deterministic truth maintenance and temporal validity engine."""

    def __init__(self, cautious_conflicts: bool = True):
        self.cautious_conflicts = cautious_conflicts
        self.facts: dict[str, TemporalFact] = {}
        self.rules: dict[str, TemporalRule] = {}
        self.events: list[TemporalEvent] = []

    def add_fact(self, fact: TemporalFact) -> None:
        """Register a factual premise."""
        self.facts[fact.fact_id] = fact

    def add_rule(self, rule: TemporalRule) -> None:
        """Register a Horn derivation rule."""
        self.rules[rule.rule_id] = rule

    def record_event(self, event: TemporalEvent) -> None:
        """Append a state transition event to the timeline."""
        self.events.append(event)
        # Sort events chronologically to preserve deterministic playback
        self.events.sort(key=lambda e: (e.timestamp, e.event_id))

    def is_fact_valid(self, fact_id: str, t: int, simulated_events: list[TemporalEvent] | None = None) -> bool:
        """Determine whether a fact is active and valid at timestamp t."""
        if fact_id not in self.facts:
            return False

        fact = self.facts[fact_id]
        if fact.asserted_at > t:
            return False

        if fact.expires_at is not None and t >= fact.expires_at:
            return False

        all_events = self.events if simulated_events is None else sorted(self.events + simulated_events, key=lambda e: (e.timestamp, e.event_id))

        in_conflict = False
        for ev in all_events:
            if ev.timestamp > t:
                continue

            # Retraction terminates validity
            if ev.event_type == EventType.RETRACT and ev.target_fact_id == fact_id:
                return False

            # Supersession terminates validity of the superseded old fact
            if ev.event_type == EventType.SUPERSEDES and ev.secondary_fact_id == fact_id:
                return False

            # Contradiction marks fact in conflict
            if ev.event_type == EventType.CONTRADICTS:
                if ev.target_fact_id == fact_id or ev.secondary_fact_id == fact_id:
                    in_conflict = True

            # Resolving conflict clears the conflict flag
            if ev.event_type == EventType.RESOLVE_CONFLICT:
                if ev.target_fact_id == fact_id or ev.secondary_fact_id == fact_id:
                    in_conflict = False

        if in_conflict and self.cautious_conflicts:
            return False

        return True

    def get_active_facts(self, t: int, simulated_events: list[TemporalEvent] | None = None) -> list[TemporalFact]:
        """Return all active facts at timestamp t."""
        return [f for f in self.facts.values() if self.is_fact_valid(f.fact_id, t, simulated_events)]

    def compute_temporal_support(
        self,
        query: tuple[str, str, str],
        t: int,
        simulated_events: list[TemporalEvent] | None = None,
    ) -> set[frozenset[str]]:
        """Compute minimal active premise support sets S_t(query) via backward chaining."""
        active_facts = self.get_active_facts(t, simulated_events)
        active_triples: dict[tuple[str, str, str], list[TemporalFact]] = {}
        for f in active_facts:
            active_triples.setdefault(f.triple, []).append(f)

        # Memoization cache for derivation paths to prevent infinite recursion
        memo: dict[tuple[str, str, str], set[frozenset[str]]] = {}
        visiting: set[tuple[str, str, str]] = set()

        def derive(target: tuple[str, str, str]) -> set[frozenset[str]]:
            if target in memo:
                return memo[target]
            if target in visiting:
                return set()  # Cycle detected

            visiting.add(target)
            results: set[frozenset[str]] = set()

            # 1. Base facts directly matching target
            if target in active_triples:
                for f in active_triples[target]:
                    results.add(frozenset([f.fact_id]))

            # 2. Rule derivations
            for rule in self.rules.values():
                if rule.head == target:
                    # Cartesian product across body premise derivations
                    body_supports: list[set[frozenset[str]]] = []
                    valid_rule = True
                    for body_triple in rule.body:
                        b_supp = derive(body_triple)
                        if not b_supp:
                            valid_rule = False
                            break
                        body_supports.append(b_supp)

                    if valid_rule and body_supports:
                        combined: set[frozenset[str]] = {frozenset()}
                        for b_supp in body_supports:
                            next_comb = set()
                            for cur in combined:
                                for s in b_supp:
                                    next_comb.add(cur | s)
                            combined = next_comb
                        results.update(combined)

            visiting.remove(target)
            minimized = compute_antichain(results)
            memo[target] = minimized
            return minimized

        return derive(query)

    def compute_temporal_lineage(
        self,
        query: tuple[str, str, str],
        t: int,
        simulated_events: list[TemporalEvent] | None = None,
    ) -> set[frozenset[str]]:
        """Compute antichain-minimized lineage-projected support hypergraph S_L,t(query)."""
        support_sets = self.compute_temporal_support(query, t, simulated_events)
        if not support_sets:
            return set()

        lineage_sets: set[frozenset[str]] = set()
        for s in support_sets:
            l_set: set[str] = set()
            for fact_id in s:
                if fact_id in self.facts:
                    l_set.update(self.facts[fact_id].roots)
            if l_set:
                lineage_sets.add(frozenset(l_set))

        return compute_antichain(lineage_sets)

    def compute_authority(
        self,
        query: tuple[str, str, str],
        t: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
        simulated_events: list[TemporalEvent] | None = None,
    ) -> float:
        """Compute normalized action governance authority Auth_t(query)."""
        current_l = self.compute_temporal_lineage(query, t, simulated_events)
        if not current_l:
            return 0.0

        if init_lineage_sets is None or not init_lineage_sets:
            # Baseline is current state
            return 1.0

        kappa_curr = compute_cut_set_size(current_l)
        kappa_init = compute_cut_set_size(init_lineage_sets)
        paths_curr = len(current_l)
        paths_init = len(init_lineage_sets)

        kappa_ratio = (kappa_curr / kappa_init) if kappa_init > 0 else 0.0
        paths_ratio = (paths_curr / paths_init) if paths_init > 0 else 0.0

        return 0.5 * (kappa_ratio + paths_ratio)

    def why_t(
        self,
        query: tuple[str, str, str],
        t: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
    ) -> dict[str, Any]:
        """Query why a claim is entitled at timestamp t."""
        support = self.compute_temporal_support(query, t)
        lineage = self.compute_temporal_lineage(query, t)
        auth = self.compute_authority(query, t, init_lineage_sets)

        return {
            "query": query,
            "timestamp": t,
            "is_entitled": len(support) > 0,
            "support_sets_S_t": [sorted(list(s)) for s in sorted(support, key=lambda x: sorted(list(x)))],
            "lineage_sets_S_L_t": [sorted(list(s)) for s in sorted(lineage, key=lambda x: sorted(list(x)))],
            "lineage_cut_set_kappa_L": compute_cut_set_size(lineage),
            "authority_score": round(auth, 4),
        }

    def what_if_t(
        self,
        query: tuple[str, str, str],
        event: TemporalEvent,
        t: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
    ) -> dict[str, Any]:
        """Evaluate hypothetical entitlement under counterfactual event without state mutation."""
        eval_t = max(t, event.timestamp)
        base_state = self.why_t(query, eval_t, init_lineage_sets)
        hypo_support = self.compute_temporal_support(query, eval_t, simulated_events=[event])
        hypo_lineage = self.compute_temporal_lineage(query, eval_t, simulated_events=[event])
        hypo_auth = self.compute_authority(query, eval_t, init_lineage_sets, simulated_events=[event])

        return {
            "query": query,
            "timestamp": eval_t,
            "simulated_event": {
                "event_type": event.event_type.value,
                "target_fact_id": event.target_fact_id,
                "secondary_fact_id": event.secondary_fact_id,
            },
            "prior_entitled": base_state["is_entitled"],
            "hypothetical_entitled": len(hypo_support) > 0,
            "prior_authority": base_state["authority_score"],
            "hypothetical_authority": round(hypo_auth, 4),
            "hypothetical_support_S": [sorted(list(s)) for s in sorted(hypo_support, key=lambda x: sorted(list(x)))],
            "hypothetical_lineage_S_L": [sorted(list(s)) for s in sorted(hypo_lineage, key=lambda x: sorted(list(x)))],
        }

    def then_what_t(
        self,
        event: TemporalEvent,
        candidate_queries: list[tuple[str, str, str]],
        t: int,
    ) -> dict[str, Any]:
        """Compute downstream impact of event across candidate queries."""
        eval_t = max(t, event.timestamp)
        impacted: list[dict[str, Any]] = []
        for q in candidate_queries:
            analysis = self.what_if_t(q, event, eval_t)
            if (analysis["prior_entitled"] != analysis["hypothetical_entitled"] or
                    analysis["prior_authority"] != analysis["hypothetical_authority"]):
                impacted.append({
                    "query": q,
                    "prior_entitled": analysis["prior_entitled"],
                    "post_entitled": analysis["hypothetical_entitled"],
                    "prior_authority": analysis["prior_authority"],
                    "post_authority": analysis["hypothetical_authority"],
                    "transition": (
                        "LOST_ENTITLEMENT" if analysis["prior_entitled"] and not analysis["hypothetical_entitled"]
                        else "GAINED_ENTITLEMENT" if not analysis["prior_entitled"] and analysis["hypothetical_entitled"]
                        else "DEGRADED_AUTHORITY" if analysis["prior_authority"] > analysis["hypothetical_authority"]
                        else "AUGMENTED_AUTHORITY"
                    )
                })

        return {
            "timestamp": eval_t,
            "event": {
                "event_type": event.event_type.value,
                "target_fact_id": event.target_fact_id,
                "secondary_fact_id": event.secondary_fact_id,
            },
            "impacted_count": len(impacted),
            "impacted_propositions": impacted,
        }

    def timeline(
        self,
        query: tuple[str, str, str],
        max_t: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
    ) -> list[dict[str, Any]]:
        """Compute full chronological progression of entitlement states from t=0 to max_t."""
        records: list[dict[str, Any]] = []
        for t in range(max_t + 1):
            info = self.why_t(query, t, init_lineage_sets)
            records.append({
                "t": t,
                "entitled": info["is_entitled"],
                "authority": info["authority_score"],
                "support_paths_count": len(info["support_sets_S_t"]),
                "roots_count": len(info["lineage_sets_S_L_t"]),
            })
        return records

    def audit_conflicts(self, t: int) -> list[dict[str, Any]]:
        """Identify all active contradiction pairs at timestamp t."""
        conflicts: list[dict[str, Any]] = []
        for ev in self.events:
            if ev.timestamp <= t and ev.event_type == EventType.CONTRADICTS:
                # Check if resolved
                resolved = any(
                    rev.timestamp <= t and rev.event_type == EventType.RESOLVE_CONFLICT and
                    {rev.target_fact_id, rev.secondary_fact_id} == {ev.target_fact_id, ev.secondary_fact_id}
                    for rev in self.events
                )
                if not resolved:
                    conflicts.append({
                        "event_id": ev.event_id,
                        "timestamp": ev.timestamp,
                        "fact_a": ev.target_fact_id,
                        "fact_b": ev.secondary_fact_id,
                    })
        return conflicts
