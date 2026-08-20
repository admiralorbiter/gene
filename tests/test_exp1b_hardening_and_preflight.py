"""Unit and invariant tests for GENE hardening, persistence linkage, pure B2 mode, and retrieval sweeps."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys
import pytest

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gene.memory.scored_retriever import BM25ScoredRetriever
from gene.memory.store import MemoryNode
from gene.ollama_client import FakeOllamaClient, CallSpec
from gene.persistence.db import Database
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact

from scripts.run_exp1b_retrieval_assay import (
    generate_clutter_distractors,
    run_exp1b_b1_assay,
    run_exp1b_b1_k_sweep,
    run_exp1b_b2_surface_feedback_assay,
    run_exp1b_retrieval_shape_map,
)


def test_g1_g2_evaluation_node_linkage_and_inactive_persistence(tmp_path: Path):
    """Verify that all G1 and G2 outputs create occurrence nodes and evaluations point to them."""
    db_path = tmp_path / "test_linkage.db"
    db = Database(db_path)

    run_exp1b_b1_assay(
        worlds_count=1,
        top_k=6,
        easy_clutter=2,
        hard_clutter=2,
        prompt_version="v2",
        model_name="fake_model",
        use_fake=True,
        db_path=str(db_path),
    )

    with db.conn:
        runs = db.conn.execute("SELECT run_id, status, completed_at FROM runs").fetchall()
        assert len(runs) >= 2
        for r in runs:
            assert r["status"] == "completed"
            assert r["completed_at"] is not None

        evals = db.conn.execute("SELECT evaluation_id, call_id, node_id, generation, phenotype FROM dual_oracle_evaluations").fetchall()
        assert len(evals) > 0
        for ev in evals:
            node_id = ev["node_id"]
            assert node_id is not None
            assert isinstance(node_id, str)
            assert len(node_id) > 0

            node_row = db.conn.execute("SELECT * FROM memory_nodes WHERE node_id = ?", (node_id,)).fetchone()
            assert node_row is not None
            assert node_row["created_by_call_id"] == ev["call_id"]

            if ev["phenotype"] == "extinct":
                assert node_row["is_active"] == 0
                assert node_row["reproductive_status"] == "inactive"
                assert "UNKNOWN" in node_row["natural_text"]
            else:
                assert node_row["is_active"] == 1
                assert node_row["reproductive_status"] == "active"

    db.close()


def test_inactive_unknown_persistence_under_pruned_retrieval(tmp_path: Path):
    """Under top_k=3 (path pruned), verify model abstains and inactive UNKNOWN nodes are persisted."""
    db_path = tmp_path / "test_unknown_nodes.db"
    
    run_exp1b_b1_assay(
        worlds_count=1,
        top_k=3,
        easy_clutter=4,
        hard_clutter=4,
        prompt_version="v2",
        model_name="fake_model",
        use_fake=True,
        db_path=str(db_path),
    )

    db = Database(db_path)
    with db.conn:
        inactive_nodes = db.conn.execute("SELECT * FROM memory_nodes WHERE is_active = 0").fetchall()
        assert len(inactive_nodes) > 0
        for node in inactive_nodes:
            assert node["reproductive_status"] == "inactive"
            assert "UNKNOWN" in node["natural_text"]
            assert node["created_by_call_id"] is not None

        for node in inactive_nodes:
            ev = db.conn.execute("SELECT * FROM dual_oracle_evaluations WHERE node_id = ?", (node["node_id"],)).fetchone()
            assert ev is not None
            assert ev["phenotype"] == "extinct"
    db.close()


def test_pure_b2_mode_contains_single_allele_at_founder_locus(tmp_path: Path):
    """Verify that pure B2 multiplicity mode contains exactly one allele at the founder locus."""
    db_path = tmp_path / "test_b2_pure.db"
    bundle = generate_exp1_branching_world(world_seed=4000, rotation_idx=0, mutated_supervisor="TAL")
    
    clean_founder = bundle.clean_founder_fact
    mutated_founder = bundle.mutated_founder_fact

    pure_bg = [
        f for f in bundle.clean_world.facts
        if not (f.fact_id == clean_founder.fact_id or f.locus_id == clean_founder.locus_id)
    ]
    assert not any(f.locus_id == "locus_manager_supervisor" for f in pure_bg)
    assert not any(f.object == clean_founder.object for f in pure_bg)

    comp_bg = list(bundle.clean_world.facts)
    assert any(f.locus_id == "locus_manager_supervisor" for f in comp_bg)

    results_pure = run_exp1b_b2_surface_feedback_assay(
        worlds_count=2,
        top_k=4,
        clutter_count=8,
        mode="pure",
        db_path=str(db_path),
    )
    assert 0 in results_pure
    assert 8 in results_pure
    assert results_pure[8]["mean_top_k_occupancy"] >= results_pure[0]["mean_top_k_occupancy"]

    db = Database(db_path)
    with db.conn:
        rows = db.conn.execute("SELECT * FROM surface_feedback_sweeps WHERE sweep_id LIKE '%_pure'").fetchall()
        assert len(rows) == 5
    db.close()


def test_retrieval_sweep_results_persistence(tmp_path: Path):
    """Verify that retrieval sweeps persist per-query and aggregate records to retrieval_sweep_results table."""
    db_path = tmp_path / "test_sweeps.db"

    run_exp1b_b1_k_sweep(
        worlds_count=2,
        k_values=[4, 6],
        easy_clutter=2,
        hard_clutter=2,
        db_path=str(db_path),
    )

    db = Database(db_path)
    with db.conn:
        rows = db.conn.execute("SELECT * FROM retrieval_sweep_results WHERE sweep_type = 'k_rescue'").fetchall()
        assert len(rows) > 0
        for r in rows:
            assert r["sweep_id"] is not None
            assert r["top_k"] in (4, 6)
            assert r["founder_retrieved"] in (0, 1)
            assert r["cosup_retrieved"] in (0, 1)
            if r["founder_rank"] is not None:
                assert r["founder_margin"] == (r["top_k"] - 1) - r["founder_rank"]
            if r["cosup_rank"] is not None:
                assert r["cosup_margin"] == (r["top_k"] - 1) - r["cosup_rank"]

    db.close()


def test_paired_clean_infected_retrieval_symmetry(tmp_path: Path):
    """Verify paired clean vs infected retrieval symmetry and shape map execution."""
    db_path = tmp_path / "test_shape_map.db"

    cond_stats, boundaries = run_exp1b_retrieval_shape_map(
        worlds_count=2,
        k_values=[3, 6],
        hard_values=[0, 4],
        easy_clutter=2,
        db_path=str(db_path),
    )

    k6_h0 = cond_stats[(6, 0)]
    assert k6_h0["clean"]["xpath_sum"] == k6_h0["clean"]["n"]
    assert k6_h0["infected"]["xpath_sum"] == k6_h0["infected"]["n"]

    db = Database(db_path)
    with db.conn:
        rows = db.conn.execute("SELECT COUNT(*) as cnt FROM retrieval_sweep_results WHERE sweep_type = 'shape_map'").fetchone()
        assert rows["cnt"] > 0
    db.close()


def test_exp1b_b1c_matched_expression_assay(tmp_path: Path):
    """Verify 1B-B1c matched path sufficiency assay flow with fake client."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from run_exp1b_b1c_matched_expression import run_exp1b_b1c_matched_expression_assay

    db_path = tmp_path / "test_b1c.db"
    results = run_exp1b_b1c_matched_expression_assay(
        seed_rotations=[(7000, 0)],
        use_fake=True,
        db_path=str(db_path),
    )

    assert len(results) == 8  # 1 world x 2 arms x 2 tasks x 2 path states
    broken_results = [r for r in results if r["path"] == "BROKEN"]
    assert all(r["derived"] == "UNKNOWN" for r in broken_results)
    assert all(r["active"] == 0 for r in broken_results)

    db = Database(db_path)
    with db.conn:
        runs = db.conn.execute("SELECT COUNT(*) as cnt FROM runs WHERE status = 'completed'").fetchone()
        assert runs["cnt"] == 4  # 1 world x 2 arms x 2 path states
        nodes = db.conn.execute("SELECT COUNT(*) as cnt FROM memory_nodes").fetchone()
        assert nodes["cnt"] == 8
    db.close()


def test_exp1b_c1_delayed_adjudication_sandbox(tmp_path: Path):
    """Verify 1B-C1 delayed adjudication sandbox execution and SQLite persistence."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from run_exp1b_c_immunity_sandbox import run_exp1b_c_immunity_sandbox

    db_path = tmp_path / "test_c1_sandbox.db"
    results = run_exp1b_c_immunity_sandbox(
        world_seeds=[(7000, 0)],
        tprs=[0.9],
        fprs=[0.1],
        top_k_list=[6],
        db_path=str(db_path),
    )

    # Check that lineage quarantine achieved superior separation compared to node_only
    lin_res = results[6]["lineage_quarantine"][(0.9, 0.1)]
    node_res = results[6]["node_only_quarantine"][(0.9, 0.1)]
    assert lin_res["s"] > node_res["s"]
    assert lin_res["containment"] > node_res["containment"]
    assert node_res["containment"] == 0.0  # Provenance laundering under node-only

    db = Database(db_path)
    with db.conn:
        sweeps = db.conn.execute("SELECT COUNT(*) as cnt FROM retrieval_sweep_results WHERE sweep_type = 'immunity_sandbox'").fetchone()
        assert sweeps["cnt"] == 6  # 6 policies x 1 grid point x 1 top_k
    db.close()


def test_exp1b_c1b_shared_ecology(tmp_path: Path):
    """Verify 1B-C1b shared-ecology sandbox execution, multi-control policies, and delta_I containment."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from run_exp1b_c1b_shared_ecology import run_exp1b_c1b_shared_ecology

    db_path = tmp_path / "test_c1b_shared.db"
    results = run_exp1b_c1b_shared_ecology(
        tprs=[0.9],
        fprs=[0.1],
        top_k_list=[6],
        n_mc_samples=5,
        db_path=str(db_path),
    )

    lin = results[6]["lineage_quarantine"][(0.9, 0.1)]
    blind_uni = results[6]["signal_blind_uniform_thinning"][(0.9, 0.1)]
    sig_uni = results[6]["signal_conditioned_uniform_thinning"][(0.9, 0.1)]
    gen = results[6]["generation_matched_thinning"][(0.9, 0.1)]
    node = results[6]["node_only_quarantine"][(0.9, 0.1)]

    # Signal-blind uniform thinning has zero selective separation under balanced ecologies
    assert pytest.approx(blind_uni["s"], abs=1e-7) == 0.0

    # Lineage achieves higher separation than node-only, signal-conditioned uniform, and generation controls
    assert lin["s"] > node["s"]
    assert lin["s"] > sig_uni["s"]
    assert lin["s"] > gen["s"]

    db = Database(db_path)
    with db.conn:
        sweeps = db.conn.execute("SELECT COUNT(*) as cnt FROM immunity_policy_results WHERE sweep_type = 'shared_ecology_hardened_full_envelope'").fetchone()
        assert sweeps["cnt"] == 20  # 8 core + 12 budget sweep policies x 1 grid point x 1 top_k
    db.close()
