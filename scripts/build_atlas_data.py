"""Script to compile canonical evidence and results into the GENE Atlas web asset directory.

Ensures that docs/atlas/data/ always mirrors data/claim_ledger.json,
data/canonical_results_manifest.json, and docs/design/epigraphs.json.
"""

from __future__ import annotations

import json
from pathlib import Path


def build_atlas_data() -> None:
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data"
    atlas_data_dir = root_dir / "docs" / "atlas" / "data"
    atlas_data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy claims ledger
    claims_src = data_dir / "claim_ledger.json"
    claims_dst = atlas_data_dir / "claims.json"
    claims_dst.write_text(claims_src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Compiled {claims_src} -> {claims_dst}")

    # 2. Copy manifest
    manifest_src = data_dir / "canonical_results_manifest.json"
    manifest_dst = atlas_data_dir / "results.json"
    manifest_dst.write_text(manifest_src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Compiled {manifest_src} -> {manifest_dst}")

    # 3. Copy epigraphs
    epigraphs_src = root_dir / "docs" / "design" / "epigraphs.json"
    epigraphs_dst = atlas_data_dir / "epigraphs.json"
    epigraphs_dst.write_text(epigraphs_src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Compiled {epigraphs_src} -> {epigraphs_dst}")


if __name__ == "__main__":
    build_atlas_data()
