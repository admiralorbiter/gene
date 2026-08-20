"""Track B3 Factorial Decomposition: Main Effects and Two-Way Interactions.

Analyzes runs/explore_round3/track_b3_multiverse.db across all 16 primary factorial cells.
"""

from __future__ import annotations

import itertools
import json
import sqlite3
from pathlib import Path


def main():
    db_path = Path("runs/explore_round3/track_b3_multiverse.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT call_id, emitted_claim, metadata_json, eval_metadata_json FROM exploration_calls JOIN exploration_evaluations USING (call_id)").fetchall()
    conn.close()

    main_cells = []
    for cid, emitted, meta_j, eval_j in rows:
        meta = json.loads(meta_j)
        if meta.get("assay_arm") == "main_factorial":
            main_cells.append({
                "cell_id": meta["cell_id"],
                "station": meta["station"],
                "root_structure": meta["root_structure"],
                "token_mapping": meta["token_mapping"],
                "doc_order": meta["doc_order"],
                "majority_protocol": meta["majority_protocol"],
                "minority_protocol": meta["minority_protocol"],
                "emitted": emitted,
                "follows_majority": (emitted == meta["majority_protocol"]),
                "follows_minority": (emitted == meta["minority_protocol"]),
                "is_unknown": (emitted == "UNKNOWN"),
            })

    print("================================================================================")
    print("      TRACK B3 POST-EXECUTION AUDIT: 16-CELL FACTORIAL DECOMPOSITION            ")
    print("================================================================================")
    print(f"Total Primary Factorial Cells: {len(main_cells)}")

    # 1. Main Effects
    factors = {
        "Root Structure": ("root_structure", ["independent", "monoculture"]),
        "Token Mapping": ("token_mapping", ["M4_majority", "Q7_majority"]),
        "Document Order": ("doc_order", ["forward", "interleaved"]),
        "Station Entity": ("station", ["VELORA", "KESTREL"]),
    }

    print("\n--- Main Effects (P(Follows Majority Protocol)) ---")
    for fname, (fkey, levels) in factors.items():
        lvl0_matches = [c["follows_majority"] for c in main_cells if c[fkey] == levels[0]]
        lvl1_matches = [c["follows_majority"] for c in main_cells if c[fkey] == levels[1]]
        p0 = sum(lvl0_matches) / len(lvl0_matches)
        p1 = sum(lvl1_matches) / len(lvl1_matches)
        diff = p0 - p1
        print(f"  {fname:<18}: {levels[0]}={sum(lvl0_matches)}/8 ({p0*100:.1f}%) vs {levels[1]}={sum(lvl1_matches)}/8 ({p1*100:.1f}%) | Delta = {diff:+.3f}")

    # 2. Main Effects on Abstention Rate P(UNKNOWN)
    print("\n--- Main Effects on Abstention Rate (P(UNKNOWN)) ---")
    for fname, (fkey, levels) in factors.items():
        lvl0_unk = [c["is_unknown"] for c in main_cells if c[fkey] == levels[0]]
        lvl1_unk = [c["is_unknown"] for c in main_cells if c[fkey] == levels[1]]
        p0 = sum(lvl0_unk) / len(lvl0_unk)
        p1 = sum(lvl1_unk) / len(lvl1_unk)
        diff = p0 - p1
        print(f"  {fname:<18}: {levels[0]}={sum(lvl0_unk)}/8 ({p0*100:.1f}%) vs {levels[1]}={sum(lvl1_unk)}/8 ({p1*100:.1f}%) | Delta = {diff:+.3f}")

    # 3. Two-Way Interactions
    print("\n--- Two-Way Interaction Breakdown (Document Order x Root Structure) ---")
    for do in ["forward", "interleaved"]:
        for rs in ["independent", "monoculture"]:
            sub = [c for c in main_cells if c["doc_order"] == do and c["root_structure"] == rs]
            n_maj = sum(1 for c in sub if c["follows_majority"])
            n_unk = sum(1 for c in sub if c["is_unknown"])
            n_min = sum(1 for c in sub if c["follows_minority"])
            print(f"  Order: {do:<12} | Root: {rs:<12} (N={len(sub)}) -> Majority={n_maj}/4 ({n_maj/4*100:.1f}%), Minority={n_min}/4 ({n_min/4*100:.1f}%), UNKNOWN={n_unk}/4 ({n_unk/4*100:.1f}%)")

    # 4. Two-Way Interaction (Station x Document Order)
    print("\n--- Two-Way Interaction Breakdown (Station x Document Order) ---")
    for st in ["VELORA", "KESTREL"]:
        for do in ["forward", "interleaved"]:
            sub = [c for c in main_cells if c["station"] == st and c["doc_order"] == do]
            n_maj = sum(1 for c in sub if c["follows_majority"])
            n_unk = sum(1 for c in sub if c["is_unknown"])
            n_min = sum(1 for c in sub if c["follows_minority"])
            print(f"  Station: {st:<8} | Order: {do:<12} (N={len(sub)}) -> Majority={n_maj}/4 ({n_maj/4*100:.1f}%), Minority={n_min}/4 ({n_min/4*100:.1f}%), UNKNOWN={n_unk}/4 ({n_unk/4*100:.1f}%)")


if __name__ == "__main__":
    main()
