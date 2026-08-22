"""Contract Verifier for Stage 8C-R3-R1 (CONTRACT-R8-8C-R3-R1).
Verifies:
1. Gate 1: Neural Proposal Telemetry Logging across all N=120 decisions.
2. Gate 2a: Hybrid Durable False Merge Floor == 0.0% (0/120).
3. Gate 2b: Semantic False Provisional Existence Floor == 0.0% on unasserted mentions.
4. Gate 3: Provisional Entity Fragmentation == 0 duplicate creations.
5. Gate 4: Permanent Non-Resolution Invariant >= 7/8 (87.5%) worlds in Arm 4A (both docs defer).
6. Gate 5: Evidence Accumulation Lifecycle State Machine (Verifies exact status matching live candidate proposals across all 7 Arm 4B worlds).
7. Gate 5b: Deterministic CPU Branch-Coverage Unit Test (Proves all 4 terminal states RETARGETED, CONFIRMED, RESOLVED_EXISTING, RESOLVED_NOVEL execute soundly).
8. Gate 6: Useful Resolvable Coverage >= 85.0% across N=97 resolvable decisions.
9. Gate 7: Full Relational SQLite Schema & Hypothesis Ledger Reconciliation (Strict 8 UNRESOLVED + 7 Resolved == 15 Total).
10. Dual Paired Replays:
    - Historical Frozen R2 Replay (Total improvement over R2)
    - Matched Precedence Ablation Replay (Isolated causal effect of discriminating sub-IDs)
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from gene.benchmarks.r8_stage8c_r2.runner import (
    EpistemicIngressSession as EpistemicIngressSessionR2,
)
from gene.benchmarks.r8_stage8c_r3_r1.runner import (
    EpistemicIngressSessionR3Ablation,
    EpistemicIngressSessionR3R1,
    normalize_alias,
)
from gene.benchmarks.r8_stage8c_r3_r1.worlds import (
    get_stage8c_r3_r1_base_registry,
    verify_r3r1_freshness_against_r3,
)


def verify_cpu_branch_coverage_state_machine() -> bool:
    """Deterministic CPU-only branch-coverage test proving the hypothesis state machine

    executes all 4 terminal transitions and UNRESOLVED accumulation with 100% soundness.
    """
    base_reg = get_stage8c_r3_r1_base_registry()

    # Case 1: RETARGETED (Doc 1 candidate = cluster_alpha, Doc 2 resolves to router_beta)
    s1 = EpistemicIngressSessionR3R1(base_reg, world_id="test_retargeted")
    s1.process_mention("d1", "s1", "Unverified Node", "Context 1", {"target_entity_id": "compute_cluster_alpha"})
    s1.process_mention("d2", "s2", "Router-Beta", "Context 2", {})
    h1 = s1.hypothesis_ledger.get("test_retargeted")
    c1_ok = (h1 and h1["status"] == "RETARGETED" and h1["resolved_target"] == "gateway_router_beta")

    # Case 2: CONFIRMED (Doc 1 candidate = cluster_beta, Doc 2 resolves to cluster_beta)
    s2 = EpistemicIngressSessionR3R1(base_reg, world_id="test_confirmed")
    s2.process_mention("d1", "s1", "Unverified Node", "Context 1", {"target_entity_id": "compute_cluster_beta"})
    s2.process_mention("d2", "s2", "Cluster-Beta", "Context 2", {})
    h2 = s2.hypothesis_ledger.get("test_confirmed")
    c2_ok = (h2 and h2["status"] == "CONFIRMED" and h2["resolved_target"] == "compute_cluster_beta")

    # Case 3: RESOLVED_EXISTING (Doc 1 candidate = null, Doc 2 resolves to router_alpha)
    s3 = EpistemicIngressSessionR3R1(base_reg, world_id="test_resolved_existing")
    s3.process_mention("d1", "s1", "Ambiguous Component", "Context 1", {"target_entity_id": None})
    s3.process_mention("d2", "s2", "Router-Alpha", "Context 2", {})
    h3 = s3.hypothesis_ledger.get("test_resolved_existing")
    c3_ok = (h3 and h3["status"] == "RESOLVED_EXISTING" and h3["resolved_target"] == "gateway_router_alpha")

    # Case 4: RESOLVED_NOVEL (Doc 1 candidate = null, Doc 2 creates novel provisional)
    s4 = EpistemicIngressSessionR3R1(base_reg, world_id="test_resolved_novel")
    s4.process_mention("d1", "s1", "Uncommissioned Mesh", "Context 1", {"target_entity_id": None})
    s4.process_mention("d2", "s2", "Mesh Zeta", "Official deployment notice: Mesh Zeta is active in production.", {})
    h4 = s4.hypothesis_ledger.get("test_resolved_novel")
    c4_ok = (h4 and h4["status"] == "RESOLVED_NOVEL" and h4["resolved_target"] == "prov_mesh_zeta")

    # Case 5: UNRESOLVED (Doc 1 defers, Doc 2 defers -> accumulates 2 evidence items)
    s5 = EpistemicIngressSessionR3R1(base_reg, world_id="test_unresolved")
    s5.process_mention("d1", "s1", "Ambiguous Item 1", "Context 1", {})
    s5.process_mention("d2", "s2", "Ambiguous Item 2", "Context 2", {})
    h5 = s5.hypothesis_ledger.get("test_unresolved")
    c5_ok = (h5 and h5["status"] == "UNRESOLVED" and len(h5["evidence_history"]) == 2)

    return bool(c1_ok and c2_ok and c3_ok and c4_ok and c5_ok)


def run_paired_comparator_replay(
    records: List[Dict[str, Any]],
    gold_manifest: Dict[str, Any],
    session_cls: Any,
) -> Dict[str, Any]:
    """Runs a comparator resolver (Frozen R2 or Matched Ablation) against the identical documents and proposals."""
    base_reg = get_stage8c_r3_r1_base_registry()
    records_by_world: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        records_by_world.setdefault(r["world_id"], []).append(r)

    resolvable_correct = 0
    total_resolvable = sum(1 for g in gold_manifest.values() if g.get("resolvable", False))
    n11 = 0
    n10 = 0
    n01 = 0
    n00 = 0

    for wid, world_records in sorted(records_by_world.items()):
        comp_session = session_cls(base_reg)
        for r in world_records:
            doc_id = r["doc_id"]
            gold = gold_manifest[doc_id]
            mention = r["mention"]
            context = r["context"]
            source_id = r["source_id"]
            proposal = r.get("neural_proposal", {})

            comp_decision = comp_session.process_mention(
                doc_id=doc_id,
                source_id=source_id,
                mention=mention,
                context=context,
                neural_proposal=proposal,
            )

            if gold.get("resolvable", False):
                comp_ok = (comp_decision.get("action") == gold["action"] and comp_decision.get("target_id") == gold["expected_target"])
                r3_d = r["hybrid_decision"]
                r3_ok = (r3_d.get("action") == gold["action"] and r3_d.get("target_id") == gold["expected_target"])

                if comp_ok:
                    resolvable_correct += 1
                if comp_ok and r3_ok:
                    n11 += 1
                elif comp_ok and not r3_ok:
                    n10 += 1
                elif not comp_ok and r3_ok:
                    n01 += 1
                else:
                    n00 += 1

    coverage_pct = (resolvable_correct / total_resolvable) * 100.0 if total_resolvable > 0 else 0.0
    return {
        "resolvable_correct": resolvable_correct,
        "total_resolvable": total_resolvable,
        "coverage_pct": coverage_pct,
        "n11": n11,
        "n10": n10,
        "n01": n01,
        "n00": n00,
    }


def verify_stage8c_r3_r1_contract(
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

    # 3. Gate 2b: False Provisional Creations on Unasserted (Arm 4A Sentinel)
    false_prov_unasserted = 0
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        d = r["hybrid_decision"]
        if gold.get("arm") == "ARM4A_PERMANENT_DEFERRAL":
            if d.get("action") == "CREATE_PROVISIONAL":
                false_prov_unasserted += 1
    gate_2b_pass = (false_prov_unasserted == 0)

    # 3b. Gate 2c: Global False Provisional Invariant (Claim Ceiling across all 120 decisions)
    global_false_prov = 0
    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        d = r["hybrid_decision"]
        if d.get("action") == "CREATE_PROVISIONAL":
            if gold.get("action") != "CREATE_PROVISIONAL":
                global_false_prov += 1
    gate_2c_pass = (global_false_prov == 0)

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

    # Connect to SQLite DB for Gate 5 and Gate 7 verification
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # 6. Gate 5: Evidence Accumulation Lifecycle State Machine (Conditioned on live candidate proposal)
    cur.execute(
        """SELECT world_id, candidate_target, status, resolved_target, resolving_doc_id, evidence_history_json
           FROM hypothesis_ledger WHERE world_id LIKE '%arm4b%'"""
    )
    arm4b_rows = cur.fetchall()
    arm4b_lifecycles_passed = 0

    for wid, cand, status, res_target, res_doc, ev_json in arm4b_rows:
        doc2_id = f"{wid}_doc_2"
        gold2 = gold_manifest[doc2_id]
        expected_target = gold2["expected_target"]
        expected_action = gold2["action"]

        # Validate conditional lifecycle state
        if expected_action == "CREATE_PROVISIONAL":
            status_valid = (status == "RESOLVED_NOVEL")
        elif expected_action == "LINK":
            if cand is not None and cand != expected_target:
                status_valid = (status == "RETARGETED")
            elif cand is not None and cand == expected_target:
                status_valid = (status == "CONFIRMED")
            else:
                status_valid = (status == "RESOLVED_EXISTING")
        else:
            status_valid = False

        target_valid = (res_target == expected_target)
        doc_valid = (res_doc == doc2_id)
        ev_history = json.loads(ev_json) if ev_json else []
        history_valid = (len(ev_history) == 2)

        if status_valid and target_valid and doc_valid and history_valid:
            arm4b_lifecycles_passed += 1

    gate_5_pass = (len(arm4b_rows) == 7 and arm4b_lifecycles_passed == 7)

    # Gate 5b: Deterministic CPU Branch-Coverage Test
    gate_5b_pass = verify_cpu_branch_coverage_state_machine()

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
    cur.execute("PRAGMA integrity_check")
    integrity_status = cur.fetchone()[0]
    cur.execute("PRAGMA foreign_key_check")
    fk_violations = len(cur.fetchall())
    cur.execute("SELECT COUNT(*) FROM entities")
    entity_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM provenance_edges")
    edge_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM execution_records")
    rec_count = cur.fetchone()[0]

    cur.execute("SELECT hypothesis_id, evidence_history_json FROM hypothesis_ledger WHERE world_id LIKE '%arm4a%' AND status == 'UNRESOLVED' AND resolved_target IS NULL AND resolving_doc_id IS NULL")
    arm4a_rows = cur.fetchall()
    arm4a_unresolved_count = len(arm4a_rows)
    arm4a_evidence_valid = all(len(json.loads(r[1])) == 2 for r in arm4a_rows)

    cur.execute("SELECT hypothesis_id, evidence_history_json FROM hypothesis_ledger WHERE world_id LIKE '%arm4b%' AND status != 'UNRESOLVED' AND resolved_target IS NOT NULL AND resolving_doc_id IS NOT NULL")
    arm4b_resolved_rows = cur.fetchall()
    arm4b_resolved_count = len(arm4b_resolved_rows)
    arm4b_evidence_valid = all(len(json.loads(r[1])) == 2 for r in arm4b_resolved_rows)

    cur.execute("SELECT COUNT(*) FROM hypothesis_ledger")
    total_hypo_count = cur.fetchone()[0]

    conn.close()

    gate_7_pass = (
        (integrity_status == "ok")
        and (fk_violations == 0)
        and (entity_count >= 6)
        and (edge_count > 0)
        and (arm4a_unresolved_count == 8)
        and arm4a_evidence_valid
        and (arm4b_resolved_count == 7)
        and arm4b_evidence_valid
        and (total_hypo_count == 15)
        and (rec_count == 120)
    )

    # 9. Dual Paired Replays
    r2_replay = run_paired_comparator_replay(records, gold_manifest, EpistemicIngressSessionR2)
    ablation_replay = run_paired_comparator_replay(records, gold_manifest, EpistemicIngressSessionR3Ablation)

    # 10. Dual Freshness Audit vs Frozen Stage 8C-R3 (Mention-Level and Pair-Level)
    is_fresh, m_ov_cnt, p_ov_cnt, m_ov, p_ov = verify_r3r1_freshness_against_r3()

    all_passed = (
        gate_1_pass
        and gate_2a_pass
        and gate_2b_pass
        and gate_2c_pass
        and gate_3_pass
        and gate_4_pass
        and gate_5_pass
        and gate_5b_pass
        and gate_6_pass
        and gate_7_pass
        and is_fresh
    )

    metrics = {
        "gate_1_telemetry_logged": gate_1_pass,
        "gate_2a_false_canonical_merges": false_canonical_merges,
        "gate_2a_pass": gate_2a_pass,
        "gate_2b_false_prov_unasserted": false_prov_unasserted,
        "gate_2b_pass": gate_2b_pass,
        "gate_2c_global_false_prov": global_false_prov,
        "gate_2c_pass": gate_2c_pass,
        "gate_3_duplicate_provisional_creations": duplicate_prov,
        "gate_3_pass": gate_3_pass,
        "gate_4_arm4a_fully_deferred_worlds": f"{arm4a_fully_deferred_worlds}/{len(arm4a_worlds)}",
        "gate_4_pass": gate_4_pass,
        "gate_5_arm4b_lifecycles_sound": f"{arm4b_lifecycles_passed}/7",
        "gate_5_pass": gate_5_pass,
        "gate_5b_cpu_branch_coverage_pass": gate_5b_pass,
        "gate_6_coverage_pct": f"{coverage_pct:.1f}% ({resolvable_correct}/{resolvable_total})",
        "gate_6_pass": gate_6_pass,
        "gate_7_db_integrity": integrity_status,
        "gate_7_fk_violations": fk_violations,
        "gate_7_entity_count": entity_count,
        "gate_7_edge_count": edge_count,
        "gate_7_arm4a_unresolved": f"{arm4a_unresolved_count}/8",
        "gate_7_arm4b_resolved": f"{arm4b_resolved_count}/7",
        "gate_7_total_hypotheses": f"{total_hypo_count}/15",
        "gate_7_record_count": f"{rec_count}/120",
        "gate_7_pass": gate_7_pass,
        "freshness_audit_pass": is_fresh,
        "freshness_mention_overlap_count": m_ov_cnt,
        "freshness_pair_overlap_count": p_ov_cnt,

        "historical_r2_replay": {
            "coverage_pct": f"{r2_replay['coverage_pct']:.1f}% ({r2_replay['resolvable_correct']}/{r2_replay['total_resolvable']})",
            "total_gain_over_r2": f"+{coverage_pct - r2_replay['coverage_pct']:.1f}%",
            "n11": r2_replay["n11"],
            "n01_recovered": r2_replay["n01"],
            "n10_regressions": r2_replay["n10"],
            "n00": r2_replay["n00"],
        },
        "matched_precedence_ablation": {
            "coverage_pct": f"{ablation_replay['coverage_pct']:.1f}% ({ablation_replay['resolvable_correct']}/{ablation_replay['total_resolvable']})",
            "isolated_precedence_gain": f"+{coverage_pct - ablation_replay['coverage_pct']:.1f}%",
            "n11": ablation_replay["n11"],
            "n01_recovered": ablation_replay["n01"],
            "n10_regressions": ablation_replay["n10"],
            "n00": ablation_replay["n00"],
        },
        "all_passed": all_passed,
    }

    return all_passed, metrics

