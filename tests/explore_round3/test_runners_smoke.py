"""Executable Runner Smoke Tests for Round 3.

Verifies that every live runner executes 1 iteration under FakeOllamaClient,
persists records, and verifies N_calls == N_evaluations == 1 with zero exceptions.
"""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
import sqlite3
from gene.ollama_client import FakeOllamaClient
from scripts.explore_round3.run_track_h_coalition import run_track_h_live
from scripts.explore_round3.run_track_g2_immunity import run_track_g2_live
from scripts.explore_round3.run_track_b3_multiverse import run_track_b3_live
from scripts.explore_round3.run_track_l_laundering import run_track_l_live


def test_track_h_smoke(tmp_path: Path):
    db_file = tmp_path / "smoke_h.db"
    fake = FakeOllamaClient(canned_responses={"QUESTION": {"station": "VELORA", "protocol": "PROTO_X7", "evidence_status": "sufficient"}})
    res = run_track_h_live(db_path=db_file, max_calls=1, client=fake)

    assert res["calls_spent"] == 1
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    n_calls = c.execute("SELECT count(*) FROM exploration_calls").fetchone()[0]
    n_evals = c.execute("SELECT count(*) FROM exploration_evaluations").fetchone()[0]
    conn.close()
    assert n_calls == 1
    assert n_evals == 1


def test_track_g2_smoke(tmp_path: Path):
    db_file = tmp_path / "smoke_g2.db"
    fake = FakeOllamaClient(canned_responses={"QUESTION": {"station": "VELORA", "protocol": "PROTO_X7", "evidence_status": "sufficient"}})
    res = run_track_g2_live(db_path=db_file, max_calls=1, client=fake)

    assert res["calls_spent"] == 1
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    n_calls = c.execute("SELECT count(*) FROM exploration_calls").fetchone()[0]
    n_evals = c.execute("SELECT count(*) FROM exploration_evaluations").fetchone()[0]
    conn.close()
    assert n_calls == 1
    assert n_evals == 1


def test_track_b3_smoke(tmp_path: Path):
    db_file = tmp_path / "smoke_b3.db"
    fake = FakeOllamaClient(canned_responses={"QUESTION": {"station": "VELORA", "adjudicated_protocol": "PROTO_M4", "evidence_status": "sufficient"}})
    res = run_track_b3_live(db_path=db_file, max_calls=1, client=fake)

    assert res["calls_spent"] == 1
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    n_calls = c.execute("SELECT count(*) FROM exploration_calls").fetchone()[0]
    n_evals = c.execute("SELECT count(*) FROM exploration_evaluations").fetchone()[0]
    conn.close()
    assert n_calls == 1
    assert n_evals == 1


def test_track_l_smoke(tmp_path: Path):
    db_file = tmp_path / "smoke_l.db"
    fake = FakeOllamaClient(canned_responses={"QUESTION": {
        "station": "VELORA",
        "protocol": "PROTO_ALPHA",
        "independence_status": "determinable",
        "estimated_independent_sources": 1,
        "evidence_status": "sufficient"
    }})
    res = run_track_l_live(db_path=db_file, max_calls=1, client=fake)

    assert res["calls_spent"] == 1
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    n_calls = c.execute("SELECT count(*) FROM exploration_calls").fetchone()[0]
    n_evals = c.execute("SELECT count(*) FROM exploration_evaluations").fetchone()[0]
    row = c.execute("SELECT eval_metadata_json FROM exploration_evaluations").fetchone()
    conn.close()
    assert n_calls == 1
    assert n_evals == 1
    assert "estimated_independent_sources" in row[0]
    assert "independence_status" in row[0]
