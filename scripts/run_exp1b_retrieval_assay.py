"""Experiment 1B-B: Endogenous Multi-Hop Retrieval & Surface-Area Scaling Assay Runner.

Assays:
- 1B-B1: Endogenous Multi-Hop Retrieval (X_F, X_A, X_path, k-rescue sweeps, hard-negative ablation).
- 1B-B2: Controlled Lineage Surface-Area Scaling (retrieval visibility vs lineage multiplicity N_lineage in {0, 1, 2, 4, 8}).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.evaluation.dual_oracle import DualOracle, DualOracleEvaluation
from gene.evaluation.exposure_engine import ExposureEngine
from gene.experiments.runner import get_environment_info, get_git_commit
from gene.memory.scored_retriever import BM25ScoredRetriever, EvaluatedCandidate, ScoredRetrievalResult
from gene.memory.store import MemoryNode
from gene.ollama_client import CallSpec, FakeOllamaClient, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, Task, World, compute_fact_id


def generate_clutter_distractors(
    station: str,
    easy_count: int = 4,
    hard_count: int = 4,
    seed: int = 42,
) -> tuple[list[Fact], list[Fact]]:
    """Generate easy clutter (unrelated facilities) and hard negatives (same station, genuine lexical overlap, zero target answer leakage)."""
    easy_facts: list[Fact] = []
    facilities = ["OUTPOST_ALPHA", "SECTOR_9", "STATION_NEXUS", "BASE_AURORA", "DEPOT_ZETA", "RELAY_7"]
    predicates = ["containment status", "power grid frequency", "beacon channel", "inspection cycle", "cooling subsystem", "docking bay"]
    values = ["nominal alpha", "five hundred hertz", "channel ninety nine", "monthly inspection", "cryogenic active", "bay primary"]

    for i in range(easy_count):
        fac = facilities[(seed + i) % len(facilities)]
        pred = predicates[(seed + i * 2) % len(predicates)]
        val = values[(seed + i * 3) % len(values)]
        easy_facts.append(
            Fact(
                subject=f"{fac}_{i//len(facilities)}",
                predicate=pred,
                object=val,
                truth_value=True,
                source_type="generated",
                locus_id=f"locus_easy_{i}",
            )
        )

    hard_facts: list[Fact] = []
    # Natural multi-token predicates and values with ZERO target output tokens
    hard_predicates = [
        "emergency security protocol", "annual security audit", "routine maintenance protocol",
        "access control policy", "communication beacon channel", "internal transit corridor",
        "facility clearance classification", "general inspection schedule"
    ]
    hard_values = [
        "standard operational baseline", "verified quarterly", "routine internal cycle",
        "nominal archive status", "frequency channel nine", "corridor sector zero",
        "restricted personnel only", "directive sixty six"
    ]

    for j in range(hard_count):
        pred = hard_predicates[(seed + j) % len(hard_predicates)]
        val = hard_values[(seed + j * 2) % len(hard_values)]
        hard_facts.append(
            Fact(
                subject=station,
                predicate=pred,
                object=val,
                truth_value=True,
                source_type="generated",
                locus_id=f"locus_hard_{j}",
            )
        )

    return easy_facts, hard_facts


def log_retrieval_events(
    db: Database,
    run_id: str,
    call_id: str,
    generation: int,
    task_id: str,
    query_text: str,
    top_k: int,
    ret_res: ScoredRetrievalResult,
):
    """Persist all evaluated candidate scores and ranks to SQLite."""
    now = datetime.now(timezone.utc).isoformat()
    with db.conn:
        for cand in ret_res.all_evaluated_candidates:
            event_id = f"rev_{call_id}_{cand.memory_id}"
            db.conn.execute("""
                INSERT OR REPLACE INTO retrieval_events (
                    event_id, run_id, call_id, generation, task_id, query_text,
                    top_k, pool_size, candidate_node_id, paired_slot_id, bm25_score,
                    retrieval_rank, is_selected, context_position, is_founder,
                    is_co_support, is_required_path, is_infected, is_distractor, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, run_id, call_id, generation, task_id, query_text,
                top_k, ret_res.candidate_pool_size, cand.memory_id, cand.paired_slot_id,
                cand.bm25_score, cand.retrieval_rank, 1 if cand.is_selected else 0,
                cand.context_position, 1 if cand.is_founder else 0,
                1 if cand.is_co_support else 0, 1 if cand.is_required_path else 0,
                1 if cand.is_infected else 0, 1 if cand.is_distractor else 0, now
            ))


def run_exp1b_b1_assay(
    worlds_count: int = 4,
    top_k: int = 4,
    easy_clutter: int = 4,
    hard_clutter: int = 4,
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    mutated_supervisor: str = "TAL",
    use_fake: bool = False,
    preflight: bool = False,
    db_path: str | None = None,
):
    """Execute Experiment 1B-B1: Endogenous Multi-Hop Retrieval Assay."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_file = db_path or f"gene_exp1b_b1_{timestamp}.db"
    db = Database(db_file)
    template = PromptTemplate(prompt_version)
    retriever = BM25ScoredRetriever()
    client = FakeOllamaClient() if use_fake else OllamaClient()
    git_commit = get_git_commit()
    env_info = get_environment_info()

    try:
        model_metadata = client.get_model_info(model_name)
        model_digest = model_metadata.digest if model_metadata else ("fake_digest" if use_fake else "sha256:unknown")
    except Exception:
        model_digest = "fake_digest" if use_fake else "sha256:unknown"
    config_str = f"1b_b1_k{top_k}_easy{easy_clutter}_hard{hard_clutter}_{prompt_version}"
    config_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()[:16]

    print("=" * 135)
    print("      EXPERIMENT 1B-B1: ENDOGENOUS MULTI-HOP RETRIEVAL & CLUTTER ASSAY")
    print(f"      (Worlds: {worlds_count} | Top-k: {top_k} | Clutter: {easy_clutter} Easy, {hard_clutter} Hard | Mode: {'PREFLIGHT' if preflight else ('FAKE' if use_fake else model_name)})")
    print(f"      (Database: {db_file} | Commit: {git_commit[:8]} | Digest: {model_digest[:16]})")
    print("=" * 135)

    stats = {
        "clean": {"g1_founder": 0, "g1_co_sup": 0, "g1_path": 0, "g1_total": 0, "g2_parent": 0, "g2_total": 0},
        "infected": {"g1_founder": 0, "g1_co_sup": 0, "g1_path": 0, "g1_total": 0, "g2_parent": 0, "g2_total": 0},
    }

    for world_idx in range(worlds_count):
        seed = 3000 + world_idx
        bundle = generate_exp1_branching_world(
            world_seed=seed,
            rotation_idx=world_idx,
            mutated_supervisor=mutated_supervisor,
        )
        db.save_world(bundle.clean_world)
        db.save_world(bundle.mutated_world)

        station = bundle.station
        mut_sup = bundle.mutated_supervisor
        clean_sup = bundle.target_supervisor

        easy_facts, hard_facts = generate_clutter_distractors(station, easy_clutter, hard_clutter, seed)

        for arm in ["clean", "infected"]:
            is_infected_arm = (arm == "infected")
            current_world = bundle.mutated_world if is_infected_arm else bundle.clean_world
            founder_fact = bundle.mutated_founder_fact if is_infected_arm else bundle.clean_founder_fact
            founder_sup = mut_sup if is_infected_arm else clean_sup
            run_id = f"exp1b_b1_{arm}_w{world_idx}_k{top_k}"

            with db.conn:
                db.conn.execute("""
                    INSERT OR REPLACE INTO runs (
                        run_id, experiment_name, experiment_version, condition, world_id,
                        model_name, seed, num_ctx, temperature, prompt_version, started_at, status,
                        git_commit, model_digest, prompt_hash, config_hash, environment_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id, "exp1b_b1_retrieval", "1.0.0", f"{arm}_k{top_k}",
                    current_world.world_id, "fake_model" if use_fake else model_name,
                    seed, 4096, 0.0, prompt_version, datetime.now(timezone.utc).isoformat(), "running",
                    git_commit, model_digest, template.prompt_hash(), config_hash, json.dumps(env_info)
                ))

            # ---------------------------------------------------------
            # Build Candidate Pool
            # ---------------------------------------------------------
            memory_pool: list[MemoryNode] = []
            infected_node_ids: set[str] = set()
            distractor_node_ids: set[str] = set()
            co_support_node_ids: set[str] = set()
            founder_node_id: str = ""

            for f in current_world.facts:
                node_id = f"node_{run_id}_{f.locus_id}_{f.fact_id[:8]}"
                is_founder = (f.fact_id == founder_fact.fact_id)
                is_co_sup = (f.predicate == "manager")
                is_inf = (is_infected_arm and is_founder)

                if is_founder:
                    founder_node_id = node_id
                if is_co_sup:
                    co_support_node_ids.add(node_id)
                if is_inf:
                    infected_node_ids.add(node_id)

                node = MemoryNode(
                    node_id=node_id,
                    run_id=run_id,
                    world_id=current_world.world_id,
                    generation=0,
                    locus_id=f.locus_id,
                    node_type="source",
                    natural_text=NaturalLanguageRenderer.render_fact(f),
                    structured_json=f.model_dump(),
                )
                memory_pool.append(node)
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (node_id, run_id, current_world.world_id, 0, "source", node.natural_text, json.dumps(f.model_dump()), f.locus_id, f.fact_id, 1, None, datetime.now(timezone.utc).isoformat()))

            for c_f in easy_facts + hard_facts:
                c_node_id = f"node_{run_id}_{c_f.locus_id}"
                distractor_node_ids.add(c_node_id)
                node = MemoryNode(
                    node_id=c_node_id,
                    run_id=run_id,
                    world_id=current_world.world_id,
                    generation=0,
                    locus_id=c_f.locus_id,
                    node_type="source",
                    natural_text=NaturalLanguageRenderer.render_fact(c_f),
                    structured_json=c_f.model_dump(),
                )
                memory_pool.append(node)
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (c_node_id, run_id, current_world.world_id, 0, "source", node.natural_text, json.dumps(c_f.model_dump()), c_f.locus_id, c_f.fact_id, 1, None, datetime.now(timezone.utc).isoformat()))

            # ---------------------------------------------------------
            # G1 Execution
            # ---------------------------------------------------------
            g1_admitted_claims: dict[str, MemoryNode] = {}
            for task in bundle.g1_tasks:
                stats[arm]["g1_total"] += 1
                query = task.prompt
                ret_res = retriever.rank(
                    query=query,
                    candidate_nodes=memory_pool,
                    top_k=top_k,
                    founder_node_id=founder_node_id,
                    co_support_node_ids=co_support_node_ids,
                    infected_node_ids=infected_node_ids,
                    distractor_node_ids=distractor_node_ids,
                    seed=seed,
                )

                if ret_res.founder_retrieved:
                    stats[arm]["g1_founder"] += 1
                if ret_res.co_support_retrieved:
                    stats[arm]["g1_co_sup"] += 1
                if ret_res.path_retrieved:
                    stats[arm]["g1_path"] += 1

                call_id = f"call_{run_id}_g1_{task.target_fact.predicate}"
                log_retrieval_events(db, run_id, call_id, 1, task.task_id, query, top_k, ret_res)

                ctx_facts: list[Fact] = []
                for cand in ret_res.selected_memories:
                    if cand.structured_fact:
                        ctx_facts.append(cand.structured_fact)

                g1_ctx_world = World(
                    world_id=f"ctx_g1_{run_id}_{task.target_fact.predicate}",
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

                if preflight:
                    print(f"\n[PREFLIGHT {arm.upper()} G1] Task: {task.target_fact.predicate}")
                    print(f"  Query: {query}")
                    print(f"  Top-{top_k} Retrieved Candidates:")
                    for sm in ret_res.selected_memories:
                        print(f"    - Rank {sm.retrieval_rank} (Score: {sm.bm25_score:.2f}) [Founder: {sm.is_founder}, CoSup: {sm.is_co_support}]: {sm.text}")
                    print(f"  Multi-Hop Recall: Founder={ret_res.founder_retrieved} (Rank {ret_res.founder_retrieval_rank}), CoSup={ret_res.co_support_retrieved}, Path={ret_res.path_retrieved}")
                    print(f"  Context World Fact Count: {len(ctx_facts)} -> D_ctx will be {1 if ret_res.path_retrieved else 0}")
                    continue

                exposed_texts = [{"memory_id": sm.memory_id, "text": sm.text} for sm in ret_res.selected_memories]
                for j, r in enumerate(bundle.g1_rules):
                    exposed_texts.append({"memory_id": f"rule_g1_{j}", "text": NaturalLanguageRenderer.render_rule(r)})

                prompt = template.format_user_prompt(
                    memories=exposed_texts,
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
                    has_infected_ancestry=is_infected_arm and ret_res.founder_retrieved,
                )

                # Persist call to SQLite
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
                    eval_id_g1 = f"eval_{call_id}"
                    db.conn.execute("""
                        INSERT OR REPLACE INTO dual_oracle_evaluations (
                            evaluation_id, call_id, node_id, generation, task_id, target_subject, target_predicate, derived_object, canonical_truth_status,
                            local_derivability_status, A_correct, E_correct, K_consistent, phenotype,
                            state_vector_json, ancestral_allele_fidelity, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        eval_id_g1, call_id, None, 1, task.task_id, task.target_fact.subject, task.target_fact.predicate, eval_res.normalized_object,
                        eval_res.canonical_truth_status, eval_res.context_truth_status,
                        1 if eval_res.A_correct else 0, 1 if eval_res.E_correct else 0,
                        1 if eval_res.K_consistent else 0, eval_res.phenotype, json.dumps(eval_res.state_vector),
                        eval_res.ancestral_allele_fidelity, datetime.now(timezone.utc).isoformat()
                    ))

                locus_id = f"locus_{task.target_fact.predicate}"
                allele_id = compute_fact_id(station, task.target_fact.predicate, eval_res.normalized_object)
                node_id = f"node_{run_id}_{call_id}_{locus_id}_{allele_id[:8]}"
                is_written = (eval_res.normalized_object not in ("UNKNOWN", "NONE", ""))

                if is_written:
                    derived_fact = Fact(
                        subject=station,
                        predicate=task.target_fact.predicate,
                        object=eval_res.normalized_object,
                        truth_value=True,
                        source_type="derived",
                        locus_id=locus_id,
                    )
                    derived_text = f"Station {station} {task.target_fact.predicate} {eval_res.normalized_object}."
                    child_node = MemoryNode(
                        node_id=node_id,
                        run_id=run_id,
                        world_id=current_world.world_id,
                        generation=1,
                        locus_id=locus_id,
                        node_type="derived",
                        natural_text=derived_text,
                        structured_json=derived_fact.model_dump(),
                    )
                    memory_pool.append(child_node)
                    with db.conn:
                        db.conn.execute("""
                            INSERT OR REPLACE INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (node_id, run_id, current_world.world_id, 1, "derived", derived_text, json.dumps(derived_fact.model_dump()), locus_id, allele_id, 1, 0, datetime.now(timezone.utc).isoformat()))

                    if is_infected_arm and eval_res.phenotype == "semantic":
                        infected_node_ids.add(node_id)
                    g1_admitted_claims[task.target_fact.predicate] = child_node

            # ---------------------------------------------------------
            # G2 Execution
            # ---------------------------------------------------------
            for g2_tmpl in bundle.g2_task_templates:
                stats[arm]["g2_total"] += 1
                target_pred = g2_tmpl["target_predicate"]
                parent_pred = g2_tmpl["parent_predicate"]
                matching_g2_rules = [r for r in bundle.g2_rules if g2_tmpl["rules_filter"](r)]
                parent_node = g1_admitted_claims.get(parent_pred)
                parent_node_id = parent_node.node_id if parent_node else "MISSING_PARENT"

                query = g2_tmpl["prompt"]
                ret_res = retriever.rank(
                    query=query,
                    candidate_nodes=memory_pool,
                    top_k=top_k,
                    founder_node_id=parent_node_id,
                    infected_node_ids=infected_node_ids,
                    distractor_node_ids=distractor_node_ids,
                    seed=seed,
                )

                if ret_res.founder_retrieved:
                    stats[arm]["g2_parent"] += 1

                call_id = f"call_{run_id}_g2_{target_pred}"
                log_retrieval_events(db, run_id, call_id, 2, f"task_{target_pred}", query, top_k, ret_res)

                ctx_facts = []
                for cand in ret_res.selected_memories:
                    if cand.structured_fact:
                        ctx_facts.append(cand.structured_fact)

                g2_ctx_world = World(
                    world_id=f"ctx_g2_{run_id}_{target_pred}",
                    world_seed=seed,
                    world_version=prompt_version,
                    facts=ctx_facts,
                    rules=matching_g2_rules,
                )
                dual_oracle_g2 = DualOracle(
                    canonical_world=bundle.clean_world,
                    context_world=g2_ctx_world,
                    ancestral_seed_allele=founder_sup,
                    allele_decoder=bundle.allele_decoder,
                )

                g2_task = Task(
                    task_id=f"task_{run_id}_{g2_tmpl['task_id_suffix']}",
                    world_id=bundle.clean_world.world_id,
                    query_type="rule_inference",
                    target_fact=Fact(subject=station, predicate=target_pred, object=g2_tmpl["clean_expected"]),
                    reasoning_depth=2,
                    prompt=g2_tmpl["prompt"],
                    expected_answer=g2_tmpl["clean_expected"],
                    valid_support_path_ids=[],
                )

                if preflight:
                    print(f"  [PREFLIGHT {arm.upper()} G2] Task: {target_pred} | Parent in Top-{top_k}: {ret_res.founder_retrieved} (Rank: {ret_res.founder_retrieval_rank})")
                    continue

                exposed_texts = [{"memory_id": sm.memory_id, "text": sm.text} for sm in ret_res.selected_memories]
                for j, r in enumerate(matching_g2_rules):
                    exposed_texts.append({"memory_id": f"rule_g2_{j}", "text": NaturalLanguageRenderer.render_rule(r)})

                prompt = template.format_user_prompt(
                    memories=exposed_texts,
                    question_prompt=g2_task.prompt,
                    target_subject=station,
                    target_predicate=target_pred,
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

                eval_res = dual_oracle_g2.evaluate_response(
                    raw_text=res.raw_response_text,
                    parsed_json=res.parsed_json,
                    task=g2_task,
                    has_infected_ancestry=is_infected_arm and ret_res.founder_retrieved,
                )

                # Persist call & evaluation
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO calls (
                            call_id, run_id, generation, task_id, request_json, response_text,
                            response_json, prompt_tokens, completion_tokens, latency_ms,
                            load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        call_id, run_id, 2, g2_task.task_id, json.dumps(spec.to_request_payload()),
                        res.raw_response_text, json.dumps(res.parsed_json),
                        res.prompt_tokens, res.completion_tokens,
                        res.latency_ms if res.latency_ms > 0 else latency_ms,
                        res.load_duration_ms, res.prompt_eval_duration_ms, res.eval_duration_ms,
                        datetime.now(timezone.utc).isoformat()
                    ))
                    eval_id_g2 = f"eval_{call_id}"
                    db.conn.execute("""
                        INSERT OR REPLACE INTO dual_oracle_evaluations (
                            evaluation_id, call_id, node_id, generation, task_id, target_subject, target_predicate, derived_object, canonical_truth_status,
                            local_derivability_status, A_correct, E_correct, K_consistent, phenotype,
                            state_vector_json, ancestral_allele_fidelity, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        eval_id_g2, call_id, None, 2, g2_task.task_id, station, target_pred, eval_res.normalized_object,
                        eval_res.canonical_truth_status, eval_res.context_truth_status,
                        1 if eval_res.A_correct else 0, 1 if eval_res.E_correct else 0,
                        1 if eval_res.K_consistent else 0, eval_res.phenotype, json.dumps(eval_res.state_vector),
                        eval_res.ancestral_allele_fidelity, datetime.now(timezone.utc).isoformat()
                    ))

                print(f"  [{arm.upper()} G2] {target_pred} (Parent Exposed: {ret_res.founder_retrieved}): {eval_res.normalized_object} | D_ctx={eval_res.context_derivability} | Phenotype: {eval_res.phenotype.upper()}", flush=True)

    # -------------------------------------------------------------
    # Summary Table
    # -------------------------------------------------------------
    print("\n" + "=" * 135)
    print("      EXPERIMENT 1B-B1: MULTI-HOP RETRIEVAL LEDGER SUMMARY")
    print("=" * 135)
    for arm in ["clean", "infected"]:
        s = stats[arm]
        xf = s["g1_founder"] / s["g1_total"] if s["g1_total"] else 0.0
        xa = s["g1_co_sup"] / s["g1_total"] if s["g1_total"] else 0.0
        xpath = s["g1_path"] / s["g1_total"] if s["g1_total"] else 0.0
        xp2 = s["g2_parent"] / s["g2_total"] if s["g2_total"] else 0.0
        print(f"Arm: {arm.upper():<8} | G1 Founder X_F: {xf*100:5.1f}% ({s['g1_founder']}/{s['g1_total']}) | G1 Co-Sup X_A: {xa*100:5.1f}% ({s['g1_co_sup']}/{s['g1_total']}) | G1 Full Path X_path: {xpath*100:5.1f}% ({s['g1_path']}/{s['g1_total']}) | G2 Parent Recall: {xp2*100:5.1f}% ({s['g2_parent']}/{s['g2_total']})")
    print("=" * 135 + "\n")
    db.close()


def run_exp1b_b1_k_sweep(
    worlds_count: int = 4,
    k_values: list[int] | None = None,
    easy_clutter: int = 4,
    hard_clutter: int = 4,
    mutated_supervisor: str = "TAL",
):
    """Run deterministic zero-cost top-k retrieval rescue sweep (k in 4, 5, 6, 7, 8)."""
    ks = k_values or [4, 5, 6, 7, 8]
    retriever = BM25ScoredRetriever()

    print("=" * 135)
    print("      EXPERIMENT 1B-B1: TOP-k RETRIEVAL RESCUE SWEEP (ZERO LLM COST)")
    print(f"      (Worlds: {worlds_count} | k-values: {ks} | Distractors: {easy_clutter} Easy, {hard_clutter} Hard)")
    print("=" * 135)

    results: dict[int, dict[str, float]] = {}

    for k in ks:
        total_g1 = 0
        founder_hits = 0
        cosup_hits = 0
        path_hits = 0

        for world_idx in range(worlds_count):
            seed = 5000 + world_idx
            bundle = generate_exp1_branching_world(world_seed=seed, rotation_idx=world_idx, mutated_supervisor=mutated_supervisor)
            station = bundle.station
            founder_fact = bundle.mutated_founder_fact
            easy_facts, hard_facts = generate_clutter_distractors(station, easy_clutter, hard_clutter, seed)

            memory_pool = []
            co_sup_ids = set()
            founder_id = ""
            for f in bundle.mutated_world.facts:
                nid = f"node_{f.locus_id}_{f.fact_id[:8]}"
                if f.fact_id == founder_fact.fact_id:
                    founder_id = nid
                if f.predicate == "manager":
                    co_sup_ids.add(nid)
                memory_pool.append(MemoryNode(
                    node_id=nid, run_id="sweep", world_id="w", generation=0,
                    locus_id=f.locus_id, node_type="source",
                    natural_text=NaturalLanguageRenderer.render_fact(f), structured_json=f.model_dump()
                ))

            for c_f in easy_facts + hard_facts:
                memory_pool.append(MemoryNode(
                    node_id=f"node_dist_{c_f.locus_id}", run_id="sweep", world_id="w", generation=0,
                    locus_id=c_f.locus_id, node_type="source",
                    natural_text=NaturalLanguageRenderer.render_fact(c_f), structured_json=c_f.model_dump()
                ))

            for task in bundle.g1_tasks:
                total_g1 += 1
                res = retriever.rank(query=task.prompt, candidate_nodes=memory_pool, top_k=k, founder_node_id=founder_id, co_support_node_ids=co_sup_ids)
                if res.founder_retrieved:
                    founder_hits += 1
                if res.co_support_retrieved:
                    cosup_hits += 1
                if res.path_retrieved:
                    path_hits += 1

        results[k] = {
            "x_f": founder_hits / total_g1,
            "x_a": cosup_hits / total_g1,
            "x_path": path_hits / total_g1,
        }

    print(f"{'Top-k Context Budget':<25} | {'Founder Recall X_F':<25} | {'Co-Support Recall X_A':<25} | {'Complete Path X_path':<25}")
    print("-" * 135)
    for k, d in results.items():
        print(f"k = {k:<21} | {d['x_f']*100:5.1f}%                   | {d['x_a']*100:5.1f}%                      | {d['x_path']*100:5.1f}%")
    print("=" * 135 + "\n")


def run_exp1b_b1_hard_ablation(
    worlds_count: int = 4,
    top_k: int = 4,
    hard_values: list[int] | None = None,
    mutated_supervisor: str = "TAL",
):
    """Run hard-negative clutter dose-response ablation sweep (N_hard in 0, 2, 4, 8)."""
    hards = hard_values or [0, 2, 4, 8]
    retriever = BM25ScoredRetriever()

    print("=" * 135)
    print("      EXPERIMENT 1B-B1: HARD-NEGATIVE CLUTTER ABLATION SWEEP (ZERO LLM COST)")
    print(f"      (Worlds: {worlds_count} | Fixed Top-k: {top_k} | N_hard: {hards})")
    print("=" * 135)

    results: dict[int, dict[str, float]] = {}

    for nh in hards:
        total_g1 = 0
        founder_hits = 0
        cosup_hits = 0
        path_hits = 0

        for world_idx in range(worlds_count):
            seed = 6000 + world_idx
            bundle = generate_exp1_branching_world(world_seed=seed, rotation_idx=world_idx, mutated_supervisor=mutated_supervisor)
            station = bundle.station
            founder_fact = bundle.mutated_founder_fact
            easy_facts, hard_facts = generate_clutter_distractors(station, easy_count=4, hard_count=nh, seed=seed)

            memory_pool = []
            co_sup_ids = set()
            founder_id = ""
            for f in bundle.mutated_world.facts:
                nid = f"node_{f.locus_id}_{f.fact_id[:8]}"
                if f.fact_id == founder_fact.fact_id:
                    founder_id = nid
                if f.predicate == "manager":
                    co_sup_ids.add(nid)
                memory_pool.append(MemoryNode(
                    node_id=nid, run_id="sweep", world_id="w", generation=0,
                    locus_id=f.locus_id, node_type="source",
                    natural_text=NaturalLanguageRenderer.render_fact(f), structured_json=f.model_dump()
                ))

            for c_f in easy_facts + hard_facts:
                memory_pool.append(MemoryNode(
                    node_id=f"node_dist_{c_f.locus_id}", run_id="sweep", world_id="w", generation=0,
                    locus_id=c_f.locus_id, node_type="source",
                    natural_text=NaturalLanguageRenderer.render_fact(c_f), structured_json=c_f.model_dump()
                ))

            for task in bundle.g1_tasks:
                total_g1 += 1
                res = retriever.rank(query=task.prompt, candidate_nodes=memory_pool, top_k=top_k, founder_node_id=founder_id, co_support_node_ids=co_sup_ids)
                if res.founder_retrieved:
                    founder_hits += 1
                if res.co_support_retrieved:
                    cosup_hits += 1
                if res.path_retrieved:
                    path_hits += 1

        results[nh] = {
            "x_f": founder_hits / total_g1,
            "x_a": cosup_hits / total_g1,
            "x_path": path_hits / total_g1,
        }

    print(f"{'Hard Negatives (N_hard)':<25} | {'Founder Recall X_F':<25} | {'Co-Support Recall X_A':<25} | {'Complete Path X_path':<25}")
    print("-" * 135)
    for nh, d in results.items():
        print(f"N_hard = {nh:<16} | {d['x_f']*100:5.1f}%                   | {d['x_a']*100:5.1f}%                      | {d['x_path']*100:5.1f}%")
    print("=" * 135 + "\n")


def run_exp1b_b2_surface_feedback_assay(
    worlds_count: int = 4,
    top_k: int = 4,
    clutter_count: int = 16,
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    mutated_supervisor: str = "TAL",
    use_fake: bool = False,
    db_path: str | None = None,
):
    """Execute Experiment 1B-B2: Controlled Lineage Surface-Area Scaling Assay."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_file = db_path or f"gene_exp1b_b2_{timestamp}.db"
    db = Database(db_file)
    retriever = BM25ScoredRetriever()

    print("=" * 135)
    print("      EXPERIMENT 1B-B2: CONTROLLED LINEAGE SURFACE-AREA SCALING ASSAY")
    print(f"      (Worlds: {worlds_count} | Top-k: {top_k} | Distractor Pool: {clutter_count})")
    print(f"      (Database: {db_file})")
    print("=" * 135)

    n_lineage_values = [0, 1, 2, 4, 8]
    summary_results: dict[int, dict[str, Any]] = {}

    for n_lin in n_lineage_values:
        total_queries = 0
        parent_retrieved_count = 0
        any_lineage_retrieved_count = 0
        occupancy_sum = 0

        for world_idx in range(worlds_count):
            seed = 4000 + world_idx
            bundle = generate_exp1_branching_world(
                world_seed=seed,
                rotation_idx=world_idx,
                mutated_supervisor=mutated_supervisor,
            )
            station = bundle.station
            founder_fact = bundle.mutated_founder_fact

            # Clean & distractor background nodes
            background_nodes: list[MemoryNode] = []
            for f in bundle.clean_world.facts:
                background_nodes.append(
                    MemoryNode(
                        node_id=f"node_clean_{f.locus_id}",
                        run_id="exp1b_b2",
                        world_id=bundle.clean_world.world_id,
                        generation=0,
                        locus_id=f.locus_id,
                        node_type="source",
                        natural_text=NaturalLanguageRenderer.render_fact(f),
                        structured_json=f.model_dump(),
                    )
                )

            easy_f, hard_f = generate_clutter_distractors(station, clutter_count//2, clutter_count//2, seed)
            for c in easy_f + hard_f:
                background_nodes.append(
                    MemoryNode(
                        node_id=f"node_dist_{c.locus_id}",
                        run_id="exp1b_b2",
                        world_id=bundle.clean_world.world_id,
                        generation=0,
                        locus_id=c.locus_id,
                        node_type="source",
                        natural_text=NaturalLanguageRenderer.render_fact(c),
                        structured_json=c.model_dump(),
                    )
                )

            # Target required parent node
            parent_node = MemoryNode(
                node_id="node_target_founder",
                run_id="exp1b_b2",
                world_id=bundle.clean_world.world_id,
                generation=0,
                locus_id="locus_manager_supervisor",
                node_type="source",
                natural_text=NaturalLanguageRenderer.render_fact(founder_fact),
                structured_json=founder_fact.model_dump(),
            )

            # Synthesize N_lineage descendants
            lineage_nodes: list[MemoryNode] = []
            for i in range(n_lin):
                lin_f = Fact(
                    subject=station,
                    predicate=f"lineage trait {i}",
                    object=f"record {i}",
                    truth_value=True,
                    source_type="derived",
                    locus_id=f"locus_lin_{i}",
                )
                lineage_nodes.append(
                    MemoryNode(
                        node_id=f"node_lin_{i}",
                        run_id="exp1b_b2",
                        world_id=bundle.clean_world.world_id,
                        generation=1,
                        locus_id=f"locus_lin_{i}",
                        node_type="derived",
                        natural_text=f"Station {station} lineage trait {i} is record {i}.",
                        structured_json=lin_f.model_dump(),
                    )
                )

            all_inf_ids = {"node_target_founder"} | {n.node_id for n in lineage_nodes}
            candidate_pool = background_nodes + [parent_node] + lineage_nodes

            for task in bundle.g1_tasks:
                total_queries += 1
                ret_res = retriever.rank(
                    query=task.prompt,
                    candidate_nodes=candidate_pool,
                    top_k=top_k,
                    founder_node_id="node_target_founder",
                    infected_node_ids=all_inf_ids,
                    seed=seed,
                )

                if ret_res.founder_retrieved:
                    parent_retrieved_count += 1
                if ret_res.num_infected_in_top_k > 0:
                    any_lineage_retrieved_count += 1
                occupancy_sum += ret_res.num_infected_in_top_k

        p_parent = parent_retrieved_count / total_queries if total_queries else 0.0
        p_any = any_lineage_retrieved_count / total_queries if total_queries else 0.0
        avg_occ = occupancy_sum / total_queries if total_queries else 0.0

        summary_results[n_lin] = {
            "p_parent": p_parent,
            "p_any_lineage": p_any,
            "mean_top_k_occupancy": avg_occ,
        }

        # Persist to SQLite surface_feedback_sweeps
        with db.conn:
            db.conn.execute("""
                INSERT OR REPLACE INTO surface_feedback_sweeps (
                    sweep_id, run_id, world_id, n_lineage, top_k, pool_size,
                    p_parent_in_top_k, p_any_lineage_in_top_k, mean_top_k_occupancy, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"sweep_n{n_lin}_k{top_k}", "exp1b_b2", "pooled_4w", n_lin, top_k,
                len(candidate_pool), p_parent, p_any, avg_occ, datetime.now(timezone.utc).isoformat()
            ))

    print("\n" + "=" * 135)
    print("      EXPERIMENT 1B-B2: SURFACE-AREA SCALING RESULTS")
    print("=" * 135)
    print(f"{'Lineage Multiplicity (N_lin)':<28} | {'P(Founder in Top-k)':<20} | {'P(Any Lineage in Top-k)':<25} | {'Mean Top-k Occupancy (k=4)':<25}")
    print("-" * 135)
    for n_lin, data in summary_results.items():
        print(f"N_lineage = {n_lin:<17} | {data['p_parent']*100:5.1f}%              | {data['p_any_lineage']*100:5.1f}%                   | {data['mean_top_k_occupancy']:.2f} / {top_k}")
    print("=" * 135 + "\n")
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B-B Retrieval Assays")
    parser.add_argument("--assay", type=str, default="1b-b1", choices=["1b-b1", "1b-b2", "sweep-k", "sweep-hard"], help="Assay to run")
    parser.add_argument("--worlds", type=int, default=4, help="Number of worlds")
    parser.add_argument("--top-k", type=int, default=4, help="Top-k retrieval budget")
    parser.add_argument("--easy-clutter", type=int, default=4, help="Easy clutter distractors")
    parser.add_argument("--hard-clutter", type=int, default=4, help="Hard negative distractors")
    parser.add_argument("--version", type=str, default="v2", choices=["v1", "v2"], help="Prompt schema version")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model name")
    parser.add_argument("--fake", action="store_true", help="Use deterministic Fake client")
    parser.add_argument("--preflight", action="store_true", help="Run preflight retrieval inspection without LLM")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    if args.assay == "1b-b1":
        run_exp1b_b1_assay(
            worlds_count=args.worlds,
            top_k=args.top_k,
            easy_clutter=args.easy_clutter,
            hard_clutter=args.hard_clutter,
            prompt_version=args.version,
            model_name=args.model,
            use_fake=args.fake,
            preflight=args.preflight,
            db_path=args.db,
        )
    elif args.assay == "1b-b2":
        run_exp1b_b2_surface_feedback_assay(
            worlds_count=args.worlds,
            top_k=args.top_k,
            clutter_count=args.easy_clutter + args.hard_clutter,
            prompt_version=args.version,
            model_name=args.model,
            use_fake=args.fake,
            db_path=args.db,
        )
    elif args.assay == "sweep-k":
        run_exp1b_b1_k_sweep(
            worlds_count=args.worlds,
            k_values=[4, 5, 6, 7, 8],
            easy_clutter=args.easy_clutter,
            hard_clutter=args.hard_clutter,
        )
    elif args.assay == "sweep-hard":
        run_exp1b_b1_hard_ablation(
            worlds_count=args.worlds,
            top_k=args.top_k,
            hard_values=[0, 2, 4, 8],
        )


