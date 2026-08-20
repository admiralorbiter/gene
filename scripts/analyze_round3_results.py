"""Round 3 Portfolio Analysis Script.

Analyzes empirical results across all 4 databases in runs/explore_round3/
computing preregistered endpoints for Tracks H, G2, B3, and L.
"""

from __future__ import annotations

import sqlite3
import json
from pathlib import Path


def analyze_track_h(db_path: Path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT call_id, emitted_claim, metadata_json, eval_metadata_json FROM exploration_calls JOIN exploration_evaluations USING (call_id)").fetchall()
    conn.close()

    print(f"\n=======================================================")
    print(f"TRACK H: COALITION CAUSALITY & OVERDETERMINATION (N={len(rows)})")
    print(f"=======================================================")
    
    by_station = {"VELORA": {}, "KESTREL": {}}
    for cid, emitted, meta_j, eval_j in rows:
        meta = json.loads(meta_j)
        eval_meta = json.loads(eval_j)
        st = meta["station"]
        label = meta["label"]
        knocked = tuple(meta["knocked_out"])
        expected = meta["expected"]
        by_station[st][knocked] = (emitted, expected, label)

    for st, data in by_station.items():
        print(f"\n--- Station: {st} (16-Point Lattice) ---")
        concordant = 0
        for knocked, (emitted, expected, label) in sorted(data.items(), key=lambda x: (len(x[0]), x[0])):
            is_match = (emitted == expected)
            if is_match: concordant += 1
            knocked_str = "{" + ",".join(knocked) + "}" if knocked else "Ø"
            print(f"  Knockout {knocked_str:<12} [{label:<24}] -> Emitted: {emitted:<10} | Expected: {expected:<10} | {'MATCH' if is_match else 'DISCORDANT'}")
        print(f"Concordance Rate: {concordant}/16 ({concordant/16*100:.1f}%)")


def analyze_track_g2(db_path: Path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT call_id, emitted_claim, metadata_json, eval_metadata_json FROM exploration_calls JOIN exploration_evaluations USING (call_id)").fetchall()
    conn.close()

    print(f"\n=======================================================")
    print(f"TRACK G2: NON-DESTRUCTIVE SUPPORT IMMUNITY (N={len(rows)})")
    print(f"=======================================================")
    
    by_arm = {}
    for cid, emitted, meta_j, eval_j in rows:
        meta = json.loads(meta_j)
        arm = meta["arm"]
        expected = meta["expected"]
        by_arm.setdefault(arm, []).append((emitted == expected, emitted, expected))

    for arm, results in by_arm.items():
        correct = sum(1 for r in results if r[0])
        total = len(results)
        print(f"  Arm: {arm:<42} -> {correct}/{total} ({correct/total*100:.1f}%) [Emitted: {results[0][1]}, Expected: {results[0][2]}]")


def analyze_track_b3(db_path: Path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT call_id, emitted_claim, metadata_json, eval_metadata_json FROM exploration_calls JOIN exploration_evaluations USING (call_id)").fetchall()
    conn.close()

    print(f"\n=======================================================")
    print(f"TRACK B3: MONOCULTURE MULTIVERSE (N={len(rows)})")
    print(f"=======================================================")
    
    main_rows = []
    exact_replay_rows = []
    seed_perturb_rows = []

    for cid, emitted, meta_j, eval_j in rows:
        meta = json.loads(meta_j)
        eval_meta = json.loads(eval_j)
        arm = meta.get("assay_arm")
        if arm == "main_factorial":
            main_rows.append((meta, emitted))
        elif arm == "exact_replay":
            exact_replay_rows.append((meta, emitted))
        elif arm == "seed_perturb":
            seed_perturb_rows.append((meta, emitted))

    # 1. Main 16 Factorial Cells
    indep_maj = [emitted == meta["majority_protocol"] for meta, emitted in main_rows if meta["root_structure"] == "independent"]
    mono_maj = [emitted == meta["majority_protocol"] for meta, emitted in main_rows if meta["root_structure"] == "monoculture"]
    
    p_indep = sum(indep_maj) / len(indep_maj) if indep_maj else 0.0
    p_mono = sum(mono_maj) / len(mono_maj) if mono_maj else 0.0
    delta_root = p_indep - p_mono

    # Also check abstention rate
    indep_unknown = sum(1 for meta, emitted in main_rows if meta["root_structure"] == "independent" and emitted == "UNKNOWN")
    mono_unknown = sum(1 for meta, emitted in main_rows if meta["root_structure"] == "monoculture" and emitted == "UNKNOWN")

    print(f"  Main 16 Factorial Cells:")
    print(f"    P(Majority | Independent Roots) = {sum(indep_maj)}/8 ({p_indep*100:.1f}%) [UNKNOWN: {indep_unknown}/8]")
    print(f"    P(Majority | Monoculture Roots) = {sum(mono_maj)}/8 ({p_mono*100:.1f}%) [UNKNOWN: {mono_unknown}/8]")
    print(f"    Delta_root = {delta_root:+.3f}")

    # 2. Exact Replay Instability (eps_replay)
    main_by_cell = {meta["cell_id"]: emitted for meta, emitted in main_rows}
    replay_disagreements = 0
    for meta, emitted in exact_replay_rows:
        orig = main_by_cell.get(meta["cell_id"])
        if orig != emitted:
            replay_disagreements += 1
            print(f"    [EXACT REPLAY INSTABILITY] {meta['cell_id']}: {orig} -> {emitted}")
    eps_replay = replay_disagreements / len(exact_replay_rows) if exact_replay_rows else 0.0
    print(f"  Exact CallSpec Replay Instability (eps_replay) = {replay_disagreements}/{len(exact_replay_rows)} ({eps_replay*100:.1f}%)")

    # 3. Seed Perturbation Sensitivity (eps_seed)
    seed_disagreements = 0
    for meta, emitted in seed_perturb_rows:
        orig = main_by_cell.get(meta["cell_id"])
        if orig != emitted:
            seed_disagreements += 1
            print(f"    [SEED PERTURBATION DIFF] {meta['cell_id']}: {orig} (seed 42) -> {emitted} (seed 43)")
    eps_seed = seed_disagreements / len(seed_perturb_rows) if seed_perturb_rows else 0.0
    print(f"  Seed Perturbation Sensitivity (eps_seed) = {seed_disagreements}/{len(seed_perturb_rows)} ({eps_seed*100:.1f}%)")


def analyze_track_l(db_path: Path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT call_id, emitted_claim, metadata_json, eval_metadata_json FROM exploration_calls JOIN exploration_evaluations USING (call_id)").fetchall()
    conn.close()

    print(f"\n=======================================================")
    print(f"TRACK L: INDEPENDENCE LAUNDERING (N={len(rows)})")
    print(f"=======================================================")
    
    by_stage = {}
    for cid, emitted, meta_j, eval_j in rows:
        meta = json.loads(meta_j)
        eval_meta = json.loads(eval_j)
        st_name = meta["stage_name"]
        gen = meta["generation"]
        true_roots = meta["true_root_count"]
        status = eval_meta.get("independence_status")
        est = eval_meta.get("estimated_independent_sources")
        by_stage.setdefault(st_name, []).append((gen, true_roots, status, est, emitted))

    for st_name, results in by_stage.items():
        n_det = sum(1 for r in results if r[2] == "determinable")
        n_indet = sum(1 for r in results if r[2] == "indeterminable")
        est_list = [r[3] for r in results if r[3] is not None]
        avg_est = sum(est_list) / len(est_list) if est_list else 0.0
        true_r = results[0][1]
        print(f"  Stage: {st_name:<30} (True Roots={true_r})")
        print(f"    Determinable: {n_det}/4 ({n_det/4*100:.1f}%) | Indeterminable: {n_indet}/4 ({n_indet/4*100:.1f}%)")
        print(f"    Estimated Sources: {est_list} (Mean: {avg_est:.2f})")


if __name__ == "__main__":
    analyze_track_h(Path("runs/explore_round3/track_h_coalition.db"))
    analyze_track_g2(Path("runs/explore_round3/track_g2_immunity.db"))
    analyze_track_b3(Path("runs/explore_round3/track_b3_multiverse.db"))
    analyze_track_l(Path("runs/explore_round3/track_l_laundering.db"))
