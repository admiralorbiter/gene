"""Experiment: D1-C Competing-Consequent 10-Intervention Biological Assay.

Executes the complete 10-intervention biological assay across D1-C micro-worlds:
1. Clean Baseline (Full R+A+B) -> Target Protocol (e.g. PROTO_X7)
2. Knockout Fact A -> UNKNOWN
3. Knockout Fact B -> UNKNOWN
4. Knockout Active Rule -> UNKNOWN
5. Knockout Foil Rule -> Target Protocol (Control)
6. Epistasis Double Knockout (A + B) -> UNKNOWN
7. Directional Mutation 1 (reports_to Kira -> Tal) -> Directional Redirection to PROTO_Q2
8. Directional Mutation 2 (reports_to Kira -> Mira) -> Directional Redirection to PROTO_M9
9. Unmatched Mutation (reports_to Kira -> Soren) -> Abstention to UNKNOWN
10. Rescue (Tal -> Kira) -> Causal Recovery to PROTO_X7
11. No-op Sham Replay -> PROTO_X7 (S0 Stability)
12. Distractor Removal -> PROTO_X7 (HD Control)

Supports both Schema v1 (Cell 3) and Schema v2 (Cell 4) with first-class counterfactual oracles and timing telemetry.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
import time
from pathlib import Path

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.config import ExperimentConfig, ModelConfig, RetrievalConfig
from gene.evaluation.claims import ClaimEvaluator, EvaluatedClaim
from gene.evaluation.interventions import CounterfactualOracle, InterventionSpec, InterventionType
from gene.ollama_client import CallSpec, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.competing import generate_d1_c_world
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.renderer import NaturalLanguageRenderer


def render_memory_block(bundle, intervention: InterventionSpec | None = None) -> list[dict[str, str]]:
    """Render memory slot records with constant slot IDs."""
    memories = []
    target_ids = set(intervention.target_node_ids) if intervention else set()
    itype = intervention.intervention_type if intervention else None
    mutated_mem = intervention.mutated_memories if intervention else {}

    # 1. Rules
    for r in bundle.world.rules:
        if r.rule_id in target_ids:
            if itype in (InterventionType.KNOCKOUT, InterventionType.EPISTASIS, InterventionType.CONTROL_DISTRACTOR):
                continue
        text = NaturalLanguageRenderer.render_rule(r)
        memories.append({"memory_id": f"mem_{r.rule_id}", "text": text, "raw_id": r.rule_id})

    # 2. Facts
    for f in bundle.world.facts:
        if f.fact_id in target_ids:
            if itype in (InterventionType.KNOCKOUT, InterventionType.EPISTASIS):
                continue
            elif itype in (InterventionType.MUTATION, InterventionType.RESCUE):
                if f.fact_id in mutated_mem:
                    # Preserve constant slot ID while supplying mutated text
                    memories.append({"memory_id": f"mem_{f.fact_id}", "text": mutated_mem[f.fact_id], "raw_id": f.fact_id})
                    continue
            elif itype == InterventionType.CONTROL_DISTRACTOR:
                continue
        text = NaturalLanguageRenderer.render_fact(f)
        memories.append({"memory_id": f"mem_{f.fact_id}", "text": text, "raw_id": f.fact_id})

    return memories


def run_d1_c_assay(
    worlds_count: int = 3,
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    db_path: str | None = None,
):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if not db_path:
        db_path = f"gene_d1_c_{prompt_version}_{timestamp}.db"

    print("=" * 85, flush=True)
    print(f"   GENE D1-C COMPETING-CONSEQUENTS BIOLOGICAL ASSAY (Schema {prompt_version.upper()})", flush=True)
    print(f"   Model: Live Ollama ({model_name}) | Worlds: {worlds_count} | Database: {db_path}", flush=True)
    print("=" * 85, flush=True)

    db = Database(db_path)
    client = OllamaClient()
    template = PromptTemplate(prompt_version)

    overall_results = []

    for w_idx in range(worlds_count):
        seed = 42 + w_idx * 17
        rotation_idx = w_idx % 3
        perm_idx = w_idx % 6
        bundle = generate_d1_c_world(world_seed=seed, rotation_idx=rotation_idx, rule_perm_idx=perm_idx)
        db.save_world(bundle.world)

        run_id = f"run_d1_c_{bundle.world.world_id}"
        with db.conn:
            db.conn.execute("""
                INSERT OR REPLACE INTO runs (
                    run_id, experiment_name, experiment_version, condition, world_id,
                    model_name, seed, num_ctx, temperature, prompt_version, started_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, "d1_c_competing_assay", "1.0.0", "competing_rules",
                bundle.world.world_id, model_name, 42, 4096, 0.0, prompt_version,
                datetime.now(timezone.utc).isoformat(), "running"
            ))

        # Populate memory_nodes for world facts and rules
        with db.conn:
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

        print(f"\n" + "=" * 85, flush=True)
        print(f"WORLD {w_idx+1}/{worlds_count}: {bundle.world.world_id} (Seed: {seed}, Rotation: {rotation_idx}, Perm: {perm_idx})", flush=True)
        print(f"Target Subject: {bundle.task.target_fact.subject} | Target Protocol: {bundle.target_protocol}", flush=True)
        print(f"Active Rule:    {bundle.active_rule.rule_id}", flush=True)
        print(f"Foil Rules:     {[r.rule_id for r in bundle.foil_rules]}", flush=True)
        print(f"Fact A:         {NaturalLanguageRenderer.render_fact(bundle.fact_a)}", flush=True)
        print(f"Fact B:         {NaturalLanguageRenderer.render_fact(bundle.fact_b)}", flush=True)

        question_prompt = NaturalLanguageRenderer.render_task_prompt(bundle.task.target_fact.subject, bundle.task.target_fact.predicate)

        # -------------------------------------------------------------
        # 1. Clean Baseline Invocation
        # -------------------------------------------------------------
        clean_mems = render_memory_block(bundle, intervention=None)
        clean_prompt = template.format_user_prompt(
            memories=clean_mems,
            question_prompt=question_prompt,
            target_subject=bundle.task.target_fact.subject,
            target_predicate=bundle.task.target_fact.predicate,
        )

        spec_clean = CallSpec(
            model_name=model_name,
            system_prompt=template.system_prompt,
            user_prompt=clean_prompt,
            temperature=0.0,
            seed=42,
            format=template.format_schema,
        )

        t0 = time.perf_counter()
        res_clean = client.chat(spec_clean)
        lat_clean = time.perf_counter() - t0

        oracle_clean = Oracle(bundle.world)
        claim_clean = ClaimEvaluator.evaluate_response(
            raw_text=res_clean.raw_response_text,
            parsed_json=res_clean.parsed_json,
            oracle=oracle_clean,
        )

        call_id_clean = f"call_{bundle.world.world_id}_clean"
        node_id_clean = f"node_{call_id_clean}"
        with db.conn:
            db.conn.execute("""
                INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (call_id_clean, run_id, 1, bundle.task.task_id, spec_clean.model_dump_json(), res_clean.raw_response_text, res_clean.prompt_tokens, res_clean.completion_tokens, lat_clean * 1000.0, res_clean.load_duration_ms, res_clean.prompt_eval_duration_ms, res_clean.eval_duration_ms, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

            db.conn.execute("""
                INSERT INTO memory_nodes (node_id, run_id, world_id, generation, node_type, natural_text, structured_json, created_by_call_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (node_id_clean, run_id, bundle.world.world_id, 1, "derived", f"{bundle.task.target_fact.subject} uses_protocol {claim_clean.object}", claim_clean.model_dump_json(), call_id_clean, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

        print(f"\n--- Clean Baseline ---", flush=True)
        print(f"  Raw Output:       {res_clean.raw_response_text.strip()}", flush=True)
        print(f"  Evidence Status:  {claim_clean.evidence_status}", flush=True)
        print(f"  Derived Object:   {claim_clean.object} (Expected: {bundle.target_protocol})", flush=True)
        print(f"  Truth Status:     {claim_clean.truth_status}", flush=True)
        print(f"  Reported Parents: {claim_clean.reported_parent_ids}", flush=True)
        print(f"  Telemetry:        latency={lat_clean:.2f}s | prompt_eval={res_clean.prompt_eval_duration_ms:.1f}ms | eval={res_clean.eval_duration_ms:.1f}ms", flush=True)

        # -------------------------------------------------------------
        # 2. Execute 11 Interventions
        # -------------------------------------------------------------
        intervention_results = []

        for iv in bundle.interventions:
            iv_mems = render_memory_block(bundle, intervention=iv)
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

            # Counterfactual Oracle Evaluation
            cf_oracle = CounterfactualOracle(base_world=bundle.world, intervention=iv)
            claim_iv = ClaimEvaluator.evaluate_response(
                raw_text=res_iv.raw_response_text,
                parsed_json=res_iv.parsed_json,
                oracle=cf_oracle.counterfactual_oracle,
            )

            call_id_iv = f"call_{bundle.world.world_id}_{iv.intervention_id}"
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
                    f"node_{call_id_clean}",
                    call_id_clean,
                    iv.intervention_type.value,
                    42,
                    call_id_iv,
                    "matched" if claim_iv.object == iv.expected_counterfactual_object else "unmatched",
                    1.0 if claim_iv.object == iv.expected_counterfactual_object else 0.0,
                    json.dumps({"derived": claim_iv.object, "expected": iv.expected_counterfactual_object}),
                    json.dumps(iv.target_node_ids),
                    json.dumps(iv.mutated_memories),
                    str(claim_clean.truth_status),
                    str(claim_iv.truth_status),
                    claim_iv.evidence_status,
                    iv.rescue_source_call_id,
                ))

            # Classify match vs expected
            is_match = (claim_iv.object == iv.expected_counterfactual_object)
            status_match = (claim_iv.evidence_status == iv.expected_evidence_status) if iv.expected_evidence_status else True
            match_str = "PASS [MATCHED]" if (is_match and status_match) else "FAIL [UNMATCHED]"

            print(f"\n  [{iv.intervention_id}] ({iv.description}):", flush=True)
            print(f"    Raw Output:       {res_iv.raw_response_text.strip()}", flush=True)
            print(f"    Evidence Status:  {claim_iv.evidence_status} (Expected: {iv.expected_evidence_status})", flush=True)
            print(f"    Derived Object:   {claim_iv.object} (Expected: {iv.expected_counterfactual_object})", flush=True)
            print(f"    CF Truth Status:  {claim_iv.truth_status}", flush=True)
            print(f"    Assay Verdict:    {match_str}", flush=True)
            print(f"    Telemetry:        latency={lat_iv:.2f}s | prompt_eval={res_iv.prompt_eval_duration_ms:.1f}ms | eval={res_iv.eval_duration_ms:.1f}ms", flush=True)

            intervention_results.append({
                "id": iv.intervention_id,
                "type": iv.intervention_type.value,
                "expected": iv.expected_counterfactual_object,
                "derived": claim_iv.object,
                "evidence_status": claim_iv.evidence_status,
                "verdict": match_str,
                "latency_s": lat_iv,
            })

        overall_results.append({
            "world_id": bundle.world.world_id,
            "target": bundle.target_protocol,
            "clean_derived": claim_clean.object,
            "clean_truth": str(claim_clean.truth_status),
            "interventions": intervention_results,
        })

    # Summary Table
    print("\n" + "=" * 85, flush=True)
    print(f"             D1-C COMPETING-CONSEQUENTS BIOLOGICAL ASSAY SUMMARY ({prompt_version.upper()})", flush=True)
    print("=" * 85, flush=True)
    for res in overall_results:
        print(f"\nWorld: {res['world_id']} (Target: {res['target']}) -> Baseline: {res['clean_derived']} ({res['clean_truth']})", flush=True)
        print(f"  {'-'*80}", flush=True)
        for iv in res["interventions"]:
            print(f"  {iv['id']:<24} | Expected: {iv['expected']:<10} | Derived: {iv['derived']:<10} | Status: {iv['evidence_status']:<12} | {iv['verdict']}", flush=True)

    print("=" * 85, flush=True)
    print(f"Database Preserved At: {db_path}", flush=True)
    print("=" * 85 + "\n", flush=True)
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run D1-C Competing Consequents Assay")
    parser.add_argument("--worlds", type=int, default=1, help="Number of micro-worlds to test")
    parser.add_argument("--version", type=str, default="v2", choices=["v1", "v2"], help="Prompt schema version (v1 or v2)")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model name")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_d1_c_assay(
        worlds_count=args.worlds,
        prompt_version=args.version,
        model_name=args.model,
        db_path=args.db,
    )
