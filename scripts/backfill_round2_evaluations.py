"""Backfill exploration_evaluations table for Round 2 databases."""

import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone


def backfill_evaluations(db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")

    calls = c.execute("SELECT call_id, run_id, emitted_claim, metadata_json FROM exploration_calls").fetchall()
    count = 0

    for call_id, run_id, emitted_claim, meta_json in calls:
        eval_id = f"eval_{call_id}"
        meta = json.loads(meta_json) if meta_json else {}
        
        # DualOracle classification logic
        canonical_status = "UNKNOWN"
        local_status = "UNKNOWN"
        phenotype = "UNKNOWN"
        is_compliant = 1

        if "track_a2" in str(db_path):
            locus = meta.get("locus", "protocol")
            expected_clean = "PROTO_X7" if locus == "protocol" else "ROUTE_ALPHA"
            stale_val = "PROTO_Q2" if locus == "protocol" else "ROUTE_BETA"
            if emitted_claim == expected_clean:
                canonical_status = "TRUE"
                local_status = "TRUE"
                phenotype = "ACTIVE_CLEAN"
            elif emitted_claim == stale_val:
                canonical_status = "FALSE"
                local_status = "TRUE"
                phenotype = "ACTIVE_STALE"
            else:
                phenotype = "INACTIVE_UNKNOWN"

        elif "track_b2" in str(db_path):
            cond = meta.get("condition", "")
            if emitted_claim in ["PROTO_X", "PROTO_Y"]:
                phenotype = f"ACTIVE_{emitted_claim}"
            else:
                phenotype = "INACTIVE_UNKNOWN"

        elif "track_g" in str(db_path):
            if emitted_claim == "PROTO_X7":
                phenotype = "ACTIVE_SURVIVING"
            else:
                phenotype = "INACTIVE_COLLAPSED"

        elif "track_m" in str(db_path):
            case = meta.get("case", "")
            if emitted_claim in ["PROTO_X7", "PROTO_Q2"]:
                phenotype = f"ACTIVE_{emitted_claim}"
            elif emitted_claim == "UNKNOWN":
                phenotype = "INACTIVE_UNKNOWN"
            else:
                is_compliant = 0
                phenotype = "MALFORMED_OUTPUT"

        c.execute("""
            INSERT OR REPLACE INTO exploration_evaluations
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            eval_id,
            call_id,
            run_id,
            canonical_status,
            local_status,
            phenotype,
            is_compliant,
            json.dumps({"backfilled": True}),
            datetime.now(timezone.utc).isoformat(),
        ))
        count += 1

    conn.commit()
    conn.close()
    return count


if __name__ == "__main__":
    runs_dir = Path("runs/explore_round2")
    for db in sorted(runs_dir.glob("*.db")):
        n = backfill_evaluations(db)
        print(f"Backfilled {n} evaluations in {db.name}")
