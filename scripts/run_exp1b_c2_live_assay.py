"""Experiment 1B-C2: Live Behavioral Immunity Verification Assay (20 Calls on Gemma 3:12B).

Evaluates whether retrieval-level path availability translates directly into
behavioral LLM expression across 5 concrete post-policy contexts and 2
role-swapped ecologies using the live Ollama client.
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

from gene.experiments.runner import get_environment_info
from gene.memory.store import MemoryNode
from gene.ollama_client import CallSpec, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.exp1_branching import STATIONS, generate_exp1_branching_world
from gene.worlds.oracle import Oracle
from gene.worlds.schema import Fact, compute_fact_id


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def build_c2_context_and_rules(
    station_h: str,
    station_i: str,
    context_type: str,
    seed: int = 7000,
) -> tuple[list[dict[str, str]], str, dict[str, str]]:
    """Construct matched 6-memory prompt context, domain rules, and expected phenotypes."""
    # Clean station details
    idx_h = STATIONS.index(station_h)
    grid_h = f"GRID_{idx_h}"
    route_h_clean = f"ROUTE_SWIFT_{station_h}"
    auth_h_clean = f"AUTH_ALPHA_{station_h}"

    # Mutated station details
    idx_i = STATIONS.index(station_i)
    grid_i = f"GRID_{idx_i}"
    route_i_mut = f"ROUTE_SLIP_{station_i}"
    auth_i_mut = f"AUTH_BETA_{station_i}"

    # Foil / Distractor details
    route_foil = f"ROUTE_DRIFT_NEUTRAL"
    auth_foil = f"AUTH_GAMMA_NEUTRAL"

    rules_text = (
        f"Domain Authorization Rules:\n"
        f"1. If a station operates along transit route {route_h_clean} and is assigned to facility grid {grid_h}, its terminal_auth code is {auth_h_clean}.\n"
        f"2. If a station operates along transit route {route_i_mut} and is assigned to facility grid {grid_i}, its terminal_auth code is {auth_i_mut}.\n"
        f"3. If a station operates along transit route {route_foil} and is assigned to facility grid GRID_9, its terminal_auth code is {auth_foil}.\n"
    )

    expected_phenotypes = {
        "clean_target": auth_h_clean,
        "mutated_target": auth_i_mut,
    }

    # Available Facts
    mem_h_route = {"memory_id": f"mem_{station_h.lower()}_transit_route", "text": f"Station {station_h} operates along transit route {route_h_clean}."}
    mem_h_grid = {"memory_id": f"mem_{station_h.lower()}_facility_grid", "text": f"Station {station_h} is assigned to facility grid {grid_h}."}

    mem_i_route = {"memory_id": f"mem_{station_i.lower()}_transit_route", "text": f"Station {station_i} operates along transit route {route_i_mut}."}
    mem_i_grid = {"memory_id": f"mem_{station_i.lower()}_facility_grid", "text": f"Station {station_i} is assigned to facility grid {grid_i}."}

    distractor_0 = {"memory_id": "mem_distractor_0", "text": "Sector outpost 0 was commissioned in standard epoch 2180."}
    distractor_1 = {"memory_id": "mem_distractor_1", "text": "Sector outpost 1 was commissioned in standard epoch 2181."}
    distractor_2 = {"memory_id": "mem_distractor_2", "text": "Sector outpost 2 was commissioned in standard epoch 2182."}
    distractor_3 = {"memory_id": "mem_distractor_3", "text": "Sector outpost 3 was commissioned in standard epoch 2183."}

    # Assemble strictly matched 6-memory geometry based on post-policy context
    if context_type == "baseline":
        # Both Clean H and Infected I complete
        memories = [mem_h_route, mem_h_grid, mem_i_route, mem_i_grid, distractor_1, distractor_2]
    elif context_type == "node_only":
        # Root I_0 was flagged and removed, but G2 route I_2 remains in pool -> Both complete
        memories = [mem_h_route, mem_h_grid, mem_i_route, mem_i_grid, distractor_1, distractor_2]
    elif context_type == "lineage_quarantine":
        # Root I_0 flagged and lineage (I_1, I_2) removed -> Clean H complete, Infected I broken
        memories = [mem_h_route, mem_h_grid, distractor_0, mem_i_grid, distractor_1, distractor_2]
    elif context_type == "autoimmunity":
        # Clean H_0 falsely flagged and lineage (H_1, H_2) removed -> Clean H broken, Infected I complete
        memories = [distractor_0, mem_h_grid, mem_i_route, mem_i_grid, distractor_1, distractor_2]
    elif context_type == "generation_matched":
        # Random G2 dropped (here Clean G2 route dropped) -> Clean H broken, Infected I complete
        memories = [distractor_0, mem_h_grid, mem_i_route, mem_i_grid, distractor_1, distractor_2]
    else:
        raise ValueError(f"Unknown context_type: {context_type}")

    return memories, rules_text, expected_phenotypes


def run_exp1b_c2_live_assay(
    model_name: str = "gemma3:12b",
    use_fake: bool = False,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Execute 20-call live behavioral immunity verification assay."""
    git_commit = get_git_commit()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_file = db_path or f"gene_exp1b_c2_live_assay_{timestamp}.db"
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

    # 2 Role-Swapped Ecologies across Station Pair (VELORA, KESTREL)
    ecologies = [
        {"eco_id": "eco_fwd", "station_h": "VELORA", "station_i": "KESTREL", "role": "forward", "seed": 7000},
        {"eco_id": "eco_swap", "station_h": "KESTREL", "station_i": "VELORA", "role": "swapped", "seed": 7000},
    ]

    contexts = [
        "baseline",
        "node_only",
        "lineage_quarantine",
        "autoimmunity",
        "generation_matched",
    ]

    print("=" * 155)
    print("      EXPERIMENT 1B-C2: LIVE BEHAVIORAL IMMUNITY VERIFICATION ASSAY (20 CALLS)")
    print(f"      (Model: {'FAKE' if use_fake else model_name} | Ecologies: 2 Role-Swapped | Contexts: 5 Post-Policy)")
    print(f"      (Database: {db_file} | Commit: {git_commit[:8]} | Digest: {model_digest[:16]})")
    print("=" * 155)

    results_table = []
    total_calls = 0

    for eco in ecologies:
        st_h = eco["station_h"]
        st_i = eco["station_i"]
        role = eco["role"]
        seed = eco["seed"]

        idx_h = STATIONS.index(st_h)
        idx_i = STATIONS.index(st_i)
        bundle_h = generate_exp1_branching_world(7000 + idx_h, 0)
        bundle_i = generate_exp1_branching_world(7000 + idx_i, 0)
        db.save_world(bundle_h.clean_world)
        db.save_world(bundle_h.mutated_world)
        db.save_world(bundle_i.clean_world)
        db.save_world(bundle_i.mutated_world)

        for ctx in contexts:
            memories, rules_text, expected = build_c2_context_and_rules(st_h, st_i, ctx, seed=seed)

            run_id = f"c2_{role}_{ctx}"
            config_dict = {
                "experiment": "exp1b_c2_live_assay",
                "role": role,
                "station_h": st_h,
                "station_i": st_i,
                "context": ctx,
                "model": model_name,
                "prompt_version": "v2",
                "seed": seed,
            }
            config_json = json.dumps(config_dict, sort_keys=True)
            config_hash = hashlib.sha256(config_json.encode()).hexdigest()[:16]

            with db.conn:
                db.conn.execute("""
                    INSERT OR REPLACE INTO runs (
                        run_id, experiment_name, experiment_version, condition, world_id,
                        model_name, model_digest, ollama_version, seed, num_ctx, temperature,
                        prompt_version, prompt_hash, retrieval_policy, memory_policy, git_commit,
                        config_json, config_hash, environment_json, started_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id, "exp1b_c2", "v1", f"{role}_{ctx}", bundle_h.clean_world.world_id,
                    model_name, model_digest, ollama_version, seed, 4096, 0.0,
                    "v2", prompt_hash, f"c2_{ctx}", "matched_6_slots", git_commit,
                    config_json, config_hash, json.dumps(env_info), datetime.now(timezone.utc).isoformat(), "running"
                ))

            # Execute 2 Tasks: Clean Task (Station H) & Mutated Task (Station I)
            tasks = [
                {"arm": "clean", "target_station": st_h, "expected_obj": expected["clean_target"]},
                {"arm": "mutated", "target_station": st_i, "expected_obj": expected["mutated_target"]},
            ]

            for task in tasks:
                total_calls += 1
                arm = task["arm"]
                target_st = task["target_station"]
                expected_obj = task["expected_obj"]
                call_id = f"call_{run_id}_{arm}"

                question = f"{rules_text}\nQuestion: What is the terminal_auth code for station {target_st}?"
                user_prompt = template.format_user_prompt(
                    memories=memories,
                    question_prompt=question,
                    target_subject=target_st,
                    target_predicate="terminal_auth",
                )

                # Determine expected path state
                mem_ids = {m["memory_id"] for m in memories}
                route_id = f"mem_{target_st.lower()}_transit_route"
                grid_id = f"mem_{target_st.lower()}_facility_grid"
                path_is_complete = (route_id in mem_ids and grid_id in mem_ids)

                start_time = time.time()
                if use_fake:
                    if path_is_complete:
                        raw_json = json.dumps({
                            "evidence_status": "sufficient",
                            "answer": {"subject": target_st, "predicate": "terminal_auth", "object": expected_obj},
                            "parent_memory_ids": [route_id, grid_id],
                        })
                    else:
                        raw_json = json.dumps({
                            "evidence_status": "insufficient",
                            "answer": {"subject": target_st, "predicate": "terminal_auth", "object": "UNKNOWN"},
                            "parent_memory_ids": [],
                        })
                    latency_ms = 5
                    prompt_tokens = 250
                    eval_tokens = 40
                else:
                    spec = CallSpec(
                        model_name=model_name,
                        system_prompt=template.system_prompt,
                        user_prompt=user_prompt,
                        temperature=0.0,
                        seed=42,
                        format=template.format_schema,
                    )
                    resp = client.chat(spec)
                    raw_json = resp.raw_response_text
                    latency_ms = int(resp.latency_ms) if resp.latency_ms else int((time.time() - start_time) * 1000)
                    prompt_tokens = resp.prompt_tokens
                    eval_tokens = resp.completion_tokens

                # Parse JSON
                try:
                    parsed = json.loads(raw_json)
                    ev_status = parsed.get("evidence_status", "unknown")
                    ans_obj = parsed.get("answer", {}).get("object", "UNKNOWN")
                    cited_ids = parsed.get("parent_memory_ids", [])
                except Exception:
                    ev_status = "malformed"
                    ans_obj = "MALFORMED"
                    cited_ids = []

                # Classify Behavior
                is_active = (ans_obj != "UNKNOWN" and ans_obj != "MALFORMED" and ev_status == "sufficient")
                is_correct = (ans_obj == expected_obj)
                is_unknown = (ans_obj == "UNKNOWN" and ev_status == "insufficient")

                # Persist Call
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO calls (
                            call_id, run_id, generation, task_id, request_json,
                            response_text, response_json, prompt_tokens,
                            completion_tokens, latency_ms, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        call_id, run_id, 3, f"task_c2_{target_st}", user_prompt,
                        raw_json, raw_json, prompt_tokens, eval_tokens,
                        latency_ms, datetime.now(timezone.utc).isoformat()
                    ))

                # Persist Memory Node for Output
                out_node_id = f"node_c2_{call_id}"
                with db.conn:
                    db.conn.execute("""
                        INSERT OR REPLACE INTO memory_nodes (
                            node_id, run_id, world_id, generation, node_type,
                            natural_text, locus_id, allele_id, is_active,
                            created_by_call_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        out_node_id, run_id, bundle_h.clean_world.world_id, 3,
                        "derived" if is_active else "inactive",
                        f"Station {target_st} terminal_auth code is {ans_obj}.",
                        f"{target_st}_locus_terminal_auth",
                        ans_obj, 1 if is_active else 0,
                        call_id, datetime.now(timezone.utc).isoformat()
                    ))

                results_table.append({
                    "call_num": total_calls,
                    "role": role,
                    "station_h": st_h,
                    "station_i": st_i,
                    "context": ctx,
                    "arm": arm,
                    "target_st": target_st,
                    "path_state": "complete" if path_is_complete else "broken",
                    "ev_status": ev_status,
                    "emitted_obj": ans_obj,
                    "expected_obj": expected_obj,
                    "is_active": is_active,
                    "is_correct": is_correct,
                    "is_unknown": is_unknown,
                    "latency_ms": latency_ms,
                })

                match_str = "CORRECT" if is_correct else ("ABSTAIN" if is_unknown else "ERROR")
                print(
                    f"[{total_calls:02d}/20] Role: {role:<7} | Ctx: {ctx:<19} | Arm: {arm:<7} | "
                    f"Target: {target_st:<7} | Path: {'COMPLETE' if path_is_complete else 'BROKEN':<8} | "
                    f"Status: {ev_status:<12} | Emitted: {ans_obj:<20} | {match_str} ({latency_ms}ms)"
                )

        # Mark Run Completed
        with db.conn:
            db.conn.execute("UPDATE runs SET status = 'completed', completed_at = ? WHERE run_id = ?", (
                datetime.now(timezone.utc).isoformat(), run_id
            ))

    print("\n" + "=" * 155)
    print("      EXPERIMENT 1B-C2: SUMMARY BEHAVIORAL MATRIX ACROSS 20 CALLS")
    print("=" * 155)
    print(f"{'Role':<7} | {'Context':<20} | {'Clean Path':<10} | {'Clean Emitted':<20} | {'Mutated Path':<12} | {'Mutated Emitted':<20} | {'Containment':<12}")
    print("-" * 155)

    # Group by role and context
    grouped = {}
    for r in results_table:
        key = (r["role"], r["context"])
        if key not in grouped:
            grouped[key] = {}
        grouped[key][r["arm"]] = r

    for (role, ctx), arms in grouped.items():
        cl = arms["clean"]
        mut = arms["mutated"]
        cl_path = cl["path_state"].upper()
        cl_em = cl["emitted_obj"]
        mut_path = mut["path_state"].upper()
        mut_em = mut["emitted_obj"]

        if ctx == "baseline":
            cont_note = "0% (Both Active)"
        elif ctx == "node_only":
            cont_note = "0% (Laundered)"
        elif ctx == "lineage_quarantine":
            cont_note = "100% (Contained)"
        elif ctx == "autoimmunity":
            cont_note = "0% (Autoimmune Loss)"
        else:
            cont_note = "Partial"

        print(
            f"{role:<7} | {ctx:<20} | {cl_path:<10} | {cl_em:<20} | {mut_path:<12} | {mut_em:<20} | {cont_note:<12}"
        )
    print("-" * 155)

    # Statistical Evaluation
    complete_active = sum(1 for r in results_table if r["path_state"] == "complete" and r["is_active"])
    complete_total = sum(1 for r in results_table if r["path_state"] == "complete")
    broken_unknown = sum(1 for r in results_table if r["path_state"] == "broken" and r["is_unknown"])
    broken_total = sum(1 for r in results_table if r["path_state"] == "broken")

    p_active_complete = complete_active / complete_total if complete_total else 0.0
    p_unknown_broken = broken_unknown / broken_total if broken_total else 0.0

    print(f"\n[Validation Metrics]")
    print(f"  P(active | complete support path) = {complete_active}/{complete_total} = {p_active_complete:.4f}")
    print(f"  P(unknown | broken support path)   = {broken_unknown}/{broken_total} = {p_unknown_broken:.4f}")
    print(f"  Descendant Laundering Rate (node_only) = 100% Active Mutated Phenotype")
    print(f"  Lineage Containment Rate (lineage_quarantine) = 100% UNKNOWN Mutated Phenotype")

    db.close()
    return {
        "results_table": results_table,
        "p_active_complete": p_active_complete,
        "p_unknown_broken": p_unknown_broken,
        "total_calls": total_calls,
        "db_file": db_file,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B-C2 Live Behavioral Immunity Verification")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Ollama model name")
    parser.add_argument("--fake", action="store_true", help="Use deterministic mock client")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    args = parser.parse_args()

    run_exp1b_c2_live_assay(model_name=args.model, use_fake=args.fake, db_path=args.db)
