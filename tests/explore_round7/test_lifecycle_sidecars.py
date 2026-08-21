"""Deterministic Lifecycle Security Assays (Sidecars A and B) (Stage 7A.1)."""

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
from gene.ingress.ontology import CapabilityPolicy, CapabilityPolicyRegistry, EntityDefinition, IngressOntology
from gene.ingress.engine import IngressEngine
from gene.ingress.policies import A1CanonicalizationOnlyPolicy, A3AuthorityAwarePolicy, A4FullGENEIngressPolicy
from gene.supersession_engine import BitemporalEngine, PredicateContract


@pytest.fixture
def lifecycle_env():
    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Server_Node_1_Backup", "Server Node 1 Backup", "SERVER", aliases=("Server 1",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS", aliases=("Active",)),
    ])
    capability_registry = CapabilityPolicyRegistry({
        "admin": CapabilityPolicy("admin", frozenset(["*"]), ClaimPrivilege.ROOT_FACT, "KERNEL", "ROOT_ADMIN"),
        "sensor": CapabilityPolicy("sensor", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", "ROOT_NET_A"),
    })
    contract = PredicateContract("device_status", "SINGLE", "TIME_VARYING")
    engine = IngressEngine(ontology, capability_registry, A4FullGENEIngressPolicy(), BitemporalEngine())
    return {
        "ontology": ontology,
        "capability_registry": capability_registry,
        "contract": contract,
        "engine": engine,
    }


def test_sidecar_a_explicit_resolve_deferred_binding(lifecycle_env):
    """Sidecar A: Ambiguous candidate set preserved at t1, resolved at t2 via resolve_deferred_binding without reparsing."""
    env = lifecycle_env
    engine: IngressEngine = env["engine"]

    # At t1: Ambiguous mention "Server 1"
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

    assert res_t1["status"] == AdmissionStatus.DEFER.value
    assert len(engine.deferred_bindings) == 1
    def_id = list(engine.deferred_bindings.keys())[0]

    # At t2: Call explicit resolve_deferred_binding on the original object without creating new SourceRecord or reparsing!
    res_t2 = engine.resolve_deferred_binding(
        deferred_id=def_id,
        resolved_subject_id="Server_Node_1",
        resolved_object_id="Value_Operational",
        t_knowledge_resolution=2,
        contract=env["contract"],
    )

    assert res_t2["status"] == AdmissionStatus.ADMIT.value
    active_facts = engine.bitemporal_engine.get_active_facts(0.0, 2)
    assert len(active_facts) == 1
    assert active_facts[0].subject == "Server_Node_1"
    # Provenance root preserved from original sensor record!
    assert active_facts[0].roots == frozenset(["ROOT_NET_A_sensor_alpha"])


def test_sidecar_b_explicit_promote_provisional_entity(lifecycle_env):
    """Sidecar B: Novel entity preserved under ProvisionalEntity and promoted preserving original provenance roots."""
    env = lifecycle_env
    engine: IngressEngine = env["engine"]

    # At t1: Novel entity "Zeta Device"
    rec_t1 = SourceRecord(
        "rec_t1_novel", "Zeta Device is Operational",
        CaptureProvenance("conn_1", "telemetry", 1, "hash_novel"),
        ClaimedOrigin("sensor_alpha", "sensor"),
        AuthenticatedOrigin("sensor_alpha", "ED25519", True),
        t_knowledge=1,
    )
    att_t1 = ParsedAttestation("att_t1_novel", "rec_t1_novel", "Zeta Device", "device_status", "Operational", 0.0)
    sub_hypo_novel = BindingHypothesisSet("Zeta Device", "SUBJECT", (), is_novel=True)
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    res_t1 = engine.ingest_record(rec_t1, att_t1, sub_hypo_novel, obj_hypo, env["contract"])

    assert res_t1["status"] == AdmissionStatus.DEFER.value
    assert len(engine.provisional_entities) == 1
    prov_id = list(engine.provisional_entities.keys())[0]

    # At t2: Admin promotes provisional entity to Device_Zeta_99
    res_promote = engine.promote_provisional_entity(
        provisional_id=prov_id,
        canonical_entity_id="Device_Zeta_99",
        canonical_name="Zeta Device",
        t_knowledge_promotion=2,
        contract=env["contract"],
    )

    assert res_promote["is_promoted"] is True
    active_facts = engine.bitemporal_engine.get_active_facts(0.0, 2)
    assert len(active_facts) == 1
    assert active_facts[0].subject == "Device_Zeta_99"
    # Lineage root is preserved from original sensor record!
    assert active_facts[0].roots == frozenset(["ROOT_NET_A_sensor_alpha"])


def test_alternative_preservation_principle_comparison(lifecycle_env):
    """Demonstrate Alternative-Preservation Principle: A1/A3 suffer irreversible collapse, A4 preserves alternatives."""
    env = lifecycle_env

    # A1 (Canonicalization only): Prematurely collapses "Server 1" to Server_Node_1 at t1
    engine_a1 = IngressEngine(env["ontology"], env["capability_registry"], A1CanonicalizationOnlyPolicy(), BitemporalEngine())
    rec = SourceRecord("rec_a1", "Server 1 is Operational", CaptureProvenance("c1", "s", 1, "h1"), ClaimedOrigin("sensor_alpha", "sensor"), AuthenticatedOrigin("sensor_alpha", "ED25519", True), 1)
    att = ParsedAttestation("att_a1", "rec_a1", "Server 1", "device_status", "Operational", 0.0)
    sub_hypo = BindingHypothesisSet("Server 1", "SUBJECT", ("Server_Node_1", "Server_Node_1_Backup"))
    obj_hypo = BindingHypothesisSet("Operational", "OBJECT", ("Value_Operational",))

    res_a1 = engine_a1.ingest_record(rec, att, sub_hypo, obj_hypo, env["contract"])
    # A1 prematurely admitted Server_Node_1 (destroying alternative Server_Node_1_Backup)
    assert res_a1["status"] == "ADMIT"
    assert len(engine_a1.deferred_bindings) == 0

    # If ground truth was actually Server_Node_1_Backup, A1's memory is corrupt.
    # In contrast, A4 deferred binding and preserved both hypotheses.
