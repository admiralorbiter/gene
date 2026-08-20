"""Track C Runner: Epistemic Context Compiler Conformance Benchmark (32 Calls).

Evaluates 4 compiler pipelines x 4 test ecologies x 2 stations.
Uses backend-neutral evidence support reporting, exact-copy multiplication scoping, and immutable persistence.
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
from gene.experiments.context_compiler import EpistemicContextCompiler
from gene.experiments.evaluators_round4 import (
    CallRecord,
    EvaluationRecord,
    FROZEN_ROUND4_SYSTEM_PROMPT,
    evaluate_conformance_k_a,
    evaluate_conformance_k_l,
    evaluate_conformance_k_s_neutral,
    init_round4_db,
    parse_round4_model_output,
    persist_round4_call_and_evaluation,
)


def build_track_c_ecology(station: str, eco_type: str) -> tuple[EpistemicState, QueryContract, str, list[set[str]], int | None]:
    """Construct specific test ecology for Track C.
    
    Returns: (state, query, expected_protocol, gold_paths_claim_sets, expected_roots)
    """
    st_lower = station.lower()
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

    query = QueryContract(
        target_station=station,
        target_predicate="station_operates_protocol",
        query_question=f"Based on authorized rules and evidence, what protocol is authorized for station {station}?",
        allow_unknown=True,
        output_schema_json=f'{{"station": "{station}", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "reported_support_evidence": ["EVID_TAG_OR_NONE"], "independence_status": "determinable|indeterminable", "perceived_independent_roots": "INTEGER_OR_NULL", "evidence_status": "sufficient|insufficient"}}',
    )

    path_AB_claims = {f"claim_{st_lower}_nerin_manager", f"claim_{st_lower}_nerin_reports_s1"}
    path_DE_claims = {f"claim_{st_lower}_vael_sector_lead", f"claim_{st_lower}_vael_reports_s2"}

    if eco_type == "eco_entitled":
        premises = {
            "occ_A": PremiseNode(occurrence_id="occ_A", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_B": PremiseNode(occurrence_id="occ_B", semantic_claim_id=f"claim_{st_lower}_nerin_reports_s1", predicate="reports_to", subject="Nerin", entity=station, target_value="sector lead S1", root_ids=["R1"]),
            "occ_D": PremiseNode(occurrence_id="occ_D", semantic_claim_id=f"claim_{st_lower}_vael_sector_lead", predicate="has_role", subject="Vael", entity=station, role="sector_lead", root_ids=["R2"]),
            "occ_E": PremiseNode(occurrence_id="occ_E", semantic_claim_id=f"claim_{st_lower}_vael_reports_s2", predicate="reports_to", subject="Vael", entity=station, target_value="sector lead S2", root_ids=["R2"]),
        }
        envs = [
            SupportEnvironment(path_id="path_AB", rule_id="rule_1", required_semantic_claim_ids=list(path_AB_claims)),
            SupportEnvironment(path_id="path_DE", rule_id="rule_2", required_semantic_claim_ids=list(path_DE_claims)),
        ]
        state = EpistemicState(premises=premises, rules=rules, support_environments=envs)
        EpistemicRenderer.render_state(state)
        return state, query, "PROTO_X7", [path_AB_claims, path_DE_claims], None

    elif eco_type == "eco_pruned":
        premises = {
            "occ_A": PremiseNode(occurrence_id="occ_A", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_B": PremiseNode(occurrence_id="occ_B", semantic_claim_id=f"claim_{st_lower}_nerin_reports_s1", predicate="reports_to", subject="Nerin", entity=station, target_value="sector lead S1", root_ids=["R1"]),
        }
        envs = [
            SupportEnvironment(path_id="path_AB", rule_id="rule_1", required_semantic_claim_ids=list(path_AB_claims)),
        ]
        state = EpistemicState(premises=premises, rules=rules, support_environments=envs)
        EpistemicRenderer.render_state(state)
        return state, query, "PROTO_X7", [path_AB_claims], None

    elif eco_type == "eco_copy_multiplication":
        # Exact duplicate copy multiplication (4 identical copies of A under shared root R1)
        premises = {
            "occ_A1": PremiseNode(occurrence_id="occ_A1", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_A2": PremiseNode(occurrence_id="occ_A2", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_A3": PremiseNode(occurrence_id="occ_A3", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_A4": PremiseNode(occurrence_id="occ_A4", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_B": PremiseNode(occurrence_id="occ_B", semantic_claim_id=f"claim_{st_lower}_nerin_reports_s1", predicate="reports_to", subject="Nerin", entity=station, target_value="sector lead S1", root_ids=["R1"]),
        }
        envs = [
            SupportEnvironment(path_id="path_AB", rule_id="rule_1", required_semantic_claim_ids=list(path_AB_claims)),
        ]
        state = EpistemicState(premises=premises, rules=rules, support_environments=envs)
        EpistemicRenderer.render_state(state)
        return state, query, "PROTO_X7", [path_AB_claims], 1

    elif eco_type == "eco_unentitled":
        premises = {
            "occ_F": PremiseNode(occurrence_id="occ_F", semantic_claim_id=f"claim_{st_lower}_corin_duty", predicate="neutral_fact", subject="Corin", entity=station, root_ids=["R3"]),
        }
        envs = []
        state = EpistemicState(premises=premises, rules=rules, support_environments=envs)
        EpistemicRenderer.render_state(state)
        return state, query, "UNKNOWN", [], None

    else:
        raise ValueError(f"Unknown ecology type: {eco_type}")


def run_track_c(client: Any, db_path: str, max_calls: int | None = None) -> list[EvaluationRecord]:
    """Execute Track C experimental design."""
    init_round4_db(db_path)
    stations = ["VELORA", "KESTREL"]
    ecologies = ["eco_entitled", "eco_pruned", "eco_copy_multiplication", "eco_unentitled"]
    pipelines = [
        PrivilegeLevel.RAW_SERIALIZATION,
        PrivilegeLevel.TOPOLOGY_AWARE_GROUPING,
        PrivilegeLevel.GENEALOGICAL_NORMALIZATION,
        PrivilegeLevel.PROOF_CARRYING_CERTIFICATE,
    ]

    evaluations = []
    call_idx = 0

    for pipeline in pipelines:
        compiler = EpistemicContextCompiler(pipeline=pipeline)
        for eco_type in ecologies:
            for station in stations:
                if max_calls is not None and call_idx >= max_calls:
                    break

                state, query, expected_proto, gold_paths, expected_roots = build_track_c_ecology(station, eco_type)
                ctx = compiler.compile(state, query, equivalence_class_id=f"{pipeline.value}_{eco_type}")

                call_id = f"call_c_{pipeline.value}_{eco_type}_{station}"
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

                k_a = evaluate_conformance_k_a(parsed.protocol, expected_proto, is_valid_json=parsed.is_valid_json)
                if gold_paths:
                    k_s_suff, k_s_exact, excess_count = evaluate_conformance_k_s_neutral(
                        parsed.reported_support_evidence, ctx.evidence_tag_to_claim_map, gold_paths
                    )
                else:
                    k_s_suff, k_s_exact, excess_count = None, None, None

                is_det, k_l = evaluate_conformance_k_l(parsed.independence_status, parsed.perceived_independent_roots, expected_roots)

                call_spec_sha = hashlib.sha256(spec.model_dump_json().encode("utf-8")).hexdigest()
                call_rec = CallRecord(
                    call_id=call_id,
                    track="track_c",
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
                    track="track_c",
                    condition_id=f"{pipeline.value}_{eco_type}_{station}",
                    station=station,
                    expected_protocol=expected_proto,
                    predicted_protocol=parsed.protocol,
                    reported_support_evidence=parsed.reported_support_evidence,
                    independence_status=parsed.independence_status,
                    perceived_independent_roots=parsed.perceived_independent_roots,
                    is_valid_json=1 if parsed.is_valid_json else 0,
                    k_a=k_a,
                    k_s_suff=k_s_suff,
                    k_s_exact=k_s_exact,
                    excess_evidence_count=excess_count,
                    k_l=k_l,
                    prompt_hash=hashlib.sha256(ctx.prompt.encode("utf-8")).hexdigest(),
                    state_hash=ctx.state_hash,
                    compiler_pipeline=pipeline.value,
                )

                persist_round4_call_and_evaluation(db_path, call_rec, eval_rec)
                evaluations.append(eval_rec)
                call_idx += 1

    return evaluations
