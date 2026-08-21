"""Prompt templates for Stage 7B Live Neural Ingress Assay."""

from __future__ import annotations

import json
from gene.benchmarks.ingress_live.models import LiveIngressCase

SYSTEM_PROMPT = """You are the Semantic Ingress Extraction & Entity Disambiguation Unit for the GENE Epistemic Kernel.
Your job is to read raw input text, extract semantic spans, temporal validity intervals, and map mentions to provided ontology candidate options.

STRICT PROTOCOL RULES:
1. Extract the exact textual mention spans for Subject, Predicate, and Object.
2. Extract the Valid Time start and end (float). If no explicit end time is given, set t_valid_end to null.
3. Match the extracted Subject and Object spans against the provided Candidate Options:
   - If an exact or alias match is clear, select that candidate ID.
   - If the mention is genuinely ambiguous among multiple candidates, select the single candidate that best fits OR declare is_novel=false with multiple matching candidates.
   - If the mention represents a genuinely novel entity not present in the candidate options, set is_novel=true and selected_candidate to null.
4. Extract the claim type: "FACTUAL_OBSERVATION", "OPERATOR_PREFERENCE", "QUOTED_TELEMETRY", or "HYPOTHETICAL_DERIVATION".
5. Output ONLY a valid JSON object matching the requested schema. Do NOT include markdown code fences or conversational filler."""


def format_live_ingress_prompt(case: LiveIngressCase) -> str:
    """Format user prompt for live model extraction."""
    payload = {
        "task": "EXTRACT_SEMANTIC_INGRESS_AND_BIND_CANDIDATES",
        "raw_text": case.raw_text,
        "source_metadata": {
            "claimed_source": case.claimed_source,
            "claimed_role": case.claimed_role,
            "t_knowledge": case.t_knowledge,
        },
        "candidate_ontology_options": {
            "subject_candidates": list(case.subject_candidate_options),
            "object_candidates": list(case.object_candidate_options),
        },
        "expected_predicate": case.predicate_name,
        "json_schema": {
            "subject_span": "string (verbatim substring from text)",
            "predicate_span": "string (target predicate name)",
            "object_span": "string (verbatim substring from text)",
            "t_valid_start": "float",
            "t_valid_end": "float or null",
            "selected_subject_candidate": "string or null (exact candidate ID from options)",
            "selected_object_candidate": "string or null (exact candidate ID from options)",
            "is_subject_novel": "boolean",
            "is_object_novel": "boolean",
            "extracted_claim_type": "string (FACTUAL_OBSERVATION | OPERATOR_PREFERENCE | QUOTED_TELEMETRY | HYPOTHETICAL_DERIVATION)",
            "reasoning": "brief explanation",
        }
    }
    return json.dumps(payload, indent=2)
