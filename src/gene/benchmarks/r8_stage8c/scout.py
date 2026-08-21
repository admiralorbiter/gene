"""Stage 8C Exploratory Scout: Open-World Identity Formation & Autonomous Ontology Induction.

Exploratory, dev-only scout evaluating LLM capacity to classify entity mentions without pre-registered alias maps:
1. Novel Entity -> CREATE_PROVISIONAL
2. New Alias for Known Entity -> LINK_TO_EXISTING
3. Near-Collision Distinct Entities -> KEEP_DISTINCT
4. Insufficient Evidence / Ambiguous Mention -> DEFER
"""

import json
import os
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

DecisionType = Literal["LINK_TO_EXISTING", "CREATE_PROVISIONAL", "KEEP_DISTINCT", "DEFER"]


@dataclass
class ScoutCase:
    case_id: str
    category: str  # "novel_entity", "new_alias", "near_collision", "ambiguous"
    mention_span: str
    context_sentence: str
    existing_registry: list[dict[str, Any]]
    ground_truth_decision: DecisionType
    ground_truth_target: str | None


def generate_scout_cases() -> list[ScoutCase]:
    cases: list[ScoutCase] = []

    # Category 1: Genuinely Novel Entity (5 cases) -> CREATE_PROVISIONAL
    novel_specs = [
        ("scout_novel_01", "Aurora Node 1", "Aurora Node 1 initiated telemetry stream on channel 0.", "aurora_node_1"),
        ("scout_novel_02", "Borealis Gateway Alpha", "Borealis Gateway Alpha routed telemetry packets.", "borealis_gateway_alpha"),
        ("scout_novel_03", "Stellar Transceiver 9", "Stellar Transceiver 9 calibrated sensor optics.", "stellar_transceiver_9"),
        ("scout_novel_04", "Helios Ingress Unit", "Helios Ingress Unit registered valid diagnostic link.", "helios_ingress_unit"),
        ("scout_novel_05", "Nova Storage Fabric 3", "Nova Storage Fabric 3 synchronized snapshot storage.", "nova_storage_fabric_3"),
    ]
    for cid, span, ctx, target in novel_specs:
        cases.append(
            ScoutCase(
                case_id=cid,
                category="novel_entity",
                mention_span=span,
                context_sentence=ctx,
                existing_registry=[
                    {"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]},
                    {"canonical_id": "processing_array_2", "name": "Processing Array 2", "known_aliases": ["PA-2"]},
                ],
                ground_truth_decision="CREATE_PROVISIONAL",
                ground_truth_target=target,
            )
        )

    # Category 2: New Alias for Known Entity (5 cases) -> LINK_TO_EXISTING
    alias_specs = [
        ("scout_alias_01", "CC-1 Prime", "CC-1 Prime reported degraded power supply rail.", "compute_cluster_1"),
        ("scout_alias_02", "Compute-01 Unit", "Telemetry from Compute-01 Unit shows temperature spike.", "compute_cluster_1"),
        ("scout_alias_03", "Array PA-2 Main", "Array PA-2 Main experienced clock drift at epoch 12.", "processing_array_2"),
        ("scout_alias_04", "Cluster One Subsystem", "Cluster One Subsystem engaged auxiliary power unit.", "compute_cluster_1"),
        ("scout_alias_05", "Proc-Array-2 Secondary", "Proc-Array-2 Secondary synchronized frame buffer.", "processing_array_2"),
    ]
    for cid, span, ctx, target in alias_specs:
        cases.append(
            ScoutCase(
                case_id=cid,
                category="new_alias",
                mention_span=span,
                context_sentence=ctx,
                existing_registry=[
                    {"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1", "Cluster Unit 1"]},
                    {"canonical_id": "processing_array_2", "name": "Processing Array 2", "known_aliases": ["PA-2", "Array 2"]},
                ],
                ground_truth_decision="LINK_TO_EXISTING",
                ground_truth_target=target,
            )
        )

    # Category 3: Near-Collision Distinct Entities (5 cases) -> KEEP_DISTINCT
    collision_specs = [
        ("scout_collision_01", "Compute Cluster 10", "Compute Cluster 10 initialized cold boot sequence.", "compute_cluster_10"),
        ("scout_collision_02", "Compute Cluster 1-B", "Compute Cluster 1-B is a separate standby partition.", "compute_cluster_1_b"),
        ("scout_collision_03", "PA-20", "PA-20 telemetry stream opened on distinct bus.", "pa_20"),
        ("scout_collision_04", "Compute Cluster 11", "Compute Cluster 11 operational status verified.", "compute_cluster_11"),
        ("scout_collision_05", "Processing Array 22", "Processing Array 22 reported distinct cache invalidation.", "processing_array_22"),
    ]
    for cid, span, ctx, target in collision_specs:
        cases.append(
            ScoutCase(
                case_id=cid,
                category="near_collision",
                mention_span=span,
                context_sentence=ctx,
                existing_registry=[
                    {"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]},
                    {"canonical_id": "processing_array_2", "name": "Processing Array 2", "known_aliases": ["PA-2"]},
                ],
                ground_truth_decision="KEEP_DISTINCT",
                ground_truth_target=target,
            )
        )

    # Category 4: Insufficient Evidence / Ambiguous Mention (5 cases) -> DEFER
    ambig_specs = [
        ("scout_ambig_01", "The Cluster", "The Cluster reported intermittent sensor noise.", None),
        ("scout_ambig_02", "Array", "Array buffer overflow encountered at t=5.", None),
        ("scout_ambig_03", "Node", "Node status degraded during routine sweep.", None),
        ("scout_ambig_04", "Target Unit", "Target Unit switched to secondary backup link.", None),
        ("scout_ambig_05", "System", "System telemetry packet received without header identifier.", None),
    ]
    for cid, span, ctx, target in ambig_specs:
        cases.append(
            ScoutCase(
                case_id=cid,
                category="ambiguous",
                mention_span=span,
                context_sentence=ctx,
                existing_registry=[
                    {"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]},
                    {"canonical_id": "processing_array_2", "name": "Processing Array 2", "known_aliases": ["PA-2"]},
                ],
                ground_truth_decision="DEFER",
                ground_truth_target=None,
            )
        )

    return cases


def invoke_llm_scout(model: str, case: ScoutCase) -> dict[str, Any]:
    registry_str = json.dumps(case.existing_registry, indent=2)
    prompt = f"""You are an Autonomous Epistemic Ontology Reasoner.
You are given a mention of an entity in a technical text document, along with the current Known Canonical Entity Registry.

Existing Registry:
{registry_str}

Entity Mention: "{case.mention_span}"
Context Sentence: "{case.context_sentence}"

Your task is to determine the epistemic identity classification for this mention.
Choose exactly ONE decision from:
1. "LINK_TO_EXISTING": If the mention clearly refers to an already registered entity (e.g. an unlisted operational alias or minor variation of a known unit). Specify "target_canonical_id".
2. "CREATE_PROVISIONAL": If the mention is a specific, unambiguous new entity that is definitely not in the registry. Propose a new snake_case "provisional_id".
3. "KEEP_DISTINCT": If the mention looks similar to an existing entity name (e.g. "Cluster 10" vs "Cluster 1") but clearly refers to a separate, distinct hardware entity. Propose a new snake_case "provisional_id".
4. "DEFER": If the mention is vague, ambiguous, or lacks sufficient context to identify a specific entity (e.g. "The Cluster", "System", "Node").

Respond ONLY with a valid JSON object formatted exactly as:
{{
  "decision": "LINK_TO_EXISTING" | "CREATE_PROVISIONAL" | "KEEP_DISTINCT" | "DEFER",
  "target_canonical_id": "canonical_id_here" | null,
  "confidence": 0.0 to 1.0,
  "rationale": "one short sentence"
}}
"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0},
    }

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - t0
            raw_text = data.get("response", "{}")
            parsed = json.loads(raw_text)
            return {
                "success": True,
                "elapsed": elapsed,
                "parsed": parsed,
                "raw": raw_text,
            }
    except Exception as e:
        return {
            "success": False,
            "elapsed": time.time() - t0,
            "error": str(e),
        }


def main() -> None:
    print("================================================================================")
    print("GENE STAGE 8C EXPLORATORY SCOUT: Autonomous Open-World Ontology Induction")
    print("Model: gemma3:12b | 20 Dev Cases (4 Categories x 5 Cases) | Dev-Only Exploratory")
    print("================================================================================\n")

    cases = generate_scout_cases()
    results = []
    correct_by_cat = {"novel_entity": 0, "new_alias": 0, "near_collision": 0, "ambiguous": 0}
    total_by_cat = {"novel_entity": 0, "new_alias": 0, "near_collision": 0, "ambiguous": 0}

    for idx, c in enumerate(cases, 1):
        print(f"[{idx:02d}/20] Testing {c.case_id} ({c.category}): '{c.mention_span}'...", end=" ", flush=True)
        res = invoke_llm_scout("gemma3:12b", c)
        if not res.get("success"):
            print(f"FAILED (error: {res.get('error')})")
            continue

        parsed = res["parsed"]
        pred_decision = parsed.get("decision")
        pred_target = parsed.get("target_canonical_id")
        confidence = parsed.get("confidence", 0.0)
        rationale = parsed.get("rationale", "")

        is_decision_correct = pred_decision == c.ground_truth_decision
        total_by_cat[c.category] += 1
        if is_decision_correct:
            correct_by_cat[c.category] += 1
            print(f"CORRECT -> {pred_decision} (conf={confidence:.2f})")
        else:
            print(f"MISMATCH -> Pred: {pred_decision}, Expected: {c.ground_truth_decision} (rationale: {rationale})")

        results.append(
            {
                "case_id": c.case_id,
                "category": c.category,
                "mention_span": c.mention_span,
                "ground_truth_decision": c.ground_truth_decision,
                "predicted_decision": pred_decision,
                "predicted_target": pred_target,
                "confidence": confidence,
                "rationale": rationale,
                "correct": is_decision_correct,
                "elapsed_seconds": res["elapsed"],
            }
        )

    print("\n================================================================================")
    print("STAGE 8C SCOUT SUMMARY BY CATEGORY:")
    for cat in ["novel_entity", "new_alias", "near_collision", "ambiguous"]:
        acc = (correct_by_cat[cat] / total_by_cat[cat] * 100.0) if total_by_cat[cat] > 0 else 0.0
        print(f"  - {cat:16s}: {correct_by_cat[cat]}/{total_by_cat[cat]} ({acc:.1f}%)")

    total_correct = sum(correct_by_cat.values())
    total_cases = sum(total_by_cat.values())
    overall_acc = total_correct / total_cases * 100.0 if total_cases > 0 else 0.0
    print(f"\nOverall Scout Accuracy: {total_correct}/{total_cases} ({overall_acc:.1f}%)")
    print("================================================================================")

    out_file = Path("data/r8_stage8c_scout_summary.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    summary_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ"),
        "model": "gemma3:12b",
        "total_cases": total_cases,
        "total_correct": total_correct,
        "overall_accuracy": overall_acc,
        "breakdown_by_category": {
            cat: {"correct": correct_by_cat[cat], "total": total_by_cat[cat]} for cat in total_by_cat
        },
        "cases": results,
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"Scout telemetry saved to {out_file}")


if __name__ == "__main__":
    main()
