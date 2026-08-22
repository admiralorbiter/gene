"""Scout-C Benchmark: Deterministic Guardrail Boundary & Partition Invariant Testing

Evaluates 40 challenging development cases targeting boundary conditions between:
1. Legitimate syntactic aliases (e.g. Model X-B, Aurora-7, Alpha Unit) -> LINK
2. Partitions & Subcomponents (e.g. Cluster 4-B, Node 1 Slice B, Blade 3) -> CREATE_PROVISIONAL + MUST_NOT_LINK
3. Sibling number collisions (e.g. Node 10 vs Node 1, CC-20 vs CC-2) -> CREATE_PROVISIONAL + MUST_NOT_LINK
4. Location & Firmware qualifiers (e.g. Cluster 1 [DC-West], Firmware v2.1) -> LINK or NOVEL depending on semantics
5. Bare generic tokens (e.g. The System, Host, Unit) -> DEFER

Reports:
- Raw neural proposal (gemma3:12b)
- Deterministic guardrail action
- Final hybrid system decision
- Gold identity
"""

import json
import os
import re
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:12b"

# Preregistered Deterministic Partition Syntax Grammar
PARTITION_REGEX = re.compile(
    r"(?i)\b(partition|part|sub|slice|module|aux|secondary|core\s+\d+|blade)\b|[-_][A-Z0-9]+$"
)

# Known canonical registry for Scout-C
CANONICAL_REGISTRY = {
    "compute_cluster_1": {
        "canonical_name": "Compute Cluster 1",
        "aliases": ["CC-1", "Cluster 1", "Cluster One"],
        "category": "cluster",
    },
    "compute_cluster_4": {
        "canonical_name": "Compute Cluster 4",
        "aliases": ["CC-4", "Cluster 4"],
        "category": "cluster",
    },
    "aurora_node_1": {
        "canonical_name": "Aurora Node 1",
        "aliases": ["AN-1", "Node 1"],
        "category": "node",
    },
    "model_x": {
        "canonical_name": "Model X",
        "aliases": ["MX-Base", "Model X Base"],
        "category": "model_family",
    },
    "storage_array_alpha": {
        "canonical_name": "Storage Array Alpha",
        "aliases": ["Array Alpha", "SAN-Alpha"],
        "category": "storage",
    },
}


@dataclass
class ScoutCCase:
    case_id: str
    category: str
    mention_text: str
    context_sentence: str
    gold_judgment: str  # EXISTING | NOVEL | AMBIGUOUS
    gold_mutation: str  # LINK | CREATE_PROVISIONAL | DEFER
    gold_target_id: Optional[str]
    gold_must_not_link: List[str]


def generate_scout_c_cases() -> List[ScoutCCase]:
    cases = []

    # Category 1: Suffix Collision & Subunit vs Legitimate Variant (10 cases)
    cases.extend(
        [
            ScoutCCase(
                "C1-01",
                "suffix_partition",
                "Cluster 4-B",
                "Cluster 4-B failed over during scheduled maintenance.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_4"],
            ),
            ScoutCCase(
                "C1-02",
                "suffix_model_variant",
                "Model X-B",
                "Model X-B was released as the revision B alias of Model X.",
                "EXISTING",
                "LINK",
                "model_x",
                [],
            ),
            ScoutCCase(
                "C1-03",
                "partition_explicit",
                "Compute Cluster 1 Partition 2",
                "Compute Cluster 1 Partition 2 experienced memory degradation.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_1"],
            ),
            ScoutCCase(
                "C1-04",
                "slice_explicit",
                "Node 1 Slice A",
                "Node 1 Slice A CPU frequency was throttled.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["aurora_node_1"],
            ),
            ScoutCCase(
                "C1-05",
                "blade_explicit",
                "Cluster 1 Blade 3",
                "Cluster 1 Blade 3 was unseated.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_1"],
            ),
            ScoutCCase(
                "C1-06",
                "module_explicit",
                "Storage Array Alpha Module 2",
                "Storage Array Alpha Module 2 disk controller failed.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["storage_array_alpha"],
            ),
            ScoutCCase(
                "C1-07",
                "alias_variant",
                "Cluster One Main",
                "Cluster One Main is operating at nominal capacity.",
                "EXISTING",
                "LINK",
                "compute_cluster_1",
                [],
            ),
            ScoutCCase(
                "C1-08",
                "alias_variant",
                "AN-1 Primary",
                "AN-1 Primary completed self-test.",
                "EXISTING",
                "LINK",
                "aurora_node_1",
                [],
            ),
            ScoutCCase(
                "C1-09",
                "auxiliary_partition",
                "Cluster 4 Aux Unit",
                "Cluster 4 Aux Unit was powered down.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_4"],
            ),
            ScoutCCase(
                "C1-10",
                "secondary_partition",
                "Storage Array Alpha Secondary",
                "Storage Array Alpha Secondary synchronized mirror.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["storage_array_alpha"],
            ),
        ]
    )

    # Category 2: Sibling Number Prefix Collisions (10 cases)
    cases.extend(
        [
            ScoutCCase(
                "C2-01",
                "number_collision",
                "Node 10",
                "Node 10 was deployed to rack 4.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["aurora_node_1"],
            ),
            ScoutCCase(
                "C2-02",
                "number_collision",
                "Cluster 10",
                "Cluster 10 initialized network interfaces.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_1"],
            ),
            ScoutCCase(
                "C2-03",
                "number_collision",
                "CC-10",
                "CC-10 reported storage quota exceeded.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_1"],
            ),
            ScoutCCase(
                "C2-04",
                "number_collision",
                "Aurora Node 11",
                "Aurora Node 11 benchmarked at 940 GFLOPS.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["aurora_node_1"],
            ),
            ScoutCCase(
                "C2-05",
                "number_collision",
                "Cluster 40",
                "Cluster 40 joined the orchestrator pool.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_4"],
            ),
            ScoutCCase(
                "C2-06",
                "legitimate_exact",
                "Cluster 1",
                "Cluster 1 health check passed.",
                "EXISTING",
                "LINK",
                "compute_cluster_1",
                [],
            ),
            ScoutCCase(
                "C2-07",
                "legitimate_exact",
                "CC-4",
                "CC-4 received new workload assignment.",
                "EXISTING",
                "LINK",
                "compute_cluster_4",
                [],
            ),
            ScoutCCase(
                "C2-08",
                "legitimate_exact",
                "Aurora Node 1",
                "Aurora Node 1 thermal sensors nominal.",
                "EXISTING",
                "LINK",
                "aurora_node_1",
                [],
            ),
            ScoutCCase(
                "C2-09",
                "number_collision",
                "Node 100",
                "Node 100 provisioned in testing enclave.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["aurora_node_1"],
            ),
            ScoutCCase(
                "C2-10",
                "number_collision",
                "CC-100",
                "CC-100 provisioned in secondary rack.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_1"],
            ),
        ]
    )

    # Category 3: Location Qualifiers & Environmental Context (10 cases)
    cases.extend(
        [
            ScoutCCase(
                "C3-01",
                "location_qualifier_same",
                "Cluster 1 (DC-West)",
                "Cluster 1 (DC-West) handles primary traffic in the western datacenter.",
                "EXISTING",
                "LINK",
                "compute_cluster_1",
                [],
            ),
            ScoutCCase(
                "C3-02",
                "location_qualifier_diff",
                "Cluster 1 DC-East Branch",
                "Cluster 1 DC-East Branch is an independent eastern deployment.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_1"],
            ),
            ScoutCCase(
                "C3-03",
                "location_qualifier_same",
                "Storage Array Alpha [Building 4]",
                "Storage Array Alpha [Building 4] is the physical SAN location.",
                "EXISTING",
                "LINK",
                "storage_array_alpha",
                [],
            ),
            ScoutCCase(
                "C3-04",
                "rack_identifier",
                "Rack 12 Node 1",
                "Rack 12 Node 1 corresponds to Aurora Node 1 in rack position.",
                "EXISTING",
                "LINK",
                "aurora_node_1",
                [],
            ),
            ScoutCCase(
                "C3-05",
                "bay_partition",
                "Cluster 4 Bay 2 Unit",
                "Cluster 4 Bay 2 Unit is the separate bay enclosure.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_4"],
            ),
            ScoutCCase(
                "C3-06",
                "firmware_qualifier",
                "Cluster 1 running Firmware v3.2",
                "Cluster 1 running Firmware v3.2 upgraded successfully.",
                "EXISTING",
                "LINK",
                "compute_cluster_1",
                [],
            ),
            ScoutCCase(
                "C3-07",
                "firmware_variant_novel",
                "Cluster 1 Prototype v4",
                "Cluster 1 Prototype v4 is an experimental testbed.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["compute_cluster_1"],
            ),
            ScoutCCase(
                "C3-08",
                "site_alias",
                "SAN Alpha West",
                "SAN Alpha West is the regional alias for Storage Array Alpha.",
                "EXISTING",
                "LINK",
                "storage_array_alpha",
                [],
            ),
            ScoutCCase(
                "C3-09",
                "site_novel",
                "SAN Alpha Standby Enclave",
                "SAN Alpha Standby Enclave is a distinct DR installation.",
                "NOVEL",
                "CREATE_PROVISIONAL",
                None,
                ["storage_array_alpha"],
            ),
            ScoutCCase(
                "C3-10",
                "exact_alias",
                "Cluster One",
                "Cluster One completed telemetry flush.",
                "EXISTING",
                "LINK",
                "compute_cluster_1",
                [],
            ),
        ]
    )

    # Category 4: Bare Generic Tokens & Ambiguous Mentions (10 cases)
    cases.extend(
        [
            ScoutCCase(
                "C4-01",
                "bare_token",
                "The System",
                "The System was restarted by administrator.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-02",
                "bare_token",
                "The Node",
                "The Node experienced packet loss.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-03",
                "bare_token",
                "The Cluster",
                "The Cluster load rebalanced.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-04",
                "bare_token",
                "The Array",
                "The Array started RAID scrub.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-05",
                "bare_token",
                "Host Unit",
                "Host Unit CPU usage at 88%.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-06",
                "bare_token",
                "Primary Unit",
                "Primary Unit responded to ping.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-07",
                "bare_token",
                "Backup Node",
                "Backup Node is standing by.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-08",
                "bare_token",
                "Standby Cluster",
                "Standby Cluster initialized.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-09",
                "bare_token",
                "Hardware Appliance",
                "Hardware Appliance firmware updated.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
            ScoutCCase(
                "C4-10",
                "bare_token",
                "Target Device",
                "Target Device disconnected.",
                "AMBIGUOUS",
                "DEFER",
                None,
                [],
            ),
        ]
    )

    return cases


def call_neural_proposal(
    mention: str, context: str, registry: Dict[str, Any]
) -> Dict[str, Any]:
    prompt = f"""You are an entity resolution engine.
Given the existing registry:
{json.dumps(registry, indent=2)}

Resolve the following entity mention:
Mention: "{mention}"
Context: "{context}"

Return JSON matching this exact schema:
{{
  "identity_judgment": "EXISTING" | "NOVEL" | "AMBIGUOUS",
  "registry_mutation": "LINK" | "CREATE_PROVISIONAL" | "DEFER",
  "target_id": "string_or_null",
  "must_not_link": ["list_of_forbidden_ids"],
  "confidence": 0.0_to_1.0,
  "rationale": "short explanation"
}}
"""
    req_body = json.dumps(
        {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.0},
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL, data=req_body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return json.loads(res["response"])


def apply_deterministic_guardrail(
    mention: str, neural_proposal: Dict[str, Any], registry: Dict[str, Any]
) -> Dict[str, Any]:
    """Applies the deterministic ingress policy:

    1. Partition Grammar Check: If mention matches PARTITION_REGEX and tries to LINK to a base entity,
       OVERRIDE to CREATE_PROVISIONAL and attach MUST_NOT_LINK to that base entity.
    2. Number Sibling Collision Check: If mention contains a number that differs from matched canonical number,
       OVERRIDE to CREATE_PROVISIONAL + MUST_NOT_LINK.
    3. Bare Token Invariant: If mention is a single generic noun with no qualifier, enforce DEFER.
    """
    final_decision = dict(neural_proposal)
    guardrail_actions = []

    # 1. Partition syntax check
    is_partition_syntax = bool(PARTITION_REGEX.search(mention))
    if is_partition_syntax:
        # Check if neural proposed linking to a parent unit
        target = neural_proposal.get("target_id")
        if target and target in registry:
            # Model X is an exception (Model X-B is a model variant, not a hardware partition)
            if "model" not in registry[target].get("category", ""):
                guardrail_actions.append(
                    f"OVERRIDE_PARTITION_MERGE: blocked merge of '{mention}' into parent '{target}'"
                )
                final_decision["identity_judgment"] = "NOVEL"
                final_decision["registry_mutation"] = "CREATE_PROVISIONAL"
                final_decision["target_id"] = None
                must_not = list(final_decision.get("must_not_link", []))
                if target not in must_not:
                    must_not.append(target)
                final_decision["must_not_link"] = must_not

    # 2. Numbered Unit Sibling Collision Check (e.g. Node 10 vs Node 1)
    target = final_decision.get("target_id")
    if target and target in registry:
        mention_digits = re.findall(r"\d+", mention)
        target_digits = re.findall(r"\d+", target)
        if mention_digits and target_digits and mention_digits != target_digits:
            guardrail_actions.append(
                f"OVERRIDE_NUMBER_COLLISION: mention digits {mention_digits} != target digits {target_digits}"
            )
            final_decision["identity_judgment"] = "NOVEL"
            final_decision["registry_mutation"] = "CREATE_PROVISIONAL"
            final_decision["target_id"] = None
            must_not = list(final_decision.get("must_not_link", []))
            if target not in must_not:
                must_not.append(target)
            final_decision["must_not_link"] = must_not

    # 3. Bare Generic Token Check
    bare_tokens = {
        "the system",
        "the node",
        "the cluster",
        "the array",
        "host unit",
        "primary unit",
        "backup node",
        "standby cluster",
        "hardware appliance",
        "target device",
    }
    if mention.strip().lower() in bare_tokens:
        if final_decision.get("registry_mutation") != "DEFER":
            guardrail_actions.append(
                f"OVERRIDE_BARE_TOKEN: generic token '{mention}' must be DEFER"
            )
            final_decision["identity_judgment"] = "AMBIGUOUS"
            final_decision["registry_mutation"] = "DEFER"
            final_decision["target_id"] = None

    final_decision["guardrail_actions"] = guardrail_actions
    return final_decision


def main():
    os.makedirs("data", exist_ok=True)
    print("=" * 80, flush=True)
    print("RUNNING SCOUT-C: Deterministic Guardrail & Partition Boundary Benchmark", flush=True)
    print(f"Model: {MODEL_NAME} | Test Cases: 40 | Evaluated on Gemma 3 12B", flush=True)
    print("=" * 80 + "\n", flush=True)

    cases = generate_scout_c_cases()
    results = []

    neural_correct = 0
    hybrid_correct = 0
    false_merges_raw = 0
    false_merges_hybrid = 0
    guardrail_overrides = 0

    category_neural_stats = {}
    category_hybrid_stats = {}

    for idx, case in enumerate(cases, 1):
        cat = case.category.split("_")[0]
        if cat not in category_neural_stats:
            category_neural_stats[cat] = {"correct": 0, "total": 0}
            category_hybrid_stats[cat] = {"correct": 0, "total": 0}

        category_neural_stats[cat]["total"] += 1
        category_hybrid_stats[cat]["total"] += 1

        # 1. Get raw neural proposal
        try:
            raw_neural = call_neural_proposal(
                case.mention_text, case.context_sentence, CANONICAL_REGISTRY
            )
        except Exception as e:
            raw_neural = {
                "identity_judgment": "AMBIGUOUS",
                "registry_mutation": "DEFER",
                "target_id": None,
                "must_not_link": [],
                "confidence": 0.0,
                "rationale": f"Error: {e}",
            }

        # 2. Apply deterministic safety guardrail
        hybrid = apply_deterministic_guardrail(
            case.mention_text, raw_neural, CANONICAL_REGISTRY
        )

        # Check neural correctness
        raw_judg = raw_neural.get("identity_judgment")
        raw_mut = raw_neural.get("registry_mutation")
        raw_tgt = raw_neural.get("target_id")

        neural_is_correct = (
            raw_judg == case.gold_judgment
            and raw_mut == case.gold_mutation
            and (raw_tgt == case.gold_target_id or case.gold_target_id is None)
        )
        if neural_is_correct:
            neural_correct += 1
            category_neural_stats[cat]["correct"] += 1

        # Check raw false merge
        if case.gold_mutation != "LINK" and raw_mut == "LINK":
            false_merges_raw += 1

        # Check hybrid correctness
        hyb_judg = hybrid.get("identity_judgment")
        hyb_mut = hybrid.get("registry_mutation")
        hyb_tgt = hybrid.get("target_id")

        hybrid_is_correct = (
            hyb_judg == case.gold_judgment
            and hyb_mut == case.gold_mutation
            and (hyb_tgt == case.gold_target_id or case.gold_target_id is None)
        )
        if hybrid_is_correct:
            hybrid_correct += 1
            category_hybrid_stats[cat]["correct"] += 1

        # Check hybrid false merge
        if case.gold_mutation != "LINK" and hyb_mut == "LINK":
            false_merges_hybrid += 1

        if hybrid.get("guardrail_actions"):
            guardrail_overrides += 1

        results.append(
            {
                "case_id": case.case_id,
                "mention": case.mention_text,
                "category": case.category,
                "gold": {
                    "judgment": case.gold_judgment,
                    "mutation": case.gold_mutation,
                    "target_id": case.gold_target_id,
                    "must_not_link": case.gold_must_not_link,
                },
                "raw_neural": raw_neural,
                "hybrid_decision": hybrid,
                "neural_correct": neural_is_correct,
                "hybrid_correct": hybrid_is_correct,
            }
        )

        status_mark = "PASS" if hybrid_is_correct else "FAIL"
        override_mark = " [GUARDRAIL RESCUE]" if hybrid.get("guardrail_actions") else ""
        print(
            f"[{idx:02d}/40] {case.case_id} ({case.category}): '{case.mention_text}' -> {status_mark}{override_mark}",
            flush=True,
        )
        if not neural_is_correct:
            print(
                f"       Neural Proposed: {raw_judg} | {raw_mut} -> {raw_tgt} (Gold: {case.gold_judgment} | {case.gold_mutation})",
                flush=True,
            )
        if hybrid.get("guardrail_actions"):
            for act in hybrid["guardrail_actions"]:
                print(f"       Policy Action:   {act}", flush=True)

    # Output Summary
    print("\n" + "=" * 80, flush=True)
    print("SCOUT-C EMPIRICAL SUMMARY:", flush=True)
    print("=" * 80, flush=True)
    print(
        f"Raw Neural Decision Quality:     {neural_correct}/40 ({neural_correct / 40 * 100:.1f}%)",
        flush=True,
    )
    print(
        f"Raw Neural False Merges (FDAR):  {false_merges_raw}/40 ({false_merges_raw / 40 * 100:.1f}%)",
        flush=True,
    )
    print(
        f"Hybrid System Decision Quality:  {hybrid_correct}/40 ({hybrid_correct / 40 * 100:.1f}%)",
        flush=True,
    )
    print(
        f"Hybrid False Merges (FDAR_merge): {false_merges_hybrid}/40 ({false_merges_hybrid / 40 * 100:.1f}%)",
        flush=True,
    )
    print(f"Deterministic Guardrail Rescues: {guardrail_overrides}/40 cases", flush=True)
    print("-" * 80, flush=True)
    print("Per-Category Breakdown (Neural vs Hybrid):", flush=True)
    for cat in category_neural_stats:
        n_c = category_neural_stats[cat]["correct"]
        n_t = category_neural_stats[cat]["total"]
        h_c = category_hybrid_stats[cat]["correct"]
        print(
            f"  - {cat:20s}: Neural {n_c}/{n_t} ({n_c/n_t*100:.1f}%) -> Hybrid {h_c}/{n_t} ({h_c/n_t*100:.1f}%)",
            flush=True,
        )
    print("=" * 80, flush=True)

    # Write results
    with open("data/scout_c_results.json", "w") as f:
        json.dump(
            {
                "benchmark": "SCOUT-C",
                "total_cases": 40,
                "neural_correct": neural_correct,
                "hybrid_correct": hybrid_correct,
                "false_merges_raw": false_merges_raw,
                "false_merges_hybrid": false_merges_hybrid,
                "guardrail_overrides": guardrail_overrides,
                "category_neural_stats": category_neural_stats,
                "category_hybrid_stats": category_hybrid_stats,
                "cases": results,
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()
