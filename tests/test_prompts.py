"""Unit tests for prompt versioning and hashing."""

from __future__ import annotations

from gene.prompts.templates import PromptTemplate


def test_prompt_template_formatting():
    template = PromptTemplate(version="v1")
    hash1 = template.prompt_hash()
    hash2 = template.prompt_hash()
    assert hash1 == hash2
    assert len(hash1) == 64

    memories = [
        {"memory_id": "mem_01", "text": "Nerin is manager of Velora."},
        {"memory_id": "mem_02", "text": "Velora operates under Green protocol."},
    ]
    prompt = template.format_user_prompt(
        memories=memories,
        question_prompt="Who manages Velora?",
        target_subject="VELORA",
        target_predicate="manager",
    )
    assert "[mem_01] Nerin is manager of Velora." in prompt
    assert "[mem_02] Velora operates under Green protocol." in prompt
    assert "Who manages Velora?" in prompt
    assert "Target Subject: VELORA" in prompt
