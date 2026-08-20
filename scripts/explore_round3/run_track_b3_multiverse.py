"""Track B3: Monoculture Measurement Multiverse Runner.

Executes the balanced 16-cell factorial design with pure lexical isolation + 4 exact CallSpec replays (seed 42)
+ 4 seed-perturbed replays (seed 43) across a balanced half-fraction (24 calls) to measure epsilon_replay and epsilon_seed.
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
    """Execute Track B3 multiverse panel (16 factorial cells + 4 exact replays + 4 seed perturbations = 24 calls)."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_b3_monoculture_multiverse",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    gen = MultiverseGenerator()
    cells = gen.generate_all_16_cells()
    
    # Construct a balanced 8-cell half-fraction subset:
    # 4 cells for exact replay (2 VELORA, 2 KESTREL, balanced on root/token/order)
    # 4 cells for seed perturbation (2 VELORA, 2 KESTREL, balanced on root/token/order)
    velora_cells = [c for c in cells if c.station == "VELORA"]
    kestrel_cells = [c for c in cells if c.station == "KESTREL"]
    
    # Pick balanced indices: [0, 3] from VELORA and [1, 2] from KESTREL for exact replay
    exact_replay_cells = [velora_cells[0], velora_cells[3], kestrel_cells[1], kestrel_cells[2]]
    # Pick balanced indices: [1, 2] from VELORA and [0, 3] from KESTREL for seed perturbation
    seed_perturb_cells = [velora_cells[1], velora_cells[2], kestrel_cells[0], kestrel_cells[3]]

    calls_spent = 0
    results = []

    # 1. First Pass: All 16 Factorial Cells (seed=42)
    for cell in cells:
        if calls_spent >= max_calls:
            break

        call_id = f"call_track_b3_{cell.cell_id}_main"
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
                "assay_arm": "main_factorial",
                "seed": 42,
            },
            fail_on_lexical_leak=True,
        )

        emitted = rec.emitted_claim
        follows_majority = (emitted == cell.majority_protocol)
        is_abstention = (emitted == "UNKNOWN")
        phenotype = f"ACTIVE_{emitted}" if not is_abstention else "INACTIVE_UNKNOWN"

        harness.record_evaluation(
            call_id=call_id,
            canonical_status="BEHAVIORAL_EVALUATION",
            local_status="TRUE",
            dual_oracle_phenotype=phenotype,
            is_contract_compliant=True,
            metadata={
                "root_structure": cell.root_structure,
                "token_mapping": cell.token_mapping,
                "doc_order": cell.doc_order,
                "majority_protocol": cell.majority_protocol,
                "emitted": emitted,
                "follows_majority": follows_majority,
                "assay_arm": "main_factorial",
                "seed": 42,
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
            "assay_arm": "main_factorial",
        })
        print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {emitted} (maj={cell.majority_protocol}, follows_maj={follows_majority})", flush=True)
        calls_spent += 1

    # 2. Exact CallSpec Replays: 4 cells with identical seed=42, temp=0.0
    for cell in exact_replay_cells:
        if calls_spent >= max_calls:
            break

        call_id = f"call_track_b3_{cell.cell_id}_exact_replay"
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
                "assay_arm": "exact_replay",
                "seed": 42,
            },
            fail_on_lexical_leak=True,
        )

        emitted = rec.emitted_claim
        follows_majority = (emitted == cell.majority_protocol)
        is_abstention = (emitted == "UNKNOWN")
        phenotype = f"ACTIVE_{emitted}" if not is_abstention else "INACTIVE_UNKNOWN"

        harness.record_evaluation(
            call_id=call_id,
            canonical_status="BEHAVIORAL_EVALUATION",
            local_status="TRUE",
            dual_oracle_phenotype=phenotype,
            is_contract_compliant=True,
            metadata={
                "root_structure": cell.root_structure,
                "token_mapping": cell.token_mapping,
                "doc_order": cell.doc_order,
                "majority_protocol": cell.majority_protocol,
                "emitted": emitted,
                "follows_majority": follows_majority,
                "assay_arm": "exact_replay",
                "seed": 42,
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
            "assay_arm": "exact_replay",
        })
        print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {emitted} (exact_replay)", flush=True)
        calls_spent += 1

    # 3. Seed-Perturbation Replays: 4 cells with seed=43, temp=0.0
    for cell in seed_perturb_cells:
        if calls_spent >= max_calls:
            break

        call_id = f"call_track_b3_{cell.cell_id}_seed_perturb"
        forbidden = ["PROTO_M4", "PROTO_Q7"]

        spec = CallSpec(
            model_name="gemma3:12b",
            system_prompt="You are a precise evidence analysis assistant. Return strictly valid JSON.",
            user_prompt=cell.prompt,
            temperature=0.0,
            seed=43,
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
                "assay_arm": "seed_perturb",
                "seed": 43,
            },
            fail_on_lexical_leak=True,
        )

        emitted = rec.emitted_claim
        follows_majority = (emitted == cell.majority_protocol)
        is_abstention = (emitted == "UNKNOWN")
        phenotype = f"ACTIVE_{emitted}" if not is_abstention else "INACTIVE_UNKNOWN"

        harness.record_evaluation(
            call_id=call_id,
            canonical_status="BEHAVIORAL_EVALUATION",
            local_status="TRUE",
            dual_oracle_phenotype=phenotype,
            is_contract_compliant=True,
            metadata={
                "root_structure": cell.root_structure,
                "token_mapping": cell.token_mapping,
                "doc_order": cell.doc_order,
                "majority_protocol": cell.majority_protocol,
                "emitted": emitted,
                "follows_majority": follows_majority,
                "assay_arm": "seed_perturb",
                "seed": 43,
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
            "assay_arm": "seed_perturb",
        })
        print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {emitted} (seed_perturb)", flush=True)
        calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_b3_multiverse.db")
    print("Running Track B3: Monoculture Factorial Multiverse (24 calls on gemma3:12b)...", flush=True)
    res = run_track_b3_live(db, max_calls=24)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
