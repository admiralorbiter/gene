"""Track C Runner: Epistemic Context Compiler Conformance Benchmark (32 Calls).

Evaluates 4 compiler pipelines x 4 test ecologies x 2 stations.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any
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
    ConformanceEvaluation,
    evaluate_conformance_k_a,
    evaluate_conformance_k_l,
    evaluate_conformance_k_s,
    init_round4_db,
    parse_round4_model_output,
    persist_round4_evaluation,
)


def build_track_c_ecology(station: str, eco_type: str) -> tuple[EpistemicState, QueryContract, str, list[str], int | None]:
    """Construct specific test ecology for Track C.
    
    Returns: (state, query, expected_protocol, gold_paths, expected_roots)
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
        output_schema_json=f'{{"station": "{station}", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "reported_support_path": "path_AB|path_DE|none", "perceived_independent_roots": 1, "evidence_status": "sufficient|insufficient"}}',
    )

    if eco_type == "eco_entitled":
        premises = {
            "occ_A": PremiseNode(occurrence_id="occ_A", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_B": PremiseNode(occurrence_id="occ_B", semantic_claim_id=f"claim_{st_lower}_nerin_reports_s1", predicate="reports_to", subject="Nerin", entity=station, target_value="sector lead S1", root_ids=["R1"]),
            "occ_D": PremiseNode(occurrence_id="occ_D", semantic_claim_id=f"claim_{st_lower}_vael_sector_lead", predicate="has_role", subject="Vael", entity=station, role="sector_lead", root_ids=["R2"]),
            "occ_E": PremiseNode(occurrence_id="occ_E", semantic_claim_id=f"claim_{st_lower}_vael_reports_s2", predicate="reports_to", subject="Vael", entity=station, target_value="sector lead S2", root_ids=["R2"]),
        }
        envs = [
            SupportEnvironment(path_id="path_AB", rule_id="rule_1", required_semantic_claim_ids=[f"claim_{st_lower}_nerin_manager", f"claim_{st_lower}_nerin_reports_s1"]),
            SupportEnvironment(path_id="path_DE", rule_id="rule_2", required_semantic_claim_ids=[f"claim_{st_lower}_vael_sector_lead", f"claim_{st_lower}_vael_reports_s2"]),
        ]
        state = EpistemicState(premises=premises, rules=rules, support_environments=envs)
        EpistemicRenderer.render_state(state)
        return state, query, "PROTO_X7", ["path_AB", "path_DE"], None

    elif eco_type == "eco_pruned":
        premises = {
            "occ_A": PremiseNode(occurrence_id="occ_A", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_B": PremiseNode(occurrence_id="occ_B", semantic_claim_id=f"claim_{st_lower}_nerin_reports_s1", predicate="reports_to", subject="Nerin", entity=station, target_value="sector lead S1", root_ids=["R1"]),
        }
        envs = [
            SupportEnvironment(path_id="path_AB", rule_id="rule_1", required_semantic_claim_ids=[f"claim_{st_lower}_nerin_manager", f"claim_{st_lower}_nerin_reports_s1"]),
        ]
        state = EpistemicState(premises=premises, rules=rules, support_environments=envs)
        EpistemicRenderer.render_state(state)
        return state, query, "PROTO_X7", ["path_AB"], None

    elif eco_type == "eco_4copy":
        premises = {
            "occ_A1": PremiseNode(occurrence_id="occ_A1", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_A2": PremiseNode(occurrence_id="occ_A2", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_A3": PremiseNode(occurrence_id="occ_A3", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_A4": PremiseNode(occurrence_id="occ_A4", semantic_claim_id=f"claim_{st_lower}_nerin_manager", predicate="has_role", subject="Nerin", entity=station, role="manager", root_ids=["R1"]),
            "occ_B": PremiseNode(occurrence_id="occ_B", semantic_claim_id=f"claim_{st_lower}_nerin_reports_s1", predicate="reports_to", subject="Nerin", entity=station, target_value="sector lead S1", root_ids=["R1"]),
        }
        envs = [
            SupportEnvironment(path_id="path_AB", rule_id="rule_1", required_semantic_claim_ids=[f"claim_{st_lower}_nerin_manager", f"claim_{st_lower}_nerin_reports_s1"]),
        ]
        state = EpistemicState(premises=premises, rules=rules, support_environments=envs)
        EpistemicRenderer.render_state(state)
        return state, query, "PROTO_X7", ["path_AB"], 1

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


def run_track_c(client: Any, db_path: str, max_calls: int | None = None) -> list[ConformanceEvaluation]:
    """Execute Track C experimental design."""
    init_round4_db(db_path)
    stations = ["VELORA", "KESTREL"]
    ecologies = ["eco_entitled", "eco_pruned", "eco_4copy", "eco_unentitled"]
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
                resp_text = client.chat(messages=[{"role": "user", "content": ctx.prompt}], model="gemma3:12b")
                parsed = parse_round4_model_output(resp_text)

                k_a = evaluate_conformance_k_a(parsed.protocol, expected_proto)
                k_s = evaluate_conformance_k_s(parsed.reported_support_path, gold_paths) if gold_paths else None
                k_l = evaluate_conformance_k_l(parsed.perceived_independent_roots, expected_roots) if expected_roots is not None else None

                eval_record = ConformanceEvaluation(
                    call_id=call_id,
                    track="track_c",
                    condition_id=f"{pipeline.value}_{eco_type}_{station}",
                    station=station,
                    expected_protocol=expected_proto,
                    predicted_protocol=parsed.protocol,
                    k_a=k_a,
                    k_s=k_s,
                    k_l=k_l,
                    prompt_hash=hashlib.sha256(ctx.prompt.encode("utf-8")).hexdigest(),
                    state_hash=ctx.state_hash,
                    compiler_pipeline=pipeline.value,
                    raw_output=resp_text,
                )
                persist_round4_evaluation(db_path, eval_record)
                evaluations.append(eval_record)
                call_idx += 1

    return evaluations
