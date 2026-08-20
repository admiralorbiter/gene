"""Experiment 1B-A1: Controlled Balanced Exposure Dose-Response & Clean Utility Assay.

Varies retrieval exposure probability p in {0.0, 0.25, 0.50, 0.75, 1.0} using deterministic balanced masks:
- Measures whether epistemic transmissibility tau_S remains invariant as contact rate X is reduced.
- Measures the critical replacement threshold at p_c = 0.50 where R_S = 1.0.
- Simultaneously measures Clean Cognitive Utility U_clean(p) to quantify the exact trade-off between
  misinformation containment and cognitive utility.
- Uses dynamic graph-traversed ancestry and full SQLite opportunity persistence.
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
from gene.evaluation.exposure_engine import (
    BALANCED_EXPOSURE_MASKS,
    ExposureDoseSummary,
    ExposureEngine,
    get_exposure_mask,
)
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


def run_exp1b_exposure_assay(
    worlds_count: int = 4,
    grid_str: str = "0.0,0.25,0.5,0.75,1.0",
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    mutated_supervisor: str = "TAL",
    db_path: str | None = None,
):
    grid = [float(x.strip()) for x in grid_str.split(",")]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if not db_path:
        db_path = f"gene_exp1b_exposure_{prompt_version}_{timestamp}.db"

    print("=" * 95, flush=True)
    print(f"   GENE EXPERIMENT 1B-A1: BALANCED EXPOSURE DOSE-RESPONSE & CLEAN UTILITY ASSAY", flush=True)
    print(f"   Model: {model_name} | Worlds: {worlds_count} | Exposure Doses (p): {grid}", flush=True)
    print(f"   Database: {db_path}", flush=True)
    print("=" * 95, flush=True)

    db = Database(db_path)
    client = OllamaClient()
    template = PromptTemplate(prompt_version)
    exposure_engine = ExposureEngine()

    git_commit = get_git_commit()
    env_info = get_environment_info()
    model_info = client.get_model_info(model_name)
    model_digest = model_info.digest
    prompt_hash = template.prompt_hash()

    for p in grid:
        print(f"\n" + "#" * 95, flush=True)
        print(f"   EXPOSURE DOSE: p = {p:.2f} (Target Contact X = {2*p:.2f}, Uniform-Thinning Expected R_S = {2*p:.2f})", flush=True)
        print("#" * 95, flush=True)

        for w_idx in range(worlds_count):
            mask = get_exposure_mask(exposure_p=p, world_idx=w_idx)
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

            for arm in ["clean", "infected"]:
                is_infected_arm = (arm == "infected")
                current_world = bundle.mutated_world if is_infected_arm else bundle.clean_world
                founder_fact = bundle.mutated_founder_fact if is_infected_arm else bundle.clean_founder_fact
                founder_sup = bundle.mutated_supervisor if is_infected_arm else bundle.target_supervisor

                run_id = f"run_exp1b_p{int(p*100)}_{arm}_{current_world.world_id}"

                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO runs (
                            run_id, experiment_name, experiment_version, condition, world_id,
                            model_name, seed, num_ctx, temperature, prompt_version, started_at, status,
                            git_commit, model_digest, prompt_hash, config_hash, environment_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        run_id, "exp1b_exposure_dose_response", "2.0.0", f"p_{p:.2f}_{arm}",
                        current_world.world_id, model_name, seed, 4096, 0.0, prompt_version,
                        datetime.now(timezone.utc).isoformat(), "running",
                        git_commit, model_digest, prompt_hash, hashlib.sha256(f"exp1b_{p}".encode()).hexdigest()[:16], json.dumps(env_info)
                    ))

                # Unique node_ids for G0
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

                # -------------------------------------------------------------
                # G1 Execution (Fully Exposed, p=1.0 at G1 to establish parent population)
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
                    node_id = f"node_{run_id}_{call_id}_{locus_id}_{allele_id[:8]}"

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

                    # Register parent node in ExposureEngine
                    exposure_engine.register_parent(
                        parent_node_id=node_id,
                        parent_gen=1,
                        parent_phenotype=eval_res.phenotype,
                        arm=arm,
                    )

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

                        for exp_node_id, c_pos in exposures:
                            db.conn.execute("""
                                INSERT OR REPLACE INTO exposure_edges (parent_node_id, child_node_id, call_id, retrieval_rank, context_position)
                                VALUES (?, ?, ?, ?, ?)
                            """, (exp_node_id, node_id, call_id, c_pos, c_pos))

                    g1_call_records.append({"task_pred": task.target_fact.predicate, "node_id": node_id, "phenotype": eval_res.phenotype, "locus_id": locus_id})

                # -------------------------------------------------------------
                # G2 Execution with Balanced Exposure Mask
                # -------------------------------------------------------------
                for g2_idx, g2_tmpl in enumerate(bundle.g2_task_templates):
                    is_task_exposed = mask[g2_idx]
                    parent_pred = g2_tmpl["parent_predicate"]
                    target_pred = g2_tmpl["target_predicate"]
                    admitted_parent_fact = g1_admitted_claims.get(parent_pred)

                    matching_g1_rec = next((r for r in g1_call_records if r["task_pred"] == parent_pred), None)
                    parent_node_id = matching_g1_rec["node_id"] if matching_g1_rec else "unknown"
                    parent_phenotype = matching_g1_rec["phenotype"] if matching_g1_rec else "unknown"
                    parent_locus_id = matching_g1_rec["locus_id"] if matching_g1_rec else "unknown"

                    matching_g2_rules = [r for r in bundle.g2_rules if g2_tmpl["rules_filter"](r)]

                    # If task is exposed: include admitted G1 parent fact.
                    # If masked (p < 1): do NOT include parent fact (clean distractor only!).
                    g2_exposed_facts: list[Fact] = []
                    if is_task_exposed and admitted_parent_fact:
                        g2_exposed_facts.append(admitted_parent_fact)
                    g2_exposed_facts.append(current_world.facts[2])  # clean distractor

                    # Dynamic context world based on exact exposed facts
                    g2_context_world = World(
                        world_id=f"ctx_g2_{current_world.world_id}_{target_pred}_p{int(p*100)}",
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

                    # Dynamic ancestry: child has infected ancestry iff the infected parent was exposed!
                    has_infected_ancestry = (is_infected_arm and is_task_exposed)

                    eval_res = dual_oracle_g2.evaluate_response(
                        raw_text=res.raw_response_text,
                        parsed_json=res.parsed_json,
                        task=g2_task,
                        has_infected_ancestry=has_infected_ancestry,
                    )

                    call_id = f"call_{run_id}_g2_{target_pred}"
                    locus_id = g2_tmpl["target_locus_id"]
                    allele_id = compute_fact_id(station, target_pred, eval_res.normalized_object)
                    node_id = f"node_{run_id}_{call_id}_{locus_id}_{allele_id[:8]}"
                    is_generated = (eval_res.normalized_object not in ("UNKNOWN", "NONE", ""))
                    is_written = is_generated  # ungated W=1 for concrete claims

                    opportunity_id = f"opp_{run_id}_{target_pred}"

                    # Record opportunity in ExposureEngine
                    exposure_engine.record_opportunity(
                        opportunity_id=opportunity_id,
                        run_id=run_id,
                        world_id=current_world.world_id,
                        arm=arm,
                        exposure_p=p,
                        parent_gen=1,
                        child_gen=2,
                        parent_node_id=parent_node_id,
                        parent_locus_id=parent_locus_id,
                        parent_phenotype=parent_phenotype,
                        child_task_id=g2_task.task_id,
                        target_predicate=target_pred,
                        is_exposed=is_task_exposed,
                        is_generated=is_generated,
                        is_written=is_written,
                        child_node_id=node_id if is_written else None,
                        child_phenotype=eval_res.phenotype,
                        ancestral_allele_fidelity=eval_res.ancestral_allele_fidelity if is_task_exposed else None,
                    )

                    with db.conn:
                        db.conn.execute("""
                            INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (call_id, run_id, 2, g2_task.task_id, spec.model_dump_json(), res.raw_response_text, res.prompt_tokens, res.completion_tokens, lat * 1000.0, res.load_duration_ms, res.prompt_eval_duration_ms, res.eval_duration_ms, datetime.now(timezone.utc).isoformat()))

                        db.conn.execute("""
                            INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, locus_id, allele_id, is_active, parent_generation, created_by_call_id, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (node_id, run_id, current_world.world_id, 2, "derived", f"{station} {target_pred} {eval_res.normalized_object}", json.dumps({"raw_response": res.parsed_json}), locus_id, allele_id, 1 if is_written else 0, 1, call_id, datetime.now(timezone.utc).isoformat()))

                        db.conn.execute("""
                            INSERT INTO dual_oracle_evaluations (evaluation_id, call_id, node_id, generation, task_id, target_subject, target_predicate, derived_object, canonical_truth_status, local_derivability_status, A_correct, E_correct, K_consistent, phenotype, state_vector_json, ancestral_allele_fidelity, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (f"eval_{call_id}", call_id, node_id, 2, g2_task.task_id, station, target_pred, eval_res.normalized_object, eval_res.canonical_truth_status, eval_res.context_truth_status, eval_res.A_correct, eval_res.E_correct, eval_res.K_consistent, eval_res.phenotype, json.dumps(eval_res.state_vector), eval_res.ancestral_allele_fidelity, datetime.now(timezone.utc).isoformat()))

                        for exp_node_id, c_pos in exposures:
                            db.conn.execute("""
                                INSERT OR REPLACE INTO exposure_edges (parent_node_id, child_node_id, call_id, retrieval_rank, context_position)
                                VALUES (?, ?, ?, ?, ?)
                            """, (exp_node_id, node_id, call_id, c_pos, c_pos))

                        db.conn.execute("""
                            INSERT INTO transmission_opportunities (
                                opportunity_id, run_id, world_id, arm, exposure_p, parent_generation, child_generation,
                                parent_node_id, parent_locus_id, parent_phenotype, child_task_id, target_predicate,
                                is_exposed, is_generated, is_written, child_node_id, child_phenotype, ancestral_allele_fidelity, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            opportunity_id, run_id, current_world.world_id, arm, p, 1, 2,
                            parent_node_id, parent_locus_id, parent_phenotype, g2_task.task_id, target_pred,
                            1 if is_task_exposed else 0, 1 if is_generated else 0, 1 if is_written else 0,
                            node_id if is_written else None, eval_res.phenotype, eval_res.ancestral_allele_fidelity if is_task_exposed else None,
                            datetime.now(timezone.utc).isoformat()
                        ))

                    print(f"  [G2.{g2_idx+1}] {target_pred} (Exposed={is_task_exposed}): {eval_res.normalized_object} | Phenotype: {eval_res.phenotype.upper()} | Vector: {eval_res.state_vector}", flush=True)

    # -------------------------------------------------------------
    # Final Dose-Response Summary Report
    # -------------------------------------------------------------
    print("\n" + "=" * 145, flush=True)
    print(f"         EXPERIMENT 1B-A1: BALANCED EXPOSURE DOSE-RESPONSE SUMMARY REPORT", flush=True)
    print("=" * 145, flush=True)
    print(f"{'Dose (p)':<10} | {'Contact X':<10} | {'tau_S':<8} | {'Write W_hat':<12} | {'R_trans':<8} | {'R_total':<8} | {'Clean Cov C':<14} | {'mu_de_novo':<12} | {'mu_unsupp':<12} | {'Fidelity F2':<12} | {'Epidemic State'}", flush=True)
    print("-" * 145, flush=True)

    for p in grid:
        s = exposure_engine.compute_summary(exposure_p=p)
        tau_str = f"{s.epistemic_transmissibility_tau_S:.2f}" if s.epistemic_transmissibility_tau_S is not None else "N/A"
        w_str = f"{s.write_admission_W_hat:.2f}" if s.write_admission_W_hat is not None else "N/A"
        c_str = f"{s.clean_coverage_C*100:.1f}% ({s.clean_correct_derived}/{s.clean_opportunities})" if s.clean_coverage_C is not None else "N/A"
        mu_denovo_str = f"{s.mu_de_novo*100:.1f}% ({s.unexposed_false_children_emitted}/{s.unexposed_opportunities})" if s.unexposed_opportunities > 0 else "0.0%"
        mu_unsupp_str = f"{s.mu_unsupported_concrete*100:.1f}% ({s.unexposed_concrete_children_emitted}/{s.unexposed_opportunities})" if s.unexposed_opportunities > 0 else "0.0%"
        f2_str = f"{s.ancestral_fidelity_F2:.2f}" if s.ancestral_fidelity_F2 is not None else "N/A"
        
        if s.reproduction_number_R_trans > 1.0:
            rep_str = "SUPERCRITICAL (R > 1) [Amplification]"
        elif abs(s.reproduction_number_R_trans - 1.0) < 1e-4:
            rep_str = "CRITICAL (R = 1) [Replacement Equilibrium]"
        else:
            rep_str = "SUBCRITICAL (R < 1) [Lineage Decay]"
        
        print(f"p = {p:<6.2f} | X = {s.contact_rate_X:<6.2f} | {tau_str:<8} | {w_str:<12} | {s.reproduction_number_R_trans:<8.2f} | {s.reproduction_number_R_total_corruption:<8.2f} | {c_str:<14} | {mu_denovo_str:<12} | {mu_unsupp_str:<12} | {f2_str:<12} | {rep_str}", flush=True)

    print("=" * 145 + "\n", flush=True)
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B Balanced Exposure Assay")
    parser.add_argument("--worlds", type=int, default=4, help="Number of micro-worlds per dose")
    parser.add_argument("--grid", type=str, default="0.0,0.25,0.5,0.75,1.0", help="Comma-separated exposure dose grid")
    parser.add_argument("--version", type=str, default="v2", choices=["v1", "v2"], help="Prompt schema version")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model name")
    parser.add_argument("--mutated-supervisor", type=str, default="TAL", help="Mutated supervisor allele")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_exp1b_exposure_assay(
        worlds_count=args.worlds,
        grid_str=args.grid,
        prompt_version=args.version,
        model_name=args.model,
        mutated_supervisor=args.mutated_supervisor,
        db_path=args.db,
    )
