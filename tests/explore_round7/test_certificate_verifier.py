"""Deterministic Mutation Testing for CertificateVerifier (Thread C)."""

import pytest
from gene.ingress.models import (
    AdmissionCertificate,
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
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status"]), "ROOT_FACT"),
        "guest": CapabilityPolicy("guest", frozenset(["device_status"]), "ATTESTATION_ONLY"),
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
    src_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "ROOT_1")
    
    valid_obs = Observation(
        subject="Server_Node_1",
        predicate="device_status",
        obj="Value_Operational",
        t_valid_start=0.0,
        t_valid_end=None,
        t_knowledge=1,
        source_id="sensor_1",
        origin_id="sensor_1",
        lineage_roots=frozenset(["ROOT_1"]),
        observation_id="obs_100",
    )
    
    valid_cert = AdmissionCertificate(
        status=AdmissionStatus.ADMIT,
        binding_witness={"subject": "Server_Node_1", "object": "Value_Operational"},
        schema_witness="CANONICAL_SCHEMA",
        temporal_witness="[0.0, None)",
        auth_witness="AUTHORIZED_SCOPE",
        lineage_roots=frozenset(["ROOT_1"]),
    )
    
    return {
        "ontology": ontology,
        "capability_registry": capability_registry,
        "contract": contract,
        "source_rec": source_rec,
        "parsed_att": parsed_att,
        "sub_hypo": sub_hypo,
        "obj_hypo": obj_hypo,
        "src_ctx": src_ctx,
        "valid_obs": valid_obs,
        "valid_cert": valid_cert,
    }


def test_valid_certificate_passes_verification(verifier_fixtures):
    f = verifier_fixtures
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        f["valid_obs"], f["ontology"], f["capability_registry"], f["contract"], f["src_ctx"], f["valid_cert"]
    )
    assert is_valid is True
    assert msg is None


def test_mutation_tampered_binding_witness_fails(verifier_fixtures):
    f = verifier_fixtures
    # Attack: Certificate claims subject is Server_Node_1, but proposed observation binds unknown Server_Node_99
    tampered_obs = Observation(
        subject="Server_Node_99",
        predicate="device_status",
        obj="Value_Operational",
        t_valid_start=0.0,
        observation_id="obs_tampered",
    )
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        tampered_obs, f["ontology"], f["capability_registry"], f["contract"], f["src_ctx"], f["valid_cert"]
    )
    assert is_valid is False
    assert "does not match" in msg


def test_mutation_out_of_hypothesis_binding_fails(verifier_fixtures):
    f = verifier_fixtures
    # Attack: Certificate binds Value_Degraded, which was not in candidate hypotheses
    tampered_cert = AdmissionCertificate(
        status=AdmissionStatus.ADMIT,
        binding_witness={"subject": "Server_Node_1", "object": "Value_Degraded"},
        lineage_roots=frozenset(["ROOT_1"]),
    )
    tampered_obs = Observation(
        subject="Server_Node_1",
        predicate="device_status",
        obj="Value_Degraded",
        t_valid_start=0.0,
        observation_id="obs_tampered2",
    )
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        tampered_obs, f["ontology"], f["capability_registry"], f["contract"], f["src_ctx"], tampered_cert
    )
    assert is_valid is False
    assert "not in object candidate hypothesis set" in msg


def test_mutation_unauthorized_scope_fails(verifier_fixtures):
    f = verifier_fixtures
    # Attack: SourceContext has restricted scope, attempting to admit unpermitted predicate
    restricted_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["temperature_only"]), "HIGH_PRECISION_SENSOR", "ROOT_1")
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        f["valid_obs"], f["ontology"], f["capability_registry"], f["contract"], restricted_ctx, f["valid_cert"]
    )
    assert is_valid is False
    assert "lacks authorization scope" in msg


def test_mutation_empty_lineage_roots_fails(verifier_fixtures):
    f = verifier_fixtures
    # Attack: Certificate with empty lineage roots (fabricating rootless truth)
    rootless_cert = AdmissionCertificate(
        status=AdmissionStatus.ADMIT,
        binding_witness={"subject": "Server_Node_1", "object": "Value_Operational"},
        lineage_roots=frozenset(),
    )
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        f["valid_obs"], f["ontology"], f["capability_registry"], f["contract"], f["src_ctx"], rootless_cert
    )
    assert is_valid is False
    assert "declare non-empty lineage roots" in msg
