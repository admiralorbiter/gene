"""Deterministic Lifecycle Security Assays (Sidecars A and B) (Thread C)."""

import pytest
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


@pytest.fixture
def lifecycle_env():
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER"),
        EntityDefinition("Server_Node_1_Backup", "Server Node 1 Backup", "SERVER"),
        EntityDefinition("Value_Operational", "Operational", "STATUS"),
        EntityDefinition("Value_Offline", "Offline", "STATUS"),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "admin": CapabilityPolicy("admin", frozenset(["*"]), "ROOT_FACT"),
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status"]), "ROOT_FACT"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    engine = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    return {
        "ontology": ontology,
        "capability_registry": capability_registry,
        "contract": contract,
        "engine": engine,
    }


def test_sidecar_a_deferred_binding_resolution(lifecycle_env):
    """Sidecar A: Ambiguous candidate set preserved at t1, resolved at t2 without reparsing."""
    env = lifecycle_env
    engine: IngressEngine = env["engine"]

    # At t1: Ambiguous mention "Server 1" matching both Server_Node_1 and Server_Node_1_Backup
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
    src_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "ROOT_NET_A")

    res_t1 = engine.ingest_record(rec_t1, att_t1, sub_hypo_t1, obj_hypo_t1, env["contract"], src_ctx)

    # Must be DEFER, zero facts admitted into bitemporal engine
    assert res_t1["status"] == AdmissionStatus.DEFER.value
    assert len(engine.deferred_bindings) == 1
    assert len(engine.bitemporal_engine.events) == 0

    # At t2: Subsequent evidence prunes candidate set to {Server_Node_1}
    def_item = list(engine.deferred_bindings.values())[0]
    resolved_sub_hypo = BindingHypothesisSet(def_item.subject_hypotheses.mention_span, "SUBJECT", ("Server_Node_1",))
    
    rec_t2 = SourceRecord(
        "rec_t2", "Disambiguation: Target was Primary Server Node 1",
        CaptureProvenance("conn_1", "telemetry", 2, "hash_t2"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=2,
    )
    att_t2 = ParsedAttestation("att_t2", "rec_t2", "Server Node 1", "device_status", "Operational", 0.0)
    res_t2 = engine.ingest_record(rec_t2, att_t2, resolved_sub_hypo, obj_hypo_t1, env["contract"], src_ctx)

    # Must now be ADMIT and instantiate authoritative occurrence event
    assert res_t2["status"] == AdmissionStatus.ADMIT.value
    assert len(engine.bitemporal_engine.events) >= 1
    active_facts = engine.bitemporal_engine.get_active_facts(0.0, 2)
    assert len(active_facts) == 1
    assert active_facts[0].subject == "Server_Node_1"


def test_sidecar_b_provisional_entity_promotion(lifecycle_env):
    """Sidecar B: Novel entity preserved as ProvisionalEntity, promoted preserving provenance."""
    env = lifecycle_env
    engine: IngressEngine = env["engine"]

    # At t1: Novel entity "Zeta Device" not in ontology
    rec_t1_novel = SourceRecord(
        "rec_t1_novel", "Zeta Device is Operational",
        CaptureProvenance("conn_1", "telemetry", 1, "hash_novel"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    att_t1 = ParsedAttestation("att_t1_novel", "rec_t1_novel", "Zeta Device", "device_status", "Operational", 0.0)
    sub_hypo_novel = BindingHypothesisSet("Zeta Device", "SUBJECT", (), is_novel=True)
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))
    src_ctx = SourceContext("CRYPTOGRAPHIC_VERIFIED", frozenset(["device_status"]), "HIGH_PRECISION_SENSOR", "ROOT_NET_A")

    res_t1 = engine.ingest_record(rec_t1_novel, att_t1, sub_hypo_novel, obj_hypo, env["contract"], src_ctx)

    # Must be DEFER with ProvisionalEntity created
    assert res_t1["status"] == AdmissionStatus.DEFER.value
    assert len(engine.provisional_entities) == 1
    prov_ent = list(engine.provisional_entities.values())[0]
    assert prov_ent.provisional_id == "prov_zeta_device"
    assert len(engine.bitemporal_engine.events) == 0

    # At t2: Admin promotes Zeta Device into canonical ontology
    canonical_zeta = EntityDefinition(
        entity_id="Device_Zeta_99",
        canonical_name="Zeta Device",
        entity_type="DEVICE",
        aliases=("Zeta", "Zeta_Device"),
    )
    env["ontology"].register_entity(canonical_zeta)

    # Subsequent re-evaluation with updated ontology admits canonical fact
    sub_hypo_promoted = BindingHypothesisSet("Zeta Device", "SUBJECT", ("Device_Zeta_99",))
    rec_t2 = SourceRecord(
        "rec_t2_promoted", "Zeta Device registration confirmed",
        CaptureProvenance("conn_1", "admin_channel", 2, "hash_admin"),
        ClaimedOrigin("admin_1", "admin"),
        AuthenticatedOrigin("admin_1", "KERNEL_LOCAL", True),
        t_knowledge=2,
    )
    att_t2 = ParsedAttestation("att_t2_promoted", "rec_t2_promoted", "Zeta Device", "device_status", "Operational", 0.0)
    res_t2 = engine.ingest_record(rec_t2, att_t2, sub_hypo_promoted, obj_hypo, env["contract"], src_ctx)

    assert res_t2["status"] == AdmissionStatus.ADMIT.value
    active_facts = engine.bitemporal_engine.get_active_facts(0.0, 2)
    assert len(active_facts) == 1
    assert active_facts[0].subject == "Device_Zeta_99"
    # Provenance root preserved from original sensor context
    assert active_facts[0].roots == frozenset(["ROOT_NET_A"])
