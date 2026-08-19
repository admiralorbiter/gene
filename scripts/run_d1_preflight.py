"""Targeted D1 preflight inspection script for multi-parent inference and causal controls."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.config import ExperimentConfig, ModelConfig, RetrievalConfig
from gene.evaluation.causality import CausalRunner
from gene.evaluation.metrics import MetricsCalculator, format_rate
from gene.experiments.runner import SingleCallRunner
from gene.memory.lineage import LineageRecorder
from gene.memory.retrieval import ControlledRetriever
from gene.memory.store import MemoryStore
from gene.ollama_client import HonestClient, OllamaClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator
from gene.worlds.oracle import Oracle
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.tasks import TaskGenerator


def run_d1_preflight(num_tasks: int = 3, use_live_model: bool = False, model_name: str = "gemma3:12b", seed: int = 42):
    client_label = f"Live Ollama ({model_name})" if use_live_model else "Deterministic Honest Reference Client"
    print("=" * 80)
    print(f"   GENE TARGETED D1 PREFLIGHT CAUSAL INSPECTION ({num_tasks} TASKS)")
    print(f"   Instrument: {client_label}")
    print("=" * 80)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    db_path = f"gene_d1_preflight_{timestamp}.db"
    print(f"[*] Initializing preflight database at: {db_path}")

    db = Database(db_path)
    client = OllamaClient() if use_live_model else HonestClient()

    cfg = ExperimentConfig(
        experiment_name="d1_preflight_inspection",
        experiment_version="exp0-v2",
        model=ModelConfig(model_name=model_name, temperature=0.0),
        retrieval=RetrievalConfig(num_distractors=3),
    )

    runner = SingleCallRunner(db=db, client=client, config=cfg)
    causal_runner = CausalRunner(db=db, client=client, config=cfg)

    executed_count = 0
    world_seed_idx = 0
    run_ids: list[str] = []

    while executed_count < num_tasks and world_seed_idx < 20:
        current_seed = seed + world_seed_idx * 17
        world_seed_idx += 1

        world = WorldGenerator.generate(seed=current_seed)
        oracle = Oracle(world)
        d1_tasks = TaskGenerator.generate_d1_tasks(world, oracle)
        if not d1_tasks:
            continue

        run_id = runner.create_run(world=world, condition="clean")
        run_ids.append(run_id)
        mem_store = MemoryStore(db=db, run_id=run_id, world_id=world.world_id)

        fact_to_node: dict[str, str] = {}
        node_to_text: dict[str, str] = {}
        for fact in world.facts:
            nid = f"mem_{run_id[:8]}_{fact.fact_id}"
            fact_to_node[fact.fact_id] = nid
            text = NaturalLanguageRenderer.render_fact(fact)
            node_to_text[nid] = text
            mem_store.add_node(generation=0, node_type="source", natural_text=text, structured_json=fact.canonical_dict(), node_id=nid)

        for rule in world.rules:
            nid = f"mem_{run_id[:8]}_{rule.rule_id}"
            fact_to_node[rule.rule_id] = nid
            text = NaturalLanguageRenderer.render_rule(rule)
            node_to_text[nid] = text
            mem_store.add_node(generation=0, node_type="source", natural_text=text, structured_json=rule.canonical_dict(), node_id=nid)

        active_candidate_nodes = mem_store.get_all_active_nodes(max_generation=0)

        for task in d1_tasks:
            if executed_count >= num_tasks:
                break
            executed_count += 1

            mapped_support_paths: list[list[str]] = []
            for path in task.valid_support_path_ids:
                mapped_support_paths.append([fact_to_node[fid] for fid in path])

            task_mapped = task.model_copy(update={"valid_support_path_ids": mapped_support_paths})
            required_support_ids = mapped_support_paths[0] if mapped_support_paths else []

            # Controlled retrieval
            retrieval_res = ControlledRetriever.retrieve(
                candidate_nodes=active_candidate_nodes,
                required_support_ids=required_support_ids,
                num_distractors=cfg.retrieval.num_distractors,
                seed=current_seed + executed_count,
            )

            exposed_payload = [{"memory_id": em.memory_id, "text": em.text} for em in retrieval_res.exposed_memories]

            # Execute single call
            call_res, evaluated_claim, call_id, child_node_id = runner.execute_task(
                run_id=run_id,
                world=world,
                task=task_mapped,
                oracle=oracle,
                generation=1,
                exposed_memories=exposed_payload,
            )

            # Log edges
            exposure_tuples = [(em.memory_id, child_node_id, call_id, em.retrieval_rank, em.context_position) for em in retrieval_res.exposed_memories]
            LineageRecorder.record_exposure_edges(db, exposure_tuples)

            reported_tuples = [(p_id, child_node_id, call_id, "reported_support") for p_id in evaluated_claim.reported_parent_ids]
            LineageRecorder.record_reported_support_edges(db, reported_tuples)

            print(f"\n" + "-" * 80)
            print(f"D1 Task {executed_count}/{num_tasks}: {task.task_id} (World Seed: {current_seed})")
            print(f"Question:     '{task.prompt}'")
            print(f"Target Fact:  ({task.target_fact.subject}, {task.target_fact.predicate}, {task.target_fact.object})")
            print(f"Required Ancestry Paths ({len(mapped_support_paths)} valid paths):")
            for p_i, p in enumerate(mapped_support_paths):
                print(f"  Path {p_i+1}:")
                for nid in p:
                    print(f"    - [{nid}] {node_to_text.get(nid, 'unknown')}")

            print(f"\nModel Output:")
            print(f"  Derived Claim:    ({evaluated_claim.subject}, {evaluated_claim.predicate}, {evaluated_claim.object})")
            print(f"  Truth Status:     {evaluated_claim.truth_status.value.upper()}")
            print(f"  Parse Status:     {evaluated_claim.parse_status}")
            print(f"  Reported Parents: {evaluated_claim.reported_parent_ids}")

            # Causal Counterfactual Testing
            print(f"\nCausal Counterfactual Interventions:")

            # 1. No-op sham replay
            noop_res = causal_runner.replay_intervention(
                original_call_id=call_id,
                child_node_id=child_node_id,
                target_parent_id="noop",
                intervention_type="noop",
                oracle=oracle,
                world=world,
                seed=cfg.decoding_seed,
            )
            noop_status = "STABLE (S0=0)" if noop_res.outcome == "none" else f"UNSTABLE ({noop_res.outcome})"
            print(f"  - [noop] Sham Replay:                 outcome={noop_res.outcome:<13} score={noop_res.score:.1f} -> {noop_status}")

            # 2. Reported parent ablations
            for p_id in evaluated_claim.reported_parent_ids:
                cf_res = causal_runner.replay_intervention(
                    original_call_id=call_id,
                    child_node_id=child_node_id,
                    target_parent_id=p_id,
                    intervention_type="remove",
                    oracle=oracle,
                    world=world,
                    seed=cfg.decoding_seed,
                )
                shift_desc = f"CHANGED -> ({cf_res.counterfactual_claim.subject}, {cf_res.counterfactual_claim.predicate}, {cf_res.counterfactual_claim.object})" if cf_res.outcome in ("strong", "partial") else "UNCHANGED"
                p_desc = node_to_text.get(p_id, p_id)
                if len(p_desc) > 35:
                    p_desc = p_desc[:32] + "..."
                print(f"  - [remove reported] [{p_id}] ({p_desc}): outcome={cf_res.outcome:<13} score={cf_res.score:.1f} -> {shift_desc}")

            # 3. Unreported required parent ablations (if any)
            unreported_req = [sid for sid in required_support_ids if sid not in evaluated_claim.reported_parent_ids]
            for p_id in unreported_req:
                cf_res = causal_runner.replay_intervention(
                    original_call_id=call_id,
                    child_node_id=child_node_id,
                    target_parent_id=p_id,
                    intervention_type="remove",
                    oracle=oracle,
                    world=world,
                    seed=cfg.decoding_seed,
                )
                shift_desc = f"HIDDEN PARENT CAUSAL (HR=1) -> ({cf_res.counterfactual_claim.subject}, {cf_res.counterfactual_claim.predicate}, {cf_res.counterfactual_claim.object})" if cf_res.outcome in ("strong", "partial") else "NON-CAUSAL"
                print(f"  - [remove hidden required] [{p_id}]: outcome={cf_res.outcome:<13} score={cf_res.score:.1f} -> {shift_desc}")

            # 4. Distractor ablation
            unreported_distractors = [
                em.memory_id for em in retrieval_res.exposed_memories
                if not em.is_required_support and em.memory_id not in evaluated_claim.reported_parent_ids
            ]
            if unreported_distractors:
                d_id = unreported_distractors[0]
                cf_res = causal_runner.replay_intervention(
                    original_call_id=call_id,
                    child_node_id=child_node_id,
                    target_parent_id=d_id,
                    intervention_type="remove",
                    oracle=oracle,
                    world=world,
                    seed=cfg.decoding_seed,
                )
                dist_status = "UNCHANGED CONTROL (HD=0)" if cf_res.outcome == "none" else f"DISTRACTOR INFLUENCE (HD=1) -> ({cf_res.counterfactual_claim.subject}, {cf_res.counterfactual_claim.predicate}, {cf_res.counterfactual_claim.object})"
                print(f"  - [remove distractor] [{d_id}]:       outcome={cf_res.outcome:<13} score={cf_res.score:.1f} -> {dist_status}")

    # Compute preflight metrics across executed runs
    metrics_list = [MetricsCalculator.compute_exp0_metrics(db, rid) for rid in run_ids]
    tot_claims = sum(m.total_claims for m in metrics_list)
    tot_causal = sum(m.total_causal_tests for m in metrics_list)
    tot_indet = sum(m.total_indeterminate_tests for m in metrics_list)

    avg_truth = sum(m.task_truth_accuracy for m in metrics_list) / len(metrics_list) if metrics_list else 0.0
    avg_prec = sum(m.reported_lineage_precision for m in metrics_list) / len(metrics_list) if metrics_list else 0.0
    avg_rec = sum(m.reported_lineage_recall for m in metrics_list) / len(metrics_list) if metrics_list else 0.0
    
    cnec_vals = [m.overall.reported_parent_necessity_rate_determinate for m in metrics_list if m.overall and m.overall.reported_parent_necessity_rate_determinate is not None]
    avg_cnec = sum(cnec_vals) / len(cnec_vals) if cnec_vals else None

    hr_vals = [m.overall.unreported_required_causal_rate_determinate for m in metrics_list if m.overall and m.overall.unreported_required_causal_rate_determinate is not None]
    avg_hr = sum(hr_vals) / len(hr_vals) if hr_vals else None

    hd_vals = [m.overall.unreported_distractor_influence_rate_determinate for m in metrics_list if m.overall and m.overall.unreported_distractor_influence_rate_determinate is not None]
    avg_hd = sum(hd_vals) / len(hd_vals) if hd_vals else None

    s0_vals = [m.overall.noop_instability_rate for m in metrics_list if m.overall and m.overall.noop_instability_rate is not None]
    avg_s0 = sum(s0_vals) / len(s0_vals) if s0_vals else None

    print("\n" + "=" * 80)
    print("                       D1 PREFLIGHT METRIC SUMMARY")
    print("=" * 80)
    print(f"D1 Tasks Tested:                  {tot_claims}")
    print(f"Task Truth Accuracy:              {format_rate(avg_truth)}")
    print(f"Reported Lineage Precision:       {format_rate(avg_prec)}")
    print(f"Reported Lineage Recall:          {format_rate(avg_rec)}")
    print(f"Reported Parent Necessity (Cnec): {format_rate(avg_cnec)}")
    print(f"Unreported Required Causal (HR):  {format_rate(avg_hr)}")
    print(f"Distractor Influence Rate (HD):   {format_rate(avg_hd)}")
    print(f"No-Op Instability Rate (S0):      {format_rate(avg_s0)}")
    print(f"Indeterminate Interventions:      {tot_indet} / {tot_causal}")
    print("=" * 80)
    print(f"Database Preserved At:            {db_path}")
    print("=" * 80 + "\n")

    db.close()


if __name__ == "__main__":
    use_live = "--live" in sys.argv
    tasks = 3
    if "--tasks" in sys.argv:
        idx = sys.argv.index("--tasks")
        if idx + 1 < len(sys.argv):
            tasks = int(sys.argv[idx + 1])
    run_d1_preflight(num_tasks=tasks, use_live_model=use_live, model_name="gemma3:12b")
