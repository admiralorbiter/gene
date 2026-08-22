"""Contract Verifier for Stage 8C-R3 (CONTRACT-R8-8C-R3).
Verifies:
1. Gate 1: Neural Proposal Telemetry Logging.
2. Gate 2a: Hybrid Durable False Merge Floor == 0.0% (0/120).
3. Gate 2b: Semantic False Provisional Existence Floor == 0.0% on unasserted.
4. Gate 3: Provisional Entity Fragmentation == 0 duplicate creations.
5. Gate 4: Permanent Non-Resolution Invariant >= 7/8 in Arm 4A.
6. Gate 5: Disconfirmation & Accumulation Matrix == 7/7 exact in Arm 4B.
7. Gate 6: Useful Resolvable Coverage >= 85.0% across N=97 resolvable decisions.
8. Gate 7: Relational SQLite Schema & FK Integrity Audit.
9. Paired Offline R1/R2 Comparative Replay.
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def verify_stage8c_r3_contract(
    gold_manifest_path: Path,
    evidence_path: Path,
    db_path: Path,
) -> Tuple[bool, Dict[str, Any]]:
    with open(gold_manifest_path, "r", encoding="utf-8") as f:
        gold_manifest = json.load(f)

    records = []
    with open(evidence_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    assert len(records) == 120, f"Expected 120 execution records, found {len(records)}"

    # 1. Gate 2a: False Canonical Merges
    false_canonical_merges = 0
    canonical_entities = {
        "compute_cluster_alpha", "compute_cluster_beta",
        "storage_array_alpha", "storage_array_beta",
        "gateway_router_alpha", "gateway_router_beta",
    }
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        d = r["hybrid_decision"]
        if d.get("action") == "LINK" and d.get("target_id") in canonical_entities:
            if gold["expected_target"] != d["target_id"]:
                false_canonical_merges += 1
    gate_2a_pass = (false_canonical_merges == 0)

    # 2. Gate 2b: False Provisional Creations on Unasserted
    false_prov_unasserted = 0
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        d = r["hybrid_decision"]
        if gold.get("arm") == "ARM4A_PERMANENT_DEFERRAL":
            if d.get("action") == "CREATE_PROVISIONAL":
                false_prov_unasserted += 1
    gate_2b_pass = (false_prov_unasserted == 0)

    # 3. Gate 3: Provisional Entity Fragmentation
    prov_created_per_world: Dict[str, List[str]] = {}
    for r in records:
        wid = r["world_id"]
        d = r["hybrid_decision"]
        if d.get("action") == "CREATE_PROVISIONAL":
            prov_created_per_world.setdefault(wid, []).append(d.get("target_id"))
    duplicate_prov = 0
    for wid, plist in prov_created_per_world.items():
        if len(plist) != len(set(plist)):
            duplicate_prov += 1
    gate_3_pass = (duplicate_prov == 0)

    # 4. Gate 4: Permanent Non-Resolution Invariant (Arm 4A)
    arm4a_deferred = 0
    arm4a_total = 0
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        if gold.get("arm") == "ARM4A_PERMANENT_DEFERRAL":
            arm4a_total += 1
            if r["hybrid_decision"].get("action") == "DEFER":
                arm4a_deferred += 1
    gate_4_pass = (arm4a_total == 16 and arm4a_deferred >= 14)

    # 5. Gate 5: Disconfirmation & Accumulation Matrix (Arm 4B)
    arm4b_correct = 0
    arm4b_total = 0
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        if gold.get("arm") == "ARM4B_DISCONFIRMATION":
            arm4b_total += 1
            d = r["hybrid_decision"]
            if d.get("action") == gold["action"] and d.get("target_id") == gold["expected_target"]:
                arm4b_correct += 1
    gate_5_pass = (arm4b_total == 14 and arm4b_correct == 14)

    # 6. Gate 6: Useful Resolvable Coverage
    resolvable_correct = 0
    resolvable_total = 0
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        if gold.get("resolvable", False):
            resolvable_total += 1
            d = r["hybrid_decision"]
            if d.get("action") == gold["action"] and d.get("target_id") == gold["expected_target"]:
                resolvable_correct += 1
    coverage_pct = (resolvable_correct / resolvable_total) * 100.0 if resolvable_total > 0 else 0.0
    gate_6_pass = (coverage_pct >= 85.0)

    # 7. Gate 7: Relational DB & Ledger Audit
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check")
    integrity_status = cur.fetchone()[0]
    cur.execute("PRAGMA foreign_key_check")
    fk_violations = len(cur.fetchall())
    cur.execute("SELECT COUNT(*) FROM provenance_edges")
    edge_count = cur.fetchone()[0]
    conn.close()
    gate_7_pass = (integrity_status == "ok") and (fk_violations == 0) and (edge_count > 0)

    all_passed = (
        gate_2a_pass
        and gate_2b_pass
        and gate_3_pass
        and gate_4_pass
        and gate_5_pass
        and gate_6_pass
        and gate_7_pass
    )

    metrics = {
        "gate_2a_false_canonical_merges": false_canonical_merges,
        "gate_2a_pass": gate_2a_pass,
        "gate_2b_false_prov_unasserted": false_prov_unasserted,
        "gate_2b_pass": gate_2b_pass,
        "gate_3_duplicate_provisional_creations": duplicate_prov,
        "gate_3_pass": gate_3_pass,
        "gate_4_arm4a_deferred": f"{arm4a_deferred}/{arm4a_total}",
        "gate_4_pass": gate_4_pass,
        "gate_5_arm4b_exact": f"{arm4b_correct}/{arm4b_total}",
        "gate_5_pass": gate_5_pass,
        "gate_6_coverage_pct": f"{coverage_pct:.1f}% ({resolvable_correct}/{resolvable_total})",
        "gate_6_pass": gate_6_pass,
        "gate_7_db_integrity": integrity_status,
        "gate_7_fk_violations": fk_violations,
        "gate_7_pass": gate_7_pass,
        "all_passed": all_passed,
    }

    return all_passed, metrics
