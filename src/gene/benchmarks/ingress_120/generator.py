"""120-World Factorial Benchmark Generator (Thread B).

Factorial Grid:
- 4 Predicate Modes: TIME_VARYING, ADDITIVE, EPISODIC, INTERVAL_BOUNDED
- 5 Binding Conditions: EXACT_CANONICAL, SURFACE_ALIAS, CANDIDATE_COLLISION, ROLE_DISTRACTOR, NOVEL_ENTITY
- 3 Temporal Relations: FORWARD_UPDATE, RETROACTIVE_BACKFILL, CONTEMPORANEOUS_DISPUTE
- 2 Source Role Forms: DIRECT_OBSERVATION, ATTRIBUTED_REPORT
Total: 4 x 5 x 3 x 2 = 120 worlds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class IngressTestCase:
    """Specification of a single world in the 120-world factorial benchmark."""
    case_id: str
    predicate_mode: str
    binding_condition: str
    temporal_relation: str
    source_role_form: str
    # Raw observation details
    raw_text: str
    subject_mention: str
    predicate_name: str
    object_mention: str
    t_valid_start: float
    t_valid_end: float | None
    t_knowledge: int
    claimed_source: str
    claimed_role: str
    is_authenticated: bool
    # Candidate hypotheses provided by upstream candidate generator
    subject_candidate_ids: tuple[str, ...]
    object_candidate_ids: tuple[str, ...]
    is_subject_novel: bool = False
    is_object_novel: bool = False
    # Ground truth expected entity bindings (if resolvable)
    gold_subject_id: str | None = None
    gold_object_id: str | None = None


def generate_120_worlds() -> list[IngressTestCase]:
    """Generate the deterministic, balanced 120-world factorial benchmark."""
    predicate_modes = ["TIME_VARYING", "ADDITIVE", "EPISODIC", "INTERVAL_BOUNDED"]
    binding_conditions = ["EXACT_CANONICAL", "SURFACE_ALIAS", "CANDIDATE_COLLISION", "ROLE_DISTRACTOR", "NOVEL_ENTITY"]
    temporal_relations = ["FORWARD_UPDATE", "RETROACTIVE_BACKFILL", "CONTEMPORANEOUS_DISPUTE"]
    source_role_forms = ["DIRECT_OBSERVATION", "ATTRIBUTED_REPORT"]

    cases: list[IngressTestCase] = []
    case_num = 0

    for p_mode in predicate_modes:
        pred_name = f"metric_{p_mode.lower()}"
        for b_cond in binding_conditions:
            for t_rel in temporal_relations:
                for s_role in source_role_forms:
                    cid = f"C7_{case_num:03d}"
                    case_num += 1

                    # Establish timing coordinates
                    if t_rel == "FORWARD_UPDATE":
                        tv_s, tv_e, tk = 10.0, None if p_mode != "INTERVAL_BOUNDED" else 15.0, 2
                    elif t_rel == "RETROACTIVE_BACKFILL":
                        tv_s, tv_e, tk = 2.0, 5.0 if p_mode == "INTERVAL_BOUNDED" else None, 3
                    else:  # CONTEMPORANEOUS_DISPUTE
                        tv_s, tv_e, tk = 5.0, None if p_mode != "INTERVAL_BOUNDED" else 10.0, 2

                    # Establish source context
                    is_auth = (s_role == "DIRECT_OBSERVATION")
                    claimed_src = "sensor_alpha" if s_role == "DIRECT_OBSERVATION" else "unverified_third_party"
                    claimed_r = "sensor" if s_role == "DIRECT_OBSERVATION" else "guest"

                    # Establish binding specifics
                    if b_cond == "EXACT_CANONICAL":
                        sub_mention = "Server_Node_1"
                        obj_mention = "Value_Operational"
                        sub_cands = ("Server_Node_1",)
                        obj_cands = ("Value_Operational",)
                        is_sub_nov, is_obj_nov = False, False
                        gold_s, gold_o = "Server_Node_1", "Value_Operational"
                        raw = f"Server_Node_1 {pred_name} is Value_Operational"

                    elif b_cond == "SURFACE_ALIAS":
                        sub_mention = "Primary Server 1"
                        obj_mention = "Active"
                        sub_cands = ("Server_Node_1",)
                        obj_cands = ("Value_Operational",)
                        is_sub_nov, is_obj_nov = False, False
                        gold_s, gold_o = "Server_Node_1", "Value_Operational"
                        raw = f"Primary Server 1 {pred_name} is Active"

                    elif b_cond == "CANDIDATE_COLLISION":
                        sub_mention = "Server 1"
                        obj_mention = "Operational"
                        sub_cands = ("Server_Node_1", "Server_Node_1_Backup")
                        obj_cands = ("Value_Operational",)
                        is_sub_nov, is_obj_nov = False, False
                        gold_s, gold_o = None, None  # Ambiguous collision
                        raw = f"Server 1 {pred_name} is Operational"

                    elif b_cond == "ROLE_DISTRACTOR":
                        sub_mention = "Field Monitor Beta reported Server Node 1"
                        obj_mention = "Operational"
                        sub_cands = ("Server_Node_1",)  # Monitored device correctly identified
                        obj_cands = ("Value_Operational",)
                        is_sub_nov, is_obj_nov = False, False
                        gold_s, gold_o = "Server_Node_1", "Value_Operational"
                        raw = f"Field Monitor Beta reported Server Node 1 {pred_name} is Operational"

                    else:  # NOVEL_ENTITY
                        sub_mention = "Quantum Core 99"
                        obj_mention = "Operational"
                        sub_cands = ()
                        obj_cands = ("Value_Operational",)
                        is_sub_nov, is_obj_nov = True, False
                        gold_s, gold_o = None, None
                        raw = f"Quantum Core 99 {pred_name} is Operational"

                    case = IngressTestCase(
                        case_id=cid,
                        predicate_mode=p_mode,
                        binding_condition=b_cond,
                        temporal_relation=t_rel,
                        source_role_form=s_role,
                        raw_text=raw,
                        subject_mention=sub_mention,
                        predicate_name=pred_name,
                        object_mention=obj_mention,
                        t_valid_start=tv_s,
                        t_valid_end=tv_e,
                        t_knowledge=tk,
                        claimed_source=claimed_src,
                        claimed_role=claimed_r,
                        is_authenticated=is_auth,
                        subject_candidate_ids=sub_cands,
                        object_candidate_ids=obj_cands,
                        is_subject_novel=is_sub_nov,
                        is_object_novel=is_obj_nov,
                        gold_subject_id=gold_s,
                        gold_object_id=gold_o,
                    )
                    cases.append(case)

    return cases
