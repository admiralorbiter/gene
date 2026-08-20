"""Track S: Support Acquisition from Observable Traces Runner.

Extracts minimal epistemic support environments S_F(c) from runtime execution traces
and compares them with live neural outputs across 8 validation calls.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd()))

import json
from typing import Any

from gene.experiments.exploration_harness import ExplorationHarness
from gene.experiments.trace_support_compiler import ExecutionTraceNode, TraceSupportCompiler
from gene.ollama_client import CallSpec, OllamaClient


def run_track_s_live(
    db_path: Path = Path("runs/explore_round3/track_s_acquisition.db"),
    max_calls: int = 8,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track S trace compiler verification panel."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_s_support_acquisition",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    compiler = TraceSupportCompiler()
    # Build trace DAG
    compiler.add_node(ExecutionTraceNode(node_id="fact_A", claim_type="founder", claim_value="KIRA", is_root_premise=True))
    compiler.add_node(ExecutionTraceNode(node_id="fact_B", claim_type="assignment", claim_value="SEC_LEAD", is_root_premise=True))
    compiler.add_node(ExecutionTraceNode(node_id="fact_D", claim_type="founder", claim_value="VALEN", is_root_premise=True))
    compiler.add_node(ExecutionTraceNode(node_id="fact_E", claim_type="assignment", claim_value="DIRECTOR", is_root_premise=True))
    compiler.add_node(ExecutionTraceNode(node_id="lemma_P1", claim_type="protocol", claim_value="PROTO_X7", parent_ids=["fact_A", "fact_B"]))
    compiler.add_node(ExecutionTraceNode(node_id="lemma_P2", claim_type="protocol", claim_value="PROTO_X7", parent_ids=["fact_D", "fact_E"]))
    compiler.add_node(ExecutionTraceNode(node_id="target_C", claim_type="protocol", claim_value="PROTO_X7", parent_ids=["lemma_P1"]))

    extracted_s = compiler.compile_minimal_support_environments("target_C")
    print(f"Mechanically compiled S_F(target_C) = {extracted_s}", flush=True)

    stations = ["VELORA", "KESTREL"]
    calls_spent = 0
    results = []

    for st in stations:
        for case in ["single_path", "recombinant_path", "missing_premise", "conflicting_root"]:
            if calls_spent >= max_calls:
                break

            call_id = f"call_track_s_{st.lower()}_{case}"
            
            rules = (
                "RULES:\n"
                f"1. manager({st}, person) AND reports_to(person, KIRA) -> uses_protocol({st}, PROTO_X7)\n"
                f"2. sector_lead({st}, person) AND reports_to(person, VALEN) -> uses_protocol({st}, PROTO_X7)\n"
                "3. If evidence is insufficient, protocol is UNKNOWN."
            )

            if case == "single_path":
                mems = [f"- MEM_01: Nerin is manager of {st}.", "- MEM_02: Nerin directly reports to KIRA."]
                expected = "PROTO_X7"
            elif case == "recombinant_path":
                mems = [
                    f"- MEM_01: Nerin is manager of {st}.",
                    "- MEM_02: Nerin directly reports to KIRA.",
                    f"- MEM_03: Vael is sector lead of {st}.",
                    "- MEM_04: Vael directly reports to VALEN.",
                ]
                expected = "PROTO_X7"
            elif case == "missing_premise":
                mems = [f"- MEM_01: Nerin is manager of {st}."]
                expected = "UNKNOWN"
            elif case == "conflicting_root":
                mems = [f"- MEM_01: Nerin is manager of {st}.", "- MEM_02: Nerin directly reports to TAL."]
                expected = "UNKNOWN"

            prompt = (
                f"{rules}\n\n"
                "RETRIEVED EVIDENCE:\n"
                + "\n".join(mems)
                + f"\n\nQUESTION: What security protocol is authorized for station {st}?\n"
                "Return strictly JSON matching this schema:\n"
                '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
            )

            forbidden = ["PROTO_X7", "PROTO_Q2"]

            spec = CallSpec(
                model_name="gemma3:12b",
                system_prompt="You are a precise logical reasoning assistant. Return strictly valid JSON.",
                user_prompt=prompt,
                temperature=0.0,
                seed=42,
            )

            rec = harness.execute_call(
                call_id=call_id,
                spec=spec,
                forbidden_schema_leaks=forbidden,
                metadata={"station": st, "case": case, "expected": expected},
                fail_on_lexical_leak=True,
            )

            is_correct = (rec.emitted_claim == expected)
            phenotype = "ACTIVE_CONCORDANT" if is_correct else "DISCORDANT"

            # Contemporaneous evaluation logging
            harness.record_evaluation(
                call_id=call_id,
                canonical_status="TRUE" if expected == "PROTO_X7" else "UNKNOWN",
                local_status="TRUE" if is_correct else "FALSE",
                phenotype=phenotype,
                is_compliant=True,
                oracle_details={"case": case, "expected": expected, "emitted": rec.emitted_claim, "is_correct": is_correct},
            )

            results.append({
                "call_id": call_id,
                "station": st,
                "case": case,
                "emitted": rec.emitted_claim,
                "expected": expected,
                "is_correct": is_correct,
            })
            print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (expected={expected}, correct={is_correct})", flush=True)
            calls_spent += 1

    return {"calls_spent": calls_spent, "results": results, "extracted_support": extracted_s}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_s_acquisition.db")
    print("Running Track S: Support Acquisition from Observable Traces (8 calls on gemma3:12b)...", flush=True)
    res = run_track_s_live(db, max_calls=8)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
