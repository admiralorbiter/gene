"""Stage 5C Execution Manifest Builder & Preregistered Assay Generator.

Constructs the machine-readable 32-call execution manifest for Stage 5C (Neural Revision Bridge).
Freezes:
1. 4 Acquisition calls (one per structural micro-world).
2. 24 Factorial Revision calls (4 worlds x 2 interventions x 3 arms).
3. 4 Replay Canaries.
4. Exact prompt structures, matched serialization grammar, and deterministic oracles.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field


class Stage5CWorldSpec(BaseModel):
    world_id: str
    topology_name: str
    description: str
    query_entity: str
    target_attribute: str
    ground_truth_answer: str
    facts: dict[str, str]  # fact_id -> natural language statement
    lineage_map: dict[str, str]  # fact_id -> root_id
    rules: list[str]
    initial_support_family: list[list[str]]
    initial_root_family: list[list[str]]
    degraded_intervention: list[str]  # premise IDs to invalidate
    retracted_intervention: list[str]  # premise IDs to invalidate


class Stage5CCallSpec(BaseModel):
    call_index: int  # 1 to 32
    call_id: str
    phase: str  # "acquisition", "revision", "replay_canary"
    world_id: str
    arm: str  # "acquisition", "arm1_raw_neural", "arm2_naive_reported", "arm3_gene_kernel"
    condition: str  # "baseline", "DEGRADED", "RETRACTED"
    invalidated_facts: list[str]
    expected_entitled: bool
    expected_surviving_support: list[list[str]]
    expected_surviving_lineage: list[list[str]]
    expected_oracle_answer: str
    prompt_template_version: str = "stage5c_v1"
    matched_serialization_grammar: str = "structured_json_evidence_block"
    replay_target_call_id: str | None = None


def build_stage5c_worlds() -> dict[str, Stage5CWorldSpec]:
    """Define the 4 structural micro-worlds with exact premises, rules, and interventions."""
    return {
        "W_IND": Stage5CWorldSpec(
            world_id="W_IND",
            topology_name="independent_alternatives",
            description="Two independent 2-premise derivation paths from distinct roots R1, R2.",
            query_entity="Station KESTREL",
            target_attribute="operating_protocol",
            ground_truth_answer="PROTOCOL_OMEGA",
            facts={
                "FACT_IND_A": "Station KESTREL is located in Sector ALPHA.",
                "FACT_IND_B": "Sector ALPHA operates under protocol Rule 1 producing PROTOCOL_OMEGA.",
                "FACT_IND_D": "Station KESTREL carries telemetry beacon BEACON_DELTA.",
                "FACT_IND_E": "Telemetry beacon BEACON_DELTA authorizes protocol Rule 2 producing PROTOCOL_OMEGA.",
            },
            lineage_map={
                "FACT_IND_A": "ROOT_R1",
                "FACT_IND_B": "ROOT_R1",
                "FACT_IND_D": "ROOT_R2",
                "FACT_IND_E": "ROOT_R2",
            },
            rules=[
                "Rule 1: IF (Station in Sector ALPHA) AND (Sector ALPHA operates under Rule 1) THEN Protocol is PROTOCOL_OMEGA",
                "Rule 2: IF (Station carries BEACON_DELTA) AND (BEACON_DELTA authorizes Rule 2) THEN Protocol is PROTOCOL_OMEGA",
            ],
            initial_support_family=[["FACT_IND_A", "FACT_IND_B"], ["FACT_IND_D", "FACT_IND_E"]],
            initial_root_family=[["ROOT_R1"], ["ROOT_R2"]],
            degraded_intervention=["FACT_IND_D"],
            retracted_intervention=["FACT_IND_A", "FACT_IND_D"],
        ),
        "W_SHP": Stage5CWorldSpec(
            world_id="W_SHP",
            topology_name="shared_premise_alternatives",
            description="Two alternative derivation paths sharing premise Fact_A (kappa-blindness boundary).",
            query_entity="Station ORION",
            target_attribute="clearance_tier",
            ground_truth_answer="TIER_SIGMA",
            facts={
                "FACT_SHP_A": "Station ORION is certified under Central Division.",
                "FACT_SHP_B": "Central Division with secondary channel BLUE assigns TIER_SIGMA.",
                "FACT_SHP_D": "Central Division with secondary channel GOLD assigns TIER_SIGMA.",
            },
            lineage_map={
                "FACT_SHP_A": "ROOT_R1",
                "FACT_SHP_B": "ROOT_R2",
                "FACT_SHP_D": "ROOT_R3",
            },
            rules=[
                "Rule 1: IF (Central Division) AND (Secondary Channel BLUE) THEN Tier is TIER_SIGMA",
                "Rule 2: IF (Central Division) AND (Secondary Channel GOLD) THEN Tier is TIER_SIGMA",
            ],
            initial_support_family=[["FACT_SHP_A", "FACT_SHP_B"], ["FACT_SHP_A", "FACT_SHP_D"]],
            initial_root_family=[["ROOT_R1", "ROOT_R2"], ["ROOT_R1", "ROOT_R3"]],
            degraded_intervention=["FACT_SHP_B"],
            retracted_intervention=["FACT_SHP_A"],
        ),
        "W_SHO": Stage5CWorldSpec(
            world_id="W_SHO",
            topology_name="shared_origin_ancestry",
            description="Two alternative premise paths whose premises share common conjunctive roots R1, R2.",
            query_entity="Station VANGUARD",
            target_attribute="access_code",
            ground_truth_answer="CODE_EPSILON",
            facts={
                "FACT_SHO_A": "Station VANGUARD connects to Relay NORTH.",
                "FACT_SHO_B": "Relay NORTH with Port 1 verifies CODE_EPSILON.",
                "FACT_SHO_D": "Station VANGUARD connects to Relay SOUTH.",
                "FACT_SHO_E": "Relay SOUTH with Port 2 verifies CODE_EPSILON.",
            },
            lineage_map={
                "FACT_SHO_A": "ROOT_R1",
                "FACT_SHO_D": "ROOT_R1",
                "FACT_SHO_B": "ROOT_R2",
                "FACT_SHO_E": "ROOT_R2",
            },
            rules=[
                "Rule 1: IF (Relay NORTH) AND (Port 1 verified) THEN Code is CODE_EPSILON",
                "Rule 2: IF (Relay SOUTH) AND (Port 2 verified) THEN Code is CODE_EPSILON",
            ],
            initial_support_family=[["FACT_SHO_A", "FACT_SHO_B"], ["FACT_SHO_D", "FACT_SHO_E"]],
            initial_root_family=[["ROOT_R1", "ROOT_R2"]],
            degraded_intervention=["FACT_SHO_D"],
            retracted_intervention=["FACT_SHO_A", "FACT_SHO_D"],
        ),
        "W_REC": Stage5CWorldSpec(
            world_id="W_REC",
            topology_name="recombinant_tri_path",
            description="Three overlapping alternative derivation paths across four roots.",
            query_entity="Station DRAKE",
            target_attribute="transit_lane",
            ground_truth_answer="LANE_THETA",
            facts={
                "FACT_REC_A": "Station DRAKE aligns with Beacon 1.",
                "FACT_REC_B": "Beacon 1 with Corridor X assigns LANE_THETA.",
                "FACT_REC_C": "Corridor X with Gate 3 assigns LANE_THETA.",
                "FACT_REC_D": "Gate 3 with Channel 4 assigns LANE_THETA.",
            },
            lineage_map={
                "FACT_REC_A": "ROOT_R1",
                "FACT_REC_B": "ROOT_R2",
                "FACT_REC_C": "ROOT_R3",
                "FACT_REC_D": "ROOT_R4",
            },
            rules=[
                "Rule 1: IF (Beacon 1) AND (Corridor X) THEN Lane is LANE_THETA",
                "Rule 2: IF (Corridor X) AND (Gate 3) THEN Lane is LANE_THETA",
                "Rule 3: IF (Gate 3) AND (Channel 4) THEN Lane is LANE_THETA",
            ],
            initial_support_family=[
                ["FACT_REC_A", "FACT_REC_B"],
                ["FACT_REC_B", "FACT_REC_C"],
                ["FACT_REC_C", "FACT_REC_D"],
            ],
            initial_root_family=[
                ["ROOT_R1", "ROOT_R2"],
                ["ROOT_R2", "ROOT_R3"],
                ["ROOT_R3", "ROOT_R4"],
            ],
            degraded_intervention=["FACT_REC_A", "FACT_REC_B"],
            retracted_intervention=["FACT_REC_B", "FACT_REC_C"],
        ),
    }


def generate_stage5c_manifest() -> dict[str, Any]:
    """Assemble all 32 calls with fixed parameters, matched grammar, and expected oracles."""
    worlds = build_stage5c_worlds()
    calls: list[Stage5CCallSpec] = []
    idx = 1

    # Phase 1: 4 Acquisition Calls
    for wid in ["W_IND", "W_SHP", "W_SHO", "W_REC"]:
        w = worlds[wid]
        calls.append(
            Stage5CCallSpec(
                call_index=idx,
                call_id=f"CALL_ACQ_{wid}",
                phase="acquisition",
                world_id=wid,
                arm="acquisition",
                condition="baseline",
                invalidated_facts=[],
                expected_entitled=True,
                expected_surviving_support=w.initial_support_family,
                expected_surviving_lineage=w.initial_root_family,
                expected_oracle_answer=w.ground_truth_answer,
            )
        )
        idx += 1

    # Phase 2: 24 Factorial Revision Calls (4 worlds x 2 interventions x 3 arms)
    arms = ["arm1_raw_neural", "arm2_naive_reported", "arm3_gene_kernel"]
    conditions = ["DEGRADED", "RETRACTED"]

    for wid in ["W_IND", "W_SHP", "W_SHO", "W_REC"]:
        w = worlds[wid]
        for cond in conditions:
            inval = w.degraded_intervention if cond == "DEGRADED" else w.retracted_intervention
            is_entitled = (cond == "DEGRADED")

            # Compute surviving support
            surviving_s = [
                s for s in w.initial_support_family if not any(p in inval for p in s)
            ]
            surviving_l = [
                r for r in w.initial_root_family
                if all(
                    any(p in w.facts and p not in inval for p in path)
                    for path in w.initial_support_family
                )
            ] if is_entitled else []

            expected_ans = w.ground_truth_answer if is_entitled else "UNKNOWN"

            for arm in arms:
                calls.append(
                    Stage5CCallSpec(
                        call_index=idx,
                        call_id=f"CALL_REV_{wid}_{cond}_{arm}",
                        phase="revision",
                        world_id=wid,
                        arm=arm,
                        condition=cond,
                        invalidated_facts=inval,
                        expected_entitled=is_entitled,
                        expected_surviving_support=surviving_s,
                        expected_surviving_lineage=surviving_l,
                        expected_oracle_answer=expected_ans,
                    )
                )
                idx += 1

    # Phase 3: 4 Replay Canaries (Test replay stability on identical prompt hashes)
    canary_targets = [
        ("W_IND", "DEGRADED", "arm1_raw_neural"),
        ("W_IND", "RETRACTED", "arm3_gene_kernel"),
        ("W_REC", "DEGRADED", "arm3_gene_kernel"),
        ("W_REC", "RETRACTED", "arm1_raw_neural"),
    ]
    for wid, cond, arm in canary_targets:
        target_id = f"CALL_REV_{wid}_{cond}_{arm}"
        w = worlds[wid]
        inval = w.degraded_intervention if cond == "DEGRADED" else w.retracted_intervention
        is_entitled = (cond == "DEGRADED")
        surviving_s = [
            s for s in w.initial_support_family if not any(p in inval for p in s)
        ]
        calls.append(
            Stage5CCallSpec(
                call_index=idx,
                call_id=f"CALL_CANARY_{idx}_{wid}_{cond}_{arm}",
                phase="replay_canary",
                world_id=wid,
                arm=arm,
                condition=cond,
                invalidated_facts=inval,
                expected_entitled=is_entitled,
                expected_surviving_support=surviving_s,
                expected_surviving_lineage=[],
                expected_oracle_answer=w.ground_truth_answer if is_entitled else "UNKNOWN",
                replay_target_call_id=target_id,
            )
        )
        idx += 1

    manifest = {
        "manifest_version": "1.0.0",
        "experiment": "Exploration Round 5 Stage 5C: Neural Revision Bridge (32-Call Live Assay)",
        "target_model": "gemma3:12b",
        "execution_parameters": {
            "temperature": 0.0,
            "seed": 42,
            "total_calls": 32,
            "acquisition_calls": 4,
            "factorial_revision_calls": 24,
            "replay_canaries": 4,
        },
        "worlds": {wid: w.model_dump() for wid, w in worlds.items()},
        "calls": [c.model_dump() for c in calls],
    }

    # Write to data/exploration_round5_stage5c_manifest.json
    out_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "exploration_round5_stage5c_manifest.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    m = generate_stage5c_manifest()
    print(f"Stage 5C Execution Manifest successfully generated with {len(m['calls'])} calls.")
