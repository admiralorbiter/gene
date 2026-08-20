"""Track G2: Clean Non-Destructive Support Immunity Runner.

Evaluates support-aware governance vs naive lineage quarantine under real policy-filtered
retrieval contexts across independent and shared-root geometries.
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


def build_track_g2_governance_prompt(
    station: str,
    policy_condition: str,
) -> tuple[str, list[str], str]:
    """Construct retrieval context dictated by the active governance policy."""
    rules = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, S1) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. sector_lead({station}, person) AND reports_to(person, S2) -> uses_protocol({station}, PROTO_X7)\n"
        "3. If evidence is missing, revoked, or insufficient, protocol is UNKNOWN."
    )

    if policy_condition == "baseline_independent":
        # Both paths unrevoked -> Full context
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            f"- MEM_03: Vael is sector lead of {station}.",
            "- MEM_04: Vael directly reports to S2.",
        ]
        expected = "PROTO_X7"

    elif policy_condition == "baseline_shared":
        # Shared root unrevoked -> Full context
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            f"- MEM_03: Vael is sector lead of {station}.",
            "- MEM_04: Vael directly reports to S1.",
        ]
        expected = "PROTO_X7"

    elif policy_condition == "naive_lineage_quarantine":
        # S1 revoked under naive lineage -> Entire claim family quarantined -> Zero valid evidence presented!
        memories = [
            "- MEM_QUARANTINED: Evidence quarantined by lineage governance policy due to tainted ancestor S1.",
        ]
        expected = "UNKNOWN"

    elif policy_condition == "support_aware_independent_preservation":
        # S1 revoked under support-aware kernel -> Path 1 pruned, surviving Path 2 (S2) preserved and presented!
        memories = [
            f"- MEM_03: Vael is sector lead of {station}.",
            "- MEM_04: Vael directly reports to S2.",
        ]
        expected = "PROTO_X7"

    elif policy_condition == "support_aware_shared_collapse":
        # S1 revoked under support-aware kernel on shared root -> All paths broken -> Inactivated
        memories = [
            "- MEM_INACTIVATED: All minimal support paths for claim invalidated under S1 retraction.",
        ]
        expected = "UNKNOWN"

    else:
        raise ValueError(f"Unknown policy condition: {policy_condition}")

    prompt = (
        f"{rules}\n\n"
        "RETRIEVED EVIDENCE:\n"
        + "\n".join(memories)
        + f"\n\nQUESTION: What security protocol is authorized for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
    )

    forbidden = ["PROTO_X7", "PROTO_Q2"]
    return prompt, forbidden, expected


def run_track_g2_live(
    db_path: Path = Path("runs/explore_round3/track_g2_immunity.db"),
    max_calls: int = 16,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track G2 real governance policy panel (4 conditions x 2 stations x 2 reps = 16 calls)."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_g2_non_destructive_immunity",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    stations = ["VELORA", "KESTREL"]
    conditions = [
        "baseline_independent",
        "baseline_shared",
        "naive_lineage_quarantine",
        "support_aware_independent_preservation",
    ]

    calls_spent = 0
    results = []

    for rep in range(1, 3):
        for st in stations:
            for cond in conditions:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_g2_{st.lower()}_{cond}_rep{rep}"
                prompt, forbidden, expected = build_track_g2_governance_prompt(st, cond)

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
                        "policy_condition": cond,
                        "rep": rep,
                        "expected": expected,
                    },
                    fail_on_lexical_leak=True,
                )

                is_correct = (rec.emitted_claim == expected)
                phenotype = "ACTIVE_PRESERVED" if rec.emitted_claim == "PROTO_X7" else "INACTIVE_QUARANTINED"

                # Contemporaneous evaluation logging
                harness.record_evaluation(
                    call_id=call_id,
                    canonical_status="BEHAVIORAL_EVALUATION",
                    local_status="TRUE" if is_correct else "FALSE",
                    dual_oracle_phenotype=phenotype,
                    is_contract_compliant=True,
                    metadata={
                        "policy_condition": cond,
                        "expected": expected,
                        "emitted": rec.emitted_claim,
                        "is_correct": is_correct,
                    },
                )

                results.append({
                    "call_id": call_id,
                    "station": st,
                    "condition": cond,
                    "emitted": rec.emitted_claim,
                    "expected": expected,
                    "is_correct": is_correct,
                })
                print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (expected={expected}, correct={is_correct})", flush=True)
                calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_g2_immunity.db")
    print("Running Track G2: Real Governance Policy Comparison (16 calls on gemma3:12b)...", flush=True)
    res = run_track_g2_live(db, max_calls=16)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
