#!/usr/bin/env python3
"""CLI wrapper to run Stage 8C-R1 Confirmatory Benchmark."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.benchmarks.r8_stage8c_r1.runner import run_stage8c_r1_benchmark

if __name__ == "__main__":
    run_stage8c_r1_benchmark()
