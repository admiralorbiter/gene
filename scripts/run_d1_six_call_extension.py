"""Experiment: Six-Call D1 Extension (Joint Premise Knockout + Semantic Mutation).

Runs exactly 6 targeted live Ollama calls on Gemma 3 12B across the 3 preflight D1 tasks:
1. Joint Premise Knockout: f(R, ¬A, ¬B) -> removes both Fact A and Fact B, leaving Rule.
2. Semantic Mutation: f(R, A, B') -> replaces Fact B premise with a counterfactual entity.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.config import ExperimentConfig, ModelConfig, RetrievalConfig
from gene.evaluation.causality import CausalRunner
from gene.evaluation.claims import ClaimEvaluator, EvaluatedClaim
from gene.evaluation.metrics import format_rate
from gene.experiments.runner import SingleCallRunner
from gene.ollama_client import CallSpec, OllamaClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.schema import World
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.tasks import TaskGenerator


def run_six_call_extension(source_db_path: str = "gene_d1_preflight_20260819_181409.db", model_name: str = "gemma3:12b"):
    print("=" * 80, flush=True)
    print("   GENE D1 EXTENSION: SIX-CALL JOINT KNOCKOUT & SEMANTIC MUTATION", flush=True)
    print(f"   Model: Live Ollama ({model_name})", flush=True)
    print("=" * 80, flush=True)

    db = Database(source_db_path)
    client = OllamaClient()

    # Query the 3 D1 tasks executed in the source DB
    calls = db.conn.execute("""
        SELECT c.call_id, c.run_id, c.task_id, c.request_json, c.response_text,
               r.world_id, w.canonical_json, w.world_seed
        FROM calls c
        JOIN runs r ON r.run_id = c.run_id
        JOIN worlds w ON w.world_id = r.world_id
        WHERE c.call_id NOT LIKE '%_cf_%' AND c.call_id NOT LIKE '%_ext_%'
        ORDER BY c.created_at
    """).fetchall()

    print(f"[*] Found {len(calls)} original D1 baseline calls in source DB.", flush=True)

    results_summary = []

    for idx, row in enumerate(calls):
        call_id = row["call_id"]
        run_id = row["run_id"]
        task_id = row["task_id"]
        world_seed = row["world_seed"]
        canonical_json = row["canonical_json"]
        world = World.model_validate_json(canonical_json)
        oracle = Oracle(world)

        req_json = json.loads(row["request_json"])
        resp_text = row["response_text"]

        # Parse original baseline response
        orig_parsed = json.loads(resp_text)
        orig_obj = (orig_parsed.get("answer", {}).get("object") or orig_parsed.get("object", "")).upper()
        orig_parents = orig_parsed.get("parent_memory_ids", [])

        # Fetch original exposed memories from user prompt
        user_prompt = req_json["user_prompt"]
        system_prompt = req_json["system_prompt"]

        print("\n" + "=" * 80, flush=True)
        print(f"TASK {idx+1}/3: {task_id} (World Seed: {world_seed})", flush=True)
        print(f"Baseline Derived: (..., uses_protocol, {orig_obj})", flush=True)
        print(f"Baseline Reported Parents: {orig_parents}", flush=True)

        mem_pattern = re.compile(r"\[(mem_[^\]]+)\]\s+(.*?)(?=\n\[|\n\nQuestion:|\nQuestion:|$)", re.DOTALL)
        matches = mem_pattern.findall(user_prompt)
        exposed_memories = {m_id: text.strip() for m_id, text in matches}

        rule_mid = None
        fact_a_mid = None # manager
        fact_b_mid = None # reports_to
        distractor_mids = []

        for mid, text in exposed_memories.items():
            if "operational policy:" in text.lower():
                rule_mid = mid
            elif "station manager" in text.lower():
                fact_a_mid = mid
            elif "directly reports to" in text.lower():
                fact_b_mid = mid
            else:
                distractor_mids.append(mid)

        print(f"Identified Components:", flush=True)
        print(f"  - [Rule]   [{rule_mid}]: {exposed_memories.get(rule_mid)}", flush=True)
        print(f"  - [Fact A] [{fact_a_mid}]: {exposed_memories.get(fact_a_mid)}", flush=True)
        print(f"  - [Fact B] [{fact_b_mid}]: {exposed_memories.get(fact_b_mid)}", flush=True)

        # Extract question section from prompt
        q_split = user_prompt.split("Question:")
        question_section = "Question:" + q_split[1] if len(q_split) > 1 else ""

        # -------------------------------------------------------------
        # CALL 1: JOINT PREMISE KNOCKOUT: f(R, ¬A, ¬B)
        # -------------------------------------------------------------
        print("\n--- [Call 1] Joint Premise Knockout: f(R, ¬A, ¬B) ---", flush=True)
        joint_ko_memories = [
            f"[{m_id}] {text}" for m_id, text in exposed_memories.items()
            if m_id not in (fact_a_mid, fact_b_mid)
        ]
        joint_ko_user_prompt = "Available Memories:\n" + "\n".join(joint_ko_memories) + "\n\n" + question_section

        spec_joint = CallSpec(
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=joint_ko_user_prompt,
            temperature=0.0,
            seed=42,
            format="json",
        )

        t0 = time.perf_counter()
        res_joint = client.chat(spec_joint)
        latency_joint = time.perf_counter() - t0

        joint_claim = ClaimEvaluator.evaluate_response(
            raw_text=res_joint.raw_response_text,
            parsed_json=res_joint.parsed_json,
            oracle=oracle,
        )

        print(f"  Prompt Content: Retained Rule + Distractors (Removed Fact A and Fact B)", flush=True)
        print(f"  Raw Output:     {res_joint.raw_response_text.strip()}", flush=True)
        print(f"  Derived Object: {joint_claim.object}", flush=True)
        print(f"  Parse Status:   {joint_claim.parse_status}", flush=True)
        print(f"  Reported Parents: {joint_claim.reported_parent_ids}", flush=True)
        print(f"  Telemetry:      latency={latency_joint:.2f}s | load={res_joint.load_duration_ms:.1f}ms | prompt_eval={res_joint.prompt_eval_duration_ms:.1f}ms ({res_joint.prompt_tokens} tok) | eval={res_joint.eval_duration_ms:.1f}ms ({res_joint.completion_tokens} tok)", flush=True)

        if joint_claim.object == orig_obj:
            joint_outcome = "UNCHANGED (Rule Alone Sufficient - Salience Shortcut Confirmed)"
        elif joint_claim.object in ("UNKNOWN", "UNKNOWN_OR_UNSUPPORTED"):
            joint_outcome = "UNKNOWN (Premises Jointly Required - Epistasis Confirmed)"
        else:
            joint_outcome = f"CHANGED -> {joint_claim.object}"
        print(f"  => Outcome:     {joint_outcome}", flush=True)

        # -------------------------------------------------------------
        # CALL 2: SEMANTIC MUTATION: f(R, A, B')
        # -------------------------------------------------------------
        print("\n--- [Call 2] Semantic Mutation: f(R, A, B') ---", flush=True)
        orig_fact_b_text = exposed_memories.get(fact_b_mid, "")
        if "Kira" in orig_fact_b_text:
            mutated_fact_b_text = orig_fact_b_text.replace("Kira", "Tal")
            alt_supervisor = "Tal"
        elif "Jaxon" in orig_fact_b_text:
            mutated_fact_b_text = orig_fact_b_text.replace("Jaxon", "Kira")
            alt_supervisor = "Kira"
        else:
            mutated_fact_b_text = orig_fact_b_text.replace("directly reports to ", "directly reports to Vance (mutated). ")
            alt_supervisor = "Vance"

        mutation_memories = []
        for m_id, text in exposed_memories.items():
            if m_id == fact_b_mid:
                mutation_memories.append(f"[{m_id}_mutated] {mutated_fact_b_text}")
            else:
                mutation_memories.append(f"[{m_id}] {text}")

        mutation_user_prompt = "Available Memories:\n" + "\n".join(mutation_memories) + "\n\n" + question_section

        spec_mutation = CallSpec(
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=mutation_user_prompt,
            temperature=0.0,
            seed=42,
            format="json",
        )

        t0 = time.perf_counter()
        res_mutation = client.chat(spec_mutation)
        latency_mutation = time.perf_counter() - t0

        mutation_claim = ClaimEvaluator.evaluate_response(
            raw_text=res_mutation.raw_response_text,
            parsed_json=res_mutation.parsed_json,
            oracle=oracle,
        )

        print(f"  Mutated Fact B: '{orig_fact_b_text}' -> '{mutated_fact_b_text}'", flush=True)
        print(f"  Raw Output:     {res_mutation.raw_response_text.strip()}", flush=True)
        print(f"  Derived Object: {mutation_claim.object}", flush=True)
        print(f"  Parse Status:   {mutation_claim.parse_status}", flush=True)
        print(f"  Reported Parents: {mutation_claim.reported_parent_ids}", flush=True)
        print(f"  Telemetry:      latency={latency_mutation:.2f}s | load={res_mutation.load_duration_ms:.1f}ms | prompt_eval={res_mutation.prompt_eval_duration_ms:.1f}ms ({res_mutation.prompt_tokens} tok) | eval={res_mutation.eval_duration_ms:.1f}ms ({res_mutation.completion_tokens} tok)", flush=True)

        if mutation_claim.object == orig_obj:
            mut_outcome = "UNCHANGED (Model ignored mutated premise, outputted rule token)"
        elif mutation_claim.object in ("UNKNOWN", "UNKNOWN_OR_UNSUPPORTED"):
            mut_outcome = "UNKNOWN (Model recognized antecedent mismatch with mutated premise)"
        else:
            mut_outcome = f"MUTATED TO {mutation_claim.object} (Model followed mutation)"
        print(f"  => Outcome:     {mut_outcome}", flush=True)

        # Persist extension calls into DB
        with db.conn:
            db.conn.execute("""
                INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, latency_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (f"{call_id}_ext_joint_ko", run_id, 1, f"{task_id}_joint_ko", spec_joint.model_dump_json(), res_joint.raw_response_text, latency_joint * 1000.0, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

            db.conn.execute("""
                INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, latency_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (f"{call_id}_ext_mutation", run_id, 1, f"{task_id}_mutation", spec_mutation.model_dump_json(), res_mutation.raw_response_text, latency_mutation * 1000.0, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

        results_summary.append({
            "task_id": task_id,
            "target": orig_obj,
            "joint_ko_derived": joint_claim.object,
            "joint_outcome": joint_outcome,
            "mutation_derived": mutation_claim.object,
            "mutation_outcome": mut_outcome,
        })

    print("\n" + "=" * 80, flush=True)
    print("                     SIX-CALL D1 EXTENSION SUMMARY", flush=True)
    print("=" * 80, flush=True)
    for r in results_summary:
        print(f"Task: {r['task_id']}", flush=True)
        print(f"  - Target Fact Object:           {r['target']}", flush=True)
        print(f"  - Joint Knockout f(R,¬A,¬B):    {r['joint_ko_derived']} ({r['joint_outcome']})", flush=True)
        print(f"  - Semantic Mutation f(R,A,B'):  {r['mutation_derived']} ({r['mutation_outcome']})", flush=True)
    print("=" * 80, flush=True)
    print(f"Results recorded in DB: {source_db_path}", flush=True)
    print("=" * 80 + "\n", flush=True)

    db.close()


if __name__ == "__main__":
    db_file = "gene_d1_preflight_20260819_181409.db"
    model = "gemma3:12b"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        db_file = sys.argv[1]
    run_six_call_extension(source_db_path=db_file, model_name=model)
