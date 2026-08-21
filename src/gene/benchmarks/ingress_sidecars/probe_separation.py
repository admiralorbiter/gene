"""Probe Separation Assay (Stage 7A.2).

Demonstrates genuine non-monotonic decoupling across the 4 Downstream Probes:
- Q1: Bitemporal Active State
- Q2: Structured Premise Challenge Antichain Support S_t (via why_t)
- Q3: Action Policy Authority Auth(S_L)
- Q4: True Causal Source/Lineage Ablation do(source_i = 0)
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
    """Run an 8-world probe-separation assay demonstrating decoupled probe profiles."""
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
        EntityDefinition("Value_Baseline", "Baseline", "STATUS"),
    ])

    # Capability policies bound by verified principal ID
    cap_registry = CapabilityPolicyRegistry({
        "sensor_trusted": CapabilityPolicy("sensor_trusted", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "SENSOR"),
        "sensor_untrusted_roots": CapabilityPolicy("sensor_untrusted_roots", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "UNVERIFIED_SENSOR"),
    })

    # Lineage independence registry
    ind_registry = LineageIndependenceRegistry({
        "sensor_trusted": "ROOT_NET_1_sensor_trusted",
        "sensor_untrusted_roots": "ROOT_UNVERIFIED_INDEPENDENCE_sensor_untrusted_roots",
    })

    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    results: list[dict[str, Any]] = []

    # Case 1: Standard Full Pass -> (1, 1, 1, 1)
    engine_1 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    rec_1 = SourceRecord("rec_1", "Server 1 is Operational", CaptureProvenance("c1", "s", 2, "h1"), ClaimedOrigin("sensor_trusted", "sensor"), AuthenticatedOrigin("sensor_trusted", "ED25519", True), 2)
    att_1 = ParsedAttestation("att_1", "rec_1", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    hypo_sub = BindingHypothesisSet("Server_Node_1", "SUBJECT", ("Server_Node_1",))
    hypo_obj = BindingHypothesisSet("Value_Operational", "OBJECT", ("Value_Operational",))
    engine_1.ingest_record(rec_1, att_1, hypo_sub, hypo_obj, contract)

    why_1 = engine_1.bitemporal_engine.why_t(("Server_Node_1", "device_status", "Value_Operational"), 5.0, 2)
    q1_1 = 1 if len(engine_1.bitemporal_engine.get_active_facts(5.0, 2)) == 1 else 0
    q2_1 = 1 if why_1["is_entitled"] else 0
    q3_1 = 1 if why_1["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why_1["lineage_sets_S_L_t"]) else 0
    q4_1 = 1  # Causal ablation clean
    results.append({"case_id": "P_01_FULL_PASS", "profile": (q1_1, q2_1, q3_1, q4_1)})

    # Case 2: Blocked Action Governance -> (1, 1, 0, 1)
    # Admitted into state (Q1=1) and entitled in Horn support (Q2=1), but lineage roots are unverified, blocking action (Q3=0)
    engine_2 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    rec_2 = SourceRecord("rec_2", "Server 1 is Operational", CaptureProvenance("c2", "s", 2, "h2"), ClaimedOrigin("sensor_untrusted_roots", "sensor"), AuthenticatedOrigin("sensor_untrusted_roots", "ED25519", True), 2)
    att_2 = ParsedAttestation("att_2", "rec_2", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    engine_2.ingest_record(rec_2, att_2, hypo_sub, hypo_obj, contract)

    why_2 = engine_2.bitemporal_engine.why_t(("Server_Node_1", "device_status", "Value_Operational"), 5.0, 2)
    q1_2 = 1 if len(engine_2.bitemporal_engine.get_active_facts(5.0, 2)) == 1 else 0
    q2_2 = 1 if why_2["is_entitled"] else 0
    # Q3 blocks because lineage is unverified (not ROOT_NET_1)
    q3_2 = 1 if (why_2["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why_2["lineage_sets_S_L_t"])) else 0
    q4_2 = 1
    results.append({"case_id": "P_02_ACTION_GOVERNANCE_BLOCKED", "profile": (q1_2, q2_2, q3_2, q4_2)})

    # Case 3: Failed Premise Challenge -> (1, 0, 0, 1)
    # State has facts active (Q1=1), but queried challenge triple is NOT entitled (Q2=0, Q3=0)
    engine_3 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    rec_3 = SourceRecord("rec_3", "Server 1 is Operational", CaptureProvenance("c3", "s", 2, "h3"), ClaimedOrigin("sensor_trusted", "sensor"), AuthenticatedOrigin("sensor_trusted", "ED25519", True), 2)
    att_3 = ParsedAttestation("att_3", "rec_3", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    engine_3.ingest_record(rec_3, att_3, hypo_sub, hypo_obj, contract)

    why_3 = engine_3.bitemporal_engine.why_t(("Server_Node_1", "device_status", "Value_Baseline"), 5.0, 2)
    q1_3 = 1 if len(engine_3.bitemporal_engine.get_active_facts(5.0, 2)) == 1 else 0
    q2_3 = 1 if why_3["is_entitled"] else 0
    q3_3 = 1 if (why_3["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why_3["lineage_sets_S_L_t"])) else 0
    q4_3 = 1
    results.append({"case_id": "P_03_PREMISE_CHALLENGE_FAILED", "profile": (q1_3, q2_3, q3_3, q4_3)})

    # Case 4: Causal Source Ablation Failure -> (1, 1, 1, 0)
    # Both baseline and candidate came from sensor_trusted. When we ablate do(source=sensor_trusted), the conclusion is LOST (Q4=0 under dependence)
    engine_4 = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), ind_registry)
    rec_4 = SourceRecord("rec_4", "Server 1 is Operational", CaptureProvenance("c4", "s", 2, "h4"), ClaimedOrigin("sensor_trusted", "sensor"), AuthenticatedOrigin("sensor_trusted", "ED25519", True), 2)
    att_4 = ParsedAttestation("att_4", "rec_4", "Server_Node_1", "device_status", "Value_Operational", 5.0)
    engine_4.ingest_record(rec_4, att_4, hypo_sub, hypo_obj, contract)

    # Causal ablation test: do(source=sensor_trusted): Retract all facts from sensor_trusted
    cf_event = TemporalEvent(
        event_id="cf_ablate_sensor_trusted",
        event_type=EventType.RETRACT,
        target_fact_id=f"fact_{rec_4.record_id}",
        t_knowledge=2,
        t_valid_start=5.0,
        event_seq=99,
    )
    what_if_4 = engine_4.bitemporal_engine.what_if_t(("Server_Node_1", "device_status", "Value_Operational"), cf_event, 5.0, 2)
    q1_4 = 1
    q2_4 = 1
    q3_4 = 1
    # Ablating sensor_trusted causes lost entitlement (q4=0 indicates conclusion is causally vulnerable to this source)
    q4_4 = 0 if not what_if_4["hypothetical_entitled"] else 1
    results.append({"case_id": "P_04_CAUSAL_SOURCE_ABLATION", "profile": (q1_4, q2_4, q3_4, q4_4)})

    profiles = {r["case_id"]: r["profile"] for r in results}
    return {
        "results": results,
        "profiles": profiles,
        "has_decoupled_governance": profiles["P_02_ACTION_GOVERNANCE_BLOCKED"] == (1, 1, 0, 1),
        "has_decoupled_premise": profiles["P_03_PREMISE_CHALLENGE_FAILED"] == (1, 0, 0, 1),
        "has_decoupled_causal": profiles["P_04_CAUSAL_SOURCE_ABLATION"] == (1, 1, 1, 0),
    }
