"""Experiment 1B-C2 / C2a: Live Behavioral Immunity & Replay Stability Assay.

Evaluates:
1. Complete 4-State Discrete Panel (States 00, 01, 10, 11 + node_only + generation_matched across 2 ecologies = 24 calls)
2. Replay Stability Assay (10x Swapped Broken + 10x Forward Broken = 20 calls)
3. Cross-Entity Binding Factorial Manipulation (3x Foreign Route Present vs 3x Foreign Route Removed = 6 calls)
Total: 50 Live Calls on Gemma 3:12B with structured DualOracle evaluation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.evaluation.dual_oracle import DualOracle
from gene.experiments.runner import get_environment_info
from gene.memory.store import MemoryNode
from gene.ollama_client import CallSpec, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.exp1_branching import STATIONS, generate_exp1_branching_world
from gene.worlds.schema import Fact, Rule, Task, World, compute_fact_id


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def build_c2_structures(
    station_h: str,
    station_i: str,
    context_type: str,
    seed: int = 7000,
    competing_route_override: bool = True,
) -> tuple[list[dict[str, str]], World, World, list[Task], str]:
    """Construct structured Facts, Rules, Tasks, Canonical/Context Worlds, and prompt memories."""
    idx_h = STATIONS.index(station_h)
    grid_h = f"GRID_{idx_h}"
    route_h_clean = f"ROUTE_SWIFT_{station_h}"
    auth_h_clean = f"AUTH_ALPHA_{station_h}"

    idx_i = STATIONS.index(station_i)
    grid_i = f"GRID_{idx_i}"
    route_i_mut = f"ROUTE_SLIP_{station_i}"
    auth_i_mut = f"AUTH_BETA_{station_i}"

    route_foil = "ROUTE_DRIFT_NEUTRAL"
    auth_foil = "AUTH_GAMMA_NEUTRAL"

    # Canonical Facts
    f_h_route = Fact(subject=station_h, predicate="transit_route", object=route_h_clean, locus_id=f"{station_h}_locus_transit_route")
    f_h_grid = Fact(subject=station_h, predicate="facility_grid", object=grid_h, locus_id=f"{station_h}_locus_facility_grid")
    f_i_route = Fact(subject=station_i, predicate="transit_route", object=route_i_mut, locus_id=f"{station_i}_locus_transit_route")
    f_i_grid = Fact(subject=station_i, predicate="facility_grid", object=grid_i, locus_id=f"{station_i}_locus_facility_grid")

    # Distractor Facts
    dist_0 = Fact(subject="OUTPOST_0", predicate="commissioned_epoch", object="2180")
    dist_1 = Fact(subject="OUTPOST_1", predicate="commissioned_epoch", object="2181")
    dist_2 = Fact(subject="OUTPOST_2", predicate="commissioned_epoch", object="2182")
    dist_3 = Fact(subject="OUTPOST_3", predicate="commissioned_epoch", object="2183")

    # Authorization Rules
    r_h = Rule(
        rule_id=f"rule_auth_{station_h.lower()}",
        antecedents=[("?s", "transit_route", route_h_clean), ("?s", "facility_grid", grid_h)],
        consequent=("?s", "terminal_auth", auth_h_clean),
        depth=3,
    )
    r_i = Rule(
        rule_id=f"rule_auth_{station_i.lower()}",
        antecedents=[("?s", "transit_route", route_i_mut), ("?s", "facility_grid", grid_i)],
        consequent=("?s", "terminal_auth", auth_i_mut),
        depth=3,
    )
    r_foil = Rule(
        rule_id="rule_auth_neutral",
        antecedents=[("?s", "transit_route", route_foil), ("?s", "facility_grid", "GRID_9")],
        consequent=("?s", "terminal_auth", auth_foil),
        depth=3,
    )
    rules = [r_h, r_i, r_foil]

    rules_text = (
        f"Domain Authorization Rules:\n"
        f"1. If a station operates along transit route {route_h_clean} and is assigned to facility grid {grid_h}, its terminal_auth code is {auth_h_clean}.\n"
        f"2. If a station operates along transit route {route_i_mut} and is assigned to facility grid {grid_i}, its terminal_auth code is {auth_i_mut}.\n"
        f"3. If a station operates along transit route {route_foil} and is assigned to facility grid GRID_9, its terminal_auth code is {auth_foil}.\n"
    )

    # Canonical World (Contains All Legitimate Facts + Rules)
    canonical_world = World(
        world_id=f"canonical_{station_h}_{station_i}",
        world_seed=seed,
        world_version="v2",
        facts=[f_h_route, f_h_grid, f_i_route, f_i_grid, dist_0, dist_1, dist_2, dist_3],
        rules=rules,
    )

    # Tasks
    t_clean = Task(
        task_id=f"task_auth_{station_h.lower()}",
        world_id=canonical_world.world_id,
        query_type="rule_inference",
        target_fact=Fact(subject=station_h, predicate="terminal_auth", object=auth_h_clean),
        reasoning_depth=3,
        prompt=f"{rules_text}\nQuestion: What is the terminal_auth code for station {station_h}?",
        expected_answer=auth_h_clean,
    )
    t_mutated = Task(
        task_id=f"task_auth_{station_i.lower()}",
        world_id=canonical_world.world_id,
        query_type="rule_inference",
        target_fact=Fact(subject=station_i, predicate="terminal_auth", object=auth_i_mut),
        reasoning_depth=3,
        prompt=f"{rules_text}\nQuestion: What is the terminal_auth code for station {station_i}?",
        expected_answer=auth_i_mut,
    )
    tasks = [t_clean, t_mutated]

    # Memory Dicts
    mem_h_route = {"memory_id": f"mem_{station_h.lower()}_transit_route", "text": f"Station {station_h} operates along transit route {route_h_clean}."}
    mem_h_grid = {"memory_id": f"mem_{station_h.lower()}_facility_grid", "text": f"Station {station_h} is assigned to facility grid {grid_h}."}
    mem_i_route = {"memory_id": f"mem_{station_i.lower()}_transit_route", "text": f"Station {station_i} operates along transit route {route_i_mut}."}
    mem_i_grid = {"memory_id": f"mem_{station_i.lower()}_facility_grid", "text": f"Station {station_i} is assigned to facility grid {grid_i}."}

    m_dist_0 = {"memory_id": "mem_distractor_0", "text": "Sector outpost 0 was commissioned in standard epoch 2180."}
    m_dist_1 = {"memory_id": "mem_distractor_1", "text": "Sector outpost 1 was commissioned in standard epoch 2181."}
    m_dist_2 = {"memory_id": "mem_distractor_2", "text": "Sector outpost 2 was commissioned in standard epoch 2182."}
    m_dist_3 = {"memory_id": "mem_distractor_3", "text": "Sector outpost 3 was commissioned in standard epoch 2183."}

    # Context Assembly based on post-policy state
    if context_type == "baseline":
        # 00: Both complete
        memories = [mem_h_route, mem_h_grid, mem_i_route, mem_i_grid, m_dist_1, m_dist_2]
        ctx_facts = [f_h_route, f_h_grid, f_i_route, f_i_grid, dist_1, dist_2]
    elif context_type == "node_only":
        # Root I_0 dropped, but G2 route intact -> Both complete
        memories = [mem_h_route, mem_h_grid, mem_i_route, mem_i_grid, m_dist_1, m_dist_2]
        ctx_facts = [f_h_route, f_h_grid, f_i_route, f_i_grid, dist_1, dist_2]
    elif context_type == "lineage_quarantine":
        # 01: Infected root + descendants dropped -> Clean complete, Mutated broken
        memories = [mem_h_route, mem_h_grid, m_dist_0, mem_i_grid, m_dist_1, m_dist_2]
        ctx_facts = [f_h_route, f_h_grid, dist_0, f_i_grid, dist_1, dist_2]
    elif context_type == "autoimmunity":
        # 10: Clean root + descendants dropped -> Clean broken, Mutated complete
        i_route_mem = mem_i_route if competing_route_override else m_dist_3
        i_route_fact = f_i_route if competing_route_override else dist_3
        memories = [m_dist_0, mem_h_grid, i_route_mem, mem_i_grid, m_dist_1, m_dist_2]
        ctx_facts = [dist_0, f_h_grid, i_route_fact, f_i_grid, dist_1, dist_2]
    elif context_type == "generation_matched":
        # Random G2 dropped -> Clean broken, Mutated complete
        memories = [m_dist_0, mem_h_grid, mem_i_route, mem_i_grid, m_dist_1, m_dist_2]
        ctx_facts = [dist_0, f_h_grid, f_i_route, f_i_grid, dist_1, dist_2]
    elif context_type == "double_quarantine":
        # 11: Both roots flagged -> Both Clean and Mutated broken
        memories = [m_dist_0, mem_h_grid, m_dist_3, mem_i_grid, m_dist_1, m_dist_2]
        ctx_facts = [dist_0, f_h_grid, dist_3, f_i_grid, dist_1, dist_2]
    else:
        raise ValueError(f"Unknown context_type: {context_type}")

    context_world = World(
        world_id=f"ctx_{station_h}_{station_i}_{context_type}",
        world_seed=seed,
        world_version="v2",
        facts=ctx_facts,
        rules=rules,
    )

    return memories, canonical_world, context_world, tasks, rules_text


def execute_call_with_oracle(
    client: OllamaClient | None,
    template: PromptTemplate,
    db: Database,
    run_id: str,
    call_id: str,
    task: Task,
    memories: list[dict[str, str]],
    canonical_world: World,
    context_world: World,
    model_name: str,
    model_digest: str,
    use_fake: bool = False,
    is_infected_arm: bool = False,
) -> dict[str, Any]:
    """Execute a single LLM call, evaluate under DualOracle, and persist complete audit trail."""
    prompt = template.format_user_prompt(
        memories=memories,
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

    prompt_req_payload = json.dumps(spec.to_request_payload())
    prompt_hash = hashlib.sha256(prompt_req_payload.encode()).hexdigest()[:12]

    # Context derivability check
    mem_ids = {m["memory_id"] for m in memories}
    route_id = f"mem_{task.target_fact.subject.lower()}_transit_route"
    grid_id = f"mem_{task.target_fact.subject.lower()}_facility_grid"
    path_is_complete = (route_id in mem_ids and grid_id in mem_ids)

    start_time = time.time()
    if use_fake:
        if path_is_complete:
            raw_json = json.dumps({
                "evidence_status": "sufficient",
                "answer": {
                    "subject": task.target_fact.subject,
                    "predicate": task.target_fact.predicate,
                    "object": task.expected_answer,
                },
                "parent_memory_ids": [route_id, grid_id],
            })
        else:
            raw_json = json.dumps({
                "evidence_status": "insufficient",
                "answer": {
                    "subject": task.target_fact.subject,
                    "predicate": task.target_fact.predicate,
                    "object": "UNKNOWN",
                },
                "parent_memory_ids": [],
            })
        latency_ms = 5.0
        prompt_tokens = 250
        eval_tokens = 40
    else:
        assert client is not None
        resp = client.chat(spec)
        raw_json = resp.raw_response_text
        latency_ms = float(resp.latency_ms) if resp.latency_ms else (time.time() - start_time) * 1000.0
        prompt_tokens = resp.prompt_tokens
        eval_tokens = resp.completion_tokens

    # Parse JSON
    try:
        parsed = json.loads(raw_json)
    except Exception:
        parsed = None

    # DualOracle Evaluation
    dual_oracle = DualOracle(canonical_world=canonical_world, context_world=context_world)
    eval_res = dual_oracle.evaluate_response(
        raw_text=raw_json,
        parsed_json=parsed,
        task=task,
        has_infected_ancestry=is_infected_arm,
    )

    # Persist Call Record
    with db.conn:
        db.conn.execute("""
            INSERT OR REPLACE INTO calls (
                call_id, run_id, generation, task_id, request_json,
                response_text, response_json, prompt_tokens,
                completion_tokens, latency_ms, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            call_id, run_id, 3, task.task_id, prompt_req_payload,
            raw_json, raw_json, prompt_tokens, eval_tokens,
            latency_ms, datetime.now(timezone.utc).isoformat()
        ))

    # Persist Output Memory Node
    is_active = (eval_res.normalized_object != "UNKNOWN" and eval_res.raw_evidence_status == "sufficient")
    out_node_id = f"node_{call_id}"
    with db.conn:
        db.conn.execute("""
            INSERT OR REPLACE INTO memory_nodes (
                node_id, run_id, world_id, generation, node_type,
                natural_text, locus_id, allele_id, is_active,
                created_by_call_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            out_node_id, run_id, canonical_world.world_id, 3,
            "derived" if is_active else "inactive",
            f"Station {task.target_fact.subject} terminal_auth code is {eval_res.normalized_object}.",
            f"{task.target_fact.subject}_locus_terminal_auth",
            eval_res.normalized_object, 1 if is_active else 0,
            call_id, datetime.now(timezone.utc).isoformat()
        ))

    # Persist DualOracle Evaluation Record
    eval_id = f"eval_{call_id}"
    with db.conn:
        db.conn.execute("""
            INSERT OR REPLACE INTO dual_oracle_evaluations (
                evaluation_id, call_id, node_id, generation, task_id,
                target_subject, target_predicate, derived_object,
                canonical_truth_status, local_derivability_status,
                A_correct, E_correct, K_consistent, phenotype,
                state_vector_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            eval_id, call_id, out_node_id, 3, task.task_id,
            task.target_fact.subject, task.target_fact.predicate,
            eval_res.normalized_object, eval_res.canonical_truth_status,
            eval_res.context_truth_status, eval_res.A_correct,
            eval_res.E_correct, eval_res.K_consistent, eval_res.phenotype,
            json.dumps(eval_res.state_vector), datetime.now(timezone.utc).isoformat()
        ))

    return {
        "call_id": call_id,
        "run_id": run_id,
        "task_id": task.task_id,
        "target_subject": task.target_fact.subject,
        "prompt_hash": prompt_hash,
        "path_is_complete": path_is_complete,
        "emitted_object": eval_res.normalized_object,
        "expected_object": task.expected_answer,
        "evidence_status": eval_res.raw_evidence_status,
        "state_vector": eval_res.state_vector,
        "phenotype": eval_res.phenotype,
        "A_correct": eval_res.A_correct,
        "E_correct": eval_res.E_correct,
        "K_consistent": eval_res.K_consistent,
        "latency_ms": latency_ms,
    }


def run_exp1b_c2a_suite(
    mode: str = "all",
    model_name: str = "gemma3:12b",
    use_fake: bool = False,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Execute Experiment 1B-C2a comprehensive test suite."""
    git_commit = get_git_commit()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_file = db_path or f"gene_exp1b_c2a_live_assay_{timestamp}.db"
    db = Database(Path(db_file))

    template = PromptTemplate(version="v2")
    prompt_hash = template.prompt_hash()

    client = None
    model_digest = "fake_digest"
    ollama_version = "unknown"
    if not use_fake:
        client = OllamaClient()
        try:
            m_info = client.get_model_info(model_name)
            model_digest = m_info.digest if m_info else "sha256:unknown"
            ollama_version = client.get_version()
        except Exception:
            pass

    env_info = get_environment_info()

    ecologies = [
        {"eco_id": "eco_fwd", "station_h": "VELORA", "station_i": "KESTREL", "role": "forward", "seed": 7000},
        {"eco_id": "eco_swap", "station_h": "KESTREL", "station_i": "VELORA", "role": "swapped", "seed": 7000},
    ]

    all_results = []
    total_calls = 0

    print("=" * 155)
    print("      EXPERIMENT 1B-C2a: LIVE BEHAVIORAL IMMUNITY, REPLAY STABILITY & CROSS-BINDING ASSAY")
    print(f"      (Mode: {mode.upper()} | Model: {'FAKE' if use_fake else model_name} | Commit: {git_commit[:8]} | DB: {db_file})")
    print("=" * 155)

    # -------------------------------------------------------------
    # PANEL 1: Complete 4-State Discrete Panel (24 Calls)
    # -------------------------------------------------------------
    if mode in ("discrete", "all"):
        print("\n>>> EXECUTING PANEL 1: COMPLETE 4-STATE DISCRETE PANEL (24 CALLS) <<<")
        contexts = [
            "baseline",           # State 00
            "node_only",          # G0 dropped, G2 present
            "lineage_quarantine", # State 01
            "autoimmunity",       # State 10
            "generation_matched", # Generation control
            "double_quarantine",  # State 11 (Both roots quarantined)
        ]

        for eco in ecologies:
            st_h = eco["station_h"]
            st_i = eco["station_i"]
            role = eco["role"]
            seed = eco["seed"]

            idx_h = STATIONS.index(st_h)
            idx_i = STATIONS.index(st_i)
            b_h = generate_exp1_branching_world(7000 + idx_h, 0)
            b_i = generate_exp1_branching_world(7000 + idx_i, 0)
            db.save_world(b_h.clean_world)
            db.save_world(b_h.mutated_world)
            db.save_world(b_i.clean_world)
            db.save_world(b_i.mutated_world)

            for ctx in contexts:
                run_id = f"c2a_panel1_{role}_{ctx}"
                memories, can_world, ctx_world, tasks, _ = build_c2_structures(st_h, st_i, ctx, seed=seed)
                db.save_world(can_world)
                db.save_world(ctx_world)

                cfg_dict = {"panel": "discrete_4state", "role": role, "station_h": st_h, "station_i": st_i, "context": ctx, "model": model_name}
                cfg_json = json.dumps(cfg_dict, sort_keys=True)
                cfg_hash = hashlib.sha256(cfg_json.encode()).hexdigest()[:16]

                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO runs (
                            run_id, experiment_name, experiment_version, condition, world_id,
                            model_name, model_digest, ollama_version, seed, num_ctx, temperature,
                            prompt_version, prompt_hash, retrieval_policy, memory_policy, git_commit,
                            config_json, config_hash, environment_json, started_at, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        run_id, "exp1b_c2a", "v1", f"{role}_{ctx}", can_world.world_id,
                        model_name, model_digest, ollama_version, seed, 4096, 0.0,
                        "v2", prompt_hash, f"c2a_{ctx}", "matched_6_slots", git_commit,
                        cfg_json, cfg_hash, json.dumps(env_info), datetime.now(timezone.utc).isoformat(), "running"
                    ))

                for t_idx, task in enumerate(tasks):
                    total_calls += 1
                    arm = "clean" if t_idx == 0 else "mutated"
                    call_id = f"call_{run_id}_{arm}"

                    res = execute_call_with_oracle(
                        client=client,
                        template=template,
                        db=db,
                        run_id=run_id,
                        call_id=call_id,
                        task=task,
                        memories=memories,
                        canonical_world=can_world,
                        context_world=ctx_world,
                        model_name=model_name,
                        model_digest=model_digest,
                        use_fake=use_fake,
                        is_infected_arm=(arm == "mutated"),
                    )
                    res["panel"] = "discrete_4state"
                    res["role"] = role
                    res["context"] = ctx
                    res["arm"] = arm
                    all_results.append(res)

                    status_str = "ACTIVE" if res["emitted_object"] != "UNKNOWN" else "UNKNOWN"
                    print(
                        f"[{total_calls:02d}/50] [Panel 1] Role: {role:<7} | Ctx: {ctx:<19} | Arm: {arm:<7} | "
                        f"Target: {task.target_fact.subject:<7} | Hash: {res['prompt_hash']} | "
                        f"Path: {'COMPLETE' if res['path_is_complete'] else 'BROKEN':<8} | "
                        f"State: {str(res['state_vector']):<15} | Phenotype: {res['phenotype']:<12} | "
                        f"Emitted: {res['emitted_object']:<20} ({int(res['latency_ms'])}ms)"
                    )

                with db.conn:
                    db.conn.execute("UPDATE runs SET status = 'completed', completed_at = ? WHERE run_id = ?", (
                        datetime.now(timezone.utc).isoformat(), run_id
                    ))

    # -------------------------------------------------------------
    # PANEL 2: Replay Stability Assay (20 Calls: 10x Swapped + 10x Forward)
    # -------------------------------------------------------------
    if mode in ("replay", "all"):
        print("\n>>> EXECUTING PANEL 2: REPLAY STABILITY ASSAY (20 CALLS) <<<")
        replay_targets = [
            ("swapped", "KESTREL", "VELORA", "autoimmunity", 0), # Swapped Clean broken (Hash 168def247468)
            ("forward", "VELORA", "KESTREL", "autoimmunity", 0), # Forward Clean broken (Hash b3b6d5e4ae85)
        ]

        for role, st_h, st_i, ctx, t_idx in replay_targets:
            memories, can_world, ctx_world, tasks, _ = build_c2_structures(st_h, st_i, ctx, seed=7000)
            target_task = tasks[t_idx]
            run_id = f"c2a_replay_{role}_{target_task.target_fact.subject}"

            cfg_dict = {"panel": "replay_stability", "role": role, "target": target_task.target_fact.subject}
            cfg_json = json.dumps(cfg_dict, sort_keys=True)
            cfg_hash = hashlib.sha256(cfg_json.encode()).hexdigest()[:16]

            with db.conn:
                db.conn.execute("""
                    INSERT OR REPLACE INTO runs (
                        run_id, experiment_name, experiment_version, condition, world_id,
                        model_name, model_digest, ollama_version, seed, num_ctx, temperature,
                        prompt_version, prompt_hash, retrieval_policy, memory_policy, git_commit,
                        config_json, config_hash, environment_json, started_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id, "exp1b_c2a", "v1", f"replay_{role}", can_world.world_id,
                    model_name, model_digest, ollama_version, 7000, 4096, 0.0,
                    "v2", prompt_hash, "replay_stability", "matched_6_slots", git_commit,
                    cfg_json, cfg_hash, json.dumps(env_info), datetime.now(timezone.utc).isoformat(), "running"
                ))

            for rep in range(10):
                total_calls += 1
                call_id = f"call_{run_id}_rep{rep:02d}"

                res = execute_call_with_oracle(
                    client=client,
                    template=template,
                    db=db,
                    run_id=run_id,
                    call_id=call_id,
                    task=target_task,
                    memories=memories,
                    canonical_world=can_world,
                    context_world=ctx_world,
                    model_name=model_name,
                    model_digest=model_digest,
                    use_fake=use_fake,
                    is_infected_arm=False,
                )
                res["panel"] = "replay_stability"
                res["role"] = role
                res["context"] = f"replay_{rep}"
                res["arm"] = "clean"
                all_results.append(res)

                print(
                    f"[{total_calls:02d}/50] [Panel 2 Replay] Role: {role:<7} | Rep: {rep:02d}/10 | "
                    f"Target: {target_task.target_fact.subject:<7} | Hash: {res['prompt_hash']} | "
                    f"State: {str(res['state_vector']):<15} | Phenotype: {res['phenotype']:<12} | "
                    f"Emitted: {res['emitted_object']:<20} ({int(res['latency_ms'])}ms)"
                )

            with db.conn:
                db.conn.execute("UPDATE runs SET status = 'completed', completed_at = ? WHERE run_id = ?", (
                    datetime.now(timezone.utc).isoformat(), run_id
                ))

    # -------------------------------------------------------------
    # PANEL 3: Cross-Entity Binding Factorial Manipulation (6 Calls)
    # -------------------------------------------------------------
    if mode in ("factorial", "all"):
        print("\n>>> EXECUTING PANEL 3: CROSS-ENTITY BINDING FACTORIAL ASSAY (6 CALLS) <<<")
        st_h = "KESTREL"
        st_i = "VELORA"

        for cond_name, foreign_route_present in [("foreign_route_present", True), ("foreign_route_removed", False)]:
            memories, can_world, ctx_world, tasks, _ = build_c2_structures(
                st_h, st_i, "autoimmunity", seed=7000, competing_route_override=foreign_route_present
            )
            target_task = tasks[0] # Clean broken task for KESTREL
            run_id = f"c2a_factorial_{cond_name}"

            cfg_dict = {"panel": "factorial_binding", "condition": cond_name, "foreign_present": foreign_route_present}
            cfg_json = json.dumps(cfg_dict, sort_keys=True)
            cfg_hash = hashlib.sha256(cfg_json.encode()).hexdigest()[:16]

            with db.conn:
                db.conn.execute("""
                    INSERT OR REPLACE INTO runs (
                        run_id, experiment_name, experiment_version, condition, world_id,
                        model_name, model_digest, ollama_version, seed, num_ctx, temperature,
                        prompt_version, prompt_hash, retrieval_policy, memory_policy, git_commit,
                        config_json, config_hash, environment_json, started_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id, "exp1b_c2a", "v1", cond_name, can_world.world_id,
                    model_name, model_digest, ollama_version, 7000, 4096, 0.0,
                    "v2", prompt_hash, cond_name, "matched_6_slots", git_commit,
                    cfg_json, cfg_hash, json.dumps(env_info), datetime.now(timezone.utc).isoformat(), "running"
                ))

            for rep in range(3):
                total_calls += 1
                call_id = f"call_{run_id}_rep{rep:02d}"

                res = execute_call_with_oracle(
                    client=client,
                    template=template,
                    db=db,
                    run_id=run_id,
                    call_id=call_id,
                    task=target_task,
                    memories=memories,
                    canonical_world=can_world,
                    context_world=ctx_world,
                    model_name=model_name,
                    model_digest=model_digest,
                    use_fake=use_fake,
                    is_infected_arm=False,
                )
                res["panel"] = "factorial_binding"
                res["role"] = cond_name
                res["context"] = f"factorial_{rep}"
                res["arm"] = "clean"
                all_results.append(res)

                print(
                    f"[{total_calls:02d}/50] [Panel 3 Factorial] Cond: {cond_name:<22} | Rep: {rep:02d}/03 | "
                    f"Target: {target_task.target_fact.subject:<7} | Hash: {res['prompt_hash']} | "
                    f"State: {str(res['state_vector']):<15} | Phenotype: {res['phenotype']:<12} | "
                    f"Emitted: {res['emitted_object']:<20} ({int(res['latency_ms'])}ms)"
                )

            with db.conn:
                db.conn.execute("UPDATE runs SET status = 'completed', completed_at = ? WHERE run_id = ?", (
                    datetime.now(timezone.utc).isoformat(), run_id
                ))

    print("\n" + "=" * 155)
    print("      EXPERIMENT 1B-C2a: AGGREGATE SUMMARY & DUAL-ORACLE PHENOTYPE DISTRIBUTION")
    print("=" * 155)

    phenotypes: dict[str, int] = {}
    for r in all_results:
        phenotypes[r["phenotype"]] = phenotypes.get(r["phenotype"], 0) + 1

    for ph, cnt in sorted(phenotypes.items()):
        print(f"  Phenotype: {ph:<18} | Count: {cnt:<3} ({cnt/len(all_results)*100:.1f}%)")

    db.close()
    return {
        "all_results": all_results,
        "total_calls": total_calls,
        "phenotype_distribution": phenotypes,
        "db_file": db_file,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B-C2a Live Behavioral Immunity & Replay Stability Suite")
    parser.add_argument("--mode", type=str, default="all", choices=["discrete", "replay", "factorial", "all"], help="Execution mode")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Ollama model name")
    parser.add_argument("--fake", action="store_true", help="Use deterministic mock client")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_exp1b_c2a_suite(mode=args.mode, model_name=args.model, use_fake=args.fake, db_path=args.db)
