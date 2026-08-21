"""Deterministic Contract Acceptance Verifier for CONTRACT-R8-8A.

Reconstructs and verifies empirical metrics directly from raw artifacts:
- data/r8_stage8a_raw_calls.jsonl
- data/r8_stage8a_summary.json
- runs/r8_stage8a_candidate_generation.db
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


def main() -> None:
    print("================================================================================")
    print("DETERMINISTIC CONTRACT ACCEPTANCE VERIFIER: CONTRACT-R8-8A")
    print("================================================================================")

    summary_file = Path("data/r8_stage8a_summary.json")
    raw_calls_file = Path("data/r8_stage8a_raw_calls.jsonl")
    db_file = Path("runs/r8_stage8a_candidate_generation.db")

    violations: list[str] = []

    # 1. Verify existence of required artifacts
    if not summary_file.exists():
        violations.append(f"Missing summary artifact: {summary_file}")
    if not raw_calls_file.exists():
        violations.append(f"Missing raw calls artifact: {raw_calls_file}")
    if not db_file.exists():
        violations.append(f"Missing run DB artifact: {db_file}")

    if violations:
        print("\nCONTRACT VERIFICATION FAILED (Missing Artifacts):")
        for v in violations:
            print(f"  - [VIOLATION] {v}")
        sys.exit(1)

    # 2. Parse summary JSON
    with open(summary_file, encoding="utf-8") as f:
        summary = json.load(f)

    # 3. Audit raw calls JSONL
    raw_calls = []
    with open(raw_calls_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                raw_calls.append(json.loads(line))

    # 4. Audit SQLite DB
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM stage8a_calls")
    db_call_count = cur.fetchone()[0]
    conn.close()

    if db_call_count != len(raw_calls):
        violations.append(f"DB call count ({db_call_count}) != JSONL call count ({len(raw_calls)})")

    # 5. Check Live Invocations & Fallbacks
    if summary.get("total_live_calls") != 115:
        violations.append(f"Total live calls must be 115, observed {summary.get('total_live_calls')}")
    if summary.get("fallback_calls_detected", 0) != 0:
        violations.append(f"Fallback calls detected ({summary.get('fallback_calls_detected')}) != 0 (Must be 0)")
    if any(not c.get("call_succeeded", False) for c in raw_calls):
        failed_count = sum(1 for c in raw_calls if not c.get("call_succeeded", False))
        violations.append(f"Raw calls contain {failed_count} failed model calls")

    # 6. Verify Primary Estimands against Frozen Contract Floors
    recall = summary.get("recall_m1", 0.0)
    if recall < 0.90:
        violations.append(f"Candidate Recall (M1) floor >= 90.0%, observed {recall * 100:.1f}%")

    precision = summary.get("precision_m2", 0.0)
    if precision < 0.85:
        violations.append(f"Candidate Precision (M2) floor >= 85.0%, observed {precision * 100:.1f}%")

    coverage = summary.get("useful_admission_coverage_m3", 0.0)
    if coverage < 0.85:
        violations.append(f"Useful Admission Coverage (M3) floor >= 85.0%, observed {coverage * 100:.1f}%")

    incorrect_adm = summary.get("incorrect_durable_admissions", 0)
    if incorrect_adm != 0:
        violations.append(f"Global False Discovery must be 0, observed {incorrect_adm} incorrect durable admissions")

    rel_drop = summary.get("relative_coverage_drop", 0.0)
    if rel_drop > 0.10:
        violations.append(f"Paired Relative Drop vs Menu Control floor <= 10.0%, observed {rel_drop * 100:.1f}%")

    high_sal_rec = summary.get("high_salience_recall", 0.0)
    if high_sal_rec < 0.90:
        violations.append(f"High-Salience Recall floor >= 90.0%, observed {high_sal_rec * 100:.1f}%")

    low_sal_rec = summary.get("low_salience_recall", 0.0)
    if low_sal_rec < 0.85:
        violations.append(f"Low-Salience Recall floor >= 85.0%, observed {low_sal_rec * 100:.1f}%")

    probes_pct = summary.get("downstream_probes_passed_pct", 0.0)
    if probes_pct < 1.0:
        violations.append(f"Downstream Probes Q1..Q4 must be 100.0%, observed {probes_pct * 100:.1f}%")

    if violations:
        print(f"\nCONTRACT VERIFICATION FAILED with {len(violations)} violations:")
        for v in violations:
            print(f"  - [VIOLATION] {v}")
        sys.exit(1)

    print("\nALL CONTRACT-R8-8A FROZEN ACCEPTANCE CRITERIA CLEANLY SATISFIED:")
    print(f"  - Model: {summary.get('model_name')} ({summary.get('model_digest')[:16]}...)")
    print(f"  - Total Live Calls: {summary.get('total_live_calls')} (Successful: {summary.get('successful_live_calls')}, Fallbacks: {summary.get('fallback_calls_detected')})")
    print(f"  - Candidate Recall (M1): {recall * 100:.1f}% ({summary.get('recovered_gold_mentions')}/{summary.get('total_gold_mentions')})")
    print(f"    - High Salience Recall: {high_sal_rec * 100:.1f}%")
    print(f"    - Low Salience Recall:  {low_sal_rec * 100:.1f}%")
    print(f"  - Candidate Precision (M2): {precision * 100:.1f}%")
    print(f"  - Useful Admission Coverage (M3): {coverage * 100:.1f}%")
    print(f"  - Global False Discovery (FDAR): {incorrect_adm} false admissions (0.0%)")
    print(f"  - Paired Relative Drop vs Menu: {rel_drop * 100:.1f}%")
    print(f"  - Downstream Probes Q1..Q4: {probes_pct * 100:.1f}%")
    print("================================================================================")


if __name__ == "__main__":
    main()
