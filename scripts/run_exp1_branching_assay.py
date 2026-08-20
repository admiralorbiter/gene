"""Experiment 1A: Controlled Branching Transmission Assay Runner.

Executes the multi-generation branching transmission assay on live Ollama:
- Evaluates 3-generation genealogy (G0 -> G1 -> G2).
- Dynamic local-context derivability oracle (D_t^ctx) built strictly from prompt-exposed context and actual admitted model claims.
- Generational firewalling: G2 tasks see only the admitted G1 parent claim + depth-2 rules + clean distractors (0 founder facts, 0 G1 rules).
- Dual-oracle evaluations with full 5D state vectors (T*, D_t^ctx, A, E, K).
- Full Next-Generation / Progeny Matrix estimation with explicit row observation statuses.
- Complete timing telemetry, full provenance, and SQLite persistence.
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
from gene.worlds.schema import Fact, Task, World, compute_fact_id


def render_memory_block(facts: list[Fact], rules: list[Any]) -> list[dict[str, str]]:
    """Render memory slot records from exact exposed facts and rules."""
    memories = []
    for r in rules:
        memories.append({
            "memory_id": f"mem_{r.rule_id}",
            "text": NaturalLanguageRenderer.render_rule(r),
            "raw_id": r.rule_id,
        })
    for f in facts:
        slot_id = f"mem_{f.locus_id or f.fact_id}"
        memories.append({
            "memory_id": slot_id,
            "text": NaturalLanguageRenderer.render_fact(f),
            "raw_id": f.fact_id,
        })
    return memories


def run_exp1_branching_assay(
    worlds_count: int = 1,
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    db_path: str | None = None,
):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if not db_path:
        db_path = f"gene_exp1_branching_{prompt_version}_{timestamp}.db"

    print("=" * 95, flush=True)
    print(f"   GENE EXPERIMENT 1A: CONTROLLED BRANCHING TRANSMISSION ASSAY", flush=True)
    print(f"   Model: Live Ollama ({model_name}) | Worlds: {worlds_count} | Database: {db_path}", flush=True)
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
    config_hash = hashlib.sha256(f"exp1a_{prompt_version}_{model_name}_42".encode()).hexdigest()[:16]

    world_summaries = []

    for w_idx in range(worlds_count):
        seed = 42 + w_idx * 17
        rotation_idx = w_idx % 3
        rule_perm_idx = w_idx % 6
        bundle = generate_exp1_branching_world(world_seed=seed, rotation_idx=rotation_idx, rule_perm_idx=rule_perm_idx)
        db.save_world(bundle.clean_world)
        db.save_world(bundle.mutated_world)

        station = bundle.station
        run_id = f"run_exp1a_{bundle.mutated_world.world_id}"

        with db.conn:
            db.conn.execute("""
                INSERT OR REPLACE INTO runs (
                    run_id, experiment_name, experiment_version, condition, world_id,
                    model_name, seed, num_ctx, temperature, prompt_version, started_at, status,
                    git_commit, model_digest, prompt_hash, config_hash, environment_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, "exp1a_controlled_branching", "2.0.0", "branching_transmission",
                bundle.mutated_world.world_id, model_name, seed, 4096, 0.0, prompt_version,
                datetime.now(timezone.utc).isoformat(), "running",
                git_commit, model_digest, prompt_hash, config_hash, json.dumps(env_info)
            ))

            # Store G0 founder memory nodes
            for f in bundle.mutated_world.facts:
                db.conn.execute("""
                    INSERT OR REPLACE INTO memory_nodes (
                        node_id, run_id, world_id, generation, node_type, natural_text, structured_json,
                        locus_id, allele_id, is_active, parent_generation, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f.fact_id, run_id, bundle.mutated_world.world_id, 0, "source",
                    NaturalLanguageRenderer.render_fact(f), f.canonical_json(),
                    f.locus_id, f.fact_id, 1, None, datetime.now(timezone.utc).isoformat()
                ))

        print(f"\n" + "=" * 95, flush=True)
        print(f"WORLD {w_idx+1}/{worlds_count}: {bundle.mutated_world.world_id} (Seed: {seed}, Rotation: {rotation_idx})", flush=True)
        print(f"Station:            {station} | Manager: {bundle.manager}", flush=True)
        print(f"Clean Founder (F0): {bundle.target_supervisor} -> {NaturalLanguageRenderer.render_fact(bundle.clean_founder_fact)}", flush=True)
        print(f"Infected Founder:   {bundle.mutated_supervisor} -> {NaturalLanguageRenderer.render_fact(bundle.mutated_founder_fact)}", flush=True)

        # -------------------------------------------------------------
        # 1. Generation 1 Execution (Infected Arm)
        # -------------------------------------------------------------
        print(f"\n--- GENERATION 1: Primary Inference (2 Child Tasks) ---", flush=True)
        g1_admitted_claims: dict[str, Fact] = {}
        g1_evaluations: list[DualOracleEvaluation] = []
        g1_call_records: list[dict[str, Any]] = []

        g1_exposed_facts = bundle.mutated_world.facts  # Fact A, Mutated Fact B, Distractors
        g1_exposed_rules = bundle.g1_rules

        # Local context world for G1
        g1_context_world = World(
            world_id=f"ctx_g1_{bundle.mutated_world.world_id}",
            world_seed=seed,
            world_version="v2",
            facts=g1_exposed_facts,
            rules=g1_exposed_rules,
        )

        dual_oracle_g1 = DualOracle(
            canonical_world=bundle.clean_world,
            context_world=g1_context_world,
            ancestral_seed_allele=bundle.mutated_supervisor,
            allele_decoder=bundle.allele_decoder,
        )

        for task_idx, task in enumerate(bundle.g1_tasks):
            mems = render_memory_block(g1_exposed_facts, g1_exposed_rules)
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
                has_infected_ancestry=True,
            )
            g1_evaluations.append(eval_res)

            call_id = f"call_exp1a_{bundle.mutated_world.world_id}_g1_{task.target_fact.predicate}"
            node_id = f"node_{call_id}"

            # Admit claim to active memory if not UNKNOWN
            is_admitted = 1 if eval_res.normalized_object not in ("UNKNOWN", "NONE", "") else 0
            if is_admitted:
                admitted_fact = Fact(
                    subject=station,
                    predicate=task.target_fact.predicate,
                    object=eval_res.normalized_object,
                    truth_value=True,
                    source_type="derived",
                    fact_id=compute_fact_id(station, task.target_fact.predicate, eval_res.normalized_object),
                    locus_id=f"locus_station_{task.target_fact.predicate}",
                )
                g1_admitted_claims[task.target_fact.predicate] = admitted_fact

            with db.conn:
                db.conn.execute("""
                    INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (call_id, run_id, 1, task.task_id, spec.model_dump_json(), res.raw_response_text, res.prompt_tokens, res.completion_tokens, lat * 1000.0, res.load_duration_ms, res.prompt_eval_duration_ms, res.eval_duration_ms, datetime.now(timezone.utc).isoformat()))

                db.conn.execute("""
                    INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_by_call_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (node_id, run_id, bundle.mutated_world.world_id, 1, "derived", f"{station} {task.target_fact.predicate} {eval_res.normalized_object}", json.dumps({"raw_response": res.parsed_json}), f"locus_station_{task.target_fact.predicate}", compute_fact_id(station, task.target_fact.predicate, eval_res.normalized_object), is_admitted, 0, call_id, datetime.now(timezone.utc).isoformat()))

                db.conn.execute("""
                    INSERT INTO dual_oracle_evaluations (evaluation_id, call_id, node_id, generation, task_id, target_subject, target_predicate, derived_object, canonical_truth_status, local_derivability_status, A_correct, E_correct, K_consistent, phenotype, state_vector_json, ancestral_allele_fidelity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (f"eval_{call_id}", call_id, node_id, 1, task.task_id, station, task.target_fact.predicate, eval_res.normalized_object, eval_res.canonical_truth_status, eval_res.context_truth_status, eval_res.A_correct, eval_res.E_correct, eval_res.K_consistent, eval_res.phenotype, json.dumps(eval_res.state_vector), eval_res.ancestral_allele_fidelity, datetime.now(timezone.utc).isoformat()))

                # Log parent exposure edge from mutated founder fact
                db.conn.execute("""
                    INSERT OR REPLACE INTO exposure_edges (parent_node_id, child_node_id, call_id, retrieval_rank, context_position)
                    VALUES (?, ?, ?, ?, ?)
                """, (bundle.mutated_founder_fact.fact_id, node_id, call_id, 1, 1))

            # Record transmission from founder F0
            matrix_engine.record_transmission(
                parent_node_id=bundle.mutated_founder_fact.fact_id,
                child_node_id=node_id,
                parent_gen=0,
                child_gen=1,
                parent_phenotype="founder",
                child_phenotype=eval_res.phenotype,
                ancestral_allele_fidelity=eval_res.ancestral_allele_fidelity,
            )

            print(f"  [G1.{task_idx+1}] {task.target_fact.predicate}:", flush=True)
            print(f"    Raw Output:       {res.raw_response_text.strip()}", flush=True)
            print(f"    Derived Object:   {eval_res.normalized_object}", flush=True)
            print(f"    State Vector:     T*={eval_res.canonical_truth} | D_ctx={eval_res.context_derivability} | A={eval_res.A_correct} | E={eval_res.E_correct} | K={eval_res.K_consistent}", flush=True)
            print(f"    Phenotype:        {eval_res.phenotype.upper()} (Allele Fidelity: {eval_res.ancestral_allele_fidelity})", flush=True)
            print(f"    Telemetry:        latency={lat:.2f}s | prompt_eval={res.prompt_eval_duration_ms:.1f}ms | eval={res.eval_duration_ms:.1f}ms", flush=True)

            g1_call_records.append({"task_pred": task.target_fact.predicate, "node_id": node_id, "phenotype": eval_res.phenotype})

        # -------------------------------------------------------------
        # 2. Generation 2 Execution (4 Grandchild Tasks with Generational Firewall)
        # -------------------------------------------------------------
        print(f"\n--- GENERATION 2: Secondary Inference (4 Grandchild Tasks) ---", flush=True)
        g2_evaluations: list[DualOracleEvaluation] = []

        for g2_idx, g2_tmpl in enumerate(bundle.g2_task_templates):
            parent_pred = g2_tmpl["parent_predicate"]
            target_pred = g2_tmpl["target_predicate"]
            admitted_parent_fact = g1_admitted_claims.get(parent_pred)

            # Find matching parent node from G1
            matching_g1_rec = next((r for r in g1_call_records if r["task_pred"] == parent_pred), None)
            parent_node_id = matching_g1_rec["node_id"] if matching_g1_rec else "unknown"
            parent_phenotype = matching_g1_rec["phenotype"] if matching_g1_rec else "unknown"

            # Filter G2 rules
            matching_g2_rules = [r for r in bundle.g2_rules if g2_tmpl["rules_filter"](r)]

            # Generational Firewall: Expose ONLY admitted G1 parent fact + matching G2 rules + clean distractor
            # (Strictly 0 founder facts, 0 G1 rules)
            g2_exposed_facts = [admitted_parent_fact] if admitted_parent_fact else []
            g2_exposed_facts.append(bundle.clean_world.facts[2])  # clean distractor (located_in)

            # Dynamic local context world built strictly from actual admitted G1 claim
            g2_context_world = World(
                world_id=f"ctx_g2_{bundle.mutated_world.world_id}_{target_pred}",
                world_seed=seed,
                world_version="v2",
                facts=g2_exposed_facts,
                rules=matching_g2_rules,
            )

            dual_oracle_g2 = DualOracle(
                canonical_world=bundle.clean_world,
                context_world=g2_context_world,
                ancestral_seed_allele=bundle.mutated_supervisor,
                allele_decoder=bundle.allele_decoder,
            )

            g2_task = Task(
                task_id=f"task_exp1a_{bundle.mutated_world.world_id}_{g2_tmpl['task_id_suffix']}",
                world_id=bundle.clean_world.world_id,
                query_type="rule_inference",
                target_fact=Fact(subject=station, predicate=target_pred, object=g2_tmpl["clean_expected"]),
                reasoning_depth=2,
                prompt=g2_tmpl["prompt"],
                expected_answer=g2_tmpl["clean_expected"],
                valid_support_path_ids=[],
            )

            mems = render_memory_block(g2_exposed_facts, matching_g2_rules)
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
                has_infected_ancestry=True,
            )
            g2_evaluations.append(eval_res)

            call_id = f"call_exp1a_{bundle.mutated_world.world_id}_g2_{target_pred}"
            node_id = f"node_{call_id}"
            is_admitted = 1 if eval_res.normalized_object not in ("UNKNOWN", "NONE", "") else 0

            with db.conn:
                db.conn.execute("""
                    INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (call_id, run_id, 2, g2_task.task_id, spec.model_dump_json(), res.raw_response_text, res.prompt_tokens, res.completion_tokens, lat * 1000.0, res.load_duration_ms, res.prompt_eval_duration_ms, res.eval_duration_ms, datetime.now(timezone.utc).isoformat()))

                db.conn.execute("""
                    INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_by_call_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (node_id, run_id, bundle.mutated_world.world_id, 2, "derived", f"{station} {target_pred} {eval_res.normalized_object}", json.dumps({"raw_response": res.parsed_json}), g2_tmpl["target_locus_id"], compute_fact_id(station, target_pred, eval_res.normalized_object), is_admitted, 1, call_id, datetime.now(timezone.utc).isoformat()))

                db.conn.execute("""
                    INSERT INTO dual_oracle_evaluations (evaluation_id, call_id, node_id, generation, task_id, target_subject, target_predicate, derived_object, canonical_truth_status, local_derivability_status, A_correct, E_correct, K_consistent, phenotype, state_vector_json, ancestral_allele_fidelity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (f"eval_{call_id}", call_id, node_id, 2, g2_task.task_id, station, target_pred, eval_res.normalized_object, eval_res.canonical_truth_status, eval_res.context_truth_status, eval_res.A_correct, eval_res.E_correct, eval_res.K_consistent, eval_res.phenotype, json.dumps(eval_res.state_vector), eval_res.ancestral_allele_fidelity, datetime.now(timezone.utc).isoformat()))

                # Log parent exposure edge from G1 parent node
                db.conn.execute("""
                    INSERT OR REPLACE INTO exposure_edges (parent_node_id, child_node_id, call_id, retrieval_rank, context_position)
                    VALUES (?, ?, ?, ?, ?)
                """, (parent_node_id, node_id, call_id, 1, 1))

                # Log transmission in lineage_transmissions
                db.conn.execute("""
                    INSERT INTO lineage_transmissions (transmission_id, parent_node_id, child_node_id, parent_generation, child_generation, parent_phenotype, child_phenotype, transition_type, ancestral_allele_transmitted, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (f"trans_{node_id}", parent_node_id, node_id, 1, 2, parent_phenotype, eval_res.phenotype, f"{parent_phenotype}->{eval_res.phenotype}", 1 if eval_res.ancestral_allele_fidelity == 1.0 else 0, datetime.now(timezone.utc).isoformat()))

            # Record transmission in matrix engine
            matrix_engine.record_transmission(
                parent_node_id=parent_node_id,
                child_node_id=node_id,
                parent_gen=1,
                child_gen=2,
                parent_phenotype=parent_phenotype,
                child_phenotype=eval_res.phenotype,
                ancestral_allele_fidelity=eval_res.ancestral_allele_fidelity,
            )

            print(f"  [G2.{g2_idx+1}] {target_pred} (Parent: {parent_pred}):", flush=True)
            print(f"    Raw Output:       {res.raw_response_text.strip()}", flush=True)
            print(f"    Derived Object:   {eval_res.normalized_object} (Expected Mutated: {g2_tmpl['mutated_expected']})", flush=True)
            print(f"    State Vector:     T*={eval_res.canonical_truth} | D_ctx={eval_res.context_derivability} | A={eval_res.A_correct} | E={eval_res.E_correct} | K={eval_res.K_consistent}", flush=True)
            print(f"    Phenotype:        {eval_res.phenotype.upper()} (Allele Fidelity: {eval_res.ancestral_allele_fidelity})", flush=True)
            print(f"    Telemetry:        latency={lat:.2f}s | prompt_eval={res.prompt_eval_duration_ms:.1f}ms | eval={res.eval_duration_ms:.1f}ms", flush=True)

        world_summaries.append({
            "world_id": bundle.mutated_world.world_id,
            "station": station,
            "g1_evals": [e.phenotype for e in g1_evaluations],
            "g2_evals": [e.phenotype for e in g2_evaluations],
        })

    # Summary Report & Progeny Matrix
    summary = matrix_engine.compute_summary(founder_count=worlds_count)

    print("\n" + "=" * 95, flush=True)
    print(f"                 EXPERIMENT 1A TRANSMISSION & PROGENY REPORT", flush=True)
    print("=" * 95, flush=True)
    print(f"  Worlds Tested:                   {worlds_count}", flush=True)
    print(f"  Founder Reproduction (R_F):       {summary.founder_reproduction_R_F:.2f} infected G1 children / founder", flush=True)
    print(f"  Semantic Reproduction (R_S):     {summary.semantic_parent_reproduction_R_S:.2f} infected G2 children / semantic parent", flush=True)
    print(f"  Epistemic Transmissibility (tau):{summary.epistemic_transmissibility_tau_S:.2f}", flush=True)
    print(f"  Ancestral Allele Fidelity (F1):  {summary.fidelity_G1_F1:.2f}", flush=True)
    print(f"  Ancestral Allele Fidelity (F2):  {summary.fidelity_G2_F2:.2f}", flush=True)
    
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
    parser = argparse.ArgumentParser(description="Run Experiment 1A Branching Transmission Assay")
    parser.add_argument("--worlds", type=int, default=1, help="Number of micro-worlds to test")
    parser.add_argument("--version", type=str, default="v2", choices=["v1", "v2"], help="Prompt schema version")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model name")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_exp1_branching_assay(
        worlds_count=args.worlds,
        prompt_version=args.version,
        model_name=args.model,
        db_path=args.db,
    )
