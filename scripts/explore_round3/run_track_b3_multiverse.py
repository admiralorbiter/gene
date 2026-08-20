"""Track B3: Monoculture Measurement Multiverse Runner.

Executes the balanced 16-cell factorial design over root structure, token mapping,
document ordering, and station context to isolate the pure marginal effect of common roots (Delta_root).
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd()))

import json
from typing import Any

from gene.experiments.exploration_harness import ExplorationHarness
from gene.experiments.multiverse_generator import MultiverseGenerator
from gene.ollama_client import CallSpec, OllamaClient


def run_track_b3_live(
    db_path: Path = Path("runs/explore_round3/track_b3_multiverse.db"),
    max_calls: int = 24,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track B3 multiverse panel."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_b3_monoculture_multiverse",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    gen = MultiverseGenerator()
    cells = gen.generate_all_16_cells()

    calls_spent = 0
    results = []

    for cell in cells:
        if calls_spent >= max_calls:
            break

        call_id = f"call_track_b3_{cell.cell_id}"
        forbidden = ["PROTO_M4", "PROTO_Q7"]

        spec = CallSpec(
            model_name="gemma3:12b",
            system_prompt="You are a precise evidence analysis assistant. Return strictly valid JSON.",
            user_prompt=cell.prompt,
            temperature=0.0,
            seed=42,
        )

        rec = harness.execute_call(
            call_id=call_id,
            spec=spec,
            forbidden_schema_leaks=forbidden,
            metadata={
                "cell_id": cell.cell_id,
                "station": cell.station,
                "root_structure": cell.root_structure,
                "token_mapping": cell.token_mapping,
                "doc_order": cell.doc_order,
                "majority_protocol": cell.majority_protocol,
                "minority_protocol": cell.minority_protocol,
            },
            fail_on_lexical_leak=True,
        )

        emitted = rec.emitted_claim
        follows_majority = (emitted == cell.majority_protocol)
        follows_minority = (emitted == cell.minority_protocol)
        is_abstention = (emitted == "UNKNOWN")

        phenotype = f"ACTIVE_{emitted}" if not is_abstention else "INACTIVE_UNKNOWN"

        # Contemporaneous evaluation logging
        harness.record_evaluation(
            call_id=call_id,
            canonical_status="UNKNOWN",
            local_status="TRUE",
            phenotype=phenotype,
            is_compliant=True,
            oracle_details={
                "root_structure": cell.root_structure,
                "token_mapping": cell.token_mapping,
                "doc_order": cell.doc_order,
                "majority_protocol": cell.majority_protocol,
                "emitted": emitted,
                "follows_majority": follows_majority,
            },
        )

        results.append({
            "call_id": call_id,
            "station": cell.station,
            "root_structure": cell.root_structure,
            "token_mapping": cell.token_mapping,
            "doc_order": cell.doc_order,
            "emitted": emitted,
            "follows_majority": follows_majority,
            "is_abstention": is_abstention,
        })
        print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {emitted} (maj={cell.majority_protocol}, follows_maj={follows_majority})", flush=True)
        calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_b3_multiverse.db")
    print("Running Track B3: Monoculture Factorial Multiverse (16-24 calls on gemma3:12b)...", flush=True)
    res = run_track_b3_live(db, max_calls=24)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
