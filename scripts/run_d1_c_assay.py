"""Hardened Matched 2x2 Biological Assay Runner.

Executes the biological assay across counterbalanced micro-worlds:
- Matched ecologies: Ecology S (single rule) vs Ecology C (competing rules) derived from identical canonical worlds.
- Unadulterated scoring with 3 independent diagnostic metrics:
  * A: Answer Correctness [normalized_object == expected_counterfactual_object]
  * E: Status Correctness [raw_evidence_status == expected_evidence_status]
  * K: Contract Consistency [(evidence_status in {insufficient, conflicting}) => (object == UNKNOWN)]
- True sequential compositional rescue chain:
  S0 (Clean Baseline, Kira) -> S1 (Mutation, Tal) -> S2 (Rescue, Kira)
  Tracking Y(S0)=X7 -> Y(S1)=Q2 -> Y(S2)=X7.
- Full timing telemetry and SQLite persistence.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
import time
from pathlib import Path
from typing import Literal

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.config import ExperimentConfig, ModelConfig, RetrievalConfig
from gene.evaluation.claims import ClaimEvaluator, EvaluatedClaim
from gene.evaluation.interventions import (
    CounterfactualOracle,
    InterventionSpec,
    InterventionType,
    apply_intervention,
    compose_interventions,
)
from gene.ollama_client import CallSpec, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.competing import generate_d1_c_world
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.renderer import NaturalLanguageRenderer


def render_memory_block_for_world(world, active_text_overrides: dict[str, str] | None = None) -> list[dict[str, str]]:
    """Render memory slot records directly from a canonical World object with optional text overrides."""
    memories = []
    overrides = active_text_overrides or {}

    for r in world.rules:
        text = overrides.get(r.rule_id, NaturalLanguageRenderer.render_rule(r))
        memories.append({"memory_id": f"mem_{r.rule_id}", "text": text, "raw_id": r.rule_id})

    for f in world.facts:
        text = overrides.get(f.fact_id, NaturalLanguageRenderer.render_fact(f))
        memories.append({"memory_id": f"mem_{f.fact_id}", "text": text, "raw_id": f.fact_id})

    return memories


def run_hardened_assay(
    worlds_count: int = 6,
    prompt_version: str = "v2",
    ecology: Literal["S", "C"] = "C",
    model_name: str = "gemma3:12b",
    db_path: str | None = None,
):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if not db_path:
        db_path = f"gene_d1_{ecology.lower()}_{prompt_version}_{timestamp}.db"

    print("=" * 90, flush=True)
    print(f"   GENE HARDENED BIOLOGICAL ASSAY (Ecology: {ecology} | Schema: {prompt_version.upper()})", flush=True)
    print(f"   Model: Live Ollama ({model_name}) | Worlds: {worlds_count} | Database: {db_path}", flush=True)
    print("=" * 90, flush=True)

    db = Database(db_path)
    client = OllamaClient()
    template = PromptTemplate(prompt_version)

    overall_results = []

    for w_idx in range(worlds_count):
        seed = 42 + w_idx * 17
        rotation_idx = w_idx % 3
        perm_idx = w_idx % 6
        bundle = generate_d1_c_world(world_seed=seed, rotation_idx=rotation_idx, rule_perm_idx=perm_idx, ecology=ecology)
        db.save_world(bundle.world)

        run_id = f"run_d1_{ecology.lower()}_{bundle.world.world_id}"
        with db.conn:
            db.conn.execute("""
                INSERT OR REPLACE INTO runs (
                    run_id, experiment_name, experiment_version, condition, world_id,
                    model_name, seed, num_ctx, temperature, prompt_version, started_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, f"d1_{ecology.lower()}_hardened_assay", "2.0.0", f"ecology_{ecology}",
                bundle.world.world_id, model_name, 42, 4096, 0.0, prompt_version,
                datetime.now(timezone.utc).isoformat(), "running"
            ))

            # Populate source memory nodes
            for f in bundle.world.facts:
                db.conn.execute("""
                    INSERT OR REPLACE INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (f.fact_id, run_id, bundle.world.world_id, 0, "source", NaturalLanguageRenderer.render_fact(f), f.canonical_json(), datetime.now(timezone.utc).isoformat()))

            for r in bundle.world.rules:
                db.conn.execute("""
                    INSERT OR REPLACE INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (r.rule_id, run_id, bundle.world.world_id, 0, "rule", NaturalLanguageRenderer.render_rule(r), r.canonical_json(), datetime.now(timezone.utc).isoformat()))

        print(f"\n" + "=" * 90, flush=True)
        print(f"WORLD {w_idx+1}/{worlds_count}: {bundle.world.world_id} (Seed: {seed}, Rotation: {rotation_idx}, Perm: {perm_idx})", flush=True)
        print(f"Target Subject:  {bundle.task.target_fact.subject} | Target Protocol: {bundle.target_protocol}", flush=True)
        print(f"Fact A:          {NaturalLanguageRenderer.render_fact(bundle.fact_a)}", flush=True)
        print(f"Fact B:          {NaturalLanguageRenderer.render_fact(bundle.fact_b)}", flush=True)
        print(f"Active Rule:     {bundle.active_rule.rule_id}", flush=True)
        if ecology == "C":
            print(f"Foil Rules:      {[r.rule_id for r in bundle.foil_rules]}", flush=True)

        question_prompt = NaturalLanguageRenderer.render_task_prompt(bundle.task.target_fact.subject, bundle.task.target_fact.predicate)

        # -------------------------------------------------------------
        # 1. Clean Baseline (S0 State)
        # -------------------------------------------------------------
        s0_mems = render_memory_block_for_world(bundle.world)
        s0_prompt = template.format_user_prompt(
            memories=s0_mems,
            question_prompt=question_prompt,
            target_subject=bundle.task.target_fact.subject,
            target_predicate=bundle.task.target_fact.predicate,
        )

        spec_s0 = CallSpec(
            model_name=model_name,
            system_prompt=template.system_prompt,
            user_prompt=s0_prompt,
            temperature=0.0,
            seed=42,
            format=template.format_schema,
        )

        t0 = time.perf_counter()
        res_s0 = client.chat(spec_s0)
        lat_s0 = time.perf_counter() - t0

        oracle_s0 = Oracle(bundle.world)
        claim_s0 = ClaimEvaluator.evaluate_response(
            raw_text=res_s0.raw_response_text,
            parsed_json=res_s0.parsed_json,
            oracle=oracle_s0,
        )

        call_id_s0 = f"call_{bundle.world.world_id}_s0_clean"
        node_id_s0 = f"node_{call_id_s0}"
        with db.conn:
            db.conn.execute("""
                INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (call_id_s0, run_id, 1, bundle.task.task_id, spec_s0.model_dump_json(), res_s0.raw_response_text, res_s0.prompt_tokens, res_s0.completion_tokens, lat_s0 * 1000.0, res_s0.load_duration_ms, res_s0.prompt_eval_duration_ms, res_s0.eval_duration_ms, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

            db.conn.execute("""
                INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, created_by_call_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (node_id_s0, run_id, bundle.world.world_id, 1, "derived", f"{bundle.task.target_fact.subject} uses_protocol {claim_s0.object}", claim_s0.model_dump_json(), call_id_s0, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

        print(f"\n--- S0: Clean Baseline ---", flush=True)
        print(f"  Raw Output:       {res_s0.raw_response_text.strip()}", flush=True)
        print(f"  Evidence Status:  {claim_s0.raw_evidence_status}", flush=True)
        print(f"  Derived Object:   {claim_s0.object} (Expected: {bundle.target_protocol})", flush=True)
        print(f"  Truth Status:     {claim_s0.truth_status}", flush=True)
        print(f"  Contract Status:  K={claim_s0.is_contract_consistent}", flush=True)
        print(f"  Reported Parents: {claim_s0.reported_parent_ids}", flush=True)
        print(f"  Telemetry:        latency={lat_s0:.2f}s | prompt_eval={res_s0.prompt_eval_duration_ms:.1f}ms | eval={res_s0.eval_duration_ms:.1f}ms", flush=True)

        # -------------------------------------------------------------
        # 2. Execute Interventions with Sequential Rescue Lineage
        # -------------------------------------------------------------
        intervention_results = []
        s1_tal_world = None
        call_id_s1 = None

        for iv in bundle.interventions:
            # Check if this is the compositional rescue intervention
            if iv.intervention_type == InterventionType.RESCUE:
                # S2 is a true descendant of S1 (Tal-mutated state)
                base_for_iv = s1_tal_world if s1_tal_world is not None else bundle.world
                cf_world = apply_intervention(base_for_iv, iv)
                overrides = iv.mutated_memories
            elif iv.intervention_type == InterventionType.MUTATION:
                cf_world = apply_intervention(bundle.world, iv)
                overrides = iv.mutated_memories
                if iv.intervention_id == "mut_redirect_tal":
                    s1_tal_world = cf_world
            else:
                cf_world = apply_intervention(bundle.world, iv)
                overrides = {}

            iv_mems = render_memory_block_for_world(cf_world, active_text_overrides=overrides)
            iv_prompt = template.format_user_prompt(
                memories=iv_mems,
                question_prompt=question_prompt,
                target_subject=bundle.task.target_fact.subject,
                target_predicate=bundle.task.target_fact.predicate,
            )

            spec_iv = CallSpec(
                model_name=model_name,
                system_prompt=template.system_prompt,
                user_prompt=iv_prompt,
                temperature=0.0,
                seed=42,
                format=template.format_schema,
            )

            t0 = time.perf_counter()
            res_iv = client.chat(spec_iv)
            lat_iv = time.perf_counter() - t0

            cf_oracle = Oracle(cf_world)
            claim_iv = ClaimEvaluator.evaluate_response(
                raw_text=res_iv.raw_response_text,
                parsed_json=res_iv.parsed_json,
                oracle=cf_oracle,
            )

            call_id_iv = f"call_{bundle.world.world_id}_{iv.intervention_id}"
            if iv.intervention_id == "mut_redirect_tal":
                call_id_s1 = call_id_iv

            # Diagnostics: A, E, K
            a_correct = (claim_iv.object == iv.expected_counterfactual_object)
            e_correct = (claim_iv.raw_evidence_status == iv.expected_evidence_status) if iv.expected_evidence_status else True
            k_consistent = claim_iv.is_contract_consistent
            all_pass = (a_correct and e_correct and k_consistent)

            with db.conn:
                db.conn.execute("""
                    INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (call_id_iv, run_id, 1, f"{bundle.task.task_id}_{iv.intervention_id}", spec_iv.model_dump_json(), res_iv.raw_response_text, res_iv.prompt_tokens, res_iv.completion_tokens, lat_iv * 1000.0, res_iv.load_duration_ms, res_iv.prompt_eval_duration_ms, res_iv.eval_duration_ms, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

                db.conn.execute("""
                    INSERT INTO causal_tests (
                        causal_test_id, parent_node_id, child_node_id, original_call_id,
                        intervention_type, intervention_seed, counterfactual_call_id,
                        outcome, score, comparison_json, target_node_ids_json, mutation_spec_json,
                        original_truth_status, counterfactual_truth_status, evidence_status, rescue_source_call_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"test_{call_id_iv}",
                    iv.target_node_ids[0] if iv.target_node_ids else "none",
                    node_id_s0,
                    call_id_s0,
                    iv.intervention_type.value,
                    42,
                    call_id_iv,
                    "matched" if all_pass else "unmatched",
                    1.0 if all_pass else 0.0,
                    json.dumps({
                        "derived_object": claim_iv.object,
                        "expected_object": iv.expected_counterfactual_object,
                        "raw_evidence_status": claim_iv.raw_evidence_status,
                        "expected_evidence_status": iv.expected_evidence_status,
                        "A_correct": a_correct,
                        "E_correct": e_correct,
                        "K_consistent": k_consistent,
                    }),
                    json.dumps(iv.target_node_ids),
                    json.dumps(iv.mutated_memories),
                    str(claim_s0.truth_status),
                    str(claim_iv.truth_status),
                    claim_iv.evidence_status,
                    call_id_s1 if iv.intervention_type == InterventionType.RESCUE else None,
                ))

            verdict_str = "PASS [ALL MATCHED]" if all_pass else f"FAIL [A={a_correct}, E={e_correct}, K={k_consistent}]"

            print(f"\n  [{iv.intervention_id}] ({iv.description}):", flush=True)
            print(f"    Raw Output:       {res_iv.raw_response_text.strip()}", flush=True)
            print(f"    Evidence Status:  {claim_iv.raw_evidence_status} (Expected: {iv.expected_evidence_status})", flush=True)
            print(f"    Derived Object:   {claim_iv.object} (Expected: {iv.expected_counterfactual_object})", flush=True)
            print(f"    Diagnostics:      A={a_correct} | E={e_correct} | K={k_consistent}", flush=True)
            print(f"    Assay Verdict:    {verdict_str}", flush=True)
            print(f"    Telemetry:        latency={lat_iv:.2f}s | prompt_eval={res_iv.prompt_eval_duration_ms:.1f}ms | eval={res_iv.eval_duration_ms:.1f}ms", flush=True)

            intervention_results.append({
                "id": iv.intervention_id,
                "type": iv.intervention_type.value,
                "expected_obj": iv.expected_counterfactual_object,
                "derived_obj": claim_iv.object,
                "expected_ev": iv.expected_evidence_status,
                "derived_ev": claim_iv.raw_evidence_status,
                "A": a_correct,
                "E": e_correct,
                "K": k_consistent,
                "pass": all_pass,
                "verdict": verdict_str,
            })

        overall_results.append({
            "world_id": bundle.world.world_id,
            "target": bundle.target_protocol,
            "s0_derived": claim_s0.object,
            "s0_truth": str(claim_s0.truth_status),
            "interventions": intervention_results,
        })

    # Summary Report
    print("\n" + "=" * 90, flush=True)
    print(f"          HARDENED ASSAY SUMMARY: Ecology {ecology} | Schema {prompt_version.upper()}", flush=True)
    print("=" * 90, flush=True)

    total_tests = 0
    passed_tests = 0

    for res in overall_results:
        print(f"\nWorld: {res['world_id']} (Target: {res['target']}) -> S0: {res['s0_derived']} ({res['s0_truth']})", flush=True)
        print(f"  {'-'*85}", flush=True)
        for iv in res["interventions"]:
            total_tests += 1
            if iv["pass"]:
                passed_tests += 1
            print(f"  {iv['id']:<22} | Exp: {iv['expected_obj']:<10} | Der: {iv['derived_obj']:<10} | Ev: {iv['derived_ev']:<12} | [A={int(iv['A'])},E={int(iv['E'])},K={int(iv['K'])}] -> {iv['verdict']}", flush=True)

    pass_rate = (passed_tests / total_tests) * 100.0 if total_tests > 0 else 0.0
    print("\n" + "=" * 90, flush=True)
    print(f"  TOTAL SCORE: {passed_tests}/{total_tests} PASSED ({pass_rate:.1f}%)", flush=True)
    print(f"  Database Preserved At: {db_path}", flush=True)
    print("=" * 90 + "\n", flush=True)
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Hardened Matched Assay")
    parser.add_argument("--worlds", type=int, default=6, help="Number of micro-worlds to test")
    parser.add_argument("--ecology", type=str, default="C", choices=["S", "C"], help="Information ecology: S (Single) or C (Competing)")
    parser.add_argument("--version", type=str, default="v2", choices=["v1", "v2"], help="Prompt schema version (v1 or v2)")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model name")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_hardened_assay(
        worlds_count=args.worlds,
        prompt_version=args.version,
        ecology=args.ecology,
        model_name=args.model,
        db_path=args.db,
    )
