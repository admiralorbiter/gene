"""Track P Runner: Permutation Invariance & Serialization Spread (28 Calls).

Evaluates 24 raw flat permutations + 1 canonical baseline + 3 exact replays on VELORA.
Uses production CallSpec and immutable SQLite persistence.
"""

from __future__ import annotations

import hashlib
import json
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
from gene.experiments.transformations import PermutationTransform
from gene.experiments.context_compiler import EpistemicContextCompiler
from gene.experiments.evaluators_round4 import (
    CallRecord,
    EvaluationRecord,
    FROZEN_ROUND4_SYSTEM_PROMPT,
    TrackPMetrics,
    evaluate_conformance_k_a,
    evaluate_track_p_panel,
    init_round4_db,
    parse_round4_model_output,
    persist_round4_call_and_evaluation,
)


def build_velora_track_p_base() -> tuple[EpistemicState, QueryContract]:
    """Construct Velora baseline epistemic state."""
    premises = {
        "occ_A": PremiseNode(
            occurrence_id="occ_A",
            semantic_claim_id="claim_velora_nerin_manager",
            predicate="has_role",
            subject="Nerin",
            entity="VELORA",
            role="manager",
            root_ids=["R1"],
        ),
        "occ_B": PremiseNode(
            occurrence_id="occ_B",
            semantic_claim_id="claim_velora_nerin_reports_s1",
            predicate="reports_to",
            subject="Nerin",
            entity="VELORA",
            target_value="sector lead S1",
            root_ids=["R1"],
        ),
        "occ_D": PremiseNode(
            occurrence_id="occ_D",
            semantic_claim_id="claim_velora_vael_sector_lead",
            predicate="has_role",
            subject="Vael",
            entity="VELORA",
            role="sector_lead",
            root_ids=["R2"],
        ),
        "occ_E": PremiseNode(
            occurrence_id="occ_E",
            semantic_claim_id="claim_velora_vael_reports_s2",
            predicate="reports_to",
            subject="Vael",
            entity="VELORA",
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
            required_semantic_claim_ids=["claim_velora_nerin_manager", "claim_velora_nerin_reports_s1"],
        ),
        SupportEnvironment(
            path_id="path_DE",
            rule_id="rule_2",
            required_semantic_claim_ids=["claim_velora_vael_sector_lead", "claim_velora_vael_reports_s2"],
        ),
    ]

    query = QueryContract(
        target_station="VELORA",
        target_predicate="station_operates_protocol",
        query_question="Based on authorized rules and evidence, what protocol is authorized for station VELORA?",
        allow_unknown=True,
        output_schema_json='{"station": "VELORA", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}',
    )

    state = EpistemicState(
        premises=premises,
        rules=rules,
        support_environments=envs,
        invalidated_roots=[],
    )
    EpistemicRenderer.render_state(state)
    return state, query


def run_track_p(client: Any, db_path: str, max_calls: int | None = None) -> tuple[list[EvaluationRecord], TrackPMetrics]:
    """Execute Track P experimental design."""
    init_round4_db(db_path)
    base_state, base_query = build_velora_track_p_base()

    all_perms = PermutationTransform.generate_all_permutations(base_state)
    assert len(all_perms) == 24

    compiler_raw = EpistemicContextCompiler(pipeline=PrivilegeLevel.RAW_SERIALIZATION)
    compiler_canon = EpistemicContextCompiler(pipeline=PrivilegeLevel.TOPOLOGY_AWARE_GROUPING)

    evaluations = []
    raw_predictions = []
    call_idx = 0

    # 1. 24 Raw Flat Permutations
    for idx, perm in enumerate(all_perms):
        if max_calls is not None and call_idx >= max_calls:
            break

        ctx = compiler_raw.compile(base_state, base_query, occurrence_order=perm, equivalence_class_id=f"perm_{idx+1}")
        call_id = f"call_p_raw_perm_{idx+1:02d}"
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
        raw_predictions.append(parsed.protocol)

        k_a = evaluate_conformance_k_a(parsed.protocol, "PROTO_X7", is_valid_json=parsed.is_valid_json)

        call_spec_sha = hashlib.sha256(spec.model_dump_json().encode("utf-8")).hexdigest()
        call_rec = CallRecord(
            call_id=call_id,
            track="track_p",
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
            track="track_p",
            condition_id=f"raw_perm_{idx+1:02d}",
            station="VELORA",
            expected_protocol="PROTO_X7",
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

    # 2. 1 Canonical Baseline + 3 Exact Replays (4 total canonical calls)
    canonical_replay_predictions = []
    for rep_idx in range(4):
        if max_calls is not None and call_idx >= max_calls:
            break

        ctx = compiler_canon.compile(base_state, base_query, equivalence_class_id="canonical_blocks")
        call_id = f"call_p_canonical_rep_{rep_idx+1:02d}"
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
        canonical_replay_predictions.append(parsed.protocol)

        k_a = evaluate_conformance_k_a(parsed.protocol, "PROTO_X7", is_valid_json=parsed.is_valid_json)

        call_spec_sha = hashlib.sha256(spec.model_dump_json().encode("utf-8")).hexdigest()
        call_rec = CallRecord(
            call_id=call_id,
            track="track_p",
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
            track="track_p",
            condition_id=f"canonical_rep_{rep_idx+1:02d}",
            station="VELORA",
            expected_protocol="PROTO_X7",
            predicted_protocol=parsed.protocol,
            reported_support_evidence=parsed.reported_support_evidence,
            independence_status=parsed.independence_status,
            perceived_independent_roots=parsed.perceived_independent_roots,
            is_valid_json=1 if parsed.is_valid_json else 0,
            k_a=k_a,
            prompt_hash=hashlib.sha256(ctx.prompt.encode("utf-8")).hexdigest(),
            state_hash=ctx.state_hash,
            compiler_pipeline="TOPOLOGY_AWARE_GROUPING",
        )

        persist_round4_call_and_evaluation(db_path, call_rec, eval_rec)
        evaluations.append(eval_rec)
        call_idx += 1

    panel_metrics = evaluate_track_p_panel(raw_predictions, canonical_replay_predictions=canonical_replay_predictions)
    return evaluations, panel_metrics
