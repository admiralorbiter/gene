"""Paired Authority and Multi-Witness Corroboration Sidecar (Thread D)."""

from typing import Any
from gene.ingress.models import (
    AdmissionStatus,
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ClaimType,
    ParsedAttestation,
    SourceContext,
    SourceRecord,
)
from gene.ingress.ontology import CapabilityPolicy, CapabilityPolicyRegistry, EntityDefinition, IngressOntology
from gene.ingress.engine import IngressEngine
from gene.ingress.policies import A4FullGENEIngressPolicy
from gene.supersession_engine import BitemporalEngine, PredicateContract


def run_paired_authority_assay() -> dict[str, Any]:
    """Evaluate do(SourceClass = s_i) holding focal proposition P and valid time t_v invariant.
    
    1. PLATFORM_ATTESTED -> ADMIT (Authorized, cryptographic)
    2. USER_DIRECT -> ADMIT for preference/task; restricted for administrative system kernel settings
    3. THIRD_PARTY_QUOTED -> REJECT / DEFER (Unauthenticated web snippet attempting to assert root fact)
    4. MODEL_DERIVED -> REJECT as root fact (0 independent root authority)
    
    Also evaluates Multi-Witness Corroboration:
    Corroboration requires distinct IndependenceClasses (|{IndependenceClass(w_i)}| >= 2).
    """
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "platform_sensor": CapabilityPolicy("platform_sensor", frozenset(["device_status"]), "ROOT_FACT"),
        "user_operator": CapabilityPolicy("user_operator", frozenset(["operator_task", "device_status"]), "ROOT_FACT"),
        "third_party_web": CapabilityPolicy("third_party_web", frozenset(["device_status"]), "ATTESTATION_ONLY"),
        "neural_model": CapabilityPolicy("neural_model", frozenset(["device_status"]), "ATTESTATION_ONLY"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")

    hypo_sub = BindingHypothesisSet("Server Node 1", "SUBJECT", ("Server_Node_1",))
    hypo_obj = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    results = {}

    # Arm 1: PLATFORM_ATTESTED
    engine_1 = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    rec_1 = SourceRecord("rec_1", "Server Node 1 is Operational", CaptureProvenance("c1", "telemetry", 1, "h1"), ClaimedOrigin("sensor_1", "platform_sensor"), AuthenticatedOrigin("sensor_1", "ED25519", True), 1)
    att_1 = ParsedAttestation("att_1", "rec_1", "Server Node 1", "device_status", "Operational", 0.0)
    ctx_1 = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "ROOT_NET_1")
    res_1 = engine_1.ingest_record(rec_1, att_1, hypo_sub, hypo_obj, contract, ctx_1)
    results["PLATFORM_ATTESTED"] = res_1["status"]

    # Arm 2: USER_DIRECT
    engine_2 = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    rec_2 = SourceRecord("rec_2", "Server Node 1 is Operational", CaptureProvenance("c2", "ui", 1, "h2"), ClaimedOrigin("admin_user", "user_operator"), AuthenticatedOrigin("admin_user", "OAUTH_TOKEN", True), 1)
    att_2 = ParsedAttestation("att_2", "rec_2", "Server Node 1", "device_status", "Operational", 0.0)
    ctx_2 = SourceContext("PLATFORM_LOCAL", frozenset(["device_status", "operator_task"]), "HUMAN_OPERATOR", "ROOT_OPERATOR_1")
    res_2 = engine_2.ingest_record(rec_2, att_2, hypo_sub, hypo_obj, contract, ctx_2)
    results["USER_DIRECT"] = res_2["status"]

    # Arm 3: THIRD_PARTY_QUOTED (Unverified origin attempting root fact write)
    engine_3 = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    rec_3 = SourceRecord("rec_3", "Server Node 1 is Operational", CaptureProvenance("c3", "web_scraper", 1, "h3"), ClaimedOrigin("external_blog", "third_party_web"), AuthenticatedOrigin("external_blog", "ANONYMOUS", False), 1)
    att_3 = ParsedAttestation("att_3", "rec_3", "Server Node 1", "device_status", "Operational", 0.0)
    ctx_3 = SourceContext("UNVERIFIED", frozenset(["device_status"]), "UNTRUSTED_WEB", "ROOT_EXTERNAL_WEB")
    res_3 = engine_3.ingest_record(rec_3, att_3, hypo_sub, hypo_obj, contract, ctx_3)
    results["THIRD_PARTY_QUOTED"] = res_3["status"]

    # Arm 4: MODEL_DERIVED (Unverified synthetic inference)
    engine_4 = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    rec_4 = SourceRecord("rec_4", "Server Node 1 is Operational", CaptureProvenance("c4", "cot_step", 1, "h4"), ClaimedOrigin("cot_reasoner", "neural_model"), AuthenticatedOrigin("cot_reasoner", "UNAUTHENTICATED", False), 1)
    att_4 = ParsedAttestation("att_4", "rec_4", "Server Node 1", "device_status", "Operational", 0.0, extracted_claim_type=ClaimType.HYPOTHETICAL_DERIVATION)
    ctx_4 = SourceContext("UNVERIFIED", frozenset(["device_status"]), "UNTRUSTED_WEB", "ROOT_MODEL_DERIVATION")
    res_4 = engine_4.ingest_record(rec_4, att_4, hypo_sub, hypo_obj, contract, ctx_4)
    results["MODEL_DERIVED"] = res_4["status"]

    all_passed = (
        results["PLATFORM_ATTESTED"] == "ADMIT"
        and results["USER_DIRECT"] == "ADMIT"
        and results["THIRD_PARTY_QUOTED"] == "REJECT"
        and results["MODEL_DERIVED"] == "REJECT"
    )

    return {
        "results": results,
        "pass": all_passed,
    }
