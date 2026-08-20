"""Tests for Experiment 1B-C2 Live Behavioral Immunity Verification Assay."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from gene.persistence.db import Database
from run_exp1b_c2_live_assay import build_c2_context_and_rules, run_exp1b_c2_live_assay


def test_build_c2_context_and_rules_geometry():
    """Verify that all 5 post-policy contexts maintain strictly matched 6-memory geometry."""
    for ctx in ["baseline", "node_only", "lineage_quarantine", "autoimmunity", "generation_matched"]:
        memories, rules_text, expected = build_c2_context_and_rules("VELORA", "KESTREL", ctx, seed=7000)
        assert len(memories) == 6
        assert "Domain Authorization Rules" in rules_text
        assert "AUTH_ALPHA_VELORA" in expected["clean_target"]
        assert "AUTH_BETA_KESTREL" in expected["mutated_target"]


def test_exp1b_c2_live_assay_mock_execution(tmp_path: Path):
    """Verify that the 20-call assay executes cleanly with 100% path-conditioned precision under fake client."""
    db_path = str(tmp_path / "test_c2.db")
    res = run_exp1b_c2_live_assay(use_fake=True, db_path=db_path)

    assert res["total_calls"] == 20
    assert res["p_active_complete"] == 1.0
    assert res["p_unknown_broken"] == 1.0

    db = Database(Path(db_path))
    with db.conn:
        runs = db.conn.execute("SELECT COUNT(*) as cnt FROM runs").fetchone()
        calls = db.conn.execute("SELECT COUNT(*) as cnt FROM calls").fetchone()
        nodes = db.conn.execute("SELECT COUNT(*) as cnt FROM memory_nodes").fetchone()
        assert runs["cnt"] == 10  # 2 ecologies x 5 contexts
        assert calls["cnt"] == 20
        assert nodes["cnt"] == 20
    db.close()
