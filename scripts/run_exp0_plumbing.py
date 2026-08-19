"""Experiment 0: Calibrated scientific execution script for honest baseline and live Gemma 3."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.config import ExperimentConfig, ModelConfig, RetrievalConfig
from gene.evaluation.metrics import format_rate
from gene.experiments.exp0_lineage import Exp0LineageExperiment
from gene.ollama_client import HonestClient, OllamaClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator


def run_exp0_session(
    num_worlds: int = 5,
    use_live_model: bool = False,
    model_name: str = "gemma3:12b",
    custom_db_path: str | None = None,
):
    client_label = f"Live Ollama ({model_name})" if use_live_model else "Deterministic Honest Reference Client"
    print("=" * 78)
    print(f"   GENE EXPERIMENT 0 SESSION ({num_worlds} WORLDS)")
    print(f"   Instrument: {client_label}")
    print("=" * 78)

    # 1. Unique, non-destructive database preservation
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    db_path = custom_db_path or f"gene_exp0_{timestamp}.db"
    print(f"[*] Preserving run database to: {db_path}")

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
        print(f"    Calls: {metrics.total_calls} | Claims: {metrics.total_claims} | Causal Tests: {metrics.total_causal_tests}")
        print(f"    Task Truth Accuracy: {metrics.task_truth_accuracy:.2%}")
        print(f"    Lineage Precision: {metrics.reported_lineage_precision:.2%} | Recall: {metrics.reported_lineage_recall:.2%}")
        print(f"    Cnec (determinate): {format_rate(metrics.overall.reported_parent_necessity_rate_determinate if metrics.overall else None)}")
        print(f"    Cnec (conservative): {format_rate(metrics.overall.reported_parent_necessity_rate_conservative if metrics.overall else None)}")
        print(f"    Artifacts saved to: {output_dir}")

    total_wall_time = time.perf_counter() - start_total_time

    # Aggregate statistics
    tot_calls = sum(r["metrics"].total_calls for r in completed_runs)
    tot_claims = sum(r["metrics"].total_claims for r in completed_runs)
    tot_causal = sum(r["metrics"].total_causal_tests for r in completed_runs)
    tot_noop = sum(r["metrics"].total_noop_tests for r in completed_runs)
    tot_rep = sum(r["metrics"].total_reported_parent_tests for r in completed_runs)
    tot_unrep_req = sum(r["metrics"].total_unreported_required_tests for r in completed_runs)
    tot_dist = sum(r["metrics"].total_distractor_tests for r in completed_runs)
    tot_indet = sum(r["metrics"].total_indeterminate_tests for r in completed_runs)
    tot_prompt_toks = sum(r["metrics"].total_prompt_tokens for r in completed_runs)
    tot_comp_toks = sum(r["metrics"].total_completion_tokens for r in completed_runs)

    # Compute aggregate stratum metrics across all worlds
    def agg_stratum(getter):
        vals = [getter(r["metrics"]) for r in completed_runs if getter(r["metrics"]) is not None]
        return sum(vals) / len(vals) if vals else None

    d0_acc = agg_stratum(lambda m: m.d0.task_truth_accuracy if m.d0 else None)
    d1_acc = agg_stratum(lambda m: m.d1.task_truth_accuracy if m.d1 else None)
    ov_acc = agg_stratum(lambda m: m.overall.task_truth_accuracy if m.overall else None)

    d0_prec = agg_stratum(lambda m: m.d0.reported_lineage_precision if m.d0 else None)
    d1_prec = agg_stratum(lambda m: m.d1.reported_lineage_precision if m.d1 else None)
    ov_prec = agg_stratum(lambda m: m.overall.reported_lineage_precision if m.overall else None)

    d0_rec = agg_stratum(lambda m: m.d0.reported_lineage_recall if m.d0 else None)
    d1_rec = agg_stratum(lambda m: m.d1.reported_lineage_recall if m.d1 else None)
    ov_rec = agg_stratum(lambda m: m.overall.reported_lineage_recall if m.overall else None)

    d0_cnec_det = agg_stratum(lambda m: m.d0.reported_parent_necessity_rate_determinate if m.d0 else None)
    d1_cnec_det = agg_stratum(lambda m: m.d1.reported_parent_necessity_rate_determinate if m.d1 else None)
    ov_cnec_det = agg_stratum(lambda m: m.overall.reported_parent_necessity_rate_determinate if m.overall else None)

    d0_cnec_con = agg_stratum(lambda m: m.d0.reported_parent_necessity_rate_conservative if m.d0 else None)
    d1_cnec_con = agg_stratum(lambda m: m.d1.reported_parent_necessity_rate_conservative if m.d1 else None)
    ov_cnec_con = agg_stratum(lambda m: m.overall.reported_parent_necessity_rate_conservative if m.overall else None)

    d0_hr = agg_stratum(lambda m: m.d0.unreported_required_causal_rate_determinate if m.d0 else None)
    d1_hr = agg_stratum(lambda m: m.d1.unreported_required_causal_rate_determinate if m.d1 else None)
    ov_hr = agg_stratum(lambda m: m.overall.unreported_required_causal_rate_determinate if m.overall else None)

    d0_hd = agg_stratum(lambda m: m.d0.unreported_distractor_influence_rate_determinate if m.d0 else None)
    d1_hd = agg_stratum(lambda m: m.d1.unreported_distractor_influence_rate_determinate if m.d1 else None)
    ov_hd = agg_stratum(lambda m: m.overall.unreported_distractor_influence_rate_determinate if m.overall else None)

    d0_s0 = agg_stratum(lambda m: m.d0.noop_instability_rate if m.d0 else None)
    d1_s0 = agg_stratum(lambda m: m.d1.noop_instability_rate if m.d1 else None)
    ov_s0 = agg_stratum(lambda m: m.overall.noop_instability_rate if m.overall else None)

    d0_indet = agg_stratum(lambda m: m.d0.causal_tests_indeterminate_rate if m.d0 else None)
    d1_indet = agg_stratum(lambda m: m.d1.causal_tests_indeterminate_rate if m.d1 else None)
    ov_indet = agg_stratum(lambda m: m.overall.causal_tests_indeterminate_rate if m.overall else None)

    print("\n" + "=" * 78)
    print("                     EXPERIMENT 0 STRATIFIED SUMMARY")
    print("=" * 78)
    header = f"{'Metric':<36} {'D0 (Direct)':<14} {'D1 (Inference)':<14} {'Overall':<14}"
    print(header)
    print("-" * 78)
    print(f"{'Task Truth Accuracy':<36} {format_rate(d0_acc):<14} {format_rate(d1_acc):<14} {format_rate(ov_acc):<14}")
    print(f"{'Reported Lineage Precision':<36} {format_rate(d0_prec):<14} {format_rate(d1_prec):<14} {format_rate(ov_prec):<14}")
    print(f"{'Reported Lineage Recall':<36} {format_rate(d0_rec):<14} {format_rate(d1_rec):<14} {format_rate(ov_rec):<14}")
    print(f"{'Cnec | determinate':<36} {format_rate(d0_cnec_det):<14} {format_rate(d1_cnec_det):<14} {format_rate(ov_cnec_det):<14}")
    print(f"{'Cnec | conservative lower bound':<36} {format_rate(d0_cnec_con):<14} {format_rate(d1_cnec_con):<14} {format_rate(ov_cnec_con):<14}")
    print(f"{'Unreported Required Causal (HR)':<36} {format_rate(d0_hr):<14} {format_rate(d1_hr):<14} {format_rate(ov_hr):<14}")
    print(f"{'Distractor Influence Rate (HD)':<36} {format_rate(d0_hd):<14} {format_rate(d1_hd):<14} {format_rate(ov_hd):<14}")
    print(f"{'No-Op Instability Rate (S0)':<36} {format_rate(d0_s0):<14} {format_rate(d1_s0):<14} {format_rate(ov_s0):<14}")
    print(f"{'Indeterminate Test Rate':<36} {format_rate(d0_indet):<14} {format_rate(d1_indet):<14} {format_rate(ov_indet):<14}")
    print("=" * 78)
    print(f"Total Worlds Processed:           {num_worlds}")
    print(f"Total Model Calls:                {tot_calls}")
    print(f"Total Claims Generated:           {tot_claims}")
    print(f"Total Causal Tests Attempted:     {tot_causal}")
    print(f"  - Reported Parent Tests:        {tot_rep}")
    print(f"  - Unreported Required Tests:    {tot_unrep_req}")
    print(f"  - Distractor Tests:             {tot_dist}")
    print(f"  - No-Op Sham Tests:             {tot_noop}")
    print(f"  - Indeterminate Interventions:  {tot_indet}")
    print(f"Total Tokens Processed:           {tot_prompt_toks + tot_comp_toks:,}")
    print(f"Total Wall-Clock Time:            {total_wall_time:.2f}s")
    print(f"Database Preserved At:            {db_path}")
    print("=" * 78 + "\n")

    db.close()
    return completed_runs


if __name__ == "__main__":
    use_live = "--live" in sys.argv
    num = 1 if use_live else 5
    if "--worlds" in sys.argv:
        idx = sys.argv.index("--worlds")
        if idx + 1 < len(sys.argv):
            num = int(sys.argv[idx + 1])

    db_arg = None
    if "--db" in sys.argv:
        idx = sys.argv.index("--db")
        if idx + 1 < len(sys.argv):
            db_arg = sys.argv[idx + 1]

    run_exp0_session(num_worlds=num, use_live_model=use_live, model_name="gemma3:12b", custom_db_path=db_arg)
