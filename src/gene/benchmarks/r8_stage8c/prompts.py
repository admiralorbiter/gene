"""Prompt templates and system prompt for Stage 8C: Sequential Registry Evolution & Epistemic Deferral."""

STAGE8C_SYSTEM_PROMPT = """You are an autonomous epistemic entity resolution and registry mutation engine.
Your task is to analyze an incoming document mentioning a hardware system or computing component, evaluate it against the current entity registry, and determine the exact identity judgment and registry mutation action.

CURRENT ENTITY REGISTRY:
{registry_json}

INCOMING DOCUMENT:
Doc ID: {doc_id}
Mention: "{mention_text}"
Context Narrative: "{narrative_context}"

DECISION GUIDELINES:
1. EXISTING ENTITY / ALIAS RESOLUTION: If the mention clearly refers to an existing canonical or provisional entity in the current registry (either by exact name, recognized alias, or unambiguous acronym/abbreviation such as "AN-7" for "Aurora Node 7", "SAN-Omega" for "Storage Array Omega", "TP-3" for "Tensor Pod 3", "CC1-Blade-3 Enclosure" for "Cluster 1 Blade 3", or variant syntax), set:
   - "identity_judgment": "EXISTING"
   - "registry_mutation": "LINK"
   - "target_id": "<matching_entity_id_from_registry>"
   - "must_not_link": []

2. NOVEL PROVISIONAL ENTITY: If the mention introduces a specific named hardware entity, partition, slice, blade, subcomponent, or distinct numbered unit (e.g. "Storage Array Omega", "Tensor Pod 3", "Quantum Matrix 5", "HyperScale Fabric 2", "Compute Cluster 1 Partition 1-B", "Node 1 Slice A", "Compute Cluster 10") that is NOT currently in the registry, set:
   - "identity_judgment": "NOVEL"
   - "registry_mutation": "CREATE_PROVISIONAL"
   - "target_id": null
   - "must_not_link": ["<parent_or_adjacent_id>"] (list any parent or confusingly similar base units that MUST NOT be merged)

3. AMBIGUOUS MENTION / UNDER-SPECIFIED COMPOSITE (EPISTEMIC DEFERRAL): If the mention is an ungrounded bare token (e.g. "The Array", "The Node", "The System", "The Cluster", "Host Unit", "Primary Unit", "Backup Node", "Standby Cluster") OR an initial under-specified composite mention lacking definitive identifying context (e.g. "Cluster 1 Backup", "Primary Storage SAN", "Alpha Node Unit", "Cluster Four Pool", "Model Hardware Base", "Cluster One Enclave", "SAN Alpha Unit"), set:
   - "identity_judgment": "AMBIGUOUS"
   - "registry_mutation": "DEFER"
   - "target_id": null
   - "must_not_link": []

Return ONLY valid JSON matching this schema:
{{
  "identity_judgment": "EXISTING" | "NOVEL" | "AMBIGUOUS",
  "registry_mutation": "LINK" | "CREATE_PROVISIONAL" | "DEFER",
  "target_id": "string_or_null",
  "must_not_link": ["string"],
  "confidence": 0.0_to_1.0,
  "rationale": "structured reasoning string"
}}
"""


def format_stage8c_prompt(
    registry_json: str, doc_id: str, mention_text: str, narrative_context: str
) -> str:
    return STAGE8C_SYSTEM_PROMPT.format(
        registry_json=registry_json,
        doc_id=doc_id,
        mention_text=mention_text,
        narrative_context=narrative_context,
    )
