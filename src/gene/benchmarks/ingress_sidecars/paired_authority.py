"""Paired Authority and Privilege Scope Sidecar (Stage 7A.2)."""

from typing import Any
from gene.ingress.models import (
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ClaimPrivilege,
    ClaimType,
    ParsedAttestation,
    SourceRecord,
)
from gene.ingress.ontology import CapabilityPolicy, CapabilityPolicyRegistry, EntityDefinition, IngressOntology
from gene.ingress.engine import IngressEngine
from gene.ingress.policies import A4FullGENEIngressPolicy
from gene.supersession_engine import BitemporalEngine, PredicateContract


def run_paired_authority_assay() -> dict[str, Any]:
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "sensor_1": CapabilityPolicy("sensor_1", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "SENSOR"),
        "admin_user": CapabilityPolicy("admin_user", frozenset(["operator_task", "device_status"]), ClaimPrivilege.ROOT_FACT, "OPERATOR"),
        "external_blog": CapabilityPolicy("external_blog", frozenset(["device_status"]), ClaimPrivilege.ATTESTATION_ONLY, "WEB"),
        "cot_reasoner": CapabilityPolicy("cot_reasoner", frozenset(["device_status"]), ClaimPrivilege.ATTESTATION_ONLY, "MODEL"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    hypo_sub = BindingHypothesisSet("Server Node 1", "SUBJECT", ("Server_Node_1",))
    hypo_obj = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    results = {}

    # Arm 1: PLATFORM_ATTESTED
    engine_1 = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    rec_1 = SourceRecord("rec_1", "Server Node 1 is Operational", CaptureProvenance("c1", "telemetry", 1, "h1"), ClaimedOrigin("sensor_1", "sensor"), AuthenticatedOrigin("sensor_1", "ED25519", True), 1)
    att_1 = ParsedAttestation("att_1", "rec_1", "Server Node 1", "device_status", "Operational", 0.0)
    res_1 = engine_1.ingest_record(rec_1, att_1, hypo_sub, hypo_obj, contract)
    results["PLATFORM_ATTESTED"] = res_1["status"]

    # Arm 2: USER_DIRECT
    engine_2 = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    rec_2 = SourceRecord("rec_2", "Server Node 1 is Operational", CaptureProvenance("c2", "ui", 1, "h2"), ClaimedOrigin("admin_user", "operator"), AuthenticatedOrigin("admin_user", "OAUTH_TOKEN", True), 1)
    att_2 = ParsedAttestation("att_2", "rec_2", "Server Node 1", "device_status", "Operational", 0.0)
    res_2 = engine_2.ingest_record(rec_2, att_2, hypo_sub, hypo_obj, contract)
    results["USER_DIRECT"] = res_2["status"]

    # Arm 3: THIRD_PARTY_QUOTED (Unauthenticated anonymous)
    engine_3 = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    rec_3 = SourceRecord("rec_3", "Server Node 1 is Operational", CaptureProvenance("c3", "web_scraper", 1, "h3"), ClaimedOrigin("external_blog", "web"), AuthenticatedOrigin("external_blog", "ANONYMOUS", False), 1)
    att_3 = ParsedAttestation("att_3", "rec_3", "Server Node 1", "device_status", "Operational", 0.0)
    res_3 = engine_3.ingest_record(rec_3, att_3, hypo_sub, hypo_obj, contract)
    results["THIRD_PARTY_QUOTED"] = res_3["status"]

    # Arm 4: MODEL_DERIVED (Privilege restricted to ATTESTATION_ONLY)
    engine_4 = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    rec_4 = SourceRecord("rec_4", "Server Node 1 is Operational", CaptureProvenance("c4", "cot_step", 1, "h4"), ClaimedOrigin("cot_reasoner", "model"), AuthenticatedOrigin("cot_reasoner", "KERNEL_LOCAL", True), 1)
    att_4 = ParsedAttestation("att_4", "rec_4", "Server Node 1", "device_status", "Operational", 0.0, extracted_claim_type=ClaimType.HYPOTHETICAL_DERIVATION)
    res_4 = engine_4.ingest_record(rec_4, att_4, hypo_sub, hypo_obj, contract)
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
