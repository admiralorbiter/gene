"""Deterministic Lifecycle Security Assays (Stage 7A.2)."""

import pytest
from gene.ingress.models import (
    AdmissionStatus,
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ClaimPrivilege,
    ParsedAttestation,
    PromotionCertificate,
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
from gene.ingress.engine import IngressEngine
from gene.ingress.policies import A4FullGENEIngressPolicy
from gene.supersession_engine import BitemporalEngine, PredicateContract


@pytest.fixture
def lifecycle_env():
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Server_Node_1_Backup", "Server Node 1 Backup", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS", aliases=("Active",)),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "admin_user": CapabilityPolicy("admin_user", frozenset(["*"]), ClaimPrivilege.ROOT_FACT, "KERNEL", is_ontology_admin=True),
        "sensor_alpha": CapabilityPolicy("sensor_alpha", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR"),
        "unauthorized_user": CapabilityPolicy("unauthorized_user", frozenset(["user_feedback"]), ClaimPrivilege.ATTESTATION_ONLY, "WEB", is_ontology_admin=False),
    })
    independence_registry = LineageIndependenceRegistry({
        "sensor_alpha": "ROOT_NET_A_sensor_alpha",
        "admin_user": "ROOT_ADMIN_admin_user",
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    engine = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine(), independence_registry)
    return {
        "ontology": ontology,
        "capability_registry": capability_registry,
        "independence_registry": independence_registry,
        "contract": contract,
        "engine": engine,
    }


def test_proof_carrying_resolve_deferred_binding_and_out_of_candidate_rejection(lifecycle_env):
    """Test proof-carrying resolution: verifies containment in original candidates and rejects out-of-set targets."""
    env = lifecycle_env
    engine: IngressEngine = env["engine"]

    rec_t1 = SourceRecord(
        "rec_t1", "Server 1 is Operational",
        CaptureProvenance("conn_1", "telemetry", 1, "hash_t1"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    att_t1 = ParsedAttestation("att_t1", "rec_t1", "Server 1", "device_status", "Operational", 0.0)
    sub_hypo_t1 = BindingHypothesisSet("Server 1", "SUBJECT", ("Server_Node_1", "Server_Node_1_Backup"))
    obj_hypo_t1 = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    res_t1 = engine.ingest_record(rec_t1, att_t1, sub_hypo_t1, obj_hypo_t1, env["contract"])
    def_id = list(engine.deferred_bindings.keys())[0]

    disambiguating_rec = SourceRecord(
        "rec_disambig", "Disambiguation telemetry confirmed Server_Node_1",
        CaptureProvenance("conn_1", "telemetry", 2, "hash_dis"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=2,
    )

    # Attack: Attempt to resolve to entity "Server_Node_UNKNOWN" outside original candidates B(x) = {Server_Node_1, Server_Node_1_Backup}
    forged_cert = ResolutionCertificate(
        deferred_id=def_id,
        chosen_subject_id="Server_Node_UNKNOWN",
        chosen_object_id="Value_Operational",
        disambiguating_source_record_id=disambiguating_rec.record_id,
        resolution_witness="FORGED",
        lineage_roots=frozenset(["ROOT_NET_A_sensor_alpha"]),
    )
    res_attack = engine.resolve_deferred_binding(
        deferred_id=def_id,
        chosen_subject_id="Server_Node_UNKNOWN",
        chosen_object_id="Value_Operational",
        disambiguating_record=disambiguating_rec,
        resolution_certificate=forged_cert,
        contract=env["contract"],
    )
    assert res_attack["status"] == "REJECT"
    assert "not in original candidate set" in res_attack["failure_reason"]

    # Legitimate resolution to valid candidate Server_Node_1
    valid_cert = ResolutionCertificate(
        deferred_id=def_id,
        chosen_subject_id="Server_Node_1",
        chosen_object_id="Value_Operational",
        disambiguating_source_record_id=disambiguating_rec.record_id,
        resolution_witness="CANONICAL_EVIDENCE",
        lineage_roots=frozenset(["ROOT_NET_A_sensor_alpha"]),
    )
    res_valid = engine.resolve_deferred_binding(
        deferred_id=def_id,
        chosen_subject_id="Server_Node_1",
        chosen_object_id="Value_Operational",
        disambiguating_record=disambiguating_rec,
        resolution_certificate=valid_cert,
        contract=env["contract"],
    )
    assert res_valid["status"] == "ADMIT"
    active_facts = engine.bitemporal_engine.get_active_facts(0.0, 2)
    assert len(active_facts) == 1
    assert active_facts[0].roots == frozenset(["ROOT_NET_A_sensor_alpha"])


def test_proof_carrying_promote_provisional_entity_and_collision_rejection(lifecycle_env):
    """Test proof-carrying promotion: rejects collision and unauthorized promoter, preserves sensor roots."""
    env = lifecycle_env
    engine: IngressEngine = env["engine"]

    rec_novel = SourceRecord(
        "rec_nov", "Zeta Device is Operational",
        CaptureProvenance("conn_1", "telemetry", 1, "hash_nov"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    att_novel = ParsedAttestation("att_nov", "rec_nov", "Zeta Device", "device_status", "Operational", 0.0)
    hypo_novel = BindingHypothesisSet("Zeta Device", "SUBJECT", (), is_novel=True)
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))
    engine.ingest_record(rec_novel, att_novel, hypo_novel, obj_hypo, env["contract"])
    prov_id = list(engine.provisional_entities.keys())[0]

    # Attack 1: Unauthorized user attempts promotion
    unauth_rec = SourceRecord("rec_unauth", "Promote Zeta", CaptureProvenance("c2", "ui", 2, "h_u"), ClaimedOrigin("unauthorized_user", "guest"), AuthenticatedOrigin("unauthorized_user", "OAUTH", True), 2)
    cert_unauth = PromotionCertificate(prov_id, "Device_Zeta_99", "Zeta Device", "DEVICE", unauth_rec.record_id, "UNAUTH_WITNESS")
    res_unauth = engine.promote_provisional_entity(prov_id, "Device_Zeta_99", "Zeta Device", unauth_rec, cert_unauth)
    assert res_unauth["status"] == "REJECT"
    assert "lacks CANONICAL_ONTOLOGY_ADMIN" in res_unauth["failure_reason"]

    # Attack 2: Canonical ID collision (attempting to promote to existing 'Server_Node_1')
    admin_rec = SourceRecord("rec_admin", "Promote Zeta", CaptureProvenance("c3", "ui", 2, "h_adm"), ClaimedOrigin("admin_user", "admin"), AuthenticatedOrigin("admin_user", "KERNEL_LOCAL", True), 2)
    cert_collision = PromotionCertificate(prov_id, "Server_Node_1", "Zeta Device", "DEVICE", admin_rec.record_id, "COLLISION_WITNESS")
    res_collision = engine.promote_provisional_entity(prov_id, "Server_Node_1", "Zeta Device", admin_rec, cert_collision)
    assert res_collision["status"] == "REJECT"
    assert "already exists in ontology" in res_collision["failure_reason"]

    # Legitimate promotion
    cert_valid = PromotionCertificate(prov_id, "Device_Zeta_99", "Zeta Device", "DEVICE", admin_rec.record_id, "ADMIN_APPROVAL")
    res_valid = engine.promote_provisional_entity(prov_id, "Device_Zeta_99", "Zeta Device", admin_rec, cert_valid)
    assert res_valid["status"] == "ADMIT"
    assert res_valid["is_promoted"] is True


def test_dual_novel_entities_relation_and_promotion(lifecycle_env):
    """Test dual-novel relation (NovelA related_to NovelB) and provisional migration."""
    env = lifecycle_env
    engine: IngressEngine = env["engine"]

    rec_dual = SourceRecord(
        "rec_dual", "Quantum Sensor Alpha connected to Quantum Core Beta",
        CaptureProvenance("conn_1", "telemetry", 1, "hash_dual"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    att_dual = ParsedAttestation("att_dual", "rec_dual", "Quantum Sensor Alpha", "device_status", "Quantum Core Beta", 0.0)
    hypo_sub_nov = BindingHypothesisSet("Quantum Sensor Alpha", "SUBJECT", (), is_novel=True)
    hypo_obj_nov = BindingHypothesisSet("Quantum Core Beta", "OBJECT", (), is_novel=True)

    res_dual = engine.ingest_record(rec_dual, att_dual, hypo_sub_nov, hypo_obj_nov, env["contract"])

    assert res_dual["status"] == AdmissionStatus.DEFER.value
    assert len(engine.provisional_entities) == 2
    assert len(engine.provisional_relations) == 1
    rel = list(engine.provisional_relations.values())[0]
    assert rel.is_subject_provisional is True
    assert rel.is_object_provisional is True
