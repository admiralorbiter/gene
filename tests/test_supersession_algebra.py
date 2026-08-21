"""Unit and property tests for Temporal Supersession Algebra (Stage 6A)."""

import pytest
from gene.supersession_engine import (
    EventType,
    SupersessionEngine,
    TemporalEvent,
    TemporalFact,
    TemporalRule,
    compute_antichain,
    compute_cut_set_size,
)


def test_antichain_minimization_core():
    """Verify that strict supersets are eliminated while non-comparable sets remain."""
    s1 = frozenset(["A", "B"])
    s2 = frozenset(["A", "B", "C"])
    s3 = frozenset(["D"])
    
    input_sets = {s1, s2, s3}
    minimized = compute_antichain(input_sets)
    assert minimized == {s1, s3}
    assert s2 not in minimized


def test_cut_set_size_computation():
    """Verify hitting set / cut set computation across multi-path geometries."""
    # Independent 2-path
    s_ind = {frozenset(["R1"]), frozenset(["R2"])}
    assert compute_cut_set_size(s_ind) == 2

    # Shared premise
    s_shp = {frozenset(["R1", "R2"]), frozenset(["R1", "R3"])}
    assert compute_cut_set_size(s_shp) == 1  # {R1} hits both


def test_temporal_supersession_non_destructive_survival():
    """Verify that superseding one branch in an alternative support family preserves entitlement."""
    engine = SupersessionEngine()

    # Initial state at t=0: Alice has two independent ways to be authorized:
    # Path 1: (Alice, has_badge, B1) & (B1, valid_for, SecA)
    # Path 2: (Alice, has_pass, P2) & (P2, valid_for, SecA)
    f1 = TemporalFact("f_b1", "Alice", "has_badge", "B1", asserted_at=0, roots=frozenset(["R1"]))
    f2 = TemporalFact("f_b1_sec", "B1", "valid_for", "SecA", asserted_at=0, roots=frozenset(["R1"]))
    f3 = TemporalFact("f_p2", "Alice", "has_pass", "P2", asserted_at=0, roots=frozenset(["R2"]))
    f4 = TemporalFact("f_p2_sec", "P2", "valid_for", "SecA", asserted_at=0, roots=frozenset(["R2"]))

    engine.add_fact(f1)
    engine.add_fact(f2)
    engine.add_fact(f3)
    engine.add_fact(f4)

    # Rule 1: Badge implies access
    r1 = TemporalRule("r_badge", ("Alice", "access_to", "SecA"), (("Alice", "has_badge", "B1"), ("B1", "valid_for", "SecA")))
    # Rule 2: Pass implies access
    r2 = TemporalRule("r_pass", ("Alice", "access_to", "SecA"), (("Alice", "has_pass", "P2"), ("P2", "valid_for", "SecA")))

    engine.add_rule(r1)
    engine.add_rule(r2)

    query = ("Alice", "access_to", "SecA")

    # At t=0: both paths active
    why_0 = engine.why_t(query, t=0)
    assert why_0["is_entitled"] is True
    assert len(why_0["support_sets_S_t"]) == 2
    assert why_0["lineage_cut_set_kappa_L"] == 2
    init_l = engine.compute_temporal_lineage(query, t=0)

    # At t=3: Badge B1 is superseded by Badge B3 (which is NOT valid for SecA)
    f5 = TemporalFact("f_b3", "Alice", "has_badge", "B3", asserted_at=3, roots=frozenset(["R3"]))
    engine.add_fact(f5)
    ev_sup = TemporalEvent("ev_1", EventType.SUPERSEDES, timestamp=3, target_fact_id="f_b3", secondary_fact_id="f_b1")
    engine.record_event(ev_sup)

    # At t=2: f_b1 was still valid
    assert engine.is_fact_valid("f_b1", t=2) is True
    assert len(engine.compute_temporal_support(query, t=2)) == 2

    # At t=3: f_b1 is superseded and inactive, but f_p2 path survives!
    assert engine.is_fact_valid("f_b1", t=3) is False
    why_3 = engine.why_t(query, t=3, init_lineage_sets=init_l)
    assert why_3["is_entitled"] is True  # Non-destructive survival!
    assert len(why_3["support_sets_S_t"]) == 1
    assert why_3["support_sets_S_t"] == [["f_p2", "f_p2_sec"]]
    # Authority degraded from 1.0 to 0.5 * (1/2 + 1/2) = 0.5
    assert why_3["authority_score"] == 0.5


def test_temporal_expiration_lifecycle():
    """Verify that facts with expiration timestamps automatically deactivate at expiry."""
    engine = SupersessionEngine()

    f_temp = TemporalFact("f_temp", "Bob", "clearance", "TEMP_GUEST", asserted_at=1, expires_at=5, roots=frozenset(["R_BOB"]))
    engine.add_fact(f_temp)

    # Valid in interval [1, 5)
    assert engine.is_fact_valid("f_temp", t=0) is False
    assert engine.is_fact_valid("f_temp", t=1) is True
    assert engine.is_fact_valid("f_temp", t=4) is True
    assert engine.is_fact_valid("f_temp", t=5) is False
    assert engine.is_fact_valid("f_temp", t=10) is False


def test_what_if_and_then_what_queries():
    """Verify counterfactual simulation and downstream impact prediction."""
    engine = SupersessionEngine()

    f1 = TemporalFact("f1", "NodeX", "status", "ONLINE", asserted_at=0, roots=frozenset(["R1"]))
    f2 = TemporalFact("f2", "NodeY", "status", "ONLINE", asserted_at=0, roots=frozenset(["R2"]))
    engine.add_fact(f1)
    engine.add_fact(f2)

    r1 = TemporalRule("r_sys", ("System", "state", "OPERATIONAL"), (("NodeX", "status", "ONLINE"),))
    r2 = TemporalRule("r_sec", ("System", "redundancy", "HIGH"), (("NodeX", "status", "ONLINE"), ("NodeY", "status", "ONLINE")))
    engine.add_rule(r1)
    engine.add_rule(r2)

    q_op = ("System", "state", "OPERATIONAL")
    q_red = ("System", "redundancy", "HIGH")

    # What if f1 is retracted?
    ev_retract = TemporalEvent("ev_hypo", EventType.RETRACT, timestamp=1, target_fact_id="f1")
    what_if = engine.what_if_t(q_op, ev_retract, t=0)
    assert what_if["prior_entitled"] is True
    assert what_if["hypothetical_entitled"] is False

    # Then what across all system queries?
    then_what = engine.then_what_t(ev_retract, [q_op, q_red], t=0)
    assert then_what["impacted_count"] == 2
    propositions = {p["query"] for p in then_what["impacted_propositions"]}
    assert propositions == {q_op, q_red}


def test_cautious_conflict_isolation():
    """Verify that contradiction events isolate conflicting premises."""
    engine = SupersessionEngine(cautious_conflicts=True)

    f_kc = TemporalFact("f_kc", "Alice", "city", "KansasCity", asserted_at=0, roots=frozenset(["R1"]))
    f_chi = TemporalFact("f_chi", "Alice", "city", "Chicago", asserted_at=2, roots=frozenset(["R2"]))
    f_job = TemporalFact("f_job", "Alice", "role", "Engineer", asserted_at=0, roots=frozenset(["R3"]))

    engine.add_fact(f_kc)
    engine.add_fact(f_chi)
    engine.add_fact(f_job)

    # Record contradiction between cities at t=2
    ev_conflict = TemporalEvent("ev_conf", EventType.CONTRADICTS, timestamp=2, target_fact_id="f_kc", secondary_fact_id="f_chi")
    engine.record_event(ev_conflict)

    # In cautious mode at t=2, both conflicting facts are inactive
    assert engine.is_fact_valid("f_kc", t=1) is True
    assert engine.is_fact_valid("f_kc", t=2) is False
    assert engine.is_fact_valid("f_chi", t=2) is False

    # Orthogonal fact remains valid!
    assert engine.is_fact_valid("f_job", t=2) is True

    # Audit conflicts
    conflicts = engine.audit_conflicts(t=2)
    assert len(conflicts) == 1
    assert conflicts[0]["fact_a"] == "f_kc"
    assert conflicts[0]["fact_b"] == "f_chi"

    # Resolve conflict in favor of Chicago at t=4
    ev_resolve = TemporalEvent("ev_res", EventType.RESOLVE_CONFLICT, timestamp=4, target_fact_id="f_chi", secondary_fact_id="f_kc")
    engine.record_event(ev_resolve)
    ev_sup = TemporalEvent("ev_sup", EventType.SUPERSEDES, timestamp=4, target_fact_id="f_chi", secondary_fact_id="f_kc")
    engine.record_event(ev_sup)

    assert engine.is_fact_valid("f_chi", t=4) is True
    assert engine.is_fact_valid("f_kc", t=4) is False
    assert len(engine.audit_conflicts(t=4)) == 0


def test_timeline_chronological_immutability():
    """Verify that the engine produces a complete, historical timeline of entitlement."""
    engine = SupersessionEngine()

    f = TemporalFact("f_test", "Server", "status", "RUNNING", asserted_at=1, expires_at=4, roots=frozenset(["R_SRV"]))
    engine.add_fact(f)

    timeline = engine.timeline(("Server", "status", "RUNNING"), max_t=5)
    assert len(timeline) == 6
    assert timeline[0]["entitled"] is False  # t=0 (before assert)
    assert timeline[1]["entitled"] is True   # t=1
    assert timeline[2]["entitled"] is True   # t=2
    assert timeline[3]["entitled"] is True   # t=3
    assert timeline[4]["entitled"] is False  # t=4 (expired)
    assert timeline[5]["entitled"] is False  # t=5
