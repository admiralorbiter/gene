"""Unit tests for Thread A Epistemic Ingress Engine and Ingress Policies (A0 to A4)."""

import pytest
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
from gene.ingress.policies import (
    A0Top1BlindWritePolicy,
    A1CanonicalizationOnlyPolicy,
    A2CandidateAwarePolicy,
    A3AuthorityAwarePolicy,
    A4FullGENEIngressPolicy,
)
from gene.ingress.engine import IngressEngine
from gene.supersession_engine import BitemporalEngine, PredicateContract


@pytest.fixture
def sample_ontology() -> IngressOntology:
    entities = [
        EntityDefinition(entity_id="Server_Node_1", canonical_name="Server Node 1", entity_type="SERVER", aliases=("Server 1", "S1")),
        EntityDefinition(entity_id="Server_Node_1_Backup", canonical_name="Server Node 1 Backup", entity_type="SERVER", aliases=("Backup Server 1", "S1_Backup")),
        EntityDefinition(entity_id="Facility_East", canonical_name="Facility East", entity_type="FACILITY", aliases=("East Wing", "FE")),
        EntityDefinition(entity_id="Value_Operational", canonical_name="Operational", entity_type="STATUS_VALUE", aliases=("Active", "OK")),
        EntityDefinition(entity_id="Value_Degraded", canonical_name="Degraded", entity_type="STATUS_VALUE", aliases=("Warning", "Slow")),
    ]
    return IngressOntology(entities)


@pytest.fixture
def sample_capability_registry() -> CapabilityPolicyRegistry:
    policies = {
        "admin": CapabilityPolicy(source_role="admin", authorized_predicates=frozenset(["*"]), max_claim_privilege="ROOT_FACT"),
        "sensor": CapabilityPolicy(source_role="sensor", authorized_predicates=frozenset(["device_status", "temperature"]), max_claim_privilege="ROOT_FACT"),
        "guest": CapabilityPolicy(source_role="guest", authorized_predicates=frozenset(["user_feedback"]), max_claim_privilege="ATTESTATION_ONLY"),
    }
    return CapabilityPolicyRegistry(policies)


@pytest.fixture
def status_contract() -> PredicateContract:
    return PredicateContract(
        predicate="device_status",
        cardinality="SINGLE",
        temporal_mode="TIME_VARYING",
    )


def test_a0_top1_blind_write_policy(sample_ontology, sample_capability_registry, status_contract):
    policy = A0Top1BlindWritePolicy()
    source_rec = SourceRecord(
        record_id="rec_001",
        raw_text="Server 1 is Operational",
        capture_provenance=CaptureProvenance("conn_1", "sensor_feed", 1, "hash_1"),
        claimed_origin=ClaimedOrigin("sensor_alpha", "sensor"),
        authenticated_origin=AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    attestation = ParsedAttestation("att_001", "rec_001", "Server 1", "device_status", "Operational", 0.0)
    sub_hypo = BindingHypothesisSet("Server 1", "SUBJECT", ("Server_Node_1", "Server_Node_1_Backup"))
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))
    src_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "SENSOR_NET_1")

    cert, obs, deferred, prov = policy.evaluate(
        source_rec, attestation, sub_hypo, obj_hypo, sample_ontology, sample_capability_registry, status_contract, src_ctx
    )

    # A0 binds top-1 candidate blindly
    assert cert.status == AdmissionStatus.ADMIT
    assert obs is not None
    assert obs.subject == "Server_Node_1"
    assert deferred is None
    assert prov is None


def test_a4_full_gene_ingress_preserves_ambiguity(sample_ontology, sample_capability_registry, status_contract):
    policy = A4FullGENEIngressPolicy()
    source_rec = SourceRecord(
        record_id="rec_002",
        raw_text="Server 1 is Operational",
        capture_provenance=CaptureProvenance("conn_1", "sensor_feed", 1, "hash_2"),
        claimed_origin=ClaimedOrigin("sensor_alpha", "sensor"),
        authenticated_origin=AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    attestation = ParsedAttestation("att_002", "rec_002", "Server 1", "device_status", "Operational", 0.0)
    # Ambiguous collision: 2 candidate IDs
    sub_hypo = BindingHypothesisSet("Server 1", "SUBJECT", ("Server_Node_1", "Server_Node_1_Backup"))
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))
    src_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "SENSOR_NET_1")

    cert, obs, deferred, prov = policy.evaluate(
        source_rec, attestation, sub_hypo, obj_hypo, sample_ontology, sample_capability_registry, status_contract, src_ctx
    )

    # A4 must DEFER and preserve candidates in DEFERRED_BINDING
    assert cert.status == AdmissionStatus.DEFER
    assert obs is None
    assert deferred is not None
    assert deferred.subject_hypotheses.candidate_entity_ids == ("Server_Node_1", "Server_Node_1_Backup")
    assert prov is None


def test_a4_full_gene_ingress_detects_unauthorized_scope(sample_ontology, sample_capability_registry, status_contract):
    policy = A4FullGENEIngressPolicy()
    source_rec = SourceRecord(
        record_id="rec_003",
        raw_text="Admin access granted to Operator",
        capture_provenance=CaptureProvenance("conn_1", "sensor_feed", 1, "hash_3"),
        claimed_origin=ClaimedOrigin("sensor_alpha", "sensor"),
        authenticated_origin=AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    # Out of scope predicate: 'security_clearance' not in sensor scope
    attestation = ParsedAttestation("att_003", "rec_003", "Server 1", "security_clearance", "Operational", 0.0)
    sub_hypo = BindingHypothesisSet("Server 1", "SUBJECT", ("Server_Node_1",))
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))
    src_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "SENSOR_NET_1")

    cert, obs, deferred, prov = policy.evaluate(
        source_rec, attestation, sub_hypo, obj_hypo, sample_ontology, sample_capability_registry, status_contract, src_ctx
    )

    # A4 must REJECT out-of-scope capability
    assert cert.status == AdmissionStatus.REJECT
    assert "OUT_OF_SCOPE" in cert.rejection_cause
