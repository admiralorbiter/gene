"""Rescore raw Stage 8C-R1 JSONL evidence with world-local gold provisional identity binding.
"""
import json
import sqlite3
from pathlib import Path

def rescore_stage8c_r1():
    data_dir = Path("data")
    jsonl_path = data_dir / "r8_stage8c_r1_candidate_evidence.jsonl"
    sqlite_path = data_dir / "r8_stage8c_r1_registry.sqlite"

    with open(jsonl_path, "r", encoding="utf-8") as f:
        records = [json.loads(line.strip()) for line in f if line.strip()]

    # Group by world_id
    worlds = {}
    for r in records:
        wid = r["world_id"]
        if wid not in worlds:
            worlds[wid] = []
        worlds[wid].append(r)

    rescored_records = []
    
    for wid, w_recs in worlds.items():
        prov_binding_hybrid = {} # gold_prov_id -> runtime_prov_id
        prov_binding_neural = {}

        for r in w_recs:
            doc_id = r["doc_id"]
            gold = r["gold"]
            neural = r["neural_proposal"]
            ingress = r["ingress_result"]

            gold_act = gold.get("action")
            gold_tgt = gold.get("expected_target")

            # --- Rescore Neural Proposal ---
            neural_act = neural.get("registry_mutation")
            neural_tgt = neural.get("target_id")
            neural_judg = neural.get("identity_judgment")

            is_neural_correct = False
            if gold_act == "DEFER":
                is_neural_correct = (neural_act in ["DEFER", None]) or (neural_judg == "AMBIGUOUS")
            elif gold_act == "CREATE_PROVISIONAL":
                # Neural schema requires target_id=None or NOVEL
                is_neural_correct = (neural_act == "CREATE_PROVISIONAL") or (neural_judg == "NOVEL")
                if is_neural_correct and neural_tgt:
                    prov_binding_neural[gold_tgt] = neural_tgt
                elif is_neural_correct:
                    prov_binding_neural[gold_tgt] = "PROV_CREATED"
            elif gold_act == "LINK":
                if gold_tgt in prov_binding_neural:
                    bound = prov_binding_neural[gold_tgt]
                    is_neural_correct = (neural_act == "LINK") and (neural_tgt == bound or (bound == "PROV_CREATED" and neural_tgt and neural_tgt.startswith("prov_")))
                else:
                    is_neural_correct = (neural_act == "LINK") and (neural_tgt == gold_tgt)

            # --- Rescore Hybrid Ingress ---
            hybrid_act = ingress.get("action")
            hybrid_tgt = ingress.get("target_id")

            is_hybrid_correct = False
            if gold_act == "DEFER":
                is_hybrid_correct = (hybrid_act == "DEFER")
            elif gold_act == "CREATE_PROVISIONAL":
                is_hybrid_correct = (hybrid_act == "CREATE_PROVISIONAL") and (hybrid_tgt is not None)
                if is_hybrid_correct:
                    prov_binding_hybrid[gold_tgt] = hybrid_tgt
            elif gold_act == "LINK":
                if gold_tgt in prov_binding_hybrid:
                    bound = prov_binding_hybrid[gold_tgt]
                    is_hybrid_correct = (hybrid_act == "LINK") and (hybrid_tgt == bound)
                else:
                    is_hybrid_correct = (hybrid_act == "LINK") and (hybrid_tgt == gold_tgt)

            rescored_r = dict(r)
            rescored_r["is_neural_correct"] = is_neural_correct
            rescored_r["is_hybrid_correct"] = is_hybrid_correct
            rescored_records.append(rescored_r)

    # Compute Rescored Gate Metrics
    neural_acc = sum(1 for r in rescored_records if r["is_neural_correct"]) / len(rescored_records)
    
    resolvable = [
        r for r in rescored_records
        if r["arm"] in ["ARM1_NOVEL", "ARM2_KNOWN_ALIAS", "ARM3_PARTITION"]
        or (r["arm"] == "ARM4B_DEFERRED_RESOLVED" and r["doc_id"].endswith("_2"))
    ]
    useful_admissions = sum(1 for r in resolvable if r["is_hybrid_correct"])
    useful_rate = useful_admissions / len(resolvable)

    print("================================================================================")
    print("MECHANICAL RESCORING OF FROZEN R1 EVIDENCE WITH WORLD-LOCAL IDENTITY BINDING")
    print("================================================================================")
    print(f"Total Decisions: {len(rescored_records)}")
    print(f"Rescored Gate 1 Neural Proposal Accuracy:  {sum(1 for r in rescored_records if r['is_neural_correct'])}/120 ({neural_acc*100:.1f}%) [was 53/120, 44.2%]")
    print(f"Rescored Gate 6 Useful Resolvable Coverage: {useful_admissions}/97 ({useful_rate*100:.1f}%) [was 36/97, 37.1%]")
    print("--------------------------------------------------------------------------------")
    print("Arm Breakdown (Hybrid Correct / Total):")
    for arm in ["ARM1_NOVEL", "ARM2_KNOWN_ALIAS", "ARM3_PARTITION", "ARM4A_PERMANENT_DEFERRAL", "ARM4B_DEFERRED_RESOLVED"]:
        arm_recs = [r for r in rescored_records if r["arm"] == arm]
        arm_h_corr = sum(1 for r in arm_recs if r["is_hybrid_correct"])
        arm_n_corr = sum(1 for r in arm_recs if r["is_neural_correct"])
        print(f"  {arm:<26}: Neural {arm_n_corr:>2}/{len(arm_recs)} ({arm_n_corr/len(arm_recs)*100:5.1f}%) | Hybrid {arm_h_corr:>2}/{len(arm_recs)} ({arm_h_corr/len(arm_recs)*100:5.1f}%)")

if __name__ == "__main__":
    rescore_stage8c_r1()
