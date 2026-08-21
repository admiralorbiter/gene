"""Comprehensive Local Verification Script for GENE.

Performs deterministic, offline preflight checks:
1. Pytest suite execution across all tests.
2. Documentation and asset link integrity check.
3. Canonical results manifest regeneration and semantic check (--check).
4. Interactive Atlas claim ledger synchronization check.
5. Worktree cleanliness assertion (zero unstaged/untracked drift).
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

root_dir = Path(__file__).resolve().parent.parent


def run_check(name: str, cmd: list[str]) -> None:
    print(f"--> Running check: {name} ({' '.join(cmd)})")
    res = subprocess.run(cmd, cwd=root_dir)
    if res.returncode != 0:
        print(f"FAILED: {name}")
        sys.exit(res.returncode)
    print(f"PASSED: {name}\n")


def verify_atlas_sync() -> None:
    print("--> Checking Atlas Claims Deep Synchronization...")
    ledger_path = root_dir / "data" / "claim_ledger.json"
    atlas_path = root_dir / "docs" / "atlas" / "data" / "claims.json"
    assert ledger_path.exists() and atlas_path.exists(), "Both claim_ledger.json and atlas claims.json must exist!"

    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    with open(atlas_path, "r", encoding="utf-8") as f:
        atlas = json.load(f)

    assert ledger["claims"] == atlas["claims"], "Atlas claims.json does not deeply match data/claim_ledger.json!"
    print("PASSED: Atlas claims match claim_ledger.json deeply.\n")


def verify_clean_worktree() -> None:
    print("--> Checking git worktree status (git status --porcelain)...")
    res = subprocess.run(["git", "status", "--porcelain"], cwd=root_dir, capture_output=True, text=True)
    out = res.stdout.strip()
    if out:
        lines = out.splitlines()
        print(f"FAILED: Worktree has {len(lines)} dirty / untracked files:")
        for line in lines[:15]:
            print(f"  {line}")
        print("\nERROR: Verification failed due to uncommitted or untracked worktree drift.")
        sys.exit(1)
    else:
        print("PASSED: Worktree is 100% clean with zero drift.\n")


def verify_git_tracked_artifacts() -> None:
    print("--> Verifying all canonical research artifacts are tracked in git...")
    required_artifacts = [
        "data/canonical_results_manifest.json",
        "data/claim_ledger.json",
        "data/exploration_round5_stage5a_cases.jsonl",
        "data/exploration_round5_stage5a_summary.json",
        "data/exploration_round5_stage5b_cases.jsonl",
        "data/exploration_round5_stage5b_summary.json",
        "data/exploration_round5_stage5c_manifest.json",
        "data/exploration_round5_stage5c_summary.json",
        "data/exploration_round5_stage5c_runs.json",
        "data/exploration_round5_stage5c_calls.jsonl",
        "data/exploration_round6_scale_envelope_summary.json",
        "data/exploration_round6_lineage_threat_matrix_summary.json",
        "data/exploration_round6_stage6b_cases.jsonl",
        "data/exploration_round6_stage6b_manifest.json",
        "data/exploration_round6_stage6b_results_summary.json",
        "data/exploration_round6_stage6b1_temporal_summary.json",
        "data/exploration_round6_stage6c_cases.jsonl",
        "data/exploration_round6_stage6c_manifest.json",
        "data/exploration_round6_stage6c_summary.json",
        "data/exploration_round6_stage6c_results.db",
        "data/exploration_round6_stage6c_raw_calls.jsonl",
        "data/exploration_round7_stage7a_benchmark_summary.json",
    ]
    for rel_path in required_artifacts:
        res = subprocess.run(["git", "ls-files", "--error-unmatch", rel_path], cwd=root_dir, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"FAILED: Artifact {rel_path} is NOT tracked in git!")
            sys.exit(1)
    print("PASSED: All canonical data artifacts are actively tracked in git.\n")


def main() -> None:
    print("=========================================================")
    print("      GENE LOCAL REPRODUCIBILITY & VERIFICATION SUITE    ")
    print("=========================================================\n")

    # 1. Pytest
    run_check("Pytest Suite", [sys.executable, "-m", "pytest", "-v"])

    # 2. Doc links
    run_check("Doc Links Integrity", [sys.executable, "scripts/check_doc_links.py"])

    # 3. Manifest Semantic Check (Non-destructive)
    run_check("Canonical Manifest Check", [sys.executable, "scripts/generate_results_manifest.py", "--check"])

    # 4. Atlas Deep Sync
    verify_atlas_sync()

    # 5. Git-Tracked Artifacts Invariant
    verify_git_tracked_artifacts()

    # 6. Clean Worktree Check
    verify_clean_worktree()

    print("=========================================================")
    print("  ALL LOCAL PREFLIGHT CHECKS AND INTEGRITY TESTS PASSED  ")
    print("=========================================================")


if __name__ == "__main__":
    main()
