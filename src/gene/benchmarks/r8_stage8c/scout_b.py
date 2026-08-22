"""Stage 8C Exploratory Scout-B: Hard-Negative Disambiguation & Two-Stage Registry Mutation.

Evaluates 40 dev cases across hard-negative failure modes:
1. Suffix partitions (Cluster 1-A / 1-B / 1-C vs Cluster 1) -> NOVEL / CREATE_PROVISIONAL + MUST_NOT_LINK
2. Numeric adjacency (Cluster 10 / 11 / 101 vs Cluster 1) -> NOVEL / CREATE_PROVISIONAL + MUST_NOT_LINK
3. Bare generic head nouns (Array, Node, System, Unit) -> AMBIGUOUS / DEFER
4. Two-document sequential evolution (Doc 1 -> Doc 2 resolution) -> Dynamic Registry Linking
"""

import json
import os
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass
class ScoutBCase:
    case_id: str
    category: str  # "suffix_collision", "numeric_collision", "bare_generic", "sequential_evolution"
    doc_index: int
    mention_span: str
    context_sentence: str
    existing_registry: list[dict[str, Any]]
    expected_identity: Literal["EXISTING", "NOVEL", "AMBIGUOUS"]
    expected_mutation: Literal["LINK", "CREATE_PROVISIONAL", "DEFER"]
    expected_target: str | None
    expected_must_not_link: list[str]


def generate_scout_b_cases() -> list[ScoutBCase]:
    cases: list[ScoutBCase] = []

    # Category 1: Partition Suffix Near-Collisions (10 cases)
    # E.g. "Cluster 1-A" is a distinct standalone partition from "Cluster 1", NOT an alias.
    suffixes = ["1-A", "1-B", "1-C", "2-Alpha", "2-Beta", "1-Sub", "2-Part", "1-Aux", "2-Ext", "1-Sec"]
    for idx, suf in enumerate(suffixes, 1):
        base_id = "compute_cluster_1" if "1" in suf else "processing_array_2"
        base_name = "Compute Cluster 1" if "1" in suf else "Processing Array 2"
        mention = f"{base_name} Partition {suf}"
        ctx = f"Telemetry packet from {mention} indicates isolated local memory bus."
        cases.append(
            ScoutBCase(
                case_id=f"scout_b_suffix_{idx:02d}",
                category="suffix_collision",
                doc_index=1,
                mention_span=mention,
                context_sentence=ctx,
                existing_registry=[
                    {"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]},
                    {"canonical_id": "processing_array_2", "name": "Processing Array 2", "known_aliases": ["PA-2"]},
                ],
                expected_identity="NOVEL",
                expected_mutation="CREATE_PROVISIONAL",
                expected_target=f"partition_{suf.lower().replace('-', '_')}",
                expected_must_not_link=[base_id],
            )
        )

    # Category 2: Numeric Adjacency Near-Collisions (10 cases)
    # E.g. "Compute Cluster 10" is distinct from "Compute Cluster 1".
    numerics = ["10", "11", "101", "12", "102", "20", "22", "202", "21", "201"]
    for idx, num in enumerate(numerics, 1):
        is_cluster = int(num) < 20 or int(num) > 100 and "1" in num[0:2]
        base_id = "compute_cluster_1" if is_cluster else "processing_array_2"
        unit_type = "Compute Cluster" if is_cluster else "Processing Array"
        mention = f"{unit_type} {num}"
        ctx = f"System diagnostic test passed on {mention} at timestamp 14.0."
        cases.append(
            ScoutBCase(
                case_id=f"scout_b_numeric_{idx:02d}",
                category="numeric_collision",
                doc_index=1,
                mention_span=mention,
                context_sentence=ctx,
                existing_registry=[
                    {"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]},
                    {"canonical_id": "processing_array_2", "name": "Processing Array 2", "known_aliases": ["PA-2"]},
                ],
                expected_identity="NOVEL",
                expected_mutation="CREATE_PROVISIONAL",
                expected_target=f"{unit_type.lower().replace(' ', '_')}_{num}",
                expected_must_not_link=[base_id],
            )
        )

    # Category 3: Bare Generic Head Nouns (10 cases)
    # E.g. "The Array", "Node", "System" without identifier -> AMBIGUOUS / DEFER
    generics = [
        ("scout_b_generic_01", "The Array", "The Array encountered transient bus contention."),
        ("scout_b_generic_02", "The Node", "The Node initiated telemetry transmission."),
        ("scout_b_generic_03", "System", "System state transitioned to degraded mode."),
        ("scout_b_generic_04", "Hardware Unit", "Hardware Unit status check completed."),
        ("scout_b_generic_05", "Target Cluster", "Target Cluster received command sequence."),
        ("scout_b_generic_06", "The Device", "The Device reported temperature variance."),
        ("scout_b_generic_07", "Module", "Module synchronization fault detected."),
        ("scout_b_generic_08", "Processor", "Processor frequency scaled back."),
        ("scout_b_generic_09", "The Subsystem", "The Subsystem power level normalized."),
        ("scout_b_generic_10", "Computing Element", "Computing Element clock drift within tolerance."),
    ]
    for cid, span, ctx in generics:
        cases.append(
            ScoutBCase(
                case_id=cid,
                category="bare_generic",
                doc_index=1,
                mention_span=span,
                context_sentence=ctx,
                existing_registry=[
                    {"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]},
                    {"canonical_id": "processing_array_2", "name": "Processing Array 2", "known_aliases": ["PA-2"]},
                ],
                expected_identity="AMBIGUOUS",
                expected_mutation="DEFER",
                expected_target=None,
                expected_must_not_link=[],
            )
        )

    # Category 4: Two-Document Sequential Evolution (10 cases = 5 pairs)
    # Pair 1: Doc 1 Defer -> Doc 2 Clarify
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_01_d1",
            category="sequential_evolution",
            doc_index=1,
            mention_span="Cluster 1 Backup",
            context_sentence="Cluster 1 Backup reported standby status.",
            existing_registry=[{"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]}],
            expected_identity="AMBIGUOUS",
            expected_mutation="DEFER",
            expected_target=None,
            expected_must_not_link=["compute_cluster_1"],
        )
    )
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_01_d2",
            category="sequential_evolution",
            doc_index=2,
            mention_span="Cluster 1 Backup (CC-1 Standby Partition)",
            context_sentence="Cluster 1 Backup (CC-1 Standby Partition) confirmed as operational alias for Compute Cluster 1.",
            existing_registry=[{"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]}],
            expected_identity="EXISTING",
            expected_mutation="LINK",
            expected_target="compute_cluster_1",
            expected_must_not_link=[],
        )
    )

    # Pair 2: Novel Creation in Doc 1 -> Subsequent Alias Link in Doc 2
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_02_d1",
            category="sequential_evolution",
            doc_index=1,
            mention_span="Aurora Processing Core 7",
            context_sentence="Aurora Processing Core 7 initialized diagnostic sweep.",
            existing_registry=[{"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1"}],
            expected_identity="NOVEL",
            expected_mutation="CREATE_PROVISIONAL",
            expected_target="aurora_processing_core_7",
            expected_must_not_link=["compute_cluster_1"],
        )
    )
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_02_d2",
            category="sequential_evolution",
            doc_index=2,
            mention_span="APC-7 Prime",
            context_sentence="APC-7 Prime is the primary execution thread on Aurora Processing Core 7.",
            existing_registry=[
                {"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1"},
                {"canonical_id": "provisional_aurora_core_7", "name": "Aurora Processing Core 7", "status": "PROVISIONAL"},
            ],
            expected_identity="EXISTING",
            expected_mutation="LINK",
            expected_target="provisional_aurora_core_7",
            expected_must_not_link=["compute_cluster_1"],
        )
    )

    # Pair 3: Distinct Suffix in Doc 1 -> Second Mention in Doc 2
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_03_d1",
            category="sequential_evolution",
            doc_index=1,
            mention_span="Processing Array 2-South",
            context_sentence="Processing Array 2-South is a geographically distinct facility from Processing Array 2.",
            existing_registry=[{"canonical_id": "processing_array_2", "name": "Processing Array 2"}],
            expected_identity="NOVEL",
            expected_mutation="CREATE_PROVISIONAL",
            expected_target="processing_array_2_south",
            expected_must_not_link=["processing_array_2"],
        )
    )
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_03_d2",
            category="sequential_evolution",
            doc_index=2,
            mention_span="PA-2-South Facility",
            context_sentence="PA-2-South Facility synchronized telemetry link.",
            existing_registry=[
                {"canonical_id": "processing_array_2", "name": "Processing Array 2"},
                {"canonical_id": "provisional_pa_2_south", "name": "Processing Array 2-South", "status": "PROVISIONAL"},
            ],
            expected_identity="EXISTING",
            expected_mutation="LINK",
            expected_target="provisional_pa_2_south",
            expected_must_not_link=["processing_array_2"],
        )
    )

    # Pair 4: Defer Ambiguous in Doc 1 -> Defer Again in Doc 2 (Permanent Ambiguity)
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_04_d1",
            category="sequential_evolution",
            doc_index=1,
            mention_span="Auxiliary Node",
            context_sentence="Auxiliary Node reported low voltage.",
            existing_registry=[{"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1"}],
            expected_identity="AMBIGUOUS",
            expected_mutation="DEFER",
            expected_target=None,
            expected_must_not_link=[],
        )
    )
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_04_d2",
            category="sequential_evolution",
            doc_index=2,
            mention_span="Auxiliary Node",
            context_sentence="Auxiliary Node still unlinked in telemetry stream.",
            existing_registry=[{"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1"}],
            expected_identity="AMBIGUOUS",
            expected_mutation="DEFER",
            expected_target=None,
            expected_must_not_link=[],
        )
    )

    # Pair 5: Direct Multi-Doc Alias Resolution
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_05_d1",
            category="sequential_evolution",
            doc_index=1,
            mention_span="Compute Cluster Unit One",
            context_sentence="Compute Cluster Unit One operational.",
            existing_registry=[{"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1"]}],
            expected_identity="EXISTING",
            expected_mutation="LINK",
            expected_target="compute_cluster_1",
            expected_must_not_link=[],
        )
    )
    cases.append(
        ScoutBCase(
            case_id="scout_b_seq_05_d2",
            category="sequential_evolution",
            doc_index=2,
            mention_span="Cluster Unit 1-Main",
            context_sentence="Cluster Unit 1-Main active telemetry stream.",
            existing_registry=[{"canonical_id": "compute_cluster_1", "name": "Compute Cluster 1", "known_aliases": ["CC-1", "Compute Cluster Unit One"]}],
            expected_identity="EXISTING",
            expected_mutation="LINK",
            expected_target="compute_cluster_1",
            expected_must_not_link=[],
        )
    )

    return cases


def invoke_llm_scout_b(model: str, case: ScoutBCase) -> dict[str, Any]:
    registry_str = json.dumps(case.existing_registry, indent=2)
    prompt = f"""You are an Autonomous Epistemic Ontology Reasoner.
You are given an entity mention in technical text, and the Current Entity Registry.

Registry:
{registry_str}

Entity Mention: "{case.mention_span}"
Context: "{case.context_sentence}"

Your task is to provide:
1. "identity_judgment":
   - "EXISTING": If the mention refers to an already registered entity or known alias.
   - "NOVEL": If the mention is an unambiguous, specific NEW hardware entity (including separate partitions like "Cluster 1-A" vs "Cluster 1", or separate numbered units like "Cluster 10" vs "Cluster 1").
   - "AMBIGUOUS": If the mention is generic, bare, or lacks sufficient identifier context (e.g. "The Array", "Node", "System").

2. "registry_mutation":
   - "LINK": Connect to an existing canonical or provisional entity. Provide "target_id".
   - "CREATE_PROVISIONAL": Create a new provisional entity. Propose snake_case "target_id".
   - "DEFER": Do not mutate registry; defer until clarifying evidence arrives.

3. "must_not_link":
   - List any existing registry IDs that this mention MUST NOT be merged with (e.g. for "Cluster 1-A", must_not_link: ["compute_cluster_1"]).

Respond ONLY with a JSON object:
{{
  "identity_judgment": "EXISTING" | "NOVEL" | "AMBIGUOUS",
  "registry_mutation": "LINK" | "CREATE_PROVISIONAL" | "DEFER",
  "target_id": "target_id_here" | null,
  "must_not_link": ["id1", "id2"],
  "confidence": 0.0 to 1.0,
  "rationale": "one sentence explanation"
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
    print("GENE STAGE 8C EXPLORATORY SCOUT-B: Hard-Negative Disambiguation & Evolution")
    print("Model: gemma3:12b | 40 Dev Cases (4 Categories x 10 Cases) | Dev-Only")
    print("================================================================================\n")

    cases = generate_scout_b_cases()
    results = []
    correct_by_cat = {"suffix_collision": 0, "numeric_collision": 0, "bare_generic": 0, "sequential_evolution": 0}
    total_by_cat = {"suffix_collision": 0, "numeric_collision": 0, "bare_generic": 0, "sequential_evolution": 0}

    for idx, c in enumerate(cases, 1):
        print(f"[{idx:02d}/40] Testing {c.case_id} ({c.category}): '{c.mention_span}'...", end=" ", flush=True)
        res = invoke_llm_scout_b("gemma3:12b", c)
        if not res.get("success"):
            print(f"FAILED (error: {res.get('error')})")
            continue

        parsed = res["parsed"]
        pred_identity = parsed.get("identity_judgment")
        pred_mutation = parsed.get("registry_mutation")
        pred_target = parsed.get("target_id")
        pred_must_not_link = parsed.get("must_not_link", [])
        confidence = parsed.get("confidence", 0.0)
        rationale = parsed.get("rationale", "")

        is_identity_correct = pred_identity == c.expected_identity
        is_mutation_correct = pred_mutation == c.expected_mutation

        # Check negative constraints in collision cases
        constraint_satisfied = True
        if c.expected_must_not_link:
            for forbidden in c.expected_must_not_link:
                if pred_target == forbidden or pred_mutation == "LINK":
                    constraint_satisfied = False

        case_passed = is_identity_correct and is_mutation_correct and constraint_satisfied
        total_by_cat[c.category] += 1
        if case_passed:
            correct_by_cat[c.category] += 1
            print(f"PASS -> {pred_identity}/{pred_mutation} (conf={confidence:.2f})")
        else:
            print(f"FAIL -> Pred: {pred_identity}/{pred_mutation} (target: {pred_target}), Expected: {c.expected_identity}/{c.expected_mutation}")

        results.append(
            {
                "case_id": c.case_id,
                "category": c.category,
                "mention_span": c.mention_span,
                "expected_identity": c.expected_identity,
                "expected_mutation": c.expected_mutation,
                "predicted_identity": pred_identity,
                "predicted_mutation": pred_mutation,
                "predicted_target": pred_target,
                "must_not_link": pred_must_not_link,
                "confidence": confidence,
                "rationale": rationale,
                "passed": case_passed,
                "elapsed_seconds": res["elapsed"],
            }
        )

    print("\n================================================================================")
    print("STAGE 8C SCOUT-B SUMMARY BY CATEGORY:")
    for cat in ["suffix_collision", "numeric_collision", "bare_generic", "sequential_evolution"]:
        acc = (correct_by_cat[cat] / total_by_cat[cat] * 100.0) if total_by_cat[cat] > 0 else 0.0
        print(f"  - {cat:22s}: {correct_by_cat[cat]}/{total_by_cat[cat]} ({acc:.1f}%)")

    total_correct = sum(correct_by_cat.values())
    total_cases = sum(total_by_cat.values())
    overall_acc = total_correct / total_cases * 100.0 if total_cases > 0 else 0.0
    print(f"\nOverall Scout-B Accuracy: {total_correct}/{total_cases} ({overall_acc:.1f}%)")
    print("================================================================================")

    out_file = Path("data/r8_stage8c_scout_b_summary.json")
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
    print(f"Scout-B telemetry saved to {out_file}")


if __name__ == "__main__":
    main()
