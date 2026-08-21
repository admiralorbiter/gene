"""Core Data Models for Epistemic Ingress & Write Admission (Round 7)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class AdmissionStatus(str, Enum):
    """Result of an epistemic write admission evaluation."""
    ADMIT = "ADMIT"
    DEFER = "DEFER"
    REJECT = "REJECT"


class ClaimType(str, Enum):
    """Nature of the claim being admitted."""
    FACTUAL_OBSERVATION = "FACTUAL_OBSERVATION"
    OPERATOR_PREFERENCE = "OPERATOR_PREFERENCE"
    QUOTED_TELEMETRY = "QUOTED_TELEMETRY"
    HYPOTHETICAL_DERIVATION = "HYPOTHETICAL_DERIVATION"


@dataclass(frozen=True)
class CaptureProvenance:
    """Telemetry about physical receipt of the message by the platform."""
    connector_id: str
    ingress_channel: str
    t_received: int
    raw_payload_hash: str


@dataclass(frozen=True)
class ClaimedOrigin:
    """Origin entity claimed inside the textual payload."""
    claimed_source_name: str
    claimed_role: str = "reporter"


@dataclass(frozen=True)
class AuthenticatedOrigin:
    """Cryptographically or platform-verified identity of the sender."""
    verified_id: str
    auth_method: str  # e.g., "ED25519_SIGNATURE", "KERNEL_LOCAL", "OAUTH_TOKEN", "ANONYMOUS"
    is_authenticated: bool = False


@dataclass(frozen=True)
class SourceRecord:
    """Immutable, incontrovertible historical event observed by the runtime."""
    record_id: str
    raw_text: str
    capture_provenance: CaptureProvenance
    claimed_origin: ClaimedOrigin
    authenticated_origin: AuthenticatedOrigin
    t_knowledge: int


@dataclass(frozen=True)
class ParsedAttestation:
    """Fallible syntactic and semantic parse extracted from a SourceRecord."""
    attestation_id: str
    source_record_id: str
    subject_span: str
    predicate_span: str
    object_span: str
    t_valid_start: float
    t_valid_end: Optional[float] = None
    extracted_claim_type: ClaimType = ClaimType.FACTUAL_OBSERVATION
    raw_extraction_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BindingHypothesisSet:
    """Hypothesis space of candidate entity bindings for a mention span."""
    mention_span: str
    role: str  # "SUBJECT" | "OBJECT"
    candidate_entity_ids: tuple[str, ...]
    is_novel: bool = False
    retrieval_confidence: float = 1.0


@dataclass(frozen=True)
class DeferredBinding:
    """Unresolved candidate bindings preserved to avoid lossy premature collapse."""
    deferred_id: str
    source_record_id: str
    attestation_id: str
    subject_hypotheses: BindingHypothesisSet
    predicate: str
    object_hypotheses: BindingHypothesisSet
    t_valid_start: float
    t_valid_end: Optional[float] = None
    t_knowledge: int = 1
    reason_deferred: str = "AMBIGUOUS_CANDIDATE_SET"


@dataclass(frozen=True)
class ProvisionalEntity:
    """Novel entity preserved with raw evidence without polluting canonical namespace."""
    provisional_id: str
    first_mention_span: str
    first_source_record_id: str
    t_created_knowledge: int
    associated_attestation_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ProvisionalRelation:
    """Relation involving at least one provisional entity; held outside root facts."""
    relation_id: str
    subject_id: str
    predicate: str
    object_id: str
    t_valid_start: float
    t_valid_end: Optional[float]
    source_record_id: str
    is_subject_provisional: bool
    is_object_provisional: bool


@dataclass(frozen=True)
class SourceContext:
    """Multidimensional capability, reliability, and provenance context."""
    authenticity: str  # "CRYPTOGRAPHIC_VERIFIED" | "PLATFORM_LOCAL" | "UNVERIFIED"
    authorization_scope: frozenset[str]  # e.g., frozenset(["system_status", "temperature"])
    reliability_class: str  # "HIGH_PRECISION_SENSOR" | "HUMAN_OPERATOR" | "UNTRUSTED_WEB"
    independence_class: str  # e.g., "SENSOR_NET_A", "OPERATOR_ROOT_1"
    claim_type: ClaimType = ClaimType.FACTUAL_OBSERVATION


@dataclass(frozen=True)
class AdmissionCertificate:
    """Proof-carrying witness emitted by the admission gate."""
    status: AdmissionStatus
    binding_witness: Optional[dict[str, str]] = None  # {"subject": id, "object": id}
    schema_witness: Optional[str] = None
    temporal_witness: Optional[str] = None
    auth_witness: Optional[str] = None
    lineage_roots: frozenset[str] = field(default_factory=frozenset)
    failed_constraint: Optional[str] = None
    rejection_cause: Optional[str] = None
    candidates_remaining: Optional[tuple[str, ...]] = None
    evidence_needed: Optional[str] = None
