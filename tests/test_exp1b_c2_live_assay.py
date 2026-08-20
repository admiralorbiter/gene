"""Tests for Experiment 1B-C2 / C2a Live Behavioral Immunity & Replay Stability Assay."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from gene.persistence.db import Database
from run_exp1b_c2_live_assay import build_c2_structures, run_exp1b_c2a_suite


def test_build_c2_structures_geometry():
    """Verify that all 6 post-policy contexts maintain strictly matched 6-memory geometry and valid worlds."""
    for ctx in ["baseline", "node_only", "lineage_quarantine", "autoimmunity", "generation_matched", "double_quarantine"]:
        memories, can_world, ctx_world, tasks, rules_text = build_c2_structures("VELORA", "KESTREL", ctx, seed=7000)
        assert len(memories) == 6
        assert len(tasks) == 2
        assert len(can_world.facts) == 8
        assert len(can_world.rules) == 3
        assert "Domain Authorization Rules" in rules_text
        assert tasks[0].expected_answer == "AUTH_ALPHA_VELORA"
        assert tasks[1].expected_answer == "AUTH_BETA_KESTREL"


def test_exp1b_c2a_mock_execution(tmp_path: Path):
    """Verify that the 50-call assay executes cleanly with DualOracle evaluations and valid runs."""
    db_path = str(tmp_path / "test_c2a.db")
    res = run_exp1b_c2a_suite(mode="all", use_fake=True, db_path=db_path)

    assert res["total_calls"] == 50

    db = Database(Path(db_path))
    with db.conn:
        runs = db.conn.execute("SELECT COUNT(*) as cnt FROM runs").fetchone()
        calls = db.conn.execute("SELECT COUNT(*) as cnt FROM calls").fetchone()
        nodes = db.conn.execute("SELECT COUNT(*) as cnt FROM memory_nodes").fetchone()
        evals = db.conn.execute("SELECT COUNT(*) as cnt FROM dual_oracle_evaluations").fetchone()
        uncompleted_runs = db.conn.execute("SELECT COUNT(*) as cnt FROM runs WHERE status != 'completed'").fetchone()

        assert runs["cnt"] == 16  # 12 discrete + 2 replay + 2 factorial
        assert calls["cnt"] == 50
        assert nodes["cnt"] == 50
        assert evals["cnt"] == 50
        assert uncompleted_runs["cnt"] == 0  # All runs properly marked completed
    db.close()
