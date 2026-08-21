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
    # Independent
    assert compute_cut_set_size({frozenset(["R1"]), frozenset(["R2"])}) == 2
    # Shared premise
    assert compute_cut_set_size({frozenset(["R1", "R2"]), frozenset(["R1", "R3"])}) == 1


def test_bitemporal_valid_vs_knowledge_time_and_delayed_report():
    """Verify separation of Valid Time (world) and Knowledge Time (agent ledger)."""
    engine = BitemporalEngine()

    # Register fact template
    f_residence = BitemporalFact("f_res", "Alice", "lives_in", "Chicago", roots=frozenset(["R_ALICE"]))
    engine.register_fact(f_residence)

    # Scenario: Alice moved to Chicago at t_v=2.0, but the agent learned this at transaction time t_k=5.
    ev_assert = TemporalEvent(
        event_id="ev_assert_delayed",
        event_type=EventType.ASSERT,
        t_knowledge=5,
        t_valid_start=2.0,
        t_valid_end=10.0,
        target_fact_id="f_res",
    )
    engine.record_event(ev_assert)

    # At t_k=4 (before agent learned): fact was not believed to be valid at any t_v
    assert engine.is_fact_valid("f_res", t_v=3.0, t_k=4) is False

    # At t_k=5 (after agent learned): fact is recognized as valid for t_v in [2.0, 10.0)
    assert engine.is_fact_valid("f_res", t_v=1.0, t_k=5) is False
    assert engine.is_fact_valid("f_res", t_v=2.0, t_k=5) is True
    assert engine.is_fact_valid("f_res", t_v=5.0, t_k=5) is True
    assert engine.is_fact_valid("f_res", t_v=10.0, t_k=5) is False


def test_bitemporal_supersession_non_destructive_survival():
    """Verify that superseding one branch in an alternative support family preserves entitlement."""
    engine = BitemporalEngine()

    # Facts: Alice has Badge B1 (valid for SecA) and Pass P2 (valid for SecA)
    f1 = BitemporalFact("f_b1", "Alice", "has_badge", "B1", roots=frozenset(["R1"]))
    f2 = BitemporalFact("f_b1_sec", "B1", "valid_for", "SecA", roots=frozenset(["R1"]))
    f3 = BitemporalFact("f_p2", "Alice", "has_pass", "P2", roots=frozenset(["R2"]))
    f4 = BitemporalFact("f_p2_sec", "P2", "valid_for", "SecA", roots=frozenset(["R2"]))
    f5 = BitemporalFact("f_b3", "Alice", "has_badge", "B3", roots=frozenset(["R3"]))  # Superseding badge

    for f in [f1, f2, f3, f4, f5]:
        engine.register_fact(f)

    # Assert base facts at t_k=0, valid from t_v=0.0 to inf
    for fid in ["f_b1", "f_b1_sec", "f_p2", "f_p2_sec"]:
        engine.record_event(TemporalEvent(f"ev_ass_{fid}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=fid))

    # Rules
    r1 = BitemporalRule("r_badge", ("Alice", "access_to", "SecA"), (("Alice", "has_badge", "B1"), ("B1", "valid_for", "SecA")))
    r2 = BitemporalRule("r_pass", ("Alice", "access_to", "SecA"), (("Alice", "has_pass", "P2"), ("P2", "valid_for", "SecA")))
    engine.register_rule(r1)
    engine.register_rule(r2)

    query = ("Alice", "access_to", "SecA")

    # At t_k=0, t_v=1.0: both paths entitled
    init_l = engine.compute_temporal_lineage(query, t_v=1.0, t_k=0)
    assert len(init_l) == 2
    why_init = engine.why_t(query, t_v=1.0, t_k=0, init_lineage_sets=init_l)
    assert why_init["is_entitled"] is True
    assert why_init["authority_score"] == 1.0

    # At t_k=2: At valid time t_v=3.0, Badge B3 supersedes Badge B1
    engine.record_event(TemporalEvent("ev_ass_b3", EventType.ASSERT, t_knowledge=2, t_valid_start=3.0, target_fact_id="f_b3"))
    engine.record_event(TemporalEvent("ev_sup", EventType.SUPERSEDES, t_knowledge=2, t_valid_start=3.0, target_fact_id="f_b3", secondary_fact_id="f_b1"))

    # Check validity of f_b1 across valid time at t_k=2
    assert engine.is_fact_valid("f_b1", t_v=2.0, t_k=2) is True
    assert engine.is_fact_valid("f_b1", t_v=3.0, t_k=2) is False

    # Check query at t_v=4.0, t_k=2: Non-destructive survival via Pass P2!
    why_post = engine.why_t(query, t_v=4.0, t_k=2, init_lineage_sets=init_l)
    assert why_post["is_entitled"] is True
    assert len(why_post["support_sets_S_t"]) == 1
    assert why_post["support_sets_S_t"] == [["f_p2", "f_p2_sec"]]
    assert why_post["authority_score"] == 0.5  # Degraded authority


def test_multi_pair_conflict_isolation_and_partial_resolution():
    """Verify that resolving conflict pair {A, B} does not erroneously clear conflict {A, C}."""
    engine = BitemporalEngine(cautious_conflicts=True)

    fa = BitemporalFact("f_a", "Alice", "city", "KansasCity", roots=frozenset(["R1"]))
    fb = BitemporalFact("f_b", "Alice", "city", "Chicago", roots=frozenset(["R2"]))
    fc = BitemporalFact("f_c", "Alice", "city", "Seattle", roots=frozenset(["R3"]))
    for f in [fa, fb, fc]:
        engine.register_fact(f)
        engine.record_event(TemporalEvent(f"ev_ass_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    # At t_k=1: Conflict A vs B and Conflict A vs C recorded
    engine.record_event(TemporalEvent("ev_conf_ab", EventType.CONTRADICTS, t_knowledge=1, target_fact_id="f_a", secondary_fact_id="f_b"))
    engine.record_event(TemporalEvent("ev_conf_ac", EventType.CONTRADICTS, t_knowledge=1, target_fact_id="f_a", secondary_fact_id="f_c"))

    # In cautious mode at t_k=1: all three facts in conflict
    assert engine.is_fact_valid("f_a", t_v=0.0, t_k=1) is False
    assert engine.is_fact_valid("f_b", t_v=0.0, t_k=1) is False
    assert engine.is_fact_valid("f_c", t_v=0.0, t_k=1) is False

    conflicts_k1 = engine.audit_conflicts(t_k=1)
    assert len(conflicts_k1) == 2

    # At t_k=2: Resolve conflict A vs B (determining B is false / retracted)
    engine.record_event(TemporalEvent("ev_res_ab", EventType.RESOLVE_CONFLICT, t_knowledge=2, target_fact_id="f_a", secondary_fact_id="f_b"))
    engine.record_event(TemporalEvent("ev_ret_b", EventType.RETRACT, t_knowledge=2, t_valid_start=0.0, target_fact_id="f_b"))

    # f_b is retracted
    assert engine.is_fact_valid("f_b", t_v=0.0, t_k=2) is False

    # CRITICAL INVARIANT: f_a must STILL be invalid because conflict {f_a, f_c} remains active!
    assert engine.is_fact_valid("f_a", t_v=0.0, t_k=2) is False
    assert engine.is_fact_valid("f_c", t_v=0.0, t_k=2) is False

    conflicts_k2 = engine.audit_conflicts(t_k=2)
    assert len(conflicts_k2) == 1
    assert conflicts_k2[0] == {"fact_a": "f_a", "fact_b": "f_c"}

    # At t_k=3: Resolve conflict A vs C (confirming f_a)
    engine.record_event(TemporalEvent("ev_res_ac", EventType.RESOLVE_CONFLICT, t_knowledge=3, target_fact_id="f_a", secondary_fact_id="f_c"))
    engine.record_event(TemporalEvent("ev_ret_c", EventType.RETRACT, t_knowledge=3, t_valid_start=0.0, target_fact_id="f_c"))

    # Now f_a is valid!
    assert engine.is_fact_valid("f_a", t_v=0.0, t_k=3) is True
    assert len(engine.audit_conflicts(t_k=3)) == 0


def test_automatic_reverse_dependency_then_what():
    """Verify then_what_t discovers downstream derived impact without candidate lists."""
    engine = BitemporalEngine()

    f1 = BitemporalFact("f1", "SensorA", "reading", "HIGH", roots=frozenset(["R1"]))
    f2 = BitemporalFact("f2", "SensorB", "reading", "HIGH", roots=frozenset(["R2"]))
    for f in [f1, f2]:
        engine.register_fact(f)
        engine.record_event(TemporalEvent(f"ev_ass_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    r_alarm = BitemporalRule("r_alarm", ("Plant", "alarm", "ACTIVE"), (("SensorA", "reading", "HIGH"),))
    r_shutdown = BitemporalRule("r_shutdown", ("Plant", "emergency", "SHUTDOWN"), (("SensorA", "reading", "HIGH"), ("SensorB", "reading", "HIGH")))
    engine.register_rule(r_alarm)
    engine.register_rule(r_shutdown)

    # Invalidate SensorA via retraction at t_v=1.0, t_k=1
    ev_retract = TemporalEvent("ev_ret_s1", EventType.RETRACT, t_knowledge=1, t_valid_start=1.0, target_fact_id="f1")

    # then_what_t automatically evaluates all derived propositions in the rule graph
    impact = engine.then_what_t(ev_retract, t_v=1.0, t_k=0)
    assert impact["impacted_count"] >= 2
    propositions = {p["query"] for p in impact["impacted_propositions"]}
    assert ("Plant", "alarm", "ACTIVE") in propositions
    assert ("Plant", "emergency", "SHUTDOWN") in propositions
