"""Offline Re-scoring and Decoupled Phenotype Evaluator for Experiment 1B-C2a.

Re-scores all 50 live calls from gene_exp1b_c2a_live_assay_a1474d6.db against:
1. True Canonical World W* where both Station H and Station I have clean SWIFT routes -> AUTH_ALPHA (T*=0 for AUTH_BETA).
2. Decoupled State Ontology: separating Reproductive Status (active vs inactive) from Epistemic Phenotype (healthy, semantic, epistemic, contract_failure, clean_abstention).
3. Exact prompt_hash equivalence class grouping and empirical replay frequency extraction.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.worlds.exp1_branching import STATIONS
from gene.worlds.schema import Fact, Rule, Task, World
from gene.worlds.oracle import Oracle, TruthStatus


def build_true_canonical_and_context_worlds(
    station_h: str,
    station_i: str,
    context_type: str,
    competing_route_override: bool = True,
    seed: int = 7000,
) -> tuple[World, World, list[Task]]:
    """Build canonical world W* where ALL stations are clean, and context world."""
    idx_h = STATIONS.index(station_h)
    grid_h = f"GRID_{idx_h}"
    route_h_clean = f"ROUTE_SWIFT_{station_h}"
    auth_h_clean = f"AUTH_ALPHA_{station_h}"

    idx_i = STATIONS.index(station_i)
    grid_i = f"GRID_{idx_i}"
    route_i_clean = f"ROUTE_SWIFT_{station_i}" # True canonical route for station I
    auth_i_clean = f"AUTH_ALPHA_{station_i}"   # True canonical auth for station I
    route_i_mut = f"ROUTE_SLIP_{station_i}"    # Mutated route
    auth_i_mut = f"AUTH_BETA_{station_i}"

    route_foil = "ROUTE_DRIFT_NEUTRAL"
    auth_foil = "AUTH_GAMMA_NEUTRAL"

    # Canonical Facts in W* (Both Clean!)
    f_h_route_clean = Fact(subject=station_h, predicate="transit_route", object=route_h_clean)
    f_h_grid = Fact(subject=station_h, predicate="facility_grid", object=grid_h)
    f_i_route_clean = Fact(subject=station_i, predicate="transit_route", object=route_i_clean)
    f_i_grid = Fact(subject=station_i, predicate="facility_grid", object=grid_i)

    # Mutated fact (present in context world if unquarantined)
    f_i_route_mut = Fact(subject=station_i, predicate="transit_route", object=route_i_mut)

    # Distractor Facts
    dist_0 = Fact(subject="OUTPOST_0", predicate="commissioned_epoch", object="2180")
    dist_1 = Fact(subject="OUTPOST_1", predicate="commissioned_epoch", object="2181")
    dist_2 = Fact(subject="OUTPOST_2", predicate="commissioned_epoch", object="2182")
    dist_3 = Fact(subject="OUTPOST_3", predicate="commissioned_epoch", object="2183")

    # Domain Rules
    r_h = Rule(rule_id=f"rule_auth_{station_h.lower()}", antecedents=[("?s", "transit_route", route_h_clean), ("?s", "facility_grid", grid_h)], consequent=("?s", "terminal_auth", auth_h_clean), depth=3)
    r_i = Rule(rule_id=f"rule_auth_{station_i.lower()}", antecedents=[("?s", "transit_route", route_i_mut), ("?s", "facility_grid", grid_i)], consequent=("?s", "terminal_auth", auth_i_mut), depth=3)
    r_foil = Rule(rule_id="rule_auth_neutral", antecedents=[("?s", "transit_route", route_foil), ("?s", "facility_grid", "GRID_9")], consequent=("?s", "terminal_auth", auth_foil), depth=3)
    rules = [r_h, r_i, r_foil]

    canonical_world = World(
        world_id=f"canonical_true_{station_h}_{station_i}",
        world_seed=seed,
        world_version="v2",
        facts=[f_h_route_clean, f_h_grid, f_i_route_clean, f_i_grid, dist_0, dist_1, dist_2, dist_3],
        rules=rules,
    )

    t_clean = Task(
        task_id=f"task_auth_{station_h.lower()}",
        world_id=canonical_world.world_id,
        query_type="rule_inference",
        target_fact=Fact(subject=station_h, predicate="terminal_auth", object=auth_h_clean),
        reasoning_depth=3,
        prompt=f"Question: What is the terminal_auth code for station {station_h}?",
        expected_answer=auth_h_clean,
    )
    t_mutated = Task(
        task_id=f"task_auth_{station_i.lower()}",
        world_id=canonical_world.world_id,
        query_type="rule_inference",
        target_fact=Fact(subject=station_i, predicate="terminal_auth", object=auth_i_mut),
        reasoning_depth=3,
        prompt=f"Question: What is the terminal_auth code for station {station_i}?",
        expected_answer=auth_i_mut,
    )

    # Context facts based on policy
    if context_type in ("baseline", "node_only"):
        ctx_facts = [f_h_route_clean, f_h_grid, f_i_route_mut, f_i_grid, dist_1, dist_2]
    elif context_type == "lineage_quarantine":
        ctx_facts = [f_h_route_clean, f_h_grid, dist_0, f_i_grid, dist_1, dist_2]
    elif context_type in ("autoimmunity", "generation_matched"):
        i_route_fact = f_i_route_mut if competing_route_override else dist_3
        ctx_facts = [dist_0, f_h_grid, i_route_fact, f_i_grid, dist_1, dist_2]
    elif context_type == "double_quarantine":
        ctx_facts = [dist_0, f_h_grid, dist_3, f_i_grid, dist_1, dist_2]
    else:
        ctx_facts = [dist_0, dist_1, dist_2, dist_3]

    context_world = World(
        world_id=f"ctx_{station_h}_{station_i}_{context_type}",
        world_seed=seed,
        world_version="v2",
        facts=ctx_facts,
        rules=rules,
    )

    return canonical_world, context_world, [t_clean, t_mutated]


def classify_decoupled_phenotype(
    raw_json_str: str,
    task: Task,
    canonical_world: World,
    context_world: World,
    is_infected_arm: bool = False,
) -> dict[str, Any]:
    """Evaluate response with decoupled reproductive status and epistemic phenotype."""
    try:
        parsed = json.loads(raw_json_str)
    except Exception:
        parsed = None

    raw_ev = "insufficient"
    raw_obj = "UNKNOWN"
    if parsed and isinstance(parsed, dict):
        raw_ev = str(parsed.get("evidence_status", "insufficient")).strip().lower()
        ans_block = parsed.get("answer")
        if isinstance(ans_block, dict):
            raw_obj_val = ans_block.get("object")
            if raw_obj_val is not None:
                raw_obj = str(raw_obj_val).strip().upper().replace(" ", "_")

    if raw_obj in ("UNKNOWN", "NONE", "", "UNKNOWN_OR_UNSUPPORTED") or raw_obj.startswith("UNKNOWN"):
        norm_obj = "UNKNOWN"
        is_unknown = True
    else:
        norm_obj = raw_obj
        is_unknown = False

    is_claim_active = (not is_unknown and raw_ev == "sufficient")
    reproductive_status = "active" if is_claim_active else "inactive"

    # Evaluate against Canonical Oracle W* (T*)
    can_oracle = Oracle(canonical_world)
    t_star_res = can_oracle.evaluate_triple(task.target_fact.subject, task.target_fact.predicate, norm_obj)
    if is_unknown:
        canonical_truth = 1 if t_star_res in (TruthStatus.UNSUPPORTED, TruthStatus.FALSE) else 0
    else:
        canonical_truth = 1 if t_star_res == TruthStatus.TRUE else 0

    # Evaluate against Context Oracle W_ctx (D_ctx)
    ctx_oracle = Oracle(context_world)
    ctx_res = ctx_oracle.evaluate_triple(task.target_fact.subject, task.target_fact.predicate, norm_obj)
    context_derivability = 1 if ctx_res == TruthStatus.TRUE else 0

    # 3 Diagnostic Metrics
    if context_derivability == 1:
        A_correct = 1 if not is_unknown and ctx_res == TruthStatus.TRUE else 0
        E_correct = 1 if raw_ev == "sufficient" else 0
    else:
        A_correct = 1 if is_unknown else 0
        E_correct = 1 if raw_ev in ("insufficient", "conflicting") else 0

    if raw_ev == "sufficient":
        K_consistent = 1 if not is_unknown else 0
    elif raw_ev in ("insufficient", "conflicting"):
        K_consistent = 1 if is_unknown else 0
    else:
        K_consistent = 0

    state_vector = (canonical_truth, context_derivability, A_correct, E_correct, K_consistent)

    # Decoupled Epistemic Phenotype Classification
    if is_unknown:
        if E_correct == 1 and K_consistent == 1:
            epistemic_phenotype = "clean_abstention"
        else:
            epistemic_phenotype = "contract_failure"
    else:
        if context_derivability == 1:
            if canonical_truth == 1:
                epistemic_phenotype = "healthy"
            else:
                epistemic_phenotype = "semantic"
        else:
            if canonical_truth == 1:
                epistemic_phenotype = "epistemic" # Locally underivable but happens to match W*
            else:
                epistemic_phenotype = "de_novo_error"

    return {
        "raw_evidence_status": raw_ev,
        "normalized_object": norm_obj,
        "reproductive_status": reproductive_status,
        "canonical_truth": canonical_truth,
        "canonical_truth_status": t_star_res.value,
        "context_derivability": context_derivability,
        "context_truth_status": ctx_res.value,
        "A_correct": A_correct,
        "E_correct": E_correct,
        "K_consistent": K_consistent,
        "state_vector": state_vector,
        "epistemic_phenotype": epistemic_phenotype,
    }


def rescore_c2a_database(db_path: str = "gene_exp1b_c2a_live_assay_a1474d6.db"):
    """Re-score existing C2a database with corrected canonical world and decoupled ontology."""
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create dual_oracle_evaluations_v2 table
    c.execute("""
        CREATE TABLE IF NOT EXISTS dual_oracle_evaluations_v2 (
            evaluation_id TEXT PRIMARY KEY,
            call_id TEXT NOT NULL,
            prompt_hash TEXT NOT NULL,
            run_id TEXT NOT NULL,
            generation INTEGER NOT NULL,
            task_id TEXT NOT NULL,
            target_subject TEXT NOT NULL,
            target_predicate TEXT NOT NULL,
            derived_object TEXT,
            reproductive_status TEXT NOT NULL,
            canonical_truth_status TEXT NOT NULL,
            local_derivability_status TEXT NOT NULL,
            A_correct INTEGER NOT NULL,
            E_correct INTEGER NOT NULL,
            K_consistent INTEGER NOT NULL,
            state_vector_json TEXT NOT NULL,
            epistemic_phenotype TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(call_id) REFERENCES calls(call_id)
        )
    """)

    # Query all calls and run metadata
    query = """
        SELECT c.call_id, c.run_id, c.task_id, c.request_json, c.response_text,
               r.condition, r.config_json
        FROM calls c
        JOIN runs r ON c.run_id = r.run_id
        ORDER BY c.rowid
    """
    rows = c.execute(query).fetchall()
    print(f"Loaded {len(rows)} calls from {db_path}.")

    rescored_records = []
    by_prompt_hash: dict[str, list[dict[str, Any]]] = {}

    for call_id, run_id, task_id, req_json, resp_text, cond, cfg_json in rows:
        cfg = json.loads(cfg_json) if cfg_json else {}
        prompt_hash = hashlib.sha256(req_json.encode()).hexdigest()[:12]

        role = cfg.get("role", "forward")
        ctx_type = cfg.get("context", "baseline")
        panel = cfg.get("panel", "discrete_4state")

        if panel == "factorial_binding":
            st_h, st_i = "KESTREL", "VELORA"
            foreign_route_present = cfg.get("foreign_present", True)
            can_w, ctx_w, tasks = build_true_canonical_and_context_worlds(
                st_h, st_i, "autoimmunity", competing_route_override=foreign_route_present
            )
            target_task = tasks[0]
            is_infected_arm = False
        elif panel == "replay_stability":
            if "swapped" in role:
                st_h, st_i = "KESTREL", "VELORA"
            else:
                st_h, st_i = "VELORA", "KESTREL"
            can_w, ctx_w, tasks = build_true_canonical_and_context_worlds(st_h, st_i, "autoimmunity")
            target_task = tasks[0]
            is_infected_arm = False
        else:
            # Discrete panel
            if role == "swapped":
                st_h, st_i = "KESTREL", "VELORA"
            else:
                st_h, st_i = "VELORA", "KESTREL"
            can_w, ctx_w, tasks = build_true_canonical_and_context_worlds(st_h, st_i, ctx_type)
            if "clean" in call_id or st_h.lower() in task_id.lower():
                target_task = tasks[0]
                is_infected_arm = False
            else:
                target_task = tasks[1]
                is_infected_arm = True

        eval_data = classify_decoupled_phenotype(
            raw_json_str=resp_text,
            task=target_task,
            canonical_world=can_w,
            context_world=ctx_w,
            is_infected_arm=is_infected_arm,
        )
        eval_data["call_id"] = call_id
        eval_data["run_id"] = run_id
        eval_data["prompt_hash"] = prompt_hash
        eval_data["task_id"] = target_task.task_id
        eval_data["target_subject"] = target_task.target_fact.subject
        eval_data["target_predicate"] = target_task.target_fact.predicate
        rescored_records.append(eval_data)

        by_prompt_hash.setdefault(prompt_hash, []).append(eval_data)

        # Insert into v2 table
        c.execute("""
            INSERT OR REPLACE INTO dual_oracle_evaluations_v2 (
                evaluation_id, call_id, prompt_hash, run_id, generation,
                task_id, target_subject, target_predicate, derived_object,
                reproductive_status, canonical_truth_status, local_derivability_status,
                A_correct, E_correct, K_consistent, state_vector_json,
                epistemic_phenotype, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            f"eval_v2_{call_id}", call_id, prompt_hash, run_id, 3,
            target_task.task_id, target_task.target_fact.subject,
            target_task.target_fact.predicate, eval_data["normalized_object"],
            eval_data["reproductive_status"], eval_data["canonical_truth_status"],
            eval_data["context_truth_status"], eval_data["A_correct"],
            eval_data["E_correct"], eval_data["K_consistent"],
            json.dumps(eval_data["state_vector"]), eval_data["epistemic_phenotype"],
        ))

    conn.commit()
    conn.close()

    print("\n" + "=" * 155)
    print("      EXPERIMENT 1B-C2a.1: RE-SCORED PHENOTYPE DISTRIBUTION (50 CALLS)")
    print("=" * 155)

    pheno_counts: dict[str, int] = {}
    repro_counts: dict[str, int] = {}
    for r in rescored_records:
        pheno_counts[r["epistemic_phenotype"]] = pheno_counts.get(r["epistemic_phenotype"], 0) + 1
        repro_counts[r["reproductive_status"]] = repro_counts.get(r["reproductive_status"], 0) + 1

    print("\n[Decoupled Reproductive Status]")
    for rep, cnt in sorted(repro_counts.items()):
        print(f"  Reproductive Status: {rep:<15} | Count: {cnt:<3} ({cnt/len(rescored_records)*100:.1f}%)")

    print("\n[Decoupled Epistemic Phenotype]")
    for ph, cnt in sorted(pheno_counts.items()):
        print(f"  Epistemic Phenotype: {ph:<18} | Count: {cnt:<3} ({cnt/len(rescored_records)*100:.1f}%)")

    print("\n" + "=" * 155)
    print("      EXPERIMENT 1B-C2a.1: EXACT PROMPT-HASH EQUIVALENCE CLASSES (12 UNIQUE REQUESTS)")
    print("=" * 155)

    for h, calls in sorted(by_prompt_hash.items(), key=lambda x: len(x[1]), reverse=True):
        first = calls[0]
        objs = [c["normalized_object"] for c in calls]
        phenos = [c["epistemic_phenotype"] for c in calls]
        vecs = [str(c["state_vector"]) for c in calls]
        print(f"\nPrompt Hash: {h} (N = {len(calls)} invocations) | Target: {first['target_subject']} | Path: {first['context_truth_status']}")
        for c in calls:
            print(f"  {c['call_id']:<45} | Repro: {c['reproductive_status']:<8} | State: {str(c['state_vector']):<15} | Pheno: {c['epistemic_phenotype']:<18} | Emitted: {c['normalized_object']}")


if __name__ == "__main__":
    rescore_c2a_database()
