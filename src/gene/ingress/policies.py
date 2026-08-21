"""Comparative Epistemic Ingress Policies (A0 to A4) (Stage 7A.2)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple

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
    IngressOntology,
    LineageIndependenceRegistry,
    derive_trusted_source_context,
)
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
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], list[ProvisionalEntity], Optional[ProvisionalRelation], TrustedSourceContext]:
        """Evaluate an incoming parsed attestation and return admission certificate and artifacts."""
        pass


class A0Top1BlindWritePolicy(IngressPolicy):
    """A0: Top-1 Blind Write."""

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], list[ProvisionalEntity], Optional[ProvisionalRelation], TrustedSourceContext]:
        trusted_ctx = derive_trusted_source_context(source_record, capability_registry, independence_registry)
        sub_cands = subject_hypotheses.candidate_entity_ids
        obj_cands = object_hypotheses.candidate_entity_ids

        if not sub_cands or not obj_cands:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="A0_NO_CANDIDATE_FOUND",
            )
            return cert, None, None, [], None, trusted_ctx

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
            lineage_roots=frozenset([trusted_ctx.independence_class]),
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
        return cert, obs, None, [], None, trusted_ctx


class A1CanonicalizationOnlyPolicy(IngressPolicy):
    """A1: Canonicalization Only."""

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], list[ProvisionalEntity], Optional[ProvisionalRelation], TrustedSourceContext]:
        trusted_ctx = derive_trusted_source_context(source_record, capability_registry, independence_registry)
        sub_cands = ontology.resolve_alias_candidates(parsed_attestation.subject_span) or subject_hypotheses.candidate_entity_ids
        obj_cands = ontology.resolve_alias_candidates(parsed_attestation.object_span) or object_hypotheses.candidate_entity_ids

        sub_id = sub_cands[0] if sub_cands else None
        obj_id = obj_cands[0] if obj_cands else None

        if not sub_id or not obj_id:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="A1_CANONICALIZATION_FAILED",
            )
            return cert, None, None, [], None, trusted_ctx

        obs = Observation(
            subject=sub_id,
            predicate=parsed_attestation.predicate_span,
            obj=obj_id,
            t_valid_start=parsed_attestation.t_valid_start,
            t_valid_end=parsed_attestation.t_valid_end,
            t_knowledge=source_record.t_knowledge,
            source_id=source_record.claimed_origin.claimed_source_name,
            origin_id=source_record.authenticated_origin.verified_id,
            lineage_roots=frozenset([trusted_ctx.independence_class]),
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
        return cert, obs, None, [], None, trusted_ctx


class A2CandidateAwarePolicy(IngressPolicy):
    """A2: Candidate-Aware Gate."""

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], list[ProvisionalEntity], Optional[ProvisionalRelation], TrustedSourceContext]:
        trusted_ctx = derive_trusted_source_context(source_record, capability_registry, independence_registry)
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
            return cert, None, deferred, [], None, trusted_ctx

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
            lineage_roots=frozenset([trusted_ctx.independence_class]),
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
        return cert, obs, None, [], None, trusted_ctx


class A3AuthorityAwarePolicy(IngressPolicy):
    """A3: Authority-Aware Gate."""

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], list[ProvisionalEntity], Optional[ProvisionalRelation], TrustedSourceContext]:
        trusted_ctx = derive_trusted_source_context(source_record, capability_registry, independence_registry)

        if trusted_ctx.is_spoofed_origin:
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause="SPOOFED_ORIGIN")
            return cert, None, None, [], None, trusted_ctx

        if trusted_ctx.authenticity == "UNVERIFIED":
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause="UNAUTHENTICATED_ORIGIN")
            return cert, None, None, [], None, trusted_ctx

        pred = parsed_attestation.predicate_span
        if pred not in trusted_ctx.authorization_scope and "*" not in trusted_ctx.authorization_scope:
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause=f"UNAUTHORIZED_PREDICATE_SCOPE_{pred}")
            return cert, None, None, [], None, trusted_ctx

        if trusted_ctx.max_claim_privilege != ClaimPrivilege.ROOT_FACT:
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause="PRIVILEGE_RESTRICTED_ATTESTATION_ONLY")
            return cert, None, None, [], None, trusted_ctx

        sub_cands = ontology.resolve_alias_candidates(parsed_attestation.subject_span) or subject_hypotheses.candidate_entity_ids
        obj_cands = ontology.resolve_alias_candidates(parsed_attestation.object_span) or object_hypotheses.candidate_entity_ids

        sub_id = sub_cands[0] if sub_cands else None
        obj_id = obj_cands[0] if obj_cands else None

        if not sub_id or not obj_id:
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause="A3_CANONICALIZATION_FAILED")
            return cert, None, None, [], None, trusted_ctx

        obs = Observation(
            subject=sub_id,
            predicate=pred,
            obj=obj_id,
            t_valid_start=parsed_attestation.t_valid_start,
            t_valid_end=parsed_attestation.t_valid_end,
            t_knowledge=source_record.t_knowledge,
            source_id=source_record.claimed_origin.claimed_source_name,
            origin_id=source_record.authenticated_origin.verified_id,
            lineage_roots=frozenset([trusted_ctx.independence_class]),
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
        return cert, obs, None, [], None, trusted_ctx


class A4FullGENEIngressPolicy(IngressPolicy):
    """A4: Full Proof-Carrying GENE Ingress Policy with Dual Novelty Support."""

    def evaluate(
        self,
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[AdmissionCertificate, Optional[Observation], Optional[DeferredBinding], list[ProvisionalEntity], Optional[ProvisionalRelation], TrustedSourceContext]:
        trusted_ctx = derive_trusted_source_context(source_record, capability_registry, independence_registry)

        # 1. Authority & Capability Scope Validation
        if trusted_ctx.is_spoofed_origin:
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause="SPOOFED_ORIGIN_DETECTED")
            return cert, None, None, [], None, trusted_ctx

        if trusted_ctx.authenticity == "UNVERIFIED":
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause="UNAUTHENTICATED_ORIGIN_ROOT_FACT_FORBIDDEN")
            return cert, None, None, [], None, trusted_ctx

        pred = parsed_attestation.predicate_span
        if pred not in trusted_ctx.authorization_scope and "*" not in trusted_ctx.authorization_scope:
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause=f"OUT_OF_SCOPE_PREDICATE_{pred}")
            return cert, None, None, [], None, trusted_ctx

        if trusted_ctx.max_claim_privilege != ClaimPrivilege.ROOT_FACT:
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause=f"PRIVILEGE_RESTRICTED_{trusted_ctx.max_claim_privilege.value}")
            return cert, None, None, [], None, trusted_ctx

        if parsed_attestation.extracted_claim_type != ClaimType.FACTUAL_OBSERVATION:
            cert = AdmissionCertificate(status=AdmissionStatus.REJECT, rejection_cause=f"CLAIM_TYPE_NOT_ROOT_FACT_{parsed_attestation.extracted_claim_type.value}")
            return cert, None, None, [], None, trusted_ctx

        # 2. Novel Entity Detection -> PROVISIONAL_ENTITY (Subject, Object, OR BOTH!)
        if subject_hypotheses.is_novel or object_hypotheses.is_novel:
            prov_entities: list[ProvisionalEntity] = []

            prov_sub_id = None
            if subject_hypotheses.is_novel:
                prov_sub = ProvisionalEntity(
                    provisional_id=f"prov_{parsed_attestation.subject_span.strip().lower().replace(' ', '_')}",
                    first_mention_span=parsed_attestation.subject_span,
                    first_source_record_id=source_record.record_id,
                    t_created_knowledge=source_record.t_knowledge,
                    associated_attestation_ids=(parsed_attestation.attestation_id,),
                )
                prov_entities.append(prov_sub)
                prov_sub_id = prov_sub.provisional_id
            else:
                prov_sub_id = subject_hypotheses.candidate_entity_ids[0] if subject_hypotheses.candidate_entity_ids else "unknown_sub"

            prov_obj_id = None
            if object_hypotheses.is_novel:
                prov_obj = ProvisionalEntity(
                    provisional_id=f"prov_{parsed_attestation.object_span.strip().lower().replace(' ', '_')}",
                    first_mention_span=parsed_attestation.object_span,
                    first_source_record_id=source_record.record_id,
                    t_created_knowledge=source_record.t_knowledge,
                    associated_attestation_ids=(parsed_attestation.attestation_id,),
                )
                prov_entities.append(prov_obj)
                prov_obj_id = prov_obj.provisional_id
            else:
                prov_obj_id = object_hypotheses.candidate_entity_ids[0] if object_hypotheses.candidate_entity_ids else "unknown_obj"

            prov_rel = ProvisionalRelation(
                relation_id=f"provrel_{source_record.record_id}",
                subject_id=prov_sub_id,
                predicate=pred,
                object_id=prov_obj_id,
                t_valid_start=parsed_attestation.t_valid_start,
                t_valid_end=parsed_attestation.t_valid_end,
                source_record_id=source_record.record_id,
                is_subject_provisional=subject_hypotheses.is_novel,
                is_object_provisional=object_hypotheses.is_novel,
                lineage_roots=frozenset([trusted_ctx.independence_class]),
            )

            cert = AdmissionCertificate(
                status=AdmissionStatus.DEFER,
                candidates_remaining=(),
                evidence_needed="CANONICAL_ONTOLOGY_REGISTRATION",
                failed_constraint="NOVEL_ENTITY_CANONICAL_PROMOTION_REQUIRED",
            )
            return cert, None, None, prov_entities, prov_rel, trusted_ctx

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
            return cert, None, deferred, [], None, trusted_ctx

        if len(sub_cands) == 0 or len(obj_cands) == 0:
            cert = AdmissionCertificate(
                status=AdmissionStatus.REJECT,
                rejection_cause="ZERO_CANDIDATES_RESOLVED",
            )
            return cert, None, None, [], None, trusted_ctx

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
            lineage_roots=frozenset([trusted_ctx.independence_class]),
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
        return cert, obs, None, [], None, trusted_ctx
