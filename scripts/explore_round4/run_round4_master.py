"""Master Batch Runner for Exploration Round 4 (116 Total Calls).

Orchestrates:
- Track R (24 calls)
- Track P (28 calls)
- Track M (32 calls)
- Track C (32 calls)

Fails closed if the destination DB exists without --allow-overwrite.
Persists relational metrics in SQLite and exports summary JSON artifact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from gene.ollama_client import OllamaClient
from gene.experiments.evaluators_round4 import persist_round4_relational_evaluation
from scripts.explore_round4.run_track_r import run_track_r
from scripts.explore_round4.run_track_p import run_track_p
from scripts.explore_round4.run_track_m import run_track_m
from scripts.explore_round4.run_track_c import run_track_c


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Exploration Round 4 Batch Experiments.")
    parser.add_argument("--db-path", type=str, default="data/exploration_round4_results.db", help="Path to SQLite results database")
    parser.add_argument("--track", type=str, choices=["all", "r", "p", "m", "c"], default="all", help="Specific track to execute")
    parser.add_argument("--max-calls", type=int, default=None, help="Optional max call cap for testing/canary")
    parser.add_argument("--allow-overwrite", action="store_true", help="Allow using an existing DB file (for canaries)")
    parser.add_argument("--summary-json", type=str, default="data/exploration_round4_summary.json", help="Path to write summary JSON artifact")
    args = parser.parse_args()

    db_file = Path(args.db_path)
    if db_file.exists():
        if not args.allow_overwrite:
            print(f"[FAIL-CLOSED ERROR] Results database '{args.db_path}' already exists! Aborting to prevent overwrite. Use --allow-overwrite for canary runs.")
            sys.exit(1)
        else:
            db_file.unlink()
            print(f"[ALLOW OVERWRITE] Removed previous database '{args.db_path}' for fresh canary run.")

    client = OllamaClient()
    print(f"=== Starting Exploration Round 4 Batch (DB: {args.db_path}, Track: {args.track}) ===")

    summary_artifact: dict[str, Any] = {"tracks": {}, "total_evals": 0}
    total_evals = 0

    if args.track in ["all", "r"]:
        print("\n--- Executing Track R (Role Equivariance, 24 calls) ---")
        evals_r, metrics_r = run_track_r(client, args.db_path, max_calls=args.max_calls)
        print(f"Track R complete: {len(evals_r)} calls evaluated. Role Classification: {metrics_r.classification}")
        total_evals += len(evals_r)
        persist_round4_relational_evaluation(args.db_path, "track_r", "role_equivariance", metrics_r.role_follow_ratio, metrics_r.classification, metrics_r)
        summary_artifact["tracks"]["track_r"] = {
            "evals_count": len(evals_r),
            "metrics": metrics_r.model_dump(),
        }

    if args.track in ["all", "p"]:
        print("\n--- Executing Track P (Permutation Invariance, 28 calls) ---")
        evals_p, metrics_p = run_track_p(client, args.db_path, max_calls=args.max_calls)
        print(f"Track P complete: {len(evals_p)} calls evaluated. Entropy: {metrics_p.output_entropy}, Disagreement: {metrics_p.disagreement_rate}, K_I: {metrics_p.k_i}, Epsilon Replay: {metrics_p.canonical_replay_disagreement_rate}")
        total_evals += len(evals_p)
        persist_round4_relational_evaluation(args.db_path, "track_p", "permutation_invariance", metrics_p.k_i, f"entropy={metrics_p.output_entropy}_dperm={metrics_p.disagreement_rate}", metrics_p)
        summary_artifact["tracks"]["track_p"] = {
            "evals_count": len(evals_p),
            "metrics": metrics_p.model_dump(),
        }

    if args.track in ["all", "m"]:
        print("\n--- Executing Track M (Monotonic Scaffolding, 32 calls) ---")
        evals_m, metrics_m_list = run_track_m(client, args.db_path, max_calls=args.max_calls)
        total_s_to_e = sum(m.success_to_error_count for m in metrics_m_list)
        print(f"Track M complete: {len(evals_m)} calls evaluated across {len(metrics_m_list)} chains. Total S->E Transitions: {total_s_to_e}")
        total_evals += len(evals_m)
        m_payload = [m.model_dump() for m in metrics_m_list]
        persist_round4_relational_evaluation(args.db_path, "track_m", "monotonic_scaffolding", float(total_s_to_e), f"chains={len(metrics_m_list)}_s_to_e={total_s_to_e}", m_payload)
        summary_artifact["tracks"]["track_m"] = {
            "evals_count": len(evals_m),
            "total_success_to_error_transitions": total_s_to_e,
            "chains": m_payload,
        }

    if args.track in ["all", "c"]:
        print("\n--- Executing Track C (Compiler Benchmark, 32 calls) ---")
        evals_c = run_track_c(client, args.db_path, max_calls=args.max_calls)
        print(f"Track C complete: {len(evals_c)} calls evaluated.")
        total_evals += len(evals_c)
        summary_artifact["tracks"]["track_c"] = {
            "evals_count": len(evals_c),
        }

    summary_artifact["total_evals"] = total_evals
    if args.summary_json:
        Path(args.summary_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.summary_json, "w", encoding="utf-8") as f:
            json.dump(summary_artifact, f, indent=2)
        print(f"[SUMMARY ARTIFACT] Written to {args.summary_json}")

    print(f"\n=== Exploration Round 4 Complete: {total_evals} total calls persisted in {args.db_path} ===")


if __name__ == "__main__":
    main()
