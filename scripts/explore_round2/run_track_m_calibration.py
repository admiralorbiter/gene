"""Track M: Measurement Invariance & Model Calibration Gateway.

Calibrates open-weight models (qwen2.5:3b, llama3.2:3b) on a 4-case functional battery
to establish measurement invariance before experimental admission.
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


def build_calibration_prompt(
    station: str,
    case_key: str,
    contract_variant: str = "generic_placeholder",
) -> tuple[str, list[str], str]:
    """Construct calibration prompt and expected target."""
    rules = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, KIRA) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. manager({station}, person) AND reports_to(person, TAL) -> uses_protocol({station}, PROTO_Q2)\n"
        "3. If evidence is missing, conflicting, or mentions a different station, protocol is UNKNOWN."
    )

    if case_key == "complete_valid":
        memories = [
            f"- MEM_01: Nerin serves as the designated station manager of {station}.",
            "- MEM_02: Nerin directly reports to KIRA.",
        ]
        expected = "PROTO_X7"
    elif case_key == "missing_premise":
        memories = [
            f"- MEM_01: Nerin serves as the designated station manager of {station}.",
        ]
        expected = "UNKNOWN"
    elif case_key == "directional_mutation":
        memories = [
            f"- MEM_01: Nerin serves as the designated station manager of {station}.",
            "- MEM_02: Nerin directly reports to TAL.",
        ]
        expected = "PROTO_Q2"
    elif case_key == "entity_mismatch":
        memories = [
            "- MEM_01: Nerin serves as the designated station manager of OTHER_BASE.",
            "- MEM_02: Nerin directly reports to KIRA.",
        ]
        expected = "UNKNOWN"
    else:
        raise ValueError(f"Unknown case key {case_key}")

    if contract_variant == "raw_enum":
        schema_text = '{"station": "' + station + '", "protocol": "PROTO_X7|PROTO_Q2|UNKNOWN", "evidence_status": "sufficient|insufficient"}'
    else:  # generic_placeholder
        schema_text = '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'

    prompt = (
        f"{rules}\n\n"
        "RETRIEVED EPISODIC MEMORIES:\n"
        + "\n".join(memories)
        + f"\n\nQUESTION: What security protocol is authorized for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        f"{schema_text}"
    )

    forbidden = ["PROTO_X7", "PROTO_Q2"] if contract_variant != "raw_enum" else []
    return prompt, forbidden, expected


def run_track_m_calibration(
    db_path: Path = Path("runs/explore_round2/track_m_calibration.db"),
    models: list[str] = ["gemma3:12b", "qwen2.5:3b", "llama3.2:3b"],
    contract_variant: str = "generic_placeholder",
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute calibration battery across models."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_m_calibration",
        client=client,
        config={"models": models, "contract_variant": contract_variant},
    )

    cases = ["complete_valid", "missing_premise", "directional_mutation", "entity_mismatch"]
    results = []
    calls_spent = 0

    for model in models:
        for case in cases:
            call_id = f"call_calib_{model.replace(':', '_').replace('.', '_')}_{case}"
            prompt, forbidden, expected = build_calibration_prompt("VELORA", case, contract_variant=contract_variant)

            spec = CallSpec(
                model_name=model,
                system_prompt="You are a precise logical reasoning assistant. Return strictly valid JSON.",
                user_prompt=prompt,
                temperature=0.0,
                seed=42,
            )

            rec = harness.execute_call(
                call_id=call_id,
                spec=spec,
                forbidden_schema_leaks=forbidden,
                metadata={"model": model, "case": case, "variant": contract_variant},
                fail_on_lexical_leak=True,
            )

            is_pass = (rec.emitted_claim == expected)
            results.append({
                "call_id": call_id,
                "model": model,
                "case": case,
                "emitted": rec.emitted_claim,
                "expected": expected,
                "is_pass": is_pass,
            })
            print(f"[{calls_spent+1}/{len(models)*len(cases)}] {call_id} -> {rec.emitted_claim} (expected={expected}, pass={is_pass})", flush=True)
            calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round2/track_m_calibration.db")
    print("Running Track M: Model Calibration Gateway across Qwen 2.5:3B & Llama 3.2:3B...", flush=True)
    res = run_track_m_calibration(db, models=["qwen2.5:3b", "llama3.2:3b"], contract_variant="generic_placeholder")
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
