"""Track F: Reported-Lineage Identifier Equivariance Runner.

Evaluates whether model self-reported citation sets (R) depend on the arbitrary string tokenization
used to label memory IDs (Semantic Natural vs Short Coded vs Random Hashes).
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

MAPPINGS = {
    "semantic_natural": {
        "parent_mgr": "KAVO_ARCHIVE",
        "parent_sup": "RILEN_LOG",
        "distractor": "TEPA_DOC",
    },
    "short_coded": {
        "parent_mgr": "ZURI_01",
        "parent_sup": "MEKO_02",
        "distractor": "NAVI_99",
    },
    "random_hashes": {
        "parent_mgr": "NODE_8F3A2B",
        "parent_sup": "NODE_E1C7D9",
        "distractor": "NODE_4B6E02",
    },
}


def build_track_f_prompt(station: str, mapping_key: str) -> tuple[str, dict[str, str]]:
    """Build prompt with specific ID tokenization."""
    mapping = MAPPINGS[mapping_key]
    inv_mapping = {v: k for k, v in mapping.items()}

    memories = [
        f"- manager({station}, Nerin) [id: {mapping['parent_mgr']}]",
        f"- reports_to(Nerin, Kira) [id: {mapping['parent_sup']}]",
        f"- weather_condition({station}, SOLAR_FLUX) [id: {mapping['distractor']}]",
    ]

    target_schema = '{"station": "' + station + '", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["' + mapping['parent_mgr'] + '", "' + mapping['parent_sup'] + '"]}'

    prompt = (
        "RULES:\n"
        "1. IF manager(Station, Person) AND reports_to(Person, Supervisor) -> protocol(Station, Protocol)\n"
        "   - Supervisor KIRA -> PROTO_X7, Supervisor TAL -> PROTO_Q2\n\n"
        f"RETRIEVED MEMORIES:\n" + "\n".join(memories) + "\n\n"
        f"QUESTION: What protocol applies to station {station}?\n"
        f"Return strictly a valid JSON object matching this schema:\n{target_schema}\n"
        f"Cite strictly the exact memory IDs that provided the necessary and sufficient evidence."
    )
    return prompt, inv_mapping


def unmap_cited_ids(raw_cited_ids: list[str], inv_mapping: dict[str, str]) -> set[str]:
    """Unmap raw cited IDs to canonical semantic roles."""
    canonical_set = set()
    for cid in raw_cited_ids:
        cid_clean = str(cid).strip()
        if cid_clean in inv_mapping:
            canonical_set.add(inv_mapping[cid_clean])
        else:
            canonical_set.add(f"UNKNOWN_ID:{cid_clean}")
    return canonical_set


def run_track_f_live(db_path: Path, max_calls: int = 12) -> dict[str, Any]:
    """Execute live model panel across ID mappings."""
    runs_dir = db_path.parent
    runs_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS track_f_results (
            call_id TEXT PRIMARY KEY,
            station TEXT,
            mapping_key TEXT,
            raw_response TEXT,
            emitted_value TEXT,
            raw_cited_ids TEXT,
            unmapped_roles TEXT,
            is_parent_set_exact INTEGER,
            has_distractor_citation INTEGER
        )
    """)
    conn.commit()

    client = OllamaClient()
    stations = ["VELORA", "KESTREL"]
    mapping_keys = ["semantic_natural", "short_coded", "random_hashes"]

    calls_spent = 0
    results = []

    # 2 stations x 3 mappings x 2 repetitions = 12 calls
    for rep in [1, 2]:
        for station in stations:
            for m_key in mapping_keys:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_f_{station.lower()}_{m_key}_rep{rep}"
                prompt, inv_map = build_track_f_prompt(station, m_key)

                try:
                    spec = CallSpec(
                        model_name="gemma3:12b",
                        system_prompt="You are a precise, deterministic reasoning system. Cite exact supporting IDs from the prompt.",
                        user_prompt=prompt,
                        temperature=0.0,
                        seed=42 + rep,
                    )
                    call_res = client.chat(spec)
                    data = call_res.parsed_json or {}
                    raw_text = call_res.raw_response_text

                    proto = str(data.get("protocol", "UNKNOWN")).strip().upper()
                    raw_cited = data.get("cited_memory_ids", [])
                    unmapped = unmap_cited_ids(raw_cited, inv_map)

                    # Check exact parent set {"parent_mgr", "parent_sup"}
                    is_exact = 1 if unmapped == {"parent_mgr", "parent_sup"} else 0
                    has_dist = 1 if "distractor" in unmapped else 0

                    c.execute("""
                        INSERT OR REPLACE INTO track_f_results 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (call_id, station, m_key, raw_text, proto, json.dumps(raw_cited), json.dumps(sorted(list(unmapped))), is_exact, has_dist))
                    conn.commit()

                    print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {proto}, roles={unmapped} (exact={is_exact}, dist={has_dist})", flush=True)
                    results.append({
                        "call_id": call_id,
                        "station": station,
                        "mapping": m_key,
                        "protocol": proto,
                        "unmapped_roles": sorted(list(unmapped)),
                        "is_exact": is_exact,
                        "has_distractor": has_dist
                    })
                    calls_spent += 1
                    time.sleep(0.1)

                except Exception as e:
                    print(f"Error on {call_id}: {e}", flush=True)

    conn.close()
    return {
        "calls_spent": calls_spent,
        "results": results
    }


if __name__ == "__main__":
    db = Path("runs/explore/track_f_id_equivariance.db")
    print("Running Track F: Reported-ID Equivariance (12 calls on gemma3:12b)...", flush=True)
    res = run_track_f_live(db, max_calls=12)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
