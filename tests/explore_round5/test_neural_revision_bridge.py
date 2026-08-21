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
)
from src.gene.experiments.stage5c_manifest import build_stage5c_worlds, generate_stage5c_manifest


def make_mock_client(worlds: dict):
    """Create a deterministic mock client that responds according to prompt content."""
    def client_fn(prompt: str) -> str:
        # Check if prompt has "No active valid facts remain" or "RETRACTION NOTICE" that severs all paths
        if "No active valid facts remain" in prompt:
            return json.dumps({
                "status": "INDETERMINABLE",
                "answer": None,
                "cited_facts": [],
                "proposed_action": None,
                "action_confidence": None,
            })
        
        # Check target entity
        if "Station KESTREL" in prompt:
            ans = "PROTOCOL_OMEGA"
            action = "DEPLOY_PROTOCOL"
            facts = ["FACT_IND_A", "FACT_IND_B", "FACT_IND_D", "FACT_IND_E"]
        elif "Station ORION" in prompt:
            ans = "TIER_SIGMA"
            action = "AUTHORIZE_ENTRY"
            facts = ["FACT_SHP_A", "FACT_SHP_B", "FACT_SHP_D"]
        elif "Station VANGUARD" in prompt:
            ans = "CODE_EPSILON"
            action = "EXECUTE_DISPATCH"
            facts = ["FACT_SHO_A", "FACT_SHO_B", "FACT_SHO_D", "FACT_SHO_E"]
        elif "Station DRAKE" in prompt:
            ans = "LANE_THETA"
            action = "AUTHORIZE_ENTRY"
            facts = ["FACT_REC_A", "FACT_REC_B", "FACT_REC_C", "FACT_REC_D"]
        else:
            ans = "UNKNOWN"
            action = None
            facts = []

        # If it's a retracted prompt that severed all paths
        if "RETRACTION NOTICE" in prompt:
            if "FACT_IND_A" in prompt and "FACT_IND_D" in prompt and "RETRACTED / INVALID: [FACT_IND_A]" in prompt and "RETRACTED / INVALID: [FACT_IND_D]" in prompt:
                return json.dumps({
                    "status": "INDETERMINABLE",
                    "answer": None,
                    "cited_facts": [],
                    "proposed_action": None,
                    "action_confidence": 0.0,
                })
            if "FACT_SHP_A" in prompt and "RETRACTED / INVALID: [FACT_SHP_A]" in prompt:
                return json.dumps({
                    "status": "INDETERMINABLE",
                    "answer": None,
                    "cited_facts": [],
                    "proposed_action": None,
                    "action_confidence": 0.0,
                })
            if "FACT_SHO_A" in prompt and "FACT_SHO_D" in prompt and "RETRACTED / INVALID: [FACT_SHO_A]" in prompt and "RETRACTED / INVALID: [FACT_SHO_D]" in prompt:
                return json.dumps({
                    "status": "INDETERMINABLE",
                    "answer": None,
                    "cited_facts": [],
                    "proposed_action": None,
                    "action_confidence": 0.0,
                })
            if "FACT_REC_B" in prompt and "FACT_REC_C" in prompt and "RETRACTED / INVALID: [FACT_REC_B]" in prompt and "RETRACTED / INVALID: [FACT_REC_C]" in prompt:
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


def test_stage5c_manifest_structure(tmp_path: Path):
    """Verify that Stage 5C execution manifest generates all 32 required calls."""
    manifest = generate_stage5c_manifest()
    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["execution_parameters"]["total_calls"] == 32
    assert len(manifest["calls"]) == 32

    # Check phase counts
    acq_calls = [c for c in manifest["calls"] if c["phase"] == "acquisition"]
    rev_calls = [c for c in manifest["calls"] if c["phase"] == "revision"]
    canary_calls = [c for c in manifest["calls"] if c["phase"] == "replay_canary"]

    assert len(acq_calls) == 4
    assert len(rev_calls) == 24
    assert len(canary_calls) == 4


def test_stage5c_mock_runner_execution(tmp_path: Path):
    """Verify that the NeuralRevisionBridgeRunner executes all 32 calls end-to-end."""
    db_path = tmp_path / "test_stage5c.db"
    manifest_path = tmp_path / "test_manifest.json"
    
    manifest = generate_stage5c_manifest()
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    worlds = build_stage5c_worlds()
    mock_client = make_mock_client(worlds)

    runner = NeuralRevisionBridgeRunner(
        db_path=db_path,
        manifest_path=manifest_path,
        client_fn=mock_client,
        model_name="mock_gemma3",
    )

    results = runner.run_all_calls(tau_gate=0.5)
    assert len(results) == 32

    # Verify SQLite Persistence
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM stage5c_calls").fetchone()[0]
        assert count == 32

    # Check Arm 3 (GENE Kernel) on DEGRADED states achieves 100% entitlement retention
    arm3_degraded = [r for r in results if r.phase == "revision" and r.arm == "arm3_gene_kernel" and r.condition == "DEGRADED"]
    assert len(arm3_degraded) == 4
    for r in arm3_degraded:
        assert r.parsed_status == "DETERMINABLE"
        assert r.is_correct_entitlement is True
        assert r.is_correct_semantic_answer is True

    # Check Arm 2 (Naive Reported) on DEGRADED states triggers false retractions when bloated
    arm2_degraded = [r for r in results if r.phase == "revision" and r.arm == "arm2_naive_reported" and r.condition == "DEGRADED"]
    assert len(arm2_degraded) == 4
    for r in arm2_degraded:
        # Since mock acquisition cited all facts (bloated), invalidating any fact triggers NaiveRetract
        assert r.parsed_status == "INDETERMINABLE"
        assert r.is_correct_entitlement is False  # False retraction!
