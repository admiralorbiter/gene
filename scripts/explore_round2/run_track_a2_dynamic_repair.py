"""Track A2: Dynamic Memory Repair & Lazy Revalidation Runner.

Executes real in-situ graph updates in SQLite, evaluates retrieved query prompts,
and records empirical inspection, recomputation, and accuracy metrics.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd()))

import json
import sqlite3
import time
from typing import Any

from gene.experiments.dynamic_repair import DynamicMemoryStore, DynamicRepairMetrics
from gene.experiments.exploration_harness import ExplorationHarness
from gene.ollama_client import CallSpec, OllamaClient


def build_track_a2_query_prompt(
    station: str,
    target_locus: str,  # 'protocol' vs 'route'
    retrieved_memories: list[dict[str, Any]],
) -> tuple[str, list[str]]:
    """Construct retrieval prompt from live memory state without pre-baked answers."""
    rules_text = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, KIRA) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. manager({station}, person) AND reports_to(person, TAL) -> uses_protocol({station}, PROTO_Q2)\n"
        f"3. uses_protocol({station}, PROTO_X7) -> primary_route({station}, ROUTE_ALPHA)\n"
        f"4. uses_protocol({station}, PROTO_Q2) -> primary_route({station}, ROUTE_BETA)\n"
        "5. If evidence is missing or insufficient, return UNKNOWN."
    )

    mem_lines = []
    for m in retrieved_memories:
        m_id = m["memory_id"]
        c_type = m["claim_type"]
        val = m["claim_value"]
        if c_type == "founder":
            mem_lines.append(f"- {m_id}: Nerin directly reports to {val}.")
        elif c_type == "protocol":
            mem_lines.append(f"- {m_id}: Station {station} operates under security protocol {val}.")
        elif c_type == "route":
            mem_lines.append(f"- {m_id}: Station {station} routes transport along corridor {val}.")

    mem_lines.insert(0, f"- MEM_BASE: Nerin serves as the designated station manager of {station}.")

    query_subj = "protocol" if target_locus == "protocol" else "primary route"
    prompt = (
        f"{rules_text}\n\n"
        "RETRIEVED EPISODIC MEMORIES:\n"
        + "\n".join(mem_lines)
        + f"\n\nQUESTION: What is the authorized {query_subj} for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        '{"station": "STATION_NAME", "derived_value": "VALUE_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
    )

    forbidden = ["PROTO_X7", "PROTO_Q2", "ROUTE_ALPHA", "ROUTE_BETA"]
    return prompt, forbidden


def run_track_a2_live(
    db_path: Path = Path("runs/explore_round2/track_a2_dynamic_repair.db"),
    max_calls: int = 16,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track A2 live panel under ExplorationHarness."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_a2_dynamic_repair",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    stations = ["VELORA", "KESTREL"]
    policies = ["root_overwrite", "eager_repair", "lazy_revalidation"]
    loci = ["protocol", "route"]
    calls_spent = 0
    results = []

    for station in stations:
        for pol in policies:
            # Create fresh in-memory SQLite store for this test arm
            temp_store_db = db_path.parent / f"temp_{station}_{pol}.db"
            if temp_store_db.exists():
                temp_store_db.unlink()
            store = DynamicMemoryStore(temp_store_db)

            # 1. Populate initial state: TAL (mutated) -> PROTO_Q2 -> ROUTE_BETA
            store.insert_node("mem_g0_root", station, "founder", "TAL", [])
            store.insert_node("mem_g1_protocol", station, "protocol", "PROTO_Q2", ["mem_g0_root"])
            store.insert_node("mem_g2_route", station, "route", "ROUTE_BETA", ["mem_g1_protocol"])

            # 2. Execute active mutation policy
            if pol == "root_overwrite":
                store.update_root_overwrite("mem_g0_root", "KIRA")
            elif pol == "eager_repair":
                store.update_eager_repair("mem_g0_root", "KIRA")
            elif pol == "lazy_revalidation":
                store.update_lazy_revalidate_mark_dirty("mem_g0_root", "KIRA")

            # 3. Retrieve memories according to policy
            conn = sqlite3.connect(temp_store_db)
            c = conn.cursor()
            rows = c.execute("SELECT memory_id, claim_type, claim_value, is_dirty FROM episodic_memories").fetchall()
            conn.close()

            retrieved = []
            for m_id, c_type, c_val, is_dirty in rows:
                if pol == "lazy_revalidation" and is_dirty:
                    # In lazy revalidation, dirty nodes are re-evaluated at read time
                    # We pass the clean root + allow read-time rederivation
                    if c_type == "founder":
                        retrieved.append({"memory_id": m_id, "claim_type": c_type, "claim_value": c_val})
                else:
                    retrieved.append({"memory_id": m_id, "claim_type": c_type, "claim_value": c_val})

            # 4. Issue queries for protocol and route
            for locus in loci:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_a2_{station.lower()}_{pol}_{locus}"
                prompt, forbidden = build_track_a2_query_prompt(station, locus, retrieved)

                spec = CallSpec(
                    model_name="gemma3:12b",
                    system_prompt="You are a precise data analysis assistant. Return strictly valid JSON.",
                    user_prompt=prompt,
                    temperature=0.0,
                    seed=42,
                )

                rec = harness.execute_call(
                    call_id=call_id,
                    spec=spec,
                    forbidden_schema_leaks=forbidden,
                    metadata={"station": station, "policy": pol, "locus": locus},
                    fail_on_lexical_leak=True,
                )

                expected_clean = "PROTO_X7" if locus == "protocol" else "ROUTE_ALPHA"
                stale_val = "PROTO_Q2" if locus == "protocol" else "ROUTE_BETA"

                is_recovered = (rec.emitted_claim == expected_clean)
                is_stale = (rec.emitted_claim == stale_val)

                results.append({
                    "call_id": call_id,
                    "station": station,
                    "policy": pol,
                    "locus": locus,
                    "emitted_claim": rec.emitted_claim,
                    "is_recovered": is_recovered,
                    "is_stale": is_stale,
                })
                print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (recovered={is_recovered}, stale={is_stale})", flush=True)
                calls_spent += 1

            if temp_store_db.exists():
                temp_store_db.unlink()

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round2/track_a2_dynamic_repair.db")
    print("Running Track A2: Dynamic Memory Repair & Lazy Revalidation (12 calls on gemma3:12b)...", flush=True)
    res = run_track_a2_live(db, max_calls=12)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
