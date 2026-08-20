"""Track D: Cross-Model Sentinel Replication Runner.

Evaluates a frozen 4-pair sentinel battery across multiple open-weight model architectures
(gemma3:12b, qwen2.5:7b, llama3.2:3b).
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from gene.ollama_client import OllamaClient, CallSpec
from scripts.run_exp1b_c2b_binding_assay import evaluate_epistemic_proofreading


def build_sentinel_prompts(station: str = "VELORA") -> dict[str, str]:
    """Build the 8 prompts for the 4 sentinel pairs."""
    prompts = {}

    # Pair 1: Semantic Inheritance (G1 Protocol)
    # 1.1 Clean Path
    prompts["sentinel_1_clean"] = (
        "RULES:\n1. IF manager(Station, Person) AND reports_to(Person, Supervisor) -> protocol(Station, Protocol)\n"
        "   - Supervisor KIRA -> PROTO_X7\n"
        "   - Supervisor TAL -> PROTO_Q2\n\n"
        f"RETRIEVED MEMORIES:\n- manager({station}, Nerin) [id: m1]\n- reports_to(Nerin, Kira) [id: m2]\n\n"
        f"QUESTION: What protocol applies to {station}?\n"
        'Return strictly JSON: {"station": "' + station + '", "protocol": "PROTO_X7|PROTO_Q2|UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["m1", "m2"]}'
    )
    # 1.2 Mutated Path
    prompts["sentinel_1_mutated"] = (
        "RULES:\n1. IF manager(Station, Person) AND reports_to(Person, Supervisor) -> protocol(Station, Protocol)\n"
        "   - Supervisor KIRA -> PROTO_X7\n"
        "   - Supervisor TAL -> PROTO_Q2\n\n"
        f"RETRIEVED MEMORIES:\n- manager({station}, Nerin) [id: m1]\n- reports_to(Nerin, Tal) [id: m2]\n\n"
        f"QUESTION: What protocol applies to {station}?\n"
        'Return strictly JSON: {"station": "' + station + '", "protocol": "PROTO_X7|PROTO_Q2|UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["m1", "m2"]}'
    )

    # Pair 2: Retrieval Gate
    # 2.1 Complete Path (X_path = 1)
    prompts["sentinel_2_complete"] = (
        "RULES:\n1. IF protocol(Station, Protocol) AND facility_grid(Station, Grid) -> route(Station, Route)\n"
        "   - PROTO_X7 + GRID_1 -> ROUTE_ALPHA\n\n"
        f"RETRIEVED MEMORIES:\n- protocol({station}, PROTO_X7) [id: m1]\n- facility_grid({station}, GRID_1) [id: m2]\n\n"
        f"QUESTION: What route applies to {station}?\n"
        'Return strictly JSON: {"station": "' + station + '", "route": "ROUTE_ALPHA|ROUTE_BETA|UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["m1", "m2"]}'
    )
    # 2.2 Broken Path (X_path = 0)
    prompts["sentinel_2_broken"] = (
        "RULES:\n1. IF protocol(Station, Protocol) AND facility_grid(Station, Grid) -> route(Station, Route)\n"
        "   - PROTO_X7 + GRID_1 -> ROUTE_ALPHA\n\n"
        f"RETRIEVED MEMORIES:\n- facility_grid({station}, GRID_1) [id: m2]\n\n"
        f"QUESTION: What route applies to {station}?\n"
        'Return strictly JSON: {"station": "' + station + '", "route": "ROUTE_ALPHA|ROUTE_BETA|UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["m2"]}'
    )

    # Pair 3: Pseudo-Path Vulnerability
    # 3.1 Explicit Wrong Route Context (Elicits clean abstention)
    prompts["sentinel_3_wrong_route"] = (
        "RULES:\n1. IF transit_route(Station, ROUTE_ALPHA) AND facility_grid(Station, GRID_1) -> auth_code(Station, AUTH_ALPHA)\n\n"
        f"RETRIEVED MEMORIES:\n- transit_route({station}, ROUTE_DELTA) [id: m1]\n- facility_grid({station}, GRID_1) [id: m2]\n\n"
        f"QUESTION: What auth code applies to {station}?\n"
        'Return strictly JSON: {"station": "' + station + '", "auth_code": "AUTH_ALPHA|AUTH_BETA|UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["m1", "m2"]}'
    )
    # 3.2 Zero Route Context (Tests single-premise conclusion jumping)
    prompts["sentinel_3_zero_route"] = (
        "RULES:\n1. IF transit_route(Station, ROUTE_ALPHA) AND facility_grid(Station, GRID_1) -> auth_code(Station, AUTH_ALPHA)\n\n"
        f"RETRIEVED MEMORIES:\n- facility_grid({station}, GRID_1) [id: m2]\n\n"
        f"QUESTION: What auth code applies to {station}?\n"
        'Return strictly JSON: {"station": "' + station + '", "auth_code": "AUTH_ALPHA|AUTH_BETA|UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["m2"]}'
    )

    # Pair 4: Proofreading Gate (Cross-entity binding prompt)
    # 4.1 Valid Target Route
    prompts["sentinel_4_valid_cert"] = (
        "RULES:\n1. IF transit_route(Station, ROUTE_ALPHA) AND facility_grid(Station, GRID_1) -> auth_code(Station, AUTH_ALPHA)\n\n"
        f"RETRIEVED MEMORIES:\n- transit_route({station}, ROUTE_ALPHA) [id: m1]\n- facility_grid({station}, GRID_1) [id: m2]\n\n"
        f"QUESTION: What auth code applies to {station}?\n"
        'Return strictly JSON: {"station": "' + station + '", "auth_code": "AUTH_ALPHA|AUTH_BETA|UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["m1", "m2"]}'
    )
    # 4.2 Foreign Station Target Route (Tests cross-entity binding)
    prompts["sentinel_4_cross_binding"] = (
        "RULES:\n1. IF transit_route(Station, ROUTE_ALPHA) AND facility_grid(Station, GRID_1) -> auth_code(Station, AUTH_ALPHA)\n\n"
        f"RETRIEVED MEMORIES:\n- transit_route(KESTREL, ROUTE_ALPHA) [id: m1]\n- facility_grid({station}, GRID_1) [id: m2]\n\n"
        f"QUESTION: What auth code applies to {station}?\n"
        'Return strictly JSON: {"station": "' + station + '", "auth_code": "AUTH_ALPHA|AUTH_BETA|UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["m1", "m2"]}'
    )

    return prompts


def run_track_d_live(db_path: Path, models: list[str] | None = None, max_calls_per_model: int = 8) -> dict[str, Any]:
    """Run the 8-prompt sentinel battery across target model architectures."""
    if models is None:
        models = ["gemma3:12b", "qwen2.5:3b", "llama3.2:3b"]

    runs_dir = db_path.parent
    runs_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS track_d_results (
            call_id TEXT PRIMARY KEY,
            model_name TEXT,
            sentinel_key TEXT,
            raw_response TEXT,
            emitted_value TEXT,
            evidence_status TEXT,
            cited_ids TEXT,
            is_abstention INTEGER,
            is_expected_phenotype INTEGER
        )
    """)
    conn.commit()

    client = OllamaClient()
    prompts = build_sentinel_prompts("VELORA")

    total_spent = 0
    results_by_model = {}

    for model in models:
        model_results = []
        calls_spent_model = 0

        for key, prompt in prompts.items():
            if calls_spent_model >= max_calls_per_model:
                break

            call_id = f"call_track_d_{model.replace(':', '_')}_{key}"
            try:
                spec = CallSpec(
                    model_name=model,
                    system_prompt="You are a strict, deterministic reasoning system. Adhere strictly to the JSON contract and evidence rules.",
                    user_prompt=prompt,
                    temperature=0.0,
                    seed=42,
                )
                call_res = client.chat(spec)
                data = call_res.parsed_json or {}
                raw_text = call_res.raw_response_text

                # Extract value
                val = data.get("protocol") or data.get("route") or data.get("auth_code") or "UNKNOWN"
                val = str(val).strip().upper()
                status = str(data.get("evidence_status", "")).strip().lower()
                cited = json.dumps(data.get("cited_memory_ids", []))
                is_abs = 1 if val == "UNKNOWN" else 0

                # Determine expected behavior
                is_expected = 0
                if key == "sentinel_1_clean" and val == "PROTO_X7":
                    is_expected = 1
                elif key == "sentinel_1_mutated" and val == "PROTO_Q2":
                    is_expected = 1
                elif key == "sentinel_2_complete" and val == "ROUTE_ALPHA":
                    is_expected = 1
                elif key == "sentinel_2_broken" and val == "UNKNOWN":
                    is_expected = 1
                elif key == "sentinel_3_wrong_route" and val == "UNKNOWN":
                    is_expected = 1
                elif key == "sentinel_3_zero_route":
                    # Pseudo-path trigger
                    is_expected = 1 if val == "UNKNOWN" else 0  # 1 if resilient abstention, 0 if pseudo-path jump
                elif key == "sentinel_4_valid_cert" and val == "AUTH_ALPHA":
                    is_expected = 1
                elif key == "sentinel_4_cross_binding" and val == "UNKNOWN":
                    is_expected = 1

                c.execute("""
                    INSERT OR REPLACE INTO track_d_results 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (call_id, model, key, raw_text, val, status, cited, is_abs, is_expected))
                conn.commit()

                print(f"[{calls_spent_model+1}/{max_calls_per_model}] ({model}) {key} -> {val} (expected={is_expected}, abs={is_abs})", flush=True)
                model_results.append({
                    "sentinel": key,
                    "emitted": val,
                    "is_abstention": is_abs,
                    "is_expected": is_expected
                })
                calls_spent_model += 1
                total_spent += 1
                time.sleep(0.1)

            except Exception as e:
                print(f"Error on {call_id}: {e}")

        results_by_model[model] = model_results

    conn.close()
    return {
        "total_calls": total_spent,
        "models_evaluated": models,
        "results_by_model": results_by_model
    }


if __name__ == "__main__":
    db = Path("runs/explore/track_d_model_sentinel.db")
    print("Running Track D Cross-Model Sentinel (8 calls x 3 models = 24 calls)...", flush=True)
    res = run_track_d_live(db, models=["gemma3:12b", "qwen2.5:3b", "llama3.2:3b"])
    print(f"Completed {res['total_calls']} calls across {len(res['models_evaluated'])} models.", flush=True)
