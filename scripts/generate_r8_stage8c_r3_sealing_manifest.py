"""Generates cryptographic sealing manifest for Stage 8C-R3 (CONTRACT-R8-8C-R3)."""

import hashlib
import json
from pathlib import Path


def generate_sealing_manifest():
    root = Path(__file__).resolve().parent.parent
    base_sha = "05d9e93554021151085124dba04bce79075e9fdf"

    assets = [
        "src/gene/benchmarks/r8_stage8c_r3/prompts.py",
        "src/gene/benchmarks/r8_stage8c_r3/worlds.py",
        "src/gene/benchmarks/r8_stage8c_r3/runner.py",
        "src/gene/benchmarks/r8_stage8c_r3/verifier.py",
        "research/contracts/CONTRACT-R8-8C-R3.md",
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
