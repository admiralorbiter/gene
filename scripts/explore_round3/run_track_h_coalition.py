"""Track H: Coalition Causality & Overdetermination Runner.

Exhaustively evaluates single-parent vs coalition knockouts across parent subsets
for recombinant geometry AB + DE -> C where every knockout is strictly pure premise omission.
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
    knocked_out: set[str],
) -> tuple[str, list[str], str]:
    """Construct causal intervention prompt where ALL knockouts are pure premise omissions."""
    rules = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, S1) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. sector_lead({station}, person) AND reports_to(person, S2) -> uses_protocol({station}, PROTO_X7)\n"
        "3. If evidence is insufficient to satisfy any complete rule, protocol is UNKNOWN."
    )

    memories = []
    # Atomic premise A: manager fact
    if "A" not in knocked_out:
        memories.append(f"- MEM_01: Nerin is manager of {station}.")
    # Atomic premise B: S1 reporting relationship
    if "B" not in knocked_out:
        memories.append("- MEM_02: Nerin directly reports to S1.")
    # Atomic premise D: sector-lead fact
    if "D" not in knocked_out:
        memories.append(f"- MEM_03: Vael is sector lead of {station}.")
    # Atomic premise E: S2 reporting relationship
    if "E" not in knocked_out:
        memories.append("- MEM_04: Vael directly reports to S2.")

    path1_valid = ("A" not in knocked_out) and ("B" not in knocked_out)
    path2_valid = ("D" not in knocked_out) and ("E" not in knocked_out)
    expected = "PROTO_X7" if (path1_valid or path2_valid) else "UNKNOWN"

    prompt = (
        f"{rules}\n\n"
        "RETRIEVED EVIDENCE:\n"
        + ("\n".join(memories) if memories else "- NO_EVIDENCE_RETRIEVED")
        + f"\n\nQUESTION: What security protocol is authorized for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
    )

    forbidden = ["PROTO_X7", "PROTO_Q2"]
    return prompt, forbidden, expected


def run_track_h_live(
    db_path: Path = Path("runs/explore_round3/track_h_coalition.db"),
    max_calls: int = 22,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track H coalition causality panel (11 points x 2 stations = 22 calls)."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_h_coalition_causality",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    engine = CoalitionCausalityEngine()
    stations = ["VELORA", "KESTREL"]
    
    # 11 Key Lattice Points on AB + DE -> C:
    intervention_lattice = [
        (set(), "baseline"),
        ({"A"}, "single_knockout_A"),
        ({"B"}, "single_knockout_B"),
        ({"D"}, "single_knockout_D"),
        ({"E"}, "single_knockout_E"),
        ({"A", "B"}, "path_isolate_DE"),
        ({"D", "E"}, "path_isolate_AB"),
        ({"A", "D"}, "cross_hitting_AD"),
        ({"A", "E"}, "cross_hitting_AE"),
        ({"B", "D"}, "cross_hitting_BD"),
        ({"B", "E"}, "cross_hitting_BE"),
    ]

    calls_spent = 0
    results = []
    station_behavioral_maps: dict[str, dict[tuple[str, ...], str]] = {st: {} for st in stations}

    for st in stations:
        for knocked_out, label in intervention_lattice:
            if calls_spent >= max_calls:
                break

            call_id = f"call_track_h_{st.lower()}_{label}"
            prompt, forbidden, expected = build_track_h_prompt(st, knocked_out)

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
                    "geometry": "redundant_independent",
                    "knocked_out": sorted(list(knocked_out)),
                    "label": label,
                    "expected": expected,
                },
                fail_on_lexical_leak=True,
            )

            is_correct = (rec.emitted_claim == expected)
            phenotype = "ACTIVE_CONCORDANT" if is_correct else "DISCORDANT_OR_MASKED"

            # Record contemporaneous evaluation with correct API signature
            harness.record_evaluation(
                call_id=call_id,
                canonical_status="BEHAVIORAL_EVALUATION",
                local_status="TRUE" if is_correct else "FALSE",
                dual_oracle_phenotype=phenotype,
                is_contract_compliant=True,
                metadata={
                    "geometry": "redundant_independent",
                    "knocked_out": sorted(list(knocked_out)),
                    "expected": expected,
                    "emitted": rec.emitted_claim,
                    "is_correct": is_correct,
                },
            )

            station_behavioral_maps[st][tuple(sorted(list(knocked_out)))] = rec.emitted_claim

            results.append({
                "call_id": call_id,
                "station": st,
                "label": label,
                "knocked_out": sorted(list(knocked_out)),
                "emitted": rec.emitted_claim,
                "expected": expected,
                "is_correct": is_correct,
            })
            print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (expected={expected}, correct={is_correct})", flush=True)
            calls_spent += 1

    # Extract empirical causal coalitions S_C
    empirical_s_c = {}
    for st, b_map in station_behavioral_maps.items():
        if len(b_map) >= 11:
            empirical_s_c[st] = [sorted(list(c)) for c in engine.extract_minimal_causal_coalitions("redundant_independent", b_map)]

    return {"calls_spent": calls_spent, "results": results, "empirical_S_C": empirical_s_c}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_h_coalition.db")
    print("Running Track H: Coalition Causality & Overdetermination (22 calls on gemma3:12b)...", flush=True)
    res = run_track_h_live(db, max_calls=22)
    print(f"Completed {res['calls_spent']} live calls. Recovered S_C: {res['empirical_S_C']}", flush=True)
