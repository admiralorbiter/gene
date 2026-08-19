"""Unit tests for Ollama client and mock client."""

from __future__ import annotations

from gene.ollama_client import FakeOllamaClient, OllamaClient


def test_fake_ollama_client_chat():
    client = FakeOllamaClient()
    result = client.chat(
        model_name="gemma3:12b",
        system_prompt="System instructions",
        user_prompt="User question",
    )

    assert result.model_name == "gemma3:12b"
    assert result.prompt_tokens == 120
    assert result.completion_tokens == 45
    assert result.latency_ms > 0
    assert result.parsed_json is not None
    assert result.parsed_json["answer"]["subject"] == "VELORA"


def test_fake_ollama_client_metadata():
    client = FakeOllamaClient()
    info = client.get_model_info("gemma3:12b")
    assert info.model_name == "gemma3:12b"
    assert "sha256:" in info.digest
    assert info.family == "gemma3"
