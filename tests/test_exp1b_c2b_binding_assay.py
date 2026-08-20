"""Tests for Experiment 1B-C2b Binding Disambiguation and Proofreading Assay."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from gene.persistence.db import Database
from run_exp1b_c2b_binding_assay import build_c2b_prompt_and_worlds, evaluate_epistemic_proofreading, run_exp1b_c2b_assay


def test_build_c2b_prompt_and_worlds_geometry():
    """Verify geometry across all 5 binding conditions."""
    for cond in ["no_route", "foreign_station_wrong_route", "target_station_wrong_route", "foreign_station_target_route", "valid_target_route"]:
        memories, can_w, ctx_w, task, meta = build_c2b_prompt_and_worlds("KESTREL", "VELORA", cond, seed=7000)
        assert len(memories) == 6
        assert len(can_w.facts) == 8
        assert len(can_w.rules) == 3
        if cond == "valid_target_route":
            assert meta["path_is_supported"] is True
        else:
            assert meta["path_is_supported"] is False


def test_epistemic_proofreader_logic():
    """Verify that Layer 2 proofreader accepts valid derivations and rejects unifications."""
    memories, can_w, _, _, _ = build_c2b_prompt_and_worlds("KESTREL", "VELORA", "valid_target_route", seed=7000)

    # Valid derivation
    valid_resp = {
        "evidence_status": "sufficient",
        "answer": {"subject": "KESTREL", "predicate": "terminal_auth", "object": "AUTH_ALPHA_KESTREL"},
        "parent_memory_ids": ["mem_kestrel_transit_route", "mem_kestrel_facility_grid"],
    }
    p_valid = evaluate_epistemic_proofreading(valid_resp, memories, "KESTREL", "AUTH_ALPHA_KESTREL", can_w.rules)
    assert p_valid["proofreader_verdict"] == "PASS_VALID_DERIVATION"
    assert p_valid["is_proofread_admitted"] is True

    # Cross-binding / unification failure
    cross_resp = {
        "evidence_status": "sufficient",
        "answer": {"subject": "KESTREL", "predicate": "terminal_auth", "object": "AUTH_ALPHA_KESTREL"},
        "parent_memory_ids": ["mem_velora_transit_route", "mem_kestrel_facility_grid"],
    }
    p_cross = evaluate_epistemic_proofreading(cross_resp, memories, "KESTREL", "AUTH_ALPHA_KESTREL", can_w.rules)
    assert p_cross["proofreader_verdict"] == "REJECT_UNIFICATION_FAILURE"
    assert p_cross["is_proofread_admitted"] is False

    # Clean contract-consistent abstention
    abstain_resp = {
        "evidence_status": "insufficient",
        "answer": {"subject": "KESTREL", "predicate": "terminal_auth", "object": "UNKNOWN"},
        "parent_memory_ids": [],
    }
    p_abstain = evaluate_epistemic_proofreading(abstain_resp, memories, "KESTREL", "AUTH_ALPHA_KESTREL", can_w.rules)
    assert p_abstain["proofreader_verdict"] == "PASS_ABSTENTION"
    assert p_abstain["is_proofread_admitted"] is False

    # Contract failure: UNKNOWN with sufficient status
    contract_fail_resp = {
        "evidence_status": "sufficient",
        "answer": {"subject": "KESTREL", "predicate": "terminal_auth", "object": "UNKNOWN"},
        "parent_memory_ids": [],
    }
    p_contract_fail = evaluate_epistemic_proofreading(contract_fail_resp, memories, "KESTREL", "AUTH_ALPHA_KESTREL", can_w.rules)
    assert p_contract_fail["proofreader_verdict"] == "REJECT_CONTRACT_FAILURE"
    assert p_contract_fail["is_proofread_admitted"] is False


def test_exp1b_c2b_mock_execution(tmp_path: Path):
    """Verify that the 30-call assay executes cleanly in fake mode."""
    db_path = str(tmp_path / "test_c2b.db")
    res = run_exp1b_c2b_assay(use_fake=True, db_path=db_path)

    assert res["total_calls"] == 30

    db = Database(Path(db_path))
    with db.conn:
        runs = db.conn.execute("SELECT COUNT(*) as cnt FROM runs").fetchone()
        calls = db.conn.execute("SELECT COUNT(*) as cnt FROM calls").fetchone()
        binding_res = db.conn.execute("SELECT COUNT(*) as cnt FROM binding_assay_results").fetchone()
        uncompleted_runs = db.conn.execute("SELECT COUNT(*) as cnt FROM runs WHERE status != 'completed'").fetchone()

        assert runs["cnt"] == 10  # 2 ecologies x 5 conditions
        assert calls["cnt"] == 30
        assert binding_res["cnt"] == 30
        assert uncompleted_runs["cnt"] == 0
    db.close()
