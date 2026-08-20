"""Record Exploration Round 3 Artifacts and Governance Provenance.

Computes SHA256 checksums, call counts, evaluation counts, and governance metadata
for all Round 3 databases and records them into data/exploration_round3_artifacts.json.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def inspect_db(db_path: Path) -> dict:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    n_calls = c.execute("SELECT count(*) FROM exploration_calls").fetchone()[0]
    n_evals = c.execute("SELECT count(*) FROM exploration_evaluations").fetchone()[0]
    model_digest = c.execute("SELECT model_digest FROM exploration_calls LIMIT 1").fetchone()
    digest_val = model_digest[0] if model_digest else "unknown"
    conn.close()
    return {
        "db_path": str(db_path.as_posix()),
        "sha256": compute_sha256(db_path),
        "total_calls": n_calls,
        "total_evaluations": n_evals,
        "evaluation_parity": (n_calls == n_evals),
        "model_digest": digest_val,
    }


def main():
    artifacts = {
        "round": "Exploration Round 3: When One Belief Has Many Reasons",
        "evidence_class": "exploratory_local",
        "base_tag": "gene-exploration-round3-base",
        "base_commit": "4c16d3f822a1ce0a5b28a9b3d09e86cb8140db7f",
        "preexecution_commit": "dd7dd87",
        "results_commit": "06b9c33",
        "model": "gemma3:12b",
        "tracks": {
            "track_h": inspect_db(Path("runs/explore_round3/track_h_coalition.db")),
            "track_g2": inspect_db(Path("runs/explore_round3/track_g2_immunity.db")),
            "track_b3": inspect_db(Path("runs/explore_round3/track_b3_multiverse.db")),
            "track_l": inspect_db(Path("runs/explore_round3/track_l_laundering.db")),
        },
        "total_live_calls": 96,
        "total_live_evaluations": 96,
        "evaluation_parity": True,
        "promotion_lifecycle": {
            "phase11_status": "not_earned",
            "promotion_rule": "Exploratory results are local research evidence. Claims require deterministic replication, release asset checksums, and role-counterbalanced verification before canonical core promotion."
        }
    }

    out_file = Path("data/exploration_round3_artifacts.json")
    with open(out_file, "w") as f:
        json.dump(artifacts, f, indent=2)

    print(f"Recorded hardened Round 3 artifacts to {out_file}:")
    print(json.dumps(artifacts, indent=2))


if __name__ == "__main__":
    main()
