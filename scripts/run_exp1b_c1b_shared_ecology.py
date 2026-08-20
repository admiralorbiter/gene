"""Experiment 1B-C1b: Hardened Shared-Ecology Retrieval Sandbox & True Pareto Envelope.

Evaluates delayed-adjudication post-lineage retrieval competition where Healthy
Lineage H and Infected Lineage I coexist in the same shared memory pool and compete
for top-k retrieval budget across 8 core policies and full control budget sweeps over
12 fully balanced, role-swapped ecologies with zero live LLM compute.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.immunity.policy_engine import (
    EpistemicPolicyEngine,
    PolicyNode,
    get_analytic_state_weights,
)
from gene.memory.scored_retriever import BM25ScoredRetriever
from gene.memory.store import MemoryNode
from gene.persistence.db import Database
from gene.worlds.exp1_branching import STATIONS, generate_exp1_branching_world
from gene.worlds.oracle import Oracle
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, compute_fact_id


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


# All 6 unique unordered pairs from the 4 generator stations
ALL_STATION_PAIRS = list(itertools.combinations(["VELORA", "KESTREL", "HYPERION", "VANGUARD"], 2))


def get_station_world_seed(station_name: str) -> int:
    """Return a deterministic world seed that maps directly to the target station name."""
    idx = STATIONS.index(station_name)
    return 7000 + idx


def build_role_swapped_ecology(
    station_h: str,
    station_i: str,
    base_seed: int = 7000,
) -> tuple[list[PolicyNode], str, str]:
    """Build a balanced shared memory pool with Station H (Clean) and Station I (Infected)."""
    seed_h = get_station_world_seed(station_h)
    seed_i = get_station_world_seed(station_i)

    # 1. Healthy Station H (Clean World Closure)
    bundle_h = generate_exp1_branching_world(seed_h, 0)
    oracle_h = Oracle(bundle_h.clean_world)
    h_facts = list(oracle_h.closure_facts.values())

    clean_founder = [f for f in h_facts if f.predicate == "reports_to"][0]
    clean_mgr = [f for f in h_facts if f.predicate == "manager"][0]
    clean_proto = [f for f in h_facts if f.predicate == "uses_protocol"][0]
    clean_sec = [f for f in h_facts if f.predicate == "security_clearance"][0]
    clean_route = [f for f in h_facts if f.predicate == "transit_route"][0]
    clean_res = [f for f in h_facts if f.predicate == "resource_tier"][0]

    h_grid = Fact(
        fact_id=compute_fact_id(station_h, "facility_grid", f"GRID_{seed_h % 5}"),
        subject=station_h,
        predicate="facility_grid",
        object=f"GRID_{seed_h % 5}",
    )
    h_beacon = Fact(
        fact_id=compute_fact_id(station_h, "beacon_freq", f"FREQ_{seed_h % 10}"),
        subject=station_h,
        predicate="beacon_freq",
        object=f"FREQ_{seed_h % 10}",
    )

    clean_root_id = f"{station_h}_g0_founder_{clean_founder.fact_id[:8]}"
    clean_mgr_id = f"{station_h}_g0_mgr_{clean_mgr.fact_id[:8]}"
    clean_proto_id = f"{station_h}_g1_proto_{clean_proto.fact_id[:8]}"
    clean_sec_id = f"{station_h}_g1_sec_{clean_sec.fact_id[:8]}"
    clean_route_id = f"{station_h}_g2_route_{clean_route.fact_id[:8]}"
    clean_res_id = f"{station_h}_g2_res_{clean_res.fact_id[:8]}"
    clean_grid_id = f"{station_h}_g0_grid_{h_grid.fact_id[:8]}"
    clean_beacon_id = f"{station_h}_g0_beacon_{h_beacon.fact_id[:8]}"

    h_nodes = [
        PolicyNode(
            node_id=clean_root_id,
            locus_id=f"{station_h}_locus_supervisor",
            generation=0,
            is_root=True,
            family_id=f"family_{station_h}",
            text=NaturalLanguageRenderer.render_fact(clean_founder),
        ),
        PolicyNode(
            node_id=clean_mgr_id,
            locus_id=f"{station_h}_locus_manager",
            generation=0,
            is_root=False,
            family_id=f"family_{station_h}",
            text=NaturalLanguageRenderer.render_fact(clean_mgr),
        ),
        PolicyNode(
            node_id=clean_proto_id,
            locus_id=f"{station_h}_locus_uses_protocol",
            generation=1,
            parent_ids=(clean_root_id, clean_mgr_id),
            family_id=f"family_{station_h}",
            text=NaturalLanguageRenderer.render_fact(clean_proto),
        ),
        PolicyNode(
            node_id=clean_sec_id,
            locus_id=f"{station_h}_locus_security_clearance",
            generation=1,
            parent_ids=(clean_root_id, clean_mgr_id),
            family_id=f"family_{station_h}",
            text=NaturalLanguageRenderer.render_fact(clean_sec),
        ),
        PolicyNode(
            node_id=clean_route_id,
            locus_id=f"{station_h}_locus_transit_route",
            generation=2,
            parent_ids=(clean_proto_id,),
            family_id=f"family_{station_h}",
            text=NaturalLanguageRenderer.render_fact(clean_route),
        ),
        PolicyNode(
            node_id=clean_res_id,
            locus_id=f"{station_h}_locus_resource_tier",
            generation=2,
            parent_ids=(clean_proto_id,),
            family_id=f"family_{station_h}",
            text=NaturalLanguageRenderer.render_fact(clean_res),
        ),
        PolicyNode(
            node_id=clean_grid_id,
            locus_id=f"{station_h}_locus_facility_grid",
            generation=0,
            is_root=False,
            family_id=f"common_{station_h}",
            text=NaturalLanguageRenderer.render_fact(h_grid),
        ),
        PolicyNode(
            node_id=clean_beacon_id,
            locus_id=f"{station_h}_locus_beacon_freq",
            generation=0,
            is_root=False,
            family_id=f"common_{station_h}",
            text=NaturalLanguageRenderer.render_fact(h_beacon),
        ),
    ]

    # 2. Infected Station I (Mutated World Closure)
    bundle_i = generate_exp1_branching_world(seed_i, 0)
    oracle_i = Oracle(bundle_i.mutated_world)
    i_facts = list(oracle_i.closure_facts.values())

    mut_founder = [f for f in i_facts if f.predicate == "reports_to"][0]
    mut_mgr = [f for f in i_facts if f.predicate == "manager"][0]
    mut_proto = [f for f in i_facts if f.predicate == "uses_protocol"][0]
    mut_sec = [f for f in i_facts if f.predicate == "security_clearance"][0]
    mut_route = [f for f in i_facts if f.predicate == "transit_route"][0]
    mut_res = [f for f in i_facts if f.predicate == "resource_tier"][0]

    i_grid = Fact(
        fact_id=compute_fact_id(station_i, "facility_grid", f"GRID_{seed_i % 5}"),
        subject=station_i,
        predicate="facility_grid",
        object=f"GRID_{seed_i % 5}",
    )
    i_beacon = Fact(
        fact_id=compute_fact_id(station_i, "beacon_freq", f"FREQ_{seed_i % 10}"),
        subject=station_i,
        predicate="beacon_freq",
        object=f"FREQ_{seed_i % 10}",
    )

    mut_root_id = f"{station_i}_g0_founder_{mut_founder.fact_id[:8]}"
    mut_mgr_id = f"{station_i}_g0_mgr_{mut_mgr.fact_id[:8]}"
    mut_proto_id = f"{station_i}_g1_proto_{mut_proto.fact_id[:8]}"
    mut_sec_id = f"{station_i}_g1_sec_{mut_sec.fact_id[:8]}"
    mut_route_id = f"{station_i}_g2_route_{mut_route.fact_id[:8]}"
    mut_res_id = f"{station_i}_g2_res_{mut_res.fact_id[:8]}"
    mut_grid_id = f"{station_i}_g0_grid_{i_grid.fact_id[:8]}"
    mut_beacon_id = f"{station_i}_g0_beacon_{i_beacon.fact_id[:8]}"

    i_nodes = [
        PolicyNode(
            node_id=mut_root_id,
            locus_id=f"{station_i}_locus_supervisor",
            generation=0,
            is_root=True,
            family_id=f"family_{station_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_founder),
        ),
        PolicyNode(
            node_id=mut_mgr_id,
            locus_id=f"{station_i}_locus_manager",
            generation=0,
            is_root=False,
            family_id=f"family_{station_i}",
            text=NaturalLanguageRenderer.render_fact(mut_mgr),
        ),
        PolicyNode(
            node_id=mut_proto_id,
            locus_id=f"{station_i}_locus_uses_protocol",
            generation=1,
            parent_ids=(mut_root_id, mut_mgr_id),
            family_id=f"family_{station_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_proto),
        ),
        PolicyNode(
            node_id=mut_sec_id,
            locus_id=f"{station_i}_locus_security_clearance",
            generation=1,
            parent_ids=(mut_root_id, mut_mgr_id),
            family_id=f"family_{station_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_sec),
        ),
        PolicyNode(
            node_id=mut_route_id,
            locus_id=f"{station_i}_locus_transit_route",
            generation=2,
            parent_ids=(mut_proto_id,),
            family_id=f"family_{station_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_route),
        ),
        PolicyNode(
            node_id=mut_res_id,
            locus_id=f"{station_i}_locus_resource_tier",
            generation=2,
            parent_ids=(mut_proto_id,),
            family_id=f"family_{station_i}",
            is_infected_allele=True,
            text=NaturalLanguageRenderer.render_fact(mut_res),
        ),
        PolicyNode(
            node_id=mut_grid_id,
            locus_id=f"{station_i}_locus_facility_grid",
            generation=0,
            is_root=False,
            family_id=f"common_{station_i}",
            text=NaturalLanguageRenderer.render_fact(i_grid),
        ),
        PolicyNode(
            node_id=mut_beacon_id,
            locus_id=f"{station_i}_locus_beacon_freq",
            generation=0,
            is_root=False,
            family_id=f"common_{station_i}",
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
    return shared_pool, clean_root_id, mut_root_id


def run_exp1b_c1b_shared_ecology(
    tprs: list[float] | None = None,
    fprs: list[float] | None = None,
    top_k_list: list[int] | None = None,
    n_mc_samples: int = 50,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Execute hardened Experiment 1B-C1b shared-ecology sweep across all 12 balanced ecologies."""
    tpr_grid = tprs or [0.50, 0.75, 0.90, 1.00]
    fpr_grid = fprs or [0.00, 0.05, 0.10, 0.20, 0.40]
    k_vals = top_k_list or [4, 6, 8]

    git_commit = get_git_commit()
    db_file = db_path or f"gene_exp1b_c1b_shared_ecology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    db = Database(Path(db_file))

    # Construct 12 Balanced Ecologies (6 pairs x 2 role assignments)
    ecologies: list[dict[str, Any]] = []
    for pair_idx, (st_a, st_b) in enumerate(ALL_STATION_PAIRS):
        pair_seed = 7000 + pair_idx
        ecologies.append({
            "pair_id": f"pair_{pair_idx}",
            "station_h": st_a,
            "station_i": st_b,
            "role_assignment": "forward",
            "world_seed": pair_seed,
        })
        ecologies.append({
            "pair_id": f"pair_{pair_idx}",
            "station_h": st_b,
            "station_i": st_a,
            "role_assignment": "swapped",
            "world_seed": pair_seed,
        })

    # Core policies evaluated across the grid
    core_policies = [
        "baseline",
        "signal_blind_uniform_thinning",
        "signal_conditioned_uniform_thinning",
        "generation_matched_thinning",
        "random_family_quarantine",
        "node_only_quarantine",
        "lineage_quarantine",
        "oracle_upper_bound",
    ]

    # Additional budget sweep policies for uniform thinning control
    budget_sweep_m = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14]
    budget_policies = [f"uniform_thinning_m{m}" for m in budget_sweep_m]

    all_eval_policies = core_policies + budget_policies

    print("=" * 155)
    print("      EXPERIMENT 1B-C1b: HARDENED SHARED-ECOLOGY SANDBOX & FULL CONTROL ENVELOPE")
    print(f"      (Ecologies: {len(ecologies)} [6 pairs x 2 role swaps] | Policies: {len(core_policies)} core + {len(budget_policies)} budget sweeps)")
    print(f"      (Grid: {len(tpr_grid)} TPRs x {len(fpr_grid)} FPRs | k in {k_vals} | MC Samples: N_mc={n_mc_samples})")
    print(f"      (Database: {db_file} | Commit: {git_commit} | Mode: 12-ECOLOGY ROLE-BALANCED EXACT WEIGHTING)")
    print("=" * 155)

    # Initialize results structures
    frontier_results: dict[int, dict[str, dict[tuple[float, float], dict[str, float]]]] = {
        k: {
            p: {
                (tpr, fpr): {"c_h": 0.0, "c_i": 0.0, "s": 0.0, "autoimmunity": 0.0, "containment": 0.0}
                for tpr in tpr_grid
                for fpr in fpr_grid
            }
            for p in all_eval_policies
        }
        for k in k_vals
    }

    retriever = BM25ScoredRetriever()

    for eco_idx, eco in enumerate(ecologies):
        st_h = eco["station_h"]
        st_i = eco["station_i"]
        seed = eco["world_seed"]

        shared_pool, clean_root_id, mut_root_id = build_role_swapped_ecology(st_h, st_i, base_seed=seed)

        query_h = f"What transit_route and facility_grid are assigned to station {st_h}?"
        query_i = f"What transit_route and facility_grid are assigned to station {st_i}?"

        h_g2_target_id = [n.node_id for n in shared_pool if n.locus_id == f"{st_h}_locus_transit_route"][0]
        h_grid_target_id = [n.node_id for n in shared_pool if n.locus_id == f"{st_h}_locus_facility_grid"][0]

        i_g2_target_id = [n.node_id for n in shared_pool if n.locus_id == f"{st_i}_locus_transit_route"][0]
        i_grid_target_id = [n.node_id for n in shared_pool if n.locus_id == f"{st_i}_locus_facility_grid"][0]

        # 4 Discrete signal states: (S_H, S_I) in {0, 1}^2
        state_outcomes: dict[int, dict[str, dict[tuple[int, int], tuple[float, float]]]] = {
            k: {p: {} for p in all_eval_policies} for k in k_vals
        }

        for k in k_vals:
            for policy in all_eval_policies:
                # Parse budget sweep policies
                if policy.startswith("uniform_thinning_m"):
                    base_pol = "signal_blind_uniform_thinning"
                    m_budget = int(policy.replace("uniform_thinning_m", ""))
                else:
                    base_pol = policy
                    m_budget = 3

                for s_h in [0, 1]:
                    for s_i in [0, 1]:
                        state = (s_h, s_i)
                        root_signals = {
                            clean_root_id: bool(s_h),
                            mut_root_id: bool(s_i),
                        }

                        # Generate Monte Carlo samples for stochastic policies or single for deterministic
                        samples = EpistemicPolicyEngine.apply_policy_samples(
                            policy=base_pol,
                            nodes=shared_pool,
                            root_signals=root_signals,
                            clean_root_id=clean_root_id,
                            infected_root_id=mut_root_id,
                            signal_state=state,
                            base_seed=seed,
                            n_samples=n_mc_samples,
                            fixed_thinning_budget=m_budget,
                        )

                        sample_h_scores = []
                        sample_i_scores = []

                        for s_eval in samples:
                            retained_memories = [
                                MemoryNode(
                                    node_id=n.node_id,
                                    run_id=f"c1b_eco{eco_idx}",
                                    world_id=f"shared_{st_h}_{st_i}",
                                    generation=n.generation,
                                    node_type="source" if n.generation == 0 else "derived",
                                    natural_text=n.text,
                                    locus_id=n.locus_id,
                                )
                                for n in shared_pool
                                if n.node_id in s_eval.retained_node_ids
                            ]

                            # Rank for Clean Task (Station H)
                            res_h = retriever.rank(query=query_h, candidate_nodes=retained_memories, top_k=k, seed=seed)
                            retrieved_ids_h = {c.memory_id for c in res_h.selected_memories}
                            h_ok = 1.0 if (h_g2_target_id in retrieved_ids_h and h_grid_target_id in retrieved_ids_h) else 0.0
                            sample_h_scores.append(h_ok)

                            # Rank for Infected Task (Station I)
                            res_i = retriever.rank(query=query_i, candidate_nodes=retained_memories, top_k=k, seed=seed)
                            retrieved_ids_i = {c.memory_id for c in res_i.selected_memories}
                            i_ok = 1.0 if (i_g2_target_id in retrieved_ids_i and i_grid_target_id in retrieved_ids_i) else 0.0
                            sample_i_scores.append(i_ok)

                        exp_h = sum(sample_h_scores) / len(sample_h_scores)
                        exp_i = sum(sample_i_scores) / len(sample_i_scores)
                        state_outcomes[k][policy][state] = (exp_h, exp_i)

        # Analytically weight across the (TPR, FPR) grid
        for k in k_vals:
            for policy in all_eval_policies:
                for tpr in tpr_grid:
                    for fpr in fpr_grid:
                        weights = get_analytic_state_weights(tpr, fpr)
                        w_ch = 0.0
                        w_ci = 0.0
                        for state, p_state in weights.items():
                            c_h_state, c_i_state = state_outcomes[k][policy][state]
                            w_ch += p_state * c_h_state
                            w_ci += p_state * c_i_state

                        frontier_results[k][policy][(tpr, fpr)]["c_h"] += w_ch / len(ecologies)
                        frontier_results[k][policy][(tpr, fpr)]["c_i"] += w_ci / len(ecologies)

    # Compute metrics and persist to SQLite immunity_policy_results
    for k in k_vals:
        for policy in all_eval_policies:
            for tpr in tpr_grid:
                for fpr in fpr_grid:
                    res = frontier_results[k][policy][(tpr, fpr)]
                    res["s"] = res["c_h"] - res["c_i"]
                    res["autoimmunity"] = 1.0 - res["c_h"]
                    res["containment"] = 1.0 - res["c_i"]

                    # Compute expected drop budget E[m]
                    if policy.startswith("uniform_thinning_m"):
                        exp_m = int(policy.replace("uniform_thinning_m", ""))
                        g2_b = 0
                    elif policy == "signal_blind_uniform_thinning":
                        exp_m = 3
                        g2_b = 0
                    elif policy == "node_only_quarantine":
                        exp_m = int(round(fpr + tpr))
                        g2_b = 0
                    elif policy in ("signal_conditioned_uniform_thinning", "lineage_quarantine", "random_family_quarantine"):
                        exp_m = int(round(5 * (fpr + tpr)))
                        g2_b = int(round(2 * (fpr + tpr)))
                    elif policy == "generation_matched_thinning":
                        exp_m = int(round(2 * (fpr + tpr)))
                        g2_b = exp_m
                    elif policy == "oracle_upper_bound":
                        exp_m = 5
                        g2_b = 2
                    else:
                        exp_m = 0
                        g2_b = 0

                    cfg_raw = f"{policy}_{k}_{tpr}_{fpr}_{exp_m}_{n_mc_samples}"
                    cfg_hash = hashlib.sha256(cfg_raw.encode("utf-8")).hexdigest()[:16]

                    with db.conn:
                        db.conn.execute("""
                            INSERT INTO immunity_policy_results (
                                result_id, run_id, sweep_type, policy, station_h, station_i,
                                role_assignment, world_seed, top_k, tpr, fpr, c_h, c_i,
                                separation_s, containment, autoimmunity, drop_budget,
                                g2_drop_budget, expectation_method, config_hash, git_commit, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            f"c1b_k{k}_{policy}_tpr{int(tpr*100)}_fpr{int(fpr*100)}",
                            f"run_c1b_k{k}_{policy}",
                            "shared_ecology_hardened_full_envelope",
                            policy,
                            "aggregate_12_ecologies",
                            "aggregate_12_ecologies",
                            "bidirectional_balanced",
                            7000,
                            k,
                            tpr,
                            fpr,
                            res["c_h"],
                            res["c_i"],
                            res["s"],
                            res["containment"],
                            res["autoimmunity"],
                            exp_m,
                            g2_b,
                            f"monte_carlo_n{n_mc_samples}",
                            cfg_hash,
                            git_commit,
                            datetime.now(timezone.utc).isoformat(),
                        ))

    # Print Formatted Results at k=6
    k_display = 6
    print("\n" + "=" * 155)
    print(f"      EXPERIMENT 1B-C1b: SAME-DETECTOR OPERATING POINT LEDGER AT TOP-K = {k_display} (12 BALANCED ECOLOGIES)")
    print("=" * 155)
    print(f"{'Policy':<36} | {'TPR':<5} | {'FPR':<5} | {'C_H (Healthy)':<15} | {'C_I (Infected)':<15} | {'Containment (1-CI)':<18} | {'Autoimmunity (1-CH)':<20} | {'Separation (S)':<14}")
    print("-" * 155)

    for policy in core_policies:
        for tpr in tpr_grid:
            for fpr in fpr_grid:
                if (tpr, fpr) in frontier_results[k_display][policy]:
                    r = frontier_results[k_display][policy][(tpr, fpr)]
                    print(
                        f"{policy:<36} | {tpr:<5.2f} | {fpr:<5.2f} | {r['c_h']:<15.3f} | {r['c_i']:<15.3f} | "
                        f"{r['containment']:<18.3f} | {r['autoimmunity']:<20.3f} | {r['s']:<14.3f}"
                    )
        print("-" * 155)

    # Calculate True Matched-Coverage Pareto Envelope across ALL non-lineage controls and all budget sweeps
    print("\n" + "=" * 155)
    print("      TRUE NONDOMINATED CONTROL ENVELOPE: Delta_I(C_H) = min(C_I^ctrl | C_H^ctrl >= C_H^lin) - C_I^lin")
    print("=" * 155)
    print(f"{'Detector Setting':<18} | {'Lineage C_H':<13} | {'Lineage C_I':<13} | {'Min Ctrl C_I':<14} | {'Best Control Configuration':<40} | {'Delta_I Gain':<14}")
    print("-" * 155)

    # Collect all non-lineage control configurations
    control_points: list[dict[str, Any]] = []
    all_control_policies = [p for p in all_eval_policies if p not in ("lineage_quarantine", "oracle_upper_bound")]

    for p in all_control_policies:
        for tpr in tpr_grid:
            for fpr in fpr_grid:
                pt = frontier_results[k_display][p][(tpr, fpr)]
                control_points.append({
                    "policy": p,
                    "tpr": tpr,
                    "fpr": fpr,
                    "c_h": pt["c_h"],
                    "c_i": pt["c_i"],
                })

    for tpr in [0.75, 0.90, 1.00]:
        for fpr in [0.00, 0.05, 0.10, 0.20]:
            if (tpr, fpr) in frontier_results[k_display]["lineage_quarantine"]:
                lin_pt = frontier_results[k_display]["lineage_quarantine"][(tpr, fpr)]
                c_h_target = lin_pt["c_h"]
                c_i_lin = lin_pt["c_i"]

                # Find eligible control configurations satisfying C_H >= c_h_target
                eligible_ctrls = [cp for cp in control_points if cp["c_h"] >= c_h_target - 1e-4]

                if eligible_ctrls:
                    best_ctrl = min(eligible_ctrls, key=lambda cp: cp["c_i"])
                    min_ctrl_ci = best_ctrl["c_i"]
                    best_ctrl_desc = f"{best_ctrl['policy']} (TPR={best_ctrl['tpr']:.2f}, FPR={best_ctrl['fpr']:.2f})"
                    delta_i = min_ctrl_ci - c_i_lin
                else:
                    min_ctrl_ci = float("nan")
                    best_ctrl_desc = "None (Coverage Unreachable)"
                    delta_i = float("nan")

                print(
                    f"TPR={tpr:.2f}, FPR={fpr:.2f} | {c_h_target:<13.3f} | {c_i_lin:<13.3f} | "
                    f"{min_ctrl_ci:<14.3f} | {best_ctrl_desc:<40} | {delta_i:<+14.3f}"
                )
    print("-" * 155)

    db.close()
    return frontier_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Hardened Experiment 1B-C1b Shared-Ecology Sandbox")
    parser.add_argument("--db", type=str, default=None, help="Path to output SQLite database")
    parser.add_argument("--mc", type=int, default=50, help="Number of Monte Carlo samples for random controls")
    args = parser.parse_args()

    run_exp1b_c1b_shared_ecology(db_path=args.db, n_mc_samples=args.mc)
