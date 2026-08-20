"""Track R Runner: Role Equivariance & Semantic Shortcut Dissection (24 Calls).

Evaluates 3 representation conditions (Canonical, Role-Swapped, Opaque) across 8 lattice points on KESTREL.
Uses production CallSpec and immutable SQLite persistence.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any
from gene.ollama_client import CallSpec, OllamaClient
from gene.experiments.epistemic_ir import (
    EpistemicState,
    PremiseNode,
    PrivilegeLevel,
    QueryContract,
    RuleAntecedent,
    RuleSpec,
    SupportEnvironment,
)
from gene.experiments.epistemic_renderer import EpistemicRenderer
from gene.experiments.transformations import RoleEquivarianceTransform
from gene.experiments.context_compiler import EpistemicContextCompiler
from gene.experiments.evaluators_round4 import (
    CallRecord,
    EvaluationRecord,
    FROZEN_ROUND4_SYSTEM_PROMPT,
    TrackRMetrics,
    evaluate_conformance_k_a,
    evaluate_track_r_panel,
    init_round4_db,
    parse_round4_model_output,
    persist_round4_call_and_evaluation,
)


def build_kestrel_track_r_base() -> tuple[EpistemicState, QueryContract]:
    """Construct Kestrel baseline epistemic state."""
    premises = {
        "occ_A": PremiseNode(
            occurrence_id="occ_A",
            semantic_claim_id="claim_kestrel_nerin_manager",
            predicate="has_role",
            subject="Nerin",
            entity="KESTREL",
            role="manager",
            root_ids=["R1"],
        ),
        "occ_B": PremiseNode(
            occurrence_id="occ_B",
            semantic_claim_id="claim_kestrel_nerin_reports_s1",
            predicate="reports_to",
            subject="Nerin",
            entity="KESTREL",
            target_value="sector lead S1",
            root_ids=["R1"],
        ),
        "occ_D": PremiseNode(
            occurrence_id="occ_D",
            semantic_claim_id="claim_kestrel_vael_sector_lead",
            predicate="has_role",
            subject="Vael",
            entity="KESTREL",
            role="sector_lead",
            root_ids=["R2"],
        ),
        "occ_E": PremiseNode(
            occurrence_id="occ_E",
            semantic_claim_id="claim_kestrel_vael_reports_s2",
            predicate="reports_to",
            subject="Vael",
            entity="KESTREL",
            target_value="sector lead S2",
            root_ids=["R2"],
        ),
    }

    rules = {
        "rule_1": RuleSpec(
            rule_id="rule_1",
            antecedents=[
                RuleAntecedent(predicate="has_role", subject_role="manager"),
                RuleAntecedent(predicate="reports_to", target_value="sector lead S1"),
            ],
            consequent_predicate="station_operates_protocol",
            consequent_protocol="PROTO_X7",
        ),
        "rule_2": RuleSpec(
            rule_id="rule_2",
            antecedents=[
                RuleAntecedent(predicate="has_role", subject_role="sector_lead"),
                RuleAntecedent(predicate="reports_to", target_value="sector lead S2"),
            ],
            consequent_predicate="station_operates_protocol",
            consequent_protocol="PROTO_X7",
        ),
    }

    envs = [
        SupportEnvironment(
            path_id="path_AB",
            rule_id="rule_1",
            required_semantic_claim_ids=["claim_kestrel_nerin_manager", "claim_kestrel_nerin_reports_s1"],
        ),
        SupportEnvironment(
            path_id="path_DE",
            rule_id="rule_2",
            required_semantic_claim_ids=["claim_kestrel_vael_sector_lead", "claim_kestrel_vael_reports_s2"],
        ),
    ]

    query = QueryContract(
        target_station="KESTREL",
        target_predicate="station_operates_protocol",
        query_question="Based on authorized rules and evidence, what protocol is authorized for station KESTREL?",
        allow_unknown=True,
        output_schema_json='{"station": "KESTREL", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}',
    )

    state = EpistemicState(
        premises=premises,
        rules=rules,
        support_environments=envs,
        invalidated_roots=[],
    )
    EpistemicRenderer.render_state(state)
    return state, query


def run_track_r(client: Any, db_path: str, max_calls: int | None = None) -> tuple[list[EvaluationRecord], TrackRMetrics]:
    """Execute Track R experimental design with CallSpec and immutable persistence."""
    init_round4_db(db_path)
    base_state, base_query = build_kestrel_track_r_base()

    # 3 Representation conditions
    cond_canonical = (base_state, base_query, "cond_canonical")
    swapped_state, swapped_query = RoleEquivarianceTransform.swap_role_slots(base_state, base_query, "manager", "sector_lead")
    cond_swapped = (swapped_state, swapped_query, "cond_swapped")
    anon_state, anon_query = RoleEquivarianceTransform.anonymize_roles(base_state, base_query, {"manager": "ROLE_Q7", "sector_lead": "ROLE_M2"})
    cond_opaque = (anon_state, anon_query, "cond_opaque")

    conditions = [cond_canonical, cond_swapped, cond_opaque]

    # 8 Lattice points per condition
    lattice_points = [
        (["occ_A", "occ_B", "occ_D", "occ_E"], "PROTO_X7", "point_all_4"),
        (["occ_A", "occ_B"], "PROTO_X7", "point_path_AB"),
        (["occ_D", "occ_E"], "PROTO_X7", "point_path_DE"),
        (["occ_B", "occ_D"], "UNKNOWN", "point_cross_BD"),
        (["occ_A", "occ_E"], "UNKNOWN", "point_cross_AE"),
        (["occ_A", "occ_D"], "UNKNOWN", "point_cross_AD"),
        (["occ_B", "occ_E"], "UNKNOWN", "point_cross_BE"),
        ([], "UNKNOWN", "point_empty"),
    ]

    evaluations = []
    condition_preds: dict[str, dict[str, str]] = {"cond_canonical": {}, "cond_swapped": {}, "cond_opaque": {}}
    compiler = EpistemicContextCompiler(pipeline=PrivilegeLevel.RAW_SERIALIZATION)
    call_idx = 0

    for state_cand, query_cand, cond_id in conditions:
        for occ_subset, expected_proto, pt_label in lattice_points:
            if max_calls is not None and call_idx >= max_calls:
                break

            sub_state = state_cand.subselect_occurrences(occ_subset)
            ctx = compiler.compile(sub_state, query_cand, occurrence_order=occ_subset, equivalence_class_id=cond_id)

            call_id = f"call_r_{cond_id}_{pt_label}"
            spec = CallSpec(
                model_name="gemma3:12b",
                system_prompt=FROZEN_ROUND4_SYSTEM_PROMPT,
                user_prompt=ctx.prompt,
                temperature=0.0,
                seed=42,
                format="json",
            )

            result = client.chat(spec)
            parsed = parse_round4_model_output(result.raw_response_text)
            condition_preds[cond_id][pt_label] = parsed.protocol

            k_a = evaluate_conformance_k_a(parsed.protocol, expected_proto, is_valid_json=parsed.is_valid_json)

            call_spec_sha = hashlib.sha256(spec.model_dump_json().encode("utf-8")).hexdigest()
            call_rec = CallRecord(
                call_id=call_id,
                track="track_r",
                call_spec_sha256=call_spec_sha,
                model_name=result.model_name,
                model_digest=result.model_digest,
                system_prompt=spec.system_prompt,
                user_prompt=spec.user_prompt,
                temperature=spec.temperature,
                seed=spec.seed,
                format=spec.format if isinstance(spec.format, str) else "json",
                raw_response_text=result.raw_response_text,
                latency_ms=result.latency_ms,
            )

            eval_rec = EvaluationRecord(
                call_id=call_id,
                track="track_r",
                condition_id=f"{cond_id}_{pt_label}",
                station="KESTREL",
                expected_protocol=expected_proto,
                predicted_protocol=parsed.protocol,
                reported_support_evidence=parsed.reported_support_evidence,
                independence_status=parsed.independence_status,
                perceived_independent_roots=parsed.perceived_independent_roots,
                is_valid_json=1 if parsed.is_valid_json else 0,
                k_a=k_a,
                prompt_hash=hashlib.sha256(ctx.prompt.encode("utf-8")).hexdigest(),
                state_hash=ctx.state_hash,
                compiler_pipeline="RAW_SERIALIZATION",
            )

            persist_round4_call_and_evaluation(db_path, call_rec, eval_rec)
            evaluations.append(eval_rec)
            call_idx += 1

    panel_metrics = evaluate_track_r_panel(
        condition_preds["cond_canonical"],
        condition_preds["cond_swapped"],
        condition_preds["cond_opaque"],
    )
    return evaluations, panel_metrics
