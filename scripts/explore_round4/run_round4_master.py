"""Master Batch Runner for Exploration Round 4 (116 Total Calls).

Orchestrates:
- Track R (24 calls)
- Track P (28 calls)
- Track M (32 calls)
- Track C (32 calls)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from gene.ollama_client import OllamaClient
from scripts.explore_round4.run_track_r import run_track_r
from scripts.explore_round4.run_track_p import run_track_p
from scripts.explore_round4.run_track_m import run_track_m
from scripts.explore_round4.run_track_c import run_track_c


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Exploration Round 4 Batch Experiments.")
    parser.add_argument("--db-path", type=str, default="data/exploration_round4_results.db", help="Path to SQLite results database")
    parser.add_argument("--track", type=str, choices=["all", "r", "p", "m", "c"], default="all", help="Specific track to execute")
    parser.add_argument("--max-calls", type=int, default=None, help="Optional max call cap for testing")
    args = parser.parse_args()

    client = OllamaClient()
    print(f"=== Starting Exploration Round 4 Batch (DB: {args.db_path}, Track: {args.track}) ===")

    total_evals = 0
    if args.track in ["all", "r"]:
        print("\n--- Executing Track R (Role Equivariance, 24 calls) ---")
        evals_r = run_track_r(client, args.db_path, max_calls=args.max_calls)
        print(f"Track R complete: {len(evals_r)} calls evaluated.")
        total_evals += len(evals_r)

    if args.track in ["all", "p"]:
        print("\n--- Executing Track P (Permutation Invariance, 28 calls) ---")
        evals_p = run_track_p(client, args.db_path, max_calls=args.max_calls)
        print(f"Track P complete: {len(evals_p)} calls evaluated.")
        total_evals += len(evals_p)

    if args.track in ["all", "m"]:
        print("\n--- Executing Track M (Monotonic Scaffolding, 32 calls) ---")
        evals_m = run_track_m(client, args.db_path, max_calls=args.max_calls)
        print(f"Track M complete: {len(evals_m)} calls evaluated.")
        total_evals += len(evals_m)

    if args.track in ["all", "c"]:
        print("\n--- Executing Track C (Compiler Benchmark, 32 calls) ---")
        evals_c = run_track_c(client, args.db_path, max_calls=args.max_calls)
        print(f"Track C complete: {len(evals_c)} calls evaluated.")
        total_evals += len(evals_c)

    print(f"\n=== Exploration Round 4 Complete: {total_evals} total calls persisted in {args.db_path} ===")


if __name__ == "__main__":
    main()
