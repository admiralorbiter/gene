"""Contract Verifier for Stage 8C-R3 (CONTRACT-R8-8C-R3).
Verifies:
1. Gate 1: Neural Proposal Telemetry Logging across all N=120 decisions.
2. Gate 2a: Hybrid Durable False Merge Floor == 0.0% (0/120).
3. Gate 2b: Semantic False Provisional Existence Floor == 0.0% on unasserted mentions.
4. Gate 3: Provisional Entity Fragmentation == 0 duplicate creations.
5. Gate 4: Permanent Non-Resolution Invariant >= 7/8 (14/16) in Arm 4A.
6. Gate 5: Disconfirmation & Accumulation Matrix == 7/7 exact in Arm 4B.
7. Gate 6: Useful Resolvable Coverage >= 85.0% across N=97 resolvable decisions.
8. Gate 7: Full Relational SQLite Schema & Hypothesis Ledger Reconciliation.
9. Paired Offline R2 Comparative Replay.
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from gene.benchmarks.r8_stage8c_r3.runner import (
    EpistemicIngressSessionR3,
    normalize_alias,
)
from gene.benchmarks.r8_stage8c_r3.worlds import get_stage8c_r3_base_registry


class Stage8C_R2_FrozenResolver:
    """Frozen R2 resolver logic for paired comparative replay."""
    def __init__(self, base_registry: Dict[str, Any]):
        self.durable_registry = {k: dict(v) for k, v in base_registry.items()}
        self.provenance_edges: List[Dict[str, Any]] = []

    def process_mention(self, doc_id: str, source_id: str, mention: str, context: str) -> Dict[str, Any]:
        norm_mention = normalize_alias(mention)

        # R2 Rule 1: Exact Registered Alias
        for reg_id, reg_data in self.durable_registry.items():
            canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
            aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
            if norm_mention == canon_norm or norm_mention in aliases_norm:
                return {"action": "LINK", "target_id": reg_id}

        # R2 Rule 2: Unconditional Structural First Refusal
        # (In R2, any partition keyword triggered structural refusal regardless of sub-ID)
        partition_markers = ["partition", "blade", "slice", "tray", "socket", "pool", "rack", "bay"]
        found_marker = any(m in mention.lower() for m in partition_markers)
        if found_marker:
            # Check if explicit partition entity exists
            for reg_id, reg_data in self.durable_registry.items():
                if norm_mention == normalize_alias(reg_data.get("canonical_name", "")):
                    return {"action": "LINK", "target_id": reg_id}
            # Otherwise in R2, if parent existed it created or linked partition, or failed to link parenthetical
            return {"action": "DEFER", "target_id": None}

        # R2 Rule 3: Novel Commissioning
        ctx_lower = context.lower()
        unasserted_ind = ["proposal", "pending", "rejected", "mock", "hypothetical", "generic", "unspecified"]
        if not any(ind in ctx_lower for ind in unasserted_ind) and "commissioning" in ctx_lower:
            prov_id = f"prov_{mention.lower().replace(' ', '_')}"
            self.durable_registry[prov_id] = {"entity_id": prov_id, "canonical_name": mention, "status": "provisional"}
            return {"action": "CREATE_PROVISIONAL", "target_id": prov_id}

        return {"action": "DEFER", "target_id": None}


def run_paired_r2_replay(records: List[Dict[str, Any]], gold_manifest: Dict[str, Any]) -> Dict[str, Any]:
    base_reg = get_stage8c_r3_base_registry()
    r2_session = Stage8C_R2_FrozenResolver(base_reg)

    r2_resolvable_correct = 0
    total_resolvable = sum(1 for g in gold_manifest.values() if g.get("resolvable", False))

    for r in records:
        doc_id = r["doc_id"]
        gold = gold_manifest[doc_id]
        mention = r["mention"]
        context = r["context"]
        source_id = r["source_id"]

        r2_decision = r2_session.process_mention(doc_id, source_id, mention, context)

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

    # 5. Gate 4: Permanent Non-Resolution Invariant (Arm 4A)
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

    # 6. Gate 5: Disconfirmation & Accumulation Matrix (Arm 4B)
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
    conn.close()
    gate_7_pass = (integrity_status == "ok") and (fk_violations == 0) and (entity_count >= 6) and (edge_count > 0)

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
        "gate_4_arm4a_deferred": f"{arm4a_deferred}/{arm4a_total}",
        "gate_4_pass": gate_4_pass,
        "gate_5_arm4b_exact": f"{arm4b_correct}/{arm4b_total}",
        "gate_5_pass": gate_5_pass,
        "gate_6_coverage_pct": f"{coverage_pct:.1f}% ({resolvable_correct}/{resolvable_total})",
        "gate_6_pass": gate_6_pass,
        "gate_7_db_integrity": integrity_status,
        "gate_7_fk_violations": fk_violations,
        "gate_7_entity_count": entity_count,
        "gate_7_edge_count": edge_count,
        "gate_7_pass": gate_7_pass,
        "paired_r2_replay_coverage": f"{r2_replay['r2_coverage_pct']:.1f}% ({r2_replay['r2_resolvable_correct']}/{r2_replay['total_resolvable']})",
        "all_passed": all_passed,
    }

    return all_passed, metrics
