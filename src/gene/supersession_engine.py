"""Bitemporal Supersession and Epistemic State Transition Algebra (Stage 6A-v2).

Implements the deterministic formal engine for bitemporal truth maintenance:
- Valid Time (t_v): When a fact, interval, or conflict holds true in the world.
- Knowledge Time (t_k): When the agent learned or committed the fact/event.

Key Architectural Invariants:
1. Occurrence-based interval tracking: Reassertion and recurrent validity intervals
   (e.g., [0, 5) and [10, inf)) are fully supported without historical clipping.
2. Bitemporal conflict tracking: Contradiction events carry valid-time bounds [t_v_start, t_v_end),
   so epistemic disputes at t_v=5 do not falsely invalidate undisputed history at t_v=2.
3. Multi-pair conflict resolution: Conflicts are maintained as undirected pairs C(t_v | t_k) = {{f_a, f_b}}.
   Resolving {A, B} preserves active disputes on {A, C}.
4. Deep THEN_WHAT transition discovery: Detects changes in entitlement, support geometry S(c),
   lineage geometry S_L(c), and relative/bounded action authority.
5. Action authority semantics: Separates RelativeAuthority (unbounded robustness index)
   from BoundedAuthority (strict [0, 1] authorization gating score).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import Any


class EventType(str, Enum):
    """Bitemporal state transition event types."""
    ASSERT = "ASSERT"
    SUPERSEDES = "SUPERSEDES"
    RETRACT = "RETRACT"
    EXPIRES = "EXPIRES"
    CONTRADICTS = "CONTRADICTS"
    RESOLVE_CONFLICT = "RESOLVE_CONFLICT"


@dataclass(frozen=True)
class BitemporalFact:
    """Ground proposition template with permanent identifier and root lineage."""
    fact_id: str
    subject: str
    predicate: str
    obj: str
    roots: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def triple(self) -> tuple[str, str, str]:
        return (self.subject, self.predicate, self.obj)


@dataclass(frozen=True)
class BitemporalRule:
    """Horn derivation rule: Head <= Body_1, ..., Body_k."""
    rule_id: str
    head: tuple[str, str, str]
    body: tuple[tuple[str, str, str], ...]
    roots: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class TemporalEvent:
    """Immutable event recording a state transition at knowledge time t_k with valid time interval [t_v_start, t_v_end)."""
    event_id: str
    event_type: EventType
    t_knowledge: int
    t_valid_start: float = 0.0
    t_valid_end: float | None = None
    target_fact_id: str = ""
    secondary_fact_id: str | None = None
    occurrence_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


def compute_antichain(sets: set[frozenset[str]]) -> set[frozenset[str]]:
    """Strict subset elimination: retain only minimal sets under inclusion."""
    if not sets:
        return set()
    antichain: set[frozenset[str]] = set()
    sorted_sets = sorted(sets, key=len)
    for s in sorted_sets:
        if not any(other < s for other in antichain):
            antichain.add(s)
    return antichain


def compute_cut_set_size(support_sets: set[frozenset[str]]) -> int:
    """Compute exact minimal hitting / cut-set size kappa."""
    if not support_sets:
        return 0
    if frozenset() in support_sets:
        return 0

    all_elements: set[str] = set()
    for s in support_sets:
        all_elements.update(s)

    elem_list = sorted(all_elements)
    n = len(elem_list)

    for k in range(1, n + 1):
        for combo in combinations(elem_list, k):
            combo_set = set(combo)
            if all(bool(s & combo_set) for s in support_sets):
                return k
    return n


class BitemporalEngine:
    """Deterministic bitemporal truth maintenance engine."""

    def __init__(self, cautious_conflicts: bool = True):
        self.cautious_conflicts = cautious_conflicts
        self.facts: dict[str, BitemporalFact] = {}
        self.rules: dict[str, BitemporalRule] = {}
        self.events: list[TemporalEvent] = []

    def register_fact(self, fact: BitemporalFact) -> None:
        """Register a fact template."""
        self.facts[fact.fact_id] = fact

    def register_rule(self, rule: BitemporalRule) -> None:
        """Register a Horn derivation rule."""
        self.rules[rule.rule_id] = rule

    def record_event(self, event: TemporalEvent) -> None:
        """Append an event to the authoritative event log."""
        self.events.append(event)
        self.events.sort(key=lambda e: (e.t_knowledge, e.event_id))

    def get_events_up_to(self, t_k: int, extra_events: list[TemporalEvent] | None = None) -> list[TemporalEvent]:
        """Return all events known at or before transaction time t_k."""
        ev_list = [e for e in self.events if e.t_knowledge <= t_k]
        if extra_events:
            ev_list.extend([e for e in extra_events if e.t_knowledge <= t_k])
        ev_list.sort(key=lambda e: (e.t_knowledge, e.event_id))
        return ev_list

    def is_fact_valid(
        self,
        fact_id: str,
        t_v: float,
        t_k: int,
        extra_events: list[TemporalEvent] | None = None,
    ) -> bool:
        """Determine whether fact_id holds true at valid time t_v, as known at transaction time t_k."""
        if fact_id not in self.facts:
            return False

        events = self.get_events_up_to(t_k, extra_events)

        # 1. Compute valid intervals per assertion occurrence
        # Each ASSERT event creates an independent assertion occurrence interval [s_i, e_i)
        occurrences: list[dict[str, Any]] = []
        for ev in events:
            if ev.target_fact_id == fact_id and ev.event_type == EventType.ASSERT:
                start = ev.t_valid_start
                end = ev.t_valid_end if ev.t_valid_end is not None else float("inf")
                occurrences.append({
                    "start": start,
                    "end": end,
                    "occ_id": ev.occurrence_id or ev.event_id,
                })

        if not occurrences:
            return False

        # Apply truncating events (RETRACT, SUPERSEDES, EXPIRES) to overlapping occurrences
        active_intervals: list[tuple[float, float]] = []
        for occ in occurrences:
            s = occ["start"]
            e = occ["end"]

            for ev in events:
                # Retraction of this fact truncates interval if cut time falls inside [s, e)
                if ev.event_type == EventType.RETRACT and ev.target_fact_id == fact_id:
                    cut_t = ev.t_valid_start
                    if s <= cut_t < e:
                        e = cut_t

                # Supersession of this fact (secondary_fact_id) truncates interval
                if ev.event_type == EventType.SUPERSEDES and ev.secondary_fact_id == fact_id:
                    cut_t = ev.t_valid_start
                    if s <= cut_t < e:
                        e = cut_t

                # Expiration
                if ev.event_type == EventType.EXPIRES and ev.target_fact_id == fact_id:
                    cut_t = ev.t_valid_start
                    if s <= cut_t < e:
                        e = cut_t

            if s <= t_v < e:
                active_intervals.append((s, e))

        if not active_intervals:
            return False

        # 2. Check bitemporal conflicts active at (t_v, t_k)
        # Active conflict pair is active if ev.t_valid_start <= t_v < ev.t_valid_end
        active_conflicts: set[frozenset[str]] = set()
        for ev in events:
            c_start = ev.t_valid_start
            c_end = ev.t_valid_end if ev.t_valid_end is not None else float("inf")

            if ev.event_type == EventType.CONTRADICTS and ev.secondary_fact_id:
                if c_start <= t_v < c_end:
                    pair = frozenset([ev.target_fact_id, ev.secondary_fact_id])
                    active_conflicts.add(pair)

            elif ev.event_type == EventType.RESOLVE_CONFLICT and ev.secondary_fact_id:
                if c_start <= t_v < c_end:
                    pair = frozenset([ev.target_fact_id, ev.secondary_fact_id])
                    active_conflicts.discard(pair)

        if self.cautious_conflicts:
            if any(fact_id in pair for pair in active_conflicts):
                return False

        return True

    def get_active_facts(
        self,
        t_v: float,
        t_k: int,
        extra_events: list[TemporalEvent] | None = None,
    ) -> list[BitemporalFact]:
        """Return all active facts holding at valid time t_v as known at t_k."""
        return [f for f in self.facts.values() if self.is_fact_valid(f.fact_id, t_v, t_k, extra_events)]

    def compute_temporal_support(
        self,
        query: tuple[str, str, str],
        t_v: float,
        t_k: int,
        extra_events: list[TemporalEvent] | None = None,
    ) -> set[frozenset[str]]:
        """Compute minimal active premise support sets S_{t_v}(query | t_k) via Horn backward chaining."""
        active_facts = self.get_active_facts(t_v, t_k, extra_events)
        active_triples: dict[tuple[str, str, str], list[BitemporalFact]] = {}
        for f in active_facts:
            active_triples.setdefault(f.triple, []).append(f)

        memo: dict[tuple[str, str, str], set[frozenset[str]]] = {}
        visiting: set[tuple[str, str, str]] = set()

        def derive(target: tuple[str, str, str]) -> set[frozenset[str]]:
            if target in memo:
                return memo[target]
            if target in visiting:
                return set()

            visiting.add(target)
            results: set[frozenset[str]] = set()

            # Base fact match
            if target in active_triples:
                for f in active_triples[target]:
                    results.add(frozenset([f.fact_id]))

            # Rule derivations
            for rule in self.rules.values():
                if rule.head == target:
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
        t_v: float,
        t_k: int,
        extra_events: list[TemporalEvent] | None = None,
    ) -> set[frozenset[str]]:
        """Compute antichain-minimized lineage-projected support hypergraph S_{L,t_v}(query | t_k)."""
        support_sets = self.compute_temporal_support(query, t_v, t_k, extra_events)
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

    def compute_relative_authority(
        self,
        query: tuple[str, str, str],
        t_v: float,
        t_k: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
        extra_events: list[TemporalEvent] | None = None,
    ) -> float:
        """Compute relative resilience index RelAuth (baseline = 1.0, degraded < 1.0, reinforced > 1.0)."""
        current_l = self.compute_temporal_lineage(query, t_v, t_k, extra_events)
        if not current_l:
            return 0.0

        if init_lineage_sets is None or not init_lineage_sets:
            return 1.0

        kappa_curr = compute_cut_set_size(current_l)
        kappa_init = compute_cut_set_size(init_lineage_sets)
        paths_curr = len(current_l)
        paths_init = len(init_lineage_sets)

        kappa_ratio = (kappa_curr / kappa_init) if kappa_init > 0 else 0.0
        paths_ratio = (paths_curr / paths_init) if paths_init > 0 else 0.0

        return 0.5 * (kappa_ratio + paths_ratio)

    def compute_bounded_authority(
        self,
        query: tuple[str, str, str],
        t_v: float,
        t_k: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
        extra_events: list[TemporalEvent] | None = None,
    ) -> float:
        """Compute clamped authorization score Auth in [0.0, 1.0]."""
        rel_auth = self.compute_relative_authority(query, t_v, t_k, init_lineage_sets, extra_events)
        return min(1.0, max(0.0, rel_auth))

    def get_all_derived_propositions(self) -> set[tuple[str, str, str]]:
        """Discover all possible target conclusions in the deductive rule closure."""
        targets: set[tuple[str, str, str]] = set()
        for r in self.rules.values():
            targets.add(r.head)
        for f in self.facts.values():
            targets.add(f.triple)
        return targets

    def why_t(
        self,
        query: tuple[str, str, str],
        t_v: float,
        t_k: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
    ) -> dict[str, Any]:
        """Explain why a claim is entitled at valid time t_v as known at transaction time t_k."""
        support = self.compute_temporal_support(query, t_v, t_k)
        lineage = self.compute_temporal_lineage(query, t_v, t_k)
        rel_auth = self.compute_relative_authority(query, t_v, t_k, init_lineage_sets)
        bnd_auth = self.compute_bounded_authority(query, t_v, t_k, init_lineage_sets)

        return {
            "query": query,
            "t_valid": t_v,
            "t_knowledge": t_k,
            "is_entitled": len(support) > 0,
            "support_sets_S_t": [sorted(list(s)) for s in sorted(support, key=lambda x: sorted(list(x)))],
            "lineage_sets_S_L_t": [sorted(list(s)) for s in sorted(lineage, key=lambda x: sorted(list(x)))],
            "lineage_cut_set_kappa_L": compute_cut_set_size(lineage),
            "relative_authority": round(rel_auth, 4),
            "bounded_authority": round(bnd_auth, 4),
        }

    def what_if_t(
        self,
        query: tuple[str, str, str],
        event: TemporalEvent,
        t_v: float,
        t_k: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
    ) -> dict[str, Any]:
        """Evaluate hypothetical entitlement under counterfactual event without persistent state mutation."""
        eval_tk = max(t_k, event.t_knowledge)
        base_state = self.why_t(query, t_v, eval_tk, init_lineage_sets)
        hypo_support = self.compute_temporal_support(query, t_v, eval_tk, extra_events=[event])
        hypo_lineage = self.compute_temporal_lineage(query, t_v, eval_tk, extra_events=[event])
        hypo_rel_auth = self.compute_relative_authority(query, t_v, eval_tk, init_lineage_sets, extra_events=[event])
        hypo_bnd_auth = self.compute_bounded_authority(query, t_v, eval_tk, init_lineage_sets, extra_events=[event])

        prior_supp = base_state["support_sets_S_t"]
        hypo_supp_sorted = [sorted(list(s)) for s in sorted(hypo_support, key=lambda x: sorted(list(x)))]
        prior_lin = base_state["lineage_sets_S_L_t"]
        hypo_lin_sorted = [sorted(list(s)) for s in sorted(hypo_lineage, key=lambda x: sorted(list(x)))]

        support_changed = prior_supp != hypo_supp_sorted
        lineage_changed = prior_lin != hypo_lin_sorted
        auth_changed = base_state["relative_authority"] != round(hypo_rel_auth, 4)
        ent_changed = base_state["is_entitled"] != (len(hypo_support) > 0)

        # Transition classification
        if base_state["is_entitled"] and not (len(hypo_support) > 0):
            transition = "LOST_ENTITLEMENT"
        elif not base_state["is_entitled"] and (len(hypo_support) > 0):
            transition = "GAINED_ENTITLEMENT"
        elif base_state["relative_authority"] > hypo_rel_auth:
            transition = "DEGRADED_AUTHORITY"
        elif base_state["relative_authority"] < hypo_rel_auth:
            transition = "AUGMENTED_AUTHORITY"
        elif lineage_changed:
            transition = "LINEAGE_GEOMETRY_CHANGED"
        elif support_changed:
            transition = "SUPPORT_GEOMETRY_CHANGED"
        else:
            transition = "NO_CHANGE"

        return {
            "query": query,
            "t_valid": t_v,
            "t_knowledge": eval_tk,
            "simulated_event": {
                "event_type": event.event_type.value,
                "target_fact_id": event.target_fact_id,
                "secondary_fact_id": event.secondary_fact_id,
            },
            "prior_entitled": base_state["is_entitled"],
            "hypothetical_entitled": len(hypo_support) > 0,
            "prior_relative_authority": base_state["relative_authority"],
            "hypothetical_relative_authority": round(hypo_rel_auth, 4),
            "prior_bounded_authority": base_state["bounded_authority"],
            "hypothetical_bounded_authority": round(hypo_bnd_auth, 4),
            "support_geometry_changed": support_changed,
            "lineage_geometry_changed": lineage_changed,
            "transition": transition,
            "hypothetical_support_S": hypo_supp_sorted,
            "hypothetical_lineage_S_L": hypo_lin_sorted,
        }

    def then_what_t(
        self,
        event: TemporalEvent,
        t_v: float,
        t_k: int,
        baseline_lineage_map: dict[tuple[str, str, str], set[frozenset[str]]] | None = None,
    ) -> dict[str, Any]:
        """Compute full downstream impact across all derivable propositions using deep dirty-state checking."""
        eval_tk = max(t_k, event.t_knowledge)
        candidate_queries = sorted(list(self.get_all_derived_propositions()))

        impacted: list[dict[str, Any]] = []
        for q in candidate_queries:
            init_l = baseline_lineage_map.get(q) if baseline_lineage_map else None
            analysis = self.what_if_t(q, event, t_v, eval_tk, init_lineage_sets=init_l)

            if analysis["transition"] != "NO_CHANGE":
                impacted.append({
                    "query": q,
                    "prior_entitled": analysis["prior_entitled"],
                    "post_entitled": analysis["hypothetical_entitled"],
                    "prior_relative_authority": analysis["prior_relative_authority"],
                    "post_relative_authority": analysis["hypothetical_relative_authority"],
                    "transition": analysis["transition"],
                })

        return {
            "t_valid": t_v,
            "t_knowledge": eval_tk,
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
        valid_timestamps: list[float],
        t_k: int,
        init_lineage_sets: set[frozenset[str]] | None = None,
    ) -> list[dict[str, Any]]:
        """Compute chronological progression of entitlement states across valid time t_v given transaction time t_k."""
        records: list[dict[str, Any]] = []
        for tv in valid_timestamps:
            info = self.why_t(query, tv, t_k, init_lineage_sets)
            records.append({
                "t_valid": tv,
                "t_knowledge": t_k,
                "entitled": info["is_entitled"],
                "relative_authority": info["relative_authority"],
                "bounded_authority": info["bounded_authority"],
                "support_paths_count": len(info["support_sets_S_t"]),
                "roots_count": len(info["lineage_sets_S_L_t"]),
            })
        return records

    def audit_conflicts(self, t_v: float, t_k: int) -> list[dict[str, str]]:
        """List all unresolved contradiction pairs active at (t_v, t_k)."""
        events = self.get_events_up_to(t_k)
        active_conflicts: set[frozenset[str]] = set()

        for ev in events:
            c_start = ev.t_valid_start
            c_end = ev.t_valid_end if ev.t_valid_end is not None else float("inf")

            if ev.event_type == EventType.CONTRADICTS and ev.secondary_fact_id:
                if c_start <= t_v < c_end:
                    pair = frozenset([ev.target_fact_id, ev.secondary_fact_id])
                    active_conflicts.add(pair)
            elif ev.event_type == EventType.RESOLVE_CONFLICT and ev.secondary_fact_id:
                if c_start <= t_v < c_end:
                    pair = frozenset([ev.target_fact_id, ev.secondary_fact_id])
                    active_conflicts.discard(pair)

        return [{"fact_a": sorted(list(p))[0], "fact_b": sorted(list(p))[1]} for p in sorted(active_conflicts, key=lambda x: sorted(list(x)))]
