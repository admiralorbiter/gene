"""Track L: Independence Laundering Runner.

Evaluates how downstream models adjudicate consensus across progressive reproduction
stages (G0 -> G1 -> G2 -> G3) where single-source provenance is progressively laundered.
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
    max_calls: int = 16,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track L laundering panel."""
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
                    + f"\n\nQUESTION: Based on the retrieved evidence, how many independent primary sources support the claim that station {st} uses {proto}, and is the evidence sufficient to confirm authorization?\n"
                    "Return strictly JSON matching this schema:\n"
                    '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "estimated_independent_sources": "INTEGER", "evidence_status": "sufficient|insufficient"}'
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
                        "expected_perceived": gen_stage.perceived_root_count,
                    },
                    fail_on_lexical_leak=True,
                )

                # Contemporaneous evaluation logging
                harness.record_evaluation(
                    call_id=call_id,
                    canonical_status="TRUE",
                    local_status="TRUE",
                    phenotype=f"STAGE_{gen_stage.generation}_{rec.emitted_claim}",
                    is_compliant=True,
                    oracle_details={
                        "generation": gen_stage.generation,
                        "stage_name": gen_stage.stage_name,
                        "true_roots": gen_stage.true_root_count,
                        "emitted": rec.emitted_claim,
                    },
                )

                results.append({
                    "call_id": call_id,
                    "station": st,
                    "protocol": proto,
                    "stage_name": gen_stage.stage_name,
                    "generation": gen_stage.generation,
                    "emitted": rec.emitted_claim,
                })
                print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (gen={gen_stage.generation})", flush=True)
                calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_l_laundering.db")
    print("Running Track L: Independence Laundering (16 calls on gemma3:12b)...", flush=True)
    res = run_track_l_live(db, max_calls=16)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
