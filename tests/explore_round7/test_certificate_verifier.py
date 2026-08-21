"""Exhaustive Combinatorial Adversarial Certificate Mutation Tests (Stage 7A.2)."""

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
)
from gene.ingress.ontology import (
    CapabilityPolicy,
    CapabilityPolicyRegistry,
    EntityDefinition,
    IngressOntology,
    LineageIndependenceRegistry,
)
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
        "sensor_1": CapabilityPolicy("sensor_1", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR"),
    })
    independence_registry = LineageIndependenceRegistry({
        "sensor_1": "ROOT_NET_1_sensor_1",
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
        "independence_registry": independence_registry,
        "contract": contract,
        "source_rec": source_rec,
        "parsed_att": parsed_att,
        "sub_hypo": sub_hypo,
        "obj_hypo": obj_hypo,
        "valid_obs": valid_obs,
        "valid_cert": valid_cert,
    }


def test_valid_certificate_passes(verifier_fixtures):
    f = verifier_fixtures
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        f["valid_obs"], f["ontology"], f["capability_registry"], f["contract"], f["valid_cert"], f["independence_registry"]
    )
    assert is_valid is True
    assert msg is None


@pytest.mark.parametrize("attack_type,mutate_fn", [
    ("MUTATE_PREDICATE", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation(f["valid_obs"].subject, "tampered_predicate", f["valid_obs"].obj, f["valid_obs"].t_valid_start, f["valid_obs"].t_valid_end, f["valid_obs"].t_knowledge, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_cert"])),
    ("MUTATE_TK_SPOOF", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation(f["valid_obs"].subject, f["valid_obs"].predicate, f["valid_obs"].obj, f["valid_obs"].t_valid_start, f["valid_obs"].t_valid_end, 999, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_cert"])),
    ("MUTATE_SUBJECT_BOUND", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation("Server_Node_FORGED", f["valid_obs"].predicate, f["valid_obs"].obj, f["valid_obs"].t_valid_start, f["valid_obs"].t_valid_end, f["valid_obs"].t_knowledge, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_cert"])),
    ("MUTATE_OBJECT_BOUND", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation(f["valid_obs"].subject, f["valid_obs"].predicate, "Value_FORGED", f["valid_obs"].t_valid_start, f["valid_obs"].t_valid_end, f["valid_obs"].t_knowledge, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_cert"])),
    ("MUTATE_FORGED_ROOTS", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], f["valid_obs"], AdmissionCertificate(AdmissionStatus.ADMIT, f["valid_cert"].binding_witness, lineage_roots=frozenset(["ROOT_FORGED"])))),
    ("MUTATE_EMPTY_WITNESS", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], f["valid_obs"], AdmissionCertificate(AdmissionStatus.ADMIT, binding_witness=None, lineage_roots=f["valid_obs"].lineage_roots))),
    ("MUTATE_START_TIME_MISMATCH", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation(f["valid_obs"].subject, f["valid_obs"].predicate, f["valid_obs"].obj, 99.0, f["valid_obs"].t_valid_end, f["valid_obs"].t_knowledge, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_cert"])),
])
def test_exhaustive_observation_and_certificate_mutations(verifier_fixtures, attack_type, mutate_fn):
    """Programmatic Exhaustive Adversarial Mutation Matrix: Asserts fail-closed rejection on every attack vector."""
    f = verifier_fixtures
    parsed_att, sub_hypo, obj_hypo, mutated_obs, mutated_cert = mutate_fn(f)

    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], parsed_att, sub_hypo, obj_hypo,
        mutated_obs, f["ontology"], f["capability_registry"], f["contract"], mutated_cert, f["independence_registry"]
    )
    assert is_valid is False, f"Attack '{attack_type}' was improperly admitted!"
    assert msg is not None
