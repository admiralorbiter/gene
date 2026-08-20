"""Track G: Multi-Justification & Epistemic Recombination Runner.

Evaluates whether Gemma appropriately exploits surviving alternative support paths
when one ancestral derivation path is discredited.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gene.experiments.exploration_harness import ExplorationHarness
from gene.ollama_client import CallSpec, OllamaClient


def build_track_g_prompt(
    station: str,
    condition: str,  # 'independent_survival' vs 'shared_collapse'
    target_protocol: str = "PROTO_X7",
) -> tuple[str, list[str]]:
    """Build strictly un-confounded prompt for multi-justification survival test."""
    rules_text = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, S1) AND authorized(S1) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. sector_lead({station}, person) AND reports_to(person, S2) AND authorized(S2) -> uses_protocol({station}, PROTO_X7)\n"
        "3. If an authority is REVOKED or UNAUTHORIZED, all deductions passing through that authority are invalid.\n"
        "4. If evidence is insufficient or all supporting paths are revoked, protocol is UNKNOWN."
    )

    if condition == "independent_survival":
        # S1 revoked, S2 authorized -> Path 2 survives!
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            "- MEM_03: STATUS UPDATE: Authority of S1 is REVOKED and INVALID.",
            f"- MEM_04: Vael is sector lead of {station}.",
            "- MEM_05: Vael directly reports to S2.",
            "- MEM_06: STATUS UPDATE: Authority of S2 is VALID and CONFIRMED.",
        ]
    else:  # 'shared_collapse'
        # Both paths depend on S1, which is revoked -> 0 surviving paths!
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            "- MEM_03: STATUS UPDATE: Authority of S1 is REVOKED and INVALID.",
            f"- MEM_04: Vael is sector lead of {station}.",
            "- MEM_05: Vael directly reports to S1.",
            "- MEM_06: STATUS UPDATE: Authority of S1 is REVOKED and INVALID.",
        ]

    prompt = (
        f"{rules_text}\n\n"
        "RETRIEVED EVIDENCE:\n"
        + "\n".join(memories)
        + f"\n\nQUESTION: What security protocol is currently authorized for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient", "surviving_paths_count": 0}'
    )

    # Return forbidden answer strings for pre-execution lexical leak audit
    forbidden = [target_protocol]
    return prompt, forbidden


def run_track_g_live(
    db_path: Path = Path("runs/explore_round2/track_g_multi_justification.db"),
    max_calls: int = 12,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track G live panel under ExplorationHarness."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_g_multi_justification",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    stations = ["VELORA", "KESTREL"]
    conditions = ["independent_survival", "shared_collapse"]
    calls_spent = 0
    results = []

    for rep in [1, 2, 3]:
        for station in stations:
            for cond in conditions:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_g_{station.lower()}_{cond}_rep{rep}"
                prompt, forbidden = build_track_g_prompt(station, cond)

                spec = CallSpec(
                    model_name="gemma3:12b",
                    system_prompt="You are a rigorous epistemic verification assistant. Return strictly valid JSON.",
                    user_prompt=prompt,
                    temperature=0.0,
                    seed=42 + rep,
                )

                rec = harness.execute_call(
                    call_id=call_id,
                    spec=spec,
                    forbidden_schema_leaks=forbidden,
                    metadata={"station": station, "condition": cond, "rep": rep},
                    fail_on_lexical_leak=True,
                )

                expected = "PROTO_X7" if cond == "independent_survival" else "UNKNOWN"
                is_correct = (rec.emitted_claim == expected)

                results.append({
                    "call_id": call_id,
                    "station": station,
                    "condition": cond,
                    "emitted_claim": rec.emitted_claim,
                    "expected": expected,
                    "is_correct": is_correct,
                })
                calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}
