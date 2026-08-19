"""Experiment 0: Calibrated scientific execution script for honest baseline and live Gemma 3."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from gene.config import ExperimentConfig, ModelConfig, RetrievalConfig
from gene.experiments.exp0_lineage import Exp0LineageExperiment
from gene.ollama_client import HonestClient, OllamaClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator


def run_exp0_session(num_worlds: int = 5, use_live_model: bool = False, model_name: str = "gemma3:12b"):
    client_label = f"Live Ollama ({model_name})" if use_live_model else "Deterministic Honest Reference Client"
    print("=" * 72)
    print(f"   GENE EXPERIMENT 0 SESSION ({num_worlds} WORLDS)")
    print(f"   Instrument: {client_label}")
    print("=" * 72)

    db_path = "gene_exp0_calibrated.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path)
    client = OllamaClient() if use_live_model else HonestClient()
    
    cfg = ExperimentConfig(
        experiment_name="exp0_lineage_calibrated",
        experiment_version="exp0-v2",
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
        print(f"    Task Truth Accuracy: {metrics.task_truth_accuracy:.2%}")
        print(f"    Lineage Precision: {metrics.reported_lineage_precision:.2%} | Recall: {metrics.reported_lineage_recall:.2%}")
        print(f"    Causal Validation Rate: {metrics.causal_validation_rate:.2%} | Hidden Causal Rate: {metrics.hidden_causal_parent_rate:.2%}")
        print(f"    Artifacts saved to: {output_dir}")

    total_wall_time = time.perf_counter() - start_total_time

    # Aggregate statistics
    tot_calls = sum(r["metrics"].total_calls for r in completed_runs)
    tot_claims = sum(r["metrics"].total_claims for r in completed_runs)
    tot_causal = sum(r["metrics"].raw_counts.get("tested_reported_parents", 0) + r["metrics"].raw_counts.get("tested_unreported_distractors", 0) for r in completed_runs)
    tot_prompt_toks = sum(r["metrics"].total_prompt_tokens for r in completed_runs)
    tot_comp_toks = sum(r["metrics"].total_completion_tokens for r in completed_runs)
    
    mean_prec = sum(r["metrics"].reported_lineage_precision for r in completed_runs) / num_worlds
    mean_rec = sum(r["metrics"].reported_lineage_recall for r in completed_runs) / num_worlds
    mean_causal_val = sum(r["metrics"].causal_validation_rate for r in completed_runs) / num_worlds
    mean_hidden_causal = sum(r["metrics"].hidden_causal_parent_rate for r in completed_runs) / num_worlds
    mean_truth_acc = sum(r["metrics"].task_truth_accuracy for r in completed_runs) / num_worlds
    mean_struct_acc = sum(r["metrics"].structured_output_success_rate for r in completed_runs) / num_worlds

    print("\n" + "=" * 72)
    print("   EXPERIMENT 0 AGGREGATE SUMMARY")
    print("=" * 72)
    print(f"Total Worlds Processed:           {num_worlds}")
    print(f"Total Model Calls:                {tot_calls}")
    print(f"Total Claims Generated:           {tot_claims}")
    print(f"Total Causal Counterfactuals:     {tot_causal}")
    print(f"Total Tokens Processed:           {tot_prompt_toks + tot_comp_toks:,}")
    print(f"Total Wall-Clock Time:            {total_wall_time:.2f}s")
    print(f"Structured Output Success Rate:   {mean_struct_acc:.2%}")
    print(f"Task Truth Accuracy (Targeted):   {mean_truth_acc:.2%}")
    print(f"Reported Lineage Precision:       {mean_prec:.2%}")
    print(f"Reported Lineage Recall (Path):   {mean_rec:.2%}")
    print(f"Causal Validation Rate:           {mean_causal_val:.2%}")
    print(f"Hidden Causal Parent Rate:        {mean_hidden_causal:.2%}")
    print("=" * 72 + "\n")

    db.close()
    return completed_runs


if __name__ == "__main__":
    use_live = "--live" in sys.argv
    num = 1 if use_live else 5
    if "--worlds" in sys.argv:
        idx = sys.argv.index("--worlds")
        if idx + 1 < len(sys.argv):
            num = int(sys.argv[idx + 1])

    run_exp0_session(num_worlds=num, use_live_model=use_live, model_name="gemma3:12b")
