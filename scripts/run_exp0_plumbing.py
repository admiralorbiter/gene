"""Experiment 0 Plumbing Run: Execute 5-world session, compute aggregate metrics, and generate feedback report."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from gene.config import ExperimentConfig, ModelConfig, RetrievalConfig
from gene.experiments.exp0_lineage import Exp0LineageExperiment
from gene.ollama_client import FakeOllamaClient, OllamaClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator


def run_exp0_plumbing_session(num_worlds: int = 5, use_live_model: bool = False, model_name: str = "gemma3:12b"):
    print("=" * 68)
    print(f"   GENE EXPERIMENT 0 PLUMBING SESSION ({num_worlds} WORLDS)")
    print(f"   Model: {model_name} ({'Live Ollama' if use_live_model else 'Deterministic Fast Client'})")
    print("=" * 68)

    db_path = "gene_exp0_plumbing.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path)
    client = OllamaClient() if use_live_model else FakeOllamaClient()
    
    cfg = ExperimentConfig(
        experiment_name="exp0_lineage_plumbing",
        experiment_version="exp0-v1",
        model=ModelConfig(model_name=model_name, temperature=0.0),
        retrieval=RetrievalConfig(num_distractors=3),
    )

    exp = Exp0LineageExperiment(db=db, client=client, config=cfg)
    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)

    completed_runs: list[dict] = []
    start_total_time = time.perf_counter()

    for i in range(num_worlds):
        seed = 100 + i * 23
        print(f"\n>>> Running World {i+1}/{num_worlds} (Seed: {seed})...")
        world = WorldGenerator.generate(seed=seed)
        
        run_id, metrics, output_dir = exp.run_world(
            world=world,
            world_seed=seed,
            output_base_dir=runs_dir,
            perform_causal_tests=True,
        )

        completed_runs.append({
            "world_id": world.world_id,
            "seed": seed,
            "run_id": run_id,
            "output_dir": str(output_dir),
            "metrics": metrics,
        })

        print(f"    Run ID: {run_id}")
        print(f"    Calls: {metrics.total_calls} | Claims: {metrics.total_claims}")
        print(f"    Lineage Precision: {metrics.reported_lineage_precision:.2%} | Recall: {metrics.reported_lineage_recall:.2%}")
        print(f"    Causal Validation Rate: {metrics.causal_validation_rate:.2%}")
        print(f"    Artifacts saved to: {output_dir}")

    total_wall_time = time.perf_counter() - start_total_time

    # Aggregate statistics
    tot_calls = sum(r["metrics"].total_calls for r in completed_runs)
    tot_causal = sum(r["metrics"].raw_counts.get("total_causal_tests", 0) for r in completed_runs)
    tot_prompt_toks = sum(r["metrics"].total_prompt_tokens for r in completed_runs)
    tot_comp_toks = sum(r["metrics"].total_completion_tokens for r in completed_runs)
    
    mean_prec = sum(r["metrics"].reported_lineage_precision for r in completed_runs) / num_worlds
    mean_rec = sum(r["metrics"].reported_lineage_recall for r in completed_runs) / num_worlds
    mean_causal_val = sum(r["metrics"].causal_validation_rate for r in completed_runs) / num_worlds
    mean_truth_acc = sum(r["metrics"].task_truth_accuracy for r in completed_runs) / num_worlds
    mean_struct_acc = sum(r["metrics"].structured_output_success_rate for r in completed_runs) / num_worlds

    print("\n" + "=" * 68)
    print("   EXPERIMENT 0 PLUMBING RUN AGGREGATE SUMMARY")
    print("=" * 68)
    print(f"Total Worlds Processed:      {num_worlds}")
    print(f"Total Model Calls:           {tot_calls}")
    print(f"Total Causal Counterfactuals:{tot_causal}")
    print(f"Total Tokens Processed:      {tot_prompt_toks + tot_comp_toks:,}")
    print(f"Total Wall-Clock Time:       {total_wall_time:.2f}s")
    print(f"Structured Output Success:   {mean_struct_acc:.2%}")
    print(f"Task Truth Accuracy:         {mean_truth_acc:.2%}")
    print(f"Reported Lineage Precision:  {mean_prec:.2%}")
    print(f"Reported Lineage Recall:     {mean_rec:.2%}")
    print(f"Causal Validation Rate:      {mean_causal_val:.2%}")
    print("=" * 68 + "\n")

    db.close()
    return completed_runs


if __name__ == "__main__":
    use_live = "--live" in sys.argv
    model = "gemma3:12b"
    run_exp0_plumbing_session(num_worlds=5, use_live_model=use_live, model_name=model)
