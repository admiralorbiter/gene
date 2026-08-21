"""Stage 5C Execution Manifest Builder & Preregistered Assay Generator.

Constructs the machine-readable 32-call execution manifest for Stage 5C (Neural Revision Bridge).
Freezes:
1. 4 Acquisition calls (one per structural micro-world).
2. 24 Factorial Revision calls (4 worlds x 2 interventions x 3 arms).
3. 4 Replay Canaries.
4. Exact prompt structures, matched serialization grammar, and deterministic oracles.
5. Canonical request payload SHA-256 hashes and pinned model digest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from src.gene.experiments.action_governance import project_lineage_support, minimize_antichain

PINNED_STAGE5C_MODEL = "gemma3:12b"
PINNED_STAGE5C_DIGEST = "f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a"
CANONICAL_SYSTEM_PROMPT = "You are an epistemic reasoning engine. You must output valid JSON."


class Stage5CRule(BaseModel):
    rule_id: str
    antecedent_fact_ids: list[str]
    consequent_attribute: str
    consequent_value: str
    nl_text: str


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
    rule_specs: list[Stage5CRule] = Field(default_factory=list)
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
    system_prompt: str = CANONICAL_SYSTEM_PROMPT
    user_prompt: str
    user_prompt_sha256: str
    request_payload_sha256: str
    expected_entitled: bool
    expected_surviving_support: list[list[str]]
    expected_surviving_lineage: list[list[str]]
    expected_oracle_answer: str
    prompt_template_version: str = "stage5c_v1"
    matched_serialization_grammar: str = "structured_json_evidence_block"
    replay_target_call_id: str | None = None


def render_acquisition_prompt(world: Stage5CWorldSpec) -> str:
    """Render the structured prompt for Phase 1 Acquisition."""
    facts_block = "\n".join([f"- [{fid}]: {text}" for fid, text in sorted(world.facts.items())])
    rules_block = "\n".join([f"- {r}" for r in world.rules])

    return f"""### SYSTEM INSTRUCTION
You are an epistemic reasoning engine. You must answer questions using ONLY the provided verified facts and inference rules.
If the facts and rules are sufficient to deduce a definite answer, status must be "DETERMINABLE" and answer must match the deduced value.
If the facts and rules are insufficient, broken, or ambiguous, status must be "INDETERMINABLE" and answer must be null.

### VERIFIED EVIDENCE
{facts_block}

### INFERENCE RULES
{rules_block}

### QUERY
Target: {world.query_entity}
Attribute: {world.target_attribute}

### ACTION GOVERNANCE POLICY
If the answer is determinable, propose an appropriate operational action (e.g. "AUTHORIZE_ENTRY", "EXECUTE_DISPATCH", "DEPLOY_PROTOCOL") and specify your action confidence in [0.0, 1.0].

### OUTPUT FORMAT
You must respond with ONLY valid JSON matching this schema:
```json
{{
  "status": "DETERMINABLE" | "INDETERMINABLE",
  "answer": "<STRING>" | null,
  "cited_facts": ["<FACT_ID>", ...],
  "proposed_action": "<ACTION_NAME>" | null,
  "action_confidence": 0.95
}}
```"""


def render_arm1_raw_revision_prompt(world: Stage5CWorldSpec, invalidated_facts: list[str]) -> str:
    """Render the prompt for Arm 1 (Raw Neural Revision) with explicit retraction notices."""
    facts_block = "\n".join([f"- [{fid}]: {text}" for fid, text in sorted(world.facts.items())])
    rules_block = "\n".join([f"- {r}" for r in world.rules])
    inval_block = "\n".join([f"- RETRACTED / INVALID: [{fid}]" for fid in sorted(invalidated_facts)])

    return f"""### SYSTEM INSTRUCTION
You are an epistemic reasoning engine. You must answer questions using ONLY the provided verified facts and inference rules.
CRITICAL: Some previously known facts have been RETRACTED and are no longer valid. You MUST NOT use or cite any retracted facts.
If the remaining active facts and rules are sufficient to deduce a definite answer, status must be "DETERMINABLE".
If the remaining active facts are insufficient or all derivation paths are broken, status must be "INDETERMINABLE" and answer must be null.

### PREVIOUSLY OBSERVED EVIDENCE
{facts_block}

### [SYSTEM ALERT] RETRACTION NOTICE
The following facts have been formally invalidated and revoked:
{inval_block}

### INFERENCE RULES
{rules_block}

### QUERY
Target: {world.query_entity}
Attribute: {world.target_attribute}

### ACTION GOVERNANCE POLICY
If the answer is determinable under active valid facts, propose an operational action and state your confidence.

### OUTPUT FORMAT
You must respond with ONLY valid JSON matching this schema:
```json
{{
  "status": "DETERMINABLE" | "INDETERMINABLE",
  "answer": "<STRING>" | null,
  "cited_facts": ["<FACT_ID>", ...],
  "proposed_action": "<ACTION_NAME>" | null,
  "action_confidence": 0.95
}}
```"""


def render_arm3_minimal_support_prompt(world: Stage5CWorldSpec, surviving_support: list[list[str]]) -> str:
    """Render the prompt for Arm 3 (GENE Kernel) containing only surviving minimal support."""
    active_fact_ids = sorted(list({fid for s in surviving_support for fid in s}))
    if not active_fact_ids:
        facts_block = "No active valid facts remain in context."
    else:
        facts_block = "\n".join([f"- [{fid}]: {world.facts[fid]}" for fid in active_fact_ids])
    
    rules_block = "\n".join([f"- {r}" for r in world.rules])

    return f"""### SYSTEM INSTRUCTION
You are an epistemic reasoning engine. You must answer questions using ONLY the provided verified facts and inference rules.
If the facts and rules are sufficient to deduce a definite answer, status must be "DETERMINABLE" and answer must match the deduced value.
If the facts and rules are insufficient, status must be "INDETERMINABLE" and answer must be null.

### COMPILED ACTIVE EVIDENCE
{facts_block}

### INFERENCE RULES
{rules_block}

### QUERY
Target: {world.query_entity}
Attribute: {world.target_attribute}

### ACTION GOVERNANCE POLICY
If the answer is determinable, propose an operational action and specify your action confidence in [0.0, 1.0].

### OUTPUT FORMAT
You must respond with ONLY valid JSON matching this schema:
```json
{{
  "status": "DETERMINABLE" | "INDETERMINABLE",
  "answer": "<STRING>" | null,
  "cited_facts": ["<FACT_ID>", ...],
  "proposed_action": "<ACTION_NAME>" | null,
  "action_confidence": 0.95
}}
```"""


def enumerate_entitling_supports(world: Stage5CWorldSpec, active_facts: set[str]) -> list[list[str]]:
    """Perform first-order backward-chaining support enumeration over active facts and rules."""
    valid_paths: list[list[str]] = []
    for rule in world.rule_specs:
        if all(ant in active_facts for ant in rule.antecedent_fact_ids):
            valid_paths.append(sorted(rule.antecedent_fact_ids))

    # Minimize into an antichain
    unique_sets = [set(p) for p in valid_paths]
    min_sets = minimize_antichain(unique_sets)
    return sorted([sorted(list(s)) for s in min_sets])


def compute_request_payload_hash(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.0,
    seed: int = 42,
    fmt: str = "json",
) -> str:
    """Compute canonical cryptographic SHA-256 hash of the complete API request payload."""
    canonical_dict = {
        "model": model_name,
        "system": system_prompt,
        "user": user_prompt,
        "temperature": temperature,
        "seed": seed,
        "format": fmt,
    }
    encoded = json.dumps(canonical_dict, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
            rule_specs=[
                Stage5CRule(
                    rule_id="RULE_IND_1",
                    antecedent_fact_ids=["FACT_IND_A", "FACT_IND_B"],
                    consequent_attribute="operating_protocol",
                    consequent_value="PROTOCOL_OMEGA",
                    nl_text="Rule 1",
                ),
                Stage5CRule(
                    rule_id="RULE_IND_2",
                    antecedent_fact_ids=["FACT_IND_D", "FACT_IND_E"],
                    consequent_attribute="operating_protocol",
                    consequent_value="PROTOCOL_OMEGA",
                    nl_text="Rule 2",
                ),
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
            rule_specs=[
                Stage5CRule(
                    rule_id="RULE_SHP_1",
                    antecedent_fact_ids=["FACT_SHP_A", "FACT_SHP_B"],
                    consequent_attribute="clearance_tier",
                    consequent_value="TIER_SIGMA",
                    nl_text="Rule 1",
                ),
                Stage5CRule(
                    rule_id="RULE_SHP_2",
                    antecedent_fact_ids=["FACT_SHP_A", "FACT_SHP_D"],
                    consequent_attribute="clearance_tier",
                    consequent_value="TIER_SIGMA",
                    nl_text="Rule 2",
                ),
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
            rule_specs=[
                Stage5CRule(
                    rule_id="RULE_SHO_1",
                    antecedent_fact_ids=["FACT_SHO_A", "FACT_SHO_B"],
                    consequent_attribute="access_code",
                    consequent_value="CODE_EPSILON",
                    nl_text="Rule 1",
                ),
                Stage5CRule(
                    rule_id="RULE_SHO_2",
                    antecedent_fact_ids=["FACT_SHO_D", "FACT_SHO_E"],
                    consequent_attribute="access_code",
                    consequent_value="CODE_EPSILON",
                    nl_text="Rule 2",
                ),
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
            rule_specs=[
                Stage5CRule(
                    rule_id="RULE_REC_1",
                    antecedent_fact_ids=["FACT_REC_A", "FACT_REC_B"],
                    consequent_attribute="transit_lane",
                    consequent_value="LANE_THETA",
                    nl_text="Rule 1",
                ),
                Stage5CRule(
                    rule_id="RULE_REC_2",
                    antecedent_fact_ids=["FACT_REC_B", "FACT_REC_C"],
                    consequent_attribute="transit_lane",
                    consequent_value="LANE_THETA",
                    nl_text="Rule 2",
                ),
                Stage5CRule(
                    rule_id="RULE_REC_3",
                    antecedent_fact_ids=["FACT_REC_C", "FACT_REC_D"],
                    consequent_attribute="transit_lane",
                    consequent_value="LANE_THETA",
                    nl_text="Rule 3",
                ),
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


def generate_stage5c_manifest(write: bool = True) -> dict[str, Any]:
    """Assemble all 32 calls with fixed parameters, matched grammar, and expected oracles."""
    worlds = build_stage5c_worlds()
    calls: list[Stage5CCallSpec] = []
    idx = 1

    # Phase 1: 4 Acquisition Calls
    for wid in ["W_IND", "W_SHP", "W_SHO", "W_REC"]:
        w = worlds[wid]
        prompt = render_acquisition_prompt(w)
        p_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        req_sha = compute_request_payload_hash(
            model_name=PINNED_STAGE5C_MODEL,
            system_prompt=CANONICAL_SYSTEM_PROMPT,
            user_prompt=prompt,
        )
        init_lin = project_lineage_support(w.initial_support_family, w.lineage_map).support_family_roots

        calls.append(
            Stage5CCallSpec(
                call_index=idx,
                call_id=f"CALL_ACQ_{wid}",
                phase="acquisition",
                world_id=wid,
                arm="acquisition",
                condition="baseline",
                invalidated_facts=[],
                system_prompt=CANONICAL_SYSTEM_PROMPT,
                user_prompt=prompt,
                user_prompt_sha256=p_sha,
                request_payload_sha256=req_sha,
                expected_entitled=True,
                expected_surviving_support=w.initial_support_family,
                expected_surviving_lineage=init_lin,
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

            # Compute surviving support from rules and active facts
            active_facts = set(w.facts.keys()) - set(inval)
            surviving_s = enumerate_entitling_supports(w, active_facts)
            surviving_l = (
                project_lineage_support(surviving_s, w.lineage_map).support_family_roots
                if is_entitled and surviving_s
                else []
            )

            expected_ans = w.ground_truth_answer if is_entitled else "UNKNOWN"

            for arm in arms:
                if arm in ["arm1_raw_neural", "arm2_naive_reported"]:
                    prompt = render_arm1_raw_revision_prompt(w, inval)
                else:
                    prompt = render_arm3_minimal_support_prompt(w, surviving_s)

                p_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
                req_sha = compute_request_payload_hash(
                    model_name=PINNED_STAGE5C_MODEL,
                    system_prompt=CANONICAL_SYSTEM_PROMPT,
                    user_prompt=prompt,
                )

                calls.append(
                    Stage5CCallSpec(
                        call_index=idx,
                        call_id=f"CALL_REV_{wid}_{cond}_{arm}",
                        phase="revision",
                        world_id=wid,
                        arm=arm,
                        condition=cond,
                        invalidated_facts=inval,
                        system_prompt=CANONICAL_SYSTEM_PROMPT,
                        user_prompt=prompt,
                        user_prompt_sha256=p_sha,
                        request_payload_sha256=req_sha,
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
        
        active_facts = set(w.facts.keys()) - set(inval)
        surviving_s = enumerate_entitling_supports(w, active_facts)
        surviving_l = (
            project_lineage_support(surviving_s, w.lineage_map).support_family_roots
            if is_entitled and surviving_s
            else []
        )

        if arm in ["arm1_raw_neural", "arm2_naive_reported"]:
            prompt = render_arm1_raw_revision_prompt(w, inval)
        else:
            prompt = render_arm3_minimal_support_prompt(w, surviving_s)

        p_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        req_sha = compute_request_payload_hash(
            model_name=PINNED_STAGE5C_MODEL,
            system_prompt=CANONICAL_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        calls.append(
            Stage5CCallSpec(
                call_index=idx,
                call_id=f"CALL_CANARY_{idx}_{wid}_{cond}_{arm}",
                phase="replay_canary",
                world_id=wid,
                arm=arm,
                condition=cond,
                invalidated_facts=inval,
                system_prompt=CANONICAL_SYSTEM_PROMPT,
                user_prompt=prompt,
                user_prompt_sha256=p_sha,
                request_payload_sha256=req_sha,
                expected_entitled=is_entitled,
                expected_surviving_support=surviving_s,
                expected_surviving_lineage=surviving_l,
                expected_oracle_answer=w.ground_truth_answer if is_entitled else "UNKNOWN",
                replay_target_call_id=target_id,
            )
        )
        idx += 1

    manifest = {
        "manifest_version": "2.0.0",
        "experiment": "Exploration Round 5 Stage 5C: Neural Revision Bridge (32-Call Live Assay)",
        "target_model": PINNED_STAGE5C_MODEL,
        "pinned_model_digest": PINNED_STAGE5C_DIGEST,
        "canonical_system_prompt": CANONICAL_SYSTEM_PROMPT,
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

    if write:
        out_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "exploration_round5_stage5c_manifest.json"
        out_path.parent.mkdir(exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    m = generate_stage5c_manifest(write=True)
    print(f"Stage 5C Execution Manifest v2.0.0 successfully generated with {len(m['calls'])} calls.")
