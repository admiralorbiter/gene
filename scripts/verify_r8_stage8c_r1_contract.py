#!/usr/bin/env python3
"""CLI wrapper to run Stage 8C-R1 Acceptance Verifier."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.benchmarks.r8_stage8c_r1.verifier import verify_stage8c_r1_contract

if __name__ == "__main__":
    verify_stage8c_r1_contract()
