"""Independent, Pure Certificate Verifier for Epistemic Ingress & Lifecycle Operations (Round 7)."""

from __future__ import annotations

from typing import Optional, Tuple

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
    IngressOntology,
    LineageIndependenceRegistry,
    derive_trusted_source_context,
)
from gene.supersession_engine import Observation, PredicateContract


class CertificateVerifier:
    """Pure, standalone proof-carrying certificate verification engine.
    
    SECURITY INVARIANT:
    Independently derives TrustedSourceContext from (SourceRecord, CapabilityPolicyRegistry, LineageIndependenceRegistry).
    Never trusts caller-supplied context.
    """

    @staticmethod
    def verify(
        source_record: SourceRecord,
        parsed_attestation: ParsedAttestation,
        subject_hypotheses: BindingHypothesisSet,
        object_hypotheses: BindingHypothesisSet,
        proposed_observation: Optional[Observation],
        ontology: IngressOntology,
        capability_registry: CapabilityPolicyRegistry,
        contract: PredicateContract,
        certificate: AdmissionCertificate,
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Verify that certificate legitimately justifies the proposed admission action."""

        trusted_context = derive_trusted_source_context(
            source_record=source_record,
            capability_registry=capability_registry,
            independence_registry=independence_registry,
        )

        # 1. Verification of ADMIT certificates
        if certificate.status == AdmissionStatus.ADMIT:
            if proposed_observation is None:
                return False, "ADMIT certificate must accompany a valid ProposedObservation"

            # Check binding witness integrity
            bw = certificate.binding_witness
            if not bw or "subject" not in bw or "object" not in bw:
                return False, "ADMIT certificate missing complete binding_witness"

            sub_id = bw["subject"]
            obj_id = bw["object"]

            if proposed_observation.subject != sub_id or proposed_observation.obj != obj_id:
                return False, "ProposedObservation entities do not match binding_witness"

            if sub_id not in subject_hypotheses.candidate_entity_ids:
                return False, f"Bound subject {sub_id} not in subject candidate hypothesis set"
            if obj_id not in object_hypotheses.candidate_entity_ids:
                return False, f"Bound object {obj_id} not in object candidate hypothesis set"

            if not ontology.contains_entity(sub_id):
                return False, f"Subject entity {sub_id} does not exist in domain ontology"
            if not ontology.contains_entity(obj_id):
                return False, f"Object entity {obj_id} does not exist in domain ontology"

            if proposed_observation.predicate != parsed_attestation.predicate_span:
                return False, f"ProposedObservation predicate '{proposed_observation.predicate}' != ParsedAttestation predicate '{parsed_attestation.predicate_span}'"

            if proposed_observation.t_knowledge != source_record.t_knowledge:
                return False, f"ProposedObservation t_k ({proposed_observation.t_knowledge}) != SourceRecord t_k ({source_record.t_knowledge})"

            if proposed_observation.t_valid_start != parsed_attestation.t_valid_start:
                return False, "ProposedObservation valid start does not match ParsedAttestation"
            if proposed_observation.t_valid_end != parsed_attestation.t_valid_end:
                return False, "ProposedObservation valid end does not match ParsedAttestation"

            if trusted_context.is_spoofed_origin:
                return False, "Spoofed claimed origin detected in SourceRecord"
            if trusted_context.authenticity == "UNVERIFIED" and not source_record.authenticated_origin.is_authenticated:
                return False, "Unauthenticated origin cannot produce ADMIT certificate for root fact"

            pred = parsed_attestation.predicate_span
            if pred not in trusted_context.authorization_scope and "*" not in trusted_context.authorization_scope:
                return False, f"Source lacks authorization scope for predicate '{pred}'"

            if trusted_context.max_claim_privilege != ClaimPrivilege.ROOT_FACT:
                return False, f"Source privilege {trusted_context.max_claim_privilege.value} cannot assert ROOT_FACT"

            if parsed_attestation.extracted_claim_type != ClaimType.FACTUAL_OBSERVATION:
                return False, f"Extracted claim type {parsed_attestation.extracted_claim_type.value} cannot assert ROOT_FACT"

            if not certificate.lineage_roots or proposed_observation.lineage_roots != certificate.lineage_roots:
                return False, "ADMIT certificate and Observation lineage roots must match non-empty trusted context roots"

            expected_root = trusted_context.independence_class
            if expected_root not in certificate.lineage_roots:
                return False, f"Lineage root '{expected_root}' missing from certificate lineage roots"

            return True, None

        # 2. Verification of DEFER certificates
        elif certificate.status == AdmissionStatus.DEFER:
            if not certificate.failed_constraint and not certificate.candidates_remaining:
                return False, "DEFER certificate must specify failed_constraint or candidates_remaining"
            return True, None

        # 3. Verification of REJECT certificates
        elif certificate.status == AdmissionStatus.REJECT:
            if not certificate.rejection_cause:
                return False, "REJECT certificate must declare rejection_cause"
            return True, None

        return False, f"Unknown admission status: {certificate.status}"

    @staticmethod
    def verify_resolution(
        deferred: DeferredBinding,
        chosen_subject_id: str,
        chosen_object_id: str,
        disambiguating_record: SourceRecord,
        original_source_record: SourceRecord,
        capability_registry: CapabilityPolicyRegistry,
        ontology: IngressOntology,
        certificate: ResolutionCertificate,
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Independently verify full ResolutionCertificate proof for a DeferredBinding."""
        if certificate.deferred_id != deferred.deferred_id:
            return False, f"Certificate deferred_id '{certificate.deferred_id}' != '{deferred.deferred_id}'"

        if certificate.chosen_subject_id != chosen_subject_id or certificate.chosen_object_id != chosen_object_id:
            return False, "Certificate chosen entities do not match requested resolution targets"

        if certificate.disambiguating_source_record_id != disambiguating_record.record_id:
            return False, f"Certificate disambiguating record ID '{certificate.disambiguating_source_record_id}' != '{disambiguating_record.record_id}'"

        if not certificate.resolution_witness:
            return False, "Certificate missing required resolution_witness"

        # Candidate Containment: chosen entity MUST be in original candidate hypothesis set!
        if chosen_subject_id not in deferred.subject_hypotheses.candidate_entity_ids:
            return False, f"Chosen subject '{chosen_subject_id}' is not in original candidate set {deferred.subject_hypotheses.candidate_entity_ids}"

        if chosen_object_id not in deferred.object_hypotheses.candidate_entity_ids:
            return False, f"Chosen object '{chosen_object_id}' is not in original candidate set {deferred.object_hypotheses.candidate_entity_ids}"

        # Ontology existence
        if not ontology.contains_entity(chosen_subject_id):
            return False, f"Resolved subject '{chosen_subject_id}' does not exist in domain ontology"
        if not ontology.contains_entity(chosen_object_id):
            return False, f"Resolved object '{chosen_object_id}' does not exist in domain ontology"

        # Disambiguating record verification & capability scope check
        dis_ctx = derive_trusted_source_context(disambiguating_record, capability_registry, independence_registry)
        if dis_ctx.is_spoofed_origin or dis_ctx.authenticity == "UNVERIFIED":
            return False, "Disambiguating record is unauthenticated or spoofed"

        if not capability_registry.can_disambiguate(disambiguating_record.authenticated_origin.verified_id, deferred.predicate):
            return False, f"Disambiguating principal '{disambiguating_record.authenticated_origin.verified_id}' lacks disambiguation authority for predicate '{deferred.predicate}'"

        # Lineage root preservation check: roots must match original source record provenance
        orig_ctx = derive_trusted_source_context(original_source_record, capability_registry, independence_registry)
        expected_root = orig_ctx.independence_class
        if certificate.lineage_roots != frozenset([expected_root]):
            return False, f"Certificate lineage roots {certificate.lineage_roots} != expected original source root '{expected_root}'"

        return True, None

    @staticmethod
    def verify_promotion(
        provisional: ProvisionalEntity,
        canonical_entity_id: str,
        canonical_name: str,
        entity_type: str,
        promotion_authority_record: SourceRecord,
        capability_registry: CapabilityPolicyRegistry,
        ontology: IngressOntology,
        certificate: PromotionCertificate,
        associated_relations: list[ProvisionalRelation],
        source_records_map: dict[str, SourceRecord],
        independence_registry: Optional[LineageIndependenceRegistry] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Independently verify full PromotionCertificate proof for promoting a ProvisionalEntity."""
        if certificate.provisional_id != provisional.provisional_id:
            return False, f"Certificate provisional_id '{certificate.provisional_id}' != '{provisional.provisional_id}'"

        if certificate.canonical_entity_id != canonical_entity_id:
            return False, f"Certificate canonical_entity_id '{certificate.canonical_entity_id}' != '{canonical_entity_id}'"

        if certificate.canonical_name != canonical_name:
            return False, f"Certificate canonical_name '{certificate.canonical_name}' != '{canonical_name}'"

        if certificate.entity_type != entity_type:
            return False, f"Certificate entity_type '{certificate.entity_type}' != '{entity_type}'"

        if certificate.promotion_authority_record_id != promotion_authority_record.record_id:
            return False, f"Certificate promotion_authority_record_id '{certificate.promotion_authority_record_id}' != '{promotion_authority_record.record_id}'"

        if not certificate.authority_witness:
            return False, "Certificate missing required authority_witness"

        # Collision Check: Canonical entity ID must NOT already exist in ontology
        if ontology.contains_entity(canonical_entity_id):
            return False, f"Canonical entity '{canonical_entity_id}' already exists in ontology (collision / hijacking rejected)"

        # Authority Check: Promoted by an authenticated ontology admin
        auth_ctx = derive_trusted_source_context(promotion_authority_record, capability_registry, independence_registry)
        if auth_ctx.is_spoofed_origin or auth_ctx.authenticity == "UNVERIFIED":
            return False, "Promotion authority record is unauthenticated or spoofed"

        if not capability_registry.is_ontology_admin(promotion_authority_record.authenticated_origin.verified_id):
            return False, f"Principal '{promotion_authority_record.authenticated_origin.verified_id}' lacks CANONICAL_ONTOLOGY_ADMIN capability"

        # Source Privilege Check: Underlying provisional relations from ATTESTATION_ONLY sources cannot become root facts
        for rel in associated_relations:
            orig_src = source_records_map.get(rel.source_record_id)
            if orig_src:
                orig_ctx = derive_trusted_source_context(orig_src, capability_registry, independence_registry)
                if orig_ctx.max_claim_privilege != ClaimPrivilege.ROOT_FACT:
                    return False, f"Underlying relation '{rel.relation_id}' originated from privilege-restricted source '{orig_src.authenticated_origin.verified_id}'"

        return True, None
