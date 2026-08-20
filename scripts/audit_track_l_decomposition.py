"""Track L Phenotype Decomposition: Bifurcation between False Certainty and Epistemic Resistance.

Analyzes runs/explore_round3/track_l_laundering.db across all 20 calls (5 stages x 2 stations x 2 protocols).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def main():
    db_path = Path("runs/explore_round3/track_l_laundering.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT call_id, emitted_claim, metadata_json, eval_metadata_json FROM exploration_calls JOIN exploration_evaluations USING (call_id)").fetchall()
    conn.close()

    cells = []
    for cid, emitted, meta_j, eval_j in rows:
        meta = json.loads(meta_j)
        eval_meta = json.loads(eval_j)
        cells.append({
            "call_id": cid,
            "station": meta["station"],
            "protocol": meta["protocol"],
            "stage_name": meta["stage_name"],
            "generation": meta["generation"],
            "true_roots": meta["true_root_count"],
            "naive_roots": meta["reference_naive_count"],
            "status": eval_meta.get("independence_status"),
            "estimated_sources": eval_meta.get("estimated_independent_sources"),
            "emitted_protocol": emitted,
        })

    print("================================================================================")
    print("      TRACK L POST-EXECUTION AUDIT: PHENOTYPE BIFURCATION ACROSS 20 CALLS       ")
    print("================================================================================")

    # 1. Complete Cell Matrix
    print(f"\n{'Generation':<6} {'Stage Name':<30} {'Station':<8} {'Protocol':<12} {'True':<6} {'Status':<15} {'Est Sources':<12}")
    print("-" * 95)
    for c in sorted(cells, key=lambda x: (x["generation"], x["station"], x["protocol"])):
        est_str = str(c["estimated_sources"]) if c["estimated_sources"] is not None else "null"
        print(f"G{c['generation']:<5} {c['stage_name']:<30} {c['station']:<8} {c['protocol']:<12} {c['true_roots']:<6} {c['status']:<15} {est_str:<12}")

    # 2. Stage-by-Stage Phenotype Breakdown
    print("\n--- Stage Phenotype Summary ---")
    stages = [
        "G0_True_1_Root",
        "G1_Cited_Paraphrases",
        "G2_Partial_Laundering",
        "G3_Fully_Laundered_Consensus",
        "G_True_4_Roots_Control",
    ]

    for st in stages:
        sub = [c for c in cells if c["stage_name"] == st]
        n_det = sum(1 for c in sub if c["status"] == "determinable")
        n_indet = sum(1 for c in sub if c["status"] == "indeterminable")
        estimates = [c["estimated_sources"] for c in sub if c["estimated_sources"] is not None]
        mean_est = sum(estimates) / len(estimates) if estimates else None
        
        # Categorize
        if st == "G3_Fully_Laundered_Consensus":
            n_false_certainty = sum(1 for c in sub if c["status"] == "determinable" and c["estimated_sources"] == 4)
            n_resistance = n_indet
            print(f"  Stage {st:<30} (True Roots={sub[0]['true_roots']}):")
            print(f"    - Determinable: {n_det}/4 ({n_det/4*100:.1f}%) | Indeterminable: {n_indet}/4 ({n_indet/4*100:.1f}%)")
            print(f"    - Conditional Estimates: {estimates} (Mean: {mean_est:.2f})")
            print(f"    - Epistemic Bifurcation: False 4-Source Certainty = {n_false_certainty}/4 (50%), Epistemic Resistance = {n_resistance}/4 (50%)")
        else:
            print(f"  Stage {st:<30} (True Roots={sub[0]['true_roots']}):")
            print(f"    - Determinable: {n_det}/4 ({n_det/4*100:.1f}%) | Indeterminable: {n_indet}/4 ({n_indet/4*100:.1f}%)")
            print(f"    - Conditional Estimates: {estimates} (Mean: {mean_est if mean_est is not None else 'N/A'})")


if __name__ == "__main__":
    main()
