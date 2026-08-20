"""2x2 Factorial Cell 2: D1-S (Single Consequent) with Schema v2 (Strict Abstention Contract).

Runs the 3 preflight D1 tasks on live Gemma 3 12B under Schema v2:
1. Baseline clean call with Schema v2
2. Joint Premise Knockout: f(R, ¬A, ¬B) with Schema v2 (tests if detection-to-abstention gap is closed)
3. Semantic Mutation: f(R, A, B') with Schema v2 (tests if antecedent violation persists)
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
from gene.evaluation.claims import ClaimEvaluator, EvaluatedClaim
from gene.evaluation.interventions import CounterfactualOracle, InterventionSpec, InterventionType
from gene.ollama_client import CallSpec, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.schema import Fact, World


def run_d1_s_v2(source_db_path: str = "gene_d1_preflight_20260819_181409.db", model_name: str = "gemma3:12b"):
    print("=" * 80, flush=True)
    print("   GENE 2x2 FACTORIAL CELL 2: D1-S (Single Consequent) + Schema v2 (Abstention)", flush=True)
    print(f"   Model: Live Ollama ({model_name})", flush=True)
    print("=" * 80, flush=True)

    db = Database(source_db_path)
    client = OllamaClient()
    template_v2 = PromptTemplate("v2")

    calls = db.conn.execute("""
        SELECT c.call_id, c.run_id, c.task_id, c.request_json, c.response_text,
               r.world_id, w.canonical_json, w.world_seed
        FROM calls c
        JOIN runs r ON r.run_id = c.run_id
        JOIN worlds w ON w.world_id = r.world_id
        WHERE c.call_id NOT LIKE '%_cf_%' AND c.call_id NOT LIKE '%_ext_%'
        ORDER BY c.created_at
    """).fetchall()

    print(f"[*] Found {len(calls)} original D1 baseline tasks.", flush=True)

    results_v2 = []

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

        orig_parsed = json.loads(resp_text)
        orig_obj = (orig_parsed.get("answer", {}).get("object") or orig_parsed.get("object", "")).upper()

        user_prompt_v1 = req_json["user_prompt"]

        print("\n" + "=" * 80, flush=True)
        print(f"TASK {idx+1}/3: {task_id} (World Seed: {world_seed})", flush=True)
        print(f"Schema v1 Baseline Object: {orig_obj}", flush=True)

        mem_pattern = re.compile(r"\[(mem_[^\]]+)\]\s+(.*?)(?=\n\[|\n\nQuestion:|\nQuestion:|$)", re.DOTALL)
        matches = mem_pattern.findall(user_prompt_v1)
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

        q_split = user_prompt_v1.split("Question:")
        question_section = "Question:" + q_split[1] if len(q_split) > 1 else ""

        # -------------------------------------------------------------
        # STEP 1: CLEAN BASELINE WITH SCHEMA V2
        # -------------------------------------------------------------
        print("\n--- [Call 1] Clean Baseline (Full Context) with Schema v2 ---", flush=True)
        clean_memories = [f"[{m_id}] {text}" for m_id, text in exposed_memories.items()]
        clean_user_prompt = "Available Memories:\n" + "\n".join(clean_memories) + "\n\n" + question_section

        spec_clean = CallSpec(
            model_name=model_name,
            system_prompt=template_v2.system_prompt,
            user_prompt=clean_user_prompt,
            temperature=0.0,
            seed=42,
            format=template_v2.format_schema,
        )

        t0 = time.perf_counter()
        res_clean = client.chat(spec_clean)
        lat_clean = time.perf_counter() - t0

        claim_clean = ClaimEvaluator.evaluate_response(
            raw_text=res_clean.raw_response_text,
            parsed_json=res_clean.parsed_json,
            oracle=oracle,
        )

        print(f"  Raw Output:       {res_clean.raw_response_text.strip()}", flush=True)
        print(f"  Evidence Status:  {claim_clean.evidence_status}", flush=True)
        print(f"  Derived Object:   {claim_clean.object}", flush=True)
        print(f"  Truth Status:     {claim_clean.truth_status}", flush=True)
        print(f"  Reported Parents: {claim_clean.reported_parent_ids}", flush=True)
        print(f"  Telemetry:        latency={lat_clean:.2f}s | prompt_eval={res_clean.prompt_eval_duration_ms:.1f}ms | eval={res_clean.eval_duration_ms:.1f}ms", flush=True)

        # -------------------------------------------------------------
        # STEP 2: JOINT PREMISE KNOCKOUT: f(R, ¬A, ¬B) WITH SCHEMA V2
        # -------------------------------------------------------------
        print("\n--- [Call 2] Joint Premise Knockout: f(R, ¬A, ¬B) with Schema v2 ---", flush=True)
        joint_ko_memories = [
            f"[{m_id}] {text}" for m_id, text in exposed_memories.items()
            if m_id not in (fact_a_mid, fact_b_mid)
        ]
        joint_ko_user_prompt = "Available Memories:\n" + "\n".join(joint_ko_memories) + "\n\n" + question_section

        spec_joint = CallSpec(
            model_name=model_name,
            system_prompt=template_v2.system_prompt,
            user_prompt=joint_ko_user_prompt,
            temperature=0.0,
            seed=42,
            format=template_v2.format_schema,
        )

        t0 = time.perf_counter()
        res_joint = client.chat(spec_joint)
        lat_joint = time.perf_counter() - t0

        claim_joint = ClaimEvaluator.evaluate_response(
            raw_text=res_joint.raw_response_text,
            parsed_json=res_joint.parsed_json,
            oracle=oracle,
        )

        print(f"  Prompt Content:   Retained Rule + Distractors (Removed Fact A and Fact B)", flush=True)
        print(f"  Raw Output:       {res_joint.raw_response_text.strip()}", flush=True)
        print(f"  Evidence Status:  {claim_joint.evidence_status}", flush=True)
        print(f"  Derived Object:   {claim_joint.object}", flush=True)
        print(f"  Reported Parents: {claim_joint.reported_parent_ids}", flush=True)
        print(f"  Telemetry:        latency={lat_joint:.2f}s | prompt_eval={res_joint.prompt_eval_duration_ms:.1f}ms | eval={res_joint.eval_duration_ms:.1f}ms", flush=True)

        if claim_joint.object in ("UNKNOWN", "UNKNOWN_OR_UNSUPPORTED") or claim_joint.evidence_status == "insufficient":
            joint_outcome = "SUCCESS: ABSTAINED -> UNKNOWN (Detection-to-Abstention Gap CLOSED by Schema v2!)"
        elif claim_joint.object == orig_obj:
            joint_outcome = "FAILED: UNCHANGED -> Shortcut Persisted despite Schema v2"
        else:
            joint_outcome = f"CHANGED -> {claim_joint.object}"
        print(f"  => Outcome:       {joint_outcome}", flush=True)

        # -------------------------------------------------------------
        # STEP 3: SEMANTIC MUTATION: f(R, A, B') WITH SCHEMA V2
        # -------------------------------------------------------------
        print("\n--- [Call 3] Semantic Mutation: f(R, A, B') with Schema v2 ---", flush=True)
        orig_fact_b_text = exposed_memories.get(fact_b_mid, "")
        if "Kira" in orig_fact_b_text:
            mutated_fact_b_text = orig_fact_b_text.replace("Kira", "Tal")
        elif "Jaxon" in orig_fact_b_text:
            mutated_fact_b_text = orig_fact_b_text.replace("Jaxon", "Kira")
        else:
            mutated_fact_b_text = orig_fact_b_text.replace("directly reports to ", "directly reports to Vance. ")

        # Constant Slot ID: keep slot ID identical while mutating text
        mutation_memories = []
        for m_id, text in exposed_memories.items():
            if m_id == fact_b_mid:
                mutation_memories.append(f"[{m_id}] {mutated_fact_b_text}")
            else:
                mutation_memories.append(f"[{m_id}] {text}")

        mutation_user_prompt = "Available Memories:\n" + "\n".join(mutation_memories) + "\n\n" + question_section

        spec_mutation = CallSpec(
            model_name=model_name,
            system_prompt=template_v2.system_prompt,
            user_prompt=mutation_user_prompt,
            temperature=0.0,
            seed=42,
            format=template_v2.format_schema,
        )

        t0 = time.perf_counter()
        res_mutation = client.chat(spec_mutation)
        lat_mutation = time.perf_counter() - t0

        claim_mutation = ClaimEvaluator.evaluate_response(
            raw_text=res_mutation.raw_response_text,
            parsed_json=res_mutation.parsed_json,
            oracle=oracle,
        )

        print(f"  Mutated Fact B:   '{orig_fact_b_text}' -> '{mutated_fact_b_text}' (slot ID constant)", flush=True)
        print(f"  Raw Output:       {res_mutation.raw_response_text.strip()}", flush=True)
        print(f"  Evidence Status:  {claim_mutation.evidence_status}", flush=True)
        print(f"  Derived Object:   {claim_mutation.object}", flush=True)
        print(f"  Reported Parents: {claim_mutation.reported_parent_ids}", flush=True)
        print(f"  Telemetry:        latency={lat_mutation:.2f}s | prompt_eval={res_mutation.prompt_eval_duration_ms:.1f}ms | eval={res_mutation.eval_duration_ms:.1f}ms", flush=True)

        if claim_mutation.object in ("UNKNOWN", "UNKNOWN_OR_UNSUPPORTED") or claim_mutation.evidence_status == "insufficient":
            mut_outcome = "SUCCESS: ABSTAINED -> UNKNOWN (Recognized antecedent mismatch in single-rule ecology!)"
        elif claim_mutation.object == orig_obj:
            mut_outcome = "FAILED: ANTECEDENT VIOLATION (Model forced rule conclusion despite mutated premise)"
        else:
            mut_outcome = f"MUTATED TO {claim_mutation.object}"
        print(f"  => Outcome:       {mut_outcome}", flush=True)

        # Persist v2 calls
        with db.conn:
            db.conn.execute("""
                INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f"{call_id}_v2_clean", run_id, 1, f"{task_id}_v2_clean", spec_clean.model_dump_json(), res_clean.raw_response_text, res_clean.prompt_tokens, res_clean.completion_tokens, lat_clean * 1000.0, res_clean.load_duration_ms, res_clean.prompt_eval_duration_ms, res_clean.eval_duration_ms, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

            db.conn.execute("""
                INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f"{call_id}_v2_joint_ko", run_id, 1, f"{task_id}_v2_joint_ko", spec_joint.model_dump_json(), res_joint.raw_response_text, res_joint.prompt_tokens, res_joint.completion_tokens, lat_joint * 1000.0, res_joint.load_duration_ms, res_joint.prompt_eval_duration_ms, res_joint.eval_duration_ms, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

            db.conn.execute("""
                INSERT INTO calls (call_id, run_id, generation, task_id, request_json, response_text, prompt_tokens, completion_tokens, latency_ms, load_duration_ms, prompt_eval_duration_ms, eval_duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f"{call_id}_v2_mutation", run_id, 1, f"{task_id}_v2_mutation", spec_mutation.model_dump_json(), res_mutation.raw_response_text, res_mutation.prompt_tokens, res_mutation.completion_tokens, lat_mutation * 1000.0, res_mutation.load_duration_ms, res_mutation.prompt_eval_duration_ms, res_mutation.eval_duration_ms, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))

        results_v2.append({
            "task_id": task_id,
            "target": orig_obj,
            "clean_obj": claim_clean.object,
            "clean_evidence": claim_clean.evidence_status,
            "joint_ko_obj": claim_joint.object,
            "joint_ko_evidence": claim_joint.evidence_status,
            "joint_outcome": joint_outcome,
            "mutation_obj": claim_mutation.object,
            "mutation_evidence": claim_mutation.evidence_status,
            "mut_outcome": mut_outcome,
        })

    print("\n" + "=" * 80, flush=True)
    print("           2x2 FACTORIAL COMPARISON: CELL 1 (D1-S/v1) vs CELL 2 (D1-S/v2)", flush=True)
    print("=" * 80, flush=True)
    for r in results_v2:
        print(f"Task: {r['task_id']}", flush=True)
        print(f"  - Target Object:             {r['target']}", flush=True)
        print(f"  - Clean Baseline (v2):       {r['clean_obj']} (status: {r['clean_evidence']})", flush=True)
        print(f"  - Joint Knockout f(R,¬A,¬B): {r['joint_ko_obj']} (status: {r['joint_ko_evidence']}) -> {r['joint_outcome']}", flush=True)
        print(f"  - Semantic Mutation f(R,A,B'): {r['mutation_obj']} (status: {r['mutation_evidence']}) -> {r['mut_outcome']}", flush=True)
    print("=" * 80, flush=True)
    print(f"Results recorded in DB: {source_db_path}", flush=True)
    print("=" * 80 + "\n", flush=True)

    db.close()


if __name__ == "__main__":
    db_file = "gene_d1_preflight_20260819_181409.db"
    model = "gemma3:12b"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        db_file = sys.argv[1]
    run_d1_s_v2(source_db_path=db_file, model_name=model)
