"""Deterministic Acceptance Verifier for CONTRACT-R8-8C-R1.
Independently verifies raw JSONL telemetry, SQLite archive, and evidence manifest against all 7 preregistered gates.
"""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List


def verify_stage8c_r1_contract():
    print("================================================================================")
    print("DETERMINISTIC CONTRACT ACCEPTANCE VERIFIER: CONTRACT-R8-8C-R1")
    print("================================================================================")

    data_dir = Path("data")
    jsonl_path = data_dir / "r8_stage8c_r1_candidate_evidence.jsonl"
    summary_path = data_dir / "r8_stage8c_r1_summary.json"
    sqlite_path = data_dir / "r8_stage8c_r1_registry.sqlite"
    manifest_path = data_dir / "r8_stage8c_r1_evidence_manifest.json"

    for p in [jsonl_path, summary_path, sqlite_path, manifest_path]:
        if not p.exists():
            print(f"FAIL: Required evidence artifact missing: {p}")
            sys.exit(1)

    # 1. Verify Manifest Integrity
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    jsonl_hash = hashlib.sha256(open(jsonl_path, "rb").read()).hexdigest()
    summary_hash = hashlib.sha256(open(summary_path, "rb").read()).hexdigest()
    sqlite_hash = hashlib.sha256(open(sqlite_path, "rb").read()).hexdigest()

    assert manifest["jsonl_sha256"] == jsonl_hash, "JSONL content-hash mismatch!"
    assert manifest["summary_sha256"] == summary_hash, "Summary content-hash mismatch!"
    assert manifest["sqlite_sha256"] == sqlite_hash, "SQLite content-hash mismatch!"
    print("Evidence Manifest Content-Addressed Integrity:     VERIFIED")

    # Load raw records
    records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line.strip()))

    assert len(records) == 120, f"Expected 120 calls, found {len(records)}"

    # -------------------------------------------------------------------------
    # Gate 1: Diagnostic Neural Proposal Quality (Report-Only Telemetry)
    # -------------------------------------------------------------------------
    neural_correct = sum(1 for r in records if r["is_neural_correct"])
    neural_acc = neural_correct / len(records)
    print(f"Gate 1 (Diagnostic Neural Proposal Quality):       {neural_correct}/120 ({neural_acc*100:.1f}%) -> TELEMETRY REPORTED")

    # -------------------------------------------------------------------------
    # Gate 2: Hybrid Durable False Merge Floor (FDAR_merge == 0.0%)
    # -------------------------------------------------------------------------
    false_merges = 0
    for r in records:
        gold = r["gold"]
        ingress = r["ingress_result"]
        expected_act = gold.get("action")
        expected_target = gold.get("expected_target")
        must_not_link = gold.get("must_not_link", [])

        # Check if an action linked into an incorrect canonical entity
        if ingress["action"] == "LINK" and ingress.get("target_id"):
            tgt = ingress["target_id"]
            if expected_act == "DEFER":
                false_merges += 1
            elif expected_act == "CREATE_PROVISIONAL":
                false_merges += 1
            elif tgt in must_not_link:
                false_merges += 1
            elif expected_target and tgt != expected_target and not tgt.startswith("prov_"):
                false_merges += 1

    gate2_passed = false_merges == 0
    print(f"Gate 2 (Hybrid Durable False Merge Floor == 0.0%):   {false_merges}/120 false merges -> {'PASS' if gate2_passed else 'FAIL'}")

    # -------------------------------------------------------------------------
    # Gate 3: Provisional Entity Fragmentation (0 duplicates)
    # -------------------------------------------------------------------------
    conn = sqlite3.connect(str(sqlite_path))
    cur = conn.cursor()
    cur.execute("SELECT entity_id, canonical_name FROM entities WHERE status = 'PROVISIONAL'")
    prov_entities = cur.fetchall()
    prov_names = [p[1] for p in prov_entities]
    duplicate_count = len(prov_names) - len(set(prov_names))
    gate3_passed = duplicate_count == 0
    print(f"Gate 3 (Provisional Entity Fragmentation == 0):     {duplicate_count} duplicates across {len(prov_entities)} provisionals -> {'PASS' if gate3_passed else 'FAIL'}")

    # -------------------------------------------------------------------------
    # Gate 4: Permanent Non-Resolution Invariant (>= 7/8 worlds in Sub-Arm 4A)
    # -------------------------------------------------------------------------
    arm4a_records = [r for r in records if r["arm"] == "ARM4A_PERMANENT_DEFERRAL"]
    arm4a_worlds = {}
    for r in arm4a_records:
        wid = r["world_id"]
        if wid not in arm4a_worlds:
            arm4a_worlds[wid] = []
        arm4a_worlds[wid].append(r)

    arm4a_non_durable_pass = 0
    for wid, w_recs in arm4a_worlds.items():
        all_non_durable = all(not r["ingress_result"].get("durable", False) for r in w_recs)
        if all_non_durable:
            arm4a_non_durable_pass += 1

    gate4_passed = arm4a_non_durable_pass >= 7
    print(f"Gate 4 (Permanent Non-Resolution Invariant >= 7/8): {arm4a_non_durable_pass}/8 worlds ({arm4a_non_durable_pass/8*100:.1f}%) -> {'PASS' if gate4_passed else 'FAIL'}")

    # -------------------------------------------------------------------------
    # Gate 5: Evidence Accumulation & Disconfirmation (Sub-Arm 4B)
    # -------------------------------------------------------------------------
    arm4b_records = [r for r in records if r["arm"] == "ARM4B_DEFERRED_RESOLVED"]
    arm4b_worlds = {}
    for r in arm4b_records:
        wid = r["world_id"]
        if wid not in arm4b_worlds:
            arm4b_worlds[wid] = []
        arm4b_worlds[wid].append(r)

    doc1_premature_mutations = 0
    doc2_correct_resolutions = 0
    disconfirm_clean_count = 0
    total_disconfirm_worlds = 0

    for wid, w_recs in arm4b_worlds.items():
        doc1_rec = w_recs[0]
        doc2_rec = w_recs[1]
        mode = doc1_rec["gold"].get("mode", "")

        # Doc 1 must be non-durable
        if doc1_rec["ingress_result"].get("durable", False):
            doc1_premature_mutations += 1

        # Doc 2 resolution check
        if doc2_rec["is_hybrid_correct"]:
            doc2_correct_resolutions += 1

        # Disconfirmation check
        if "CONTRADICT" in mode:
            total_disconfirm_worlds += 1
            # Check hypothesis record in sqlite to ensure initial candidate has durable_target == None
            cur.execute("SELECT candidate_target, status, durable_target, retargeted_to FROM hypothesis_records WHERE hypothesis_id LIKE ?", (f"%{doc1_rec['doc_id']}%",))
            row = cur.fetchone()
            if row:
                status, dur_tgt, retarget = row[1], row[2], row[3]
                if status == "CONTRADICTED_DISCARDED" and dur_tgt is None and retarget is not None:
                    disconfirm_clean_count += 1

    gate5_resolutions_pass = doc2_correct_resolutions >= 6
    gate5_no_premature = doc1_premature_mutations == 0
    gate5_disconfirm_pass = disconfirm_clean_count == total_disconfirm_worlds and total_disconfirm_worlds == 3
    gate5_passed = gate5_resolutions_pass and gate5_no_premature and gate5_disconfirm_pass

    print(f"Gate 5 (Evidence Accumulation & Disconfirmation):")
    print(f"  - Final Document Resolutions (>= 6/7):            {doc2_correct_resolutions}/7 ({doc2_correct_resolutions/7*100:.1f}%)")
    print(f"  - Zero Premature Doc-1 Durable Mutations:         {doc1_premature_mutations} premature mutations")
    print(f"  - Clean Disconfirmation Retargeting (3/3):        {disconfirm_clean_count}/3 clean retargets (0 residue)")
    print(f"  - Gate 5 Overall Verdict:                         {'PASS' if gate5_passed else 'FAIL'}")

    # -------------------------------------------------------------------------
    # Gate 6: Useful Resolvable Coverage (>= 85.0% on N=97)
    # -------------------------------------------------------------------------
    # N=97 comprises: Arm 1 (30), Arm 2 (30), Arm 3 (30), Arm 4B Doc 2 (7) = 97 gold-resolvable durable decisions
    resolvable_records = [
        r for r in records
        if r["arm"] in ["ARM1_NOVEL", "ARM2_KNOWN_ALIAS", "ARM3_PARTITION"]
        or (r["arm"] == "ARM4B_DEFERRED_RESOLVED" and r["doc_id"].endswith("_2"))
    ]
    assert len(resolvable_records) == 97, f"Expected 97 resolvable records, found {len(resolvable_records)}"
    useful_admissions = sum(1 for r in resolvable_records if r["is_hybrid_correct"])
    useful_rate = useful_admissions / 97.0
    gate6_passed = useful_rate >= 0.85
    print(f"Gate 6 (Useful Resolvable Coverage >= 85.0%, N=97):  {useful_admissions}/97 ({useful_rate*100:.1f}%) -> {'PASS' if gate6_passed else 'FAIL'}")

    # -------------------------------------------------------------------------
    # Gate 7: Database & Hypothesis Integrity Checks
    # -------------------------------------------------------------------------
    cur.execute("PRAGMA integrity_check")
    pragma_res = cur.fetchone()[0]
    cur.execute("PRAGMA foreign_key_check")
    fk_res = cur.fetchall()
    conn.close()

    gate7_passed = (pragma_res == "ok") and (len(fk_res) == 0)
    print(f"Gate 7 (Database Schema & Provenance Graph Check):  PRAGMA: {pragma_res}, FK Violations: {len(fk_res)} -> {'PASS' if gate7_passed else 'FAIL'}")

    print("================================================================================")
    all_passed = gate2_passed and gate3_passed and gate4_passed and gate5_passed and gate6_passed and gate7_passed
    if all_passed:
        print("STAGE 8C-R1 ACCEPTANCE VERDICT: PASS (ALL 7 GATES SATISFIED)")
        print("================================================================================")
        sys.exit(0)
    else:
        print("STAGE 8C-R1 ACCEPTANCE VERDICT: FAIL")
        print("================================================================================")
        sys.exit(1)


if __name__ == "__main__":
    verify_stage8c_r1_contract()
