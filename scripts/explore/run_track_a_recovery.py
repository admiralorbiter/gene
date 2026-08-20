"""Track A: Recovery and Epistemic Hysteresis Runner.

Evaluates whether an established false lineage can be corrected without destroying healthy knowledge,
comparing Root Overwrite, Latest Root Preference, Lineage Quarantine, Lineage Repair, and Revalidate-on-Use.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from gene.ollama_client import OllamaClient, CallSpec
from gene.evaluation.dual_oracle import DualOracle, TruthStatus


def simulate_policies_deterministic() -> dict[str, Any]:
    """Zero-compute preflight: Simulate recovery policies over a synthetic state graph."""
    # Initial graph: Root G0 (TAL) -> G1 (PROTO_Q2) -> G2 (ROUTE_BETA)
    # Correction: Root updated to KIRA (canonical protocol PROTO_X7, route ROUTE_ALPHA)
    policies = {
        "root_overwrite": {
            "g0_active": "KIRA",
            "g1_active": "PROTO_Q2 (STALE)",
            "g2_active": "ROUTE_BETA (STALE)",
            "hysteresis_H_g1": 1.0,
            "hysteresis_H_g2": 1.0,
            "repair_coverage_C_repair": 0.0,
            "nodes_recomputed_K_repair": 1,  # Only root updated
        },
        "latest_root_preference": {
            "g0_active": "KIRA (Rank 1), TAL (Rank 2)",
            "g1_active": "PROTO_Q2 (STALE)",
            "g2_active": "ROUTE_BETA (STALE)",
            "hysteresis_H_g1": 1.0,
            "hysteresis_H_g2": 1.0,
            "repair_coverage_C_repair": 0.0,
            "nodes_recomputed_K_repair": 1,
        },
        "lineage_quarantine": {
            "g0_active": "KIRA (Fresh)",
            "g1_active": "QUARANTINED",
            "g2_active": "QUARANTINED",
            "hysteresis_H_g1": 0.0,
            "hysteresis_H_g2": 0.0,
            "repair_coverage_C_repair": 0.0,  # No descendants exist yet
            "nodes_recomputed_K_repair": 0,
        },
        "lineage_repair": {
            "g0_active": "KIRA (Fresh)",
            "g1_active": "PROTO_X7 (Rederived)",
            "g2_active": "ROUTE_ALPHA (Rederived)",
            "hysteresis_H_g1": 0.0,
            "hysteresis_H_g2": 0.0,
            "repair_coverage_C_repair": 1.0,
            "nodes_recomputed_K_repair": 3,  # Root + G1 + G2 rederived immediately
        },
        "revalidate_on_use": {
            "g0_active": "KIRA (Fresh)",
            "g1_active": "PROTO_X7 (On-Demand Rederived when queried)",
            "g2_active": "ROUTE_ALPHA (On-Demand Rederived when queried)",
            "hysteresis_H_g1": 0.0,
            "hysteresis_H_g2": 0.0,
            "repair_coverage_C_repair": 1.0,
            "nodes_recomputed_K_repair": 1.0,  # Only queried branch revalidated
        },
    }
    return policies


def build_track_a_prompt(station: str, policy: str, query_type: str) -> str:
    """Build the prompt presenting the retrieved context under a specific recovery policy."""
    rules_text = (
        "RULES:\n"
        "1. IF manager(Station, Person) AND reports_to(Person, Supervisor) -> protocol(Station, Protocol)\n"
        "   - Supervisor KIRA -> PROTO_X7\n"
        "   - Supervisor TAL -> PROTO_Q2\n"
        "2. IF protocol(Station, Protocol) AND facility_grid(Station, Grid) -> route(Station, Route)\n"
        "   - PROTO_X7 -> ROUTE_ALPHA\n"
        "   - PROTO_Q2 -> ROUTE_BETA\n"
    )

    if policy == "root_overwrite":
        # Root is corrected to KIRA, but stale G1 fact (PROTO_Q2) is also present in memory
        memories = [
            f"- manager({station}, Nerin) [id: mem_mgr]",
            f"- reports_to(Nerin, Kira) [id: mem_rep_corrected, note: updated_now]",
            f"- protocol({station}, PROTO_Q2) [id: mem_proto_stale, note: generated_earlier]",
            f"- facility_grid({station}, GRID_1) [id: mem_grid]",
        ]
    elif policy == "lineage_repair":
        # Lineage has been mechanically rederived
        memories = [
            f"- manager({station}, Nerin) [id: mem_mgr]",
            f"- reports_to(Nerin, Kira) [id: mem_rep_repaired]",
            f"- protocol({station}, PROTO_X7) [id: mem_proto_repaired]",
            f"- facility_grid({station}, GRID_1) [id: mem_grid]",
        ]
    elif policy == "lineage_quarantine":
        # Stale lineage removed, only fresh root available (G1 protocol missing)
        memories = [
            f"- manager({station}, Nerin) [id: mem_mgr]",
            f"- reports_to(Nerin, Kira) [id: mem_rep_fresh]",
            f"- facility_grid({station}, GRID_1) [id: mem_grid]",
        ]
    elif policy == "revalidate_on_use":
        # Revalidation detects reports_to(Nerin, Kira) contradicts stale PROTO_Q2, so revalidation injects fresh PROTO_X7
        memories = [
            f"- manager({station}, Nerin) [id: mem_mgr]",
            f"- reports_to(Nerin, Kira) [id: mem_rep_fresh]",
            f"- protocol({station}, PROTO_X7) [id: mem_proto_revalidated, note: revalidated_on_read]",
            f"- facility_grid({station}, GRID_1) [id: mem_grid]",
        ]
    else:
        raise ValueError(f"Unknown policy: {policy}")

    memories_str = "\n".join(memories)

    if query_type == "protocol":
        question = f"What protocol applies to station {station}?"
        target_schema = '{"station": "' + station + '", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["id1", "id2"]}'
    else:  # route
        question = f"What route applies to station {station}?"
        target_schema = '{"station": "' + station + '", "route": "ROUTE_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["id1", "id2"]}'

    prompt = (
        f"{rules_text}\n"
        f"RETRIEVED MEMORIES:\n{memories_str}\n\n"
        f"QUESTION: {question}\n\n"
        f"Return strictly a valid JSON object matching this schema:\n{target_schema}\n"
        f"If the retrieved memories are insufficient or conflicting to derive the answer with certainty, set the value to 'UNKNOWN' and evidence_status to 'insufficient'."
    )
    return prompt


def run_track_a_live(db_path: Path, max_calls: int = 16) -> dict[str, Any]:
    """Execute live model panel across recovery policies."""
    runs_dir = db_path.parent
    runs_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS track_a_results (
            call_id TEXT PRIMARY KEY,
            station TEXT,
            policy TEXT,
            query_type TEXT,
            raw_response TEXT,
            emitted_value TEXT,
            evidence_status TEXT,
            cited_ids TEXT,
            is_hysteresis INTEGER,
            is_recovered INTEGER,
            is_abstention INTEGER
        )
    """)
    conn.commit()

    client = OllamaClient()

    stations = ["VELORA", "KESTREL"]
    policies = ["root_overwrite", "lineage_repair", "lineage_quarantine", "revalidate_on_use"]
    queries = ["protocol", "route"]

    calls_spent = 0
    results = []

    for station in stations:
        for policy in policies:
            for query in queries:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_a_{station.lower()}_{policy}_{query}"
                prompt = build_track_a_prompt(station, policy, query)

                try:
                    spec = CallSpec(
                        model_name="gemma3:12b",
                        system_prompt="You are a precise, deterministic reasoning system that adheres strictly to provided rules and facts.",
                        user_prompt=prompt,
                        temperature=0.0,
                        seed=42,
                    )
                    call_res = client.chat(spec)
                    data = call_res.parsed_json or {}
                    raw_text = call_res.raw_response_text
                    val = data.get("protocol") if query == "protocol" else data.get("route")
                    val = str(val).strip().upper()
                    status = str(data.get("evidence_status", "")).strip().lower()
                    cited = json.dumps(data.get("cited_memory_ids", []))

                    # Classify
                    # Clean/Recovered target: PROTO_X7 (protocol) or ROUTE_ALPHA (route)
                    # Stale/Hysteresis target: PROTO_Q2 (protocol) or ROUTE_BETA (route)
                    is_rec = 1 if val in ("PROTO_X7", "ROUTE_ALPHA") else 0
                    is_hys = 1 if val in ("PROTO_Q2", "ROUTE_BETA") else 0
                    is_abs = 1 if val == "UNKNOWN" else 0

                    c.execute("""
                        INSERT OR REPLACE INTO track_a_results 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (call_id, station, policy, query, raw_text, val, status, cited, is_hys, is_rec, is_abs))
                    conn.commit()

                    print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {val} (rec={is_rec}, hys={is_hys}, abs={is_abs})")
                    results.append({
                        "call_id": call_id,
                        "station": station,
                        "policy": policy,
                        "query": query,
                        "emitted": val,
                        "is_hysteresis": is_hys,
                        "is_recovered": is_rec,
                        "is_abstention": is_abs
                    })
                    calls_spent += 1
                    time.sleep(0.1)

                except Exception as e:
                    print(f"Error on {call_id}: {e}")

    conn.close()
    return {
        "calls_spent": calls_spent,
        "results": results
    }


if __name__ == "__main__":
    db = Path("runs/explore/track_a_recovery.db")
    print("Running Track A deterministic preflight...")
    preflight = simulate_policies_deterministic()
    print(json.dumps(preflight, indent=2))

    print("\nRunning Track A live panel (16 calls on gemma3:12b)...")
    res = run_track_a_live(db, max_calls=16)
    print(f"Completed {res['calls_spent']} live calls.")
