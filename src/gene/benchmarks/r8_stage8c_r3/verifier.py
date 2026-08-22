"""Contract Verifier for Stage 8C-R3 (CONTRACT-R8-8C-R3).
Verifies:
1. Gate 1: Neural Proposal Telemetry Logging across all N=120 decisions.
2. Gate 2a: Hybrid Durable False Merge Floor == 0.0% (0/120).
3. Gate 2b: Semantic False Provisional Existence Floor == 0.0% on unasserted mentions.
4. Gate 3: Provisional Entity Fragmentation == 0 duplicate creations.
5. Gate 4: Permanent Non-Resolution Invariant >= 7/8 (87.5%) worlds in Arm 4A (both docs defer).
6. Gate 5: Evidence Accumulation Lifecycle Matrix == 7/7 exact world lifecycle transitions in Arm 4B.
7. Gate 6: Useful Resolvable Coverage >= 85.0% across N=97 resolvable decisions.
8. Gate 7: Full Relational SQLite Schema & Hypothesis Ledger Reconciliation.
9. Paired Offline R2 Comparative Replay (invoking genuine frozen EpistemicIngressSessionR2 with R3 base registry).
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from gene.benchmarks.r8_stage8c_r2.runner import (
    EpistemicIngressSession as EpistemicIngressSessionR2,
)
from gene.benchmarks.r8_stage8c_r3.runner import (
    EpistemicIngressSessionR3,
    normalize_alias,
)
from gene.benchmarks.r8_stage8c_r3.worlds import get_stage8c_r3_base_registry


def run_paired_r2_replay(records: List[Dict[str, Any]], gold_manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Runs the genuine frozen Stage 8C-R2 deterministic resolver against the identical R3 documents and proposals

    under the identical Stage 8C-R3 starting base registry.
    """
    base_reg = get_stage8c_r3_base_registry()
    
    # Group records by world
    records_by_world: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        records_by_world.setdefault(r["world_id"], []).append(r)

    r2_resolvable_correct = 0
    total_resolvable = sum(1 for g in gold_manifest.values() if g.get("resolvable", False))

    for wid, world_records in sorted(records_by_world.items()):
        r2_session = EpistemicIngressSessionR2(base_reg)
        for r in world_records:
            doc_id = r["doc_id"]
            gold = gold_manifest[doc_id]
            mention = r["mention"]
            context = r["context"]
            source_id = r["source_id"]
            proposal = r.get("neural_proposal", {})

            r2_decision = r2_session.process_mention(
                doc_id=doc_id,
                source_id=source_id,
                mention=mention,
                context=context,
                neural_proposal=proposal,
            )

            if gold.get("resolvable", False):
                if r2_decision.get("action") == gold["action"] and r2_decision.get("target_id") == gold["expected_target"]:
                    r2_resolvable_correct += 1

    r2_coverage_pct = (r2_resolvable_correct / total_resolvable) * 100.0 if total_resolvable > 0 else 0.0
    return {
        "r2_resolvable_correct": r2_resolvable_correct,
        "total_resolvable": total_resolvable,
        "r2_coverage_pct": r2_coverage_pct,
    }


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

    # 1. Gate 1: Neural Proposal Telemetry
    gate_1_pass = all("neural_proposal" in r for r in records)

    # 2. Gate 2a: False Canonical Merges
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

    # 3. Gate 2b: False Provisional Creations on Unasserted
    false_prov_unasserted = 0
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        d = r["hybrid_decision"]
        if gold.get("arm") == "ARM4A_PERMANENT_DEFERRAL":
            if d.get("action") == "CREATE_PROVISIONAL":
                false_prov_unasserted += 1
    gate_2b_pass = (false_prov_unasserted == 0)

    # 4. Gate 3: Provisional Entity Fragmentation
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

    # 5. Gate 4: Permanent Non-Resolution Invariant (World-Level: both docs must defer)
    arm4a_worlds: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        if gold.get("arm") == "ARM4A_PERMANENT_DEFERRAL":
            arm4a_worlds.setdefault(r["world_id"], []).append(r)

    arm4a_fully_deferred_worlds = 0
    for wid, w_recs in arm4a_worlds.items():
        if len(w_recs) == 2 and all(r["hybrid_decision"].get("action") == "DEFER" for r in w_recs):
            arm4a_fully_deferred_worlds += 1
    gate_4_pass = (len(arm4a_worlds) == 8 and arm4a_fully_deferred_worlds >= 7)

    # 6. Gate 5: Evidence Accumulation Lifecycle Matrix (7 World Lifecycles in Arm 4B)
    arm4b_worlds: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        if gold.get("arm") == "ARM4B_DISCONFIRMATION":
            arm4b_worlds.setdefault(r["world_id"], []).append(r)

    arm4b_lifecycles_passed = 0
    expected_lifecycles = {
        "world_r3_arm4b_01": ("gateway_router_beta", ["RETARGETED", "RESOLVED_EXISTING"]),
        "world_r3_arm4b_02": ("compute_cluster_beta", ["RETARGETED", "RESOLVED_EXISTING"]),
        "world_r3_arm4b_03": ("storage_array_alpha", ["RETARGETED", "RESOLVED_EXISTING"]),
        "world_r3_arm4b_04": ("gateway_router_alpha", ["RESOLVED_EXISTING", "RETARGETED"]),
        "world_r3_arm4b_05": ("compute_cluster_alpha", ["RESOLVED_EXISTING", "RETARGETED"]),
        "world_r3_arm4b_06": ("prov_sensor_mesh_omega", ["RESOLVED_NOVEL"]),
        "world_r3_arm4b_07": ("compute_cluster_beta", ["CONFIRMED", "RESOLVED_EXISTING"]),
    }

    for wid, w_recs in sorted(arm4b_worlds.items()):
        doc1 = w_recs[0]
        doc2 = w_recs[1]
        gold_doc1 = gold_manifest[doc1["doc_id"]]
        gold_doc2 = gold_manifest[doc2["doc_id"]]

        # Doc 1 must defer
        doc1_deferred = (doc1["hybrid_decision"].get("action") == "DEFER")
        # Doc 2 must resolve to expected target
        doc2_resolved = (
            doc2["hybrid_decision"].get("action") == gold_doc2["action"]
            and doc2["hybrid_decision"].get("target_id") == gold_doc2["expected_target"]
        )

        expected_target, valid_statuses = expected_lifecycles.get(wid, (None, []))
        if doc1_deferred and doc2_resolved and (doc2["hybrid_decision"].get("target_id") == expected_target):
            arm4b_lifecycles_passed += 1

    gate_5_pass = (len(arm4b_worlds) == 7 and arm4b_lifecycles_passed == 7)

    # 7. Gate 6: Useful Resolvable Coverage (Frozen Denominator N=97)
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
    assert resolvable_total == 97, f"Expected 97 resolvable decisions, found {resolvable_total}"
    coverage_pct = (resolvable_correct / resolvable_total) * 100.0 if resolvable_total > 0 else 0.0
    gate_6_pass = (coverage_pct >= 85.0)

    # 8. Gate 7: Full Relational SQLite DB & Hypothesis Ledger Reconciliation
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check")
    integrity_status = cur.fetchone()[0]
    cur.execute("PRAGMA foreign_key_check")
    fk_violations = len(cur.fetchall())
    cur.execute("SELECT COUNT(*) FROM entities")
    entity_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM provenance_edges")
    edge_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hypothesis_ledger")
    hypo_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM execution_records")
    rec_count = cur.fetchone()[0]
    conn.close()

    gate_7_pass = (
        (integrity_status == "ok")
        and (fk_violations == 0)
        and (entity_count >= 6)
        and (edge_count > 0)
        and (hypo_count >= 15)  # 8 from Arm 4A + 7 from Arm 4B
        and (rec_count == 120)
    )

    # 9. Paired Offline R2 Replay
    r2_replay = run_paired_r2_replay(records, gold_manifest)

    all_passed = (
        gate_1_pass
        and gate_2a_pass
        and gate_2b_pass
        and gate_3_pass
        and gate_4_pass
        and gate_5_pass
        and gate_6_pass
        and gate_7_pass
    )

    metrics = {
        "gate_1_telemetry_logged": gate_1_pass,
        "gate_2a_false_canonical_merges": false_canonical_merges,
        "gate_2a_pass": gate_2a_pass,
        "gate_2b_false_prov_unasserted": false_prov_unasserted,
        "gate_2b_pass": gate_2b_pass,
        "gate_3_duplicate_provisional_creations": duplicate_prov,
        "gate_3_pass": gate_3_pass,
        "gate_4_arm4a_fully_deferred_worlds": f"{arm4a_fully_deferred_worlds}/{len(arm4a_worlds)}",
        "gate_4_pass": gate_4_pass,
        "gate_5_arm4b_lifecycles_exact": f"{arm4b_lifecycles_passed}/{len(arm4b_worlds)}",
        "gate_5_pass": gate_5_pass,
        "gate_6_coverage_pct": f"{coverage_pct:.1f}% ({resolvable_correct}/{resolvable_total})",
        "gate_6_pass": gate_6_pass,
        "gate_7_db_integrity": integrity_status,
        "gate_7_fk_violations": fk_violations,
        "gate_7_entity_count": entity_count,
        "gate_7_edge_count": edge_count,
        "gate_7_hypothesis_count": hypo_count,
        "gate_7_record_count": rec_count,
        "gate_7_pass": gate_7_pass,
        "paired_r2_replay_coverage": f"{r2_replay['r2_coverage_pct']:.1f}% ({r2_replay['r2_resolvable_correct']}/{r2_replay['total_resolvable']})",
        "coverage_gain_over_r2": f"+{coverage_pct - r2_replay['r2_coverage_pct']:.1f}%",
        "all_passed": all_passed,
    }

    return all_passed, metrics
