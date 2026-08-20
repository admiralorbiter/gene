"""Audit raw response text from Cell 2 database to verify unadulterated model outputs."""

import json
import sqlite3
import sys

def audit_cell2_db(db_path: str = "gene_d1_preflight_20260819_181409.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT call_id, task_id, response_text, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms
        FROM calls
        WHERE call_id LIKE '%_v2_%'
        ORDER BY created_at
    """).fetchall()

    print("=" * 85)
    print(f"   CELL 2 RAW SQLITE DATABASE AUDIT: {db_path}")
    print("=" * 85)
    print(f"Found {len(rows)} Cell 2 calls.\n")

    for r in rows:
        cid = r["call_id"]
        tid = r["task_id"]
        raw = r["response_text"]
        parsed = json.loads(raw)

        raw_ev = parsed.get("evidence_status")
        raw_obj = parsed.get("answer", {}).get("object")
        raw_parents = parsed.get("parent_memory_ids")

        print(f"Call ID:         {cid}")
        print(f"Task ID:         {tid}")
        print(f"Raw Output:      {raw.strip()}")
        print(f"Parsed Status:   {raw_ev}")
        print(f"Parsed Object:   {raw_obj}")
        print(f"Parsed Parents:  {raw_parents}")
        print(f"Raw Consistency: {(raw_ev in ('insufficient', 'conflicting') and raw_obj == 'UNKNOWN') or (raw_ev == 'sufficient' and raw_obj != 'UNKNOWN')}")
        print("-" * 85)

    conn.close()

if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "gene_d1_preflight_20260819_181409.db"
    audit_cell2_db(db)
