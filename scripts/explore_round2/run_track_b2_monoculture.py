"""Track B2: Monoculture Hardening Runner.

Evaluates whether language models spontaneously prioritize independent ancestral roots
over raw repetition under strictly matched document counts (N=5) and opaque root IDs.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd()))

import json
from typing import Any

from gene.experiments.exploration_harness import ExplorationHarness
from gene.ollama_client import CallSpec, OllamaClient


def build_track_b2_prompt(
    station: str,
    condition: str,
) -> tuple[str, list[str]]:
    """Build strictly controlled prompt for Track B2."""
    docs = []
    if condition == "concur_X":
        # 3 X (3 roots) vs 2 Y (2 roots)
        docs = [
            f"- DOC_01: Source root_R1 states station {station} requires protocol PROTO_X.",
            f"- DOC_02: Source root_R2 states station {station} requires protocol PROTO_X.",
            f"- DOC_03: Source root_R3 states station {station} requires protocol PROTO_X.",
            f"- DOC_04: Source root_R4 states station {station} requires protocol PROTO_Y.",
            f"- DOC_05: Source root_R5 states station {station} requires protocol PROTO_Y.",
        ]
    elif condition == "conflict_roots_Y":
        # 3 X (1 root) vs 2 Y (2 roots) -> RAW favors X, ROOTS favor Y!
        docs = [
            f"- DOC_01: Source root_R1 states station {station} requires protocol PROTO_X.",
            f"- DOC_02: Citing source root_R1, field log notes station {station} requires protocol PROTO_X.",
            f"- DOC_03: Archive relay quoting source root_R1 confirms station {station} requires protocol PROTO_X.",
            f"- DOC_04: Source root_R4 states station {station} requires protocol PROTO_Y.",
            f"- DOC_05: Source root_R5 states station {station} requires protocol PROTO_Y.",
        ]
    elif condition == "concur_Y":
        # 2 X (2 roots) vs 3 Y (3 roots)
        docs = [
            f"- DOC_01: Source root_R1 states station {station} requires protocol PROTO_X.",
            f"- DOC_02: Source root_R2 states station {station} requires protocol PROTO_X.",
            f"- DOC_03: Source root_R3 states station {station} requires protocol PROTO_Y.",
            f"- DOC_04: Source root_R4 states station {station} requires protocol PROTO_Y.",
            f"- DOC_05: Source root_R5 states station {station} requires protocol PROTO_Y.",
        ]
    elif condition == "conflict_roots_X":
        # 2 X (2 roots) vs 3 Y (1 root) -> RAW favors Y, ROOTS favor X!
        docs = [
            f"- DOC_01: Source root_R1 states station {station} requires protocol PROTO_X.",
            f"- DOC_02: Source root_R2 states station {station} requires protocol PROTO_X.",
            f"- DOC_03: Source root_R3 states station {station} requires protocol PROTO_Y.",
            f"- DOC_04: Citing source root_R3, field log notes station {station} requires protocol PROTO_Y.",
            f"- DOC_05: Archive relay quoting source root_R3 confirms station {station} requires protocol PROTO_Y.",
        ]

    prompt = (
        "RETRIEVED EVIDENCE:\n"
        + "\n".join(docs)
        + f"\n\nQUESTION: Based on the retrieved evidence, which security protocol is best supported for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        '{"station": "STATION_NAME", "adjudicated_protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
    )

    forbidden = ["PROTO_X", "PROTO_Y", "root_R1", "root_R2"]
    return prompt, forbidden


def run_track_b2_live(
    db_path: Path = Path("runs/explore_round2/track_b2_monoculture.db"),
    max_calls: int = 16,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track B2 live panel."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_b2_monoculture",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    stations = ["VELORA", "KESTREL"]
    conditions = ["concur_X", "conflict_roots_Y", "concur_Y", "conflict_roots_X"]
    calls_spent = 0
    results = []

    for rep in [1, 2]:
        for station in stations:
            for cond in conditions:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_b2_{station.lower()}_{cond}_rep{rep}"
                prompt, forbidden = build_track_b2_prompt(station, cond)

                spec = CallSpec(
                    model_name="gemma3:12b",
                    system_prompt="You are a precise data analysis assistant. Return strictly valid JSON.",
                    user_prompt=prompt,
                    temperature=0.0,
                    seed=100 + rep,
                )

                rec = harness.execute_call(
                    call_id=call_id,
                    spec=spec,
                    forbidden_schema_leaks=forbidden,
                    metadata={"station": station, "condition": cond, "rep": rep},
                    fail_on_lexical_leak=True,
                )

                results.append({
                    "call_id": call_id,
                    "station": station,
                    "condition": cond,
                    "adjudicated_protocol": rec.emitted_claim,
                })
                print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim}", flush=True)
                calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round2/track_b2_monoculture.db")
    print("Running Track B2: Monoculture Hardening (16 calls on gemma3:12b)...", flush=True)
    res = run_track_b2_live(db, max_calls=16)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
