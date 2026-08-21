"""Comprehensive Adversarial Certificate Mutation Tests (Thread C)."""

import pytest
from gene.ingress.models import (
    AdmissionCertificate,
    AdmissionStatus,
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ClaimPrivilege,
    ClaimType,
    ParsedAttestation,
    SourceRecord,
    TrustedSourceContext,
)
from gene.ingress.ontology import CapabilityPolicy, CapabilityPolicyRegistry, EntityDefinition, IngressOntology
from gene.ingress.verifier import CertificateVerifier
from gene.supersession_engine import Observation, PredicateContract


@pytest.fixture
def verifier_fixtures():
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
        EntityDefinition("Value_Degraded", "Degraded", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", "ROOT_NET_1"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")

    source_rec = SourceRecord(
        "rec_100", "Server Node 1 is Operational",
        CaptureProvenance("conn_1", "channel_1", 1, "hash_100"),
        ClaimedOrigin("sensor_1", "sensor"),
        AuthenticatedOrigin("sensor_1", "ED25519", True),
        t_knowledge=1,
    )
    parsed_att = ParsedAttestation("att_100", "rec_100", "Server Node 1", "device_status", "Operational", 0.0, None)
    sub_hypo = BindingHypothesisSet("Server Node 1", "SUBJECT", ("Server_Node_1",))
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))
    trusted_ctx = TrustedSourceContext(
        authenticity="CRYPTOGRAPHIC_VERIFIED",
        authorization_scope=frozenset(["device_status"]),
        max_claim_privilege=ClaimPrivilege.ROOT_FACT,
        reliability_class="HIGH_PRECISION_SENSOR",
        independence_class="ROOT_NET_1_sensor_1",
    )

    valid_obs = Observation(
        subject="Server_Node_1",
        predicate="device_status",
        obj="Value_Operational",
        t_valid_start=0.0,
        t_valid_end=None,
        t_knowledge=1,
        source_id="sensor_1",
        origin_id="sensor_1",
        lineage_roots=frozenset(["ROOT_NET_1_sensor_1"]),
        observation_id="obs_100",
    )

    valid_cert = AdmissionCertificate(
        status=AdmissionStatus.ADMIT,
        binding_witness={"subject": "Server_Node_1", "object": "Value_Operational"},
        schema_witness="CANONICAL_SCHEMA",
        temporal_witness="[0.0, None)",
        auth_witness="AUTHORIZED_SCOPE",
        lineage_roots=frozenset(["ROOT_NET_1_sensor_1"]),
    )

    return {
        "ontology": ontology,
        "capability_registry": capability_registry,
        "contract": contract,
        "source_rec": source_rec,
        "parsed_att": parsed_att,
        "sub_hypo": sub_hypo,
        "obj_hypo": obj_hypo,
        "trusted_ctx": trusted_ctx,
        "valid_obs": valid_obs,
        "valid_cert": valid_cert,
    }


def test_valid_certificate_passes(verifier_fixtures):
    f = verifier_fixtures
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        f["valid_obs"], f["ontology"], f["capability_registry"], f["contract"], f["trusted_ctx"], f["valid_cert"]
    )
    assert is_valid is True
    assert msg is None


def test_mutation_predicate_mismatch_fails(verifier_fixtures):
    f = verifier_fixtures
    # Attack: Proposed observation predicate does not match parsed attestation
    mismatched_obs = Observation(
        subject="Server_Node_1",
        predicate="temperature_level",
        obj="Value_Operational",
        t_valid_start=0.0,
        t_knowledge=1,
        lineage_roots=frozenset(["ROOT_NET_1_sensor_1"]),
        observation_id="obs_bad_pred",
    )
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        mismatched_obs, f["ontology"], f["capability_registry"], f["contract"], f["trusted_ctx"], f["valid_cert"]
    )
    assert is_valid is False
    assert "predicate" in msg


def test_mutation_knowledge_time_spoofing_fails(verifier_fixtures):
    f = verifier_fixtures
    # Attack: Proposed observation claims transaction knowledge time t_k=999
    spoofed_tk_obs = Observation(
        subject="Server_Node_1",
        predicate="device_status",
        obj="Value_Operational",
        t_valid_start=0.0,
        t_knowledge=999,
        lineage_roots=frozenset(["ROOT_NET_1_sensor_1"]),
        observation_id="obs_bad_tk",
    )
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        spoofed_tk_obs, f["ontology"], f["capability_registry"], f["contract"], f["trusted_ctx"], f["valid_cert"]
    )
    assert is_valid is False
    assert "t_k" in msg


def test_mutation_privilege_escalation_fails(verifier_fixtures):
    f = verifier_fixtures
    # Attack: Trusted context has ATTESTATION_ONLY privilege, attempting root fact ADMIT
    restricted_ctx = TrustedSourceContext(
        authenticity="CRYPTOGRAPHIC_VERIFIED",
        authorization_scope=frozenset(["device_status"]),
        max_claim_privilege=ClaimPrivilege.ATTESTATION_ONLY,
        reliability_class="NEURAL_COGNITIVE_STEP",
        independence_class="ROOT_DERIVATION_1",
    )
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        f["valid_obs"], f["ontology"], f["capability_registry"], f["contract"], restricted_ctx, f["valid_cert"]
    )
    assert is_valid is False
    assert "cannot assert ROOT_FACT" in msg


def test_mutation_forged_lineage_roots_fails(verifier_fixtures):
    f = verifier_fixtures
    # Attack: Certificate claims independence root ROOT_FORGED instead of trusted context independence class
    forged_cert = AdmissionCertificate(
        status=AdmissionStatus.ADMIT,
        binding_witness={"subject": "Server_Node_1", "object": "Value_Operational"},
        lineage_roots=frozenset(["ROOT_FORGED"]),
    )
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        f["valid_obs"], f["ontology"], f["capability_registry"], f["contract"], f["trusted_ctx"], forged_cert
    )
    assert is_valid is False
    assert "lineage roots" in msg
