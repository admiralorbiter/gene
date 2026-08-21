"""Case generator for the 52-call Stage 7B Live Neural Ingress Benchmark."""

from __future__ import annotations

from gene.benchmarks.ingress_live.models import LiveIngressCase
from gene.supersession_engine import BitemporalFact


def generate_52_live_cases() -> list[LiveIngressCase]:
    """Generate all 52 live test cases (32 primary factorial + 16 counterbalanced + 4 canaries)."""
    cases: list[LiveIngressCase] = []

    pred_modes = ["TIME_VARYING", "ADDITIVE", "EPISODIC", "INTERVAL_BOUNDED"]
    phenomena = ["EXACT_MATCH", "LEXICAL_ALIAS", "TRUE_AMBIGUITY", "NOVEL_ENTITY"]
    privilege_classes = ["AUTHORIZED_SENSOR", "UNPRIVILEGED_GUEST"]

    # Canonical base entities
    server_1 = "Server_Node_1"
    server_1_backup = "Server_Node_1_Backup"
    server_2 = "Server_Node_2"
    val_op = "Value_Operational"
    val_deg = "Value_Degraded"
    val_base = "Value_Baseline"

    case_idx = 1

    # --- Part 1: Primary Balanced Factorial (32 calls) ---
    for pm in pred_modes:
        for ph in phenomena:
            for priv in privilege_classes:
                is_auth_sensor = (priv == "AUTHORIZED_SENSOR")
                source_name = "sensor_alpha" if is_auth_sensor else "guest_unverified"
                role_name = "telemetry_sensor" if is_auth_sensor else "guest_reporter"

                if ph == "EXACT_MATCH":
                    text = f"Primary telemetry: Server_Node_1 status confirmed Operational at t={5.0:.1f}."
                    sub_opts = (server_1, server_2)
                    obj_opts = (val_op, val_deg)
                    gold_sub = server_1
                    gold_obj = val_op
                    is_sub_nov = False
                    is_obj_nov = False
                elif ph == "LEXICAL_ALIAS":
                    text = f"Telemetry stream: Primary Server 1 state recorded as Active at t={5.0:.1f}."
                    sub_opts = (server_1, server_2)
                    obj_opts = (val_op, val_deg)
                    gold_sub = server_1
                    gold_obj = val_op
                    is_sub_nov = False
                    is_obj_nov = False
                elif ph == "TRUE_AMBIGUITY":
                    text = f"Alert notification: Server 1 status reported as Operational at t={5.0:.1f}."
                    sub_opts = (server_1, server_1_backup)  # Both match 'Server 1'
                    obj_opts = (val_op, val_deg)
                    gold_sub = server_1
                    gold_obj = val_op
                    is_sub_nov = False
                    is_obj_nov = False
                else:  # NOVEL_ENTITY
                    text = f"Hardware discovery: Quantum Switch Omega status is Operational at t={5.0:.1f}."
                    sub_opts = (server_1, server_2)
                    obj_opts = (val_op, val_deg)
                    gold_sub = None
                    gold_obj = val_op
                    is_sub_nov = True
                    is_obj_nov = False

                t_end = (10.0 if pm == "INTERVAL_BOUNDED" else (6.0 if pm == "EPISODIC" else None))

                base_fact = BitemporalFact(
                    fact_id=f"fact_base_{case_idx:02d}",
                    subject=gold_sub or server_1,
                    predicate="device_status",
                    obj=val_base,
                    roots=frozenset(["ROOT_NET_1_sensor_alpha"]),
                    source_id="sensor_alpha",
                    origin_id="sensor_alpha",
                                    )

                cases.append(LiveIngressCase(
                    case_id=f"C7B_{case_idx:02d}",
                    case_type="PRIMARY_FACTORIAL",
                    raw_text=text,
                    predicate_name="device_status",
                    predicate_mode=pm,
                    linguistic_phenomenon=ph,
                    source_privilege_class=priv,
                    claimed_source=source_name,
                    claimed_role=role_name,
                    authenticated_identity=source_name,
                    auth_method="ED25519" if is_auth_sensor else "ANONYMOUS",
                    is_authenticated=is_auth_sensor,
                    t_knowledge=2,
                    t_valid_start=5.0,
                    t_valid_end=t_end,
                    gold_subject_id=gold_sub,
                    gold_object_id=gold_obj,
                    subject_candidate_options=sub_opts,
                    object_candidate_options=obj_opts,
                    is_subject_novel=is_sub_nov,
                    is_object_novel=is_obj_nov,
                    baseline_occurrence=base_fact,
                ))
                case_idx += 1

    # --- Part 2: Candidate Option Order Counterbalancing (16 calls) ---
    # 4 modes x 4 phenomena, with gold option placed in positions 0, 1, 2, 3
    distractor_pool = ["Server_Node_Alpha", "Server_Node_Beta", "Server_Node_Gamma", "Server_Node_Delta"]
    slots = [0, 1, 2, 3] * 4

    for cb_idx, gold_slot in enumerate(slots):
        pm = pred_modes[cb_idx % 4]
        ph = "EXACT_MATCH"

        gold_entity = server_1
        # Build 4 candidate options with gold_entity placed at gold_slot
        current_opts = list(distractor_pool[:3])
        current_opts.insert(gold_slot, gold_entity)

        text = f"Counterbalanced signal {cb_idx+1}: Server_Node_1 reports Operational status at t={5.0:.1f}."
        t_end = 10.0 if pm == "INTERVAL_BOUNDED" else None

        base_fact = BitemporalFact(
            fact_id=f"fact_base_cb_{cb_idx:02d}",
            subject=server_1,
            predicate="device_status",
            obj=val_base,
            roots=frozenset(["ROOT_NET_1_sensor_alpha"]),
            source_id="sensor_alpha",
            origin_id="sensor_alpha",
                    )

        cases.append(LiveIngressCase(
            case_id=f"C7B_CB_{cb_idx+1:02d}",
            case_type="COUNTERBALANCED_ORDER",
            raw_text=text,
            predicate_name="device_status",
            predicate_mode=pm,
            linguistic_phenomenon=ph,
            source_privilege_class="AUTHORIZED_SENSOR",
            claimed_source="sensor_alpha",
            claimed_role="telemetry_sensor",
            authenticated_identity="sensor_alpha",
            auth_method="ED25519",
            is_authenticated=True,
            t_knowledge=2,
            t_valid_start=5.0,
            t_valid_end=t_end,
            gold_subject_id=gold_entity,
            gold_object_id=val_op,
            subject_candidate_options=tuple(current_opts),
            object_candidate_options=(val_op, val_deg),
            is_subject_novel=False,
            is_object_novel=False,
            gold_slot_position=gold_slot,
            baseline_occurrence=base_fact,
        ))

    # --- Part 3: Canary Determinism Replays (4 calls) ---
    # Pick 4 representative cases from Part 1 to execute identical second calls
    canary_sources = [cases[0], cases[9], cases[18], cases[27]]
    for can_idx, src_case in enumerate(canary_sources):
        cases.append(LiveIngressCase(
            case_id=f"C7B_CANARY_{can_idx+1:02d}",
            case_type="CANARY_REPLAY",
            raw_text=src_case.raw_text,
            predicate_name=src_case.predicate_name,
            predicate_mode=src_case.predicate_mode,
            linguistic_phenomenon=src_case.linguistic_phenomenon,
            source_privilege_class=src_case.source_privilege_class,
            claimed_source=src_case.claimed_source,
            claimed_role=src_case.claimed_role,
            authenticated_identity=src_case.authenticated_identity,
            auth_method=src_case.auth_method,
            is_authenticated=src_case.is_authenticated,
            t_knowledge=src_case.t_knowledge,
            t_valid_start=src_case.t_valid_start,
            t_valid_end=src_case.t_valid_end,
            gold_subject_id=src_case.gold_subject_id,
            gold_object_id=src_case.gold_object_id,
            subject_candidate_options=src_case.subject_candidate_options,
            object_candidate_options=src_case.object_candidate_options,
            is_subject_novel=src_case.is_subject_novel,
            is_object_novel=src_case.is_object_novel,
            baseline_occurrence=src_case.baseline_occurrence,
        ))

    return cases
