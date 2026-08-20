"""Round 3 Master Batch Runner.

Executes all 4 live tracks (H, G2, B3, L) for Exploration Round 3 on Gemma 3:12B (96 calls total).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd()))

import json
from scripts.explore_round3.run_track_h_coalition import run_track_h_live
from scripts.explore_round3.run_track_g2_immunity import run_track_g2_live
from scripts.explore_round3.run_track_b3_multiverse import run_track_b3_live
from scripts.explore_round3.run_track_l_laundering import run_track_l_live


def main():
    print("================================================================================")
    print("      GENE EXPLORATION ROUND 3 BATCH: WHEN ONE BELIEF HAS MANY REASONS          ")
    print("================================================================================")
    start_time = time.time()

    # Track H
    print("\n>>> [1/4] EXECUTING TRACK H: COALITION CAUSALITY & OVERDETERMINATION (32 calls)...")
    h_db = Path("runs/explore_round3/track_h_coalition.db")
    h_res = run_track_h_live(db_path=h_db, max_calls=32)
    print(f"Track H Complete: {h_res['calls_spent']} calls. Recovered S_C: {h_res['empirical_S_C']}")

    # Track G2
    print("\n>>> [2/4] EXECUTING TRACK G2: NON-DESTRUCTIVE SUPPORT-AWARE IMMUNITY (20 calls)...")
    g2_db = Path("runs/explore_round3/track_g2_immunity.db")
    g2_res = run_track_g2_live(db_path=g2_db, max_calls=20)
    print(f"Track G2 Complete: {g2_res['calls_spent']} calls.")

    # Track B3
    print("\n>>> [3/4] EXECUTING TRACK B3: MONOCULTURE MEASUREMENT MULTIVERSE (24 calls)...")
    b3_db = Path("runs/explore_round3/track_b3_multiverse.db")
    b3_res = run_track_b3_live(db_path=b3_db, max_calls=24)
    print(f"Track B3 Complete: {b3_res['calls_spent']} calls.")

    # Track L
    print("\n>>> [4/4] EXECUTING TRACK L: INDEPENDENCE LAUNDERING & EPISTEMIC OBSERVABILITY (20 calls)...")
    l_db = Path("runs/explore_round3/track_l_laundering.db")
    l_res = run_track_l_live(db_path=l_db, max_calls=20)
    print(f"Track L Complete: {l_res['calls_spent']} calls.")

    elapsed = time.time() - start_time
    total_calls = h_res['calls_spent'] + g2_res['calls_spent'] + b3_res['calls_spent'] + l_res['calls_spent']
    print("\n================================================================================")
    print(f"ALL 4 LIVE TRACKS COMPLETED: {total_calls} calls in {elapsed:.1f}s")
    print("================================================================================")


if __name__ == "__main__":
    main()
