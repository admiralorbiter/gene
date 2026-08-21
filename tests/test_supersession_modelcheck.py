"""Exhaustive Model-Checker: Cross-checks BitemporalEngine against a slow reference oracle."""

import random
from typing import Any
import pytest
from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    BitemporalRule,
    EventType,
    TemporalEvent,
    compute_antichain,
    compute_cut_set_size,
)


class BruteForceReferenceOracle:
    """Slow, unoptimized, brute-force ground-truth reference interpreter."""

    def __init__(self, facts: list[BitemporalFact], rules: list[BitemporalRule], events: list[TemporalEvent]):
        self.facts = {f.fact_id: f for f in facts}
        self.rules = list(rules)
        self.events = list(events)

    def get_active_facts(self, t_v: float, t_k: int) -> set[str]:
        """Brute-force check fact validity at (t_v, t_k)."""
        valid_ids: set[str] = set()
        for fid, f in self.facts.items():
            # Check assertions up to t_k
            asserted_intervals: list[tuple[float, float]] = []
            for ev in self.events:
                if ev.t_knowledge <= t_k and ev.target_fact_id == fid and ev.event_type == EventType.ASSERT:
                    start = ev.t_valid_start
                    end = ev.t_valid_end if ev.t_valid_end is not None else float("inf")
                    asserted_intervals.append((start, end))

            if not asserted_intervals:
                continue

            # Apply retractions, supersessions, expirations
            effective: list[tuple[float, float]] = []
            for (s, e) in asserted_intervals:
                cur_s, cur_e = s, e
                for ev in self.events:
                    if ev.t_knowledge <= t_k:
                        if ev.event_type == EventType.RETRACT and ev.target_fact_id == fid:
                            cur_e = min(cur_e, ev.t_valid_start)
                        if ev.event_type == EventType.SUPERSEDES and ev.secondary_fact_id == fid:
                            cur_e = min(cur_e, ev.t_valid_start)
                        if ev.event_type == EventType.EXPIRES and ev.target_fact_id == fid:
                            cur_e = min(cur_e, ev.t_valid_start)
                if cur_s <= t_v < cur_e:
                    effective.append((cur_s, cur_e))

            if not effective:
                continue

            # Conflicts
            conflicts: set[frozenset[str]] = set()
            for ev in self.events:
                if ev.t_knowledge <= t_k:
                    if ev.event_type == EventType.CONTRADICTS and ev.secondary_fact_id:
                        conflicts.add(frozenset([ev.target_fact_id, ev.secondary_fact_id]))
                    if ev.event_type == EventType.RESOLVE_CONFLICT and ev.secondary_fact_id:
                        conflicts.discard(frozenset([ev.target_fact_id, ev.secondary_fact_id]))

            if any(fid in p for p in conflicts):
                continue

            valid_ids.add(fid)

        return valid_ids

    def derives(self, fact_subset: set[str], query: tuple[str, str, str]) -> bool:
        """Exhaustive forward deduction test on subset of facts."""
        known_triples = {self.facts[fid].triple for fid in fact_subset}
        changed = True
        while changed:
            changed = False
            for r in self.rules:
                if r.head not in known_triples:
                    if all(b in known_triples for b in r.body):
                        known_triples.add(r.head)
                        changed = True
        return query in known_triples

    def compute_minimal_support(self, query: tuple[str, str, str], t_v: float, t_k: int) -> set[frozenset[str]]:
        """Exhaustive power-set search for minimal support sets."""
        active_fids = sorted(list(self.get_active_facts(t_v, t_k)))
        n = len(active_fids)
        satisfying: set[frozenset[str]] = set()

        from itertools import combinations
        for k in range(1, n + 1):
            for combo in combinations(active_fids, k):
                combo_set = set(combo)
                if self.derives(combo_set, query):
                    satisfying.add(frozenset(combo))

        # Antichain
        return compute_antichain(satisfying)


def test_model_checker_randomized_combinatorial_histories():
    """Property test: BitemporalEngine exact equivalence to BruteForceReferenceOracle across 50 random histories."""
    rng = random.Random(42)

    for run_idx in range(50):
        # 1. Generate 4 facts
        facts = [
            BitemporalFact(f"f_{i}", f"Ent_{i}", "rel", f"Val_{i}", roots=frozenset([f"R_{i % 2}"]))
            for i in range(4)
        ]

        # 2. Generate rules
        r1 = BitemporalRule("r1", ("Goal", "status", "TRUE"), (facts[0].triple, facts[1].triple))
        r2 = BitemporalRule("r2", ("Goal", "status", "TRUE"), (facts[2].triple, facts[3].triple))
        rules = [r1, r2]

        # 3. Generate random event timeline
        events: list[TemporalEvent] = []
        ev_id = 0

        # Assertions
        for f in facts:
            t_assert = rng.randint(0, 3)
            events.append(TemporalEvent(f"ev_{ev_id}", EventType.ASSERT, t_knowledge=t_assert, t_valid_start=float(t_assert), target_fact_id=f.fact_id))
            ev_id += 1

        # Random mutation events
        for _ in range(3):
            ev_type = rng.choice([EventType.RETRACT, EventType.SUPERSEDES, EventType.CONTRADICTS])
            tk = rng.randint(2, 6)
            tv = float(rng.randint(2, 6))
            target_f = rng.choice(facts).fact_id
            sec_f = rng.choice([f.fact_id for f in facts if f.fact_id != target_f])

            if ev_type == EventType.RETRACT:
                events.append(TemporalEvent(f"ev_{ev_id}", EventType.RETRACT, t_knowledge=tk, t_valid_start=tv, target_fact_id=target_f))
            elif ev_type == EventType.SUPERSEDES:
                events.append(TemporalEvent(f"ev_{ev_id}", EventType.SUPERSEDES, t_knowledge=tk, t_valid_start=tv, target_fact_id=target_f, secondary_fact_id=sec_f))
            elif ev_type == EventType.CONTRADICTS:
                events.append(TemporalEvent(f"ev_{ev_id}", EventType.CONTRADICTS, t_knowledge=tk, target_fact_id=target_f, secondary_fact_id=sec_f))
            ev_id += 1

        engine = BitemporalEngine(cautious_conflicts=True)
        for f in facts:
            engine.register_fact(f)
        for r in rules:
            engine.register_rule(r)
        for ev in events:
            engine.record_event(ev)

        oracle = BruteForceReferenceOracle(facts, rules, events)

        # Test query across grid of (t_v, t_k)
        query = ("Goal", "status", "TRUE")
        for test_tv in [0.0, 2.0, 4.0, 7.0]:
            for test_tk in [0, 2, 4, 7]:
                engine_supp = engine.compute_temporal_support(query, t_v=test_tv, t_k=test_tk)
                oracle_supp = oracle.compute_minimal_support(query, t_v=test_tv, t_k=test_tk)

                assert engine_supp == oracle_supp, (
                    f"Discrepancy at run {run_idx}, t_v={test_tv}, t_k={test_tk}: "
                    f"Engine={engine_supp} vs Oracle={oracle_supp}"
                )
