"""Candidate Miss vs True Novelty Sidecar (Thread D)."""

from typing import Any, Tuple
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


def run_candidate_miss_assay() -> dict[str, Any]:
    """Evaluate system behavior under True Novelty vs Candidate Retrieval Miss.
    
    Case 1: NOVEL_TRUE (Entity truly absent from global domain ontology) -> Creates ProvisionalEntity.
    Case 2: KNOWN_BUT_CANDIDATE_MISS (Entity exists in ontology, but candidate generation returned empty) ->
            Detection of missing candidate triggers retrieval fallback / DEFERRED_BINDING without creating spurious duplicate entity.
    """
    global_ontology = IngressOntology([
        EntityDefinition("Server_Node_77", "Server Node 77", "SERVER", aliases=("Server 77",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status"]), "ROOT_FACT"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    src_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "ROOT_NET_1")

    engine = IngressEngine(global_ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())

    # Case 1: True Novel Entity "Device Quantum 9" (absent from ontology)
    rec_novel = SourceRecord("rec_nov", "Device Quantum 9 is Operational", CaptureProvenance("c1", "s", 1, "h1"), ClaimedOrigin("s1", "sensor"), AuthenticatedOrigin("s1", "ED25519", True), 1)
    att_novel = ParsedAttestation("att_nov", "rec_nov", "Device Quantum 9", "device_status", "Operational", 0.0)
    hypo_novel = BindingHypothesisSet("Device Quantum 9", "SUBJECT", (), is_novel=True)
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    res_novel = engine.ingest_record(rec_novel, att_novel, hypo_novel, obj_hypo, contract, src_ctx)

    # Case 2: Candidate Miss on existing Server Node 77
    # Mention is "Server 77", which is in ontology, but candidate retriever returned empty set () without marking novel
    rec_miss = SourceRecord("rec_miss", "Server 77 is Operational", CaptureProvenance("c1", "s", 2, "h2"), ClaimedOrigin("s1", "sensor"), AuthenticatedOrigin("s1", "ED25519", True), 2)
    att_miss = ParsedAttestation("att_miss", "rec_miss", "Server 77", "device_status", "Operational", 0.0)
    hypo_miss = BindingHypothesisSet("Server 77", "SUBJECT", (), is_novel=False)  # Not declared novel, but empty candidates

    res_miss = engine.ingest_record(rec_miss, att_miss, hypo_miss, obj_hypo, contract, src_ctx)

    return {
        "novel_status": res_novel["status"],
        "novel_provisional_created": len(engine.provisional_entities) == 1,
        "miss_status": res_miss["status"],
        "miss_spurious_provisional_created": len(engine.provisional_entities) > 1,
        "pass": (res_novel["status"] == "DEFER" and res_miss["status"] == "REJECT" and len(engine.provisional_entities) == 1),
    }
