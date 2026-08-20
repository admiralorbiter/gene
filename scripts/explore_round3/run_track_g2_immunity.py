"""Track G2: Clean Non-Destructive Support Immunity Runner.

Evaluates support-aware governance vs naive lineage quarantine under real policy-filtered
retrieval contexts across independent and shared-root geometries (5 arms x 2 stations x 2 reps = 20 calls).
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd()))

import json
from typing import Any

from gene.experiments.exploration_harness import ExplorationHarness
from gene.ollama_client import CallSpec, OllamaClient


def apply_governance_retrieval(
    station: str,
    geometry: str,
    policy_name: str,
    revoked_entities: set[str],
) -> tuple[list[str], str]:
    """Deterministic governance filter: applies policy over DAG to produce retrieved memories."""
    # Define atomic premises in the world
    if geometry == "independent":
        # Path 1: Nerin (mgr) -> S1
        # Path 2: Vael (sector lead) -> S2
        premises_by_path = {
            "path_1": [f"- MEM_01: Nerin is manager of {station}.", "- MEM_02: Nerin directly reports to S1."],
            "path_2": [f"- MEM_03: Vael is sector lead of {station}.", "- MEM_04: Vael directly reports to S2."],
        }
        authorities_by_path = {
            "path_1": "S1",
            "path_2": "S2",
        }
    elif geometry == "shared":
        # Path 1: Nerin (mgr) -> S1
        # Path 2: Vael (sector lead) -> S1
        premises_by_path = {
            "path_1": [f"- MEM_01: Nerin is manager of {station}.", "- MEM_02: Nerin directly reports to S1."],
            "path_2": [f"- MEM_03: Vael is sector lead of {station}.", "- MEM_04: Vael directly reports to S1."],
        }
        authorities_by_path = {
            "path_1": "S1",
            "path_2": "S1",
        }
    else:
        raise ValueError(f"Unknown geometry: {geometry}")

    # Baseline (no revocations)
    if not revoked_entities:
        all_mems = []
        for p_mems in premises_by_path.values():
            all_mems.extend(p_mems)
        return all_mems, "PROTO_X7"

    # Naive Lineage Quarantine Policy:
    # If ANY ancestor of the claim family is revoked, quarantine the ENTIRE claim family!
    if policy_name == "naive_lineage_quarantine":
        has_any_revocation = any(auth in revoked_entities for auth in authorities_by_path.values())
        if has_any_revocation:
            return ["- MEM_QUARANTINED: Evidence quarantined by lineage governance policy due to tainted ancestor."], "UNKNOWN"
        all_mems = []
        for p_mems in premises_by_path.values():
            all_mems.extend(p_mems)
        return all_mems, "PROTO_X7"

    # Support-Aware Kernel Policy:
    # Invalidate ONLY paths containing revoked entities; preserve and retrieve surviving paths!
    elif policy_name == "support_aware_kernel":
        surviving_mems = []
        surviving_paths = 0
        for p_name, auth in authorities_by_path.items():
            if auth not in revoked_entities:
                surviving_mems.extend(premises_by_path[p_name])
                surviving_paths += 1
        
        if surviving_paths > 0:
            return surviving_mems, "PROTO_X7"
        else:
            return ["- MEM_INACTIVATED: All minimal support paths invalidated under retracted premises."], "UNKNOWN"

    else:
        raise ValueError(f"Unknown policy: {policy_name}")


def build_track_g2_governance_prompt(
    station: str,
    arm: str,
) -> tuple[str, list[str], str]:
    """Construct retrieval context and dynamically matched rules via deterministic governance engine."""
    if arm in ["baseline_independent", "naive_lineage_quarantine", "support_aware_independent_preservation"]:
        geometry = "independent"
        rule2_auth = "S2"
    elif arm in ["baseline_shared", "support_aware_shared_collapse"]:
        geometry = "shared"
        rule2_auth = "S1"
    else:
        raise ValueError(f"Unknown arm: {arm}")

    rules = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, S1) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. sector_lead({station}, person) AND reports_to(person, {rule2_auth}) -> uses_protocol({station}, PROTO_X7)\n"
        "3. If evidence is missing, revoked, or insufficient, protocol is UNKNOWN."
    )

    if arm == "baseline_independent":
        memories, expected = apply_governance_retrieval(station, "independent", "support_aware_kernel", set())
    elif arm == "baseline_shared":
        memories, expected = apply_governance_retrieval(station, "shared", "support_aware_kernel", set())
    elif arm == "naive_lineage_quarantine":
        memories, expected = apply_governance_retrieval(station, "independent", "naive_lineage_quarantine", {"S1"})
    elif arm == "support_aware_independent_preservation":
        memories, expected = apply_governance_retrieval(station, "independent", "support_aware_kernel", {"S1"})
    elif arm == "support_aware_shared_collapse":
        memories, expected = apply_governance_retrieval(station, "shared", "support_aware_kernel", {"S1"})
    else:
        raise ValueError(f"Unknown arm: {arm}")

    prompt = (
        f"{rules}\n\n"
        "RETRIEVED EVIDENCE:\n"
        + "\n".join(memories)
        + f"\n\nQUESTION: What security protocol is authorized for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
    )

    forbidden = ["PROTO_X7", "PROTO_Q2"]
    return prompt, forbidden, expected


def run_track_g2_live(
    db_path: Path = Path("runs/explore_round3/track_g2_immunity.db"),
    max_calls: int = 20,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Execute Track G2 real governance policy panel (5 arms x 2 stations x 2 reps = 20 calls)."""
    harness = ExplorationHarness(
        db_path=db_path,
        track_name="track_g2_non_destructive_immunity",
        client=client,
        config={"max_calls": max_calls, "model": "gemma3:12b"},
    )

    stations = ["VELORA", "KESTREL"]
    arms = [
        "baseline_independent",
        "baseline_shared",
        "naive_lineage_quarantine",
        "support_aware_independent_preservation",
        "support_aware_shared_collapse",
    ]

    calls_spent = 0
    results = []

    for rep in range(1, 3):
        for st in stations:
            for arm in arms:
                if calls_spent >= max_calls:
                    break

                call_id = f"call_track_g2_{st.lower()}_{arm}_rep{rep}"
                prompt, forbidden, expected = build_track_g2_governance_prompt(st, arm)

                spec = CallSpec(
                    model_name="gemma3:12b",
                    system_prompt="You are a precise logical reasoning assistant. Return strictly valid JSON.",
                    user_prompt=prompt,
                    temperature=0.0,
                    seed=42 + rep,
                )

                rec = harness.execute_call(
                    call_id=call_id,
                    spec=spec,
                    forbidden_schema_leaks=forbidden,
                    metadata={
                        "station": st,
                        "arm": arm,
                        "rep": rep,
                        "expected": expected,
                    },
                    fail_on_lexical_leak=True,
                )

                is_correct = (rec.emitted_claim == expected)
                phenotype = "ACTIVE_PRESERVED" if rec.emitted_claim == "PROTO_X7" else "INACTIVE_QUARANTINED"

                # Contemporaneous evaluation logging
                harness.record_evaluation(
                    call_id=call_id,
                    canonical_status="BEHAVIORAL_EVALUATION",
                    local_status="TRUE" if is_correct else "FALSE",
                    dual_oracle_phenotype=phenotype,
                    is_contract_compliant=True,
                    metadata={
                        "arm": arm,
                        "expected": expected,
                        "emitted": rec.emitted_claim,
                        "is_correct": is_correct,
                    },
                )

                results.append({
                    "call_id": call_id,
                    "station": st,
                    "arm": arm,
                    "emitted": rec.emitted_claim,
                    "expected": expected,
                    "is_correct": is_correct,
                })
                print(f"[{calls_spent+1}/{max_calls}] {call_id} -> {rec.emitted_claim} (expected={expected}, correct={is_correct})", flush=True)
                calls_spent += 1

    return {"calls_spent": calls_spent, "results": results}


if __name__ == "__main__":
    db = Path("runs/explore_round3/track_g2_immunity.db")
    print("Running Track G2: Real Governance Policy Comparison (20 calls on gemma3:12b)...", flush=True)
    res = run_track_g2_live(db, max_calls=20)
    print(f"Completed {res['calls_spent']} live calls.", flush=True)
