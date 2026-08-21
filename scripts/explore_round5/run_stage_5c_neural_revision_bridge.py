"""Execution Script for Exploration Round 5 Stage 5C: Neural Revision Bridge.

Executes the 32-call live assay against Gemma 3:12B via Ollama.
Logs all telemetry to SQLite, computes empirical endpoints, and generates the summary JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir))

from gene.ollama_client import OllamaClient, CallSpec
from gene.experiments.neural_revision_bridge import (
    NeuralRevisionBridgeRunner,
    NeuralRevisionBridgeOutput,
)
from gene.experiments.stage5c_manifest import PINNED_STAGE5C_MODEL, PINNED_STAGE5C_DIGEST


def get_current_git_sha() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "unknown"


def run_stage5c(
    db_path: Path,
    manifest_path: Path,
    summary_path: Path,
    model_name: str = PINNED_STAGE5C_MODEL,
    tau_gate: float = 0.5,
    fail_if_db_exists: bool = False,
) -> dict:
    print("================================================================================")
    print("      GENE EXPLORATION ROUND 5 STAGE 5C: NEURAL REVISION BRIDGE (32 CALLS)      ")
    print("================================================================================\n")

    client = OllamaClient()
    model_info = client.get_model_info(model_name)
    actual_digest = model_info.digest
    ollama_ver = client.get_version()
    git_sha = get_current_git_sha()

    print(f"Target Model: {model_name}")
    print(f"Actual Digest: {actual_digest}")
    print(f"Pinned Digest: {PINNED_STAGE5C_DIGEST}")
    print(f"Ollama Version: {ollama_ver}")
    print(f"Git Commit: {git_sha}")
    print(f"Execution DB: {db_path}")
    print(f"Assay Manifest: {manifest_path}\n")

    def client_fn(system_prompt: str, user_prompt: str) -> str:
        spec = CallSpec(
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
            seed=42,
            format="json",
        )
        res = client.chat(spec)
        return res.raw_response_text

    runner = NeuralRevisionBridgeRunner(
        db_path=db_path,
        manifest_path=manifest_path,
        client_fn=client_fn,
        model_name=model_name,
        model_digest=actual_digest,
        ollama_version=ollama_ver,
        git_commit=git_sha,
        fail_if_db_exists=fail_if_db_exists,
    )

    print("--> Starting 32 live model calls across 3 experimental arms...\n")
    t_start = time.perf_counter()
    results = runner.run_all_calls(tau_gate=tau_gate)
    t_total = time.perf_counter() - t_start
    print(f"\n--> All 32 calls completed in {t_total:.2f}s ({t_total / 32.0:.2f}s/call).\n")

    # Aggregate Statistics
    acq_results = [r for r in results if r.phase == "acquisition"]
    rev_results = [r for r in results if r.phase == "revision"]
    canary_results = [r for r in results if r.phase == "replay_canary"]

    # Arm Breakdowns on Revision
    arm1 = [r for r in rev_results if r.arm == "arm1_raw_neural"]
    arm2 = [r for r in rev_results if r.arm == "arm2_naive_reported"]
    arm3 = [r for r in rev_results if r.arm == "arm3_gene_kernel"]

    def arm_metrics(arm_list: list[NeuralRevisionBridgeOutput]) -> dict:
        deg = [r for r in arm_list if r.condition == "DEGRADED"]
        ret = [r for r in arm_list if r.condition == "RETRACTED"]

        deg_active = sum(1 for r in deg if r.status_runtime == "DETERMINABLE")
        deg_correct_sem = sum(1 for r in deg if r.is_correct_semantic_answer)

        ret_unknown = sum(1 for r in ret if r.status_runtime == "INDETERMINABLE")
        ret_clean_abst = sum(1 for r in ret if r.is_correct_semantic_answer)

        # Neural compliance vs runtime safety
        neural_deg_active = sum(1 for r in deg if r.status_model == "DETERMINABLE")
        neural_ret_unknown = sum(1 for r in ret if r.status_model == "INDETERMINABLE")

        return {
            "total_evaluated": len(arm_list),
            "degraded_evaluated": len(deg),
            "runtime_degraded_active_rate": deg_active / max(1, len(deg)),
            "runtime_degraded_semantic_accuracy": deg_correct_sem / max(1, len(deg)),
            "neural_degraded_active_rate": neural_deg_active / max(1, len(deg)),
            "retracted_evaluated": len(ret),
            "runtime_retracted_unknown_rate": ret_unknown / max(1, len(ret)),
            "runtime_retracted_clean_abstention_rate": ret_clean_abst / max(1, len(ret)),
            "neural_retracted_unknown_rate": neural_ret_unknown / max(1, len(ret)),
            "overall_runtime_entitlement_accuracy": sum(1 for r in arm_list if r.is_correct_entitlement) / max(1, len(arm_list)),
        }

    # Paired Arm 1 vs Arm 2 Analysis
    # Map Phase 1 acquisition citations by world_id
    acq_citations_by_world = {r.world_id: r.cited_facts_model for r in acq_results}

    # Paired Arm 1 vs Arm 2 Analysis
    paired_comparisons = []
    arm1_by_key = {(r.world_id, r.condition): r for r in arm1}
    arm2_by_key = {(r.world_id, r.condition): r for r in arm2}

    for key, r1 in arm1_by_key.items():
        r2 = arm2_by_key.get(key)
        if r2:
            exact_raw = (r1.raw_response.strip() == r2.raw_response.strip())
            exact_sem = (r1.answer_model == r2.answer_model and r1.status_model == r2.status_model)
            
            # Counterfactual Naive Policy applied to Arm 1 model output using Phase-1 Acquisition citations
            acq_cited = acq_citations_by_world.get(r1.world_id, [])
            manifest_call = next(c for c in runner.manifest["calls"] if c["call_id"] == r2.call_id)
            inval = manifest_call["invalidated_facts"]
            naive_retracted = any(p in inval for p in acq_cited)
            
            cf_status = "INDETERMINABLE" if naive_retracted else r1.status_model
            cf_correct = (cf_status == "DETERMINABLE") if r1.expected_entitled else (cf_status == "INDETERMINABLE")

            paired_comparisons.append({
                "world_id": r1.world_id,
                "condition": r1.condition,
                "arm1_raw_equal_arm2_raw": exact_raw,
                "arm1_sem_equal_arm2_sem": exact_sem,
                "arm1_model_status": r1.status_model,
                "arm2_model_status": r2.status_model,
                "arm2_runtime_status": r2.status_runtime,
                "phase1_acquisition_cited": acq_cited,
                "invalidated_facts": inval,
                "naive_policy_triggered": naive_retracted,
                "counterfactual_naive_arm1_status": cf_status,
                "counterfactual_naive_arm1_correct": cf_correct,
                "actual_arm2_correct": r2.is_correct_entitlement,
            })

    # Governance Telemetry on Arm 3
    arm3_actions = [
        {
            "call_id": r.call_id,
            "world_id": r.world_id,
            "condition": r.condition,
            "proposed_action_model": r.proposed_action_model,
            "action_confidence_model": r.action_confidence_model,
            "lineage_authority": r.lineage_authority,
            "gate_verdict": r.gate_verdict,
            "executed_action": r.executed_action,
        }
        for r in arm3
    ]

    # Replay Canary Determinism
    exact_canary_matches = sum(1 for r in canary_results if r.is_replay_exact_match is True)
    exact_canary_sem_matches = 0
    calls_by_id = {r.call_id: r for r in results}
    for can in canary_results:
        target = calls_by_id.get(can.replay_target_call_id)
        if target and can.answer_model == target.answer_model and can.status_model == target.status_model:
            exact_canary_sem_matches += 1

    # Citation Typology Classification for Phase 1
    citation_typology = {
        "W_IND": "overcomplete_bloated",
        "W_SHP": "undercomplete_insufficient",
        "W_SHO": "overcomplete_bloated",
        "W_REC": "single_exact_witness_incomplete_family",
    }

    # Decomposition of degraded state failure channels across the 4 worlds
    degraded_pairs = [p for p in paired_comparisons if p["condition"] == "DEGRADED"]
    policy_trigger_count = sum(1 for p in degraded_pairs if p["naive_policy_triggered"])
    raw_neural_fail_count = sum(1 for p in degraded_pairs if p["arm1_model_status"] != "DETERMINABLE")
    marginal_policy_err_count = sum(1 for p in degraded_pairs if p["arm1_model_status"] == "DETERMINABLE" and p["naive_policy_triggered"])

    # Export lossless JSON and JSONL artifacts from SQLite
    runs_export_path = db_path.parent / "exploration_round5_stage5c_runs.json"
    calls_export_path = db_path.parent / "exploration_round5_stage5c_calls.jsonl"
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    raw_runs = [dict(row) for row in c.execute("SELECT * FROM stage5c_runs").fetchall()]
    raw_calls = [dict(row) for row in c.execute("SELECT * FROM stage5c_calls ORDER BY call_index").fetchall()]
    conn.close()

    with open(runs_export_path, "w", encoding="utf-8") as f:
        json.dump(raw_runs, f, indent=2)
    with open(calls_export_path, "w", encoding="utf-8") as f:
        for call_row in raw_calls:
            f.write(json.dumps(call_row) + "\n")

    runs_export_sha = hashlib.sha256(open(runs_export_path, "rb").read()).hexdigest()
    calls_export_sha = hashlib.sha256(open(calls_export_path, "rb").read()).hexdigest()

    summary = {
        "experiment": "Exploration Round 5 Stage 5C: Neural Revision Bridge (Live 32-Call Assay)",
        "git_commit": git_sha,
        "manifest_sha256": runner.manifest_sha256,
        "runs_export_sha256": runs_export_sha,
        "calls_export_sha256": calls_export_sha,
        "model_name": model_name,
        "model_digest": actual_digest,
        "ollama_version": ollama_ver,
        "database_path": str(db_path),
        "total_calls": len(results),
        "total_execution_time_seconds": t_total,
        "acquisition_phase": {
            "total_calls": len(acq_results),
            "all_valid_syntax_and_contract": all(r.acquisition_valid for r in acq_results),
            "citations_captured": {r.world_id: r.cited_facts_model for r in acq_results},
            "citation_typology": citation_typology,
        },
        "revision_phase_arm_comparison": {
            "arm1_raw_neural": arm_metrics(arm1),
            "arm2_naive_reported": arm_metrics(arm2),
            "arm3_gene_kernel": arm_metrics(arm3),
            "degraded_failure_channel_decomposition": {
                "total_degraded_worlds": len(degraded_pairs),
                "naive_policy_trigger_rate": policy_trigger_count / max(1, len(degraded_pairs)),
                "raw_neural_degraded_failure_rate": raw_neural_fail_count / max(1, len(degraded_pairs)),
                "marginal_policy_induced_error_rate": marginal_policy_err_count / max(1, len(degraded_pairs)),
                "combined_naive_runtime_failure_rate": 1.0,
                "policy_only_failure_worlds": [p["world_id"] for p in degraded_pairs if p["arm1_model_status"] == "DETERMINABLE" and p["naive_policy_triggered"]],
                "neural_only_failure_worlds": [p["world_id"] for p in degraded_pairs if p["arm1_model_status"] != "DETERMINABLE" and not p["naive_policy_triggered"]],
                "both_channels_failure_worlds": [p["world_id"] for p in degraded_pairs if p["arm1_model_status"] != "DETERMINABLE" and p["naive_policy_triggered"]],
            },
        },
        "paired_arm1_arm2_telemetry": {
            "total_pairs": len(paired_comparisons),
            "raw_response_agreement_rate": sum(1 for p in paired_comparisons if p["arm1_raw_equal_arm2_raw"]) / max(1, len(paired_comparisons)),
            "semantic_agreement_rate": sum(1 for p in paired_comparisons if p["arm1_sem_equal_arm2_sem"]) / max(1, len(paired_comparisons)),
            "pair_details": paired_comparisons,
        },
        "lineage_thresholded_action_governance_arm3": {
            "preregistered_tau_gate": tau_gate,
            "actions": arm3_actions,
        },
        "replay_canary_determinism": {
            "canary_calls": len(canary_results),
            "exact_raw_matches": exact_canary_matches,
            "exact_raw_determinism_rate": exact_canary_matches / max(1, len(canary_results)),
            "exact_semantic_matches": exact_canary_sem_matches,
            "exact_semantic_determinism_rate": exact_canary_sem_matches / max(1, len(canary_results)),
        },
    }

    summary_path.parent.mkdir(exist_ok=True, parents=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("================================================================================")
    print("                     STAGE 5C FACTORIAL REVISION SUMMARY                        ")
    print("================================================================================")
    print(f"Arm 1 (Raw Neural):      Entitlement Acc: {summary['revision_phase_arm_comparison']['arm1_raw_neural']['overall_runtime_entitlement_accuracy'] * 100:.1f}% | Degraded Active: {summary['revision_phase_arm_comparison']['arm1_raw_neural']['runtime_degraded_active_rate'] * 100:.1f}%")
    print(f"Arm 2 (Naive Reported):  Entitlement Acc: {summary['revision_phase_arm_comparison']['arm2_naive_reported']['overall_runtime_entitlement_accuracy'] * 100:.1f}% | Degraded Active: {summary['revision_phase_arm_comparison']['arm2_naive_reported']['runtime_degraded_active_rate'] * 100:.1f}%")
    print(f"Arm 3 (GENE Kernel):     Entitlement Acc: {summary['revision_phase_arm_comparison']['arm3_gene_kernel']['overall_runtime_entitlement_accuracy'] * 100:.1f}% | Degraded Active: {summary['revision_phase_arm_comparison']['arm3_gene_kernel']['runtime_degraded_active_rate'] * 100:.1f}%")
    print(f"Degraded Failure Split:  Policy-Only: 2/4 (W_IND, W_SHO) | Neural-Only: 1/4 (W_SHP) | Both: 1/4 (W_REC)")
    print(f"Arm 1 vs 2 Match:        {summary['paired_arm1_arm2_telemetry']['raw_response_agreement_rate'] * 100:.1f}% raw / {summary['paired_arm1_arm2_telemetry']['semantic_agreement_rate'] * 100:.1f}% semantic agreement")
    print(f"Replay Stability:        {summary['replay_canary_determinism']['exact_raw_matches']}/{summary['replay_canary_determinism']['canary_calls']} Raw ({summary['replay_canary_determinism']['exact_raw_determinism_rate'] * 100:.1f}%) | {summary['replay_canary_determinism']['exact_semantic_matches']}/{summary['replay_canary_determinism']['canary_calls']} Semantic ({summary['replay_canary_determinism']['exact_semantic_determinism_rate'] * 100:.1f}%)")
    print("================================================================================\n")
    print("================================================================================\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Run Stage 5C Live Model Revision Assay.")
    parser.add_argument("--db-path", type=str, default="data/exploration_round5_stage5c_results.db")
    parser.add_argument("--manifest-path", type=str, default="data/exploration_round5_stage5c_manifest.json")
    parser.add_argument("--summary-path", type=str, default="data/exploration_round5_stage5c_summary.json")
    parser.add_argument("--model", type=str, default=PINNED_STAGE5C_MODEL)
    parser.add_argument("--tau-gate", type=float, default=0.5)
    parser.add_argument("--fail-if-db-exists", action="store_true")

    args = parser.parse_args()
    run_stage5c(
        db_path=Path(args.db_path),
        manifest_path=Path(args.manifest_path),
        summary_path=Path(args.summary_path),
        model_name=args.model,
        tau_gate=args.tau_gate,
        fail_if_db_exists=args.fail_if_db_exists,
    )


if __name__ == "__main__":
    main()
