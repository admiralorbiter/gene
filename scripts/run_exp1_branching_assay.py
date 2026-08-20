"""Experiment 1A: Hardened Paired Branching Transmission Assay Runner.

Executes the paired multi-generation branching transmission assay on live Ollama:
- Paired Counterfactuals: Runs both Clean Arm (W_clean: Kira -> 2H -> 4H) and Infected Arm (W_mut: Tal/Mira -> 2S -> 4S).
- True Rule Permutations: Systematically varies all 6 rule orderings and 3 rotations.
- Instance-Unique Primary Keys: memory_nodes.node_id is strictly unique per occurrence (node_{run_id}_{locus}_{allele[:8]}).
- Complete Exposure Ledger: Logs every exposed fact, rule, and distractor with exact context position into exposure_edges.
- Complete Lineage Persistence: Logs Founder -> G1 and G1 -> G2 transitions into SQLite lineage_transmissions.
- Dynamic Local Context Oracles: D_t^ctx built strictly from prompt-exposed context and admitted claims.
- Generational Firewall: G2 tasks see only admitted G1 parent fact + matching depth-2 rules + distractor.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Literal

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.evaluation.dual_oracle import DualOracle, DualOracleEvaluation
from gene.evaluation.next_gen_matrix import NextGenMatrixEngine, NextGenMatrixSummary
from gene.experiments.runner import get_environment_info, get_git_commit
from gene.ollama_client import CallSpec, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, Rule, Task, World, compute_fact_id


def render_and_record_memory_block(
    facts: list[Fact],
    rules: list[Rule],
    fact_node_ids: dict[str, str],
    rule_node_ids: dict[str, str],
) -> tuple[list[dict[str, str]], list[tuple[str, int]]]:
    """Render memory slot records and compute exact context exposure list (node_id, pos)."""
    memories = []
    exposures: list[tuple[str, int]] = []
    pos = 1

    for r in rules:
        mem_id = f"mem_{r.rule_id}"
        node_id = rule_node_ids.get(r.rule_id, f"rule_node_{r.rule_id}")
        memories.append({
            "memory_id": mem_id,
            "text": NaturalLanguageRenderer.render_rule(r),
            "raw_id": r.rule_id,
        })
        exposures.append((node_id, pos))
        pos += 1

    for f in facts:
        slot_id = f"mem_{f.locus_id or f.fact_id}"
        node_id = fact_node_ids.get(f.fact_id, f"node_fact_{f.fact_id}")
        memories.append({
            "memory_id": slot_id,
            "text": NaturalLanguageRenderer.render_fact(f),
            "raw_id": f.fact_id,
        })
        exposures.append((node_id, pos))
        pos += 1

    return memories, exposures


def run_exp1_branching_assay(
    worlds_count: int = 6,
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    mutated_supervisor: str = "TAL",
    arm_mode: Literal["both", "clean", "infected"] = "both",
    db_path: str | None = None,
):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if not db_path:
        db_path = f"gene_exp1_branching_{prompt_version}_{mutated_supervisor.lower()}_{timestamp}.db"

    print("=" * 95, flush=True)
    print(f"   GENE EXPERIMENT 1A: HARDENED PAIRED BRANCHING TRANSMISSION ASSAY", flush=True)
    print(f"   Model: {model_name} | Worlds: {worlds_count} | Arms: {arm_mode.upper()} | Mutated Founder: {mutated_supervisor}", flush=True)
    print(f"   Database: {db_path}", flush=True)
    print("=" * 95, flush=True)

    db = Database(db_path)
    client = OllamaClient()
    template = PromptTemplate(prompt_version)
    matrix_engine = NextGenMatrixEngine()

    git_commit = get_git_commit()
    env_info = get_environment_info()
    model_info = client.get_model_info(model_name)
    model_digest = model_info.digest
    prompt_hash = template.prompt_hash()
    config_hash = hashlib.sha256(f"exp1a_{prompt_version}_{model_name}_{mutated_supervisor}_{worlds_count}".encode()).hexdigest()[:16]

    arms_to_run = ["clean", "infected"] if arm_mode == "both" else [arm_mode]

    for w_idx in range(worlds_count):
        seed = 42 + w_idx * 17
        rotation_idx = w_idx % 3
        rule_perm_idx = w_idx % 6

        bundle = generate_exp1_branching_world(
            world_seed=seed,
            rotation_idx=rotation_idx,
            rule_perm_idx=rule_perm_idx,
            mutated_supervisor=mutated_supervisor,
        )
        db.save_world(bundle.clean_world)
        db.save_world(bundle.mutated_world)

        station = bundle.station

        for arm in arms_to_run:
            is_infected_arm = (arm == "infected")
            current_world = bundle.mutated_world if is_infected_arm else bundle.clean_world
            founder_fact = bundle.mutated_founder_fact if is_infected_arm else bundle.clean_founder_fact
            founder_sup = bundle.mutated_supervisor if is_infected_arm else bundle.target_supervisor

            run_id = f"run_exp1a_{arm}_{current_world.world_id}"

            with db.conn:
                db.conn.execute("""
                    INSERT OR REPLACE INTO runs (
                        run_id, experiment_name, experiment_version, condition, world_id,
                        model_name, seed, num_ctx, temperature, prompt_version, started_at, status,
                        git_commit, model_digest, prompt_hash, config_hash, environment_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id, "exp1a_controlled_branching", "2.0.0", f"branching_{arm}",
                    current_world.world_id, model_name, seed, 4096, 0.0, prompt_version,
                    datetime.now(timezone.utc).isoformat(), "running",
                    git_commit, model_digest, prompt_hash, config_hash, json.dumps(env_info)
                ))

            # Generate Instance-Unique node_ids for all G0 source facts and rules
            fact_node_ids: dict[str, str] = {}
            for f in current_world.facts:
                node_id = f"node_{run_id}_{f.locus_id}_{f.fact_id[:8]}"
                fact_node_ids[f.fact_id] = node_id
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO memory_nodes (
                            node_id, run_id, world_id, generation, node_type, natural_text, structured_json,
                            locus_id, allele_id, is_active, parent_generation, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        node_id, run_id, current_world.world_id, 0, "source",
                        NaturalLanguageRenderer.render_fact(f), f.canonical_json(),
                        f.locus_id, f.fact_id, 1, None, datetime.now(timezone.utc).isoformat()
                    ))

            rule_node_ids: dict[str, str] = {}
            for r in current_world.rules:
                r_node_id = f"node_{run_id}_{r.rule_id}"
                rule_node_ids[r.rule_id] = r_node_id
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO memory_nodes (
                            node_id, run_id, world_id, generation, node_type, natural_text, structured_json,
                            locus_id, allele_id, is_active, parent_generation, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        r_node_id, run_id, current_world.world_id, 0, "rule",
                        NaturalLanguageRenderer.render_rule(r), r.canonical_json(),
                        f"locus_rule_{r.rule_id}", r.rule_id, 1, None, datetime.now(timezone.utc).isoformat()
                    ))

            founder_node_id = fact_node_ids[founder_fact.fact_id]

            print(f"\n" + "=" * 95, flush=True)
            print(f"WORLD {w_idx+1}/{worlds_count} [{arm.upper()} ARM]: {current_world.world_id} (Seed: {seed}, Rot: {rotation_idx}, Perm: {rule_perm_idx})", flush=True)
            print(f"Station: {station} | Manager: {bundle.manager} | Supervisor: {founder_sup}", flush=True)

            # -------------------------------------------------------------
            # Generation 1 Execution
            # -------------------------------------------------------------
            g1_exposed_facts = current_world.facts
            g1_exposed_rules = bundle.g1_rules

            g1_context_world = World(
                world_id=f"ctx_g1_{current_world.world_id}",
                world_seed=seed,
                world_version="v2",
                facts=g1_exposed_facts,
                rules=g1_exposed_rules,
            )

            dual_oracle_g1 = DualOracle(
                canonical_world=bundle.clean_world,
                context_world=g1_context_world,
                ancestral_seed_allele=founder_sup,
                allele_decoder=bundle.allele_decoder,
            )

            g1_admitted_claims: dict[str, Fact] = {}
            g1_call_records: list[dict[str, Any]] = []

            for task_idx, task in enumerate(bundle.g1_tasks):
                mems, exposures = render_and_record_memory_block(
                    facts=g1_exposed_facts,
                    rules=g1_exposed_rules,
                    fact_node_ids=fact_node_ids,
                    rule_node_ids=rule_node_ids,
                )

                prompt = template.format_user_prompt(
                    memories=mems,
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

                t0 = time.perf_counter()
                res = client.chat(spec)
                lat = time.perf_counter() - t0

                eval_res = dual_oracle_g1.evaluate_response(
                    raw_text=res.raw_response_text,
                    parsed_json=res.parsed_json,
                    task=task,
                    has_infected_ancestry=is_infected_arm,
                )

                call_id = f"call_{run_id}_g1_{task.target_fact.predicate}"
                locus_id = f"locus_station_{task.target_fact.predicate}"
                allele_id = compute_fact_id(station, task.target_fact.predicate, eval_res.normalized_object)
                node_id = f"node_{run_id}_{locus_id}_{allele_id[:8]}"

                is_admitted = 1 if eval_res.normalized_object not in ("UNKNOWN", "NONE", "") else 0
                if is_admitted:
                    admitted_fact = Fact(
                        subject=station,
                        predicate=task.target_fact.predicate,
                        object=eval_res.normalized_object,
                        truth_value=True,
                        source_type="derived",
                        fact_id=allele_id,
                        locus_id=locus_id,
                    )
                    g1_admitted_claims[task.target_fact.predicate] = admitted_fact
                    fact_node_ids[admitted_fact.fact_id] = node_id

                with db.conn:
                    db.conn.execute("""
                        INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (call_id, run_id, 1, task.task_id, spec.model_dump_json(), res.raw_response_text, res.prompt_tokens, res.completion_tokens, lat * 1000.0, res.load_duration_ms, res.prompt_eval_duration_ms, res.eval_duration_ms, datetime.now(timezone.utc).isoformat()))

                    db.conn.execute("""
                        INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_by_call_id, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (node_id, run_id, current_world.world_id, 1, "derived", f"{station} {task.target_fact.predicate} {eval_res.normalized_object}", json.dumps({"raw_response": res.parsed_json}), locus_id, allele_id, is_admitted, 0, call_id, datetime.now(timezone.utc).isoformat()))

                    db.conn.execute("""
                        INSERT INTO dual_oracle_evaluations (evaluation_id, call_id, node_id, generation, task_id, target_subject, target_predicate, derived_object, canonical_truth_status, local_derivability_status, A_correct, E_correct, K_consistent, phenotype, state_vector_json, ancestral_allele_fidelity, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (f"eval_{call_id}", call_id, node_id, 1, task.task_id, station, task.target_fact.predicate, eval_res.normalized_object, eval_res.canonical_truth_status, eval_res.context_truth_status, eval_res.A_correct, eval_res.E_correct, eval_res.K_consistent, eval_res.phenotype, json.dumps(eval_res.state_vector), eval_res.ancestral_allele_fidelity, datetime.now(timezone.utc).isoformat()))

                    # Complete prompt exposure logging
                    for exp_node_id, c_pos in exposures:
                        db.conn.execute("""
                            INSERT OR REPLACE INTO exposure_edges (parent_node_id, child_node_id, call_id, retrieval_rank, context_position)
                            VALUES (?, ?, ?, ?, ?)
                        """, (exp_node_id, node_id, call_id, c_pos, c_pos))

                    # Persist Founder -> G1 transmission to SQLite
                    db.conn.execute("""
                        INSERT INTO lineage_transmissions (transmission_id, parent_node_id, child_node_id, parent_generation, child_generation, parent_phenotype, child_phenotype, transition_type, ancestral_allele_transmitted, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (f"trans_{node_id}", founder_node_id, node_id, 0, 1, "founder", eval_res.phenotype, f"founder->{eval_res.phenotype}", 1 if eval_res.ancestral_allele_fidelity == 1.0 else 0, datetime.now(timezone.utc).isoformat()))

                if is_infected_arm:
                    matrix_engine.record_transmission(
                        parent_node_id=founder_node_id,
                        child_node_id=node_id,
                        parent_gen=0,
                        child_gen=1,
                        parent_phenotype="founder",
                        child_phenotype=eval_res.phenotype,
                        ancestral_allele_fidelity=eval_res.ancestral_allele_fidelity,
                    )

                print(f"  [G1.{task_idx+1}] {task.target_fact.predicate}: {eval_res.normalized_object} | Phenotype: {eval_res.phenotype.upper()} | Vector: {eval_res.state_vector} (lat={lat:.2f}s)", flush=True)
                g1_call_records.append({"task_pred": task.target_fact.predicate, "node_id": node_id, "phenotype": eval_res.phenotype})

            # -------------------------------------------------------------
            # Generation 2 Execution (Generational Firewall)
            # -------------------------------------------------------------
            for g2_idx, g2_tmpl in enumerate(bundle.g2_task_templates):
                parent_pred = g2_tmpl["parent_predicate"]
                target_pred = g2_tmpl["target_predicate"]
                admitted_parent_fact = g1_admitted_claims.get(parent_pred)

                matching_g1_rec = next((r for r in g1_call_records if r["task_pred"] == parent_pred), None)
                parent_node_id = matching_g1_rec["node_id"] if matching_g1_rec else "unknown"
                parent_phenotype = matching_g1_rec["phenotype"] if matching_g1_rec else "unknown"

                matching_g2_rules = [r for r in bundle.g2_rules if g2_tmpl["rules_filter"](r)]

                # Firewall: Expose ONLY admitted G1 parent fact + matching G2 rules + distractor
                g2_exposed_facts = [admitted_parent_fact] if admitted_parent_fact else []
                g2_exposed_facts.append(current_world.facts[2])  # clean distractor (located_in)

                g2_context_world = World(
                    world_id=f"ctx_g2_{current_world.world_id}_{target_pred}",
                    world_seed=seed,
                    world_version="v2",
                    facts=g2_exposed_facts,
                    rules=matching_g2_rules,
                )

                dual_oracle_g2 = DualOracle(
                    canonical_world=bundle.clean_world,
                    context_world=g2_context_world,
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

                mems, exposures = render_and_record_memory_block(
                    facts=g2_exposed_facts,
                    rules=matching_g2_rules,
                    fact_node_ids=fact_node_ids,
                    rule_node_ids=rule_node_ids,
                )

                prompt = template.format_user_prompt(
                    memories=mems,
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

                t0 = time.perf_counter()
                res = client.chat(spec)
                lat = time.perf_counter() - t0

                eval_res = dual_oracle_g2.evaluate_response(
                    raw_text=res.raw_response_text,
                    parsed_json=res.parsed_json,
                    task=g2_task,
                    has_infected_ancestry=is_infected_arm,
                )

                call_id = f"call_{run_id}_g2_{target_pred}"
                locus_id = g2_tmpl["target_locus_id"]
                allele_id = compute_fact_id(station, target_pred, eval_res.normalized_object)
                node_id = f"node_{run_id}_{locus_id}_{allele_id[:8]}"
                is_admitted = 1 if eval_res.normalized_object not in ("UNKNOWN", "NONE", "") else 0

                with db.conn:
                    db.conn.execute("""
                        INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (call_id, run_id, 2, g2_task.task_id, spec.model_dump_json(), res.raw_response_text, res.prompt_tokens, res.completion_tokens, lat * 1000.0, res.load_duration_ms, res.prompt_eval_duration_ms, res.eval_duration_ms, datetime.now(timezone.utc).isoformat()))

                    db.conn.execute("""
                        INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_by_call_id, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (node_id, run_id, current_world.world_id, 2, "derived", f"{station} {target_pred} {eval_res.normalized_object}", json.dumps({"raw_response": res.parsed_json}), locus_id, allele_id, is_admitted, 1, call_id, datetime.now(timezone.utc).isoformat()))

                    db.conn.execute("""
                        INSERT INTO dual_oracle_evaluations (evaluation_id, call_id, node_id, generation, task_id, target_subject, target_predicate, derived_object, canonical_truth_status, local_derivability_status, A_correct, E_correct, K_consistent, phenotype, state_vector_json, ancestral_allele_fidelity, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (f"eval_{call_id}", call_id, node_id, 2, g2_task.task_id, station, target_pred, eval_res.normalized_object, eval_res.canonical_truth_status, eval_res.context_truth_status, eval_res.A_correct, eval_res.E_correct, eval_res.K_consistent, eval_res.phenotype, json.dumps(eval_res.state_vector), eval_res.ancestral_allele_fidelity, datetime.now(timezone.utc).isoformat()))

                    # Complete prompt exposure logging
                    for exp_node_id, c_pos in exposures:
                        db.conn.execute("""
                            INSERT OR REPLACE INTO exposure_edges (parent_node_id, child_node_id, call_id, retrieval_rank, context_position)
                            VALUES (?, ?, ?, ?, ?)
                        """, (exp_node_id, node_id, call_id, c_pos, c_pos))

                    # Persist G1 -> G2 transmission to SQLite
                    db.conn.execute("""
                        INSERT INTO lineage_transmissions (transmission_id, parent_node_id, child_node_id, parent_generation, child_generation, parent_phenotype, child_phenotype, transition_type, ancestral_allele_transmitted, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (f"trans_{node_id}", parent_node_id, node_id, 1, 2, parent_phenotype, eval_res.phenotype, f"{parent_phenotype}->{eval_res.phenotype}", 1 if eval_res.ancestral_allele_fidelity == 1.0 else 0, datetime.now(timezone.utc).isoformat()))

                if is_infected_arm:
                    matrix_engine.record_transmission(
                        parent_node_id=parent_node_id,
                        child_node_id=node_id,
                        parent_gen=1,
                        child_gen=2,
                        parent_phenotype=parent_phenotype,
                        child_phenotype=eval_res.phenotype,
                        ancestral_allele_fidelity=eval_res.ancestral_allele_fidelity,
                    )

                print(f"  [G2.{g2_idx+1}] {target_pred} (Parent: {parent_pred}): {eval_res.normalized_object} | Phenotype: {eval_res.phenotype.upper()} | Vector: {eval_res.state_vector} (lat={lat:.2f}s)", flush=True)

    if arm_mode in ("both", "infected"):
        summary = matrix_engine.compute_summary(founder_count=worlds_count)

        print("\n" + "=" * 95, flush=True)
        print(f"                 INFECTED ARM TRANSMISSION & PROGENY REPORT", flush=True)
        print("=" * 95, flush=True)
        print(f"  Worlds Tested:                   {worlds_count}", flush=True)
        print(f"  Founder Reproduction (R_F):       {summary.founder_reproduction_R_F:.2f} infected G1 children / founder", flush=True)
        print(f"  Semantic Reproduction (R_S):     {summary.semantic_parent_reproduction_R_S:.2f} infected G2 children / semantic parent", flush=True)
        print(f"  Epistemic Transmissibility (tau):{summary.epistemic_transmissibility_tau_S:.2f}", flush=True)
        f1_str = f"{summary.fidelity_G1_F1:.2f}" if summary.fidelity_G1_F1 is not None else "N/A"
        f2_str = f"{summary.fidelity_G2_F2:.2f}" if summary.fidelity_G2_F2 is not None else "N/A"
        print(f"  Ancestral Allele Fidelity (F1):  {f1_str}", flush=True)
        print(f"  Ancestral Allele Fidelity (F2):  {f2_str}", flush=True)
        
        print("\n  Next-Generation / Mean Progeny Matrix (M):", flush=True)
        for p_type in ["semantic", "epistemic", "control"]:
            status = summary.row_status[p_type]
            if status == "observed":
                row = summary.progeny_matrix[p_type]
                print(f"    {p_type.upper():<10} -> [S={row['semantic']:.2f}, E={row['epistemic']:.2f}, C={row['control']:.2f}] (Observed)", flush=True)
            else:
                print(f"    {p_type.upper():<10} -> [N/A, N/A, N/A] (Unobserved / Not Seeded)", flush=True)

        spec_rad_str = f"{summary.spectral_radius:.2f}" if summary.spectral_radius is not None else "N/A (Partial Matrix Identifiability)"
        print(f"\n  System Reproduction Number rho(M): {spec_rad_str}", flush=True)
        print(f"  Database Preserved At:             {db_path}", flush=True)
        print("=" * 95 + "\n", flush=True)

    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Hardened Paired Branching Transmission Assay")
    parser.add_argument("--worlds", type=int, default=6, help="Number of micro-worlds to test")
    parser.add_argument("--version", type=str, default="v2", choices=["v1", "v2"], help="Prompt schema version")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model name")
    parser.add_argument("--mutated-supervisor", type=str, default="TAL", help="Mutated supervisor allele (e.g. TAL or MIRA)")
    parser.add_argument("--arm", type=str, default="both", choices=["both", "clean", "infected"], help="Arm mode")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_exp1_branching_assay(
        worlds_count=args.worlds,
        prompt_version=args.version,
        model_name=args.model,
        mutated_supervisor=args.mutated_supervisor,
        arm_mode=args.arm,
        db_path=args.db,
    )
