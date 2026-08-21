"""Exhaustive Small-History Model Checker & Standalone Oracle Invariance.

Implements an independent reference interpreter with standalone antichain and
power-set deduction algorithms, verifying BitemporalEngine across exhaustive
small-history event permutations.
"""

from __future__ import annotations

import itertools
import pytest
from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    BitemporalRule,
    EventType,
    TemporalEvent,
)


def independent_antichain(sets: set[frozenset[str]]) -> set[frozenset[str]]:
    """Standalone reference antichain implementation with zero production code dependency."""
    res = set()
    for s in sets:
        if not any(other < s for other in sets):
            res.add(s)
    return res


class StandaloneReferenceInterpreter:
    """Completely independent reference oracle."""

    def __init__(self, facts: list[BitemporalFact], rules: list[BitemporalRule], events: list[TemporalEvent]):
        self.facts = {f.fact_id: f for f in facts}
        self.rules = list(rules)
        self.events = sorted(list(events), key=lambda e: (e.t_knowledge, e.event_seq, e.event_id))

    def is_valid(self, fid: str, t_v: float, t_k: int) -> bool:
        """Evaluate occurrence node validity directly from raw event log."""
        occurrences: list[tuple[float, float]] = []
        for ev in self.events:
            if ev.t_knowledge <= t_k and ev.target_fact_id == fid and ev.event_type == EventType.ASSERT:
                start = ev.t_valid_start
                end = ev.t_valid_end if ev.t_valid_end is not None else float("inf")
                occurrences.append((start, end))

        if not occurrences:
            return False

        active_intervals: list[tuple[float, float]] = []
        for (s, e) in occurrences:
            cur_s, cur_e = s, e
            for ev in self.events:
                if ev.t_knowledge <= t_k:
                    if ev.event_type == EventType.RETRACT and ev.target_fact_id == fid:
                        if cur_s <= ev.t_valid_start < cur_e:
                            cur_e = ev.t_valid_start
                    elif ev.event_type == EventType.SUPERSEDES and ev.secondary_fact_id == fid:
                        if cur_s <= ev.t_valid_start < cur_e:
                            cur_e = ev.t_valid_start
                    elif ev.event_type == EventType.EXPIRES and ev.target_fact_id == fid:
                        if cur_s <= ev.t_valid_start < cur_e:
                            cur_e = ev.t_valid_start

            if cur_s <= t_v < cur_e:
                active_intervals.append((cur_s, cur_e))

        if not active_intervals:
            return False

        conflicts: set[frozenset[str]] = set()
        for ev in self.events:
            if ev.t_knowledge <= t_k:
                c_s = ev.t_valid_start
                c_e = ev.t_valid_end if ev.t_valid_end is not None else float("inf")
                if c_s <= t_v < c_e:
                    if ev.event_type == EventType.CONTRADICTS and ev.secondary_fact_id:
                        conflicts.add(frozenset([ev.target_fact_id, ev.secondary_fact_id]))
                    elif ev.event_type == EventType.RESOLVE_CONFLICT and ev.secondary_fact_id:
                        conflicts.discard(frozenset([ev.target_fact_id, ev.secondary_fact_id]))

        if any(fid in pair for pair in conflicts):
            return False

        return True

    def compute_support(self, query: tuple[str, str, str], t_v: float, t_k: int) -> set[frozenset[str]]:
        """Power-set deduction and independent antichain minimization."""
        valid_fids = [fid for fid in sorted(self.facts.keys()) if self.is_valid(fid, t_v, t_k)]
        n = len(valid_fids)
        satisfying: set[frozenset[str]] = set()

        for k in range(1, n + 1):
            for combo in itertools.combinations(valid_fids, k):
                known_triples = {self.facts[f].triple for f in combo}
                changed = True
                while changed:
                    changed = False
                    for r in self.rules:
                        if r.head not in known_triples and all(b in known_triples for b in r.body):
                            known_triples.add(r.head)
                            changed = True
                if query in known_triples:
                    satisfying.add(frozenset(combo))

        return independent_antichain(satisfying)


def test_exhaustive_small_world_event_permutations_including_supersedes():
    """Exhaustively model check event permutation sequences across ASSERT, RETRACT, SUPERSEDES, EXPIRES, CONTRADICT, RESOLVE."""
    f1 = BitemporalFact("occ1", "A", "rel", "1", roots=frozenset(["R1"]))
    f2 = BitemporalFact("occ2", "B", "rel", "2", roots=frozenset(["R2"]))
    f3 = BitemporalFact("occ3", "A", "rel", "3", roots=frozenset(["R3"]))
    facts = [f1, f2, f3]
    r1 = BitemporalRule("r1", ("Goal", "status", "OK"), (("A", "rel", "1"),))
    r2 = BitemporalRule("r2", ("Goal", "status", "OK"), (("A", "rel", "3"),))
    rules = [r1, r2]

    # Mutation pool exercising all 5 discrete mutation types
    event_pool = [
        TemporalEvent("ev_ret1", EventType.RETRACT, t_knowledge=2, event_seq=0, t_valid_start=3.0, target_fact_id="occ1"),
        TemporalEvent("ev_sup13", EventType.SUPERSEDES, t_knowledge=2, event_seq=1, t_valid_start=3.0, target_fact_id="occ3", secondary_fact_id="occ1"),
        TemporalEvent("ev_exp1", EventType.EXPIRES, t_knowledge=2, event_seq=0, t_valid_start=4.0, target_fact_id="occ1"),
        TemporalEvent("ev_conf", EventType.CONTRADICTS, t_knowledge=1, event_seq=0, t_valid_start=2.0, t_valid_end=5.0, target_fact_id="occ1", secondary_fact_id="occ2"),
        TemporalEvent("ev_res", EventType.RESOLVE_CONFLICT, t_knowledge=3, event_seq=0, t_valid_start=2.0, t_valid_end=5.0, target_fact_id="occ1", secondary_fact_id="occ2"),
    ]

    base_asserts = [
        TemporalEvent("ev_ass1", EventType.ASSERT, t_knowledge=0, event_seq=0, t_valid_start=1.0, target_fact_id="occ1"),
        TemporalEvent("ev_ass2", EventType.ASSERT, t_knowledge=0, event_seq=1, t_valid_start=1.0, target_fact_id="occ2"),
        TemporalEvent("ev_ass3", EventType.ASSERT, t_knowledge=2, event_seq=0, t_valid_start=3.0, target_fact_id="occ3"),
    ]

    # Enumerate all subsequences of mutations of length 1 and 2
    for r in [1, 2]:
        for mutation_seq in itertools.permutations(event_pool, r):
            raw_events = base_asserts + list(mutation_seq)
            # Re-index event_seq cleanly per t_knowledge to respect transaction uniqueness
            events_by_tk: dict[int, list[TemporalEvent]] = {}
            for ev in raw_events:
                events_by_tk.setdefault(ev.t_knowledge, []).append(ev)

            all_events: list[TemporalEvent] = []
            for tk in sorted(events_by_tk.keys()):
                for seq_idx, ev in enumerate(events_by_tk[tk]):
                    all_events.append(TemporalEvent(
                        event_id=ev.event_id,
                        event_type=ev.event_type,
                        t_knowledge=ev.t_knowledge,
                        event_seq=seq_idx,
                        t_valid_start=ev.t_valid_start,
                        t_valid_end=ev.t_valid_end,
                        target_fact_id=ev.target_fact_id,
                        secondary_fact_id=ev.secondary_fact_id,
                        payload=ev.payload,
                    ))

            engine = BitemporalEngine(cautious_conflicts=True)
            for f in facts:
                engine.register_fact(f)
            for rule in rules:
                engine.register_rule(rule)
            for ev in all_events:
                engine.record_event(ev)

            interpreter = StandaloneReferenceInterpreter(facts, rules, all_events)
            query = ("Goal", "status", "OK")

            for tv in [0.5, 2.5, 3.5, 4.5, 6.0]:
                for tk in [0, 1, 2, 3, 4]:
                    eng_supp = engine.compute_temporal_support(query, t_v=tv, t_k=tk)
                    ref_supp = interpreter.compute_support(query, t_v=tv, t_k=tk)
                    assert eng_supp == ref_supp, (
                        f"Mismatch on permutation {mutation_seq} at tv={tv}, tk={tk}: "
                        f"Engine={eng_supp} vs Ref={ref_supp}"
                    )
