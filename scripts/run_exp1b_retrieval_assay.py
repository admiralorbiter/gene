"""Experiment 1B-B: Endogenous Retrieval Dynamics & Feedback Loops Assay Runner.

Assays generational transmission where contact rate X emerges dynamically from
top-k BM25 retrieval over a growing memory pool containing clean facts, distractor clutter,
and reproducing infected descendants.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.evaluation.dual_oracle import DualOracle, DualOracleEvaluation
from gene.evaluation.exposure_engine import ExposureEngine, ExposureDoseSummary
from gene.experiments.runner import get_environment_info, get_git_commit
from gene.memory.scored_retriever import BM25ScoredRetriever, ScoredRetrievalResult
from gene.memory.store import MemoryNode
from gene.ollama_client import CallSpec, FakeOllamaClient, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, Task, World, compute_fact_id


def generate_clutter_distractors(count: int, seed: int) -> list[Fact]:
    """Generate synthetic distractor facts about non-target facilities/sectors."""
    distractors: list[Fact] = []
    facilities = ["OUTPOST_ALPHA", "SECTOR_9", "STATION_NEXUS", "BASE_AURORA", "DEPOT_ZETA", "RELAY_7"]
    predicates = ["containment_tier", "power_grid_frequency", "beacon_channel", "inspection_cycle", "cooling_subsystem", "docking_bay"]
    values = ["TIER_A", "FREQ_500", "CH_99", "CYCLE_MONTHLY", "COOLING_CRYOGENIC", "BAY_PRIMARY", "TIER_B", "FREQ_250", "CYCLE_ANNUAL"]

    for i in range(count):
        fac = facilities[(seed + i) % len(facilities)]
        pred = predicates[(seed + i * 2) % len(predicates)]
        val = values[(seed + i * 3) % len(values)]
        distractors.append(
            Fact(
                subject=f"{fac}_{i//len(facilities)}",
                predicate=pred,
                object=val,
                truth_value=True,
                source_type="generated",
                locus_id=f"locus_dist_{i}",
            )
        )
    return distractors


def run_exp1b_retrieval_assay(
    worlds_count: int = 4,
    top_k: int = 4,
    clutter_count: int = 16,
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    mutated_supervisor: str = "TAL",
    use_fake: bool = False,
    db_path: str | None = None,
):
    """Execute the full 1B-B endogenous retrieval assay."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_file = db_path or f"gene_exp1b_retrieval_v1_{timestamp}.db"
    db = Database(db_file)
    template = PromptTemplate(prompt_version)
    retriever = BM25ScoredRetriever()
    client = FakeOllamaClient() if use_fake else OllamaClient()
    git_commit = get_git_commit()
    env_info = get_environment_info()

    exposure_engine = ExposureEngine()

    print("=" * 135)
    print("      EXPERIMENT 1B-B: ENDOGENOUS RETRIEVAL DYNAMICS & POSITIVE FEEDBACK ASSAY")
    print(f"      (Worlds: {worlds_count} | Top-k: {top_k} | Clutter: {clutter_count} | Model: {'FAKE' if use_fake else model_name})")
    print(f"      (Database: {db_file} | Commit: {git_commit[:8]} | Schema: {prompt_version})")
    print("=" * 135)

    g1_exposures: list[bool] = []
    g2_exposures: list[bool] = []

    for world_idx in range(worlds_count):
        seed = 2000 + world_idx
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

        # Clutter distractors for this world
        clutter_facts = generate_clutter_distractors(clutter_count, seed=seed)

        for arm in ["clean", "infected"]:
            is_infected_arm = (arm == "infected")
            current_world = bundle.mutated_world if is_infected_arm else bundle.clean_world
            founder_fact = bundle.mutated_founder_fact if is_infected_arm else bundle.clean_founder_fact
            founder_sup = mut_sup if is_infected_arm else clean_sup
            run_id = f"exp1b_b_{arm}_w{world_idx}_k{top_k}_c{clutter_count}"

            with db.conn:
                db.conn.execute("""
                    INSERT OR REPLACE INTO runs (
                        run_id, experiment_name, experiment_version, condition, world_id,
                        model_name, seed, num_ctx, temperature, prompt_version, started_at, status,
                        git_commit, model_digest, prompt_hash, config_hash, environment_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id, "exp1b_endogenous_retrieval", "1.0.0", f"k{top_k}_c{clutter_count}_{arm}",
                    current_world.world_id, "fake_model" if use_fake else model_name,
                    seed, 4096, 0.0, prompt_version, datetime.now(timezone.utc).isoformat(), "running",
                    git_commit, "fake_digest" if use_fake else "sha256:dynamic",
                    template.prompt_hash(), f"config_{top_k}_{clutter_count}", json.dumps(env_info)
                ))

            # ---------------------------------------------------------
            # Initialize In-Memory Candidate Pool (G0 Sources + Clutter)
            # ---------------------------------------------------------
            memory_pool: list[MemoryNode] = []
            infected_node_ids: set[str] = set()
            distractor_node_ids: set[str] = set()

            # 1. World Facts
            for f in current_world.facts:
                node_id = f"node_{run_id}_{f.locus_id}_{f.fact_id[:8]}"
                is_inf = (is_infected_arm and f.fact_id == founder_fact.fact_id)
                if is_inf:
                    infected_node_ids.add(node_id)
                node = MemoryNode(
                    node_id=node_id,
                    run_id=run_id,
                    world_id=current_world.world_id,
                    generation=0,
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

            # 2. Clutter Distractor Facts
            for c_f in clutter_facts:
                c_node_id = f"node_{run_id}_{c_f.locus_id}"
                distractor_node_ids.add(c_node_id)
                node = MemoryNode(
                    node_id=c_node_id,
                    run_id=run_id,
                    world_id=current_world.world_id,
                    generation=0,
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

            founder_node_id = f"node_{run_id}_{founder_fact.locus_id}_{founder_fact.fact_id[:8]}"

            # ---------------------------------------------------------
            # G1 Execution (Endogenous BM25 Top-k Retrieval)
            # ---------------------------------------------------------
            g1_admitted_claims: dict[str, MemoryNode] = {}
            for task in bundle.g1_tasks:
                query = task.prompt
                ret_res = retriever.rank(
                    query=query,
                    candidate_nodes=memory_pool,
                    top_k=top_k,
                    required_parent_id=founder_node_id,
                    infected_node_ids=infected_node_ids,
                    distractor_node_ids=distractor_node_ids,
                    seed=seed,
                )
                is_founder_exposed = ret_res.parent_in_top_k
                g1_exposures.append(is_founder_exposed)

                # Context facts & rules
                exposed_texts = [
                    {"memory_id": sm.memory_id, "text": sm.text}
                    for sm in ret_res.selected_memories
                ]
                for j, r in enumerate(bundle.g1_rules):
                    exposed_texts.append({"memory_id": f"rule_g1_{j}", "text": NaturalLanguageRenderer.render_rule(r)})

                # Context World for DualOracle
                ctx_facts = [
                    Fact(
                        subject=sm.text.split()[1] if len(sm.text.split()) > 1 else station,
                        predicate=sm.text.split()[2] if len(sm.text.split()) > 2 else "unknown",
                        object=sm.text.split()[-1].rstrip(".") if len(sm.text.split()) > 3 else "unknown",
                        truth_value=True,
                    )
                    for sm in ret_res.selected_memories if sm.is_required_parent
                ]
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
                res = client.chat(spec)
                eval_res = dual_oracle_g1.evaluate_response(
                    raw_text=res.raw_response_text,
                    parsed_json=res.parsed_json,
                    task=task,
                    has_infected_ancestry=is_infected_arm and is_founder_exposed,
                )

                call_id = f"call_{run_id}_g1_{task.target_fact.predicate}"
                locus_id = f"locus_{task.target_fact.predicate}"
                allele_id = compute_fact_id(station, task.target_fact.predicate, eval_res.normalized_object)
                node_id = f"node_{run_id}_{call_id}_{locus_id}_{allele_id[:8]}"
                is_generated = (eval_res.normalized_object not in ("UNKNOWN", "NONE", ""))
                is_written = is_generated

                # If admitted, write into memory pool for G2 competition!
                if is_written:
                    derived_text = f"Station {station} {task.target_fact.predicate} {eval_res.normalized_object}."
                    child_node = MemoryNode(
                        node_id=node_id,
                        run_id=run_id,
                        world_id=current_world.world_id,
                        generation=1,
                        node_type="derived",
                        natural_text=derived_text,
                        structured_json=eval_res.model_dump(),
                    )
                    memory_pool.append(child_node)
                    if is_infected_arm and eval_res.phenotype == "semantic":
                        infected_node_ids.add(node_id)
                    g1_admitted_claims[task.target_fact.predicate] = child_node

                    # Register in ExposureEngine
                    if is_infected_arm:
                        exposure_engine.register_parent(
                            parent_node_id=node_id,
                            parent_gen=1,
                            parent_phenotype=eval_res.phenotype,
                            arm=arm,
                        )

            # ---------------------------------------------------------
            # G2 Execution (Endogenous Retrieval over G0 + G1 Descendants)
            # ---------------------------------------------------------
            for g2_tmpl in bundle.g2_task_templates:
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
                    required_parent_id=parent_node_id,
                    infected_node_ids=infected_node_ids,
                    distractor_node_ids=distractor_node_ids,
                    seed=seed,
                )
                is_parent_exposed = ret_res.parent_in_top_k
                g2_exposures.append(is_parent_exposed)

                exposed_texts = [
                    {"memory_id": sm.memory_id, "text": sm.text}
                    for sm in ret_res.selected_memories
                ]
                for j, r in enumerate(matching_g2_rules):
                    exposed_texts.append({"memory_id": f"rule_g2_{j}", "text": NaturalLanguageRenderer.render_rule(r)})

                # Context World for G2 DualOracle
                ctx_facts = []
                if is_parent_exposed and parent_node:
                    ctx_facts.append(
                        Fact(
                            subject=station,
                            predicate=parent_pred,
                            object=parent_node.natural_text.split()[-1].rstrip("."),
                            truth_value=True,
                            locus_id=f"locus_{parent_pred}",
                        )
                    )

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
                res = client.chat(spec)
                eval_res = dual_oracle_g2.evaluate_response(
                    raw_text=res.raw_response_text,
                    parsed_json=res.parsed_json,
                    task=g2_task,
                    has_infected_ancestry=is_infected_arm and is_parent_exposed,
                )

                call_id = f"call_{run_id}_g2_{target_pred}"
                locus_id = g2_tmpl["target_locus_id"]
                allele_id = compute_fact_id(station, target_pred, eval_res.normalized_object)
                node_id = f"node_{run_id}_{call_id}_{locus_id}_{allele_id[:8]}"
                is_generated = (eval_res.normalized_object not in ("UNKNOWN", "NONE", ""))
                is_written = is_generated

                opp_id = f"opp_{run_id}_{target_pred}"
                exposure_engine.record_opportunity(
                    opportunity_id=opp_id,
                    run_id=run_id,
                    world_id=current_world.world_id,
                    arm=arm,
                    exposure_p=1.0 if is_parent_exposed else 0.0,
                    parent_gen=1,
                    child_gen=2,
                    parent_node_id=parent_node_id,
                    parent_locus_id=f"locus_{parent_pred}",
                    parent_phenotype="semantic" if is_infected_arm else "healthy",
                    child_task_id=g2_task.task_id,
                    target_predicate=target_pred,
                    is_exposed=is_parent_exposed,
                    is_generated=is_generated,
                    is_written=is_written,
                    child_node_id=node_id if is_written else None,
                    child_phenotype=eval_res.phenotype,
                    ancestral_allele_fidelity=eval_res.ancestral_allele_fidelity if is_parent_exposed else None,
                )

                print(f"  [{arm.upper()} G2] {target_pred} (Parent Exposed: {is_parent_exposed}): {eval_res.normalized_object} | Phenotype: {eval_res.phenotype.upper()}", flush=True)

    # -------------------------------------------------------------
    # Summary of Endogenous Dynamics
    # -------------------------------------------------------------
    x1 = sum(g1_exposures) / len(g1_exposures) if g1_exposures else 0.0
    x2 = sum(g2_exposures) / len(g2_exposures) if g2_exposures else 0.0
    delta_x = x2 - x1

    print("\n" + "=" * 135)
    print("      EXPERIMENT 1B-B: ENDOGENOUS RETRIEVAL FEEDBACK SUMMARY")
    print("=" * 135)
    print(f"Generation G1 Contact Rate (X_1) : {x1*100:.1f}% ({sum(g1_exposures)}/{len(g1_exposures)} queries)")
    print(f"Generation G2 Contact Rate (X_2) : {x2*100:.1f}% ({sum(g2_exposures)}/{len(g2_exposures)} queries)")
    print(f"Lineage Feedback Gain (Delta X)  : {delta_x*100:+.1f}% ({'POSITIVE FEEDBACK' if delta_x > 0 else 'NEUTRAL / DAMPENED'})")
    print("=" * 135 + "\n")
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B-B Endogenous Retrieval Assay")
    parser.add_argument("--worlds", type=int, default=4, help="Number of worlds")
    parser.add_argument("--top-k", type=int, default=4, help="Top-k retrieval budget")
    parser.add_argument("--clutter", type=int, default=16, help="Distractor clutter count")
    parser.add_argument("--version", type=str, default="v2", choices=["v1", "v2"], help="Prompt schema version")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model name")
    parser.add_argument("--fake", action="store_true", help="Use deterministic Fake client")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_exp1b_retrieval_assay(
        worlds_count=args.worlds,
        top_k=args.top_k,
        clutter_count=args.clutter,
        prompt_version=args.version,
        model_name=args.model,
        use_fake=args.fake,
        db_path=args.db,
    )

