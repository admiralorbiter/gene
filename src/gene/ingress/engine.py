"""Epistemic Ingress Engine with Proof-Carrying Lifecycle Transitions (Round 7)."""

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
    PromotionCertificate,
    ProvisionalEntity,
    ProvisionalRelation,
    ResolutionCertificate,
    SourceRecord,
    TrustedSourceContext,
)
from gene.ingress.ontology import (
    CapabilityPolicyRegistry,
    EntityDefinition,
    IngressOntology,
    LineageIndependenceRegistry,
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
    """Master runtime coordinator for Epistemic Ingress & Lifecycle Operations."""

    def __init__(
        self,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        policy: Optional[IngressPolicy] = None,
        bitemporal_engine: Optional[BitemporalEngine] = None,
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ):
        self.ontology = ontology
        self.capability_registry = capability_registry
        self.independence_registry = independence_registry or LineageIndependenceRegistry()
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

        cert, obs, deferred, prov_list, prov_rel, trusted_ctx = self.policy.evaluate(
            source_record=source_record,
            parsed_attestation=parsed_attestation,
            subject_hypotheses=subject_hypotheses,
            object_hypotheses=object_hypotheses,
            ontology=self.ontology,
            capability_registry=self.capability_registry,
            contract=contract,
            independence_registry=self.independence_registry,
        )

        self.certificates[source_record.record_id] = cert

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
                certificate=cert,
                independence_registry=self.independence_registry,
            )

            if not is_valid:
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
            for prov in prov_list:
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
        chosen_subject_id: str,
        chosen_object_id: str,
        disambiguating_record: SourceRecord,
        resolution_certificate: ResolutionCertificate,
        contract: Optional[PredicateContract] = None,
    ) -> dict[str, Any]:
        """Resolve an existing DeferredBinding under proof-carrying evidence."""
        if deferred_id not in self.deferred_bindings:
            raise KeyError(f"DeferredBinding '{deferred_id}' not found in store.")

        deferred = self.deferred_bindings[deferred_id]
        if deferred.is_resolved:
            raise ValueError(f"DeferredBinding '{deferred_id}' is already resolved.")

        original_source_rec = self.source_records[deferred.source_record_id]
        self.source_records[disambiguating_record.record_id] = disambiguating_record

        # 1. Independent Certificate Verification for Resolution
        is_valid, msg = CertificateVerifier.verify_resolution(
            deferred=deferred,
            chosen_subject_id=chosen_subject_id,
            chosen_object_id=chosen_object_id,
            disambiguating_record=disambiguating_record,
            original_source_record=original_source_rec,
            capability_registry=self.capability_registry,
            ontology=self.ontology,
            certificate=resolution_certificate,
            independence_registry=self.independence_registry,
        )

        if not is_valid:
            return {
                "status": AdmissionStatus.REJECT.value,
                "admitted_fact_id": None,
                "failure_reason": msg,
            }

        orig_ctx = derive_trusted_source_context(original_source_rec, self.capability_registry, self.independence_registry)

        obs = Observation(
            subject=chosen_subject_id,
            predicate=deferred.predicate,
            obj=chosen_object_id,
            t_valid_start=deferred.t_valid_start,
            t_valid_end=deferred.t_valid_end,
            t_knowledge=disambiguating_record.t_knowledge,
            source_id=original_source_rec.claimed_origin.claimed_source_name,
            origin_id=original_source_rec.authenticated_origin.verified_id,
            lineage_roots=frozenset([orig_ctx.independence_class]),
            observation_id=f"obs_res_{deferred.deferred_id}",
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

        self.deferred_bindings[deferred_id] = DeferredBinding(
            deferred_id=deferred.deferred_id,
            source_record_id=deferred.source_record_id,
            attestation_id=deferred.attestation_id,
            subject_hypotheses=BindingHypothesisSet(deferred.subject_hypotheses.mention_span, "SUBJECT", (chosen_subject_id,)),
            predicate=deferred.predicate,
            object_hypotheses=BindingHypothesisSet(deferred.object_hypotheses.mention_span, "OBJECT", (chosen_object_id,)),
            t_valid_start=deferred.t_valid_start,
            t_valid_end=deferred.t_valid_end,
            t_knowledge=disambiguating_record.t_knowledge,
            reason_deferred="RESOLVED",
            is_resolved=True,
            admitted_fact_id=fid,
        )

        return {
            "status": AdmissionStatus.ADMIT.value,
            "certificate": resolution_certificate,
            "admitted_fact_id": fid,
            "observation": obs,
            "events_recorded": len(events),
            "failure_reason": None,
        }

    def promote_provisional_entity(
        self,
        provisional_id: str,
        canonical_entity_id: str,
        canonical_name: str,
        promotion_authority_record: SourceRecord,
        promotion_certificate: PromotionCertificate,
        entity_type: str = "DEVICE",
        aliases: tuple[str, ...] = (),
        contract: Optional[PredicateContract] = None,
    ) -> dict[str, Any]:
        """Promote a ProvisionalEntity to canonical status under proof-carrying authority.
        
        CRITICAL DUAL-NOVEL STATUS LAUNDERING FIX:
        When promoting entity A, relations involving A and another STILL-PROVISIONAL entity B
        are retargeted to (canonical_A, pred, provisional_B) and KEPT PROVISIONAL.
        They migrate to authoritative BitemporalFacts ONLY when ALL endpoints are canonical!
        """
        if provisional_id not in self.provisional_entities:
            raise KeyError(f"ProvisionalEntity '{provisional_id}' not found in store.")

        prov_ent = self.provisional_entities[provisional_id]
        if prov_ent.is_promoted:
            raise ValueError(f"ProvisionalEntity '{provisional_id}' is already promoted.")

        self.source_records[promotion_authority_record.record_id] = promotion_authority_record

        associated_rels = [
            rel for rel in self.provisional_relations.values()
            if rel.subject_id == provisional_id or rel.object_id == provisional_id
        ]

        # 1. Independent Certificate Verification for Promotion
        is_valid, msg = CertificateVerifier.verify_promotion(
            provisional=prov_ent,
            canonical_entity_id=canonical_entity_id,
            canonical_name=canonical_name,
            entity_type=entity_type,
            promotion_authority_record=promotion_authority_record,
            capability_registry=self.capability_registry,
            ontology=self.ontology,
            certificate=promotion_certificate,
            associated_relations=associated_rels,
            source_records_map=self.source_records,
            independence_registry=self.independence_registry,
        )

        if not is_valid:
            return {
                "status": AdmissionStatus.REJECT.value,
                "is_promoted": False,
                "failure_reason": msg,
            }

        # 2. Register canonical entity in domain ontology
        canonical_def = EntityDefinition(
            entity_id=canonical_entity_id,
            canonical_name=canonical_name,
            entity_type=entity_type,
            aliases=aliases,
        )
        self.ontology.register_entity(canonical_def)

        # 3. Retarget and migrate associated ProvisionalRelations
        migrated_facts: list[str] = []
        for rel in associated_rels:
            # Determine retargeted IDs
            sub = canonical_entity_id if rel.subject_id == provisional_id else rel.subject_id
            obj = canonical_entity_id if rel.object_id == provisional_id else rel.object_id

            sub_prov = False if rel.subject_id == provisional_id else rel.is_subject_provisional
            obj_prov = False if rel.object_id == provisional_id else rel.is_object_provisional

            # If both endpoints are now canonical, migrate to authoritative fact!
            if not sub_prov and not obj_prov:
                orig_rec = self.source_records[rel.source_record_id]
                obs = Observation(
                    subject=sub,
                    predicate=rel.predicate,
                    obj=obj,
                    t_valid_start=rel.t_valid_start,
                    t_valid_end=rel.t_valid_end,
                    t_knowledge=promotion_authority_record.t_knowledge,
                    source_id=orig_rec.claimed_origin.claimed_source_name,
                    origin_id=orig_rec.authenticated_origin.verified_id,
                    lineage_roots=rel.lineage_roots,  # Original provenance root preserved!
                    observation_id=f"obs_mig_{rel.relation_id}",
                )

                p_contract = contract or PredicateContract(predicate=rel.predicate, cardinality="SINGLE", temporal_mode="TIME_VARYING")
                fid = f"fact_prom_{rel.relation_id}"
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
                # Remove migrated relation from provisional store
                if rel.relation_id in self.provisional_relations:
                    del self.provisional_relations[rel.relation_id]
            else:
                # Still has at least one provisional endpoint -> Update provisional relation in place!
                self.provisional_relations[rel.relation_id] = ProvisionalRelation(
                    relation_id=rel.relation_id,
                    subject_id=sub,
                    predicate=rel.predicate,
                    object_id=obj,
                    t_valid_start=rel.t_valid_start,
                    t_valid_end=rel.t_valid_end,
                    source_record_id=rel.source_record_id,
                    is_subject_provisional=sub_prov,
                    is_object_provisional=obj_prov,
                    lineage_roots=rel.lineage_roots,
                )

        # 4. Mark provisional entity as promoted
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
            "status": AdmissionStatus.ADMIT.value,
            "provisional_id": provisional_id,
            "canonical_entity_id": canonical_entity_id,
            "migrated_fact_ids": migrated_facts,
            "is_promoted": True,
            "failure_reason": None,
        }
