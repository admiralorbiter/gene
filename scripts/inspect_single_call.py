"""Milestone B stop-and-inspect script: Execute live Ollama calls on D0 and D1 tasks, log audit trails to SQLite, and mechanically evaluate claims."""

from __future__ import annotations

import json
import os
import sys
from gene.config import ExperimentConfig, ModelConfig
from gene.experiments.runner import SingleCallRunner
from gene.ollama_client import OllamaClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.tasks import TaskGenerator


def run_milestone_b_inspection():
    print("=" * 65)
    print("   GENE MILESTONE B INSPECTION: LIVE AUDITABLE OLLAMA CALL")
    print("=" * 65)

    db_path = "gene_audit_milestone_b.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path)

    # 1. Inspect Ollama Availability
    model_name = "gemma3:12b"
    client = OllamaClient()
    model_info = client.get_model_info(model_name)
    print(f"\n[1] Ollama Model Connection:")
    print(f"    Model: {model_info.model_name}")
    print(f"    Digest: {model_info.digest}")
    print(f"    Parameter Size: {model_info.parameter_size}")
    print(f"    Quantization: {model_info.quantization_level}")

    # 2. Generate Deterministic World
    seed = 42
    world = WorldGenerator.generate(seed=seed)
    oracle = Oracle(world)
    print(f"\n[2] Synthetic World Generated (Seed: {seed}):")
    print(f"    World ID: {world.world_id}")
    print(f"    Validation Hash: {world.validation_hash()[:16]}...")
    print(f"    Facts: {len(world.facts)}, Closure Facts: {len(oracle.closure_facts)}")

    # 3. Generate Benchmark Tasks
    d0_tasks = TaskGenerator.generate_d0_tasks(world, oracle)
    d1_tasks = TaskGenerator.generate_d1_tasks(world, oracle)
    
    test_d0 = d0_tasks[0]
    test_d1 = d1_tasks[0]

    cfg = ExperimentConfig(
        model=ModelConfig(model_name=model_name, temperature=0.0),
        world_seed=seed,
    )
    runner = SingleCallRunner(db=db, client=client, config=cfg)
    run_id = runner.create_run(world=world, condition="clean")
    print(f"\n[3] Experiment Run Initialized:")
    print(f"    Run ID: {run_id}")

    # 4. Execute D0 Task (Direct Source Fact)
    print(f"\n[4] Executing Task 1 (D0 Direct Source Fact)...")
    print(f"    Question: '{test_d0.prompt}'")
    print(f"    Target: ({test_d0.target_fact.subject}, {test_d0.target_fact.predicate}, {test_d0.target_fact.object})")
    
    call_res_0, claim_0 = runner.execute_task(
        run_id=run_id,
        world=world,
        task=test_d0,
        oracle=oracle,
        generation=0,
    )

    print(f"    --> Latency: {call_res_0.latency_ms:.1f}ms | Prompt Tokens: {call_res_0.prompt_tokens} | Completion Tokens: {call_res_0.completion_tokens}")
    print(f"    --> Model Raw Response: {call_res_0.raw_response_text}")
    print(f"    --> Extracted Claim: ({claim_0.subject}, {claim_0.predicate}, {claim_0.object})")
    print(f"    --> Reported Parents: {claim_0.reported_parent_ids}")
    print(f"    --> Oracle Truth Status: {claim_0.truth_status.value.upper()}")
    print(f"    --> Infection Status: {claim_0.infection_status.upper()}")

    # 5. Execute D1 Task (Single-Hop Rule Deduction)
    print(f"\n[5] Executing Task 2 (D1 Rule Inference)...")
    print(f"    Question: '{test_d1.prompt}'")
    print(f"    Target: ({test_d1.target_fact.subject}, {test_d1.target_fact.predicate}, {test_d1.target_fact.object})")
    print(f"    Oracle Valid Support Paths: {test_d1.valid_support_path_ids}")

    call_res_1, claim_1 = runner.execute_task(
        run_id=run_id,
        world=world,
        task=test_d1,
        oracle=oracle,
        generation=1,
    )

    print(f"    --> Latency: {call_res_1.latency_ms:.1f}ms | Prompt Tokens: {call_res_1.prompt_tokens} | Completion Tokens: {call_res_1.completion_tokens}")
    print(f"    --> Model Raw Response: {call_res_1.raw_response_text}")
    print(f"    --> Extracted Claim: ({claim_1.subject}, {claim_1.predicate}, {claim_1.object})")
    print(f"    --> Reported Parents: {claim_1.reported_parent_ids}")
    print(f"    --> Oracle Truth Status: {claim_1.truth_status.value.upper()}")
    print(f"    --> Infection Status: {claim_1.infection_status.upper()}")

    # 6. Database Audit Verification
    print(f"\n[6] Database Audit Verification:")
    calls = db.conn.execute("SELECT call_id, task_id, prompt_tokens, completion_tokens, latency_ms FROM calls WHERE run_id = ?", (run_id,)).fetchall()
    print(f"    Calls recorded in SQLite: {len(calls)}")
    for c in calls:
        print(f"      - {c['call_id']}: task={c['task_id']}, latency={c['latency_ms']:.1f}ms, in_tokens={c['prompt_tokens']}, out_tokens={c['completion_tokens']}")

    claims = db.conn.execute("SELECT claim_id, subject, predicate, object, truth_status, parse_status FROM claims").fetchall()
    print(f"    Claims recorded in SQLite: {len(claims)}")
    for cl in claims:
        print(f"      - {cl['claim_id']}: ({cl['subject']}, {cl['predicate']}, {cl['object']}) -> truth={cl['truth_status']}, parse={cl['parse_status']}")

    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)

    print("\n" + "=" * 65)
    print("   MILESTONE B VERIFICATION COMPLETE AND AUDITABLE!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_milestone_b_inspection()
