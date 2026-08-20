"""Script to generate the authoritative, machine-readable canonical results manifest.

Extracts all headline metrics, denominators, commit hashes, model digests, and
SQL query logic from the primary frozen SQLite run databases in the GENE repository.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any


def extract_exp1b_c2b_metrics(db_path: Path) -> dict[str, Any]:
    """Extract metrics from Experiment 1B-C2b binding disambiguation assay."""
    if not db_path.exists():
        return {"status": "missing_db", "db_path": str(db_path)}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_calls = c.execute("SELECT COUNT(*) as cnt FROM binding_assay_results").fetchone()["cnt"]
    active_calls = c.execute("SELECT COUNT(*) as cnt FROM binding_assay_results WHERE emitted_object != 'UNKNOWN'").fetchone()["cnt"]
    broken_paths = c.execute("SELECT COUNT(*) as cnt FROM binding_assay_results WHERE path_supported = 0").fetchone()["cnt"]
    complete_paths = c.execute("SELECT COUNT(*) as cnt FROM binding_assay_results WHERE path_supported = 1").fetchone()["cnt"]

    # Unsupported concrete outputs (emitted concrete object on broken path)
    unsupported_concrete = c.execute(
        "SELECT COUNT(*) as cnt FROM binding_assay_results WHERE path_supported = 0 AND emitted_object != 'UNKNOWN'"
    ).fetchone()["cnt"]

    # Valid derivations
    valid_derivations = c.execute(
        "SELECT COUNT(*) as cnt FROM binding_assay_results WHERE path_supported = 1 AND emitted_object != 'UNKNOWN' AND epistemic_phenotype = 'healthy'"
    ).fetchone()["cnt"]

    # Clean abstentions
    clean_abstentions = c.execute(
        "SELECT COUNT(*) as cnt FROM binding_assay_results WHERE emitted_object = 'UNKNOWN' AND epistemic_phenotype = 'clean_abstention'"
    ).fetchone()["cnt"]

    # Proofreader actions
    rejected_unification = c.execute(
        "SELECT COUNT(*) as cnt FROM binding_assay_results WHERE proofreader_verdict = 'REJECT_UNIFICATION_FAILURE'"
    ).fetchone()["cnt"]
    pass_valid = c.execute(
        "SELECT COUNT(*) as cnt FROM binding_assay_results WHERE proofreader_verdict = 'PASS_VALID_DERIVATION'"
    ).fetchone()["cnt"]
    pass_abstention = c.execute(
        "SELECT COUNT(*) as cnt FROM binding_assay_results WHERE proofreader_verdict = 'PASS_ABSTENTION'"
    ).fetchone()["cnt"]
    admitted_unsupported = c.execute(
        "SELECT COUNT(*) as cnt FROM binding_assay_results WHERE is_proofread_admitted = 1 AND path_supported = 0"
    ).fetchone()["cnt"]

    run_row = c.execute("SELECT model_name, model_digest, git_commit FROM runs LIMIT 1").fetchone()
    conn.close()

    mu_expression_total = unsupported_concrete / total_calls if total_calls > 0 else 0.0
    mu_expression_broken = unsupported_concrete / broken_paths if broken_paths > 0 else 0.0
    mu_heritable_total = admitted_unsupported / total_calls if total_calls > 0 else 0.0
    mu_heritable_broken = admitted_unsupported / broken_paths if broken_paths > 0 else 0.0

    return {
        "experiment": "Experiment 1B-C2b (Binding Disambiguation & Layer 2 Proofreading)",
        "database": db_path.name,
        "commit": run_row["git_commit"] if run_row else "unknown",
        "model_name": run_row["model_name"] if run_row else "unknown",
        "model_digest": run_row["model_digest"] if run_row else "unknown",
        "sample_size_total": total_calls,
        "sample_size_broken_paths": broken_paths,
        "sample_size_complete_paths": complete_paths,
        "valid_concrete_derivations": valid_derivations,
        "unsupported_concrete_emitted": unsupported_concrete,
        "clean_abstentions": clean_abstentions,
        "proofreader_rejected_unification": rejected_unification,
        "proofreader_passed_valid": pass_valid,
        "proofreader_passed_abstention": pass_abstention,
        "proofreader_admitted_unsupported": admitted_unsupported,
        "mu_expression_overall": round(mu_expression_total, 4),
        "mu_expression_on_broken_paths": round(mu_expression_broken, 4),
        "mu_heritable_overall": round(mu_heritable_total, 4),
        "mu_heritable_on_broken_paths": round(mu_heritable_broken, 4),
    }


def extract_exp1b_c2a_metrics(db_path: Path) -> dict[str, Any]:
    """Extract metrics from Experiment 1B-C2a live behavioral immunity assay."""
    if not db_path.exists():
        return {"status": "missing_db", "db_path": str(db_path)}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_calls = c.execute("SELECT COUNT(*) as cnt FROM calls").fetchone()["cnt"]

    # Query dual_oracle_evaluations_v2
    phenotypes = {}
    for row in c.execute("SELECT epistemic_phenotype, count(*) as cnt FROM dual_oracle_evaluations_v2 GROUP BY epistemic_phenotype"):
        phenotypes[row["epistemic_phenotype"]] = row["cnt"]

    repro_counts = {}
    for row in c.execute("SELECT reproductive_status, count(*) as cnt FROM dual_oracle_evaluations_v2 GROUP BY reproductive_status"):
        repro_counts[row["reproductive_status"]] = row["cnt"]

    # Replay stability on swapped broken clean prompt
    replay_swapped = c.execute(
        "SELECT count(*) as total, "
        "SUM(CASE WHEN derived_object = 'AUTH_ALPHA_KESTREL' THEN 1 ELSE 0 END) as alpha_cnt, "
        "SUM(CASE WHEN derived_object = 'UNKNOWN' THEN 1 ELSE 0 END) as unk_cnt "
        "FROM dual_oracle_evaluations_v2 WHERE call_id LIKE 'call_c2a_replay_swapped_%'"
    ).fetchone()

    # Replay stability on forward broken clean prompt
    replay_forward = c.execute(
        "SELECT count(*) as total, "
        "SUM(CASE WHEN derived_object = 'UNKNOWN' THEN 1 ELSE 0 END) as unk_cnt "
        "FROM dual_oracle_evaluations_v2 WHERE call_id LIKE 'call_c2a_replay_forward_%'"
    ).fetchone()

    run_row = c.execute("SELECT model_name, model_digest, git_commit FROM runs LIMIT 1").fetchone()
    conn.close()

    return {
        "experiment": "Experiment 1B-C2a.1 (Live Behavioral Immunity & Replay Stability)",
        "database": db_path.name,
        "commit": run_row["git_commit"] if run_row else "unknown",
        "model_name": run_row["model_name"] if run_row else "unknown",
        "model_digest": run_row["model_digest"] if run_row else "unknown",
        "total_calls": total_calls,
        "reproductive_status_distribution": repro_counts,
        "epistemic_phenotype_distribution": phenotypes,
        "replay_stability_swapped_broken": {
            "total_repetitions": replay_swapped["total"],
            "active_epistemic_errors": replay_swapped["alpha_cnt"],
            "contract_failure_abstentions": replay_swapped["unk_cnt"],
        },
        "replay_stability_forward_broken": {
            "total_repetitions": replay_forward["total"],
            "clean_abstentions": replay_forward["unk_cnt"],
        },
    }


def extract_exp1b_c1b_metrics(db_path: Path) -> dict[str, Any]:
    """Extract metrics from Experiment 1B-C1b delayed adjudication shared-ecology sandbox."""
    if not db_path.exists():
        return {"status": "missing_db", "db_path": str(db_path)}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_rows = c.execute("SELECT COUNT(*) as cnt FROM immunity_policy_results").fetchone()["cnt"]

    # Lineage Quarantine Selectivity at 90/10 detector (averaged across 12 ecologies)
    lin_row = c.execute(
        "SELECT AVG(c_h) as avg_c_h, AVG(c_i) as avg_c_i, AVG(separation_s) as avg_s "
        "FROM immunity_policy_results WHERE policy = 'lineage_quarantine' AND tpr = 0.9 AND fpr = 0.1"
    ).fetchone()

    # Blind Thinning Selectivity at 90/10 detector
    thin_row = c.execute(
        "SELECT AVG(c_h) as avg_c_h, AVG(c_i) as avg_c_i, AVG(separation_s) as avg_s "
        "FROM immunity_policy_results WHERE policy = 'signal_blind_uniform_thinning' AND tpr = 0.9 AND fpr = 0.1"
    ).fetchone()

    # Random Family Quarantine
    rand_fam_row = c.execute(
        "SELECT AVG(c_h) as avg_c_h, AVG(c_i) as avg_c_i, AVG(separation_s) as avg_s "
        "FROM immunity_policy_results WHERE policy = 'random_family_quarantine' AND tpr = 0.9 AND fpr = 0.1"
    ).fetchone()

    # Node Only Quarantine at 90/10 detector
    node_row = c.execute(
        "SELECT AVG(c_h) as avg_c_h, AVG(c_i) as avg_c_i, AVG(separation_s) as avg_s "
        "FROM immunity_policy_results WHERE policy = 'node_only_quarantine' AND tpr = 0.9 AND fpr = 0.1"
    ).fetchone()

    run_row = c.execute("SELECT git_commit FROM runs LIMIT 1").fetchone()
    conn.close()

    return {
        "experiment": "Experiment 1B-C1b (Shared-Ecology Delayed Adjudication Sandbox)",
        "database": db_path.name,
        "commit": run_row["git_commit"] if run_row else "unknown",
        "total_evaluations": total_rows,
        "operating_point_tpr90_fpr10": {
            "lineage_quarantine": {
                "C_H": round(lin_row["avg_c_h"], 4) if lin_row and lin_row["avg_c_h"] is not None else None,
                "C_I": round(lin_row["avg_c_i"], 4) if lin_row and lin_row["avg_c_i"] is not None else None,
                "selectivity_S": round(lin_row["avg_s"], 4) if lin_row and lin_row["avg_s"] is not None else None,
            },
            "signal_blind_uniform_thinning": {
                "C_H": round(thin_row["avg_c_h"], 4) if thin_row and thin_row["avg_c_h"] is not None else None,
                "C_I": round(thin_row["avg_c_i"], 4) if thin_row and thin_row["avg_c_i"] is not None else None,
                "selectivity_S": round(thin_row["avg_s"], 4) if thin_row and thin_row["avg_s"] is not None else None,
            },
            "random_family_quarantine": {
                "C_H": round(rand_fam_row["avg_c_h"], 4) if rand_fam_row and rand_fam_row["avg_c_h"] is not None else None,
                "C_I": round(rand_fam_row["avg_c_i"], 4) if rand_fam_row and rand_fam_row["avg_c_i"] is not None else None,
                "selectivity_S": round(rand_fam_row["avg_s"], 4) if rand_fam_row and rand_fam_row["avg_s"] is not None else None,
            },
            "node_only_quarantine": {
                "C_H": round(node_row["avg_c_h"], 4) if node_row and node_row["avg_c_h"] is not None else None,
                "C_I": round(node_row["avg_c_i"], 4) if node_row and node_row["avg_c_i"] is not None else None,
                "selectivity_S": round(node_row["avg_s"], 4) if node_row and node_row["avg_s"] is not None else None,
            },
        },
    }


def extract_exp1b_b1c_metrics(db_path: Path) -> dict[str, Any]:
    """Extract metrics from Experiment 1B-B1c matched path expression assay."""
    if not db_path.exists():
        return {"status": "missing_db", "db_path": str(db_path)}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_calls = c.execute("SELECT COUNT(*) as cnt FROM calls").fetchone()["cnt"]

    # Expression conditioned on complete vs broken paths from dual_oracle_evaluations
    complete_active = c.execute(
        "SELECT COUNT(*) as cnt FROM dual_oracle_evaluations WHERE local_derivability_status = 'TruthStatus.TRUE' AND derived_object != 'UNKNOWN'"
    ).fetchone()["cnt"]
    complete_total = c.execute(
        "SELECT COUNT(*) as cnt FROM dual_oracle_evaluations WHERE local_derivability_status = 'TruthStatus.TRUE'"
    ).fetchone()["cnt"]

    broken_active = c.execute(
        "SELECT COUNT(*) as cnt FROM dual_oracle_evaluations WHERE local_derivability_status = 'TruthStatus.UNSUPPORTED' AND derived_object != 'UNKNOWN'"
    ).fetchone()["cnt"]
    broken_total = c.execute(
        "SELECT COUNT(*) as cnt FROM dual_oracle_evaluations WHERE local_derivability_status = 'TruthStatus.UNSUPPORTED'"
    ).fetchone()["cnt"]

    run_row = c.execute("SELECT model_name, model_digest, git_commit FROM runs LIMIT 1").fetchone()
    conn.close()

    p_active_complete = complete_active / complete_total if complete_total > 0 else 0.0
    p_active_broken = broken_active / broken_total if broken_total > 0 else 0.0

    return {
        "experiment": "Experiment 1B-B1c (Matched Path Sufficiency Assay)",
        "database": db_path.name,
        "commit": run_row["git_commit"] if run_row else "unknown",
        "model_name": run_row["model_name"] if run_row else "unknown",
        "model_digest": run_row["model_digest"] if run_row else "unknown",
        "total_calls": total_calls,
        "p_active_given_complete_path": round(p_active_complete, 4),
        "complete_active_count": complete_active,
        "complete_total_count": complete_total,
        "p_active_given_broken_path": round(p_active_broken, 4),
        "broken_active_count": broken_active,
        "broken_total_count": broken_total,
    }


def generate_manifest() -> dict[str, Any]:
    """Assemble all frozen experiment metrics into an authoritative manifest."""
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data"
    data_dir.mkdir(exist_ok=True)

    manifest = {
        "manifest_version": "1.0.0",
        "project": "GENE (Genealogical Epistemic Network Experiments)",
        "canonical_experiments": {
            "exp1b_b1c": extract_exp1b_b1c_metrics(root_dir / "gene_exp1b_b1c_matched_expression_20260820_140941.db"),
            "exp1b_c1b": extract_exp1b_c1b_metrics(root_dir / "gene_exp1b_c1b_shared_ecology_15abd87.db"),
            "exp1b_c2a": extract_exp1b_c2a_metrics(root_dir / "gene_exp1b_c2a_live_assay_a1474d6.db"),
            "exp1b_c2b": extract_exp1b_c2b_metrics(root_dir / "gene_exp1b_c2b_binding_assay_1f62908.db"),
        },
    }

    manifest_path = data_dir / "canonical_results_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Authoritative results manifest written to: {manifest_path}")
    return manifest


if __name__ == "__main__":
    manifest = generate_manifest()
    print(json.dumps(manifest, indent=2))
