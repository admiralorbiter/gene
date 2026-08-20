"""Unit tests for the hardened ExplorationHarness."""

import json
from pathlib import Path
import sqlite3
import pytest

from gene.experiments.exploration_harness import (
    ExplorationHarness,
    ExplorationCallRecord,
    ExplorationEvaluationRecord,
    LexicalLeakageError,
)
from gene.ollama_client import CallSpec, FakeOllamaClient


def test_exploration_harness_lexical_leak_detection():
    """Verify that schema lexical answer leakage is detected accurately."""
    leaking_prompt = (
        "RULES: ...\n"
        "RETRIEVED MEMORIES:\n- mem_01: text\n\n"
        "QUESTION: What is the protocol?\n"
        'Return strictly JSON: {"protocol": "PROTO_X7", "cited_memory_ids": ["mem_mgr", "mem_sup"]}'
    )
    clean_prompt = (
        "RULES: ...\n"
        "RETRIEVED MEMORIES:\n- mem_01: text\n\n"
        "QUESTION: What is the protocol?\n"
        'Return strictly JSON: {"protocol": "PROTOCOL_NAME_OR_UNKNOWN", "cited_memory_ids": ["id1", "id2"]}'
    )

    has_leak, leaked = ExplorationHarness.audit_prompt_for_lexical_leakage(leaking_prompt, ["PROTO_X7", "mem_mgr"])
    assert has_leak is True
    assert "PROTO_X7" in leaked
    assert "mem_mgr" in leaked

    has_leak_clean, leaked_clean = ExplorationHarness.audit_prompt_for_lexical_leakage(clean_prompt, ["PROTO_X7", "mem_mgr"])
    assert has_leak_clean is False
    assert len(leaked_clean) == 0


def test_exploration_harness_pre_execution_leak_fail_closed(tmp_path: Path):
    """Verify that a leaked prompt raises LexicalLeakageError before issuing network call."""
    db_file = tmp_path / "test_leak.db"
    fake_client = FakeOllamaClient()
    harness = ExplorationHarness(db_path=db_file, track_name="test_leak_track", client=fake_client)

    leaking_spec = CallSpec(
        model_name="fake:model",
        system_prompt="Test",
        user_prompt='QUESTION: Who is manager? Return strictly: {"manager": "NERIN"}',
    )

    with pytest.raises(LexicalLeakageError) as exc_info:
        harness.execute_call(
            call_id="call_leaking_01",
            spec=leaking_spec,
            forbidden_schema_leaks=["NERIN"],
            fail_on_lexical_leak=True,
        )

    assert "Pre-execution lexical leak audit failed" in str(exc_info.value)
    assert "NERIN" in str(exc_info.value)


def test_exploration_harness_full_provenance_and_evaluations(tmp_path: Path):
    """Verify complete runs, calls, evaluations persistence with full CallSpec hash and foreign keys."""
    db_file = tmp_path / "test_full_harness.db"
    canned = {
        "protocol": {
            "protocol": "PROTO_X7",
            "evidence_status": "sufficient",
            "cited_memory_ids": ["m1", "m2"],
        }
    }
    fake_client = FakeOllamaClient(canned_responses=canned)
    harness = ExplorationHarness(db_path=db_file, track_name="track_a", client=fake_client, config={"seed": 42})

    spec = CallSpec(
        model_name="fake:model",
        system_prompt="Test system",
        user_prompt="QUESTION: What protocol? Return strictly: {\"protocol\": \"PROTOCOL_OR_UNKNOWN\"}",
        temperature=0.0,
        seed=42,
    )

    # 1. Execute Call
    call_rec = harness.execute_call(
        call_id="call_001",
        spec=spec,
        forbidden_schema_leaks=["PROTO_X7"],
        metadata={"station": "VELORA"},
    )

    assert isinstance(call_rec, ExplorationCallRecord)
    assert call_rec.call_id == "call_001"
    assert len(call_rec.call_spec_sha256) == 64
    assert call_rec.emitted_claim == "PROTO_X7"
    assert call_rec.evidence_status == "sufficient"
    assert call_rec.cited_memory_ids == ["m1", "m2"]

    # 2. Record Structured Evaluation
    eval_rec = harness.record_evaluation(
        call_id="call_001",
        canonical_status="TRUE",
        local_status="TRUE",
        dual_oracle_phenotype="ACTIVE_TRUE",
        is_contract_compliant=True,
        metadata={"falsified": False},
    )

    assert isinstance(eval_rec, ExplorationEvaluationRecord)
    assert eval_rec.eval_id == "eval_call_001"
    assert eval_rec.dual_oracle_phenotype == "ACTIVE_TRUE"

    # 3. Verify SQLite Tables Integrity
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Check Run
    run_row = c.execute("SELECT run_id, track_name, config_json FROM exploration_runs WHERE run_id = ?", (harness.run_id,)).fetchone()
    assert run_row is not None
    assert run_row[1] == "track_a"
    assert json.loads(run_row[2]) == {"seed": 42}

    # Check Call
    call_row = c.execute("SELECT call_id, run_id, call_spec_sha256, emitted_claim, cited_memory_ids FROM exploration_calls WHERE call_id = ?", ("call_001",)).fetchone()
    assert call_row is not None
    assert call_row[0] == "call_001"
    assert call_row[1] == harness.run_id
    assert call_row[3] == "PROTO_X7"
    assert json.loads(call_row[4]) == ["m1", "m2"]

    # Check Evaluation
    eval_row = c.execute("SELECT eval_id, call_id, dual_oracle_phenotype FROM exploration_evaluations WHERE eval_id = ?", ("eval_call_001",)).fetchone()
    assert eval_row is not None
    assert eval_row[0] == "eval_call_001"
    assert eval_row[1] == "call_001"
    assert eval_row[2] == "ACTIVE_TRUE"

    conn.close()

    # 4. Verify Append-Only Strictness (Duplicate call_id raises IntegrityError)
    with pytest.raises(sqlite3.IntegrityError):
        harness.execute_call(call_id="call_001", spec=spec)
