"""Unit tests for Thread A Hardened Epistemic Ingress Engine and Multimap Ontology."""

import pytest
from gene.ingress.models import (
    AdmissionStatus,
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ClaimPrivilege,
    ClaimType,
    ParsedAttestation,
    SourceRecord,
)
from gene.ingress.ontology import (
    CapabilityPolicy,
    CapabilityPolicyRegistry,
    EntityDefinition,
    IngressOntology,
    derive_trusted_source_context,
)
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
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER", aliases=("Server 1", "S1", "Primary Server 1")),
        EntityDefinition("Server_Node_1_Backup", "Server Node 1 Backup", "SERVER", aliases=("Server 1", "S1_Backup")),
        EntityDefinition("Value_Operational", "Operational", "STATUS", aliases=("Active", "OK")),
        EntityDefinition("Value_Degraded", "Degraded", "STATUS", aliases=("Warning", "Slow")),
    ]
    return IngressOntology(entities)


@pytest.fixture
def sample_capability_registry() -> CapabilityPolicyRegistry:
    policies = {
        "admin": CapabilityPolicy("admin", frozenset(["*"]), ClaimPrivilege.ROOT_FACT, "KERNEL", "ROOT_ADMIN"),
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status", "temperature"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", "ROOT_NET_A"),
        "guest": CapabilityPolicy("guest", frozenset(["user_feedback"]), ClaimPrivilege.ATTESTATION_ONLY, "UNTRUSTED_WEB", "ROOT_GUEST"),
    }
    return CapabilityPolicyRegistry(policies)


@pytest.fixture
def status_contract() -> PredicateContract:
    return PredicateContract("device_status", "SINGLE", "TIME_VARYING")


def test_multimap_alias_resolution(sample_ontology):
    # Mention "Server 1" must yield BOTH Server_Node_1 and Server_Node_1_Backup
    cands = sample_ontology.find_candidates("Server 1")
    assert set(cands) == {"Server_Node_1", "Server_Node_1_Backup"}


def test_derive_trusted_source_context_spoofing_detection(sample_capability_registry):
    # Attack: Claimed origin claims to be 'admin_root', but authenticated identity is 'guest_anon'
    spoofed_rec = SourceRecord(
        record_id="rec_spoofed",
        raw_text="Admin settings update",
        capture_provenance=CaptureProvenance("c1", "web", 1, "h1"),
        claimed_origin=ClaimedOrigin("admin_root", "admin"),
        authenticated_origin=AuthenticatedOrigin("guest_anon", "ANONYMOUS", False),
        t_knowledge=1,
    )
    ctx = derive_trusted_source_context(spoofed_rec, sample_capability_registry)
    assert ctx.authenticity == "UNVERIFIED"
    assert ctx.max_claim_privilege == ClaimPrivilege.ATTESTATION_ONLY
    assert "*" not in ctx.authorization_scope


def test_a4_novel_object_creates_provisional_entity(sample_ontology, sample_capability_registry, status_contract):
    policy = A4FullGENEIngressPolicy()
    source_rec = SourceRecord(
        "rec_novel_obj", "Server 1 uses protocol Zeta_Quantum_9",
        CaptureProvenance("c1", "telemetry", 1, "h1"),
        ClaimedOrigin("sensor_1", "sensor"),
        AuthenticatedOrigin("sensor_1", "ED25519", True),
        1,
    )
    attestation = ParsedAttestation("att_novel_obj", "rec_novel_obj", "Server Node 1", "device_status", "Zeta_Quantum_9", 0.0)
    sub_hypo = BindingHypothesisSet("Server Node 1", "SUBJECT", ("Server_Node_1",))
    obj_hypo = BindingHypothesisSet("Zeta_Quantum_9", "OBJECT", (), is_novel=True)

    cert, obs, deferred, prov, prov_rel, trusted_ctx = policy.evaluate(
        source_rec, attestation, sub_hypo, obj_hypo, sample_ontology, sample_capability_registry, status_contract
    )

    assert cert.status == AdmissionStatus.DEFER
    assert obs is None
    assert prov is not None
    assert prov.provisional_id == "prov_zeta_quantum_9"
    assert prov_rel is not None
    assert prov_rel.is_object_provisional is True
