"""Prompt templates for Stage 8A Autonomous Open-World Candidate Ingress."""

STAGE8A_SYSTEM_PROMPT = """You are the Epistemic Ingress Agent for the GENE platform.
Your task is to analyze raw observation text and extract candidate subject-predicate-object relations as structured JSON.
You must extract the exact entity names or spans as mentioned in the observation.

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

def format_open_ingress_prompt(narrative: str) -> str:
    """Format raw observation text for open candidate hypothesis extraction without candidate menus."""
    return f"""Analyze the following telemetry record and extract the core factual attestation.

Observation Record:
\"\"\"{narrative}\"\"\"

Extract the subject, predicate, object, and temporal validity interval.
Return ONLY valid JSON.
"""

def format_menu_assisted_prompt(narrative: str, subject_menu: list[str], object_menu: list[str]) -> str:
    """Format observation text with finite candidate menus for paired baseline control."""
    sub_opts = "\n".join(f"- {s}" for s in subject_menu)
    obj_opts = "\n".join(f"- {o}" for o in object_menu)
    return f"""Analyze the following telemetry record and extract the core factual attestation.

Candidate Subject Options:
{sub_opts}

Candidate Object Options:
{obj_opts}

Observation Record:
\"\"\"{narrative}\"\"\"

Select the matching candidate options and extract temporal validity interval.
Return ONLY valid JSON.
"""
