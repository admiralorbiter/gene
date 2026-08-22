#!/usr/bin/env python3
"""CLI wrapper to verify CONTRACT-R8-8C-R2 Acceptance Gates."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.benchmarks.r8_stage8c_r2.verifier import verify_stage8c_r2_contract


def main():
    root = Path(__file__).resolve().parent.parent
    data_dir = root / "data"
    evidence_path = data_dir / "r8_stage8c_r2_candidate_evidence.jsonl"
    gold_manifest_path = data_dir / "r8_stage8c_r2_gold_manifest.json"
    db_path = data_dir / "r8_stage8c_r2_registry.sqlite"

    if not evidence_path.exists():
        print(f"Error: Evidence file not found: {evidence_path}")
        sys.exit(1)

    passed, summary = verify_stage8c_r2_contract(evidence_path, gold_manifest_path, db_path)

    summary_path = data_dir / "r8_stage8c_r2_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Summary written to: {summary_path}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
