"""Deterministic Mock Tests for Stage 5C (Neural Revision Bridge).

Verifies that the 32-call factorial execution harness functions with 100% zero live compute
under deterministic mock model clients.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import pytest

from src.gene.experiments.neural_revision_bridge import (
    NeuralRevisionBridgeRunner,
    render_acquisition_prompt,
    render_arm1_raw_revision_prompt,
    render_arm3_minimal_support_prompt,
    enumerate_entitling_supports,
)
from src.gene.experiments.stage5c_manifest import (
    build_stage5c_worlds,
    generate_stage5c_manifest,
    PINNED_STAGE5C_MODEL,
    PINNED_STAGE5C_DIGEST,
)


def make_mock_client():
    """Create a deterministic mock client that responds according to prompt content."""
    def client_fn(system_prompt: str, user_prompt: str) -> str:
        # Check if prompt has "No active valid facts remain"
        if "No active valid facts remain" in user_prompt:
            return json.dumps({
                "status": "INDETERMINABLE",
                "answer": None,
                "cited_facts": [],
                "proposed_action": None,
                "action_confidence": None,
            })
        
        # Check target entity
        if "Station KESTREL" in user_prompt:
            ans = "PROTOCOL_OMEGA"
            action = "DEPLOY_PROTOCOL"
            facts = ["FACT_IND_A", "FACT_IND_B", "FACT_IND_D", "FACT_IND_E"]
        elif "Station ORION" in user_prompt:
            ans = "TIER_SIGMA"
            action = "AUTHORIZE_ENTRY"
            facts = ["FACT_SHP_A", "FACT_SHP_B", "FACT_SHP_D"]
        elif "Station VANGUARD" in user_prompt:
            ans = "CODE_EPSILON"
            action = "EXECUTE_DISPATCH"
            facts = ["FACT_SHO_A", "FACT_SHO_B", "FACT_SHO_D", "FACT_SHO_E"]
        elif "Station DRAKE" in user_prompt:
            ans = "LANE_THETA"
            action = "AUTHORIZE_ENTRY"
            facts = ["FACT_REC_A", "FACT_REC_B", "FACT_REC_C", "FACT_REC_D"]
        else:
            ans = "UNKNOWN"
            action = None
            facts = []

        # If it's a retracted prompt that severed all paths
        if "RETRACTION NOTICE" in user_prompt:
            if "FACT_IND_A" in user_prompt and "FACT_IND_D" in user_prompt and "RETRACTED / INVALID: [FACT_IND_A]" in user_prompt and "RETRACTED / INVALID: [FACT_IND_D]" in user_prompt:
                return json.dumps({
                    "status": "INDETERMINABLE",
                    "answer": None,
                    "cited_facts": [],
                    "proposed_action": None,
                    "action_confidence": 0.0,
                })
            if "FACT_SHP_A" in user_prompt and "RETRACTED / INVALID: [FACT_SHP_A]" in user_prompt:
                return json.dumps({
                    "status": "INDETERMINABLE",
                    "answer": None,
                    "cited_facts": [],
                    "proposed_action": None,
                    "action_confidence": 0.0,
                })
            if "FACT_SHO_A" in user_prompt and "FACT_SHO_D" in user_prompt and "RETRACTED / INVALID: [FACT_SHO_A]" in user_prompt and "RETRACTED / INVALID: [FACT_SHO_D]" in user_prompt:
                return json.dumps({
                    "status": "INDETERMINABLE",
                    "answer": None,
                    "cited_facts": [],
                    "proposed_action": None,
                    "action_confidence": 0.0,
                })
            if "FACT_REC_B" in user_prompt and "FACT_REC_C" in user_prompt and "RETRACTED / INVALID: [FACT_REC_B]" in user_prompt and "RETRACTED / INVALID: [FACT_REC_C]" in user_prompt:
                return json.dumps({
                    "status": "INDETERMINABLE",
                    "answer": None,
                    "cited_facts": [],
                    "proposed_action": None,
                    "action_confidence": 0.0,
                })

        return json.dumps({
            "status": "DETERMINABLE",
            "answer": ans,
            "cited_facts": facts,
            "proposed_action": action,
            "action_confidence": 0.95,
        })

    return client_fn


def test_stage5c_manifest_structure_non_destructive():
    """Verify that Stage 5C manifest generation is strictly non-destructive and deep-matches tracked file."""
    manifest = generate_stage5c_manifest(write=False)
    assert manifest["manifest_version"] == "2.0.0"
    assert manifest["execution_parameters"]["total_calls"] == 32
    assert len(manifest["calls"]) == 32

    # Check phase counts
    acq_calls = [c for c in manifest["calls"] if c["phase"] == "acquisition"]
    rev_calls = [c for c in manifest["calls"] if c["phase"] == "revision"]
    canary_calls = [c for c in manifest["calls"] if c["phase"] == "replay_canary"]

    assert len(acq_calls) == 4
    assert len(rev_calls) == 24
    assert len(canary_calls) == 4

    # Deep compare against tracked manifest file
    tracked_path = Path(__file__).resolve().parent.parent.parent / "data" / "exploration_round5_stage5c_manifest.json"
    assert tracked_path.exists(), "Tracked Stage 5C manifest file must exist!"
    with open(tracked_path, "r", encoding="utf-8") as f:
        tracked_manifest = json.load(f)

    assert manifest == tracked_manifest


def test_stage5c_backward_chaining_support_enumeration():
    """Verify that first-order backward-chaining enumerates exact minimal antichains across all worlds."""
    worlds = build_stage5c_worlds()
    
    # World IND: initial support is [[A, B], [D, E]]
    w_ind = worlds["W_IND"]
    all_facts_ind = set(w_ind.facts.keys())
    assert enumerate_entitling_supports(w_ind, all_facts_ind) == sorted([["FACT_IND_A", "FACT_IND_B"], ["FACT_IND_D", "FACT_IND_E"]])
    
    # Degraded (knock out D): leaves [[A, B]]
    deg_facts_ind = all_facts_ind - {"FACT_IND_D"}
    assert enumerate_entitling_supports(w_ind, deg_facts_ind) == [["FACT_IND_A", "FACT_IND_B"]]

    # Retracted (knock out A, D): leaves []
    ret_facts_ind = all_facts_ind - {"FACT_IND_A", "FACT_IND_D"}
    assert enumerate_entitling_supports(w_ind, ret_facts_ind) == []


def test_stage5c_mock_runner_execution(tmp_path: Path):
    """Verify that the NeuralRevisionBridgeRunner executes all 32 calls end-to-end with strict checks."""
    db_path = tmp_path / "test_stage5c.db"
    manifest_path = tmp_path / "test_manifest.json"
    
    manifest = generate_stage5c_manifest(write=False)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    mock_client = make_mock_client()

    runner = NeuralRevisionBridgeRunner(
        db_path=db_path,
        manifest_path=manifest_path,
        client_fn=mock_client,
        model_name=PINNED_STAGE5C_MODEL,
        model_digest=PINNED_STAGE5C_DIGEST,
        ollama_version="ollama_mock_0.5.0",
        git_commit="test_mock_commit",
    )

    results = runner.run_all_calls(tau_gate=0.5)
    assert len(results) == 32

    # Verify SQLite Persistence
    with sqlite3.connect(db_path) as conn:
        run_count = conn.execute("SELECT COUNT(*) FROM stage5c_runs").fetchone()[0]
        call_count = conn.execute("SELECT COUNT(*) FROM stage5c_calls").fetchone()[0]
        assert run_count == 1
        assert call_count == 32

    # Check Arm 3 (GENE Kernel) on DEGRADED states achieves 100% entitlement retention
    arm3_degraded = [r for r in results if r.phase == "revision" and r.arm == "arm3_gene_kernel" and r.condition == "DEGRADED"]
    assert len(arm3_degraded) == 4
    for r in arm3_degraded:
        assert r.status_runtime == "DETERMINABLE"
        assert r.status_model == "DETERMINABLE"
        assert r.is_correct_entitlement is True
        assert r.is_correct_semantic_answer is True

    # Check Arm 2 (Naive Reported) on DEGRADED states triggers false retractions when bloated
    arm2_degraded = [r for r in results if r.phase == "revision" and r.arm == "arm2_naive_reported" and r.condition == "DEGRADED"]
    assert len(arm2_degraded) == 4
    for r in arm2_degraded:
        # Bloated acquisition citation -> NaiveRetract = 1 -> runtime status is INDETERMINABLE
        assert r.status_runtime == "INDETERMINABLE"
        assert r.status_model == "DETERMINABLE"  # Model output remains uncorrupted
        assert r.is_correct_entitlement is False  # False retraction!

    # Check Replay Canaries
    canary_results = [r for r in results if r.phase == "replay_canary"]
    assert len(canary_results) == 4
    for c in canary_results:
        assert c.is_replay_exact_match is True
