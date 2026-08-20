"""Track G2: Clean Non-Destructive Support Immunity Runner.

Evaluates support-aware governance vs naive lineage quarantine across unrevoked baseline,
single independent path revocation, and shared root revocation.
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


def build_track_g2_prompt(station: str, arm: str, geometry: str) -> tuple[str, list[str], str]:
    """Clean G2 prompt with zero auxiliary count leaks and explicit unrevoked baseline."""
    rules = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, S1) AND authorized(S1) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. sector_lead({station}, person) AND reports_to(person, S2) AND authorized(S2) -> uses_protocol({station}, PROTO_X7)\n"
        "3. If an authority is REVOKED or UNAUTHORIZED, all deductions passing through that authority are invalid.\n"
        "4. If all supporting paths are revoked, protocol is UNKNOWN."
    )

    if arm == "unrevoked_baseline":
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            "- MEM_03: STATUS: Authority of S1 is VALID and ACTIVE.",
            f"- MEM_04: Vael is sector lead of {station}.",
            "- MEM_05: Vael directly reports to S2.",
            "- MEM_06: STATUS: Authority of S2 is VALID and ACTIVE.",
        ]
        expected = "PROTO_X7"
    elif arm == "revoke_path1":
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            "- MEM_03: STATUS: Authority of S1 is REVOKED and INVALID.",
            f"- MEM_04: Vael is sector lead of {station}.",
            "- MEM_05: Vael directly reports to S2.",
            "- MEM_06: STATUS: Authority of S2 is VALID and ACTIVE.",
        ]
        expected = "PROTO_X7" if geometry == "independent" else "UNKNOWN"
    elif arm == "revoke_shared":
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            "- MEM_03: STATUS: Authority of S1 is REVOKED and INVALID.",
            f"- MEM_04: Vael is sector lead of {station}.",
            "- MEM_05: Vael directly reports to S1.",
            "- MEM_06: STATUS: Authority of S1 is REVOKED and INVALID.",
        ]
        expected = "UNKNOWN"
    else:
        raise ValueError(f"Unknown arm: {arm}")

    prompt = (
        f"{rules}\n\n"
        "RETRIEVED EVIDENCE:\n"
        + "\n".join(memories)
        + f"\n\nQUESTION: What security protocol is currently authorized for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
    )

    forbidden = ["PROTO_X7", "PROTO_Q2"]
    return prompt, forbidden, expected


def run_track_g2_live(
    db_path: Path = Path("runs/explore_round3/track_g2_immunity.db"),
    max_calls: int = 18,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track G2 clean non-destructive immunity panel."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_g2_non_destructive_immunity",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    stations = ["VELORA", "KESTREL"]
    test_arms = [
        ("unrevoked_baseline", "independent"),
        ("revoke_path1", "independent"),
        ("revoke_shared", "shared"),
    ]

    calls_spent = 0
    results = []

    for rep in range(1, 4):
        for st in stations:
            for arm, geom in test_arms:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_g2_{st.lower()}_{arm}_{geom}_rep{rep}"
                prompt, forbidden, expected = build_track_g2_prompt(st, arm, geom)

                spec = CallSpec(
                    model_name="gemma3:12b",
                    system_prompt="You are a precise logical reasoning assistant. Return strictly valid JSON.",
                    user_prompt=prompt,
                    temperature=0.0,
                    seed=42 + rep,
                )

                rec = harness.execute_call(
                    call_id=call_id,
                    spec=spec,
                    forbidden_schema_leaks=forbidden,
                    metadata={
                        "station": st,
                        "arm": arm,
                        "geometry": geom,
                        "rep": rep,
                        "expected": expected,
                    },
                    fail_on_lexical_leak=True,
                )

                is_correct = (rec.emitted_claim == expected)
                phenotype = "ACTIVE_SURVIVING" if rec.emitted_claim == "PROTO_X7" else "INACTIVE_COLLAPSED"

                # Contemporaneous evaluation logging
                harness.record_evaluation(
                    call_id=call_id,
                    canonical_status="TRUE" if expected == "PROTO_X7" else "UNKNOWN",
                    local_status="TRUE" if is_correct else "FALSE",
                    phenotype=phenotype,
                    is_compliant=True,
                    oracle_details={
                        "arm": arm,
                        "geometry": geom,
                        "expected": expected,
                        "emitted": rec.emitted_claim,
                        "is_correct": is_correct,
                    },
                )

                results.append({
                    "call_id": call_id,
                    "station": st,
                    "arm": arm,
                    "geometry": geom,
                    "emitted": rec.emitted_claim,
                    "expected": expected,
                    "is_correct": is_correct,
                })
                print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (expected={expected}, correct={is_correct})", flush=True)
                calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_g2_immunity.db")
    print("Running Track G2: Clean Non-Destructive Support Immunity (18 calls on gemma3:12b)...", flush=True)
    res = run_track_g2_live(db, max_calls=18)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
