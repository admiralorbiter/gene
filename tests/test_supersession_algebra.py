"""Comprehensive unit and property tests for Bitemporal Supersession Engine (Stage 6A-v2 Frozen)."""

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


def test_occurrence_node_reassertion_and_independent_intervals():
    """Verify occurrence-node separation: distinct occurrences of the same semantic proposition."""
    engine = BitemporalEngine()

    # Two distinct occurrence nodes realizing the same semantic claim (Alice, status, SUBSCRIBED)
    occ1 = BitemporalFact("occ_sub_1", "Alice", "status", "SUBSCRIBED", roots=frozenset(["R1"]))
    occ2 = BitemporalFact("occ_sub_2", "Alice", "status", "SUBSCRIBED", roots=frozenset(["R2"]))
    engine.register_fact(occ1)
    engine.register_fact(occ2)

    # Occurrence 1: asserted at t_k=0, valid in [0.0, inf)
    engine.record_event(TemporalEvent("ev_ass1", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id="occ_sub_1"))

    # Occurrence 1 retracted at t_v=5.0, learned at t_k=1
    engine.record_event(TemporalEvent("ev_ret1", EventType.RETRACT, t_knowledge=1, t_valid_start=5.0, target_fact_id="occ_sub_1"))

    # Occurrence 2 asserted at t_k=2, valid in [10.0, inf)
    engine.record_event(TemporalEvent("ev_ass2", EventType.ASSERT, t_knowledge=2, t_valid_start=10.0, target_fact_id="occ_sub_2"))

    # Query semantic claim at t_k=2
    claim = ("Alice", "status", "SUBSCRIBED")
    supp_t2 = engine.compute_temporal_support(claim, t_v=2.0, t_k=2)
    assert supp_t2 == {frozenset(["occ_sub_1"])}  # First occurrence active

    supp_t7 = engine.compute_temporal_support(claim, t_v=7.0, t_k=2)
    assert supp_t7 == set()  # Inactive between occurrences

    supp_t12 = engine.compute_temporal_support(claim, t_v=12.0, t_k=2)
    assert supp_t12 == {frozenset(["occ_sub_2"])}  # Second occurrence active


def test_supersedes_causal_replacement_and_separate_assert():
    """Verify that SUPERSEDES truncates the old occurrence while the new occurrence is separately asserted."""
    engine = BitemporalEngine()

    occ_old = BitemporalFact("occ_badge_b1", "Alice", "has_badge", "B1", roots=frozenset(["R1"]))
    occ_new = BitemporalFact("occ_badge_b2", "Alice", "has_badge", "B2", roots=frozenset(["R2"]))
    engine.register_fact(occ_old)
    engine.register_fact(occ_new)

    engine.record_event(TemporalEvent("ev_ass_old", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id="occ_badge_b1"))

    # At t_k=2, valid from t_v=5.0: New badge B2 asserted and supersedes old badge B1
    engine.record_event(TemporalEvent("ev_ass_new", EventType.ASSERT, t_knowledge=2, event_seq=0, t_valid_start=5.0, target_fact_id="occ_badge_b2"))
    engine.record_event(TemporalEvent("ev_sup", EventType.SUPERSEDES, t_knowledge=2, event_seq=1, t_valid_start=5.0, target_fact_id="occ_badge_b2", secondary_fact_id="occ_badge_b1"))

    # Prior to t_v=5.0 at t_k=2: old badge is valid, new badge is not yet valid
    assert engine.is_fact_valid("occ_badge_b1", t_v=4.0, t_k=2) is True
    assert engine.is_fact_valid("occ_badge_b2", t_v=4.0, t_k=2) is False

    # At and after t_v=5.0 at t_k=2: old badge is superseded, new badge is active
    assert engine.is_fact_valid("occ_badge_b1", t_v=5.0, t_k=2) is False
    assert engine.is_fact_valid("occ_badge_b2", t_v=5.0, t_k=2) is True


def test_same_tk_transaction_sequencing():
    """Verify event_seq preserves deterministic execution within the same transaction timestamp t_k."""
    engine = BitemporalEngine()

    f = BitemporalFact("occ_test", "Node", "status", "ONLINE", roots=frozenset(["R1"]))
    engine.register_fact(f)

    # In the same transaction t_k=1: assert then immediately retract
    ev_ass = TemporalEvent("ev_a", EventType.ASSERT, t_knowledge=1, event_seq=0, t_valid_start=0.0, target_fact_id="occ_test")
    ev_ret = TemporalEvent("ev_b", EventType.RETRACT, t_knowledge=1, event_seq=1, t_valid_start=0.0, target_fact_id="occ_test")
    
    # Record in reverse order to ensure event_seq sorting controls execution
    engine.record_event(ev_ret)
    engine.record_event(ev_ass)

    assert engine.is_fact_valid("occ_test", t_v=0.0, t_k=1) is False


def test_bitemporal_conflict_interval_isolation():
    """Verify that a conflict active in interval [5.0, 8.0) does NOT invalidate history at t_v=2.0."""
    engine = BitemporalEngine(cautious_conflicts=True)

    fa = BitemporalFact("fa", "Alice", "city", "KansasCity", roots=frozenset(["R1"]))
    fb = BitemporalFact("fb", "Alice", "city", "Chicago", roots=frozenset(["R2"]))
    for i, f in enumerate([fa, fb]):
        engine.register_fact(f)
        engine.record_event(TemporalEvent(f"ev_ass_{f.fact_id}", EventType.ASSERT, t_knowledge=0, event_seq=i, t_valid_start=0.0, target_fact_id=f.fact_id))

    engine.record_event(TemporalEvent(
        event_id="ev_conf_window",
        event_type=EventType.CONTRADICTS,
        t_knowledge=1,
        event_seq=0,
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


def test_deep_then_what_geometry_change_detection():
    """Verify THEN_WHAT detects SUPPORT_GEOMETRY_CHANGED even when entitlement and authority are unchanged."""
    engine = BitemporalEngine()

    f1 = BitemporalFact("f1", "X", "p", "1", roots=frozenset(["R1"]))
    f2 = BitemporalFact("f2", "X", "p", "2", roots=frozenset(["R2"]))
    f3 = BitemporalFact("f3", "X", "p", "3", roots=frozenset(["R1"]))
    f4 = BitemporalFact("f4", "X", "p", "4", roots=frozenset(["R2"]))
    for i, f in enumerate([f1, f2, f3, f4]):
        engine.register_fact(f)
        engine.record_event(TemporalEvent(f"ev_ass_{f.fact_id}", EventType.ASSERT, t_knowledge=0, event_seq=i, t_valid_start=0.0, target_fact_id=f.fact_id))

    goal = ("Goal", "status", "TRUE")
    r1 = BitemporalRule("r1", goal, (f1.triple, f2.triple))
    r2 = BitemporalRule("r2", goal, (f3.triple, f4.triple))
    engine.register_rule(r1)
    engine.register_rule(r2)

    ev_ret_f3 = TemporalEvent("ev_ret_f3", EventType.RETRACT, t_knowledge=1, event_seq=0, t_valid_start=0.0, target_fact_id="f3")

    impact = engine.then_what_t(ev_ret_f3, t_v=0.0, t_k=0)
    assert impact["impacted_count"] >= 1

    goal_trans = next(p for p in impact["impacted_propositions"] if p["query"] == goal)
    assert goal_trans["prior_entitled"] is True
    assert goal_trans["post_entitled"] is True
    assert goal_trans["transition"] == "SUPPORT_GEOMETRY_CHANGED"


def test_fail_closed_duplicate_identifiers_and_sequences():
    """Verify that duplicate fact_ids, event_ids, and (t_k, event_seq) collide and fail closed."""
    engine = BitemporalEngine()

    f1 = BitemporalFact("occ_dup", "A", "p", "1")
    engine.register_fact(f1)
    with pytest.raises(ValueError, match="Duplicate OccurrenceNode"):
        engine.register_fact(f1)

    ev1 = TemporalEvent("ev_dup", EventType.ASSERT, t_knowledge=0, event_seq=0, target_fact_id="occ_dup")
    engine.record_event(ev1)

    ev2 = TemporalEvent("ev_dup", EventType.RETRACT, t_knowledge=1, event_seq=0, target_fact_id="occ_dup")
    with pytest.raises(ValueError, match="Duplicate event_id"):
        engine.record_event(ev2)

    ev3 = TemporalEvent("ev_diff_id", EventType.RETRACT, t_knowledge=0, event_seq=0, target_fact_id="occ_dup")
    with pytest.raises(ValueError, match="Duplicate transaction sequence"):
        engine.record_event(ev3)

