"""Independent, Pure Certificate Verifier for Epistemic Ingress (Round 7)."""

from __future__ import annotations

from typing import Optional, Tuple

from gene.ingress.models import (
    AdmissionCertificate,
    AdmissionStatus,
    BindingHypothesisSet,
    ClaimPrivilege,
    ClaimType,
    ParsedAttestation,
    SourceRecord,
    TrustedSourceContext,
)
from gene.ingress.ontology import CapabilityPolicyRegistry, IngressOntology
from gene.supersession_engine import Observation, PredicateContract


class CertificateVerifier:
    """Pure, standalone proof-carrying certificate verification engine.
    
    Independently verifies:
    Certificate |-? ProposedAdmission given (SourceRecord, ParsedAttestation, BindingHypotheses, Ontology, Policy).
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
        trusted_context: TrustedSourceContext,
        certificate: AdmissionCertificate,
    ) -> Tuple[bool, Optional[str]]:
        """Verify that certificate legitimately justifies the proposed admission action."""

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

            # Verify that bound entities were legitimate candidate hypotheses
            if sub_id not in subject_hypotheses.candidate_entity_ids:
                return False, f"Bound subject {sub_id} not in subject candidate hypothesis set"
            if obj_id not in object_hypotheses.candidate_entity_ids:
                return False, f"Bound object {obj_id} not in object candidate hypothesis set"

            # Verify ontology existence
            if not ontology.contains_entity(sub_id):
                return False, f"Subject entity {sub_id} does not exist in domain ontology"
            if not ontology.contains_entity(obj_id):
                return False, f"Object entity {obj_id} does not exist in domain ontology"

            # Verify predicate consistency
            if proposed_observation.predicate != parsed_attestation.predicate_span:
                return False, f"ProposedObservation predicate '{proposed_observation.predicate}' != ParsedAttestation predicate '{parsed_attestation.predicate_span}'"

            # Verify transaction knowledge time
            if proposed_observation.t_knowledge != source_record.t_knowledge:
                return False, f"ProposedObservation t_k ({proposed_observation.t_knowledge}) != SourceRecord t_k ({source_record.t_knowledge})"

            # Verify temporal consistency
            if proposed_observation.t_valid_start != parsed_attestation.t_valid_start:
                return False, "ProposedObservation valid start does not match ParsedAttestation"
            if proposed_observation.t_valid_end != parsed_attestation.t_valid_end:
                return False, "ProposedObservation valid end does not match ParsedAttestation"

            # Verify origin authenticity and spoofing detection
            if trusted_context.is_spoofed_origin:
                return False, "Spoofed claimed origin detected in SourceRecord"
            if trusted_context.authenticity == "UNVERIFIED" and not source_record.authenticated_origin.is_authenticated:
                return False, "Unauthenticated origin cannot produce ADMIT certificate for root fact"

            # Verify capability and authorization scope
            pred = parsed_attestation.predicate_span
            if pred not in trusted_context.authorization_scope and "*" not in trusted_context.authorization_scope:
                return False, f"Source lacks authorization scope for predicate '{pred}'"

            # Verify claim privilege (ATTESTATION_ONLY cannot become ROOT_FACT)
            if trusted_context.max_claim_privilege != ClaimPrivilege.ROOT_FACT:
                return False, f"Source privilege {trusted_context.max_claim_privilege.value} cannot assert ROOT_FACT"

            # Verify extracted claim type
            if parsed_attestation.extracted_claim_type != ClaimType.FACTUAL_OBSERVATION:
                return False, f"Extracted claim type {parsed_attestation.extracted_claim_type.value} cannot assert ROOT_FACT"

            # Verify lineage root integrity
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
