"""Unit tests for the standardized ExplorationHarness."""

import json
from pathlib import Path
import sqlite3
import pytest

from gene.experiments.exploration_harness import ExplorationHarness, ExplorationCallRecord
from gene.ollama_client import CallSpec, FakeOllamaClient


def test_exploration_harness_answer_leak_detection():
    """Verify that schema answer leakage is flagged automatically."""
    leaking_prompt = (
        "RULES: ...\n"
        "RETRIEVED MEMORIES:\n- mem_01: text\n\n"
        "QUESTION: What is the protocol?\n"
        'Return schema: {"protocol": "PROTO_X7", "cited_memory_ids": ["mem_mgr", "mem_sup"]}'
    )
    clean_prompt = (
        "RULES: ...\n"
        "RETRIEVED MEMORIES:\n- mem_01: text\n\n"
        "QUESTION: What is the protocol?\n"
        'Return schema: {"protocol": "PROTOCOL_NAME_OR_UNKNOWN", "cited_memory_ids": ["id1", "id2"]}'
    )

    assert ExplorationHarness.audit_prompt_for_leakage(leaking_prompt, ["PROTO_X7", "mem_mgr"]) is True
    assert ExplorationHarness.audit_prompt_for_leakage(clean_prompt, ["PROTO_X7", "mem_mgr"]) is False


def test_exploration_harness_execution_and_persistence(tmp_path: Path):
    """Verify standardized record creation and SQLite persistence."""
    db_file = tmp_path / "test_exploration.db"
    canned = {
        "protocol": {
            "protocol": "PROTO_X7",
            "evidence_status": "sufficient",
            "cited_memory_ids": ["m1", "m2"],
        }
    }
    fake_client = FakeOllamaClient(canned_responses=canned)
    harness = ExplorationHarness(db_path=db_file, track_name="test_track", client=fake_client)

    spec = CallSpec(
        model_name="fake:model",
        system_prompt="Test system",
        user_prompt="QUESTION: What protocol? Return schema: {\"protocol\": \"PROTOCOL_OR_UNKNOWN\"}",
    )

    record = harness.execute_call(
        call_id="call_test_01",
        spec=spec,
        forbidden_schema_leaks=["PROTO_X7"],
        metadata={"world_id": "test_w1"},
    )

    assert isinstance(record, ExplorationCallRecord)
    assert record.call_id == "call_test_01"
    assert record.emitted_claim == "PROTO_X7"
    assert record.evidence_status == "sufficient"
    assert record.cited_memory_ids == ["m1", "m2"]
    assert record.has_answer_leak is False

    # Check SQLite persistence
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    row = c.execute("SELECT call_id, track_name, emitted_claim, cited_memory_ids FROM exploration_calls WHERE call_id = ?", ("call_test_01",)).fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "call_test_01"
    assert row[1] == "test_track"
    assert row[2] == "PROTO_X7"
    assert json.loads(row[3]) == ["m1", "m2"]
