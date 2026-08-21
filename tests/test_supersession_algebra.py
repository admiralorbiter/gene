"""Comprehensive unit and property tests for Bitemporal Supersession Engine (Stage 6A-v2)."""

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


def test_antichain_minimization_core():
    """Verify strict subset elimination across arbitrary sets."""
    s1 = frozenset(["A", "B"])
    s2 = frozenset(["A", "B", "C"])
    s3 = frozenset(["D"])
    
    input_sets = {s1, s2, s3}
    minimized = compute_antichain(input_sets)
    assert minimized == {s1, s3}


def test_cut_set_size_hitting_set():
    """Verify hitting set calculation across independent and shared topologies."""
    assert compute_cut_set_size({frozenset(["R1"]), frozenset(["R2"])}) == 2
    assert compute_cut_set_size({frozenset(["R1", "R2"]), frozenset(["R1", "R3"])}) == 1


def test_reassertion_and_occurrence_intervals():
    """Verify that a fact can be retracted in one interval and reasserted in a later interval."""
    engine = BitemporalEngine()

    f = BitemporalFact("f_sub", "Alice", "status", "SUBSCRIBED", roots=frozenset(["R1"]))
    engine.register_fact(f)

    # Initial subscription episode: valid in [0.0, inf), learned at t_k=0
    engine.record_event(TemporalEvent("ev_ass1", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id="f_sub", occurrence_id="occ_1"))

    # Cancellation at t_v=5.0, learned at t_k=1
    engine.record_event(TemporalEvent("ev_ret1", EventType.RETRACT, t_knowledge=1, t_valid_start=5.0, target_fact_id="f_sub"))

    # Resubscription at t_v=10.0, learned at t_k=2
    engine.record_event(TemporalEvent("ev_ass2", EventType.ASSERT, t_knowledge=2, t_valid_start=10.0, target_fact_id="f_sub", occurrence_id="occ_2"))

    # Query at t_k=2 across the valid-time spectrum
    assert engine.is_fact_valid("f_sub", t_v=2.0, t_k=2) is True   # Inside first episode [0, 5)
    assert engine.is_fact_valid("f_sub", t_v=5.0, t_k=2) is False  # Retracted boundary
    assert engine.is_fact_valid("f_sub", t_v=7.0, t_k=2) is False  # Lapsed interval [5, 10)
    assert engine.is_fact_valid("f_sub", t_v=10.0, t_k=2) is True  # Resubscription episode [10, inf)
    assert engine.is_fact_valid("f_sub", t_v=15.0, t_k=2) is True  # Active resubscription


def test_bitemporal_conflict_interval_isolation():
    """Verify that a conflict active in interval [5.0, 8.0) does NOT invalidate history at t_v=2.0."""
    engine = BitemporalEngine(cautious_conflicts=True)

    fa = BitemporalFact("fa", "Alice", "city", "KansasCity", roots=frozenset(["R1"]))
    fb = BitemporalFact("fb", "Alice", "city", "Chicago", roots=frozenset(["R2"]))
    for f in [fa, fb]:
        engine.register_fact(f)
        engine.record_event(TemporalEvent(f"ev_ass_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    # Conflict between KansasCity and Chicago specifically during disputed transition window [5.0, 8.0)
    engine.record_event(TemporalEvent(
        event_id="ev_conf_window",
        event_type=EventType.CONTRADICTS,
        t_knowledge=1,
        t_valid_start=5.0,
        t_valid_end=8.0,
        target_fact_id="fa",
        secondary_fact_id="fb",
    ))

    # At t_k=1: Prior history t_v=2.0 is NOT disputed
    assert engine.is_fact_valid("fa", t_v=2.0, t_k=1) is True
    assert engine.is_fact_valid("fb", t_v=2.0, t_k=1) is True

    # Inside disputed interval [5.0, 8.0): Both are disqualified under cautious mode
    assert engine.is_fact_valid("fa", t_v=6.0, t_k=1) is False
    assert engine.is_fact_valid("fb", t_v=6.0, t_k=1) is False

    # After disputed interval t_v=9.0: Undisputed again
    assert engine.is_fact_valid("fa", t_v=9.0, t_k=1) is True
    assert engine.is_fact_valid("fb", t_v=9.0, t_k=1) is True

    # Audit conflicts at specific valid times
    assert len(engine.audit_conflicts(t_v=2.0, t_k=1)) == 0
    assert len(engine.audit_conflicts(t_v=6.0, t_k=1)) == 1


def test_multi_pair_conflict_isolation_and_partial_resolution():
    """Verify that resolving conflict pair {A, B} preserves active conflict on {A, C}."""
    engine = BitemporalEngine(cautious_conflicts=True)

    fa = BitemporalFact("fa", "Alice", "city", "KansasCity", roots=frozenset(["R1"]))
    fb = BitemporalFact("fb", "Alice", "city", "Chicago", roots=frozenset(["R2"]))
    fc = BitemporalFact("fc", "Alice", "city", "Seattle", roots=frozenset(["R3"]))
    for f in [fa, fb, fc]:
        engine.register_fact(f)
        engine.record_event(TemporalEvent(f"ev_ass_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    # Record two independent conflict pairs at t_k=1
    engine.record_event(TemporalEvent("ev_c_ab", EventType.CONTRADICTS, t_knowledge=1, target_fact_id="fa", secondary_fact_id="fb"))
    engine.record_event(TemporalEvent("ev_c_ac", EventType.CONTRADICTS, t_knowledge=1, target_fact_id="fa", secondary_fact_id="fc"))

    # At t_k=1: all in conflict
    assert engine.is_fact_valid("fa", t_v=0.0, t_k=1) is False
    assert engine.is_fact_valid("fb", t_v=0.0, t_k=1) is False
    assert engine.is_fact_valid("fc", t_v=0.0, t_k=1) is False

    # At t_k=2: Resolve pair {fa, fb}
    engine.record_event(TemporalEvent("ev_res_ab", EventType.RESOLVE_CONFLICT, t_knowledge=2, target_fact_id="fa", secondary_fact_id="fb"))

    # fb is now resolved; fa remains in conflict with fc!
    assert engine.is_fact_valid("fb", t_v=0.0, t_k=2) is True
    assert engine.is_fact_valid("fa", t_v=0.0, t_k=2) is False
    assert engine.is_fact_valid("fc", t_v=0.0, t_k=2) is False


def test_deep_then_what_geometry_change_detection():
    """Verify THEN_WHAT detects SUPPORT_GEOMETRY_CHANGED even when entitlement and authority are unchanged."""
    engine = BitemporalEngine()

    # Two alternative proofs for Goal:
    # Proof 1: Fact 1 (root R1) + Fact 2 (root R2)
    # Proof 2: Fact 3 (root R1) + Fact 4 (root R2)
    f1 = BitemporalFact("f1", "X", "p", "1", roots=frozenset(["R1"]))
    f2 = BitemporalFact("f2", "X", "p", "2", roots=frozenset(["R2"]))
    f3 = BitemporalFact("f3", "X", "p", "3", roots=frozenset(["R1"]))
    f4 = BitemporalFact("f4", "X", "p", "4", roots=frozenset(["R2"]))
    for f in [f1, f2, f3, f4]:
        engine.register_fact(f)
        engine.record_event(TemporalEvent(f"ev_ass_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    goal = ("Goal", "status", "TRUE")
    r1 = BitemporalRule("r1", goal, (f1.triple, f2.triple))
    r2 = BitemporalRule("r2", goal, (f3.triple, f4.triple))
    engine.register_rule(r1)
    engine.register_rule(r2)

    # Initial state: S = {{f1, f2}, {f3, f4}}, S_L = {{R1, R2}}
    # Now simulate retraction of f3
    ev_ret_f3 = TemporalEvent("ev_ret_f3", EventType.RETRACT, t_knowledge=1, t_valid_start=0.0, target_fact_id="f3")

    impact = engine.then_what_t(ev_ret_f3, t_v=0.0, t_k=0)
    assert impact["impacted_count"] >= 1

    goal_trans = next(p for p in impact["impacted_propositions"] if p["query"] == goal)
    # Entitlement remains True, Lineage S_L remains {{R1, R2}}, Authority remains 1.0,
    # BUT support geometry S changed from 2 paths to 1 path!
    assert goal_trans["prior_entitled"] is True
    assert goal_trans["post_entitled"] is True
    assert goal_trans["transition"] == "SUPPORT_GEOMETRY_CHANGED"


def test_relative_vs_bounded_authority_semantics():
    """Verify that RelativeAuthority can exceed 1.0 on reinforcement while BoundedAuthority is clamped to [0, 1]."""
    engine = BitemporalEngine()

    f1 = BitemporalFact("f1", "Node", "param", "1", roots=frozenset(["R1"]))
    f2 = BitemporalFact("f2", "Node", "param", "2", roots=frozenset(["R2"]))
    for f in [f1, f2]:
        engine.register_fact(f)
        engine.record_event(TemporalEvent(f"ev_ass_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    goal = ("Node", "health", "GOOD")
    r1 = BitemporalRule("r1", goal, (f1.triple,))
    r2 = BitemporalRule("r2", goal, (f2.triple,))
    engine.register_rule(r1)
    engine.register_rule(r2)

    # Suppose baseline was a single-path lineage {{R1}}
    init_single_l = {frozenset(["R1"])}

    # At t_k=0 with both paths active: S_L = {{R1}, {R2}}
    why = engine.why_t(goal, t_v=0.0, t_k=0, init_lineage_sets=init_single_l)
    # kappa increased from 1 to 2 (ratio 2.0), paths increased from 1 to 2 (ratio 2.0) -> RelativeAuthority = 2.0
    assert why["relative_authority"] == 2.0
    # Bounded authority clamped to 1.0
    assert why["bounded_authority"] == 1.0
