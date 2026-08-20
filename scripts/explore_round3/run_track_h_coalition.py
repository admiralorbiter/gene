"""Track H: Coalition Causality & Overdetermination Runner.

Exhaustively evaluates single-parent vs coalition knockouts across parent subsets
to construct the empirical causal support lattice S_C(c) and contrast it against S_F(c).
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd()))

import json
from typing import Any

from gene.experiments.coalition_causality import CoalitionCausalityEngine
from gene.experiments.exploration_harness import ExplorationHarness
from gene.ollama_client import CallSpec, OllamaClient


def build_track_h_prompt(
    station: str,
    geometry: str,
    knocked_out: set[str],
) -> tuple[str, list[str], str]:
    """Construct causal intervention prompt across parent subsets."""
    rules = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, S1) AND authorized(S1) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. sector_lead({station}, person) AND reports_to(person, S2) AND authorized(S2) -> uses_protocol({station}, PROTO_X7)\n"
        "3. If an authority is REVOKED or UNAUTHORIZED, all deductions passing through that authority are invalid.\n"
        "4. If all supporting paths are revoked, protocol is UNKNOWN."
    )

    # Geometry 1: Single Path (A: manager, B: S1)
    if geometry == "single_path":
        memories = []
        if "A" not in knocked_out:
            memories.append(f"- MEM_01: Nerin is manager of {station}.")
        if "B" not in knocked_out:
            memories.append("- MEM_02: Nerin directly reports to S1.")
            memories.append("- MEM_03: STATUS: Authority of S1 is VALID and ACTIVE.")
        else:
            memories.append("- MEM_02: Nerin directly reports to S1.")
            memories.append("- MEM_03: STATUS: Authority of S1 is REVOKED and INVALID.")
        
        expected = "PROTO_X7" if len(knocked_out) == 0 else "UNKNOWN"

    # Geometry 2: Redundant Independent (A: manager, B: S1, D: lead, E: S2)
    elif geometry == "redundant_independent":
        memories = []
        # Path 1 (A, B)
        if "A" not in knocked_out:
            memories.append(f"- MEM_01: Nerin is manager of {station}.")
        if "B" not in knocked_out:
            memories.append("- MEM_02: Nerin directly reports to S1.")
            memories.append("- MEM_03: STATUS: Authority of S1 is VALID and ACTIVE.")
        else:
            memories.append("- MEM_02: Nerin directly reports to S1.")
            memories.append("- MEM_03: STATUS: Authority of S1 is REVOKED and INVALID.")

        # Path 2 (D, E)
        if "D" not in knocked_out:
            memories.append(f"- MEM_04: Vael is sector lead of {station}.")
        if "E" not in knocked_out:
            memories.append("- MEM_05: Vael directly reports to S2.")
            memories.append("- MEM_06: STATUS: Authority of S2 is VALID and ACTIVE.")
        else:
            memories.append("- MEM_05: Vael directly reports to S2.")
            memories.append("- MEM_06: STATUS: Authority of S2 is REVOKED and INVALID.")

        path1_valid = ("A" not in knocked_out) and ("B" not in knocked_out)
        path2_valid = ("D" not in knocked_out) and ("E" not in knocked_out)
        expected = "PROTO_X7" if (path1_valid or path2_valid) else "UNKNOWN"

    # Geometry 3: Shared Root (A: manager, X: S1, Y: S1)
    elif geometry == "shared_root":
        memories = []
        if "A" not in knocked_out:
            memories.append(f"- MEM_01: Nerin is manager of {station}.")
        if "X" not in knocked_out:
            memories.append("- MEM_02: Nerin directly reports to S1.")
        if "Y" not in knocked_out:
            memories.append("- MEM_03: Operations log confirms S1 oversees sector operations.")
        
        # In shared root, S1 validity governs both
        if "A" in knocked_out or "X" in knocked_out or "Y" in knocked_out:
            memories.append("- MEM_04: STATUS: Authority of S1 is REVOKED and INVALID.")
            expected = "UNKNOWN"
        else:
            memories.append("- MEM_04: STATUS: Authority of S1 is VALID and ACTIVE.")
            expected = "PROTO_X7"
    else:
        raise ValueError(f"Unknown geometry {geometry}")

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


def run_track_h_live(
    db_path: Path = Path("runs/explore_round3/track_h_coalition.db"),
    max_calls: int = 18,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track H coalition causality panel."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_h_coalition_causality",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    engine = CoalitionCausalityEngine()
    stations = ["VELORA", "KESTREL"]
    
    # Key test points on redundant_independent lattice:
    # 1. 0 knockouts (Baseline)
    # 2. Single knockouts: {A}, {D}
    # 3. Coalition knockouts: {A, D}, {A, E}, {B, D}
    intervention_points = [
        ("redundant_independent", set(), "baseline"),
        ("redundant_independent", {"A"}, "single_A"),
        ("redundant_independent", {"D"}, "single_D"),
        ("redundant_independent", {"A", "D"}, "coalition_AD"),
        ("redundant_independent", {"A", "E"}, "coalition_AE"),
        ("redundant_independent", {"B", "D"}, "coalition_BD"),
        ("single_path", set(), "single_baseline"),
        ("single_path", {"A"}, "single_knockout_A"),
        ("shared_root", {"A"}, "shared_root_knockout_A"),
    ]

    calls_spent = 0
    results = []

    for st in stations:
        for geom, knocked_out, label in intervention_points:
            if calls_spent >= max_calls:
                break

            call_id = f"call_track_h_{st.lower()}_{geom}_{label}"
            prompt, forbidden, expected = build_track_h_prompt(st, geom, knocked_out)

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
                metadata={
                    "station": st,
                    "geometry": geom,
                    "knocked_out": list(knocked_out),
                    "label": label,
                    "expected": expected,
                },
                fail_on_lexical_leak=True,
            )

            is_correct = (rec.emitted_claim == expected)
            phenotype = "ACTIVE_CONCORDANT" if is_correct else "DISCORDANT_OR_MASKED"

            # Contemporaneous evaluation logging
            harness.record_evaluation(
                call_id=call_id,
                canonical_status="TRUE" if expected == "PROTO_X7" else "UNKNOWN",
                local_status="TRUE" if is_correct else "FALSE",
                phenotype=phenotype,
                is_compliant=True,
                oracle_details={
                    "geometry": geom,
                    "knocked_out": list(knocked_out),
                    "expected": expected,
                    "emitted": rec.emitted_claim,
                    "is_correct": is_correct,
                },
            )

            results.append({
                "call_id": call_id,
                "station": st,
                "geometry": geom,
                "label": label,
                "emitted": rec.emitted_claim,
                "expected": expected,
                "is_correct": is_correct,
            })
            print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (expected={expected}, correct={is_correct})", flush=True)
            calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_h_coalition.db")
    print("Running Track H: Coalition Causality & Overdetermination (18 calls on gemma3:12b)...", flush=True)
    res = run_track_h_live(db, max_calls=18)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
