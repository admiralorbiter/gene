"""Experiment 1B-C1b: Shared-Ecology Retrieval Sandbox & Multi-Control Audit.

Evaluates delayed-adjudication post-lineage retrieval competition where Healthy
Lineage H (Station A) and Infected Lineage I (Station B) coexist in the same shared
memory pool and compete for top-k retrieval budget across 7 distinct control and
intervention policies with zero live LLM compute.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.immunity.policy_engine import (
    EpistemicPolicyEngine,
    PolicyNode,
    get_analytic_state_weights,
)
import subprocess
from gene.memory.scored_retriever import BM25ScoredRetriever
from gene.memory.store import MemoryNode
from gene.persistence.db import Database
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.oracle import Oracle
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, compute_fact_id


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


STATION_PAIRS = [
    ("VELORA", "KESTREL"),
    ("ORION", "ALTAIR"),
    ("SOLIS", "LUMINA"),
    ("AURA", "NOVA"),
    ("VORTEX", "NEBULA"),
    ("ZENITH", "NADIR"),
]


def build_shared_ecology_pool(
    seed: int,
) -> tuple[list[PolicyNode], str, str, str, str]:
    """Build a combined shared candidate pool with Lineage H and Lineage I."""
    # 1. Generate Clean World for Station H
    bundle_h = generate_exp1_branching_world(seed, 0)
    st_h = bundle_h.station
    oracle_h = Oracle(bundle_h.clean_world)
    h_facts = list(oracle_h.closure_facts.values())

    clean_founder = [f for f in h_facts if f.predicate == "reports_to"][0]
    clean_mgr = [f for f in h_facts if f.predicate == "manager"][0]
    clean_proto = [f for f in h_facts if f.predicate == "uses_protocol"][0]
    clean_sec = [f for f in h_facts if f.predicate == "security_clearance"][0]
    clean_route = [f for f in h_facts if f.predicate == "transit_route"][0]
    clean_res = [f for f in h_facts if f.predicate == "resource_tier"][0]

    h_grid = Fact(
        fact_id=compute_fact_id(st_h, "facility_grid", f"GRID_{seed % 5}"),
        subject=st_h,
        predicate="facility_grid",
        object=f"GRID_{seed % 5}",
    )
    h_beacon = Fact(
        fact_id=compute_fact_id(st_h, "beacon_freq", f"FREQ_{seed % 10}"),
        subject=st_h,
        predicate="beacon_freq",
        object=f"FREQ_{seed % 10}",
    )

    # 2. Generate Mutated World for Station I
    bundle_i = generate_exp1_branching_world(seed + 1, 0)
    st_i = bundle_i.station
    oracle_i = Oracle(bundle_i.mutated_world)
    i_facts = list(oracle_i.closure_facts.values())

    mut_founder = [f for f in i_facts if f.predicate == "reports_to"][0]
    mut_mgr = [f for f in i_facts if f.predicate == "manager"][0]
    mut_proto = [f for f in i_facts if f.predicate == "uses_protocol"][0]
    mut_sec = [f for f in i_facts if f.predicate == "security_clearance"][0]
    mut_route = [f for f in i_facts if f.predicate == "transit_route"][0]
    mut_res = [f for f in i_facts if f.predicate == "resource_tier"][0]

    i_grid = Fact(
        fact_id=compute_fact_id(st_i, "facility_grid", f"GRID_{(seed + 1) % 5}"),
        subject=st_i,
        predicate="facility_grid",
        object=f"GRID_{(seed + 1) % 5}",
    )
    i_beacon = Fact(
        fact_id=compute_fact_id(st_i, "beacon_freq", f"FREQ_{(seed + 1) % 10}"),
        subject=st_i,
        predicate="beacon_freq",
        object=f"FREQ_{(seed + 1) % 10}",
    )

    # Clean lineage nodes (Station H)
    clean_root_id = f"H_g0_founder_{clean_founder.fact_id[:8]}"
    h_nodes = [
        PolicyNode(
            node_id=clean_root_id,
            locus_id=f"{st_h}_locus_supervisor",
            generation=0,
            is_root=True,
            family_id=f"family_{st_h}",
            text=NaturalLanguageRenderer.render_fact(clean_founder),
        ),
        PolicyNode(
            node_id=f"H_g0_mgr_{clean_mgr.fact_id[:8]}",
            locus_id=f"{st_h}_locus_manager",
            generation=0,
            is_root=False,
            family_id=f"family_{st_h}",
            text=NaturalLanguageRenderer.render_fact(clean_mgr),
        ),
        PolicyNode(
            node_id=f"H_g1_proto_{clean_proto.fact_id[:8]}",
            locus_id=f"{st_h}_locus_uses_protocol",
            generation=1,
            parent_ids=(clean_root_id, f"H_g0_mgr_{clean_mgr.fact_id[:8]}"),
            family_id=f"family_{st_h}",
            text=NaturalLanguageRenderer.render_fact(clean_proto),
        ),
        PolicyNode(
            node_id=f"H_g1_sec_{clean_sec.fact_id[:8]}",
            locus_id=f"{st_h}_locus_security_clearance",
            generation=1,
            parent_ids=(clean_root_id, f"H_g0_mgr_{clean_mgr.fact_id[:8]}"),
            family_id=f"family_{st_h}",
            text=NaturalLanguageRenderer.render_fact(clean_sec),
        ),
        PolicyNode(
            node_id=f"H_g2_route_{clean_route.fact_id[:8]}",
            locus_id=f"{st_h}_locus_transit_route",
            generation=2,
            parent_ids=(f"H_g1_proto_{clean_proto.fact_id[:8]}",),
            family_id=f"family_{st_h}",
            text=NaturalLanguageRenderer.render_fact(clean_route),
        ),
        PolicyNode(
            node_id=f"H_g2_res_{clean_res.fact_id[:8]}",
            locus_id=f"{st_h}_locus_resource_tier",
            generation=2,
            parent_ids=(f"H_g1_proto_{clean_proto.fact_id[:8]}",),
            family_id=f"family_{st_h}",
            text=NaturalLanguageRenderer.render_fact(clean_res),
        ),
        PolicyNode(
            node_id=f"H_g0_grid_{h_grid.fact_id[:8]}",
            locus_id=f"{st_h}_locus_facility_grid",
            generation=0,
            is_root=False,
            family_id=f"common_{st_h}",
            text=NaturalLanguageRenderer.render_fact(h_grid),
        ),
        PolicyNode(
            node_id=f"H_g0_beacon_{h_beacon.fact_id[:8]}",
            locus_id=f"{st_h}_locus_beacon_freq",
            generation=0,
            is_root=False,
            family_id=f"common_{st_h}",
            text=NaturalLanguageRenderer.render_fact(h_beacon),
        ),
    ]

    # Infected lineage nodes (Station I)
    mut_root_id = f"I_g0_founder_{mut_founder.fact_id[:8]}"
    i_nodes = [
        PolicyNode(
            node_id=mut_root_id,
            locus_id=f"{st_i}_locus_supervisor",
            generation=0,
            is_root=True,
            family_id=f"family_{st_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_founder),
        ),
        PolicyNode(
            node_id=f"I_g0_mgr_{mut_mgr.fact_id[:8]}",
            locus_id=f"{st_i}_locus_manager",
            generation=0,
            is_root=False,
            family_id=f"family_{st_i}",
            text=NaturalLanguageRenderer.render_fact(mut_mgr),
        ),
        PolicyNode(
            node_id=f"I_g1_proto_{mut_proto.fact_id[:8]}",
            locus_id=f"{st_i}_locus_uses_protocol",
            generation=1,
            parent_ids=(mut_root_id, f"I_g0_mgr_{mut_mgr.fact_id[:8]}"),
            family_id=f"family_{st_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_proto),
        ),
        PolicyNode(
            node_id=f"I_g1_sec_{mut_sec.fact_id[:8]}",
            locus_id=f"{st_i}_locus_security_clearance",
            generation=1,
            parent_ids=(mut_root_id, f"I_g0_mgr_{mut_mgr.fact_id[:8]}"),
            family_id=f"family_{st_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_sec),
        ),
        PolicyNode(
            node_id=f"I_g2_route_{mut_route.fact_id[:8]}",
            locus_id=f"{st_i}_locus_transit_route",
            generation=2,
            parent_ids=(f"I_g1_proto_{mut_proto.fact_id[:8]}",),
            family_id=f"family_{st_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_route),
        ),
        PolicyNode(
            node_id=f"I_g2_res_{mut_res.fact_id[:8]}",
            locus_id=f"{st_i}_locus_resource_tier",
            generation=2,
            parent_ids=(f"I_g1_proto_{mut_proto.fact_id[:8]}",),
            family_id=f"family_{st_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_res),
        ),
        PolicyNode(
            node_id=f"I_g0_grid_{i_grid.fact_id[:8]}",
            locus_id=f"{st_i}_locus_facility_grid",
            generation=0,
            is_root=False,
            family_id=f"common_{st_i}",
            text=NaturalLanguageRenderer.render_fact(i_grid),
        ),
        PolicyNode(
            node_id=f"I_g0_beacon_{i_beacon.fact_id[:8]}",
            locus_id=f"{st_i}_locus_beacon_freq",
            generation=0,
            is_root=False,
            family_id=f"common_{st_i}",
            text=NaturalLanguageRenderer.render_fact(i_beacon),
        ),
    ]

    # Shared Clutter Distractors (6 neutral facts across the sector)
    clutter_nodes = [
        PolicyNode(
            node_id=f"clutter_{i}",
            locus_id=f"clutter_loc_{i}",
            generation=0,
            family_id="clutter_shared",
            text=f"Sector outpost {i} was commissioned in standard epoch {2180 + i}.",
        )
        for i in range(6)
    ]

    shared_pool = h_nodes + i_nodes + clutter_nodes
    return shared_pool, clean_root_id, mut_root_id, st_h, st_i


def run_exp1b_c1b_shared_ecology(
    world_pairs: list[tuple[str, str]] | None = None,
    tprs: list[float] | None = None,
    fprs: list[float] | None = None,
    top_k_list: list[int] | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Execute Experiment 1B-C1b shared-ecology sweep across all 7 policies."""
    num_pairs = len(world_pairs) if world_pairs is not None else 6
    tpr_grid = tprs or [0.50, 0.75, 0.90, 1.00]
    fpr_grid = fprs or [0.00, 0.05, 0.10, 0.20, 0.40]
    k_vals = top_k_list or [4, 6, 8]

    git_commit = get_git_commit()
    db_file = db_path or f"gene_exp1b_c1b_shared_ecology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    db = Database(Path(db_file))

    policies = [
        "baseline",
        "signal_blind_uniform_thinning",
        "signal_conditioned_uniform_thinning",
        "generation_matched_thinning",
        "random_family_quarantine",
        "node_only_quarantine",
        "lineage_quarantine",
        "oracle_upper_bound",
    ]

    print("=" * 145)
    print("      EXPERIMENT 1B-C1b: SHARED-ECOLOGY RETRIEVAL SANDBOX & MULTI-CONTROL AUDIT")
    print(f"      (World Pairs: {num_pairs} | Policies: {len(policies)} | Grid: {len(tpr_grid)} TPRs x {len(fpr_grid)} FPRs | k in {k_vals})")
    print(f"      (Database: {db_file} | Commit: {git_commit} | Mode: SHARED ECOLOGY EXACT WEIGHTING)")
    print("=" * 145)

    # Initialize results structures
    # frontier_results[top_k][policy][(tpr, fpr)] = {"c_h": float, "c_i": float, ...}
    frontier_results: dict[int, dict[str, dict[tuple[float, float], dict[str, float]]]] = {
        k: {
            p: {
                (tpr, fpr): {"c_h": 0.0, "c_i": 0.0, "s": 0.0, "autoimmunity": 0.0, "containment": 0.0}
                for tpr in tpr_grid
                for fpr in fpr_grid
            }
            for p in policies
        }
        for k in k_vals
    }

    total_evals = 0

    for pair_idx in range(num_pairs):
        seed = 7000 + pair_idx
        shared_pool, clean_root_id, mut_root_id, st_h, st_i = build_shared_ecology_pool(seed)

        query_h = f"What transit_route and facility_grid are assigned to station {st_h}?"
        query_i = f"What transit_route and facility_grid are assigned to station {st_i}?"

        h_g2_target_id = [n.node_id for n in shared_pool if n.locus_id == f"{st_h}_locus_transit_route"][0]
        h_grid_target_id = [n.node_id for n in shared_pool if n.locus_id == f"{st_h}_locus_facility_grid"][0]

        i_g2_target_id = [n.node_id for n in shared_pool if n.locus_id == f"{st_i}_locus_transit_route"][0]
        i_grid_target_id = [n.node_id for n in shared_pool if n.locus_id == f"{st_i}_locus_facility_grid"][0]

        # 4 Discrete signal states: (S_H, S_I) in {0, 1}^2
        # Precompute state outcomes (clean_path_retrieved, mut_path_retrieved) for this pair
        pair_state_outcomes: dict[int, dict[str, dict[tuple[int, int], tuple[float, float]]]] = {
            k: {p: {} for p in policies} for k in k_vals
        }

        for k in k_vals:
            for policy in policies:
                for s_h in [0, 1]:
                    for s_i in [0, 1]:
                        state = (s_h, s_i)
                        root_signals = {
                            clean_root_id: bool(s_h),
                            mut_root_id: bool(s_i),
                        }

                        # Apply policy to shared pool
                        eval_res = EpistemicPolicyEngine.apply_policy(
                            policy=policy,
                            nodes=shared_pool,
                            root_signals=root_signals,
                            clean_root_id=clean_root_id,
                            infected_root_id=mut_root_id,
                            signal_state=state,
                            seed=seed,
                            fixed_thinning_budget=3,
                        )

                        # Build retained memories for BM25
                        retained_memories = [
                            MemoryNode(
                                node_id=n.node_id,
                                run_id=f"c1b_pair{pair_idx}",
                                world_id=f"shared_{st_h}_{st_i}",
                                generation=n.generation,
                                node_type="source" if n.generation == 0 else "derived",
                                natural_text=n.text,
                                locus_id=n.locus_id,
                            )
                            for n in shared_pool
                            if n.node_id in eval_res.retained_node_ids
                        ]

                        retriever = BM25ScoredRetriever()

                        # Rank for Clean Task (Station H)
                        res_h = retriever.rank(query=query_h, candidate_nodes=retained_memories, top_k=k, seed=seed)
                        retrieved_ids_h = {c.memory_id for c in res_h.selected_memories}
                        h_path_ok = 1.0 if (h_g2_target_id in retrieved_ids_h and h_grid_target_id in retrieved_ids_h) else 0.0

                        # Rank for Infected Task (Station I)
                        res_i = retriever.rank(query=query_i, candidate_nodes=retained_memories, top_k=k, seed=seed)
                        retrieved_ids_i = {c.memory_id for c in res_i.selected_memories}
                        i_path_ok = 1.0 if (i_g2_target_id in retrieved_ids_i and i_grid_target_id in retrieved_ids_i) else 0.0

                        pair_state_outcomes[k][policy][state] = (h_path_ok, i_path_ok)
                        total_evals += 1

        # Analytically weight over (TPR, FPR) grid
        for k in k_vals:
            for policy in policies:
                for tpr in tpr_grid:
                    for fpr in fpr_grid:
                        weights = get_analytic_state_weights(tpr, fpr)
                        w_ch = 0.0
                        w_ci = 0.0
                        for state, p_state in weights.items():
                            c_h_state, c_i_state = pair_state_outcomes[k][policy][state]
                            w_ch += p_state * c_h_state
                            w_ci += p_state * c_i_state

                        frontier_results[k][policy][(tpr, fpr)]["c_h"] += w_ch / num_pairs
                        frontier_results[k][policy][(tpr, fpr)]["c_i"] += w_ci / num_pairs

    # Compute metrics and persist to SQLite
    for k in k_vals:
        for policy in policies:
            for tpr in tpr_grid:
                for fpr in fpr_grid:
                    res = frontier_results[k][policy][(tpr, fpr)]
                    res["s"] = res["c_h"] - res["c_i"]
                    res["autoimmunity"] = 1.0 - res["c_h"]
                    res["containment"] = 1.0 - res["c_i"]

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
                            f"exp1b_c1b_k{k}_{policy}_tpr{int(tpr*100)}_fpr{int(fpr*100)}",
                            f"run_c1b_k{k}_{policy}",
                            "shared_ecology_sandbox",
                            "shared_6_station_pairs",
                            7000,
                            policy,
                            3,
                            "shared_terminal_auth",
                            "transit_route",
                            k,
                            6,
                            6,
                            22,
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

    # Print Formatted Comparison Table at k=6
    k_display = 6
    print("\n" + "=" * 155)
    print(f"      EXPERIMENT 1B-C1b: SHARED-ECOLOGY IMMUNITY FRONTIER AT TOP-K = {k_display} (6 STATION PAIRS)")
    print("=" * 155)
    print(f"{'Policy':<36} | {'TPR':<5} | {'FPR':<5} | {'C_H (Healthy)':<15} | {'C_I (Infected)':<15} | {'Containment (1-CI)':<18} | {'Autoimmunity (1-CH)':<20} | {'Separation (S)':<14}")
    print("-" * 155)

    for policy in policies:
        for tpr in tpr_grid:
            for fpr in fpr_grid:
                if (tpr, fpr) in frontier_results[k_display][policy]:
                    r = frontier_results[k_display][policy][(tpr, fpr)]
                    print(
                        f"{policy:<36} | {tpr:<5.2f} | {fpr:<5.2f} | {r['c_h']:<15.3f} | {r['c_i']:<15.3f} | "
                        f"{r['containment']:<18.3f} | {r['autoimmunity']:<20.3f} | {r['s']:<14.3f}"
                    )
        print("-" * 155)

    # Matched-Coverage Gain Analysis Delta_I(C_H) = C_I^control(C_H) - C_I^lineage(C_H)
    print("\n" + "=" * 155)
    print("      MATCHED-COVERAGE CONTAINMENT GAIN: Delta_I(C_H) = C_I^control(C_H) - C_I^lineage(C_H)")
    print("=" * 155)
    print(f"{'TPR':<5} | {'FPR':<5} | {'C_H (Lineage)':<15} | {'C_I (Lineage)':<15} | {'C_I (Sig-Cond Uni)':<18} | {'C_I (Gen-Matched)':<18} | {'Delta_I vs Uni':<15} | {'Delta_I vs Gen':<15}")
    print("-" * 155)

    for tpr in tpr_grid:
        for fpr in fpr_grid:
            if (tpr, fpr) in frontier_results[k_display]["lineage_quarantine"]:
                lin_pt = frontier_results[k_display]["lineage_quarantine"][(tpr, fpr)]
                uni_pt = frontier_results[k_display]["signal_conditioned_uniform_thinning"][(tpr, fpr)]
                gen_pt = frontier_results[k_display]["generation_matched_thinning"][(tpr, fpr)]

                delta_uni = uni_pt["c_i"] - lin_pt["c_i"]
                delta_gen = gen_pt["c_i"] - lin_pt["c_i"]

                print(
                    f"{tpr:<5.2f} | {fpr:<5.2f} | {lin_pt['c_h']:<15.3f} | {lin_pt['c_i']:<15.3f} | "
                    f"{uni_pt['c_i']:<18.3f} | {gen_pt['c_i']:<18.3f} | {delta_uni:<+15.3f} | {delta_gen:<+15.3f}"
                )
    print("-" * 155)

    db.close()
    return frontier_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1B-C1b Shared-Ecology Sandbox")
    parser.add_argument("--db", type=str, default=None, help="Path to output SQLite database")
    args = parser.parse_args()

    run_exp1b_c1b_shared_ecology(db_path=args.db)
