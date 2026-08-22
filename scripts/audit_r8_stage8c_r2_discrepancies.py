import json
from pathlib import Path

gold = json.load(open("data/r8_stage8c_r2_gold_manifest.json"))
records = [json.loads(line) for line in open("data/r8_stage8c_r2_candidate_evidence.jsonl")]

print("=================== DISCREPANCY AUDIT ===================")
by_arm = {}
for r in records:
    doc_id = r["doc_id"]
    g = gold[doc_id]
    d = r["hybrid_decision"]
    arm = r["arm"]
    by_arm.setdefault(arm, {"total": 0, "correct": 0, "discrepancies": []})
    by_arm[arm]["total"] += 1

    is_match = (d.get("action") == g["action"]) and (d.get("target_id") == g["expected_target"])
    if is_match:
        by_arm[arm]["correct"] += 1
    else:
        by_arm[arm]["discrepancies"].append((r, g, d))

for arm, stats in by_arm.items():
    print(f"\nARM: {arm} -> {stats['correct']}/{stats['total']} correct ({stats['correct']/stats['total']*100:.1f}%)")
    for r, g, d in stats["discrepancies"]:
        print(f"  [{r['world_id']} {r['doc_id']}] Mention: '{r['mention']}' | Action: Gold={g['action']} vs Hybrid={d.get('action')}")
        print(f"    Gold Target:   {g['expected_target']}")
        print(f"    Hybrid Target: {d.get('target_id')}")
        print(f"    Context:       {r['context']}")
        print(f"    Rationale:     {d.get('rationale')}")
        print(f"    Neural Prop:   {r['neural_proposal']}")
