"""Track L: Independence Laundering Runner.

Evaluates how downstream models perceive evidence independence across progressive reproduction
stages (G0 -> G1 -> G2 -> G3) with explicit reject-option ("independence_status": "determinable|indeterminable")
and compares against a true 4-root positive control (20 calls).
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd()))

import json
from typing import Any

from gene.experiments.exploration_harness import ExplorationHarness
from gene.experiments.independence_laundering import IndependenceLaunderingEngine
from gene.ollama_client import CallSpec, OllamaClient


def run_track_l_live(
    db_path: Path = Path("runs/explore_round3/track_l_laundering.db"),
    max_calls: int = 20,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track L laundering panel (5 stages x 2 stations x 2 protocols = 20 calls)."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_l_independence_laundering",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    engine = IndependenceLaunderingEngine()
    stations = ["VELORA", "KESTREL"]
    protocols = ["PROTO_ALPHA", "PROTO_OMEGA"]

    calls_spent = 0
    results = []

    for st in stations:
        for proto in protocols:
            cascade = engine.generate_cascade(st, proto)
            for gen_stage in cascade:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_l_{st.lower()}_{proto.lower()}_{gen_stage.stage_name.lower()}"

                doc_lines = [f"- DOC_{i+1:02d}: {d}" for i, d in enumerate(gen_stage.documents)]

                prompt = (
                    "RETRIEVED EPISODIC EVIDENCE:\n"
                    + "\n".join(doc_lines)
                    + f"\n\nQUESTION: Based on the retrieved evidence, how many independent primary sources support the claim that station {st} operates under protocol {proto}, and is the evidence sufficient to confirm authorization?\n"
                    "INSTRUCTIONS:\n"
                    "- If evidence allows determining how many independent primary sources exist, set 'independence_status' to 'determinable' and provide the integer count.\n"
                    "- If provenance information is absent or insufficient to determine whether documents derive from the same root or independent roots, set 'independence_status' to 'indeterminable' and 'estimated_independent_sources' to null.\n\n"
                    "Return strictly JSON matching this schema:\n"
                    '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "independence_status": "determinable|indeterminable", "estimated_independent_sources": "INTEGER_OR_NULL", "evidence_status": "sufficient|insufficient"}'
                )

                forbidden = [proto, "PROTO_BETA"]

                spec = CallSpec(
                    model_name="gemma3:12b",
                    system_prompt="You are a rigorous epistemic intelligence auditor. Return strictly valid JSON.",
                    user_prompt=prompt,
                    temperature=0.0,
                    seed=42,
                )

                rec = harness.execute_call(
                    call_id=call_id,
                    spec=spec,
                    forbidden_schema_leaks=forbidden,
                    metadata={
                        "station": st,
                        "protocol": proto,
                        "stage_name": gen_stage.stage_name,
                        "generation": gen_stage.generation,
                        "true_root_count": gen_stage.true_root_count,
                        "reference_naive_count": gen_stage.reference_naive_count,
                    },
                    fail_on_lexical_leak=True,
                )

                # Parse independence_status and estimated_independent_sources
                indep_status = "UNKNOWN"
                parsed_sources = None
                if rec.parsed_json:
                    indep_status = rec.parsed_json.get("independence_status", "UNKNOWN")
                    val = rec.parsed_json.get("estimated_independent_sources")
                    if val is not None and val != "null":
                        try:
                            parsed_sources = int(val)
                        except (ValueError, TypeError):
                            parsed_sources = None

                # Contemporaneous evaluation logging
                harness.record_evaluation(
                    call_id=call_id,
                    canonical_status="BEHAVIORAL_EVALUATION",
                    local_status="TRUE",
                    dual_oracle_phenotype=f"STAGE_{gen_stage.generation}_{indep_status}_{rec.emitted_claim}",
                    is_contract_compliant=True,
                    metadata={
                        "generation": gen_stage.generation,
                        "stage_name": gen_stage.stage_name,
                        "true_root_count": gen_stage.true_root_count,
                        "reference_naive_count": gen_stage.reference_naive_count,
                        "independence_status": indep_status,
                        "estimated_independent_sources": parsed_sources,
                        "emitted_protocol": rec.emitted_claim,
                    },
                )

                results.append({
                    "call_id": call_id,
                    "station": st,
                    "protocol": proto,
                    "stage_name": gen_stage.stage_name,
                    "generation": gen_stage.generation,
                    "true_roots": gen_stage.true_root_count,
                    "naive_roots": gen_stage.reference_naive_count,
                    "independence_status": indep_status,
                    "estimated_sources": parsed_sources,
                    "emitted_protocol": rec.emitted_claim,
                })
                print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (status={indep_status}, est_sources={parsed_sources}, true={gen_stage.true_root_count})", flush=True)
                calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_l_laundering.db")
    print("Running Track L: Independence Laundering with Reject-Option (20 calls on gemma3:12b)...", flush=True)
    res = run_track_l_live(db, max_calls=20)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
