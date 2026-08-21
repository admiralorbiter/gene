"""Deterministic Lifecycle Security Assays & Dual-Novel Status Laundering Tests (Stage 7A.3)."""

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
        "admin_user": CapabilityPolicy("admin_user", frozenset(["*"]), ClaimPrivilege.ROOT_FACT, "KERNEL", is_ontology_admin=True, can_disambiguate=True),
        "sensor_alpha": CapabilityPolicy("sensor_alpha", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", can_disambiguate=True),
        "unauthorized_user": CapabilityPolicy("unauthorized_user", frozenset(["user_feedback"]), ClaimPrivilege.ATTESTATION_ONLY, "WEB", is_ontology_admin=False, can_disambiguate=False),
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


def test_proof_carrying_resolve_deferred_binding(lifecycle_env):
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
    engine.ingest_record(rec_t1, att_t1, sub_hypo_t1, obj_hypo_t1, env["contract"])
    def_id = list(engine.deferred_bindings.keys())[0]

    disambiguating_rec = SourceRecord(
        "rec_disambig", "Disambiguation telemetry confirmed Server_Node_1",
        CaptureProvenance("conn_1", "telemetry", 2, "hash_dis"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=2,
    )

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


def test_dual_novel_entities_step_by_step_promotion_prevents_status_laundering(lifecycle_env):
    """Test step-by-step promotion of dual-novel relation (NovelA related_to NovelB).
    
    1. At t1: Both endpoints novel -> Stored as ProvisionalRelation(prov_A, prov_B).
    2. At t2: Admin promotes prov_A to Canon_A.
       CRITICAL INVARIANT: The relation is retargeted to (Canon_A, prov_B) and KEPT PROVISIONAL.
       Zero authoritative BitemporalFacts are created!
    3. At t3: Admin promotes prov_B to Canon_B.
       Now all endpoints are canonical -> Relation migrates to authoritative BitemporalFact(Canon_A, Canon_B).
    """
    env = lifecycle_env
    engine: IngressEngine = env["engine"]

    rec_dual = SourceRecord(
        "rec_dual", "Quantum Core Alpha connected to Quantum Switch Beta",
        CaptureProvenance("conn_1", "telemetry", 1, "hash_dual"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    att_dual = ParsedAttestation("att_dual", "rec_dual", "Quantum Core Alpha", "device_status", "Quantum Switch Beta", 0.0)
    hypo_sub_nov = BindingHypothesisSet("Quantum Core Alpha", "SUBJECT", (), is_novel=True)
    hypo_obj_nov = BindingHypothesisSet("Quantum Switch Beta", "OBJECT", (), is_novel=True)

    res_dual = engine.ingest_record(rec_dual, att_dual, hypo_sub_nov, hypo_obj_nov, env["contract"])
    assert res_dual["status"] == AdmissionStatus.DEFER.value
    assert len(engine.provisional_entities) == 2
    assert len(engine.provisional_relations) == 1

    prov_a_id = "prov_quantum_core_alpha"
    prov_b_id = "prov_quantum_switch_beta"

    admin_rec = SourceRecord("rec_admin", "Admin Promotion", CaptureProvenance("c", "ui", 2, "ha"), ClaimedOrigin("admin_user", "admin"), AuthenticatedOrigin("admin_user", "KERNEL", True), 2)

    # Step 1: Promote prov_A only
    cert_a = PromotionCertificate(prov_a_id, "Device_Core_Alpha", "Quantum Core Alpha", "DEVICE", admin_rec.record_id, "ADMIN_APPROVAL_A")
    res_a = engine.promote_provisional_entity(prov_a_id, "Device_Core_Alpha", "Quantum Core Alpha", admin_rec, cert_a)

    assert res_a["status"] == "ADMIT"
    assert res_a["is_promoted"] is True
    # Crucial Invariant: Zero authoritative facts created because prov_B is still provisional!
    assert len(res_a["migrated_fact_ids"]) == 0
    assert len(engine.bitemporal_engine.facts) == 0

    # Provisional relation is retargeted but remains provisional
    rel = list(engine.provisional_relations.values())[0]
    assert rel.subject_id == "Device_Core_Alpha"
    assert rel.object_id == prov_b_id
    assert rel.is_subject_provisional is False
    assert rel.is_object_provisional is True

    # Step 2: Promote prov_B
    admin_rec_3 = SourceRecord("rec_admin_3", "Admin Promotion B", CaptureProvenance("c", "ui", 3, "hb"), ClaimedOrigin("admin_user", "admin"), AuthenticatedOrigin("admin_user", "KERNEL", True), 3)
    cert_b = PromotionCertificate(prov_b_id, "Device_Switch_Beta", "Quantum Switch Beta", "DEVICE", admin_rec_3.record_id, "ADMIN_APPROVAL_B")
    res_b = engine.promote_provisional_entity(prov_b_id, "Device_Switch_Beta", "Quantum Switch Beta", admin_rec_3, cert_b)

    assert res_b["status"] == "ADMIT"
    assert res_b["is_promoted"] is True
    # Now all endpoints are canonical -> Migrated to authoritative fact!
    assert len(res_b["migrated_fact_ids"]) == 1
    assert len(engine.bitemporal_engine.facts) == 1

    active_facts = engine.bitemporal_engine.get_active_facts(0.0, 3)
    assert len(active_facts) == 1
    assert active_facts[0].subject == "Device_Core_Alpha"
    assert active_facts[0].obj == "Device_Switch_Beta"
    assert active_facts[0].roots == frozenset(["ROOT_NET_A_sensor_alpha"])  # Sensor provenance preserved!
