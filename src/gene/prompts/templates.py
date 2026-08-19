"""Versioned prompt templates and deterministic hashing for GENE experiments."""

from __future__ import annotations

import hashlib
from typing import Any


PROMPT_V1_SYSTEM = """You are an epistemic reasoning agent operating in a strictly controlled information environment.
Your task is to answer questions about entities, locations, protocols, and organizational structures using ONLY the provided memory records.

You MUST respond with a valid JSON object matching this exact schema:
{
  "answer": {
    "subject": "<ENTITY_SUBJECT>",
    "predicate": "<RELATION_PREDICATE>",
    "object": "<ENTITY_OBJECT_OR_VALUE>"
  },
  "parent_memory_ids": ["<MEM_ID_1>", "<MEM_ID_2>"],
  "confidence": <FLOAT_BETWEEN_0_AND_1>,
  "explanation": "<CONCISE_ONE_SENTENCE_EXPLANATION>"
}

Rules:
1. "answer" must contain:
   - "subject": MUST match the exact "Target Subject" specified in the prompt.
   - "predicate": MUST match the exact "Target Predicate" specified in the prompt.
   - "object": the entity, name, or value that answers the question.
2. "parent_memory_ids" must list ONLY the IDs of the memory records you directly used to derive your answer. Do not guess or invent memory IDs.
3. Output ONLY the JSON object. Do not include markdown codeblocks or extra text.
"""

PROMPT_V1_USER_TEMPLATE = """Available Memories:
{memories_block}

Question:
{question_prompt}

Target Subject: {target_subject}
Target Predicate: {target_predicate}

Provide your structured JSON response:"""


class PromptTemplate:
    """Versioned prompt builder with SHA256 template hashing."""

    def __init__(self, version: str = "v1"):
        self.version = version
        if version == "v1":
            self.system_prompt = PROMPT_V1_SYSTEM
            self.user_template = PROMPT_V1_USER_TEMPLATE
        else:
            raise ValueError(f"Unknown prompt version: {version}")

    def prompt_hash(self) -> str:
        """Compute SHA256 hash of the template specification."""
        combined = f"{self.version}\n{self.system_prompt}\n{self.user_template}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def format_user_prompt(
        self,
        memories: list[dict[str, str]],
        question_prompt: str,
        target_subject: str,
        target_predicate: str,
    ) -> str:
        """Format the user prompt with explicit memory IDs and question content."""
        mem_lines = []
        for mem in memories:
            mem_id = mem["memory_id"]
            text = mem["text"]
            mem_lines.append(f"[{mem_id}] {text}")

        memories_block = "\n".join(mem_lines) if mem_lines else "[No memories provided]"
        return self.user_template.format(
            memories_block=memories_block,
            question_prompt=question_prompt,
            target_subject=target_subject,
            target_predicate=target_predicate,
        )
