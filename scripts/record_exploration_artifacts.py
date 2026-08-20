"""Record SHA-256 hashes and row counts for all exploratory run databases."""

import hashlib
import json
from pathlib import Path
import sqlite3


def generate_exploration_manifest(runs_dir: Path = Path("runs/explore")) -> dict:
    artifacts = {}

    if runs_dir.exists():
        for db_path in sorted(runs_dir.glob("*.db")):
            with open(db_path, "rb") as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            size_bytes = db_path.stat().st_size
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            row_counts = {}
            for t in tables:
                row_counts[t] = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            conn.close()

            artifacts[db_path.name] = {
                "file_path": str(db_path).replace("\\", "/"),
                "sha256": sha256,
                "size_bytes": size_bytes,
                "tables": tables,
                "row_counts": row_counts,
            }

    manifest = {
        "manifest_version": "1.0.0",
        "round": "Exploration Round 1",
        "base_commit": "9353005",
        "artifacts": artifacts,
    }
    return manifest


if __name__ == "__main__":
    out_path = Path("data/exploration_artifacts.json")
    manifest = generate_exploration_manifest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2))
    print(f"Recorded exploration artifacts manifest to {out_path}:")
    print(json.dumps(manifest, indent=2))
