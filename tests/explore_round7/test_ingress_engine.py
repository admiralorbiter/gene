"""Unit tests for Thread A Hardened Epistemic Ingress Engine (Stage 7A.2)."""

import pytest
from gene.ingress.models import (
    AdmissionStatus,
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
    derive_trusted_source_context,
)
from gene.ingress.policies import A4FullGENEIngressPolicy
from gene.supersession_engine import PredicateContract


@pytest.fixture
def sample_ontology() -> IngressOntology:
    entities = [
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER", aliases=("Server 1", "S1")),
        EntityDefinition("Server_Node_1_Backup", "Server Node 1 Backup", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS", aliases=("Active",)),
    ]
    return IngressOntology(entities)


@pytest.fixture
def sample_capability_registry() -> CapabilityPolicyRegistry:
    policies = {
        "admin_principal": CapabilityPolicy("admin_principal", frozenset(["*"]), ClaimPrivilege.ROOT_FACT, "KERNEL", is_ontology_admin=True),
        "sensor_alpha": CapabilityPolicy("sensor_alpha", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR"),
        "guest_user": CapabilityPolicy("guest_user", frozenset(["feedback"]), ClaimPrivilege.ATTESTATION_ONLY, "WEB"),
    }
    return CapabilityPolicyRegistry(policies)


def test_multimap_alias_resolution(sample_ontology):
    cands = sample_ontology.find_candidates("Server 1")
    assert set(cands) == {"Server_Node_1", "Server_Node_1_Backup"}


def test_principal_bound_role_spoofing_prevented(sample_capability_registry):
    # Attack: sensor_alpha claims role 'admin_principal' in text payload
    rec = SourceRecord(
        record_id="rec_spoof_role",
        raw_text="Admin payload",
        capture_provenance=CaptureProvenance("c1", "web", 1, "h1"),
        claimed_origin=ClaimedOrigin("sensor_alpha", "admin_principal"),
        authenticated_origin=AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    # derive_trusted_source_context looks up policy for verified_id 'sensor_alpha', NOT claimed_role!
    ctx = derive_trusted_source_context(rec, sample_capability_registry)
    assert ctx.authorization_scope == frozenset(["device_status"])
    assert "*" not in ctx.authorization_scope


def test_a4_dual_novel_entities(sample_ontology, sample_capability_registry):
    policy = A4FullGENEIngressPolicy()
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    rec = SourceRecord(
        "rec_dual", "Device Alpha uses Protocol Beta",
        CaptureProvenance("c1", "t", 1, "h1"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        1,
    )
    att = ParsedAttestation("att_dual", "rec_dual", "Device Alpha", "device_status", "Protocol Beta", 0.0)
    hypo_sub = BindingHypothesisSet("Device Alpha", "SUBJECT", (), is_novel=True)
    hypo_obj = BindingHypothesisSet("Protocol Beta", "OBJECT", (), is_novel=True)

    cert, obs, deferred, prov_list, prov_rel, trusted_ctx = policy.evaluate(
        rec, att, hypo_sub, hypo_obj, sample_ontology, sample_capability_registry, contract
    )
    assert cert.status == AdmissionStatus.DEFER
    assert len(prov_list) == 2
    assert prov_rel is not None
    assert prov_rel.is_subject_provisional is True
    assert prov_rel.is_object_provisional is True
