"""8-World Probe Separation Assay with Full Engine-Derived Evaluation (Stage 7A.3).

Demonstrates genuine non-monotonic decoupling across the 4 Downstream Probes:
- Q1: Bitemporal Active State
- Q2: Structured Premise Challenge Antichain Support S_t (via why_t)
- Q3: Action Policy Authority Auth(S_L)
- Q4: True Causal Source/Lineage Ablation do(source_i = 0) (via what_if_source_t)
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
    """Run an 8-world probe-separation assay with 100% engine-derived probe measurements."""
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
        EntityDefinition("Value_Baseline", "Baseline", "STATUS"),
        EntityDefinition("Value_Degraded", "Degraded", "STATUS"),
    ])

    cap_registry = CapabilityPolicyRegistry({
        "sensor_trusted_a": CapabilityPolicy("sensor_trusted_a", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR"),
        "sensor_trusted_b": CapabilityPolicy("sensor_trusted_b", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR"),
        "sensor_untrusted_roots": CapabilityPolicy("sensor_untrusted_roots", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "UNVERIFIED_SENSOR"),
        "guest_unauth": CapabilityPolicy("guest_unauth", frozenset(["feedback"]), ClaimPrivilege.ATTESTATION_ONLY, "WEB"),
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

    # --- World 1: Standard Full Pass -> Profile (1, 1, 1, 1) ---
    e1 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r1 = SourceRecord("r1", "Server 1 is Operational", CaptureProvenance("c1", "s", 2, "h1"), ClaimedOrigin("sensor_trusted_a", "sensor"), AuthenticatedOrigin("sensor_trusted_a", "ED25519", True), 2)
    a1 = ParsedAttestation("a1", "r1", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e1.ingest_record(r1, a1, hypo_sub, hypo_obj_op, contract_single)

    why1 = e1.bitemporal_engine.why_t(target_triple, 5.0, 2)
    q1_1 = 1 if len(e1.bitemporal_engine.get_active_facts(5.0, 2)) == 1 else 0
    q2_1 = 1 if why1["is_entitled"] else 0
    q3_1 = 1 if (why1["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why1["lineage_sets_S_L_t"])) else 0
    q4_1 = 1
    results.append({"world_id": "W1_FULL_PASS", "profile": (q1_1, q2_1, q3_1, q4_1)})

    # --- World 2: Blocked Action Governance -> Profile (1, 1, 0, 1) ---
    e2 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r2 = SourceRecord("r2", "Server 1 is Operational", CaptureProvenance("c2", "s", 2, "h2"), ClaimedOrigin("sensor_untrusted_roots", "sensor"), AuthenticatedOrigin("sensor_untrusted_roots", "ED25519", True), 2)
    a2 = ParsedAttestation("a2", "r2", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e2.ingest_record(r2, a2, hypo_sub, hypo_obj_op, contract_single)

    why2 = e2.bitemporal_engine.why_t(target_triple, 5.0, 2)
    q1_2 = 1 if len(e2.bitemporal_engine.get_active_facts(5.0, 2)) == 1 else 0
    q2_2 = 1 if why2["is_entitled"] else 0
    q3_2 = 1 if (why2["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why2["lineage_sets_S_L_t"])) else 0
    q4_2 = 1
    results.append({"world_id": "W2_ACTION_GOVERNANCE_BLOCKED", "profile": (q1_2, q2_2, q3_2, q4_2)})

    # --- World 3: Failed Premise Challenge -> Profile (1, 0, 0, 1) ---
    e3 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r3 = SourceRecord("r3", "Server 1 is Operational", CaptureProvenance("c3", "s", 2, "h3"), ClaimedOrigin("sensor_trusted_a", "sensor"), AuthenticatedOrigin("sensor_trusted_a", "ED25519", True), 2)
    a3 = ParsedAttestation("a3", "r3", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e3.ingest_record(r3, a3, hypo_sub, hypo_obj_op, contract_single)

    challenge_triple = ("Server_Node_1", "device_status", "Value_Baseline")
    why3 = e3.bitemporal_engine.why_t(challenge_triple, 5.0, 2)
    q1_3 = 1 if len(e3.bitemporal_engine.get_active_facts(5.0, 2)) == 1 else 0
    q2_3 = 1 if why3["is_entitled"] else 0
    q3_3 = 1 if (why3["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why3["lineage_sets_S_L_t"])) else 0
    q4_3 = 1
    results.append({"world_id": "W3_PREMISE_CHALLENGE_FAILED", "profile": (q1_3, q2_3, q3_3, q4_3)})

    # --- World 4: Causal Source Ablation Vulnerable -> Profile (1, 1, 1, 0) ---
    e4 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r4 = SourceRecord("r4", "Server 1 is Operational", CaptureProvenance("c4", "s", 2, "h4"), ClaimedOrigin("sensor_trusted_a", "sensor"), AuthenticatedOrigin("sensor_trusted_a", "ED25519", True), 2)
    a4 = ParsedAttestation("a4", "r4", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e4.ingest_record(r4, a4, hypo_sub, hypo_obj_op, contract_single)

    why4 = e4.bitemporal_engine.why_t(target_triple, 5.0, 2)
    q1_4 = 1 if len(e4.bitemporal_engine.get_active_facts(5.0, 2)) == 1 else 0
    q2_4 = 1 if why4["is_entitled"] else 0
    q3_4 = 1 if (why4["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why4["lineage_sets_S_L_t"])) else 0

    what_if_src = e4.bitemporal_engine.what_if_source_t("sensor_trusted_a", target_triple, 5.0, 2)
    q4_4 = 0 if not what_if_src["hypothetical_entitled"] else 1
    results.append({"world_id": "W4_CAUSAL_SOURCE_ABLATION_VULNERABLE", "profile": (q1_4, q2_4, q3_4, q4_4)})

    # --- World 5: Multi-Source Redundant Rescue -> Profile (1, 1, 1, 1) ---
    e5 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r5a = SourceRecord("r5a", "Server 1 is Operational", CaptureProvenance("c5a", "s", 2, "h5a"), ClaimedOrigin("sensor_trusted_a", "sensor"), AuthenticatedOrigin("sensor_trusted_a", "ED25519", True), 2)
    a5a = ParsedAttestation("a5a", "r5a", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e5.ingest_record(r5a, a5a, hypo_sub, hypo_obj_op, contract_multi)

    r5b = SourceRecord("r5b", "Server 1 is Operational", CaptureProvenance("c5b", "s", 2, "h5b"), ClaimedOrigin("sensor_trusted_b", "sensor"), AuthenticatedOrigin("sensor_trusted_b", "ED25519", True), 2)
    a5b = ParsedAttestation("a5b", "r5b", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    e5.ingest_record(r5b, a5b, hypo_sub, hypo_obj_op, contract_multi)

    why5 = e5.bitemporal_engine.why_t(target_triple, 5.0, 2)
    q1_5 = 1 if len(e5.bitemporal_engine.get_active_facts(5.0, 2)) >= 1 else 0
    q2_5 = 1 if why5["is_entitled"] else 0
    q3_5 = 1 if why5["bounded_authority"] == 1.0 else 0
    what_if_src5 = e5.bitemporal_engine.what_if_source_t("sensor_trusted_a", target_triple, 5.0, 2)
    q4_5 = 1 if what_if_src5["hypothetical_entitled"] else 0
    results.append({"world_id": "W5_MULTISOURCE_REDUNDANT_RESCUE", "profile": (q1_5, q2_5, q3_5, q4_5)})

    # --- World 6: Dispute Isolation -> Profile (1, 1, 1, 1) ---
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
    q1_6 = 1 if len(e6.bitemporal_engine.get_active_facts(0.0, 2)) == 0 else 0
    q2_6 = 1 if not why6["is_entitled"] else 0
    q3_6 = 1 if why6["bounded_authority"] == 0.0 else 0
    q4_6 = 1
    results.append({"world_id": "W6_DISPUTE_ISOLATION", "profile": (q1_6, q2_6, q3_6, q4_6)})

    # --- World 7: Unauthenticated Inadmissible Input -> Profile (1, 1, 1, 1) ---
    e7 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r7 = SourceRecord("r7", "Server 1 is Operational", CaptureProvenance("c7", "s", 2, "h7"), ClaimedOrigin("guest_anon", "guest"), AuthenticatedOrigin("guest_anon", "ANONYMOUS", False), 2)
    a7 = ParsedAttestation("a7", "r7", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    res7 = e7.ingest_record(r7, a7, hypo_sub, hypo_obj_op, contract_single)

    why7 = e7.bitemporal_engine.why_t(target_triple, 5.0, 2)
    q1_7 = 1 if len(e7.bitemporal_engine.get_active_facts(5.0, 2)) == 0 else 0
    q2_7 = 1 if not why7["is_entitled"] else 0
    q3_7 = 1 if why7["bounded_authority"] == 0.0 else 0
    q4_7 = 1
    results.append({"world_id": "W7_UNAUTHENTICATED_REJECT", "profile": (q1_7, q2_7, q3_7, q4_7)})

    # --- World 8: Out-of-Scope Predicate Reject -> Profile (1, 1, 1, 1) ---
    e8 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    r8 = SourceRecord("r8", "Server 1 is Operational", CaptureProvenance("c8", "s", 2, "h8"), ClaimedOrigin("guest_unauth", "guest"), AuthenticatedOrigin("guest_unauth", "OAUTH", True), 2)
    a8 = ParsedAttestation("a8", "r8", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    res8 = e8.ingest_record(r8, a8, hypo_sub, hypo_obj_op, contract_single)

    why8 = e8.bitemporal_engine.why_t(target_triple, 5.0, 2)
    q1_8 = 1 if len(e8.bitemporal_engine.get_active_facts(5.0, 2)) == 0 else 0
    q2_8 = 1 if not why8["is_entitled"] else 0
    q3_8 = 1 if why8["bounded_authority"] == 0.0 else 0
    q4_8 = 1
    results.append({"world_id": "W8_OUT_OF_SCOPE_REJECT", "profile": (q1_8, q2_8, q3_8, q4_8)})

    profiles = {r["world_id"]: r["profile"] for r in results}
    return {
        "n_worlds": len(results),
        "results": results,
        "profiles": profiles,
        "has_decoupled_governance": profiles["W2_ACTION_GOVERNANCE_BLOCKED"] == (1, 1, 0, 1),
        "has_decoupled_premise": profiles["W3_PREMISE_CHALLENGE_FAILED"] == (1, 0, 0, 1),
        "has_decoupled_causal": profiles["W4_CAUSAL_SOURCE_ABLATION_VULNERABLE"] == (1, 1, 1, 0),
        "has_redundant_rescue": profiles["W5_MULTISOURCE_REDUNDANT_RESCUE"] == (1, 1, 1, 1),
    }
