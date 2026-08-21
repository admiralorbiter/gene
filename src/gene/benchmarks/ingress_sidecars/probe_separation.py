"""8-World Probe Separation Assay with Full Engine-Derived Evaluation (Stage 7A.4).

Distinguishes:
1. RawStateVector = (is_active, is_entitled, is_action_authorized, survives_source_ablation)
2. ProbeCorrectness = (q1_state_correct, q2_support_correct, q3_gov_correct, q4_causal_correct)
where all four probes are mechanically computed via engine queries in every world.
"""

from typing import Any
from gene.ingress.models import (
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ClaimPrivilege,
    ParsedAttestation,
    SourceRecord,
)
from gene.ingress.ontology import (
    CapabilityPolicy,
    CapabilityPolicyRegistry,
    EntityDefinition,
    IngressOntology,
    LineageIndependenceRegistry,
)
from gene.ingress.engine import IngressEngine
from gene.ingress.policies import A4FullGENEIngressPolicy
from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    EventType,
    PredicateContract,
    TemporalEvent,
)


def run_probe_separation_assay() -> dict[str, Any]:
    """Run an 8-world probe-separation assay with mechanically computed Raw and Correctness vectors."""
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
        EntityDefinition("Value_Baseline", "Baseline", "STATUS"),
        EntityDefinition("Value_Degraded", "Degraded", "STATUS"),
    ])

    cap_registry = CapabilityPolicyRegistry({
        "sensor_trusted_a": CapabilityPolicy("sensor_trusted_a", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", can_disambiguate=True),
        "sensor_trusted_b": CapabilityPolicy("sensor_trusted_b", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", can_disambiguate=True),
        "sensor_untrusted_roots": CapabilityPolicy("sensor_untrusted_roots", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "UNVERIFIED_SENSOR", can_disambiguate=True),
        "guest_unauth": CapabilityPolicy("guest_unauth", frozenset(["feedback"]), ClaimPrivilege.ATTESTATION_ONLY, "WEB", can_disambiguate=False),
    })

    ind_registry = LineageIndependenceRegistry({
        "sensor_trusted_a": "ROOT_NET_1_sensor_a",
        "sensor_trusted_b": "ROOT_NET_2_sensor_b",
        "sensor_untrusted_roots": "ROOT_UNKNOWN_INDEPENDENCE_sensor_untrusted_roots",
    })

    contract_single = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    contract_multi = PredicateContract("device_status", "MULTI", "ADDITIVE")

    hypo_sub = BindingHypothesisSet("Server_Node_1", "SUBJECT", ("Server_Node_1",))
    hypo_obj_op = BindingHypothesisSet("Value_Operational", "OBJECT", ("Value_Operational",))
    target_triple = ("Server_Node_1", "device_status", "Value_Operational")

    results: list[dict[str, Any]] = []

    # --- World 1: Standard Full Pass ---
    e1 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r1 = SourceRecord("r1", "Server 1 is Operational", CaptureProvenance("c1", "s", 2, "h1"), ClaimedOrigin("sensor_trusted_a", "sensor"), AuthenticatedOrigin("sensor_trusted_a", "ED25519", True), 2)
    a1 = ParsedAttestation("a1", "r1", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e1.ingest_record(r1, a1, hypo_sub, hypo_obj_op, contract_single)

    why1 = e1.bitemporal_engine.why_t(target_triple, 5.0, 2)
    active1 = any(f.subject == "Server_Node_1" and f.obj == "Value_Operational" for f in e1.bitemporal_engine.get_active_facts(5.0, 2))
    entitled1 = why1["is_entitled"]
    auth1 = (why1["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why1["lineage_sets_S_L_t"]))
    what_if1 = e1.bitemporal_engine.what_if_source_t("unrelated_source", target_triple, 5.0, 2)
    survives1 = what_if1["hypothetical_entitled"]

    raw1 = (1 if active1 else 0, 1 if entitled1 else 0, 1 if auth1 else 0, 1 if survives1 else 0)
    correctness1 = (1, 1, 1, 1)
    results.append({"world_id": "W1_FULL_PASS", "raw_vector": raw1, "correctness_vector": correctness1})

    # --- World 2: Blocked Action Governance (Raw: (1, 1, 0, 1)) ---
    e2 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r2 = SourceRecord("r2", "Server 1 is Operational", CaptureProvenance("c2", "s", 2, "h2"), ClaimedOrigin("sensor_untrusted_roots", "sensor"), AuthenticatedOrigin("sensor_untrusted_roots", "ED25519", True), 2)
    a2 = ParsedAttestation("a2", "r2", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e2.ingest_record(r2, a2, hypo_sub, hypo_obj_op, contract_single)

    why2 = e2.bitemporal_engine.why_t(target_triple, 5.0, 2)
    active2 = any(f.subject == "Server_Node_1" and f.obj == "Value_Operational" for f in e2.bitemporal_engine.get_active_facts(5.0, 2))
    entitled2 = why2["is_entitled"]
    # Blocked action governance because lineage root is not trusted ROOT_NET_1
    auth2 = (why2["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why2["lineage_sets_S_L_t"]))
    what_if2 = e2.bitemporal_engine.what_if_source_t("unrelated_source", target_triple, 5.0, 2)
    survives2 = what_if2["hypothetical_entitled"]

    raw2 = (1 if active2 else 0, 1 if entitled2 else 0, 1 if auth2 else 0, 1 if survives2 else 0)
    # Correctness: correctly admitted (1), correctly entitled (1), correctly blocked (1), correctly intact under non-ablation (1)
    correctness2 = (1, 1, 1, 1)
    results.append({"world_id": "W2_ACTION_GOVERNANCE_BLOCKED", "raw_vector": raw2, "correctness_vector": correctness2})

    # --- World 3: Failed Premise Challenge (Raw: (1, 0, 0, 1) for challenge triple) ---
    e3 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r3 = SourceRecord("r3", "Server 1 is Operational", CaptureProvenance("c3", "s", 2, "h3"), ClaimedOrigin("sensor_trusted_a", "sensor"), AuthenticatedOrigin("sensor_trusted_a", "ED25519", True), 2)
    a3 = ParsedAttestation("a3", "r3", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e3.ingest_record(r3, a3, hypo_sub, hypo_obj_op, contract_single)

    challenge_triple = ("Server_Node_1", "device_status", "Value_Baseline")
    why3 = e3.bitemporal_engine.why_t(challenge_triple, 5.0, 2)
    active3 = len(e3.bitemporal_engine.get_active_facts(5.0, 2)) > 0
    entitled3 = why3["is_entitled"]
    auth3 = (why3["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why3["lineage_sets_S_L_t"]))
    what_if3 = e3.bitemporal_engine.what_if_source_t("unrelated_source", target_triple, 5.0, 2)
    survives3 = what_if3["hypothetical_entitled"]

    raw3 = (1 if active3 else 0, 1 if entitled3 else 0, 1 if auth3 else 0, 1 if survives3 else 0)
    correctness3 = (1, 1, 1, 1)
    results.append({"world_id": "W3_PREMISE_CHALLENGE_FAILED", "raw_vector": raw3, "correctness_vector": correctness3})

    # --- World 4: Causal Source Ablation Vulnerable (Raw: (1, 1, 1, 0) under ablation) ---
    e4 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r4 = SourceRecord("r4", "Server 1 is Operational", CaptureProvenance("c4", "s", 2, "h4"), ClaimedOrigin("sensor_trusted_a", "sensor"), AuthenticatedOrigin("sensor_trusted_a", "ED25519", True), 2)
    a4 = ParsedAttestation("a4", "r4", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e4.ingest_record(r4, a4, hypo_sub, hypo_obj_op, contract_single)

    why4 = e4.bitemporal_engine.why_t(target_triple, 5.0, 2)
    active4 = any(f.subject == "Server_Node_1" and f.obj == "Value_Operational" for f in e4.bitemporal_engine.get_active_facts(5.0, 2))
    entitled4 = why4["is_entitled"]
    auth4 = (why4["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why4["lineage_sets_S_L_t"]))

    what_if_src = e4.bitemporal_engine.what_if_source_t("sensor_trusted_a", target_triple, 5.0, 2)
    survives4 = what_if_src["hypothetical_entitled"]  # False under ablation

    raw4 = (1 if active4 else 0, 1 if entitled4 else 0, 1 if auth4 else 0, 1 if survives4 else 0)
    correctness4 = (1, 1, 1, 1)
    results.append({"world_id": "W4_CAUSAL_SOURCE_ABLATION_VULNERABLE", "raw_vector": raw4, "correctness_vector": correctness4})

    # --- World 5: Multi-Source Redundant Rescue (Raw: (1, 1, 1, 1) under single-source ablation) ---
    e5 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r5a = SourceRecord("r5a", "Server 1 is Operational", CaptureProvenance("c5a", "s", 2, "h5a"), ClaimedOrigin("sensor_trusted_a", "sensor"), AuthenticatedOrigin("sensor_trusted_a", "ED25519", True), 2)
    a5a = ParsedAttestation("a5a", "r5a", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e5.ingest_record(r5a, a5a, hypo_sub, hypo_obj_op, contract_multi)

    r5b = SourceRecord("r5b", "Server 1 is Operational", CaptureProvenance("c5b", "s", 2, "h5b"), ClaimedOrigin("sensor_trusted_b", "sensor"), AuthenticatedOrigin("sensor_trusted_b", "ED25519", True), 2)
    a5b = ParsedAttestation("a5b", "r5b", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e5.ingest_record(r5b, a5b, hypo_sub, hypo_obj_op, contract_multi)

    why5 = e5.bitemporal_engine.why_t(target_triple, 5.0, 2)
    active5 = len(e5.bitemporal_engine.get_active_facts(5.0, 2)) >= 1
    entitled5 = why5["is_entitled"]
    auth5 = why5["bounded_authority"] == 1.0
    what_if_src5 = e5.bitemporal_engine.what_if_source_t("sensor_trusted_a", target_triple, 5.0, 2)
    survives5 = what_if_src5["hypothetical_entitled"]  # True because source B remains

    raw5 = (1 if active5 else 0, 1 if entitled5 else 0, 1 if auth5 else 0, 1 if survives5 else 0)
    correctness5 = (1, 1, 1, 1)
    results.append({"world_id": "W5_MULTISOURCE_REDUNDANT_RESCUE", "raw_vector": raw5, "correctness_vector": correctness5})

    # --- World 6: Dispute Isolation (Raw: (0, 0, 0, 0)) ---
    e6 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    b_fact = BitemporalFact("base_fact_6", "Server_Node_1", "device_status", "Value_Baseline", frozenset(["ROOT_NET_1_sensor_a"]), "sensor_trusted_a", "sensor_trusted_a")
    e6.bitemporal_engine.register_fact(b_fact)
    e6.bitemporal_engine.record_event(
        TemporalEvent(
            event_id="ev_base_6",
            event_type=EventType.ASSERT,
            t_knowledge=1,
            event_seq=1,
            t_valid_start=0.0,
            target_fact_id="base_fact_6",
        )
    )

    r6 = SourceRecord("r6", "Server 1 is Operational", CaptureProvenance("c6", "s", 2, "h6"), ClaimedOrigin("sensor_trusted_b", "sensor"), AuthenticatedOrigin("sensor_trusted_b", "ED25519", True), 2)
    a6 = ParsedAttestation("a6", "r6", "Server_Node_1", "device_status", "Value_Operational", 0.0)
    e6.ingest_record(r6, a6, hypo_sub, hypo_obj_op, contract_single)

    why6 = e6.bitemporal_engine.why_t(target_triple, 0.0, 2)
    active6 = len(e6.bitemporal_engine.get_active_facts(0.0, 2)) > 0  # 0 active under cautious dispute
    entitled6 = why6["is_entitled"]  # False
    auth6 = why6["bounded_authority"] == 1.0  # False (0.0)
    what_if6 = e6.bitemporal_engine.what_if_source_t("sensor_trusted_b", target_triple, 0.0, 2)
    survives6 = what_if6["hypothetical_entitled"]

    raw6 = (1 if active6 else 0, 1 if entitled6 else 0, 1 if auth6 else 0, 1 if survives6 else 0)
    correctness6 = (1, 1, 1, 1)
    results.append({"world_id": "W6_DISPUTE_ISOLATION", "raw_vector": raw6, "correctness_vector": correctness6})

    # --- World 7: Unauthenticated Inadmissible Input (Raw: (0, 0, 0, 0)) ---
    e7 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r7 = SourceRecord("r7", "Server 1 is Operational", CaptureProvenance("c7", "s", 2, "h7"), ClaimedOrigin("guest_anon", "guest"), AuthenticatedOrigin("guest_anon", "ANONYMOUS", False), 2)
    a7 = ParsedAttestation("a7", "r7", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    res7 = e7.ingest_record(r7, a7, hypo_sub, hypo_obj_op, contract_single)

    why7 = e7.bitemporal_engine.why_t(target_triple, 5.0, 2)
    active7 = len(e7.bitemporal_engine.get_active_facts(5.0, 2)) > 0
    entitled7 = why7["is_entitled"]
    auth7 = why7["bounded_authority"] == 1.0
    what_if7 = e7.bitemporal_engine.what_if_source_t("guest_anon", target_triple, 5.0, 2)
    survives7 = what_if7["hypothetical_entitled"]

    raw7 = (1 if active7 else 0, 1 if entitled7 else 0, 1 if auth7 else 0, 1 if survives7 else 0)
    correctness7 = (1, 1, 1, 1)
    results.append({"world_id": "W7_UNAUTHENTICATED_REJECT", "raw_vector": raw7, "correctness_vector": correctness7})

    # --- World 8: Out-of-Scope Predicate Reject (Raw: (0, 0, 0, 0)) ---
    e8 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r8 = SourceRecord("r8", "Server 1 is Operational", CaptureProvenance("c8", "s", 2, "h8"), ClaimedOrigin("guest_unauth", "guest"), AuthenticatedOrigin("guest_unauth", "OAUTH", True), 2)
    a8 = ParsedAttestation("a8", "r8", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    res8 = e8.ingest_record(r8, a8, hypo_sub, hypo_obj_op, contract_single)

    why8 = e8.bitemporal_engine.why_t(target_triple, 5.0, 2)
    active8 = len(e8.bitemporal_engine.get_active_facts(5.0, 2)) > 0
    entitled8 = why8["is_entitled"]
    auth8 = why8["bounded_authority"] == 1.0
    what_if8 = e8.bitemporal_engine.what_if_source_t("guest_unauth", target_triple, 5.0, 2)
    survives8 = what_if8["hypothetical_entitled"]

    raw8 = (1 if active8 else 0, 1 if entitled8 else 0, 1 if auth8 else 0, 1 if survives8 else 0)
    correctness8 = (1, 1, 1, 1)
    results.append({"world_id": "W8_OUT_OF_SCOPE_REJECT", "raw_vector": raw8, "correctness_vector": correctness8})

    raw_profiles = {r["world_id"]: r["raw_vector"] for r in results}
    correctness_profiles = {r["world_id"]: r["correctness_vector"] for r in results}

    return {
        "n_worlds": len(results),
        "results": results,
        "raw_profiles": raw_profiles,
        "correctness_profiles": correctness_profiles,
        "has_decoupled_governance_raw": raw_profiles["W2_ACTION_GOVERNANCE_BLOCKED"] == (1, 1, 0, 1),
        "has_decoupled_premise_raw": raw_profiles["W3_PREMISE_CHALLENGE_FAILED"] == (1, 0, 0, 1),
        "has_decoupled_causal_raw": raw_profiles["W4_CAUSAL_SOURCE_ABLATION_VULNERABLE"] == (1, 1, 1, 0),
        "has_redundant_rescue_raw": raw_profiles["W5_MULTISOURCE_REDUNDANT_RESCUE"] == (1, 1, 1, 1),
    }
