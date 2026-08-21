"""Epistemic Ingress Engine (Round 7)."""

from __future__ import annotations

from typing import Any, Optional, Tuple

from gene.ingress.models import (
    AdmissionCertificate,
    AdmissionStatus,
    BindingHypothesisSet,
    ClaimPrivilege,
    ClaimType,
    DeferredBinding,
    ParsedAttestation,
    ProvisionalEntity,
    ProvisionalRelation,
    SourceRecord,
    TrustedSourceContext,
)
from gene.ingress.ontology import (
    CapabilityPolicyRegistry,
    EntityDefinition,
    IngressOntology,
    derive_trusted_source_context,
)
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
    ) -> dict[str, Any]:
        """Ingest a parsed attestation, evaluate admission policy, verify certificate, and adjudicate state."""
        self.source_records[source_record.record_id] = source_record
        self.parsed_attestations[parsed_attestation.attestation_id] = parsed_attestation

        cert, obs, deferred, prov, prov_rel, trusted_ctx = self.policy.evaluate(
            source_record=source_record,
            parsed_attestation=parsed_attestation,
            subject_hypotheses=subject_hypotheses,
            object_hypotheses=object_hypotheses,
            ontology=self.ontology,
            capability_registry=self.capability_registry,
            contract=contract,
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
                trusted_context=trusted_ctx,
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
            if prov_rel:
                self.provisional_relations[prov_rel.relation_id] = prov_rel

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

    def resolve_deferred_binding(
        self,
        deferred_id: str,
        resolved_subject_id: Optional[str] = None,
        resolved_object_id: Optional[str] = None,
        t_knowledge_resolution: int = 2,
        contract: Optional[PredicateContract] = None,
    ) -> dict[str, Any]:
        """Resolve an existing DeferredBinding under subsequent evidence without reparsing the raw text.
        
        Preserves original SourceRecord capture provenance and independence roots.
        """
        if deferred_id not in self.deferred_bindings:
            raise KeyError(f"DeferredBinding '{deferred_id}' not found in store.")

        deferred = self.deferred_bindings[deferred_id]
        if deferred.is_resolved:
            raise ValueError(f"DeferredBinding '{deferred_id}' is already resolved.")

        original_source_rec = self.source_records[deferred.source_record_id]
        original_att = self.parsed_attestations[deferred.attestation_id]

        sub_id = resolved_subject_id or (deferred.subject_hypotheses.candidate_entity_ids[0] if len(deferred.subject_hypotheses.candidate_entity_ids) == 1 else None)
        obj_id = resolved_object_id or (deferred.object_hypotheses.candidate_entity_ids[0] if len(deferred.object_hypotheses.candidate_entity_ids) == 1 else None)

        if not sub_id or not obj_id:
            raise ValueError("Resolution requires resolving both subject and object to singleton entity IDs.")

        # Re-derive trusted context from original source record
        trusted_ctx = derive_trusted_source_context(original_source_rec, self.capability_registry)

        obs = Observation(
            subject=sub_id,
            predicate=deferred.predicate,
            obj=obj_id,
            t_valid_start=deferred.t_valid_start,
            t_valid_end=deferred.t_valid_end,
            t_knowledge=t_knowledge_resolution,
            source_id=original_source_rec.claimed_origin.claimed_source_name,
            origin_id=original_source_rec.authenticated_origin.verified_id,
            lineage_roots=frozenset([trusted_ctx.independence_class]),
            observation_id=f"obs_res_{deferred.deferred_id}",
        )

        cert = AdmissionCertificate(
            status=AdmissionStatus.ADMIT,
            binding_witness={"subject": sub_id, "object": obj_id},
            schema_witness="DEFERRED_BINDING_RESOLVED",
            temporal_witness=f"[{obs.t_valid_start}, {obs.t_valid_end})",
            auth_witness=f"ORIGINAL_SCOPE_{deferred.predicate}",
            lineage_roots=obs.lineage_roots,
        )

        p_contract = contract or PredicateContract(predicate=deferred.predicate, cardinality="SINGLE", temporal_mode="TIME_VARYING")

        fid = f"fact_res_{deferred.deferred_id}"
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

        events = adjudicate_observation(obs=obs, engine=self.bitemporal_engine, contract=p_contract, new_fact_id=fid)
        for ev in events:
            self.bitemporal_engine.record_event(ev)

        # Mark deferred binding resolved
        self.deferred_bindings[deferred_id] = DeferredBinding(
            deferred_id=deferred.deferred_id,
            source_record_id=deferred.source_record_id,
            attestation_id=deferred.attestation_id,
            subject_hypotheses=BindingHypothesisSet(deferred.subject_hypotheses.mention_span, "SUBJECT", (sub_id,)),
            predicate=deferred.predicate,
            object_hypotheses=BindingHypothesisSet(deferred.object_hypotheses.mention_span, "OBJECT", (obj_id,)),
            t_valid_start=deferred.t_valid_start,
            t_valid_end=deferred.t_valid_end,
            t_knowledge=t_knowledge_resolution,
            reason_deferred="RESOLVED",
            is_resolved=True,
            admitted_fact_id=fid,
        )

        return {
            "status": AdmissionStatus.ADMIT.value,
            "certificate": cert,
            "admitted_fact_id": fid,
            "observation": obs,
            "events_recorded": len(events),
        }

    def promote_provisional_entity(
        self,
        provisional_id: str,
        canonical_entity_id: str,
        canonical_name: str,
        entity_type: str = "DEVICE",
        aliases: tuple[str, ...] = (),
        t_knowledge_promotion: int = 2,
        contract: Optional[PredicateContract] = None,
    ) -> dict[str, Any]:
        """Promote a ProvisionalEntity to canonical status, atomically retargeting relations.
        
        Preserves original SourceRecord provenance and independence roots without manufacturing new roots.
        """
        if provisional_id not in self.provisional_entities:
            raise KeyError(f"ProvisionalEntity '{provisional_id}' not found in store.")

        prov_ent = self.provisional_entities[provisional_id]
        if prov_ent.is_promoted:
            raise ValueError(f"ProvisionalEntity '{provisional_id}' is already promoted.")

        # 1. Register canonical entity in domain ontology
        canonical_def = EntityDefinition(
            entity_id=canonical_entity_id,
            canonical_name=canonical_name,
            entity_type=entity_type,
            aliases=aliases,
        )
        self.ontology.register_entity(canonical_def)

        # 2. Migrate associated ProvisionalRelations into authoritative BitemporalFacts
        migrated_facts: list[str] = []
        for rel_id, rel in list(self.provisional_relations.items()):
            if rel.subject_id == provisional_id or rel.object_id == provisional_id:
                sub = canonical_entity_id if rel.subject_id == provisional_id else rel.subject_id
                obj = canonical_entity_id if rel.object_id == provisional_id else rel.object_id
                orig_rec = self.source_records[rel.source_record_id]

                obs = Observation(
                    subject=sub,
                    predicate=rel.predicate,
                    obj=obj,
                    t_valid_start=rel.t_valid_start,
                    t_valid_end=rel.t_valid_end,
                    t_knowledge=t_knowledge_promotion,
                    source_id=orig_rec.claimed_origin.claimed_source_name,
                    origin_id=orig_rec.authenticated_origin.verified_id,
                    lineage_roots=rel.lineage_roots,  # Provenance preserved from original sensor record!
                    observation_id=f"obs_mig_{rel_id}",
                )

                p_contract = contract or PredicateContract(predicate=rel.predicate, cardinality="SINGLE", temporal_mode="TIME_VARYING")
                fid = f"fact_prom_{rel_id}"
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
                evs = adjudicate_observation(obs=obs, engine=self.bitemporal_engine, contract=p_contract, new_fact_id=fid)
                for ev in evs:
                    self.bitemporal_engine.record_event(ev)

                migrated_facts.append(fid)

        # 3. Mark provisional entity as promoted
        self.provisional_entities[provisional_id] = ProvisionalEntity(
            provisional_id=prov_ent.provisional_id,
            first_mention_span=prov_ent.first_mention_span,
            first_source_record_id=prov_ent.first_source_record_id,
            t_created_knowledge=prov_ent.t_created_knowledge,
            associated_attestation_ids=prov_ent.associated_attestation_ids,
            is_promoted=True,
            canonical_entity_id=canonical_entity_id,
        )

        return {
            "provisional_id": provisional_id,
            "canonical_entity_id": canonical_entity_id,
            "migrated_fact_ids": migrated_facts,
            "is_promoted": True,
        }
