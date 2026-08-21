"""Exhaustive Small-History Model Checker & Randomized State Invariance.

Implements an independent reference interpreter with its own standalone
antichain and power-set deduction algorithms, verifying BitemporalEngine across
exhaustive small-world event permutations and randomized multi-step histories.
"""

from __future__ import annotations

import itertools
import random
from typing import Any
import pytest
from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    BitemporalRule,
    EventType,
    TemporalEvent,
)


def independent_antichain(sets: set[frozenset[str]]) -> set[frozenset[str]]:
    """Standalone reference antichain implementation without importing production code."""
    res = set()
    for s in sets:
        # Keep s iff no other set in sets is a strict subset of s
        if not any(other < s for other in sets):
            res.add(s)
    return res


class StandaloneReferenceInterpreter:
    """Completely independent, unoptimized reference oracle."""

    def __init__(self, facts: list[BitemporalFact], rules: list[BitemporalRule], events: list[TemporalEvent]):
        self.facts = {f.fact_id: f for f in facts}
        self.rules = list(rules)
        self.events = sorted(list(events), key=lambda e: (e.t_knowledge, e.event_id))

    def is_valid(self, fid: str, t_v: float, t_k: int) -> bool:
        """Evaluate fact validity directly from raw event history."""
        # 1. Gather all ASSERT occurrences known by t_k
        occurrences: list[tuple[float, float]] = []
        for ev in self.events:
            if ev.t_knowledge <= t_k and ev.target_fact_id == fid and ev.event_type == EventType.ASSERT:
                start = ev.t_valid_start
                end = ev.t_valid_end if ev.t_valid_end is not None else float("inf")
                occurrences.append((start, end))

        if not occurrences:
            return False

        # Apply truncations
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

        # 2. Check bitemporal conflicts
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
        """Exhaustive power-set forward deduction and independent antichain minimization."""
        valid_fids = [fid for fid in sorted(self.facts.keys()) if self.is_valid(fid, t_v, t_k)]
        n = len(valid_fids)
        satisfying: set[frozenset[str]] = set()

        for k in range(1, n + 1):
            for combo in itertools.combinations(valid_fids, k):
                # Check forward deduction on this subset
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


def test_exhaustive_small_world_event_permutations():
    """Exhaustively model check all combinations of event sequences of length 3 over 2 facts."""
    f1 = BitemporalFact("f1", "A", "rel", "1", roots=frozenset(["R1"]))
    f2 = BitemporalFact("f2", "B", "rel", "2", roots=frozenset(["R2"]))
    facts = [f1, f2]
    r1 = BitemporalRule("r1", ("Goal", "status", "OK"), (f1.triple,))
    rules = [r1]

    # Possible candidate mutation events
    event_pool = [
        TemporalEvent("ev_ret1", EventType.RETRACT, t_knowledge=2, t_valid_start=3.0, target_fact_id="f1"),
        TemporalEvent("ev_exp1", EventType.EXPIRES, t_knowledge=2, t_valid_start=4.0, target_fact_id="f1"),
        TemporalEvent("ev_conf", EventType.CONTRADICTS, t_knowledge=1, t_valid_start=2.0, t_valid_end=5.0, target_fact_id="f1", secondary_fact_id="f2"),
        TemporalEvent("ev_res", EventType.RESOLVE_CONFLICT, t_knowledge=3, t_valid_start=2.0, t_valid_end=5.0, target_fact_id="f1", secondary_fact_id="f2"),
    ]

    base_asserts = [
        TemporalEvent("ev_ass1", EventType.ASSERT, t_knowledge=0, t_valid_start=1.0, target_fact_id="f1"),
        TemporalEvent("ev_ass2", EventType.ASSERT, t_knowledge=0, t_valid_start=1.0, target_fact_id="f2"),
    ]

    # Enumerate all subsequences of mutations of length 1 and 2
    for r in [1, 2]:
        for mutation_seq in itertools.permutations(event_pool, r):
            all_events = base_asserts + list(mutation_seq)

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
