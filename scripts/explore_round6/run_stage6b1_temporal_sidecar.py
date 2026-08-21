"""Stage 6B.1 Multi-Update Temporal-Ordering Sidecar Runner.

Demonstrates the necessity of bitemporal representation over single-clock (KT-LWW vs VT-LWW)
stores in the presence of out-of-order, retroactive, and delayed multi-update observation streams.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    BitemporalRule,
    EventType,
    TemporalEvent,
)


def run_stage6b1_sidecar() -> dict[str, Any]:
    f0 = BitemporalFact("occ_0", "Alice", "clearance", "ALPHA", roots=frozenset(["R0"]), source_id="s1")
    f1 = BitemporalFact("occ_1", "Alice", "clearance", "BETA", roots=frozenset(["R1"]), source_id="s1")
    f2 = BitemporalFact("occ_2", "Alice", "clearance", "GAMMA", roots=frozenset(["R2"]), source_id="s1")

    engine = BitemporalEngine(cautious_conflicts=True)
    for f in [f0, f1, f2]:
        engine.register_fact(f)

    # Event 0: t_k=0, t_v=[0, 5) -> ALPHA
    engine.record_event(TemporalEvent("ev0", EventType.ASSERT, t_knowledge=0, event_seq=0, t_valid_start=0.0, t_valid_end=5.0, target_fact_id="occ_0"))
    # Event 1: t_k=1, t_v=[10, inf) -> BETA (forward update, leaving gap [5, 10))
    engine.record_event(TemporalEvent("ev1", EventType.ASSERT, t_knowledge=1, event_seq=0, t_valid_start=10.0, target_fact_id="occ_1"))
    # Event 2: t_k=2, t_v=[5, 10) -> GAMMA (retroactive backfill into gap)
    engine.record_event(TemporalEvent("ev2", EventType.ASSERT, t_knowledge=2, event_seq=0, t_valid_start=5.0, t_valid_end=10.0, target_fact_id="occ_2"))

    # 12 Evaluation Coordinates testing the bitemporal coordinate grid (t_v, t_k)
    cases = [
        {"case_id": "TC_01", "t_v": 2.0, "t_k": 0, "expected_value": "ALPHA"},
        {"case_id": "TC_02", "t_v": 6.0, "t_k": 0, "expected_value": "UNKNOWN"},
        {"case_id": "TC_03", "t_v": 12.0, "t_k": 0, "expected_value": "UNKNOWN"},
        {"case_id": "TC_04", "t_v": 2.0, "t_k": 1, "expected_value": "ALPHA"},
        {"case_id": "TC_05", "t_v": 6.0, "t_k": 1, "expected_value": "UNKNOWN"},
        {"case_id": "TC_06", "t_v": 12.0, "t_k": 1, "expected_value": "BETA"},
        {"case_id": "TC_07", "t_v": 2.0, "t_k": 2, "expected_value": "ALPHA"},
        {"case_id": "TC_08", "t_v": 4.0, "t_k": 2, "expected_value": "ALPHA"},
        {"case_id": "TC_09", "t_v": 6.0, "t_k": 2, "expected_value": "GAMMA"},
        {"case_id": "TC_10", "t_v": 8.0, "t_k": 2, "expected_value": "GAMMA"},
        {"case_id": "TC_11", "t_v": 12.0, "t_k": 2, "expected_value": "BETA"},
        {"case_id": "TC_12", "t_v": 15.0, "t_k": 2, "expected_value": "BETA"},
    ]

    kt_lww_correct = 0
    vt_lww_correct = 0
    bitemp_correct = 0

    case_results = []

    for c in cases:
        tv = c["t_v"]
        tk = c["t_k"]
        expected = c["expected_value"]

        # 1. KT-LWW: At knowledge time tk, keeps the single record with max t_k
        known_kt = [f for f in [("ALPHA", 0), ("BETA", 1), ("GAMMA", 2)] if f[1] <= tk]
        kt_val = max(known_kt, key=lambda x: x[1])[0] if known_kt else "UNKNOWN"

        # 2. VT-LWW: At knowledge time tk, keeps the single record with max t_v <= tv
        known_vt = []
        if tk >= 0 and tv >= 0.0:
            known_vt.append(("ALPHA", 0.0))
        if tk >= 1 and tv >= 10.0:
            known_vt.append(("BETA", 10.0))
        if tk >= 2 and tv >= 5.0:
            known_vt.append(("GAMMA", 5.0))
        vt_val = max(known_vt, key=lambda x: x[1])[0] if known_vt else "UNKNOWN"

        # 3. Bitemporal Engine
        active = engine.get_active_facts(t_v=tv, t_k=tk)
        alice_active = [f for f in active if f.subject == "Alice" and f.predicate == "clearance"]
        bitemp_val = alice_active[0].obj if alice_active else "UNKNOWN"

        kt_match = (kt_val == expected)
        vt_match = (vt_val == expected)
        bt_match = (bitemp_val == expected)

        if kt_match:
            kt_lww_correct += 1
        if vt_match:
            vt_lww_correct += 1
        if bt_match:
            bitemp_correct += 1

        case_results.append({
            "case_id": c["case_id"],
            "query_coord": {"t_v": tv, "t_k": tk},
            "expected_value": expected,
            "kt_lww_value": kt_val,
            "vt_lww_value": vt_val,
            "bitemporal_value": bitemp_val,
            "kt_lww_correct": kt_match,
            "vt_lww_correct": vt_match,
            "bitemporal_correct": bt_match,
        })

    n = len(cases)
    summary = {
        "assay_name": "Stage 6B.1 Multi-Update Temporal-Ordering Micro-Assay",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_test_coordinates": n,
        "policy_accuracies": {
            "knowledge_time_lww": round(kt_lww_correct / n, 4),
            "valid_time_lww": round(vt_lww_correct / n, 4),
            "bitemporal_engine": round(bitemp_correct / n, 4),
        },
        "case_details": case_results,
    }

    out_path = Path(r"C:\Users\admir\Github\gene\data\exploration_round6_stage6b1_temporal_summary.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved Stage 6B.1 summary to {out_path}")
    print(f"KT-LWW Accuracy: {kt_lww_correct}/{n} ({kt_lww_correct/n*100:.1f}%)")
    print(f"VT-LWW Accuracy: {vt_lww_correct}/{n} ({vt_lww_correct/n*100:.1f}%)")
    print(f"Bitemporal Accuracy: {bitemp_correct}/{n} ({bitemp_correct/n*100:.1f}%)")
    return summary


if __name__ == "__main__":
    run_stage6b1_sidecar()
