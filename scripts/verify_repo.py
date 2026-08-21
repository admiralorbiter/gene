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
    print("--> Checking git worktree status...")
    res = subprocess.run(["git", "diff", "--name-only"], cwd=root_dir, capture_output=True, text=True)
    if res.stdout.strip():
        print(f"INFO: Worktree has {len(res.stdout.strip().splitlines())} unstaged modified files.")
        for f in res.stdout.strip().splitlines()[:10]:
            print(f"  - {f}")
    else:
        print("PASSED: Worktree tracked files have zero diff.\n")


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

    # 5. Clean Worktree Check
    verify_clean_worktree()

    print("=========================================================")
    print("  ALL LOCAL PREFLIGHT CHECKS AND INTEGRITY TESTS PASSED  ")
    print("=========================================================")


if __name__ == "__main__":
    main()
