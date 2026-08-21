"""Role Distractor vs True Linguistic Ambiguity Sidecar (Stage 7A.1)."""

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
from gene.ingress.ontology import CapabilityPolicy, CapabilityPolicyRegistry, EntityDefinition, IngressOntology
from gene.ingress.engine import IngressEngine
from gene.ingress.policies import A4FullGENEIngressPolicy
from gene.supersession_engine import BitemporalEngine, PredicateContract


def run_role_distractor_assay() -> dict[str, Any]:
    """Test downstream admission correctness given resolved role vs unresolved ambiguity.
    
    Case 1: Correctly role-resolved mention -> ADMIT.
    Case 2: True ambiguity with multiple candidates -> DEFERRED_BINDING.
    """
    ontology = IngressOntology([
        EntityDefinition("Sensor_Alpha", "Field Sensor Alpha", "SENSOR"),
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Server_Node_1_Primary", "Server 1 Primary", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Server_Node_1_Backup", "Server 1 Backup", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", "ROOT_1"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")

    engine = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())

    # Case 1: Role Distractor where semantic parsing extracts Server_Node_1 as subject
    rec_role = SourceRecord("rec_role", "Field Sensor Alpha reported Server Node 1 status as Operational", CaptureProvenance("c1", "telemetry", 1, "h1"), ClaimedOrigin("sensor_alpha", "sensor"), AuthenticatedOrigin("sensor_alpha", "ED25519", True), 1)
    att_role = ParsedAttestation("att_role", "rec_role", "Server Node 1", "device_status", "Operational", 0.0)
    hypo_role_sub = BindingHypothesisSet("Server Node 1", "SUBJECT", ("Server_Node_1",))
    hypo_obj = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    res_role = engine.ingest_record(rec_role, att_role, hypo_role_sub, hypo_obj, contract)

    # Case 2: True Ambiguity where mention produces 2 candidates
    rec_ambig = SourceRecord("rec_ambig", "Server 1 status is Operational", CaptureProvenance("c1", "telemetry", 2, "h2"), ClaimedOrigin("sensor_alpha", "sensor"), AuthenticatedOrigin("sensor_alpha", "ED25519", True), 2)
    att_ambig = ParsedAttestation("att_ambig", "rec_ambig", "Server 1", "device_status", "Operational", 0.0)
    hypo_ambig_sub = BindingHypothesisSet("Server 1", "SUBJECT", ("Server_Node_1_Primary", "Server_Node_1_Backup"))

    res_ambig = engine.ingest_record(rec_ambig, att_ambig, hypo_ambig_sub, hypo_obj, contract)

    return {
        "role_distractor_status": res_role["status"],
        "true_ambiguity_status": res_ambig["status"],
        "pass": (res_role["status"] == "ADMIT" and res_ambig["status"] == "DEFER"),
    }
