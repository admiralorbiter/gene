"""Data models for Stage 7B Live Neural Ingress Benchmark."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from gene.supersession_engine import BitemporalFact


@dataclass(frozen=True)
class LiveIngressCase:
    """A single test world case in the 52-call live neural ingress benchmark."""
    case_id: str
    case_type: str  # "PRIMARY_FACTORIAL" | "COUNTERBALANCED_ORDER" | "CANARY_REPLAY"
    raw_text: str
    predicate_name: str
    predicate_mode: str  # "TIME_VARYING" | "ADDITIVE" | "EPISODIC" | "INTERVAL_BOUNDED"
    linguistic_phenomenon: str  # "EXACT_MATCH" | "LEXICAL_ALIAS" | "TRUE_AMBIGUITY" | "NOVEL_ENTITY"
    source_privilege_class: str  # "AUTHORIZED_SENSOR" | "UNPRIVILEGED_GUEST"
    claimed_source: str
    claimed_role: str
    authenticated_identity: str
    auth_method: str
    is_authenticated: bool
    t_knowledge: int
    t_valid_start: float
    t_valid_end: Optional[float]
    gold_subject_id: Optional[str]
    gold_object_id: Optional[str]
    subject_candidate_options: tuple[str, ...]
    object_candidate_options: tuple[str, ...]
    is_subject_novel: bool
    is_object_novel: bool
    gold_slot_position: Optional[int] = None
    baseline_occurrence: Optional[BitemporalFact] = None


@dataclass(frozen=True)
class LiveNeuralExtraction:
    """Parsed structured output emitted by the neural model."""
    subject_span: str
    predicate_span: str
    object_span: str
    t_valid_start: float
    t_valid_end: Optional[float]
    selected_subject_candidate: Optional[str]
    selected_object_candidate: Optional[str]
    is_subject_novel: bool
    is_object_novel: bool
    extracted_claim_type: str
    confidence_score: float = 1.0
    reasoning: str = ""
