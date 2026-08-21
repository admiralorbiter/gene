"""Prompt templates for Stage 8B Multi-Document Coreference Resolution & Ingress Fusion."""

STAGE8B_SYSTEM_PROMPT = """You are the Epistemic Ingress Agent for the GENE platform.
Your task is to analyze telemetry records and document streams, resolving entity mentions and extracting structured factual attestations as valid JSON.
Extract the exact entity names or spans as mentioned in the observation.

Output strictly valid JSON with these keys:
{
  "subject_span": "<exact name or span of the subject entity>",
  "predicate_span": "<predicate or attribute being stated>",
  "object_span": "<exact name or value of the object / status>",
  "t_valid_start": <float start time of validity>,
  "t_valid_end": <float end time or null if ongoing>,
  "is_subject_novel": <boolean>,
  "is_object_novel": <boolean>,
  "extracted_claim_type": "FACTUAL_OBSERVATION",
  "reasoning": "<concise explanation>"
}
"""

def format_stage8b_prompt(narrative: str, prior_context: str | None = None) -> str:
    """Format observation text and optional prior document context for Stage 8B extraction."""
    ctx_block = f"\nPrior Document Stream Context:\n\"\"\"{prior_context}\"\"\"\n" if prior_context else ""
    return f"""Analyze the following telemetry record and extract the core factual attestation.{ctx_block}
Observation Record:
\"\"\"{narrative}\"\"\"

Extract the subject, predicate, object, and temporal validity interval.
Return ONLY valid JSON.
"""
