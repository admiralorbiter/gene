#!/usr/bin/env python3
"""Experiment 1B-B1c: Matched Path Sufficiency & Expression Assay.

Tests whether G1 derivation asymmetry (2/4 Clean vs 4/4 Infected) is an assay
artifact of prompt labeling / dynamic context or an allele/content phenomenon.

Experimental Design:
- 2 Boundary Worlds: Seed 7000 (VELORA) & Seed 7005 (KESTREL)
- Fixed Context Size: Exactly 6 memories for all conditions
- Stable Model-Facing IDs: mem_{locus_id} and mem_dist_{i}
- 2 Arms: Clean (H) vs Infected (I)
- 2 Tasks: uses_protocol, security_clearance
- 2 Path States:
    - COMPLETE: Full support pair (manager + supervisor) + 4 matched distractors
    - BROKEN:   Manager + 1 replacement distractor (supervisor removed) + 4 matched distractors
- Total Calls: 2 worlds x 2 arms x 2 tasks x 2 path states = 16 calls
"""

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gene.evaluation.dual_oracle import DualOracle
from run_exp1b_retrieval_assay import generate_clutter_distractors
from gene.experiments.runner import get_environment_info
from gene.memory.store import MemoryNode
from gene.ollama_client import CallSpec, FakeOllamaClient, HonestClient, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.schema import Fact, World, compute_fact_id


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def run_exp1b_b1c_matched_expression_assay(
    seed_rotations: list[tuple[int, int]] | None = None,
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    mutated_supervisor: str = "TAL",
    use_fake: bool = False,
    db_path: str | None = None,
):
    """Execute 16-call matched path sufficiency and expression assay."""
    targets = seed_rotations or [(7000, 0), (7005, 5)]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_file = db_path or f"gene_exp1b_b1c_matched_expression_{timestamp}.db"
    db = Database(db_file)
    template = PromptTemplate(version=prompt_version)
    client = HonestClient() if use_fake else OllamaClient()
    git_commit = get_git_commit()

    try:
        model_metadata = client.get_model_info(model_name)
        model_digest = model_metadata.digest if model_metadata else ("fake_digest" if use_fake else "sha256:unknown")
    except Exception:
        model_digest = "fake_digest" if use_fake else "sha256:unknown"

    ollama_version = client.get_version() if hasattr(client, "get_version") else "unknown"
    env_info = get_environment_info()
    prompt_hash = template.template_hash

    print("=" * 145)
    print("      EXPERIMENT 1B-B1c: MATCHED PATH SUFFICIENCY & EXPRESSION ASSAY (16 CALLS)")
    print(f"      (Target Seeds: {targets} | Model: {'FAKE' if use_fake else model_name} | Fixed Context: 6 Memories)")
    print(f"      (Database: {db_file} | Commit: {git_commit[:8]} | Digest: {model_digest[:16]})")
    print("=" * 145)

    results_table = []
    total_calls = 0

    for w_idx, (seed, rot) in enumerate(targets):
        bundle = generate_exp1_branching_world(world_seed=seed, rotation_idx=rot, mutated_supervisor=mutated_supervisor)
        db.save_world(bundle.clean_world)
        db.save_world(bundle.mutated_world)
        station = bundle.station

        # Pre-generate 6 distractors (2 easy, 4 hard) for clean replacement
        easy_facts, hard_facts = generate_clutter_distractors(station, easy_count=3, hard_count=5, seed=seed)

        for arm in ["clean", "infected"]:
            is_infected_arm = (arm == "infected")
            current_world = bundle.mutated_world if is_infected_arm else bundle.clean_world
            founder_fact = bundle.mutated_founder_fact if is_infected_arm else bundle.clean_founder_fact
            founder_sup = founder_fact.object

            # Identify manager fact
            mgr_fact = [f for f in current_world.facts if f.predicate == "manager"][0]

            for path_state in ["complete", "broken"]:
                run_id = f"exp1b_b1c_{arm}_w{w_idx}_{path_state}"
                config_dict = {
                    "experiment": "exp1b_b1c",
                    "arm": arm,
                    "world_idx": w_idx,
                    "seed": seed,
                    "rotation": rot,
                    "path_state": path_state,
                    "fixed_context_size": 6,
                    "model": model_name,
                    "mutated_supervisor": mutated_supervisor,
                }
                config_json = json.dumps(config_dict, sort_keys=True)
                config_hash = hashlib.sha256(config_json.encode()).hexdigest()[:16]

                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO runs (
                            run_id, experiment_name, experiment_version, condition, world_id,
                            model_name, model_digest, ollama_version, seed, num_ctx, temperature,
                            prompt_version, prompt_hash, retrieval_policy, memory_policy, git_commit,
                            config_json, config_hash, environment_json, started_at, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        run_id, "exp1b_b1c", "v1", f"{arm}_{path_state}", current_world.world_id,
                        model_name, model_digest, ollama_version, seed, 4096, 0.0,
                        prompt_version, prompt_hash, f"fixed_6_{path_state}", "matched_slots", git_commit,
                        config_json, config_hash, json.dumps(env_info), datetime.now(timezone.utc).isoformat(), "running"
                    ))

                # Assemble strictly matched 6-memory context
                # Position 0: Station manager fact
                # Position 1: Supervisor founder fact (if complete) OR replacement distractor (if broken)
                # Position 2..5: 4 standard distractors
                memories = []
                ctx_facts = [mgr_fact]

                mem_mgr = {
                    "memory_id": f"mem_{mgr_fact.locus_id}",
                    "text": NaturalLanguageRenderer.render_fact(mgr_fact),
                }
                memories.append(mem_mgr)

                if path_state == "complete":
                    mem_sup = {
                        "memory_id": f"mem_{founder_fact.locus_id}",
                        "text": NaturalLanguageRenderer.render_fact(founder_fact),
                    }
                    memories.append(mem_sup)
                    ctx_facts.append(founder_fact)
                else:
                    # Broken path: replace founder fact with matched replacement distractor
                    repl_fact = hard_facts[0]
                    mem_repl = {
                        "memory_id": f"mem_{repl_fact.locus_id}",
                        "text": NaturalLanguageRenderer.render_fact(repl_fact),
                    }
                    memories.append(mem_repl)
                    ctx_facts.append(repl_fact)

                # Append 4 clutter distractors (positions 2..5)
                distractors = hard_facts[1:4] + easy_facts[:1]
                for d_idx, d_f in enumerate(distractors):
                    memories.append({
                        "memory_id": f"mem_{d_f.locus_id}",
                        "text": NaturalLanguageRenderer.render_fact(d_f),
                    })
                    ctx_facts.append(d_f)

                # Add rules to prompt
                prompt_memories = list(memories)
                for j, r in enumerate(bundle.g1_rules):
                    prompt_memories.append({"memory_id": f"rule_g1_{j}", "text": NaturalLanguageRenderer.render_rule(r)})

                # Build DualOracle context world
                g1_ctx_world = World(
                    world_id=f"ctx_{run_id}",
                    world_seed=seed,
                    world_version=prompt_version,
                    facts=ctx_facts,
                    rules=bundle.g1_rules,
                )
                dual_oracle_g1 = DualOracle(
                    canonical_world=bundle.clean_world,
                    context_world=g1_ctx_world,
                    ancestral_seed_allele=founder_sup,
                    allele_decoder=bundle.allele_decoder,
                )

                for task in bundle.g1_tasks:
                    total_calls += 1
                    call_id = f"call_{run_id}_{task.target_fact.predicate}"

                    prompt = template.format_user_prompt(
                        memories=prompt_memories,
                        question_prompt=task.prompt,
                        target_subject=task.target_fact.subject,
                        target_predicate=task.target_fact.predicate,
                    )
                    spec = CallSpec(
                        model_name=model_name,
                        system_prompt=template.system_prompt,
                        user_prompt=prompt,
                        temperature=0.0,
                        seed=42,
                        format=template.format_schema,
                    )
                    start_time = time.time()
                    res = client.chat(spec)
                    latency_ms = int((time.time() - start_time) * 1000)

                    eval_res = dual_oracle_g1.evaluate_response(
                        raw_text=res.raw_response_text,
                        parsed_json=res.parsed_json,
                        task=task,
                        has_infected_ancestry=is_infected_arm and (path_state == "complete"),
                    )

                    locus_id = f"locus_{task.target_fact.predicate}"
                    allele_id = compute_fact_id(station, task.target_fact.predicate, eval_res.normalized_object)
                    node_id = f"node_{run_id}_{call_id}_{locus_id}_{allele_id[:8]}"
                    is_written = (eval_res.normalized_object not in ("UNKNOWN", "NONE", ""))

                    # Persist call
                    with db.conn:
                        db.conn.execute("""
                            INSERT OR REPLACE INTO calls (
                                call_id, run_id, generation, task_id, request_json, response_text,
                                response_json, prompt_tokens, completion_tokens, latency_ms,
                                load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            call_id, run_id, 1, task.task_id, json.dumps(spec.to_request_payload()),
                            res.raw_response_text, json.dumps(res.parsed_json),
                            res.prompt_tokens, res.completion_tokens,
                            res.latency_ms if res.latency_ms > 0 else latency_ms,
                            res.load_duration_ms, res.prompt_eval_duration_ms, res.eval_duration_ms,
                            datetime.now(timezone.utc).isoformat()
                        ))

                    # Persist memory node
                    if is_written:
                        derived_fact = Fact(
                            subject=station,
                            predicate=task.target_fact.predicate,
                            object=eval_res.normalized_object,
                            truth_value=True,
                            source_type="derived",
                            locus_id=locus_id,
                        )
                        derived_text = f"Station {station} {task.target_fact.predicate} is {eval_res.normalized_object}."
                        with db.conn:
                            db.conn.execute("""
                                INSERT OR REPLACE INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_by_call_id, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (node_id, run_id, current_world.world_id, 1, "derived", derived_text, json.dumps(derived_fact.model_dump()), locus_id, allele_id, 1, 0, call_id, datetime.now(timezone.utc).isoformat()))
                    else:
                        derived_text = f"Station {station} {task.target_fact.predicate} is UNKNOWN."
                        with db.conn:
                            db.conn.execute("""
                                INSERT OR REPLACE INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, reproductive_status, created_by_call_id, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (node_id, run_id, current_world.world_id, 1, "derived", derived_text, json.dumps({"subject": station, "predicate": task.target_fact.predicate, "object": "UNKNOWN"}), locus_id, allele_id, 0, 0, "inactive", call_id, datetime.now(timezone.utc).isoformat()))

                    # Persist evaluation
                    with db.conn:
                        eval_id = f"eval_{call_id}"
                        db.conn.execute("""
                            INSERT OR REPLACE INTO dual_oracle_evaluations (
                                evaluation_id, call_id, node_id, generation, task_id, target_subject, target_predicate, derived_object, canonical_truth_status,
                                local_derivability_status, A_correct, E_correct, K_consistent, phenotype,
                                state_vector_json, ancestral_allele_fidelity, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            eval_id, call_id, node_id, 1, task.task_id, task.target_fact.subject, task.target_fact.predicate, eval_res.normalized_object,
                            eval_res.canonical_truth_status, eval_res.context_truth_status,
                            1 if eval_res.A_correct else 0, 1 if eval_res.E_correct else 0,
                            1 if eval_res.K_consistent else 0, eval_res.phenotype, json.dumps(eval_res.state_vector),
                            eval_res.ancestral_allele_fidelity, datetime.now(timezone.utc).isoformat()
                        ))

                    ev_status = res.parsed_json.get("evidence_status", "unknown") if res.parsed_json else "unknown"
                    results_table.append({
                        "world": f"W{w_idx} ({station})",
                        "arm": arm.upper(),
                        "path": path_state.upper(),
                        "predicate": task.target_fact.predicate,
                        "ev_status": ev_status,
                        "derived": eval_res.normalized_object,
                        "d_ctx": eval_res.context_derivability,
                        "phenotype": eval_res.phenotype,
                        "active": 1 if is_written else 0,
                        "latency": latency_ms,
                    })

                    print(f"  [{arm.upper():<8} | {path_state.upper():<8}] {task.target_fact.predicate:<18} -> Ev: {ev_status:<12} | Obj: {eval_res.normalized_object:<18} | D_ctx={eval_res.context_derivability} | Phenotype: {eval_res.phenotype.upper()}", flush=True)

                db.update_run_status(run_id, status="completed", completed_at=datetime.now(timezone.utc).isoformat())

    print("\n" + "=" * 145)
    print("      EXPERIMENT 1B-B1c: MATCHED PATH EXPRESSION LEDGER")
    print("=" * 145)
    print(f"{'World':<16} | {'Arm':<8} | {'Path':<10} | {'Predicate':<18} | {'Ev Status':<12} | {'Derived Object':<18} | {'D_ctx':<6} | {'Phenotype':<12} | {'Active':<6}")
    print("-" * 145)
    for r in results_table:
        print(f"{r['world']:<16} | {r['arm']:<8} | {r['path']:<10} | {r['predicate']:<18} | {r['ev_status']:<12} | {r['derived']:<18} | {r['d_ctx']:<6} | {r['phenotype']:<12} | {r['active']:<6}")
    print("=" * 145)

    # Summary table
    print("\n" + "=" * 105)
    print("                                CONDITION SUMMARY (N=16 CALLS)")
    print("=" * 105)
    summary_q = """
    SELECT 
        r.condition,
        COUNT(*) as total_calls,
        SUM(CASE WHEN e.phenotype != 'extinct' THEN 1 ELSE 0 END) as written_calls,
        SUM(CASE WHEN e.phenotype = 'healthy' THEN 1 ELSE 0 END) as healthy_calls,
        SUM(CASE WHEN e.phenotype = 'semantic' THEN 1 ELSE 0 END) as semantic_calls,
        SUM(CASE WHEN e.phenotype = 'extinct' THEN 1 ELSE 0 END) as abstentions
    FROM dual_oracle_evaluations e
    JOIN calls c ON e.call_id = c.call_id
    JOIN runs r ON c.run_id = r.run_id
    GROUP BY r.condition
    ORDER BY r.condition;
    """
    with db.conn:
        s_rows = db.conn.execute(summary_q).fetchall()
        print(f"{'Condition':<20} | {'Total Calls':<12} | {'Written (Active)':<18} | {'Healthy':<10} | {'Semantic':<10} | {'Abstentions':<12}")
        print("-" * 105)
        for s in s_rows:
            print(f"{s['condition']:<20} | {s['total_calls']:<12} | {s['written_calls']:<18} | {s['healthy_calls']:<10} | {s['semantic_calls']:<10} | {s['abstentions']:<12}")
        print("=" * 105 + "\n")

    db.close()
    return results_table


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B-B1c Matched Path Assay")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model family to assay")
    parser.add_argument("--fake", action="store_true", help="Use deterministic HonestClient")
    parser.add_argument("--db", type=str, default=None, help="Custom SQLite database path")
    args = parser.parse_args()

    run_exp1b_b1c_matched_expression_assay(
        model_name=args.model,
        use_fake=args.fake,
        db_path=args.db,
    )
