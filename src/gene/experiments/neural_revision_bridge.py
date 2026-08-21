"""Stage 5C: Neural Revision Bridge (Hardened Live Model Revision Assay).

Evaluates belief maintenance, revision accuracy, and action governance under live LLM reasoning.
Compares:
1. Arm 1: Raw Neural Revision (Unassisted model reasoning under raw context + invalidation alerts).
2. Arm 2: Naive Reported-Dependency (Flat dependency graph over live acquisition citations R(c)).
3. Arm 3: GENE Support-First Epistemic Runtime (Formal support enumeration S_F(c, I), lineage hypergraph S_L(c, I), minimal context compilation, and deterministic Auth(S_L) gating).

Enforces:
- Strict request-payload hash freezing.
- Pinned model digest validation.
- First-order backward chaining support enumeration in Arm 3 with oracle equality preflight check.
- Explicit model-vs-runtime output separation.
- Acquisition validity tagging.
- Exact replay canary matching via replay_target_call_id.
- Append-only run/call persistence.
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
    minimize_antichain,
)
from src.gene.experiments.stage5c_manifest import (
    Stage5CCallSpec,
    Stage5CWorldSpec,
    build_stage5c_worlds,
    render_acquisition_prompt,
    render_arm1_raw_revision_prompt,
    render_arm3_minimal_support_prompt,
    enumerate_entitling_supports,
    compute_request_payload_hash,
    PINNED_STAGE5C_MODEL,
    PINNED_STAGE5C_DIGEST,
    CANONICAL_SYSTEM_PROMPT,
)


class NeuralRevisionBridgeOutput(BaseModel):
    call_id: str
    call_index: int
    phase: str
    world_id: str
    arm: str
    condition: str
    prompt_text: str
    prompt_sha256: str
    request_payload_sha256: str
    raw_response: str
    
    # Model Direct Outputs
    status_model: str  # "DETERMINABLE" | "INDETERMINABLE" | "MALFORMED"
    answer_model: str | None
    cited_facts_model: list[str]
    proposed_action_model: str | None
    action_confidence_model: float | None

    # Runtime Effective Outputs (post-policy)
    status_runtime: str
    answer_runtime: str | None
    proposed_action_runtime: str | None
    action_confidence_runtime: float | None

    # Acquisition & Policy Metadata
    acquisition_valid: bool
    expected_entitled: bool
    expected_oracle_answer: str
    is_correct_entitlement: bool
    is_correct_semantic_answer: bool
    computed_surviving_support: list[list[str]]
    computed_surviving_lineage: list[list[str]]
    lineage_authority: float
    gate_verdict: str  # "PERMIT" | "BLOCK" | "N/A"
    executed_action: str | None
    latency_ms: float
    replay_target_call_id: str | None = None
    is_replay_exact_match: bool | None = None


class NeuralRevisionBridgeRunner:
    """Executes the 32-call Stage 5C Factorial Assay with strict invariants."""

    def __init__(
        self,
        db_path: Path | str,
        manifest_path: Path | str,
        client_fn: Callable[[str, str], str],  # (system_prompt, user_prompt) -> raw_response
        model_name: str = PINNED_STAGE5C_MODEL,
        model_digest: str = PINNED_STAGE5C_DIGEST,
        ollama_version: str = "unknown",
        git_commit: str = "unknown",
        fail_if_db_exists: bool = False,
    ):
        self.db_path = Path(db_path)
        self.manifest_path = Path(manifest_path)
        self.client_fn = client_fn
        self.model_name = model_name
        self.model_digest = model_digest
        self.ollama_version = ollama_version
        self.git_commit = git_commit
        self.worlds = build_stage5c_worlds()

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

        manifest_content = self.manifest_path.read_bytes()
        self.manifest_sha256 = hashlib.sha256(manifest_content).hexdigest()

        # Pin Validation
        expected_digest = self.manifest.get("pinned_model_digest", PINNED_STAGE5C_DIGEST)
        if self.model_digest != expected_digest:
            raise ValueError(
                f"Model digest mismatch! Pinned: {expected_digest}, Actual: {self.model_digest}. "
                "Halting execution to preserve experimental integrity."
            )

        self._init_db(fail_if_db_exists)

    def _init_db(self, fail_if_exists: bool) -> None:
        """Initialize SQLite storage schema with strict append-only tables."""
        if fail_if_exists and self.db_path.exists():
            raise FileExistsError(f"Execution DB {self.db_path} already exists. Append-only policy requires fresh DB.")

        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stage5c_runs (
                    run_id TEXT PRIMARY KEY,
                    git_commit TEXT,
                    manifest_sha256 TEXT,
                    model_name TEXT,
                    model_digest TEXT,
                    ollama_version TEXT,
                    timestamp REAL
                )
            """)
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
                    request_payload_sha256 TEXT,
                    raw_response TEXT,
                    status_model TEXT,
                    answer_model TEXT,
                    cited_facts_model TEXT,
                    proposed_action_model TEXT,
                    action_confidence_model REAL,
                    status_runtime TEXT,
                    answer_runtime TEXT,
                    proposed_action_runtime TEXT,
                    action_confidence_runtime REAL,
                    acquisition_valid INTEGER,
                    expected_entitled INTEGER,
                    expected_oracle_answer TEXT,
                    is_correct_entitlement INTEGER,
                    is_correct_semantic_answer INTEGER,
                    computed_surviving_support TEXT,
                    computed_surviving_lineage TEXT,
                    lineage_authority REAL,
                    gate_verdict TEXT,
                    executed_action TEXT,
                    latency_ms REAL,
                    replay_target_call_id TEXT,
                    is_replay_exact_match INTEGER,
                    timestamp REAL
                )
            """)
            
            run_id = f"RUN_5C_{int(time.time())}"
            conn.execute("""
                INSERT INTO stage5c_runs VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                self.git_commit,
                self.manifest_sha256,
                self.model_name,
                self.model_digest,
                self.ollama_version,
                time.time(),
            ))
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
        """Execute all 32 calls in sequential order with live support enumeration & hash checking."""
        results: list[NeuralRevisionBridgeOutput] = []
        call_outputs_by_id: dict[str, NeuralRevisionBridgeOutput] = {}
        acquisition_citations: dict[str, list[str]] = {}  # world_id -> cited_facts
        acquisition_validity: dict[str, bool] = {}  # world_id -> bool

        for call_dict in self.manifest["calls"]:
            call_spec = Stage5CCallSpec(**call_dict)
            world = self.worlds[call_spec.world_id]

            # 1. Epistemic Kernel Live Support Enumeration
            active_facts = set(world.facts.keys()) - set(call_spec.invalidated_facts)
            computed_s = enumerate_entitling_supports(world, active_facts)
            
            # Assert computed support matches manifest expected support
            if computed_s != call_spec.expected_surviving_support:
                raise AssertionError(
                    f"Support enumeration discrepancy in call {call_spec.call_id}! "
                    f"Computed: {computed_s}, Expected Oracle: {call_spec.expected_surviving_support}"
                )

            # Compute lineage projection S_L'(c)
            if computed_s and call_spec.expected_entitled:
                computed_l = project_lineage_support(computed_s, world.lineage_map).support_family_roots
            else:
                computed_l = []

            # 2. Render Prompt & Verify Frozen Request Hashes
            if call_spec.phase == "acquisition":
                prompt_text = render_acquisition_prompt(world)
            elif call_spec.arm in ["arm1_raw_neural", "arm2_naive_reported"]:
                prompt_text = render_arm1_raw_revision_prompt(world, call_spec.invalidated_facts)
            elif call_spec.arm == "arm3_gene_kernel":
                prompt_text = render_arm3_minimal_support_prompt(world, computed_s)
            elif call_spec.phase == "replay_canary":
                if call_spec.arm in ["arm1_raw_neural", "arm2_naive_reported"]:
                    prompt_text = render_arm1_raw_revision_prompt(world, call_spec.invalidated_facts)
                else:
                    prompt_text = render_arm3_minimal_support_prompt(world, computed_s)
            else:
                prompt_text = render_acquisition_prompt(world)

            p_sha = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
            req_sha = compute_request_payload_hash(
                model_name=self.model_name,
                system_prompt=CANONICAL_SYSTEM_PROMPT,
                user_prompt=prompt_text,
            )

            # Assert request payload hash matches frozen manifest
            if req_sha != call_spec.request_payload_sha256:
                raise AssertionError(
                    f"Request payload hash mismatch in call {call_spec.call_id}! "
                    f"Actual: {req_sha}, Frozen: {call_spec.request_payload_sha256}"
                )

            # 3. Model Invocation
            t0 = time.perf_counter()
            raw_response = self.client_fn(CANONICAL_SYSTEM_PROMPT, prompt_text)
            latency_ms = (time.perf_counter() - t0) * 1000.0

            # 4. Parse Model Output
            parsed = self.parse_response(raw_response)
            m_status = parsed["status"]
            m_answer = parsed["answer"]
            m_cited = parsed["cited_facts"]
            m_action = parsed["proposed_action"]
            m_conf = parsed["action_confidence"]

            # Phase 1: Track Acquisition Validity
            if call_spec.phase == "acquisition":
                acquisition_citations[call_spec.world_id] = m_cited
                is_valid = (
                    m_status == "DETERMINABLE"
                    and m_answer is not None
                    and m_answer.strip().upper() == call_spec.expected_oracle_answer.strip().upper()
                    and len(m_cited) > 0
                )
                acquisition_validity[call_spec.world_id] = is_valid

            is_acq_valid = acquisition_validity.get(call_spec.world_id, True)

            # 5. Determine Runtime Effective Outputs
            if call_spec.arm == "arm2_naive_reported":
                acq_cited = acquisition_citations.get(call_spec.world_id, [])
                naive_retracted = any(p in call_spec.invalidated_facts for p in acq_cited)
                if naive_retracted:
                    r_status = "INDETERMINABLE"
                    r_answer = None
                    r_action = None
                    r_conf = 0.0
                else:
                    r_status = m_status
                    r_answer = m_answer
                    r_action = m_action
                    r_conf = m_conf
            else:
                r_status = m_status
                r_answer = m_answer
                r_action = m_action
                r_conf = m_conf

            # 6. Dual-Oracle Entitlement & Semantic Accuracy Evaluation
            r_entitled = (r_status == "DETERMINABLE")
            is_correct_ent = (r_entitled == call_spec.expected_entitled)
            if call_spec.expected_entitled:
                is_correct_sem = (
                    is_correct_ent
                    and r_answer is not None
                    and r_answer.strip().upper() == call_spec.expected_oracle_answer.strip().upper()
                )
            else:
                is_correct_sem = (r_status == "INDETERMINABLE" and r_answer is None)

            # 7. Lineage Authority & Deterministic Action Gating
            if computed_s and call_spec.expected_entitled:
                init_lin = project_lineage_support(world.initial_support_family, world.lineage_map)
                surv_lin = project_lineage_support(computed_s, world.lineage_map)
                
                kappa_ratio = surv_lin.kappa_l / max(1, init_lin.kappa_l)
                path_ratio = len(surv_lin.support_family_roots) / max(1, len(world.initial_support_family))
                auth_score = 0.5 * kappa_ratio + 0.5 * path_ratio
            else:
                auth_score = 0.0

            if r_status == "DETERMINABLE" and r_action:
                gate_verdict = "PERMIT" if auth_score >= tau_gate else "BLOCK"
                executed_action = r_action if gate_verdict == "PERMIT" else None
            else:
                gate_verdict = "N/A"
                executed_action = None

            # 8. Replay Canary Verification
            is_replay_match = None
            if call_spec.phase == "replay_canary" and call_spec.replay_target_call_id:
                target = call_outputs_by_id.get(call_spec.replay_target_call_id)
                if target:
                    # Assert prompt hash exactness
                    assert target.prompt_sha256 == p_sha
                    is_replay_match = (target.raw_response.strip() == raw_response.strip())

            res = NeuralRevisionBridgeOutput(
                call_id=call_spec.call_id,
                call_index=call_spec.call_index,
                phase=call_spec.phase,
                world_id=call_spec.world_id,
                arm=call_spec.arm,
                condition=call_spec.condition,
                prompt_text=prompt_text,
                prompt_sha256=p_sha,
                request_payload_sha256=req_sha,
                raw_response=raw_response,
                status_model=m_status,
                answer_model=m_answer,
                cited_facts_model=m_cited,
                proposed_action_model=m_action,
                action_confidence_model=m_conf,
                status_runtime=r_status,
                answer_runtime=r_answer,
                proposed_action_runtime=r_action,
                action_confidence_runtime=r_conf,
                acquisition_valid=is_acq_valid,
                expected_entitled=call_spec.expected_entitled,
                expected_oracle_answer=call_spec.expected_oracle_answer,
                is_correct_entitlement=is_correct_ent,
                is_correct_semantic_answer=is_correct_sem,
                computed_surviving_support=computed_s,
                computed_surviving_lineage=computed_l,
                lineage_authority=auth_score,
                gate_verdict=gate_verdict,
                executed_action=executed_action,
                latency_ms=latency_ms,
                replay_target_call_id=call_spec.replay_target_call_id,
                is_replay_exact_match=is_replay_match,
            )

            results.append(res)
            call_outputs_by_id[res.call_id] = res
            self._save_call_to_db(res)

        return results

    def _save_call_to_db(self, r: NeuralRevisionBridgeOutput) -> None:
        """Persist individual evaluation to SQLite using strict append-only INSERT."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO stage5c_calls VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
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
                r.request_payload_sha256,
                r.raw_response,
                r.status_model,
                r.answer_model,
                json.dumps(r.cited_facts_model),
                r.proposed_action_model,
                r.action_confidence_model,
                r.status_runtime,
                r.answer_runtime,
                r.proposed_action_runtime,
                r.action_confidence_runtime,
                1 if r.acquisition_valid else 0,
                1 if r.expected_entitled else 0,
                r.expected_oracle_answer,
                1 if r.is_correct_entitlement else 0,
                1 if r.is_correct_semantic_answer else 0,
                json.dumps(r.computed_surviving_support),
                json.dumps(r.computed_surviving_lineage),
                r.lineage_authority,
                r.gate_verdict,
                r.executed_action,
                r.latency_ms,
                r.replay_target_call_id,
                1 if r.is_replay_exact_match is True else (0 if r.is_replay_exact_match is False else None),
                time.time(),
            ))
            conn.commit()
