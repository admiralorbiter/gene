"""Track B: Epistemic Monoculture vs Independent Roots Runner.

Evaluates whether neural reasoners differentiate source independence from semantic repetition under conflicting evidence.
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


def calculate_effective_roots(root_counts: dict[str, int]) -> float:
    """Calculate effective independent evidence count N_eff = 1 / sum(p_r^2)."""
    total = sum(root_counts.values())
    if total == 0:
        return 0.0
    sum_sq = sum((cnt / total) ** 2 for cnt in root_counts.values())
    return 1.0 / sum_sq if sum_sq > 0 else 0.0


def simulate_monoculture_preflight() -> dict[str, Any]:
    """Zero-compute preflight: Calculate raw vs effective root statistics across conflict conditions."""
    conditions = {
        "monoculture": {
            "x_memories": 3,
            "x_roots": {"root_1": 3},
            "y_memories": 1,
            "y_roots": {"root_2": 1},
            "raw_ratio": "3:1 (X favored)",
            "n_eff_x": calculate_effective_roots({"root_1": 3}),  # 1.0
            "n_eff_y": calculate_effective_roots({"root_2": 1}),  # 1.0
            "root_ratio": "1:1 (Equally grounded)",
            "genealogical_prediction": "CONFLICT / UNKNOWN or TIED",
            "surface_repetition_prediction": "PROTOCOL_X (3 votes)",
        },
        "diverse_roots": {
            "x_memories": 3,
            "x_roots": {"root_1": 1, "root_2": 1, "root_3": 1},
            "y_memories": 1,
            "y_roots": {"root_4": 1},
            "raw_ratio": "3:1 (X favored)",
            "n_eff_x": calculate_effective_roots({"root_1": 1, "root_2": 1, "root_3": 1}),  # 3.0
            "n_eff_y": calculate_effective_roots({"root_4": 1}),  # 1.0
            "root_ratio": "3:1 (X genuinely favored)",
            "genealogical_prediction": "PROTOCOL_X",
            "surface_repetition_prediction": "PROTOCOL_X (3 votes)",
        },
        "inverted_diversity": {
            "x_memories": 3,
            "x_roots": {"root_1": 3},
            "y_memories": 2,
            "y_roots": {"root_2": 1, "root_3": 1},
            "raw_ratio": "3:2 (X favored by count)",
            "n_eff_x": calculate_effective_roots({"root_1": 3}),  # 1.0
            "n_eff_y": calculate_effective_roots({"root_2": 1, "root_3": 1}),  # 2.0
            "root_ratio": "1:2 (Y favored by independence)",
            "genealogical_prediction": "PROTOCOL_Y",
            "surface_repetition_prediction": "PROTOCOL_X (3 votes)",
        },
    }
    return conditions


def build_track_b_prompt(station: str, condition: str, target_favored: str = "X") -> str:
    """Build conflicting evidence prompt under specific lineage diversity structure."""
    if condition == "monoculture":
        # 3 reports for PROTO_X (all citing Supervisor KIRA at Root 1)
        # 1 report for PROTO_Y (citing Supervisor TAL at Root 2)
        memories = [
            f"- report_01: Station {station} operations require PROTO_X (Source: Station Director Kira directive, archive log 101).",
            f"- report_02: Field officer log confirms PROTO_X for {station} (Source: Station Director Kira directive, archive log 101).",
            f"- report_03: Transit memo lists PROTO_X for {station} (Source: Station Director Kira directive, archive log 101).",
            f"- report_04: Audit dispatch indicates PROTO_Y for {station} (Source: Regional Supervisor Tal directive, dispatch 502).",
        ]
    elif condition == "diverse_roots":
        # 3 reports for PROTO_X (citing 3 independent directors: Kira, Nerin, Jax)
        # 1 report for PROTO_Y (citing Tal)
        memories = [
            f"- report_01: Station {station} operations require PROTO_X (Source: Station Director Kira directive, archive log 101).",
            f"- report_02: Safety inspection certifies PROTO_X for {station} (Source: Chief Engineer Nerin inspection, docket 204).",
            f"- report_03: Transit authority confirms PROTO_X for {station} (Source: Fleet Commander Jax log, dispatch 309).",
            f"- report_04: Audit dispatch indicates PROTO_Y for {station} (Source: Regional Supervisor Tal directive, dispatch 502).",
        ]
    elif condition == "inverted_diversity":
        # 3 reports for PROTO_X (all citing 1 director: Kira)
        # 2 reports for PROTO_Y (citing 2 independent officers: Tal and Vael)
        memories = [
            f"- report_01: Station {station} operations require PROTO_X (Source: Station Director Kira directive, archive log 101).",
            f"- report_02: Field officer log confirms PROTO_X for {station} (Source: Station Director Kira directive, archive log 101).",
            f"- report_03: Transit memo lists PROTO_X for {station} (Source: Station Director Kira directive, archive log 101).",
            f"- report_04: Security assessment requires PROTO_Y for {station} (Source: Security Chief Tal mandate, security brief 412).",
            f"- report_05: Grid regulator confirms PROTO_Y for {station} (Source: Grid Auditor Vael certification, audit report 618).",
        ]
    else:
        raise ValueError(f"Unknown condition: {condition}")

    memories_str = "\n".join(memories)
    target_schema = '{"station": "' + station + '", "adjudicated_protocol": "PROTO_X|PROTO_Y|UNKNOWN", "confidence_rationale": "one_sentence_reasoning", "cited_reports": ["report_01", "report_04"]}'

    prompt = (
        f"You are an epistemic adjudication officer resolving conflicting operational reports for station {station}.\n\n"
        f"EVIDENCE LOGS:\n{memories_str}\n\n"
        f"QUESTION: Based on the authoritative evidence, which protocol applies to {station}?\n"
        f"Evaluate the reliability, independent sources, and potential corroboration of the evidence.\n"
        f"If the evidence is irreconcilably tied or insufficient, return 'UNKNOWN'.\n\n"
        f"Return strictly a valid JSON object matching this schema:\n{target_schema}"
    )
    return prompt


def run_track_b_live(db_path: Path, max_calls: int = 12) -> dict[str, Any]:
    """Execute live model panel across monoculture and diverse conditions."""
    runs_dir = db_path.parent
    runs_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS track_b_results (
            call_id TEXT PRIMARY KEY,
            station TEXT,
            condition TEXT,
            raw_response TEXT,
            adjudicated_protocol TEXT,
            rationale TEXT,
            cited_reports TEXT,
            follows_surface_count INTEGER,
            follows_lineage_diversity INTEGER,
            is_abstention INTEGER
        )
    """)
    conn.commit()

    client = OllamaClient()
    stations = ["VELORA", "KESTREL"]
    conditions = ["monoculture", "diverse_roots", "inverted_diversity"]

    calls_spent = 0
    results = []

    # 2 stations x 3 conditions x 2 repetitions = 12 calls
    for rep in [1, 2]:
        for station in stations:
            for cond in conditions:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_b_{station.lower()}_{cond}_rep{rep}"
                prompt = build_track_b_prompt(station, cond)

                try:
                    spec = CallSpec(
                        model_name="gemma3:12b",
                        system_prompt="You are an epistemic evidence adjudication officer. Evaluate evidence independence and resolve conflicts accurately.",
                        user_prompt=prompt,
                        temperature=0.0,
                        seed=42 + rep,
                    )
                    call_res = client.chat(spec)
                    data = call_res.parsed_json or {}
                    raw_text = call_res.raw_response_text

                    proto = str(data.get("adjudicated_protocol", "UNKNOWN")).strip().upper()
                    rationale = str(data.get("confidence_rationale", "")).strip()
                    cited = json.dumps(data.get("cited_reports", []))

                    # Classify behavior
                    # In monoculture: X is surface count (3:1), but roots are tied (1:1)
                    # In diverse_roots: X is both surface count and root diversity
                    # In inverted_diversity: X is surface count (3:2), but Y is root diversity (2:1)
                    follows_surface = 1 if "PROTO_X" in proto else 0
                    if cond == "inverted_diversity":
                        follows_diversity = 1 if "PROTO_Y" in proto else 0
                    elif cond == "monoculture":
                        follows_diversity = 1 if proto == "UNKNOWN" or "TIED" in proto else 0
                    else:  # diverse_roots
                        follows_diversity = 1 if "PROTO_X" in proto else 0

                    is_abs = 1 if proto == "UNKNOWN" else 0

                    c.execute("""
                        INSERT OR REPLACE INTO track_b_results 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (call_id, station, cond, raw_text, proto, rationale, cited, follows_surface, follows_diversity, is_abs))
                    conn.commit()

                    print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {proto} (surf={follows_surface}, div={follows_diversity}, abs={is_abs})")
                    results.append({
                        "call_id": call_id,
                        "station": station,
                        "condition": cond,
                        "protocol": proto,
                        "follows_surface_count": follows_surface,
                        "follows_diversity": follows_diversity,
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
    db = Path("runs/explore/track_b_monoculture.db")
    print("Running Track B deterministic preflight...")
    preflight = simulate_monoculture_preflight()
    print(json.dumps(preflight, indent=2))

    print("\nRunning Track B live panel (12 calls on gemma3:12b)...")
    res = run_track_b_live(db, max_calls=12)
    print(f"Completed {res['calls_spent']} live calls.")
