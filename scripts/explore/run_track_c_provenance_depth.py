"""Track C: Transformation Depth and Causal Provenance Decay Runner.

Evaluates whether ancestral causality decays across a 6-generation semantic transformation chain (G0 -> G5).
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


CHAIN_RULES = [
    # G0 -> G1
    ("G1_protocol", "IF manager(Station, Person) AND reports_to(Person, Supervisor) -> protocol(Station, Protocol)",
     {"KIRA": "PROTO_X7", "TAL": "PROTO_Q2"}),
    # G1 -> G2
    ("G2_clearance", "IF protocol(Station, Protocol) AND facility_grid(Station, Grid) -> clearance(Station, Clearance)",
     {"PROTO_X7": "CLEAR_LVL_1", "PROTO_Q2": "CLEAR_LVL_2"}),
    # G2 -> G3
    ("G3_route", "IF clearance(Station, Clearance) AND transit_hub(Station, Hub) -> route(Station, Route)",
     {"CLEAR_LVL_1": "ROUTE_ALPHA", "CLEAR_LVL_2": "ROUTE_BETA"}),
    # G3 -> G4
    ("G4_access_tier", "IF route(Station, Route) AND security_zone(Station, Zone) -> access_tier(Station, Tier)",
     {"ROUTE_ALPHA": "TIER_PRIORITY", "ROUTE_BETA": "TIER_RESTRICTED"}),
    # G4 -> G5
    ("G5_audit_mode", "IF access_tier(Station, Tier) AND inspection_cycle(Station, Cycle) -> audit_mode(Station, Mode)",
     {"TIER_PRIORITY": "AUDIT_EXPEDITE", "TIER_RESTRICTED": "AUDIT_MANDATORY"}),
]


def simulate_depth_closure(founder_allele: str = "KIRA") -> dict[int, dict[str, str]]:
    """Zero-compute preflight: Compute exact symbolic transformation chain from G0 to G5."""
    allele = founder_allele
    chain = {0: {"predicate": "supervisor", "value": allele}}

    current_val = allele
    for idx, (pred_name, rule_text, mapping) in enumerate(CHAIN_RULES, start=1):
        next_val = mapping[current_val]
        chain[idx] = {
            "predicate": pred_name,
            "rule": rule_text,
            "derived_value": next_val
        }
        current_val = next_val

    return chain


def build_track_c_prompt(station: str, depth_g: int, founder_allele: str) -> str:
    """Build multi-hop context up to depth g."""
    # Deterministically derive intermediate facts up to depth g
    chain = simulate_depth_closure(founder_allele)

    # Static grounding premises
    memories = [
        f"- manager({station}, Nerin) [id: mem_mgr]",
        f"- reports_to(Nerin, {founder_allele}) [id: mem_g0_root]",
        f"- facility_grid({station}, GRID_1) [id: mem_grid]",
        f"- transit_hub({station}, HUB_CENTRAL) [id: mem_hub]",
        f"- security_zone({station}, ZONE_SECURE) [id: mem_zone]",
        f"- inspection_cycle({station}, CYCLE_ANNUAL) [id: mem_cycle]",
    ]

    rules = [
        "1. IF manager(Station, Person) AND reports_to(Person, Supervisor) -> protocol(Station, Protocol): KIRA->PROTO_X7, TAL->PROTO_Q2",
        "2. IF protocol(Station, Protocol) AND facility_grid(Station, Grid) -> clearance(Station, Clearance): PROTO_X7->CLEAR_LVL_1, PROTO_Q2->CLEAR_LVL_2",
        "3. IF clearance(Station, Clearance) AND transit_hub(Station, Hub) -> route(Station, Route): CLEAR_LVL_1->ROUTE_ALPHA, CLEAR_LVL_2->ROUTE_BETA",
        "4. IF route(Station, Route) AND security_zone(Station, Zone) -> access_tier(Station, Tier): ROUTE_ALPHA->TIER_PRIORITY, ROUTE_BETA->TIER_RESTRICTED",
        "5. IF access_tier(Station, Tier) AND inspection_cycle(Station, Cycle) -> audit_mode(Station, Mode): TIER_PRIORITY->AUDIT_EXPEDITE, TIER_RESTRICTED->AUDIT_MANDATORY",
    ]

    # Target predicate for depth g
    target_info = chain[depth_g]
    target_pred = target_info["predicate"]
    rules_to_include = "\n".join(rules[:depth_g])
    memories_str = "\n".join(memories)

    target_schema = '{"station": "' + station + '", "depth": ' + str(depth_g) + ', "target_predicate": "' + target_pred + '", "derived_value": "VALUE_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'

    prompt = (
        f"You are a multi-step deductive reasoning system. Execute the required derivation chain step-by-step.\n\n"
        f"RULES:\n{rules_to_include}\n\n"
        f"RETRIEVED MEMORIES:\n{memories_str}\n\n"
        f"QUESTION: Deduce the {target_pred} for station {station} at transformation depth G{depth_g}.\n"
        f"Return strictly a valid JSON object matching this schema:\n{target_schema}\n"
        f"If the information is insufficient, set derived_value to 'UNKNOWN'."
    )
    return prompt


def run_track_c_live(db_path: Path, max_calls: int = 12) -> dict[str, Any]:
    """Execute live model panel across depths g in {1, 3, 5} with clean vs mutated founder."""
    runs_dir = db_path.parent
    runs_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS track_c_results (
            call_id TEXT PRIMARY KEY,
            station TEXT,
            depth_g INTEGER,
            founder_allele TEXT,
            expected_value TEXT,
            emitted_value TEXT,
            raw_response TEXT,
            is_allele_faithful INTEGER,
            is_abstention INTEGER
        )
    """)
    conn.commit()

    client = OllamaClient()
    stations = ["VELORA", "KESTREL"]
    depths = [1, 3, 5]
    founders = ["KIRA", "TAL"]

    calls_spent = 0
    results = []

    for station in stations:
        for depth in depths:
            for founder in founders:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_c_{station.lower()}_g{depth}_{founder.lower()}"
                prompt = build_track_c_prompt(station, depth, founder)
                expected_val = simulate_depth_closure(founder)[depth]["derived_value"]

                try:
                    spec = CallSpec(
                        model_name="gemma3:12b",
                        system_prompt="You are a deterministic, multi-hop reasoning system. Execute logical derivations without skipping intermediate steps.",
                        user_prompt=prompt,
                        temperature=0.0,
                        seed=42 + depth,
                    )
                    call_res = client.chat(spec)
                    data = call_res.parsed_json or {}
                    raw_text = call_res.raw_response_text

                    emitted = str(data.get("derived_value", "UNKNOWN")).strip().upper()
                    is_faithful = 1 if emitted == expected_val else 0
                    is_abs = 1 if emitted == "UNKNOWN" else 0

                    c.execute("""
                        INSERT OR REPLACE INTO track_c_results 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (call_id, station, depth, founder, expected_val, emitted, raw_text, is_faithful, is_abs))
                    conn.commit()

                    print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {emitted} (expected={expected_val}, faithful={is_faithful}, abs={is_abs})")
                    results.append({
                        "call_id": call_id,
                        "station": station,
                        "depth_g": depth,
                        "founder": founder,
                        "expected": expected_val,
                        "emitted": emitted,
                        "is_faithful": is_faithful,
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
    db = Path("runs/explore/track_c_provenance_depth.db")
    print("Running Track C deterministic preflight...")
    clean_chain = simulate_depth_closure("KIRA")
    mut_chain = simulate_depth_closure("TAL")
    print("Clean chain (KIRA):", {k: v["derived_value"] for k, v in clean_chain.items() if k > 0})
    print("Mutated chain (TAL):", {k: v["derived_value"] for k, v in mut_chain.items() if k > 0})

    print("\nRunning Track C live panel (12 calls on gemma3:12b)...")
    res = run_track_c_live(db, max_calls=12)
    print(f"Completed {res['calls_spent']} live calls.")
