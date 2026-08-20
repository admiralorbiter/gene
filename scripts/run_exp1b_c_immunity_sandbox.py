"""Experiment 1B-C1: Delayed-Adjudication Retrieval & Selective Immunity Sandbox.

Evaluates post-adjudication G2 -> G3 reproduction path availability (C_H, C_I)
across 6 paired worlds under BM25 retrieval across the TPR x FPR risk frontier
for 6 candidate filtering policies with exact 4-state analytic weighting.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gene.immunity.policy_engine import (
    EpistemicPolicyEngine,
    PolicyName,
    PolicyNode,
    get_analytic_state_weights,
)
from gene.memory.scored_retriever import BM25ScoredRetriever
from gene.memory.store import MemoryNode
from gene.persistence.db import Database
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, Rule, Task, World, compute_fact_id
from run_exp1b_retrieval_assay import generate_clutter_distractors


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


from gene.worlds.oracle import Oracle


def build_world_lineage_nodes(
    bundle,
    seed: int,
) -> tuple[list[PolicyNode], list[PolicyNode], Fact, Fact, Fact, Fact, list[Fact], list[Fact]]:
    """Build G0 -> G1 -> G2 lineage nodes and G3 tasks for clean and infected arms."""
    station = bundle.station
    clean_world = bundle.clean_world
    mutated_world = bundle.mutated_world

    clean_oracle = Oracle(clean_world)
    mut_oracle = Oracle(mutated_world)

    # G0 Roots
    clean_founder = bundle.clean_founder_fact
    mutated_founder = bundle.mutated_founder_fact
    mgr_fact = [f for f in clean_world.facts if f.predicate == "manager"][0]

    # G1 Nodes (protocol and security clearance)
    clean_g1_proto = [f for f in clean_oracle.closure_facts.values() if f.predicate == "uses_protocol"][0]
    mut_g1_proto = [f for f in mut_oracle.closure_facts.values() if f.predicate == "uses_protocol"][0]

    clean_g1_sec = [f for f in clean_oracle.closure_facts.values() if f.predicate == "security_clearance"][0]
    mut_g1_sec = [f for f in mut_oracle.closure_facts.values() if f.predicate == "security_clearance"][0]

    # G2 Nodes (transit_route and resource_tier)
    clean_g2_route = [f for f in clean_oracle.closure_facts.values() if f.predicate == "transit_route"][0]
    mut_g2_route = [f for f in mut_oracle.closure_facts.values() if f.predicate == "transit_route"][0]

    clean_g2_res = [f for f in clean_oracle.closure_facts.values() if f.predicate == "resource_tier"][0]
    mut_g2_res = [f for f in mut_oracle.closure_facts.values() if f.predicate == "resource_tier"][0]

    # G3 Co-supports (independent environmental facts)
    grid_fact = Fact(
        fact_id=compute_fact_id(station, "facility_grid", f"GRID_{seed % 10}"),
        subject=station,
        predicate="facility_grid",
        object=f"GRID_{seed % 10}",
    )
    beacon_fact = Fact(
        fact_id=compute_fact_id(station, "beacon_freq", f"FREQ_{seed % 10}"),
        subject=station,
        predicate="beacon_freq",
        object=f"FREQ_{seed % 10}",
    )

    # Distractor clutter (4 easy, 4 hard)
    easy_dist, hard_dist = generate_clutter_distractors(station, easy_count=4, hard_count=4, seed=seed)

    # Convert to PolicyNodes
    # Clean arm nodes
    clean_nodes = [
        PolicyNode(
            node_id=f"clean_g0_founder_{clean_founder.fact_id[:8]}",
            locus_id="locus_manager_supervisor",
            generation=0,
            is_root=True,
            family_id="clean_lineage",
            text=NaturalLanguageRenderer.render_fact(clean_founder),
        ),
        PolicyNode(
            node_id=f"clean_g0_mgr_{mgr_fact.fact_id[:8]}",
            locus_id="locus_station_manager",
            generation=0,
            is_root=False,
            family_id="station_common",
            text=NaturalLanguageRenderer.render_fact(mgr_fact),
        ),
        PolicyNode(
            node_id=f"clean_g1_proto_{clean_g1_proto.fact_id[:8]}",
            locus_id="locus_uses_protocol",
            generation=1,
            parent_ids=(f"clean_g0_founder_{clean_founder.fact_id[:8]}", f"clean_g0_mgr_{mgr_fact.fact_id[:8]}"),
            family_id="clean_lineage",
            text=NaturalLanguageRenderer.render_fact(clean_g1_proto),
        ),
        PolicyNode(
            node_id=f"clean_g1_sec_{clean_g1_sec.fact_id[:8]}",
            locus_id="locus_security_clearance",
            generation=1,
            parent_ids=(f"clean_g0_founder_{clean_founder.fact_id[:8]}", f"clean_g0_mgr_{mgr_fact.fact_id[:8]}"),
            family_id="clean_lineage",
            text=NaturalLanguageRenderer.render_fact(clean_g1_sec),
        ),
        PolicyNode(
            node_id=f"clean_g2_route_{clean_g2_route.fact_id[:8]}",
            locus_id="locus_transit_route",
            generation=2,
            parent_ids=(f"clean_g1_proto_{clean_g1_proto.fact_id[:8]}",),
            family_id="clean_lineage",
            text=NaturalLanguageRenderer.render_fact(clean_g2_route),
        ),
        PolicyNode(
            node_id=f"clean_g2_res_{clean_g2_res.fact_id[:8]}",
            locus_id="locus_resource_tier",
            generation=2,
            parent_ids=(f"clean_g1_proto_{clean_g1_proto.fact_id[:8]}",),
            family_id="clean_lineage",
            text=NaturalLanguageRenderer.render_fact(clean_g2_res),
        ),
    ]

    # Infected arm nodes
    mut_nodes = [
        PolicyNode(
            node_id=f"mut_g0_founder_{mutated_founder.fact_id[:8]}",
            locus_id="locus_manager_supervisor",
            generation=0,
            is_root=True,
            family_id="infected_lineage",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mutated_founder),
        ),
        PolicyNode(
            node_id=f"clean_g0_mgr_{mgr_fact.fact_id[:8]}",
            locus_id="locus_station_manager",
            generation=0,
            is_root=False,
            family_id="station_common",
            text=NaturalLanguageRenderer.render_fact(mgr_fact),
        ),
        PolicyNode(
            node_id=f"mut_g1_proto_{mut_g1_proto.fact_id[:8]}",
            locus_id="locus_uses_protocol",
            generation=1,
            parent_ids=(f"mut_g0_founder_{mutated_founder.fact_id[:8]}", f"clean_g0_mgr_{mgr_fact.fact_id[:8]}"),
            family_id="infected_lineage",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_g1_proto),
        ),
        PolicyNode(
            node_id=f"mut_g1_sec_{mut_g1_sec.fact_id[:8]}",
            locus_id="locus_security_clearance",
            generation=1,
            parent_ids=(f"mut_g0_founder_{mutated_founder.fact_id[:8]}", f"clean_g0_mgr_{mgr_fact.fact_id[:8]}"),
            family_id="infected_lineage",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_g1_sec),
        ),
        PolicyNode(
            node_id=f"mut_g2_route_{mut_g2_route.fact_id[:8]}",
            locus_id="locus_transit_route",
            generation=2,
            parent_ids=(f"mut_g1_proto_{mut_g1_proto.fact_id[:8]}",),
            family_id="infected_lineage",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_g2_route),
        ),
        PolicyNode(
            node_id=f"mut_g2_res_{mut_g2_res.fact_id[:8]}",
            locus_id="locus_resource_tier",
            generation=2,
            parent_ids=(f"mut_g1_proto_{mut_g1_proto.fact_id[:8]}",),
            family_id="infected_lineage",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_g2_res),
        ),
    ]

    # Shared common co-supports & clutter
    co_support_nodes = [
        PolicyNode(
            node_id=f"common_grid_{grid_fact.fact_id[:8]}",
            locus_id="locus_facility_grid",
            generation=0,
            is_root=False,
            family_id="station_common",
            text=NaturalLanguageRenderer.render_fact(grid_fact),
        ),
        PolicyNode(
            node_id=f"common_beacon_{beacon_fact.fact_id[:8]}",
            locus_id="locus_beacon_freq",
            generation=0,
            is_root=False,
            family_id="station_common",
            text=NaturalLanguageRenderer.render_fact(beacon_fact),
        ),
    ]

    clutter_nodes = []
    for idx, f in enumerate(easy_dist + hard_dist):
        clutter_nodes.append(PolicyNode(
            node_id=f"clutter_{f.fact_id[:8]}_{idx}",
            locus_id=f.locus_id,
            generation=0,
            is_root=False,
            family_id="clutter",
            text=NaturalLanguageRenderer.render_fact(f),
        ))

    full_clean_pool = clean_nodes + co_support_nodes + clutter_nodes
    full_mut_pool = mut_nodes + co_support_nodes + clutter_nodes

    clean_root_id = clean_nodes[0].node_id
    mut_root_id = mut_nodes[0].node_id

    return (
        full_clean_pool,
        full_mut_pool,
        clean_g2_route,
        mut_g2_route,
        grid_fact,
        beacon_fact,
        easy_dist,
        hard_dist,
    )


def run_exp1b_c_immunity_sandbox(
    world_seeds: list[tuple[int, int]] | None = None,
    tprs: list[float] | None = None,
    fprs: list[float] | None = None,
    top_k_list: list[int] | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Execute Experiment 1B-C1 delayed-adjudication retrieval sandbox across the TPR x FPR frontier."""
    seeds = world_seeds or [(7000, 0), (7001, 1), (7002, 2), (7003, 3), (7004, 4), (7005, 5)]
    tpr_grid = tprs or [0.5, 0.75, 0.9, 1.0]
    fpr_grid = fprs or [0.0, 0.05, 0.10, 0.20, 0.40]
    k_vals = top_k_list or [4, 6]

    policies: list[PolicyName] = [
        "baseline",
        "uniform_thinning",
        "random_family_quarantine",
        "node_only_quarantine",
        "lineage_quarantine",
        "oracle_upper_bound",
    ]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_file = db_path or f"gene_exp1b_c_immunity_sandbox_{timestamp}.db"
    db = Database(db_file)
    git_commit = get_git_commit()

    print("=" * 145)
    print("      EXPERIMENT 1B-C1: DELAYED ADJUDICATION & SELECTIVE LINEAGE IMMUNITY SANDBOX")
    print(f"      (Worlds: {len(seeds)} | Policies: {len(policies)} | Grid: {len(tpr_grid)} TPRs x {len(fpr_grid)} FPRs | k in {k_vals})")
    print(f"      (Database: {db_file} | Commit: {git_commit[:8]} | Mode: EXACT ANALYTIC WEIGHTING)")
    print("=" * 145)

    # Matrix: [top_k][policy][(tpr, fpr)] -> {ch_sum, ci_sum, count}
    frontier_results: dict[int, dict[PolicyName, dict[tuple[float, float], dict[str, float]]]] = {
        k: {
            p: {(tpr, fpr): {"c_h": 0.0, "c_i": 0.0, "s": 0.0, "autoimmunity": 0.0, "containment": 0.0} for tpr in tpr_grid for fpr in fpr_grid}
            for p in policies
        }
        for k in k_vals
    }

    total_evals = 0

    for w_idx, (seed, rot) in enumerate(seeds):
        bundle = generate_exp1_branching_world(world_seed=seed, rotation_idx=rot)
        station = bundle.station

        (
            clean_pool,
            mut_pool,
            clean_g2_target,
            mut_g2_target,
            co_support_grid,
            co_support_beacon,
            _, _,
        ) = build_world_lineage_nodes(bundle, seed)

        clean_root_id = [n.node_id for n in clean_pool if n.is_root][0]
        mut_root_id = [n.node_id for n in mut_pool if n.is_root][0]

        # Target G3 Query: "What transit_route and facility_grid are assigned to station VELORA?"
        query_text = f"What transit_route and facility_grid are assigned to station {station}?"

        # Pre-evaluate discrete state outcomes for each (k, policy, state)
        # 4 Signal states: (S_H, S_I) in {0, 1}^2
        state_outcomes: dict[int, dict[PolicyName, dict[tuple[int, int], tuple[float, float]]]] = {
            k: {p: {} for p in policies} for k in k_vals
        }

        clean_g2_id = [n.node_id for n in clean_pool if n.locus_id == "locus_transit_route"][0]
        co_grid_id = [n.node_id for n in clean_pool if n.locus_id == "locus_facility_grid"][0]
        mut_g2_id = [n.node_id for n in mut_pool if n.locus_id == "locus_transit_route"][0]

        for k in k_vals:
            for policy in policies:
                for s_h in [0, 1]:
                    for s_i in [0, 1]:
                        state = (s_h, s_i)
                        
                        # Evaluate Clean Arm
                        sig_clean = {clean_root_id: bool(s_h)}
                        clean_eval = EpistemicPolicyEngine.apply_policy(
                            policy=policy,
                            nodes=clean_pool,
                            root_signals=sig_clean,
                            clean_root_id=clean_root_id,
                            infected_root_id=mut_root_id,
                            signal_state=state,
                            seed=seed,
                        )
                        # Build BM25 retriever over retained nodes
                        clean_retriever = BM25ScoredRetriever()
                        retained_clean_memories = [
                            MemoryNode(
                                node_id=n.node_id,
                                run_id=f"c1_w{w_idx}",
                                world_id=bundle.clean_world.world_id,
                                generation=n.generation,
                                node_type="source" if n.generation == 0 else "derived",
                                natural_text=n.text,
                                locus_id=n.locus_id,
                            )
                            for n in clean_pool
                            if n.node_id in clean_eval.retained_node_ids
                        ]
                        clean_res = clean_retriever.rank(
                            query=query_text,
                            candidate_nodes=retained_clean_memories,
                            top_k=k,
                            seed=seed,
                        )
                        retrieved_clean_ids = {c.memory_id for c in clean_res.selected_memories}

                        # Check if both required G2 parent and co-support are retrieved
                        clean_path_retrieved = 1.0 if (clean_g2_id in retrieved_clean_ids and co_grid_id in retrieved_clean_ids) else 0.0

                        # Evaluate Infected Arm
                        sig_mut = {mut_root_id: bool(s_i)}
                        mut_eval = EpistemicPolicyEngine.apply_policy(
                            policy=policy,
                            nodes=mut_pool,
                            root_signals=sig_mut,
                            clean_root_id=clean_root_id,
                            infected_root_id=mut_root_id,
                            signal_state=state,
                            seed=seed,
                        )
                        mut_retriever = BM25ScoredRetriever()
                        retained_mut_memories = [
                            MemoryNode(
                                node_id=n.node_id,
                                run_id=f"c1_w{w_idx}",
                                world_id=bundle.mutated_world.world_id,
                                generation=n.generation,
                                node_type="source" if n.generation == 0 else "derived",
                                natural_text=n.text,
                                locus_id=n.locus_id,
                            )
                            for n in mut_pool
                            if n.node_id in mut_eval.retained_node_ids
                        ]
                        mut_res = mut_retriever.rank(
                            query=query_text,
                            candidate_nodes=retained_mut_memories,
                            top_k=k,
                            seed=seed,
                        )
                        retrieved_mut_ids = {c.memory_id for c in mut_res.selected_memories}

                        mut_path_retrieved = 1.0 if (mut_g2_id in retrieved_mut_ids and co_grid_id in retrieved_mut_ids) else 0.0

                        state_outcomes[k][policy][state] = (clean_path_retrieved, mut_path_retrieved)
                        total_evals += 1

        # Now compute analytically weighted expectations across the (TPR, FPR) grid
        for k in k_vals:
            for policy in policies:
                for tpr in tpr_grid:
                    for fpr in fpr_grid:
                        weights = get_analytic_state_weights(tpr, fpr)
                        w_ch = 0.0
                        w_ci = 0.0
                        for state, p_state in weights.items():
                            c_h_state, c_i_state = state_outcomes[k][policy][state]
                            w_ch += p_state * c_h_state
                            w_ci += p_state * c_i_state

                        # Accumulate across worlds (normalized by num worlds later)
                        frontier_results[k][policy][(tpr, fpr)]["c_h"] += w_ch / len(seeds)
                        frontier_results[k][policy][(tpr, fpr)]["c_i"] += w_ci / len(seeds)

    # Compute S, autoimmunity, and containment
    for k in k_vals:
        for policy in policies:
            for tpr in tpr_grid:
                for fpr in fpr_grid:
                    res = frontier_results[k][policy][(tpr, fpr)]
                    res["s"] = res["c_h"] - res["c_i"]
                    res["autoimmunity"] = 1.0 - res["c_h"]
                    res["containment"] = 1.0 - res["c_i"]

                    # Persist to SQLite
                    with db.conn:
                        db.conn.execute("""
                            INSERT INTO retrieval_sweep_results (
                                sweep_id, run_id, sweep_type, world_id, world_seed, arm, generation,
                                task_id, target_predicate, top_k, n_hard, easy_clutter, pool_size,
                                founder_retrieved, cosup_retrieved, path_retrieved,
                                founder_rank, cosup_rank, founder_margin, cosup_margin,
                                g_assembly, paired_diff_path, config_hash, git_commit, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            f"exp1b_c1_k{k}_{policy}_tpr{int(tpr*100)}_fpr{int(fpr*100)}",
                            f"run_c1_k{k}_{policy}",
                            "immunity_sandbox",
                            "aggregate_6_worlds",
                            7000,
                            policy,
                            3,
                            "terminal_auth",
                            "transit_route",
                            k,
                            4,
                            4,
                            16,
                            int(res["c_h"] * 100),
                            int(res["c_i"] * 100),
                            int(res["s"] * 100),
                            int(tpr * 100),
                            int(fpr * 100),
                            int(res["containment"] * 100),
                            int(res["autoimmunity"] * 100),
                            res["s"],
                            res["c_h"] - res["c_i"],
                            f"tpr={tpr}_fpr={fpr}",
                            git_commit,
                            datetime.now(timezone.utc).isoformat(),
                        ))

    # Print Formatted Comparison Frontier Table at k=6
    k_display = 6
    print("\n" + "=" * 145)
    print(f"      EXPERIMENT 1B-C1: SELECTIVE IMMUNITY FRONTIER AT TOP-K = {k_display} (6 PARED WORLDS)")
    print("=" * 145)
    print(f"{'Policy':<26} | {'TPR':<5} | {'FPR':<5} | {'C_H (Healthy)':<15} | {'C_I (Infected)':<15} | {'Containment (1-CI)':<18} | {'Autoimmunity (1-CH)':<20} | {'Separation (S)':<14}")
    print("-" * 145)

    for policy in policies:
        for tpr in tpr_grid:
            for fpr in fpr_grid:
                if (tpr, fpr) in frontier_results[k_display][policy]:
                    r = frontier_results[k_display][policy][(tpr, fpr)]
                    print(
                        f"{policy:<26} | {tpr:<5.2f} | {fpr:<5.2f} | {r['c_h']:<15.3f} | {r['c_i']:<15.3f} | "
                        f"{r['containment']:<18.3f} | {r['autoimmunity']:<20.3f} | {r['s']:<14.3f}"
                    )
        print("-" * 145)

    db.close()
    return frontier_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B-C1 Immunity Sandbox")
    parser.add_argument("--db", type=str, default=None, help="Custom SQLite database path")
    args = parser.parse_args()

    run_exp1b_c_immunity_sandbox(db_path=args.db)
