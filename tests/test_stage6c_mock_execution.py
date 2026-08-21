"""Tests for Exploration Round 6 Stage 6C: Neural Observation Bridge."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from gene.experiments.neural_observation_bridge import (
    Stage6CBridgeRunner,
    build_user_prompt_n1,
    build_user_prompt_n2,
)
from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    EventType,
    Observation,
    PredicateContract,
    TemporalEvent,
    adjudicate_observation,
)


def test_generalized_relevant_occurrences_query():
    engine = BitemporalEngine(cautious_conflicts=True)
    f1 = BitemporalFact("occ_1", "Alice", "clearance", "ALPHA", roots=frozenset(["R0"]), source_id="s1")
    f2 = BitemporalFact("occ_2", "Alice", "clearance", "BETA", roots=frozenset(["R1"]), source_id="s1")
    engine.register_fact(f1)
    engine.register_fact(f2)

    # occ_1 valid in [0, 5)
    engine.record_event(TemporalEvent("e1", EventType.ASSERT, t_knowledge=0, event_seq=0, t_valid_start=0.0, t_valid_end=5.0, target_fact_id="occ_1"))
    # occ_2 valid in [10, inf)
    engine.record_event(TemporalEvent("e2", EventType.ASSERT, t_knowledge=1, event_seq=0, t_valid_start=10.0, target_fact_id="occ_2"))

    # At t_v=2.0, t_k=0 -> occ_1 is active
    rel0 = engine.get_relevant_occurrences("Alice", "clearance", 2.0, 0)
    assert len(rel0["active"]) == 1
    assert rel0["active"][0].fact_id == "occ_1"

    # At t_v=6.0, t_k=1 -> occ_1 is preceding, no active facts
    rel1 = engine.get_relevant_occurrences("Alice", "clearance", 6.0, 1)
    assert len(rel1["active"]) == 0
    assert len(rel1["preceding"]) == 1
    assert rel1["preceding"][0].fact_id == "occ_1"


def test_stage6c_mock_execution_and_sqlite_logging():
    manifest_path = Path(__file__).resolve().parent.parent / "data" / "exploration_round6_stage6c_manifest.json"
    assert manifest_path.exists(), "Stage 6C manifest must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    cases_file = manifest_path.parent / manifest["dataset_file"]
    cases = [json.loads(line) for line in open(cases_file, "r", encoding="utf-8") if line.strip()]

    # Deterministic fake client
    def fake_client_fn(sys_p: str, usr_p: str) -> str:
        if "epistemic state adjudicator" in sys_p:
            # Arm N1
            # Return plausible but naive direct assertions without supersession for odd cases
            for c in cases:
                if c["natural_language_text"] in usr_p:
                    gold = c["gold_transitions"]
                    return json.dumps({"events": gold})
            return json.dumps({"events": []})
        else:
            # Arm N2
            for c in cases:
                if c["natural_language_text"] in usr_p:
                    return json.dumps(c["gold_extraction"])
            return json.dumps({})

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_stage6c.db"
        runner = Stage6CBridgeRunner(
            db_path=db_path,
            manifest_path=manifest_path,
            client_fn=fake_client_fn,
            model_name="gemma3:12b-mock",
            model_digest="mock_digest_123",
            ollama_version="0.5.0-mock",
            git_commit="mock_commit_abc",
        )

        summary = runner.run_all(run_id="test_run_1")

        assert summary["total_calls"] == 28
        assert summary["canary_determinism"]["raw_determinism_rate"] == 1.0
        assert summary["canary_determinism"]["semantic_determinism_rate"] == 1.0

        n2 = summary["arm_n2_modular_extraction"]
        assert n2["layer_0_extraction_accuracy"] == 1.0
        assert n2["layer_a_transition_fidelity"] == 1.0
        assert n2["layer_b_premise_state_fidelity"] == 1.0
        assert n2["layer_c_entitlement_accuracy"] == 1.0

        # Verify SQLite contents
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        total_calls_db = c.execute("SELECT COUNT(*) FROM stage6c_calls").fetchone()[0]
        total_evals_db = c.execute("SELECT COUNT(*) FROM stage6c_evaluations").fetchone()[0]
        conn.close()

        assert total_calls_db == 28
        assert total_evals_db == 24
