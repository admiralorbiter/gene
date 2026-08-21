"""Exhaustive Combinatorial Adversarial Certificate Mutation Tests across Admission, Resolution, and Promotion (Stage 7A.3)."""

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
    DeferredBinding,
    ParsedAttestation,
    PromotionCertificate,
    ProvisionalEntity,
    ProvisionalRelation,
    ResolutionCertificate,
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
        EntityDefinition("Server_Node_1_Backup", "Server Node 1 Backup", "SERVER"),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
        EntityDefinition("Value_Degraded", "Degraded", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "sensor_1": CapabilityPolicy("sensor_1", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", can_disambiguate=True),
        "admin_1": CapabilityPolicy("admin_1", frozenset(["*"]), ClaimPrivilege.ROOT_FACT, "KERNEL", is_ontology_admin=True, can_disambiguate=True),
        "unprivileged_guest": CapabilityPolicy("unprivileged_guest", frozenset(["feedback"]), ClaimPrivilege.ATTESTATION_ONLY, "WEB", is_ontology_admin=False, can_disambiguate=False),
    })
    independence_registry = LineageIndependenceRegistry({
        "sensor_1": "ROOT_NET_1_sensor_1",
        "admin_1": "ROOT_ADMIN_admin_1",
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

    valid_admission_cert = AdmissionCertificate(
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
        "valid_admission_cert": valid_admission_cert,
    }


def test_valid_admission_certificate_passes(verifier_fixtures):
    f = verifier_fixtures
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], f["parsed_att"], f["sub_hypo"], f["obj_hypo"],
        f["valid_obs"], f["ontology"], f["capability_registry"], f["contract"], f["valid_admission_cert"], f["independence_registry"]
    )
    assert is_valid is True
    assert msg is None


@pytest.mark.parametrize("attack_name,mutate_fn", [
    ("MUTATE_PREDICATE", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation(f["valid_obs"].subject, "tampered_predicate", f["valid_obs"].obj, f["valid_obs"].t_valid_start, f["valid_obs"].t_valid_end, f["valid_obs"].t_knowledge, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_admission_cert"])),
    ("MUTATE_TK_SPOOF", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation(f["valid_obs"].subject, f["valid_obs"].predicate, f["valid_obs"].obj, f["valid_obs"].t_valid_start, f["valid_obs"].t_valid_end, 999, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_admission_cert"])),
    ("MUTATE_SUBJECT_OUT_OF_HYPOTHESIS", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation("Server_Node_FORGED", f["valid_obs"].predicate, f["valid_obs"].obj, f["valid_obs"].t_valid_start, f["valid_obs"].t_valid_end, f["valid_obs"].t_knowledge, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_admission_cert"])),
    ("MUTATE_OBJECT_OUT_OF_HYPOTHESIS", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation(f["valid_obs"].subject, f["valid_obs"].predicate, "Value_FORGED", f["valid_obs"].t_valid_start, f["valid_obs"].t_valid_end, f["valid_obs"].t_knowledge, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_admission_cert"])),
    ("MUTATE_FORGED_ROOTS", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], f["valid_obs"], AdmissionCertificate(AdmissionStatus.ADMIT, f["valid_admission_cert"].binding_witness, lineage_roots=frozenset(["ROOT_FORGED"])))),
    ("MUTATE_EMPTY_WITNESS", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], f["valid_obs"], AdmissionCertificate(AdmissionStatus.ADMIT, binding_witness=None, lineage_roots=f["valid_obs"].lineage_roots))),
    ("MUTATE_START_TIME_MISMATCH", lambda f: (f["parsed_att"], f["sub_hypo"], f["obj_hypo"], Observation(f["valid_obs"].subject, f["valid_obs"].predicate, f["valid_obs"].obj, 99.0, f["valid_obs"].t_valid_end, f["valid_obs"].t_knowledge, f["valid_obs"].source_id, f["valid_obs"].origin_id, f["valid_obs"].lineage_roots, "obs_bad"), f["valid_admission_cert"])),
])
def test_exhaustive_admission_certificate_mutations(verifier_fixtures, attack_name, mutate_fn):
    f = verifier_fixtures
    parsed_att, sub_hypo, obj_hypo, mutated_obs, mutated_cert = mutate_fn(f)
    is_valid, msg = CertificateVerifier.verify(
        f["source_rec"], parsed_att, sub_hypo, obj_hypo,
        mutated_obs, f["ontology"], f["capability_registry"], f["contract"], mutated_cert, f["independence_registry"]
    )
    assert is_valid is False
    assert msg is not None


@pytest.mark.parametrize("attack_name,sub_target,obj_target,cert_mutator", [
    ("OUT_OF_CANDIDATE_SUBJECT", "Server_Node_UNKNOWN", "Value_Operational", lambda c: c),
    ("MISMATCHED_RECORD_ID", "Server_Node_1", "Value_Operational", lambda c: ResolutionCertificate(c.deferred_id, c.chosen_subject_id, c.chosen_object_id, "rec_FORGED", c.resolution_witness, c.lineage_roots)),
    ("FORGED_LINEAGE_ROOTS", "Server_Node_1", "Value_Operational", lambda c: ResolutionCertificate(c.deferred_id, c.chosen_subject_id, c.chosen_object_id, c.disambiguating_source_record_id, c.resolution_witness, frozenset(["ROOT_FORGED"]))),
    ("EMPTY_RESOLUTION_WITNESS", "Server_Node_1", "Value_Operational", lambda c: ResolutionCertificate(c.deferred_id, c.chosen_subject_id, c.chosen_object_id, c.disambiguating_source_record_id, "", c.lineage_roots)),
])
def test_exhaustive_resolution_certificate_mutations(verifier_fixtures, attack_name, sub_target, obj_target, cert_mutator):
    """Combinatorial Adversarial Matrix for ResolutionCertificate."""
    f = verifier_fixtures
    deferred = DeferredBinding(
        deferred_id="def_100",
        source_record_id=f["source_rec"].record_id,
        attestation_id=f["parsed_att"].attestation_id,
        subject_hypotheses=BindingHypothesisSet("Server 1", "SUBJECT", ("Server_Node_1", "Server_Node_1_Backup")),
        predicate="device_status",
        object_hypotheses=BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",)),
        t_valid_start=0.0,
    )
    dis_rec = SourceRecord("rec_dis", "Disambig", CaptureProvenance("c", "s", 2, "h"), ClaimedOrigin("sensor_1", "sensor"), AuthenticatedOrigin("sensor_1", "ED25519", True), 2)
    base_cert = ResolutionCertificate("def_100", sub_target, obj_target, dis_rec.record_id, "VALID_WITNESS", frozenset(["ROOT_NET_1_sensor_1"]))
    mutated_cert = cert_mutator(base_cert)

    is_valid, msg = CertificateVerifier.verify_resolution(
        deferred, sub_target, obj_target, dis_rec, f["source_rec"],
        f["capability_registry"], f["ontology"], mutated_cert, f["independence_registry"]
    )
    assert is_valid is False
    assert msg is not None


@pytest.mark.parametrize("attack_name,target_canon_id,canon_name,ent_type,cert_mutator", [
    ("CANONICAL_ID_COLLISION", "Server_Node_1", "Server Node 1", "SERVER", lambda c: c),
    ("MISMATCHED_AUTHORITY_RECORD_ID", "Device_Zeta_99", "Zeta Device", "DEVICE", lambda c: PromotionCertificate(c.provisional_id, c.canonical_entity_id, c.canonical_name, c.entity_type, "rec_FORGED", c.authority_witness)),
    ("EMPTY_AUTHORITY_WITNESS", "Device_Zeta_99", "Zeta Device", "DEVICE", lambda c: PromotionCertificate(c.provisional_id, c.canonical_entity_id, c.canonical_name, c.entity_type, c.promotion_authority_record_id, "")),
])
def test_exhaustive_promotion_certificate_mutations(verifier_fixtures, attack_name, target_canon_id, canon_name, ent_type, cert_mutator):
    """Combinatorial Adversarial Matrix for PromotionCertificate."""
    f = verifier_fixtures
    prov = ProvisionalEntity("prov_zeta", "Zeta Device", f["source_rec"].record_id, 1)
    admin_rec = SourceRecord("rec_adm", "Promote", CaptureProvenance("c", "ui", 2, "h"), ClaimedOrigin("admin_1", "admin"), AuthenticatedOrigin("admin_1", "KERNEL", True), 2)
    base_cert = PromotionCertificate("prov_zeta", target_canon_id, canon_name, ent_type, admin_rec.record_id, "VALID_ADMIN_APPROVAL")
    mutated_cert = cert_mutator(base_cert)

    is_valid, msg = CertificateVerifier.verify_promotion(
        prov, target_canon_id, canon_name, ent_type, admin_rec,
        f["capability_registry"], f["ontology"], mutated_cert, [], {f["source_rec"].record_id: f["source_rec"]}, f["independence_registry"]
    )
    assert is_valid is False
    assert msg is not None
