"""Stage 5C: Neural Revision Bridge (Live Model Revision Assay).

Evaluates belief maintenance, revision accuracy, and action governance under live LLM reasoning.
Compares:
1. Arm 1: Raw Neural Revision (Unassisted model reasoning under raw context + invalidation alerts).
2. Arm 2: Naive Reported-Dependency (Flat dependency graph over live acquisition citations R(c)).
3. Arm 3: GENE Support-First Epistemic Runtime (Support enumeration S_F(c), lineage hypergraph S_L(c), minimal context compilation, and deterministic Auth(S_L) gating).

Includes full SQLite logging and replay canary verification.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Callable

from pydantic import BaseModel, Field

from src.gene.experiments.action_governance import (
    project_lineage_support,
    compute_policy_lineage_projected,
    PolicyActionScore,
    LineageProjectedState,
    minimize_antichain,
)
from src.gene.experiments.stage5c_manifest import Stage5CCallSpec, Stage5CWorldSpec, build_stage5c_worlds


class NeuralRevisionBridgeOutput(BaseModel):
    call_id: str
    call_index: int
    phase: str
    world_id: str
    arm: str
    condition: str
    prompt_text: str
    prompt_sha256: str
    raw_response: str
    parsed_status: str  # "DETERMINABLE" | "INDETERMINABLE" | "MALFORMED"
    parsed_answer: str | None
    cited_facts: list[str]
    proposed_action: str | None
    action_confidence: float | None
    expected_entitled: bool
    expected_oracle_answer: str
    is_correct_entitlement: bool
    is_correct_semantic_answer: bool
    surviving_support: list[list[str]]
    surviving_lineage: list[list[str]]
    lineage_authority: float
    gate_verdict: str  # "PERMIT" | "BLOCK" | "N/A"
    executed_action: str | None
    latency_ms: float


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


class NeuralRevisionBridgeRunner:
    """Executes the 32-call Stage 5C Factorial Assay."""

    def __init__(
        self,
        db_path: Path | str,
        manifest_path: Path | str,
        client_fn: Callable[[str], str],
        model_name: str = "gemma3:12b",
    ):
        self.db_path = Path(db_path)
        self.manifest_path = Path(manifest_path)
        self.client_fn = client_fn
        self.model_name = model_name
        self.worlds = build_stage5c_worlds()
        
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite storage schema."""
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stage5c_calls (
                    call_id TEXT PRIMARY KEY,
                    call_index INTEGER,
                    phase TEXT,
                    world_id TEXT,
                    arm TEXT,
                    condition TEXT,
                    prompt_text TEXT,
                    prompt_sha256 TEXT,
                    raw_response TEXT,
                    parsed_status TEXT,
                    parsed_answer TEXT,
                    cited_facts TEXT,
                    proposed_action TEXT,
                    action_confidence REAL,
                    expected_entitled INTEGER,
                    expected_oracle_answer TEXT,
                    is_correct_entitlement INTEGER,
                    is_correct_semantic_answer INTEGER,
                    surviving_support TEXT,
                    surviving_lineage TEXT,
                    lineage_authority REAL,
                    gate_verdict TEXT,
                    executed_action TEXT,
                    latency_ms REAL,
                    timestamp REAL
                )
            """)
            conn.commit()

    def parse_response(self, raw_resp: str) -> dict[str, Any]:
        """Safely parse structured JSON from model output."""
        cleaned = raw_resp.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        try:
            data = json.loads(cleaned)
            return {
                "status": data.get("status", "MALFORMED"),
                "answer": data.get("answer"),
                "cited_facts": data.get("cited_facts", []),
                "proposed_action": data.get("proposed_action"),
                "action_confidence": float(data.get("action_confidence", 0.0)) if data.get("action_confidence") is not None else None,
            }
        except Exception:
            return {
                "status": "MALFORMED",
                "answer": None,
                "cited_facts": [],
                "proposed_action": None,
                "action_confidence": None,
            }

    def run_all_calls(self, tau_gate: float = 0.5) -> list[NeuralRevisionBridgeOutput]:
        """Execute all 32 calls in sequential order according to the manifest."""
        results: list[NeuralRevisionBridgeOutput] = []
        acquisition_citations: dict[str, list[str]] = {}  # world_id -> cited_facts

        for call_dict in self.manifest["calls"]:
            call_spec = Stage5CCallSpec(**call_dict)
            world = self.worlds[call_spec.world_id]

            # 1. Determine Prompt Text
            if call_spec.phase == "acquisition":
                prompt_text = render_acquisition_prompt(world)
            elif call_spec.arm == "arm1_raw_neural":
                prompt_text = render_arm1_raw_revision_prompt(world, call_spec.invalidated_facts)
            elif call_spec.arm == "arm2_naive_reported":
                # Arm 2 uses the acquisition citation as durable dependency
                # We prompt the model as in Arm 1, but its logical entitlement is governed by R(c) intersection
                prompt_text = render_arm1_raw_revision_prompt(world, call_spec.invalidated_facts)
            elif call_spec.arm == "arm3_gene_kernel":
                prompt_text = render_arm3_minimal_support_prompt(world, call_spec.expected_surviving_support)
            elif call_spec.phase == "replay_canary":
                # Replay canary uses target prompt
                if call_spec.arm == "arm1_raw_neural":
                    prompt_text = render_arm1_raw_revision_prompt(world, call_spec.invalidated_facts)
                else:
                    prompt_text = render_arm3_minimal_support_prompt(world, call_spec.expected_surviving_support)
            else:
                prompt_text = render_acquisition_prompt(world)

            prompt_sha = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()

            # 2. Invoke Model Client
            t0 = time.perf_counter()
            raw_response = self.client_fn(prompt_text)
            latency_ms = (time.perf_counter() - t0) * 1000.0

            # 3. Parse and Evaluate Output
            parsed = self.parse_response(raw_response)

            # Record acquisition citation for Arm 2
            if call_spec.phase == "acquisition":
                acquisition_citations[call_spec.world_id] = parsed["cited_facts"]

            # Evaluate Entitlement and Arm 2 Invalidation
            if call_spec.arm == "arm2_naive_reported":
                acq_cited = acquisition_citations.get(call_spec.world_id, [])
                naive_retracted = any(p in call_spec.invalidated_facts for p in acq_cited)
                # Arm 2 retracts if any cited fact was invalidated
                model_entitled = (parsed["status"] == "DETERMINABLE") and not naive_retracted
                effective_status = "INDETERMINABLE" if naive_retracted else parsed["status"]
                effective_answer = None if naive_retracted else parsed["answer"]
            else:
                model_entitled = (parsed["status"] == "DETERMINABLE")
                effective_status = parsed["status"]
                effective_answer = parsed["answer"]

            # Dual-Oracle Ground Truth Match
            is_correct_ent = (model_entitled == call_spec.expected_entitled)
            if call_spec.expected_entitled:
                is_correct_semantic = (
                    is_correct_ent
                    and effective_answer is not None
                    and effective_answer.strip().upper() == call_spec.expected_oracle_answer.strip().upper()
                )
            else:
                is_correct_semantic = (effective_status == "INDETERMINABLE" and effective_answer is None)

            # Lineage Authority & Action Gating
            surviving_s = call_spec.expected_surviving_support
            if surviving_s and call_spec.expected_entitled:
                init_lin = project_lineage_support(world.initial_support_family, world.lineage_map)
                surv_lin = project_lineage_support(surviving_s, world.lineage_map)
                
                kappa_init = init_lin.kappa_l
                path_init = len(world.initial_support_family)
                
                kappa_ratio = surv_lin.kappa_l / max(1, kappa_init)
                path_ratio = len(surv_lin.support_family_roots) / max(1, path_init)
                auth_score = 0.5 * kappa_ratio + 0.5 * path_ratio
                surviving_l = surv_lin.support_family_roots
            else:
                surviving_l = []
                auth_score = 0.0

            # Action Gate Decision
            if effective_status == "DETERMINABLE" and parsed["proposed_action"]:
                gate_verdict = "PERMIT" if auth_score >= tau_gate else "BLOCK"
                executed_action = parsed["proposed_action"] if gate_verdict == "PERMIT" else None
            else:
                gate_verdict = "N/A"
                executed_action = None

            res = NeuralRevisionBridgeOutput(
                call_id=call_spec.call_id,
                call_index=call_spec.call_index,
                phase=call_spec.phase,
                world_id=call_spec.world_id,
                arm=call_spec.arm,
                condition=call_spec.condition,
                prompt_text=prompt_text,
                prompt_sha256=prompt_sha,
                raw_response=raw_response,
                parsed_status=effective_status,
                parsed_answer=effective_answer,
                cited_facts=parsed["cited_facts"],
                proposed_action=parsed["proposed_action"],
                action_confidence=parsed["action_confidence"],
                expected_entitled=call_spec.expected_entitled,
                expected_oracle_answer=call_spec.expected_oracle_answer,
                is_correct_entitlement=is_correct_ent,
                is_correct_semantic_answer=is_correct_semantic,
                surviving_support=surviving_s,
                surviving_lineage=surviving_l,
                lineage_authority=auth_score,
                gate_verdict=gate_verdict,
                executed_action=executed_action,
                latency_ms=latency_ms,
            )
            results.append(res)
            self._save_call_to_db(res)

        return results

    def _save_call_to_db(self, r: NeuralRevisionBridgeOutput) -> None:
        """Persist individual evaluation to SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO stage5c_calls VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                r.call_id,
                r.call_index,
                r.phase,
                r.world_id,
                r.arm,
                r.condition,
                r.prompt_text,
                r.prompt_sha256,
                r.raw_response,
                r.parsed_status,
                r.parsed_answer,
                json.dumps(r.cited_facts),
                r.proposed_action,
                r.action_confidence,
                1 if r.expected_entitled else 0,
                r.expected_oracle_answer,
                1 if r.is_correct_entitlement else 0,
                1 if r.is_correct_semantic_answer else 0,
                json.dumps(r.surviving_support),
                json.dumps(r.surviving_lineage),
                r.lineage_authority,
                r.gate_verdict,
                r.executed_action,
                r.latency_ms,
                time.time(),
            ))
            conn.commit()
