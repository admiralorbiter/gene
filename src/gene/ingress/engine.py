"""Epistemic Ingress Engine (Round 7)."""

from __future__ import annotations

from typing import Any, Optional

from gene.ingress.models import (
    AdmissionCertificate,
    AdmissionStatus,
    BindingHypothesisSet,
    DeferredBinding,
    ParsedAttestation,
    ProvisionalEntity,
    ProvisionalRelation,
    SourceContext,
    SourceRecord,
)
from gene.ingress.ontology import CapabilityPolicyRegistry, IngressOntology
from gene.ingress.policies import A4FullGENEIngressPolicy, IngressPolicy
from gene.ingress.verifier import CertificateVerifier
from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    Observation,
    PredicateContract,
    TemporalEvent,
    adjudicate_observation,
)


class IngressEngine:
    """Master runtime coordinator for Epistemic Ingress & Write Admission."""

    def __init__(
        self,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        policy: Optional[IngressPolicy] = None,
        bitemporal_engine: Optional[BitemporalEngine] = None,
    ):
        self.ontology = ontology
        self.capability_registry = capability_registry
        self.policy: IngressPolicy = policy or A4FullGENEIngressPolicy()
        self.bitemporal_engine: BitemporalEngine = bitemporal_engine or BitemporalEngine()

        # Ingress state stores
        self.source_records: dict[str, SourceRecord] = {}
        self.parsed_attestations: dict[str, ParsedAttestation] = {}
        self.deferred_bindings: dict[str, DeferredBinding] = {}
        self.provisional_entities: dict[str, ProvisionalEntity] = {}
        self.provisional_relations: dict[str, ProvisionalRelation] = {}
        self.certificates: dict[str, AdmissionCertificate] = {}

    def ingest_record(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        contract: PredicateContract,
        source_context: SourceContext,
    ) -> dict[str, Any]:
        """Ingest a parsed attestation, evaluate admission policy, verify certificate, and adjudicate state."""
        self.source_records[source_record.record_id] = source_record
        self.parsed_attestations[parsed_attestation.attestation_id] = parsed_attestation

        cert, obs, deferred, prov = self.policy.evaluate(
            source_record=source_record,
            parsed_attestation=parsed_attestation,
            subject_hypotheses=subject_hypotheses,
            object_hypotheses=object_hypotheses,
            ontology=self.ontology,
            capability_registry=self.capability_registry,
            contract=contract,
            source_context=source_context,
        )

        self.certificates[source_record.record_id] = cert

        # For proof-carrying policies (e.g. A4), verify certificate independently
        if isinstance(self.policy, A4FullGENEIngressPolicy):
            is_valid, failure_msg = CertificateVerifier.verify(
                source_record=source_record,
                parsed_attestation=parsed_attestation,
                subject_hypotheses=subject_hypotheses,
                object_hypotheses=object_hypotheses,
                proposed_observation=obs,
                ontology=self.ontology,
                capability_registry=self.capability_registry,
                contract=contract,
                source_context=source_context,
                certificate=cert,
            )

            if not is_valid:
                # Certificate verification failed -> Fail-Closed Rejection
                rejection_cert = AdmissionCertificate(
                    status=AdmissionStatus.REJECT,
                    rejection_cause=f"CERTIFICATE_VERIFICATION_FAILED: {failure_msg}",
                )
                self.certificates[source_record.record_id] = rejection_cert
                return {
                    "status": AdmissionStatus.REJECT.value,
                    "certificate": rejection_cert,
                    "admitted_observation": None,
                    "events": [],
                    "failure_reason": failure_msg,
                }

        # Handle admission action
        events: list[TemporalEvent] = []
        if cert.status == AdmissionStatus.ADMIT and obs is not None:
            fid = f"fact_{source_record.record_id}"
            b_fact = BitemporalFact(
                fact_id=fid,
                subject=obs.subject,
                predicate=obs.predicate,
                obj=obs.obj,
                roots=obs.lineage_roots,
                source_id=obs.source_id,
                origin_id=obs.origin_id,
            )
            self.bitemporal_engine.register_fact(b_fact)

            events = adjudicate_observation(
                obs=obs,
                engine=self.bitemporal_engine,
                contract=contract,
                new_fact_id=fid,
            )
            for ev in events:
                self.bitemporal_engine.record_event(ev)

        elif cert.status == AdmissionStatus.DEFER:
            if deferred:
                self.deferred_bindings[deferred.deferred_id] = deferred
            if prov:
                self.provisional_entities[prov.provisional_id] = prov

        return {
            "status": cert.status.value,
            "certificate": cert,
            "admitted_observation": obs,
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.value,
                    "target_fact_id": e.target_fact_id,
                    "secondary_fact_id": e.secondary_fact_id,
                    "t_knowledge": e.t_knowledge,
                    "t_valid_start": e.t_valid_start,
                }
                for e in events
            ],
            "failure_reason": None,
        }
