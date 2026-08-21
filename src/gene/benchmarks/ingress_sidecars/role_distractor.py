"""Role Distractor vs True Linguistic Ambiguity Sidecar (Thread D)."""

from typing import Any
from gene.ingress.models import (
    AdmissionStatus,
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ParsedAttestation,
    SourceContext,
    SourceRecord,
)
from gene.ingress.ontology import CapabilityPolicy, CapabilityPolicyRegistry, EntityDefinition, IngressOntology
from gene.ingress.engine import IngressEngine
from gene.ingress.policies import A4FullGENEIngressPolicy
from gene.supersession_engine import BitemporalEngine, PredicateContract


def run_role_distractor_assay() -> dict[str, Any]:
    """Distinguish Role Distractor (resolvable subject) from True Ambiguity (unresolvable text).
    
    Case 1: ROLE_DISTRACTOR
    "Field Sensor Alpha reported Server Node 1 status as Operational"
    Entities present: Sensor_Alpha (reporter) and Server_Node_1 (monitored device).
    Semantic role correctly identifies Server_Node_1 as Subject -> ADMIT.
    
    Case 2: TRUE_AMBIGUITY
    "Server 1 status is Operational" (in an environment with Server_1_Primary and Server_1_Backup)
    Lacks distinguishing features -> DEFERRED_BINDING.
    """
    ontology = IngressOntology([
        EntityDefinition("Sensor_Alpha", "Field Sensor Alpha", "SENSOR"),
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Server_Node_1_Primary", "Server 1 Primary", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Server_Node_1_Backup", "Server 1 Backup", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status"]), "ROOT_FACT"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    src_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "ROOT_1")

    engine = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())

    # Case 1: Role Distractor where semantic parsing extracts Server_Node_1 as subject
    rec_role = SourceRecord("rec_role", "Field Sensor Alpha reported Server Node 1 status as Operational", CaptureProvenance("c1", "telemetry", 1, "h1"), ClaimedOrigin("sensor_alpha", "sensor"), AuthenticatedOrigin("sensor_alpha", "ED25519", True), 1)
    att_role = ParsedAttestation("att_role", "rec_role", "Server Node 1", "device_status", "Operational", 0.0)
    hypo_role_sub = BindingHypothesisSet("Server Node 1", "SUBJECT", ("Server_Node_1",))
    hypo_obj = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    res_role = engine.ingest_record(rec_role, att_role, hypo_role_sub, hypo_obj, contract, src_ctx)

    # Case 2: True Ambiguity where mention "Server 1" produces 2 candidates
    rec_ambig = SourceRecord("rec_ambig", "Server 1 status is Operational", CaptureProvenance("c1", "telemetry", 2, "h2"), ClaimedOrigin("sensor_alpha", "sensor"), AuthenticatedOrigin("sensor_alpha", "ED25519", True), 2)
    att_ambig = ParsedAttestation("att_ambig", "rec_ambig", "Server 1", "device_status", "Operational", 0.0)
    hypo_ambig_sub = BindingHypothesisSet("Server 1", "SUBJECT", ("Server_Node_1_Primary", "Server_Node_1_Backup"))

    res_ambig = engine.ingest_record(rec_ambig, att_ambig, hypo_ambig_sub, hypo_obj, contract, src_ctx)

    return {
        "role_distractor_status": res_role["status"],
        "true_ambiguity_status": res_ambig["status"],
        "pass": (res_role["status"] == "ADMIT" and res_ambig["status"] == "DEFER"),
    }
