"""Track M Runner: Support-Preserving Monotonicity & Fragility (32 Calls).

Evaluates 2 chains (AB origin, DE origin) x 2 insertion directions (append, prepend) x 4 steps x 2 stations.
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
    init_round4_db,
    parse_round4_model_output,
    persist_round4_evaluation,
)


def build_track_m_base(station: str) -> tuple[EpistemicState, QueryContract]:
    """Construct station-specific baseline epistemic state."""
    st_lower = station.lower()
    premises = {
        "occ_A": PremiseNode(
            occurrence_id="occ_A",
            semantic_claim_id=f"claim_{st_lower}_nerin_manager",
            predicate="has_role",
            subject="Nerin",
            entity=station,
            role="manager",
            root_ids=["R1"],
        ),
        "occ_B": PremiseNode(
            occurrence_id="occ_B",
            semantic_claim_id=f"claim_{st_lower}_nerin_reports_s1",
            predicate="reports_to",
            subject="Nerin",
            entity=station,
            target_value="sector lead S1",
            root_ids=["R1"],
        ),
        "occ_D": PremiseNode(
            occurrence_id="occ_D",
            semantic_claim_id=f"claim_{st_lower}_vael_sector_lead",
            predicate="has_role",
            subject="Vael",
            entity=station,
            role="sector_lead",
            root_ids=["R2"],
        ),
        "occ_E": PremiseNode(
            occurrence_id="occ_E",
            semantic_claim_id=f"claim_{st_lower}_vael_reports_s2",
            predicate="reports_to",
            subject="Vael",
            entity=station,
            target_value="sector lead S2",
            root_ids=["R2"],
        ),
        "occ_F": PremiseNode(
            occurrence_id="occ_F",
            semantic_claim_id=f"claim_{st_lower}_corin_duty",
            predicate="neutral_fact",
            subject="Corin",
            entity=station,
            root_ids=["R3"],
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
            required_semantic_claim_ids=[f"claim_{st_lower}_nerin_manager", f"claim_{st_lower}_nerin_reports_s1"],
        ),
        SupportEnvironment(
            path_id="path_DE",
            rule_id="rule_2",
            required_semantic_claim_ids=[f"claim_{st_lower}_vael_sector_lead", f"claim_{st_lower}_vael_reports_s2"],
        ),
    ]

    query = QueryContract(
        target_station=station,
        target_predicate="station_operates_protocol",
        query_question=f"Based on authorized rules and evidence, what protocol is authorized for station {station}?",
        allow_unknown=True,
        output_schema_json=f'{{"station": "{station}", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}}',
    )

    state = EpistemicState(
        premises=premises,
        rules=rules,
        support_environments=envs,
        invalidated_roots=[],
    )
    EpistemicRenderer.render_state(state)
    return state, query


def run_track_m(client: Any, db_path: str, max_calls: int | None = None) -> list[ConformanceEvaluation]:
    """Execute Track M experimental design."""
    init_round4_db(db_path)
    stations = ["VELORA", "KESTREL"]
    compiler = EpistemicContextCompiler(pipeline=PrivilegeLevel.RAW_SERIALIZATION)

    # Define exact sequences
    # Chain 1: AB base -> +D -> +E -> +F
    chain_1_append = [["occ_A", "occ_B"], ["occ_A", "occ_B", "occ_D"], ["occ_A", "occ_B", "occ_D", "occ_E"], ["occ_A", "occ_B", "occ_D", "occ_E", "occ_F"]]
    chain_1_prepend = [["occ_A", "occ_B"], ["occ_D", "occ_A", "occ_B"], ["occ_E", "occ_D", "occ_A", "occ_B"], ["occ_F", "occ_E", "occ_D", "occ_A", "occ_B"]]

    # Chain 2: DE base -> +A -> +B -> +F
    chain_2_append = [["occ_D", "occ_E"], ["occ_D", "occ_E", "occ_A"], ["occ_D", "occ_E", "occ_A", "occ_B"], ["occ_D", "occ_E", "occ_A", "occ_B", "occ_F"]]
    chain_2_prepend = [["occ_D", "occ_E"], ["occ_A", "occ_D", "occ_E"], ["occ_B", "occ_A", "occ_D", "occ_E"], ["occ_F", "occ_B", "occ_A", "occ_D", "occ_E"]]

    chains = [
        ("chain_1_append", chain_1_append),
        ("chain_1_prepend", chain_1_prepend),
        ("chain_2_append", chain_2_append),
        ("chain_2_prepend", chain_2_prepend),
    ]

    evaluations = []
    call_idx = 0

    for station in stations:
        base_state, base_query = build_track_m_base(station)
        for chain_name, step_list in chains:
            for step_idx, occ_order in enumerate(step_list):
                if max_calls is not None and call_idx >= max_calls:
                    break

                sub_state = base_state.subselect_occurrences(occ_order)
                ctx = compiler.compile(sub_state, base_query, occurrence_order=occ_order, equivalence_class_id=f"{chain_name}_step_{step_idx}")

                call_id = f"call_m_{station}_{chain_name}_step_{step_idx}"
                resp_text = client.chat(messages=[{"role": "user", "content": ctx.prompt}], model="gemma3:12b")
                parsed = parse_round4_model_output(resp_text)

                k_a = evaluate_conformance_k_a(parsed.protocol, "PROTO_X7")
                k_mono = 1 if parsed.protocol == "PROTO_X7" else 0

                eval_record = ConformanceEvaluation(
                    call_id=call_id,
                    track="track_m",
                    condition_id=f"{station}_{chain_name}_step_{step_idx}",
                    station=station,
                    expected_protocol="PROTO_X7",
                    predicted_protocol=parsed.protocol,
                    k_a=k_a,
                    k_mono=k_mono,
                    prompt_hash=hashlib.sha256(ctx.prompt.encode("utf-8")).hexdigest(),
                    state_hash=ctx.state_hash,
                    compiler_pipeline="RAW_SERIALIZATION",
                    raw_output=resp_text,
                )
                persist_round4_evaluation(db_path, eval_record)
                evaluations.append(eval_record)
                call_idx += 1

    return evaluations
