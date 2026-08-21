"""Comparative Epistemic Ingress Policies (A0 to A4) (Round 7)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple

from gene.ingress.models import (
    AdmissionCertificate,
    AdmissionStatus,
    BindingHypothesisSet,
    DeferredBinding,
    ParsedAttestation,
    ProvisionalEntity,
    SourceContext,
    SourceRecord,
)
from gene.ingress.ontology import CapabilityPolicyRegistry, IngressOntology
from gene.supersession_engine import Observation, PredicateContract


class IngressPolicy(ABC):
    """Abstract interface for epistemic write admission policies."""

    @abstractmethod
    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        source_context: SourceContext,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], Optional[ProvisionalEntity]]:
        """Evaluate an incoming parsed attestation and return admission certificate and resulting artifact."""
        pass


class A0Top1BlindWritePolicy(IngressPolicy):
    """A0: Top-1 Blind Write.
    Binds top-1 lexical candidate; drops novelty; blind to authorization and ambiguity.
    """

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        source_context: SourceContext,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], Optional[ProvisionalEntity]]:
        sub_cands = subject_hypotheses.candidate_entity_ids
        obj_cands = object_hypotheses.candidate_entity_ids

        # If no candidates exist (novelty), A0 drops the observation
        if not sub_cands or not obj_cands:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="A0_NO_CANDIDATE_FOUND",
            )
            return cert, None, None, None

        sub_id = sub_cands[0]
        obj_id = obj_cands[0]

        obs = Observation(
            subject=sub_id,
            predicate=parsed_attestation.predicate_span,
            obj=obj_id,
            t_valid_start=parsed_attestation.t_valid_start,
            t_valid_end=parsed_attestation.t_valid_end,
            t_knowledge=source_record.t_knowledge,
            source_id=source_record.claimed_origin.claimed_source_name,
            origin_id=source_record.authenticated_origin.verified_id,
            lineage_roots=frozenset([source_context.independence_class]),
            observation_id=f"obs_{source_record.record_id}",
        )

        cert = AdmissionCertificate(
            status=AdmissionStatus.ADMIT,
            binding_witness={"subject": sub_id, "object": obj_id},
            schema_witness="A0_BLIND_BIND",
            temporal_witness=f"[{obs.t_valid_start}, {obs.t_valid_end})",
            auth_witness="A0_UNCHECKED",
            lineage_roots=obs.lineage_roots,
        )
        return cert, obs, None, None


class A1CanonicalizationOnlyPolicy(IngressPolicy):
    """A1: Canonicalization Only.
    Normalizes surface aliases; collapses ambiguity/novelty to top-1; blind to authorization.
    """

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        source_context: SourceContext,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], Optional[ProvisionalEntity]]:
        sub_res = ontology.resolve_alias(parsed_attestation.subject_span)
        obj_res = ontology.resolve_alias(parsed_attestation.object_span)

        # If alias normalization fails, fallback to top-1 candidate or reject if none
        sub_id = sub_res or (subject_hypotheses.candidate_entity_ids[0] if subject_hypotheses.candidate_entity_ids else None)
        obj_id = obj_res or (object_hypotheses.candidate_entity_ids[0] if object_hypotheses.candidate_entity_ids else None)

        if not sub_id or not obj_id:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="A1_CANONICALIZATION_FAILED",
            )
            return cert, None, None, None

        obs = Observation(
            subject=sub_id,
            predicate=parsed_attestation.predicate_span,
            obj=obj_id,
            t_valid_start=parsed_attestation.t_valid_start,
            t_valid_end=parsed_attestation.t_valid_end,
            t_knowledge=source_record.t_knowledge,
            source_id=source_record.claimed_origin.claimed_source_name,
            origin_id=source_record.authenticated_origin.verified_id,
            lineage_roots=frozenset([source_context.independence_class]),
            observation_id=f"obs_{source_record.record_id}",
        )

        cert = AdmissionCertificate(
            status=AdmissionStatus.ADMIT,
            binding_witness={"subject": sub_id, "object": obj_id},
            schema_witness="A1_NORMALIZED",
            temporal_witness=f"[{obs.t_valid_start}, {obs.t_valid_end})",
            auth_witness="A1_UNCHECKED",
            lineage_roots=obs.lineage_roots,
        )
        return cert, obs, None, None


class A2CandidateAwarePolicy(IngressPolicy):
    """A2: Candidate-Aware Gate.
    Preserves ambiguity and novelty under DEFERRED_BINDING; blind to authority.
    """

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        source_context: SourceContext,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], Optional[ProvisionalEntity]]:
        sub_cands = subject_hypotheses.candidate_entity_ids
        obj_cands = object_hypotheses.candidate_entity_ids

        # Handle Novelty or Multiple Candidates -> Defer
        if len(sub_cands) != 1 or len(obj_cands) != 1 or subject_hypotheses.is_novel or object_hypotheses.is_novel:
            deferred = DeferredBinding(
                deferred_id=f"def_{source_record.record_id}",
                source_record_id=source_record.record_id,
                attestation_id=parsed_attestation.attestation_id,
                subject_hypotheses=subject_hypotheses,
                predicate=parsed_attestation.predicate_span,
                object_hypotheses=object_hypotheses,
                t_valid_start=parsed_attestation.t_valid_start,
                t_valid_end=parsed_attestation.t_valid_end,
                t_knowledge=source_record.t_knowledge,
                reason_deferred="AMBIGUOUS_OR_NOVEL_CANDIDATE_SET",
            )
            cert = AdmissionCertificate(
                status=AdmissionStatus.DEFER,
                candidates_remaining=(sub_cands + obj_cands),
                evidence_needed="DISAMBIGUATING_EVIDENCE",
            )
            return cert, None, deferred, None

        sub_id = sub_cands[0]
        obj_id = obj_cands[0]

        obs = Observation(
            subject=sub_id,
            predicate=parsed_attestation.predicate_span,
            obj=obj_id,
            t_valid_start=parsed_attestation.t_valid_start,
            t_valid_end=parsed_attestation.t_valid_end,
            t_knowledge=source_record.t_knowledge,
            source_id=source_record.claimed_origin.claimed_source_name,
            origin_id=source_record.authenticated_origin.verified_id,
            lineage_roots=frozenset([source_context.independence_class]),
            observation_id=f"obs_{source_record.record_id}",
        )

        cert = AdmissionCertificate(
            status=AdmissionStatus.ADMIT,
            binding_witness={"subject": sub_id, "object": obj_id},
            schema_witness="A2_RESOLVED",
            temporal_witness=f"[{obs.t_valid_start}, {obs.t_valid_end})",
            auth_witness="A2_UNCHECKED",
            lineage_roots=obs.lineage_roots,
        )
        return cert, obs, None, None


class A3AuthorityAwarePolicy(IngressPolicy):
    """A3: Authority-Aware Gate.
    Enforces capability and authorization checks; collapses ambiguity/novelty to top-1.
    """

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        source_context: SourceContext,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], Optional[ProvisionalEntity]]:
        # Check authorization scope
        pred = parsed_attestation.predicate_span
        if pred not in source_context.authorization_scope and "*" not in source_context.authorization_scope:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause=f"UNAUTHORIZED_PREDICATE_SCOPE_{pred}",
            )
            return cert, None, None, None

        # Check authentication if claim requires root fact privilege
        if source_context.authenticity == "UNVERIFIED":
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="UNAUTHENTICATED_ORIGIN",
            )
            return cert, None, None, None

        sub_res = ontology.resolve_alias(parsed_attestation.subject_span)
        obj_res = ontology.resolve_alias(parsed_attestation.object_span)

        sub_id = sub_res or (subject_hypotheses.candidate_entity_ids[0] if subject_hypotheses.candidate_entity_ids else None)
        obj_id = obj_res or (object_hypotheses.candidate_entity_ids[0] if object_hypotheses.candidate_entity_ids else None)

        if not sub_id or not obj_id:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="A3_CANONICALIZATION_FAILED",
            )
            return cert, None, None, None

        obs = Observation(
            subject=sub_id,
            predicate=pred,
            obj=obj_id,
            t_valid_start=parsed_attestation.t_valid_start,
            t_valid_end=parsed_attestation.t_valid_end,
            t_knowledge=source_record.t_knowledge,
            source_id=source_record.claimed_origin.claimed_source_name,
            origin_id=source_record.authenticated_origin.verified_id,
            lineage_roots=frozenset([source_context.independence_class]),
            observation_id=f"obs_{source_record.record_id}",
        )

        cert = AdmissionCertificate(
            status=AdmissionStatus.ADMIT,
            binding_witness={"subject": sub_id, "object": obj_id},
            schema_witness="A3_AUTHORIZED",
            temporal_witness=f"[{obs.t_valid_start}, {obs.t_valid_end})",
            auth_witness=f"AUTHORIZED_SCOPE_{pred}",
            lineage_roots=obs.lineage_roots,
        )
        return cert, obs, None, None


class A4FullGENEIngressPolicy(IngressPolicy):
    """A4: Full GENE Ingress.
    Hypothesis preservation (DEFERRED_BINDING) + PROVISIONAL_ENTITY + capability authorization + proof certificates.
    """

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        source_context: SourceContext,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], Optional[ProvisionalEntity]]:
        # 1. Authority & Capability Scope Validation
        pred = parsed_attestation.predicate_span
        if pred not in source_context.authorization_scope and "*" not in source_context.authorization_scope:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause=f"OUT_OF_SCOPE_PREDICATE_{pred}",
            )
            return cert, None, None, None

        if source_context.authenticity == "UNVERIFIED":
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="UNAUTHENTICATED_ORIGIN_ROOT_FACT_FORBIDDEN",
            )
            return cert, None, None, None

        # 2. Novel Entity Detection -> PROVISIONAL_ENTITY
        if subject_hypotheses.is_novel or object_hypotheses.is_novel:
            prov_entity = None
            if subject_hypotheses.is_novel:
                prov_entity = ProvisionalEntity(
                    provisional_id=f"prov_{parsed_attestation.subject_span.strip().lower().replace(' ', '_')}",
                    first_mention_span=parsed_attestation.subject_span,
                    first_source_record_id=source_record.record_id,
                    t_created_knowledge=source_record.t_knowledge,
                    associated_attestation_ids=(parsed_attestation.attestation_id,),
                )
            cert = AdmissionCertificate(
                status=AdmissionStatus.DEFER,
                candidates_remaining=(),
                evidence_needed="CANONICAL_ONTOLOGY_REGISTRATION",
                failed_constraint="NOVEL_ENTITY_CANONICAL_PROMOTION_REQUIRED",
            )
            return cert, None, None, prov_entity

        # 3. Ambiguity & Collision Detection -> DEFERRED_BINDING
        sub_cands = subject_hypotheses.candidate_entity_ids
        obj_cands = object_hypotheses.candidate_entity_ids

        if len(sub_cands) > 1 or len(obj_cands) > 1:
            deferred = DeferredBinding(
                deferred_id=f"def_{source_record.record_id}",
                source_record_id=source_record.record_id,
                attestation_id=parsed_attestation.attestation_id,
                subject_hypotheses=subject_hypotheses,
                predicate=pred,
                object_hypotheses=object_hypotheses,
                t_valid_start=parsed_attestation.t_valid_start,
                t_valid_end=parsed_attestation.t_valid_end,
                t_knowledge=source_record.t_knowledge,
                reason_deferred="COLLISION_OR_ROLE_AMBIGUITY",
            )
            cert = AdmissionCertificate(
                status=AdmissionStatus.DEFER,
                candidates_remaining=(sub_cands + obj_cands),
                evidence_needed="DISAMBIGUATING_PREDICATE_OR_SOURCE_EVIDENCE",
            )
            return cert, None, deferred, None

        if len(sub_cands) == 0 or len(obj_cands) == 0:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="ZERO_CANDIDATES_RESOLVED",
            )
            return cert, None, None, None

        # 4. Canonical Exact Match -> Issue ADMIT Certificate
        sub_id = sub_cands[0]
        obj_id = obj_cands[0]

        obs = Observation(
            subject=sub_id,
            predicate=pred,
            obj=obj_id,
            t_valid_start=parsed_attestation.t_valid_start,
            t_valid_end=parsed_attestation.t_valid_end,
            t_knowledge=source_record.t_knowledge,
            source_id=source_record.claimed_origin.claimed_source_name,
            origin_id=source_record.authenticated_origin.verified_id,
            lineage_roots=frozenset([source_context.independence_class]),
            observation_id=f"obs_{source_record.record_id}",
        )

        cert = AdmissionCertificate(
            status=AdmissionStatus.ADMIT,
            binding_witness={"subject": sub_id, "object": obj_id},
            schema_witness="GENE_EXACT_CANONICAL_BINDING",
            temporal_witness=f"[{obs.t_valid_start}, {obs.t_valid_end})",
            auth_witness=f"SCOPE_VERIFIED_{pred}",
            lineage_roots=obs.lineage_roots,
        )
        return cert, obs, None, None
