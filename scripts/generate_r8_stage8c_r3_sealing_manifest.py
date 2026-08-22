"""Generates cryptographic sealing manifest and persists sealed worlds for Stage 8C-R3 (CONTRACT-R8-8C-R3)."""

import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "src"))

from gene.benchmarks.r8_stage8c_r3.worlds import generate_stage8c_r3_worlds


def generate_sealing_manifest():
    root = Path(__file__).resolve().parent.parent
    base_sha = "1f3b0207345563ce903d00777455e1f8ed0f46f0"

    # Generate and persist sealed worlds and gold manifest
    worlds, gold_manifest = generate_stage8c_r3_worlds(seed=3141592653)
    worlds_path = root / "research" / "contracts" / "WORLDS-R8-8C-R3.json"
    gold_path = root / "research" / "contracts" / "GOLD_MANIFEST-R8-8C-R3.json"

    worlds_path.write_text(json.dumps(worlds, indent=2), encoding="utf-8")
    gold_path.write_text(json.dumps(gold_manifest, indent=2), encoding="utf-8")

    assets = [
        "src/gene/benchmarks/r8_stage8c_r3/prompts.py",
        "src/gene/benchmarks/r8_stage8c_r3/worlds.py",
        "src/gene/benchmarks/r8_stage8c_r3/runner.py",
        "src/gene/benchmarks/r8_stage8c_r3/verifier.py",
        "research/contracts/CONTRACT-R8-8C-R3.md",
        "research/contracts/WORLDS-R8-8C-R3.json",
        "research/contracts/GOLD_MANIFEST-R8-8C-R3.json",
    ]

    manifest = {
        "contract_id": "CONTRACT-R8-8C-R3",
        "base_sha": base_sha,
        "assets": {},
    }

    for rel_path in assets:
        full_path = root / rel_path
        assert full_path.is_file(), f"Asset missing: {full_path}"
        data = full_path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        manifest["assets"][rel_path] = digest

    manifest_path = root / "research" / "contracts" / "SEALING_MANIFEST-R8-8C-R3.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated fresh sealing manifest at: {manifest_path}")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    generate_sealing_manifest()
