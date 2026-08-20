"""Script to fetch and verify frozen SQLite research artifacts.

Verifies SHA-256 checksums of all frozen experiment databases.
If an artifact is missing locally, attempts download from the GitHub release asset repository.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import urllib.request


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 hex digest of a local file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_or_fetch_artifacts(root_dir: Path, download_if_missing: bool = False) -> tuple[int, int, list[str]]:
    """Verify or download all artifacts declared in data/artifacts.json."""
    artifacts_file = root_dir / "data" / "artifacts.json"
    if not artifacts_file.exists():
        raise FileNotFoundError(f"Artifacts manifest not found: {artifacts_file}")

    with open(artifacts_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    verified = 0
    downloaded = 0
    errors = []

    for filename, info in manifest.items():
        expected_sha = info["sha256"]
        target_path = root_dir / filename

        if not target_path.exists():
            if download_if_missing:
                url = info.get("download_uri")
                if not url:
                    errors.append(f"{filename}: Missing locally and no download_uri configured.")
                    continue
                print(f"Downloading {filename} from {url}...")
                try:
                    urllib.request.urlretrieve(url, target_path)
                    downloaded += 1
                except Exception as e:
                    errors.append(f"{filename}: Download failed from {url} ({e})")
                    continue
            else:
                errors.append(f"{filename}: File missing locally at {target_path}")
                continue

        # Check hash
        actual_sha = compute_sha256(target_path)
        if actual_sha.lower() != expected_sha.lower():
            errors.append(f"{filename}: SHA-256 mismatch! Expected {expected_sha}, got {actual_sha}")
        else:
            verified += 1

    return verified, downloaded, errors


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    download_flag = "--download" in sys.argv or "-d" in sys.argv
    print(f"Verifying frozen research artifacts in {root} (download_missing={download_flag})...")

    verified_cnt, downloaded_cnt, error_list = verify_or_fetch_artifacts(root, download_if_missing=download_flag)
    print(f"Results: {verified_cnt} verified, {downloaded_cnt} downloaded, {len(error_list)} errors.")

    if error_list:
        print("\nVerification Errors:")
        for err in error_list:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("All frozen database artifacts are authentic and match canonical checksums!")
