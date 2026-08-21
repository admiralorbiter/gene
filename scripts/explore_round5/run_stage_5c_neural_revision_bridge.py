"""Execution Script for Exploration Round 5 Stage 5C: Neural Revision Bridge.

Executes the 32-call live assay against Gemma 3:12B via Ollama.
Logs all telemetry to SQLite, computes empirical endpoints, and generates the summary JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
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


def run_stage5c(
    db_path: Path,
    manifest_path: Path,
    summary_path: Path,
    model_name: str = "gemma3:12b",
    tau_gate: float = 0.5,
) -> dict:
    print("================================================================================")
    print("      GENE EXPLORATION ROUND 5 STAGE 5C: NEURAL REVISION BRIDGE (32 CALLS)      ")
    print("================================================================================\n")

    client = OllamaClient()
    model_info = client.get_model_info(model_name)
    model_digest = model_info.digest
    print(f"Target Model: {model_name} (Digest: {model_digest})")
    print(f"Execution DB: {db_path}")
    print(f"Assay Manifest: {manifest_path}\n")

    def client_fn(prompt: str) -> str:
        spec = CallSpec(
            model_name=model_name,
            system_prompt="You are an epistemic reasoning engine. You must output valid JSON.",
            user_prompt=prompt,
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

        deg_active = sum(1 for r in deg if r.parsed_status == "DETERMINABLE")
        deg_correct_sem = sum(1 for r in deg if r.is_correct_semantic_answer)

        ret_unknown = sum(1 for r in ret if r.parsed_status == "INDETERMINABLE")
        ret_clean_abst = sum(1 for r in ret if r.is_correct_semantic_answer)

        return {
            "total_evaluated": len(arm_list),
            "degraded_evaluated": len(deg),
            "degraded_active_rate": deg_active / max(1, len(deg)),
            "degraded_semantic_accuracy": deg_correct_sem / max(1, len(deg)),
            "retracted_evaluated": len(ret),
            "retracted_unknown_rate": ret_unknown / max(1, len(ret)),
            "retracted_clean_abstention_rate": ret_clean_abst / max(1, len(ret)),
            "overall_entitlement_accuracy": sum(1 for r in arm_list if r.is_correct_entitlement) / max(1, len(arm_list)),
        }

    # Governance Telemetry on Arm 3
    arm3_actions = [
        {
            "call_id": r.call_id,
            "world_id": r.world_id,
            "condition": r.condition,
            "proposed_action": r.proposed_action,
            "action_confidence": r.action_confidence,
            "lineage_authority": r.lineage_authority,
            "gate_verdict": r.gate_verdict,
            "executed_action": r.executed_action,
        }
        for r in arm3
    ]

    # Replay Canary Determinism
    replay_matches = 0
    call_map = {r.call_id: r for r in results}
    for c in canary_results:
        # Match against manifest's target call
        # Call ID format CALL_REV_{wid}_{cond}_{arm}
        target_id = c.call_id.replace("CALL_CANARY_", "").split("_", 1)[1]  # strip index
        target = next((r for r in results if r.call_id == target_id), None)
        if target and target.raw_response == c.raw_response:
            replay_matches += 1

    summary = {
        "experiment": "Exploration Round 5 Stage 5C: Neural Revision Bridge (Live 32-Call Assay)",
        "model_name": model_name,
        "model_digest": model_digest,
        "database_path": str(db_path),
        "total_calls": len(results),
        "total_execution_time_seconds": t_total,
        "acquisition_phase": {
            "total_calls": len(acq_results),
            "citations_captured": {r.world_id: r.cited_facts for r in acq_results},
        },
        "revision_phase_arm_comparison": {
            "arm1_raw_neural": arm_metrics(arm1),
            "arm2_naive_reported": arm_metrics(arm2),
            "arm3_gene_kernel": arm_metrics(arm3),
        },
        "governance_action_telemetry_arm3": arm3_actions,
        "replay_canary_determinism": {
            "canary_calls": len(canary_results),
            "exact_raw_matches": replay_matches,
            "determinism_rate": replay_matches / max(1, len(canary_results)),
        },
    }

    summary_path.parent.mkdir(exist_ok=True, parents=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("================================================================================")
    print("                     STAGE 5C FACTORIAL REVISION SUMMARY                        ")
    print("================================================================================")
    print(f"Arm 1 (Raw Neural):      Entitlement Acc: {summary['revision_phase_arm_comparison']['arm1_raw_neural']['overall_entitlement_accuracy'] * 100:.1f}% | Degraded Active: {summary['revision_phase_arm_comparison']['arm1_raw_neural']['degraded_active_rate'] * 100:.1f}%")
    print(f"Arm 2 (Naive Reported):  Entitlement Acc: {summary['revision_phase_arm_comparison']['arm2_naive_reported']['overall_entitlement_accuracy'] * 100:.1f}% | Degraded Active: {summary['revision_phase_arm_comparison']['arm2_naive_reported']['degraded_active_rate'] * 100:.1f}%")
    print(f"Arm 3 (GENE Kernel):     Entitlement Acc: {summary['revision_phase_arm_comparison']['arm3_gene_kernel']['overall_entitlement_accuracy'] * 100:.1f}% | Degraded Active: {summary['revision_phase_arm_comparison']['arm3_gene_kernel']['degraded_active_rate'] * 100:.1f}%")
    print(f"Replay Stability:        {summary['replay_canary_determinism']['exact_raw_matches']} / {summary['replay_canary_determinism']['canary_calls']} Exact Prompt Matches ({summary['replay_canary_determinism']['determinism_rate'] * 100:.1f}%)")
    print("================================================================================\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Run Stage 5C Live Model Revision Assay.")
    parser.add_argument("--db-path", type=str, default="data/exploration_round5_stage5c_results.db")
    parser.add_argument("--manifest-path", type=str, default="data/exploration_round5_stage5c_manifest.json")
    parser.add_argument("--summary-path", type=str, default="data/exploration_round5_stage5c_summary.json")
    parser.add_argument("--model", type=str, default="gemma3:12b")
    parser.add_argument("--tau-gate", type=float, default=0.5)

    args = parser.parse_args()
    run_stage5c(
        db_path=Path(args.db_path),
        manifest_path=Path(args.manifest_path),
        summary_path=Path(args.summary_path),
        model_name=args.model,
        tau_gate=args.tau_gate,
    )


if __name__ == "__main__":
    main()
