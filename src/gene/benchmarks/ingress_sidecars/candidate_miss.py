"""Candidate Miss vs True Novelty Sidecar (Stage 7A.1)."""

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


def run_candidate_miss_assay() -> dict[str, Any]:
    """Evaluate system behavior under True Novelty vs Candidate Retrieval Miss.
    
    1. NOVEL_TRUE: Entity absent from global ontology -> Creates ProvisionalEntity.
    2. KNOWN_BUT_CANDIDATE_MISS: Entity exists in ontology, but candidate generator missed it.
       The gate fails closed (REJECT / ZERO_CANDIDATES_RESOLVED), avoiding spurious duplicate entity creation.
    """
    global_ontology = IngressOntology([
        EntityDefinition("Server_Node_77", "Server Node 77", "SERVER", aliases=("Server 77",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", "ROOT_NET_1"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")

    engine = IngressEngine(global_ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())

    # Case 1: True Novel Entity
    rec_novel = SourceRecord("rec_nov", "Device Quantum 9 is Operational", CaptureProvenance("c1", "s", 1, "h1"), ClaimedOrigin("sensor_1", "sensor"), AuthenticatedOrigin("sensor_1", "ED25519", True), 1)
    att_novel = ParsedAttestation("att_nov", "rec_nov", "Device Quantum 9", "device_status", "Operational", 0.0)
    hypo_novel = BindingHypothesisSet("Device Quantum 9", "SUBJECT", (), is_novel=True)
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    res_novel = engine.ingest_record(rec_novel, att_novel, hypo_novel, obj_hypo, contract)

    # Case 2: Candidate Miss on existing Server Node 77
    rec_miss = SourceRecord("rec_miss", "Server 77 is Operational", CaptureProvenance("c1", "s", 2, "h2"), ClaimedOrigin("sensor_1", "sensor"), AuthenticatedOrigin("sensor_1", "ED25519", True), 2)
    att_miss = ParsedAttestation("att_miss", "rec_miss", "Server 77", "device_status", "Operational", 0.0)
    hypo_miss = BindingHypothesisSet("Server 77", "SUBJECT", (), is_novel=False)

    res_miss = engine.ingest_record(rec_miss, att_miss, hypo_miss, obj_hypo, contract)

    return {
        "novel_status": res_novel["status"],
        "novel_provisional_created": len(engine.provisional_entities) == 1,
        "miss_status": res_miss["status"],
        "miss_spurious_provisional_created": len(engine.provisional_entities) > 1,
        "pass": (res_novel["status"] == "DEFER" and res_miss["status"] == "REJECT" and len(engine.provisional_entities) == 1),
    }
