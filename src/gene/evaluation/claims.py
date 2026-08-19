"""Claim parsing, normalization, and mechanical oracle evaluation."""

from __future__ import annotations

import json
from typing import Any, Literal
from pydantic import BaseModel, Field
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.schema import Fact, compute_fact_id


class StructuredAnswer(BaseModel):
    subject: str
    predicate: str
    object: str


class StructuredResponse(BaseModel):
    """Schema for model responses."""
    answer: StructuredAnswer
    parent_memory_ids: list[str] = Field(default_factory=list)
    confidence: float | None = 1.0
    explanation: str | None = None


class EvaluatedClaim(BaseModel):
    """The canonical outcome of parsing and mechanically evaluating a model's claim."""
    claim_id: str
    subject: str
    predicate: str
    object: str
    parse_status: Literal["success", "malformed_json", "missing_fields", "unparseable"]
    truth_status: TruthStatus
    infection_status: Literal["clean", "infected", "repaired", "de_novo", "unresolved"]
    reported_parent_ids: list[str]
    confidence: float | None = None
    explanation: str | None = None
    raw_response_text: str = ""

    def to_fact(self) -> Fact:
        """Convert normalized claim to a canonical Fact object."""
        return Fact(
            subject=self.subject,
            predicate=self.predicate,
            object=self.object,
            truth_value=(self.truth_status == TruthStatus.TRUE),
            source_type="derived",
            fact_id=self.claim_id,
        )


class ClaimEvaluator:
    """Parser and normalizer for model claims and oracle evaluations."""

    @classmethod
    def evaluate_response(
        cls,
        raw_text: str,
        parsed_json: dict[str, Any] | None,
        oracle: Oracle,
        condition: str = "clean",
    ) -> EvaluatedClaim:
        """Parse structured model response, normalize strings, and evaluate against oracle."""
        if not parsed_json:
            try:
                parsed_json = json.loads(raw_text)
            except Exception:
                pass

        if not parsed_json or not isinstance(parsed_json, dict):
            return EvaluatedClaim(
                claim_id="claim_unparseable",
                subject="UNKNOWN",
                predicate="unknown",
                object="UNKNOWN",
                parse_status="malformed_json",
                truth_status=TruthStatus.UNSUPPORTED,
                infection_status="unresolved",
                reported_parent_ids=[],
                raw_response_text=raw_text,
            )

        try:
            structured = StructuredResponse.model_validate(parsed_json)
        except Exception:
            return EvaluatedClaim(
                claim_id="claim_missing_fields",
                subject="UNKNOWN",
                predicate="unknown",
                object="UNKNOWN",
                parse_status="missing_fields",
                truth_status=TruthStatus.UNSUPPORTED,
                infection_status="unresolved",
                reported_parent_ids=[],
                raw_response_text=raw_text,
            )

        # Normalize subject, predicate, object
        norm_subj = structured.answer.subject.strip().upper().replace(" ", "_")
        norm_pred = structured.answer.predicate.strip().lower().replace(" ", "_")
        norm_obj = structured.answer.object.strip().upper().replace(" ", "_")

        claim_id = compute_fact_id(norm_subj, norm_pred, norm_obj)
        truth_status = oracle.evaluate_triple(norm_subj, norm_pred, norm_obj)

        # Determine initial infection status
        if truth_status == TruthStatus.TRUE:
            infection_status = "clean"
        elif truth_status in (TruthStatus.FALSE, TruthStatus.CONTRADICTION):
            # In clean condition or prior to causal tracing, unexpected false claim is de novo
            infection_status = "de_novo"
        else:
            infection_status = "unresolved"

        return EvaluatedClaim(
            claim_id=claim_id,
            subject=norm_subj,
            predicate=norm_pred,
            object=norm_obj,
            parse_status="success",
            truth_status=truth_status,
            infection_status=infection_status,
            reported_parent_ids=structured.parent_memory_ids,
            confidence=structured.confidence,
            explanation=structured.explanation,
            raw_response_text=raw_text,
        )
