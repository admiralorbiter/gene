"""Track H Deep Audit: Full 16-Point Lattice, S_C Recovery, Monotonicity & Role Semantics.

Analyzes runs/explore_round3/track_h_coalition.db across both VELORA and KESTREL ecologies.
"""

from __future__ import annotations

import itertools
import json
import sqlite3
from pathlib import Path


def load_track_h_data(db_path: Path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT call_id, emitted_claim, metadata_json, eval_metadata_json FROM exploration_calls JOIN exploration_evaluations USING (call_id)").fetchall()
    conn.close()

    by_station = {"VELORA": {}, "KESTREL": {}}
    for cid, emitted, meta_j, eval_j in rows:
        meta = json.loads(meta_j)
        st = meta["station"]
        knocked = tuple(meta["knocked_out"])
        active = tuple(sorted(list(set(["A", "B", "D", "E"]) - set(knocked))))
        expected = meta["expected"]
        label = meta["label"]
        by_station[st][active] = {
            "knocked": knocked,
            "active": active,
            "emitted": emitted,
            "expected": expected,
            "label": label,
            "call_id": cid,
        }
    return by_station


def extract_minimal_causal_coalitions(active_results: dict[tuple[str, ...], str], target: str = "PROTO_X7") -> list[set[str]]:
    sufficient_active = [set(active) for active, d in active_results.items() if d["emitted"] == target]
    minimal = []
    for s in sorted(sufficient_active, key=len):
        if not any(existing.issubset(s) for existing in minimal):
            minimal.append(s)
    return minimal


def check_monotonicity(active_results: dict[tuple[str, ...], str], target: str = "PROTO_X7") -> list[dict]:
    """Check whether S -> target implies all supersets S' superset S -> target."""
    violations = []
    all_active_sets = list(active_results.keys())

    for s_tuple, data in active_results.items():
        if data["emitted"] == target:
            s_set = set(s_tuple)
            # Find all proper supersets of s_set
            for sup_tuple, sup_data in active_results.items():
                sup_set = set(sup_tuple)
                if s_set < sup_set:  # Proper superset
                    if sup_data["emitted"] != target:
                        violations.append({
                            "subset": sorted(list(s_set)),
                            "subset_emitted": data["emitted"],
                            "superset": sorted(list(sup_set)),
                            "superset_emitted": sup_data["emitted"],
                            "added_premise": sorted(list(sup_set - s_set)),
                        })
    return violations


def main():
    db_path = Path("runs/explore_round3/track_h_coalition.db")
    by_station = load_track_h_data(db_path)

    print("================================================================================")
    print("      TRACK H POST-EXECUTION AUDIT: LATTICE, S_C, MONOTONICITY & ROLES          ")
    print("================================================================================")

    for st in ["VELORA", "KESTREL"]:
        data = by_station[st]
        s_c = extract_minimal_causal_coalitions(data)
        monotonicity_violations = check_monotonicity(data)

        print(f"\n################################################################################")
        print(f"STATION: {st}")
        print(f"################################################################################")
        print(f"Formal Minimal Support S_F = [{{'A', 'B'}}, {{'D', 'E'}}]")
        print(f"Empirical Minimal Behavioral Support S_C = {[sorted(list(s)) for s in s_c]}")
        print(f"S_F == S_C Concordance: {set(frozenset(s) for s in s_c) == {frozenset(['A', 'B']), frozenset(['D', 'E'])}}")

        print(f"\n--- Complete 16-Point Active Exposure Lattice ---")
        print(f"{'Active Premises':<20} {'Knocked Out':<20} {'Emitted':<12} {'Expected':<12} {'Status':<15}")
        print("-" * 79)
        for active_tuple in sorted(data.keys(), key=lambda x: (len(x), x)):
            d = data[active_tuple]
            act_str = "{" + ",".join(active_tuple) + "}" if active_tuple else "Ø"
            kno_str = "{" + ",".join(d["knocked"]) + "}" if d["knocked"] else "Ø"
            is_match = d["emitted"] == d["expected"]
            print(f"{act_str:<20} {kno_str:<20} {d['emitted']:<12} {d['expected']:<12} {'CONCORDANT' if is_match else 'DISCORDANT'}")

        print(f"\n--- Monotonicity Audit ---")
        if not monotonicity_violations:
            print("  Result: STRICTLY MONOTONIC (No superset regressions detected).")
        else:
            print(f"  Result: NON-MONOTONIC ({len(monotonicity_violations)} violations detected):")
            for v in monotonicity_violations:
                print(f"    - Subset {v['subset']} emitted {v['subset_emitted']}, but adding {v['added_premise']} -> Superset {v['superset']} emitted {v['superset_emitted']}!")

        print(f"\n--- Premise Role Representation in S_C ---")
        premise_counts = {"A (manager)": 0, "B (reports_to S1)": 0, "D (sector_lead)": 0, "E (reports_to S2)": 0}
        for s in s_c:
            if "A" in s: premise_counts["A (manager)"] += 1
            if "B" in s: premise_counts["B (reports_to S1)"] += 1
            if "D" in s: premise_counts["D (sector_lead)"] += 1
            if "E" in s: premise_counts["E (reports_to S2)"] += 1
        for p_name, cnt in premise_counts.items():
            print(f"  {p_name:<25}: appears in {cnt}/{len(s_c)} minimal coalitions")


if __name__ == "__main__":
    main()
