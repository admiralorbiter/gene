"""Generate the 200-case factorial manifest for Stage 6B Contract-Guided State Adjudication.

Factorial Grid (4 x 5 x 2 x 5 = 200 cases):
- 4 Predicate Modes: functional_time_varying, multivalued_additive, episodic_point, interval_bounded
- 5 Update Patterns: forward_update, delayed_report, retroactive_correction, contemporaneous_disagreement, recurrence_expiry
- 2 Source Relations: same_source, independent_source
- 5 Support Topologies: direct_fact, single_derived_path, independent_alternatives, shared_premise_alternatives, recombinant_paths
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    BitemporalRule,
    EventType,
    TemporalEvent,
    compute_antichain,
    compute_cut_set_size,
)


def get_predicate_contract(mode: str) -> dict[str, Any]:
    if mode == "functional_time_varying":
        return {
            "predicate": "primary_residence",
            "cardinality": "SINGLE",
            "temporal_mode": "TIME_VARYING",
            "supersession_key": ["subject", "predicate"],
            "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
        }
    elif mode == "multivalued_additive":
        return {
            "predicate": "certified_skill",
            "cardinality": "MULTI",
            "temporal_mode": "ADDITIVE",
            "supersession_key": None,
            "conflict_policy": "ALLOW_CONCURRENT_VALUES",
        }
    elif mode == "episodic_point":
        return {
            "predicate": "visited_facility",
            "cardinality": "MULTI",
            "temporal_mode": "EPISODIC",
            "supersession_key": None,
            "conflict_policy": "ALLOW_OVERLAPPING_OCCURRENCES",
        }
    elif mode == "interval_bounded":
        return {
            "predicate": "security_clearance",
            "cardinality": "SINGLE",
            "temporal_mode": "INTERVAL_BOUNDED",
            "supersession_key": ["subject", "predicate"],
            "conflict_policy": "EXPIRE_ON_WINDOW_BOUNDARY",
        }
    raise ValueError(f"Unknown mode: {mode}")


def build_stage6b_case(
    case_idx: int,
    pred_mode: str,
    upd_pat: str,
    src_rel: str,
    supp_topo: str,
) -> dict[str, Any]:
    case_id = f"CASE_6B_{case_idx:03d}"
    contract = get_predicate_contract(pred_mode)
    pred_name = contract["predicate"]

    source_1 = "source_alpha"
    source_2 = "source_alpha" if src_rel == "same_source" else "source_beta"
    origin_1 = "origin_sensor_1"
    origin_2 = "origin_sensor_1" if src_rel == "same_source" else "origin_sensor_2"

    f_init = BitemporalFact(
        fact_id=f"occ_{case_id}_init",
        subject="Agent_Alice",
        predicate=pred_name,
        obj="Value_Alpha",
        roots=frozenset(["R_ALPHA"]),
        source_id=source_1,
        origin_id=origin_1,
    )

    f_aux1 = BitemporalFact(f"occ_{case_id}_aux1", "Protocol_X", "requires", "Value_Alpha", roots=frozenset(["R_ALPHA"]))
    f_aux2 = BitemporalFact(f"occ_{case_id}_aux2", "Agent_Alice", "alt_param", "Value_Gamma", roots=frozenset(["R_BETA"]))
    f_aux3 = BitemporalFact(f"occ_{case_id}_aux3", "Protocol_X", "requires_alt", "Value_Gamma", roots=frozenset(["R_BETA"]))

    if upd_pat == "forward_update":
        t_v_in = 5.0
        t_k_in = 1
        val_in = "Value_Beta"
    elif upd_pat == "delayed_report":
        t_v_in = 2.0
        t_k_in = 5
        val_in = "Value_Beta"
    elif upd_pat == "retroactive_correction":
        t_v_in = 1.0
        t_k_in = 3
        val_in = "Value_Beta"
    elif upd_pat == "contemporaneous_disagreement":
        t_v_in = 0.0
        t_k_in = 1
        val_in = "Value_Beta"
    elif upd_pat == "recurrence_expiry":
        t_v_in = 10.0
        t_k_in = 2
        val_in = "Value_Alpha"

    f_incoming = BitemporalFact(
        fact_id=f"occ_{case_id}_in",
        subject="Agent_Alice",
        predicate=pred_name,
        obj=val_in,
        roots=frozenset(["R_INCOMING"] if src_rel == "independent_source" else ["R_ALPHA"]),
        source_id=source_2,
        origin_id=origin_2,
    )

    init_events = [
        {
            "event_id": f"ev_{case_id}_ass_init",
            "event_type": "ASSERT",
            "t_knowledge": 0,
            "event_seq": 0,
            "t_valid_start": 0.0,
            "t_valid_end": 5.0 if pred_mode == "interval_bounded" else None,
            "target_fact_id": f_init.fact_id,
        }
    ]

    goal_triple = ("System", "action", "PERMIT")
    rules = []
    if supp_topo == "direct_fact":
        rules.append(BitemporalRule("r_dir", goal_triple, (f_init.triple,)))
    elif supp_topo == "single_derived_path":
        rules.append(BitemporalRule("r_path1", goal_triple, (f_init.triple, f_aux1.triple)))
    elif supp_topo == "independent_alternatives":
        rules.append(BitemporalRule("r_path1", goal_triple, (f_init.triple, f_aux1.triple)))
        rules.append(BitemporalRule("r_path2", goal_triple, (f_aux2.triple, f_aux3.triple)))
    elif supp_topo == "shared_premise_alternatives":
        rules.append(BitemporalRule("r_path1", goal_triple, (f_init.triple, f_aux1.triple)))
        rules.append(BitemporalRule("r_path2", goal_triple, (f_init.triple, f_aux3.triple)))
    elif supp_topo == "recombinant_paths":
        rules.append(BitemporalRule("r_path1", goal_triple, (f_init.triple, f_aux1.triple)))
        rules.append(BitemporalRule("r_path2", goal_triple, (f_aux2.triple, f_aux3.triple)))
        rules.append(BitemporalRule("r_path3", goal_triple, (f_init.triple, f_aux3.triple)))

    expected_transitions = []
    if pred_mode == "functional_time_varying":
        if upd_pat in ["forward_update", "delayed_report", "retroactive_correction"]:
            expected_transitions.append({"event_type": "ASSERT", "target_fact_id": f_incoming.fact_id, "t_valid_start": t_v_in})
            expected_transitions.append({"event_type": "SUPERSEDES", "target_fact_id": f_incoming.fact_id, "secondary_fact_id": f_init.fact_id, "t_valid_start": t_v_in})
        elif upd_pat == "contemporaneous_disagreement":
            expected_transitions.append({"event_type": "ASSERT", "target_fact_id": f_incoming.fact_id, "t_valid_start": t_v_in})
            if src_rel == "same_source":
                expected_transitions.append({"event_type": "SUPERSEDES", "target_fact_id": f_incoming.fact_id, "secondary_fact_id": f_init.fact_id, "t_valid_start": t_v_in})
            else:
                expected_transitions.append({"event_type": "CONTRADICTS", "target_fact_id": f_incoming.fact_id, "secondary_fact_id": f_init.fact_id, "t_valid_start": t_v_in, "t_valid_end": float("inf")})
        elif upd_pat == "recurrence_expiry":
            expected_transitions.append({"event_type": "ASSERT", "target_fact_id": f_incoming.fact_id, "t_valid_start": t_v_in})
    elif pred_mode == "multivalued_additive" or pred_mode == "episodic_point":
        expected_transitions.append({"event_type": "ASSERT", "target_fact_id": f_incoming.fact_id, "t_valid_start": t_v_in})
    elif pred_mode == "interval_bounded":
        expected_transitions.append({"event_type": "ASSERT", "target_fact_id": f_incoming.fact_id, "t_valid_start": t_v_in, "t_valid_end": t_v_in + 5.0})
        if upd_pat in ["forward_update", "delayed_report", "retroactive_correction"]:
            expected_transitions.append({"event_type": "SUPERSEDES", "target_fact_id": f_incoming.fact_id, "secondary_fact_id": f_init.fact_id, "t_valid_start": t_v_in})

    engine = BitemporalEngine(cautious_conflicts=True)
    engine.register_fact(f_init)
    engine.register_fact(f_incoming)
    engine.register_fact(f_aux1)
    engine.register_fact(f_aux2)
    engine.register_fact(f_aux3)
    for r in rules:
        engine.register_rule(r)

    for ev_dict in init_events:
        engine.record_event(TemporalEvent(
            event_id=ev_dict["event_id"],
            event_type=EventType(ev_dict["event_type"]),
            t_knowledge=ev_dict["t_knowledge"],
            event_seq=ev_dict["event_seq"],
            t_valid_start=ev_dict["t_valid_start"],
            t_valid_end=ev_dict["t_valid_end"],
            target_fact_id=ev_dict["target_fact_id"],
        ))

    for faux in [f_aux1, f_aux2, f_aux3]:
        engine.record_event(TemporalEvent(f"ev_ass_{faux.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=faux.fact_id))

    init_lineage = engine.compute_temporal_lineage(goal_triple, t_v=0.0, t_k=0)

    seq = 0
    for tr in expected_transitions:
        ev_type = EventType(tr["event_type"])
        engine.record_event(TemporalEvent(
            event_id=f"ev_exp_{case_id}_{seq}",
            event_type=ev_type,
            t_knowledge=t_k_in,
            event_seq=seq,
            t_valid_start=tr["t_valid_start"],
            t_valid_end=tr.get("t_valid_end"),
            target_fact_id=tr["target_fact_id"],
            secondary_fact_id=tr.get("secondary_fact_id"),
        ))
        seq += 1

    post_supp = engine.compute_temporal_support(goal_triple, t_v=t_v_in, t_k=t_k_in)
    post_lineage = engine.compute_temporal_lineage(goal_triple, t_v=t_v_in, t_k=t_k_in)
    rel_auth = engine.compute_relative_authority(goal_triple, t_v=t_v_in, t_k=t_k_in, init_lineage_sets=init_lineage)
    bnd_auth = engine.compute_bounded_authority(goal_triple, t_v=t_v_in, t_k=t_k_in, init_lineage_sets=init_lineage)

    return {
        "case_id": case_id,
        "predicate_mode": pred_mode,
        "update_pattern": upd_pat,
        "source_relation": src_rel,
        "support_topology": supp_topo,
        "predicate_contract": contract,
        "initial_facts": [f_init.fact_id, f_aux1.fact_id, f_aux2.fact_id, f_aux3.fact_id],
        "initial_events": init_events,
        "incoming_observation": {
            "obs_id": f"obs_{case_id}",
            "subject": "Agent_Alice",
            "predicate": pred_name,
            "obj": val_in,
            "t_valid": t_v_in,
            "t_knowledge": t_k_in,
            "source_id": source_2,
            "origin_id": origin_2,
            "lineage_roots": list(f_incoming.roots),
        },
        "expected_transitions": expected_transitions,
        "query": goal_triple,
        "evaluation_coordinates": {"t_valid": t_v_in, "t_knowledge": t_k_in},
        "expected_support_S": [sorted(list(s)) for s in sorted(post_supp, key=lambda x: sorted(list(x)))],
        "expected_lineage_S_L": [sorted(list(s)) for s in sorted(post_lineage, key=lambda x: sorted(list(x)))],
        "expected_entitlement": len(post_supp) > 0,
        "expected_relative_authority": round(rel_auth, 4),
        "expected_bounded_authority": round(bnd_auth, 4),
    }


def generate_stage6b_dataset() -> None:
    pred_modes = ["functional_time_varying", "multivalued_additive", "episodic_point", "interval_bounded"]
    upd_patterns = ["forward_update", "delayed_report", "retroactive_correction", "contemporaneous_disagreement", "recurrence_expiry"]
    src_relations = ["same_source", "independent_source"]
    supp_topologies = ["direct_fact", "single_derived_path", "independent_alternatives", "shared_premise_alternatives", "recombinant_paths"]

    cases = []
    case_idx = 1
    for p in pred_modes:
        for u in upd_patterns:
            for s in src_relations:
                for t in supp_topologies:
                    cases.append(build_stage6b_case(case_idx, p, u, s, t))
                    case_idx += 1

    jsonl_path = Path(r"C:\Users\admir\Github\gene\data\exploration_round6_stage6b_cases.jsonl")
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    manifest_bytes = jsonl_path.read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()

    manifest = {
        "experiment_name": "Stage 6B Contract-Guided State Adjudication Factorial Benchmark",
        "total_cases": len(cases),
        "grid_dimensions": {
            "predicate_modes": pred_modes,
            "update_patterns": upd_patterns,
            "source_relations": src_relations,
            "support_topologies": supp_topologies,
        },
        "cases_file": "exploration_round6_stage6b_cases.jsonl",
        "cases_sha256": manifest_sha256,
    }

    manifest_path = Path(r"C:\Users\admir\Github\gene\data\exploration_round6_stage6b_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(cases)} Stage 6B cases at {jsonl_path}")
    print(f"Saved manifest to {manifest_path} (SHA-256: {manifest_sha256[:16]}...)")


if __name__ == "__main__":
    generate_stage6b_dataset()
