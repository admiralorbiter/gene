"""Experiment 1B-C2b: Binding Disambiguation & Epistemic Proofreading Assay.

Systematically disambiguates the mechanism of pseudo-path formation by testing 5 conditions
across 2 ecologies (Forward: VELORA target; Swapped: KESTREL target) with 3 repetitions (30 Live Calls on Gemma 3:12B):
1. no_route (Zero routes in prompt)
2. foreign_station_wrong_route (Foreign station + neutral route)
3. target_station_wrong_route (Target station + neutral route)
4. foreign_station_target_route (Foreign station + target-required route)
5. valid_target_route (Positive control: Target station + target-required route)

Evaluates both Layer 1 (Memory Governance) and Layer 2 (Epistemic Proofreading / Structural Unification Filter).
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
from gene.worlds.exp1_branching import STATIONS
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.schema import Fact, Rule, Task, World, compute_fact_id


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def build_c2b_prompt_and_worlds(
    target_station: str,
    foreign_station: str,
    condition: str,
    seed: int = 7000,
) -> tuple[list[dict[str, str]], World, World, Task, dict[str, Any]]:
    """Build matched 6-slot prompt context and canonical/context worlds for binding assay."""
    idx_target = STATIONS.index(target_station)
    grid_target = f"GRID_{idx_target}"
    route_target_req = f"ROUTE_SWIFT_{target_station}"
    auth_target_req = f"AUTH_ALPHA_{target_station}"

    idx_foreign = STATIONS.index(foreign_station)
    grid_foreign = f"GRID_{idx_foreign}"
    route_foreign_clean = f"ROUTE_SWIFT_{foreign_station}"
    auth_foreign_clean = f"AUTH_ALPHA_{foreign_station}"

    route_neutral = "ROUTE_DRIFT_NEUTRAL"
    auth_neutral = "AUTH_GAMMA_NEUTRAL"

    # Base Canonical Facts in W*
    f_target_route_true = Fact(subject=target_station, predicate="transit_route", object=route_target_req)
    f_target_grid = Fact(subject=target_station, predicate="facility_grid", object=grid_target)
    f_foreign_route_true = Fact(subject=foreign_station, predicate="transit_route", object=route_foreign_clean)
    f_foreign_grid = Fact(subject=foreign_station, predicate="facility_grid", object=grid_foreign)

    # Distractor Facts
    dist_0 = Fact(subject="OUTPOST_0", predicate="commissioned_epoch", object="2180")
    dist_1 = Fact(subject="OUTPOST_1", predicate="commissioned_epoch", object="2181")
    dist_2 = Fact(subject="OUTPOST_2", predicate="commissioned_epoch", object="2182")
    dist_3 = Fact(subject="OUTPOST_3", predicate="commissioned_epoch", object="2183")

    # Domain Authorization Rules
    r_target = Rule(rule_id=f"rule_auth_{target_station.lower()}", antecedents=[("?s", "transit_route", route_target_req), ("?s", "facility_grid", grid_target)], consequent=("?s", "terminal_auth", auth_target_req), depth=3)
    r_foreign = Rule(rule_id=f"rule_auth_{foreign_station.lower()}", antecedents=[("?s", "transit_route", route_foreign_clean), ("?s", "facility_grid", grid_foreign)], consequent=("?s", "terminal_auth", auth_foreign_clean), depth=3)
    r_neutral = Rule(rule_id="rule_auth_neutral", antecedents=[("?s", "transit_route", route_neutral), ("?s", "facility_grid", "GRID_9")], consequent=("?s", "terminal_auth", auth_neutral), depth=3)
    rules = [r_target, r_foreign, r_neutral]

    rules_text = (
        f"Domain Authorization Rules:\n"
        f"1. If a station operates along transit route {route_target_req} and is assigned to facility grid {grid_target}, its terminal_auth code is {auth_target_req}.\n"
        f"2. If a station operates along transit route {route_foreign_clean} and is assigned to facility grid {grid_foreign}, its terminal_auth code is {auth_foreign_clean}.\n"
        f"3. If a station operates along transit route {route_neutral} and is assigned to facility grid GRID_9, its terminal_auth code is {auth_neutral}.\n"
    )

    canonical_world = World(
        world_id=f"canonical_{target_station}_{foreign_station}",
        world_seed=seed,
        world_version="v2",
        facts=[f_target_route_true, f_target_grid, f_foreign_route_true, f_foreign_grid, dist_0, dist_1, dist_2, dist_3],
        rules=rules,
    )

    task = Task(
        task_id=f"task_auth_{target_station.lower()}",
        world_id=canonical_world.world_id,
        query_type="rule_inference",
        target_fact=Fact(subject=target_station, predicate="terminal_auth", object=auth_target_req),
        reasoning_depth=3,
        prompt=f"{rules_text}\nQuestion: What is the terminal_auth code for station {target_station}?",
        expected_answer=auth_target_req,
    )

    # Memories
    mem_target_grid = {"memory_id": f"mem_{target_station.lower()}_facility_grid", "text": f"Station {target_station} is assigned to facility grid {grid_target}."}
    mem_foreign_grid = {"memory_id": f"mem_{foreign_station.lower()}_facility_grid", "text": f"Station {foreign_station} is assigned to facility grid {grid_foreign}."}
    m_dist_0 = {"memory_id": "mem_distractor_0", "text": "Sector outpost 0 was commissioned in standard epoch 2180."}
    m_dist_1 = {"memory_id": "mem_distractor_1", "text": "Sector outpost 1 was commissioned in standard epoch 2181."}
    m_dist_2 = {"memory_id": "mem_distractor_2", "text": "Sector outpost 2 was commissioned in standard epoch 2182."}
    m_dist_3 = {"memory_id": "mem_distractor_3", "text": "Sector outpost 3 was commissioned in standard epoch 2183."}

    # Factorial Route Condition Slot
    if condition == "no_route":
        # Slot 0 = dist_0, Slot 2 = dist_3 (zero routes)
        memories = [m_dist_0, mem_target_grid, m_dist_3, mem_foreign_grid, m_dist_1, m_dist_2]
        ctx_facts = [dist_0, f_target_grid, dist_3, f_foreign_grid, dist_1, dist_2]
        path_is_supported = False
    elif condition == "foreign_station_wrong_route":
        # Foreign station with neutral route
        mem_f_wrong = {"memory_id": f"mem_{foreign_station.lower()}_transit_route", "text": f"Station {foreign_station} operates along transit route {route_neutral}."}
        f_f_wrong = Fact(subject=foreign_station, predicate="transit_route", object=route_neutral)
        memories = [m_dist_0, mem_target_grid, mem_f_wrong, mem_foreign_grid, m_dist_1, m_dist_2]
        ctx_facts = [dist_0, f_target_grid, f_f_wrong, f_foreign_grid, dist_1, dist_2]
        path_is_supported = False
    elif condition == "target_station_wrong_route":
        # Target station with neutral route
        mem_t_wrong = {"memory_id": f"mem_{target_station.lower()}_transit_route", "text": f"Station {target_station} operates along transit route {route_neutral}."}
        f_t_wrong = Fact(subject=target_station, predicate="transit_route", object=route_neutral)
        memories = [mem_t_wrong, mem_target_grid, m_dist_3, mem_foreign_grid, m_dist_1, m_dist_2]
        ctx_facts = [f_t_wrong, f_target_grid, dist_3, f_foreign_grid, dist_1, dist_2]
        path_is_supported = False
    elif condition == "foreign_station_target_route":
        # Foreign station with target station's required route!
        mem_f_req = {"memory_id": f"mem_{foreign_station.lower()}_transit_route", "text": f"Station {foreign_station} operates along transit route {route_target_req}."}
        f_f_req = Fact(subject=foreign_station, predicate="transit_route", object=route_target_req)
        memories = [m_dist_0, mem_target_grid, mem_f_req, mem_foreign_grid, m_dist_1, m_dist_2]
        ctx_facts = [dist_0, f_target_grid, f_f_req, f_foreign_grid, dist_1, dist_2]
        path_is_supported = False
    elif condition == "valid_target_route":
        # Positive control: Target station with valid required route
        mem_t_req = {"memory_id": f"mem_{target_station.lower()}_transit_route", "text": f"Station {target_station} operates along transit route {route_target_req}."}
        memories = [mem_t_req, mem_target_grid, m_dist_3, mem_foreign_grid, m_dist_1, m_dist_2]
        ctx_facts = [f_target_route_true, f_target_grid, dist_3, f_foreign_grid, dist_1, dist_2]
        path_is_supported = True
    else:
        raise ValueError(f"Unknown condition: {condition}")

    context_world = World(
        world_id=f"ctx_{target_station}_{foreign_station}_{condition}",
        world_seed=seed,
        world_version="v2",
        facts=ctx_facts,
        rules=rules,
    )

    return memories, canonical_world, context_world, task, {
        "path_is_supported": path_is_supported,
        "target_station": target_station,
        "foreign_station": foreign_station,
        "expected_auth": auth_target_req,
        "rules_text": rules_text,
    }


def evaluate_epistemic_proofreading(
    parsed_json: dict[str, Any] | None,
    memories: list[dict[str, str]],
    target_station: str,
    expected_auth: str,
    rules: list[Rule],
) -> dict[str, Any]:
    """Layer 2 Epistemic Proofreader: Mechanically verify structural unification of cited evidence."""
    if not parsed_json or not isinstance(parsed_json, dict):
        return {"proofreader_verdict": "REJECT_MALFORMED", "is_proofread_admitted": False, "reason": "Malformed JSON"}

    raw_ev = str(parsed_json.get("evidence_status", "insufficient")).strip().lower()
    ans = parsed_json.get("answer", {})
    if not isinstance(ans, dict):
        return {"proofreader_verdict": "REJECT_MALFORMED", "is_proofread_admitted": False, "reason": "Malformed answer block"}

    obj = str(ans.get("object", "UNKNOWN")).strip().upper()
    cited_ids = parsed_json.get("parent_memory_ids", [])

    if obj in ("UNKNOWN", "NONE", "", "UNKNOWN_OR_UNSUPPORTED") or obj.startswith("UNKNOWN"):
        if raw_ev in ("insufficient", "conflicting"):
            if cited_ids:
                return {"proofreader_verdict": "REJECT_CONTRACT_FAILURE", "is_proofread_admitted": False, "reason": "Abstention object UNKNOWN emitted with non-empty parent_memory_ids"}
            return {"proofreader_verdict": "PASS_ABSTENTION", "is_proofread_admitted": False, "reason": "Clean contract-consistent abstention"}
        else:
            return {"proofreader_verdict": "REJECT_CONTRACT_FAILURE", "is_proofread_admitted": False, "reason": f"Abstention object UNKNOWN emitted with contradictory evidence_status '{raw_ev}'"}

    # Find the rule corresponding to emitted auth code
    target_rule = None
    for r in rules:
        if r.consequent[2].upper() == obj:
            target_rule = r
            break

    if not target_rule:
        return {"proofreader_verdict": "REJECT_UNKNOWN_RULE", "is_proofread_admitted": False, "reason": f"No rule for consequent {obj}"}

    # Extract text of cited memories
    mem_lookup = {m["memory_id"]: m["text"] for m in memories}
    cited_texts = [mem_lookup.get(cid, "") for cid in cited_ids if cid in mem_lookup]

    # Verify unification: Check if cited memories instantiate all rule antecedents for target_station
    # Rule antecedent 0: transit_route
    req_route = target_rule.antecedents[0][2]
    # Rule antecedent 1: facility_grid
    req_grid = target_rule.antecedents[1][2]

    has_route_match = any((f"Station {target_station}" in txt and req_route in txt) for txt in cited_texts)
    has_grid_match = any((f"Station {target_station}" in txt and req_grid in txt) for txt in cited_texts)

    if has_route_match and has_grid_match:
        return {"proofreader_verdict": "PASS_VALID_DERIVATION", "is_proofread_admitted": True, "reason": "All antecedents structurally unified"}
    else:
        reasons = []
        if not has_route_match:
            reasons.append(f"Missing valid route '{req_route}' for {target_station}")
        if not has_grid_match:
            reasons.append(f"Missing valid grid '{req_grid}' for {target_station}")
        return {
            "proofreader_verdict": "REJECT_UNIFICATION_FAILURE",
            "is_proofread_admitted": False,
            "reason": "; ".join(reasons),
        }


def run_exp1b_c2b_assay(
    model_name: str = "gemma3:12b",
    use_fake: bool = False,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Run Experiment 1B-C2b Binding Disambiguation Assay (30 Calls)."""
    git_commit = get_git_commit()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_file = db_path or f"gene_exp1b_c2b_binding_assay_{timestamp}.db"
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
        {"role": "swapped", "target": "KESTREL", "foreign": "VELORA"},
        {"role": "forward", "target": "VELORA", "foreign": "KESTREL"},
    ]

    conditions = [
        "no_route",
        "foreign_station_wrong_route",
        "target_station_wrong_route",
        "foreign_station_target_route",
        "valid_target_route",
    ]

    # Create table for binding assay results
    with db.conn:
        db.conn.execute("""
            CREATE TABLE IF NOT EXISTS binding_assay_results (
                result_id TEXT PRIMARY KEY,
                call_id TEXT NOT NULL,
                role TEXT NOT NULL,
                target_station TEXT NOT NULL,
                foreign_station TEXT NOT NULL,
                condition TEXT NOT NULL,
                repetition INTEGER NOT NULL,
                prompt_hash TEXT NOT NULL,
                path_supported INTEGER NOT NULL,
                emitted_object TEXT NOT NULL,
                evidence_status TEXT NOT NULL,
                cited_memory_ids_json TEXT NOT NULL,
                reproductive_status TEXT NOT NULL,
                epistemic_phenotype TEXT NOT NULL,
                state_vector_json TEXT NOT NULL,
                proofreader_verdict TEXT NOT NULL,
                is_proofread_admitted INTEGER NOT NULL,
                proofreader_reason TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

    print("=" * 155)
    print("      EXPERIMENT 1B-C2b: BINDING DISAMBIGUATION & EPISTEMIC PROOFREADING ASSAY (30 CALLS)")
    print(f"      (Model: {'FAKE' if use_fake else model_name} | Commit: {git_commit[:8]} | DB: {db_file})")
    print("=" * 155)

    all_results = []
    total_calls = 0

    for eco in ecologies:
        role = eco["role"]
        target_st = eco["target"]
        foreign_st = eco["foreign"]

        for cond in conditions:
            run_id = f"c2b_{role}_{cond}"
            memories, can_w, ctx_w, task, meta = build_c2b_prompt_and_worlds(target_st, foreign_st, cond, seed=7000)
            db.save_world(can_w)
            db.save_world(ctx_w)

            cfg_dict = {"experiment": "exp1b_c2b", "role": role, "target": target_st, "foreign": foreign_st, "condition": cond, "model": model_name}
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
                    run_id, "exp1b_c2b", "v1", f"{role}_{cond}", can_w.world_id,
                    model_name, model_digest, ollama_version, 7000, 4096, 0.0,
                    "v2", prompt_hash, cond, "matched_6_slots", git_commit,
                    cfg_json, cfg_hash, json.dumps(env_info), datetime.now(timezone.utc).isoformat(), "running"
                ))

            for rep in range(3):
                total_calls += 1
                call_id = f"call_{run_id}_rep{rep:02d}"

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
                req_payload = json.dumps(spec.to_request_payload())
                p_hash = hashlib.sha256(req_payload.encode()).hexdigest()[:12]

                start_time = time.time()
                if use_fake:
                    if cond == "valid_target_route":
                        raw_json = json.dumps({
                            "evidence_status": "sufficient",
                            "answer": {"subject": target_st, "predicate": "terminal_auth", "object": meta["expected_auth"]},
                            "parent_memory_ids": [f"mem_{target_st.lower()}_transit_route", f"mem_{target_st.lower()}_facility_grid"],
                        })
                    else:
                        raw_json = json.dumps({
                            "evidence_status": "insufficient",
                            "answer": {"subject": target_st, "predicate": "terminal_auth", "object": "UNKNOWN"},
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

                try:
                    parsed = json.loads(raw_json)
                except Exception:
                    parsed = None

                raw_obj = "UNKNOWN"
                raw_ev = "insufficient"
                cited_ids = []
                if parsed and isinstance(parsed, dict):
                    raw_ev = str(parsed.get("evidence_status", "insufficient")).strip().lower()
                    ans = parsed.get("answer", {})
                    if isinstance(ans, dict):
                        raw_obj = str(ans.get("object", "UNKNOWN")).strip().upper()
                    cited_ids = parsed.get("parent_memory_ids", [])

                norm_obj = "UNKNOWN" if raw_obj in ("UNKNOWN", "NONE", "", "UNKNOWN_OR_UNSUPPORTED") else raw_obj
                is_unknown = (norm_obj == "UNKNOWN")
                repro_status = "active" if (not is_unknown and raw_ev == "sufficient") else "inactive"

                # DualOracle evaluation
                can_oracle = Oracle(can_w)
                t_star_res = can_oracle.evaluate_triple(target_st, "terminal_auth", norm_obj)
                canonical_truth = 1 if (is_unknown and t_star_res in (TruthStatus.UNSUPPORTED, TruthStatus.FALSE)) or (not is_unknown and t_star_res == TruthStatus.TRUE) else 0

                ctx_oracle = Oracle(ctx_w)
                ctx_res = ctx_oracle.evaluate_triple(target_st, "terminal_auth", norm_obj)
                context_derivability = 1 if ctx_res == TruthStatus.TRUE else 0

                if context_derivability == 1:
                    A_correct = 1 if not is_unknown and ctx_res == TruthStatus.TRUE else 0
                    E_correct = 1 if raw_ev == "sufficient" else 0
                else:
                    A_correct = 1 if is_unknown else 0
                    E_correct = 1 if raw_ev in ("insufficient", "conflicting") else 0

                K_consistent = 1 if (raw_ev == "sufficient" and not is_unknown) or (raw_ev in ("insufficient", "conflicting") and is_unknown) else 0
                state_vec = (canonical_truth, context_derivability, A_correct, E_correct, K_consistent)

                if is_unknown:
                    phenotype = "clean_abstention" if (E_correct == 1 and K_consistent == 1) else "contract_failure"
                else:
                    if context_derivability == 1:
                        phenotype = "healthy" if canonical_truth == 1 else "semantic"
                    else:
                        phenotype = "epistemic" if canonical_truth == 1 else "de_novo_error"

                # Layer 2: Epistemic Proofreader
                proofreader_eval = evaluate_epistemic_proofreading(parsed, memories, target_st, meta["expected_auth"], can_w.rules)

                # Persist Call
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO calls (
                            call_id, run_id, generation, task_id, request_json,
                            response_text, response_json, prompt_tokens,
                            completion_tokens, latency_ms, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        call_id, run_id, 3, task.task_id, req_payload,
                        raw_json, raw_json, prompt_tokens, eval_tokens,
                        latency_ms, datetime.now(timezone.utc).isoformat()
                    ))

                # Persist Binding Assay Result
                result_id = f"res_{call_id}"
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO binding_assay_results (
                            result_id, call_id, role, target_station, foreign_station,
                            condition, repetition, prompt_hash, path_supported,
                            emitted_object, evidence_status, cited_memory_ids_json,
                            reproductive_status, epistemic_phenotype, state_vector_json,
                            proofreader_verdict, is_proofread_admitted, proofreader_reason,
                            latency_ms, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        result_id, call_id, role, target_st, foreign_st,
                        cond, rep, p_hash, 1 if meta["path_is_supported"] else 0,
                        norm_obj, raw_ev, json.dumps(cited_ids),
                        repro_status, phenotype, json.dumps(state_vec),
                        proofreader_eval["proofreader_verdict"],
                        1 if proofreader_eval["is_proofread_admitted"] else 0,
                        proofreader_eval["reason"], latency_ms,
                        datetime.now(timezone.utc).isoformat()
                    ))

                call_res = {
                    "call_id": call_id,
                    "role": role,
                    "target_station": target_st,
                    "foreign_station": foreign_st,
                    "condition": cond,
                    "repetition": rep,
                    "prompt_hash": p_hash,
                    "path_supported": meta["path_is_supported"],
                    "emitted_object": norm_obj,
                    "evidence_status": raw_ev,
                    "reproductive_status": repro_status,
                    "epistemic_phenotype": phenotype,
                    "state_vector": state_vec,
                    "proofreader_verdict": proofreader_eval["proofreader_verdict"],
                    "is_proofread_admitted": proofreader_eval["is_proofread_admitted"],
                    "latency_ms": latency_ms,
                }
                all_results.append(call_res)

                print(
                    f"[{total_calls:02d}/30] Role: {role:<7} | Cond: {cond:<28} | Rep: {rep:02d}/03 | "
                    f"Target: {target_st:<7} | Pheno: {phenotype:<16} | Proofreader: {proofreader_eval['proofreader_verdict']:<25} | "
                    f"Emitted: {norm_obj:<20} ({int(latency_ms)}ms)"
                )

            with db.conn:
                db.conn.execute("UPDATE runs SET status = 'completed', completed_at = ? WHERE run_id = ?", (
                    datetime.now(timezone.utc).isoformat(), run_id
                ))

    db.close()
    return {
        "all_results": all_results,
        "total_calls": total_calls,
        "db_file": db_file,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B-C2b Binding Disambiguation Assay")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Ollama model name")
    parser.add_argument("--fake", action="store_true", help="Use deterministic mock client")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_exp1b_c2b_assay(model_name=args.model, use_fake=args.fake, db_path=args.db)
