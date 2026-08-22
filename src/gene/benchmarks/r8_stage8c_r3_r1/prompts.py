"""Prompt templates and formatting for Stage 8C-R3-R1 (CONTRACT-R8-8C-R3-R1)."""

from typing import Any, Dict, List


STAGE8C_R3_R1_SYSTEM_PROMPT = """You are an epistemic entity resolution and ontology management assistant.
Your goal is to evaluate mentions of systems, hardware partitions, and infrastructure components in telemetry or change logs.

You must return a JSON response with:
1. "candidate_action": One of "LINK_EXISTING", "CREATE_PROVISIONAL", "DEFER"
2. "target_entity_id": The exact canonical or provisional entity_id if linking, else null
3. "confidence": A float between 0.0 and 1.0
4. "rationale": Brief explanation of your reasoning

Guidelines:
- If a mention refers to an existing entity (canonical or provisional) by exact name, registered alias, or clear unambiguous reference, propose LINK_EXISTING.
- If a mention asserts the commissioning, deployment, or existence of a new standalone system not yet in the registry, propose CREATE_PROVISIONAL.
- If a mention refers to a structural sub-component (e.g. partition, blade, slice) that lacks a grounded entity identity, or is ambiguous, negated, hypothetical, or under dispute, propose DEFER.
- Never guess or merge distinct entities without strong evidence.
"""


def format_stage8c_r3_r1_prompt(
    doc_id: str,
    source_id: str,
    mention: str,
    context: str,
    durable_registry: Dict[str, Any],
) -> str:
    """Formats the complete prompt incorporating the system instructions, current durable registry, and document mention."""
    entities_formatted = []
    for eid, edata in sorted(durable_registry.items()):
        cname = edata.get("canonical_name", "")
        status = edata.get("status", "canonical")
        aliases = edata.get("aliases", [])
        alias_str = f", aliases: {', '.join(aliases)}" if aliases else ""
        entities_formatted.append(f"- [{eid}] {cname} (status: {status}{alias_str})")

    reg_text = "\n".join(entities_formatted) if entities_formatted else "(Empty registry)"

    return f"""{STAGE8C_R3_R1_SYSTEM_PROMPT}

Current Durable Entity Registry:
{reg_text}

New Document Event:
- Document ID: {doc_id}
- Source ID: {source_id}
- Surface Mention: "{mention}"
- Surrounding Context: "{context}"

Evaluate the mention and provide your JSON proposal:"""
