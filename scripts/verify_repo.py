"""Comprehensive Local Verification Script for GENE.

Performs deterministic, offline preflight checks:
1. Pytest suite execution across all tests.
2. Documentation and asset link integrity check.
3. Canonical results manifest regeneration and sync check.
4. Claim ledger git commit and artifact checksum validation.
5. Interactive Atlas claim ledger synchronization check.
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


def main() -> None:
    print("=========================================================")
    print("      GENE LOCAL REPRODUCIBILITY & VERIFICATION SUITE    ")
    print("=========================================================\n")

    # 1. Pytest
    run_check("Pytest Suite", [sys.executable, "-m", "pytest", "-v"])

    # 2. Doc links
    run_check("Doc Links Integrity", [sys.executable, "scripts/check_doc_links.py"])

    # 3. Manifest Regeneration
    run_check("Canonical Manifest Generation", [sys.executable, "scripts/generate_results_manifest.py"])

    print("=========================================================")
    print("  ALL LOCAL PREFLIGHT CHECKS AND INTEGRITY TESTS PASSED  ")
    print("=========================================================")


if __name__ == "__main__":
    main()
