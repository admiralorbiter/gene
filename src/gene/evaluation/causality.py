"""Counterfactual causal runner, CallSpec byte-equal replays, and intervention outcome comparator."""

from __future__ import annotations

import json
import uuid
from typing import Any, Literal
from pydantic import BaseModel, Field
from gene.config import ExperimentConfig
from gene.evaluation.claims import ClaimEvaluator, EvaluatedClaim
from gene.ollama_client import CallSpec, OllamaClient
from gene.persistence.db import Database
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, World


class CausalTestResult(BaseModel):
    """Auditable result of a counterfactual intervention."""
    causal_test_id: str
    parent_node_id: str
    child_node_id: str
    original_call_id: str
    intervention_type: Literal["remove", "replace_clean", "noop"]
    intervention_seed: int
    counterfactual_call_id: str
    original_claim: EvaluatedClaim
    counterfactual_claim: EvaluatedClaim
    outcome: Literal["strong", "partial", "none", "indeterminate"]
    score: float
    comparison_details: dict[str, Any] = Field(default_factory=dict)


class CausalRunner:
    """Replays LLM calls under controlled counterfactual parent interventions using stored CallSpec."""

    def __init__(
        self,
        db: Database,
        client: Any | None = None,
        config: ExperimentConfig | None = None,
    ):
        self.db = db
        self.client = client or OllamaClient()
        self.config = config or ExperimentConfig()

    def replay_intervention(
        self,
        original_call_id: str,
        child_node_id: str,
        target_parent_id: str,
        intervention_type: Literal["remove", "replace_clean", "noop"] = "remove",
        clean_counterpart_fact: Fact | None = None,
        oracle: Oracle | None = None,
        world: World | None = None,
        seed: int = 42,
    ) -> CausalTestResult:
        """Replay an original model call with a candidate parent memory removed, replaced, or unmodified (noop)."""
        # 1. Fetch original call record
        orig_call = self.db.conn.execute(
            "SELECT * FROM calls WHERE call_id = ?", (original_call_id,)
        ).fetchone()
        if not orig_call:
            raise ValueError(f"Original call {original_call_id} not found in database.")

        orig_spec = CallSpec.model_validate_json(orig_call["request_json"])
        user_prompt = orig_spec.user_prompt

        # 2. Modify prompt strictly per intervention type while holding all other CallSpec fields byte-equal
        if intervention_type == "noop":
            new_user_prompt = user_prompt
        elif intervention_type == "remove":
            lines = user_prompt.split("\n")
            filtered_lines = [l for l in lines if not l.startswith(f"[{target_parent_id}]")]
            new_user_prompt = "\n".join(filtered_lines)
        elif intervention_type == "replace_clean" and clean_counterpart_fact:
            clean_text = NaturalLanguageRenderer.render_fact(clean_counterpart_fact)
            lines = user_prompt.split("\n")
            replaced_lines = []
            for l in lines:
                if l.startswith(f"[{target_parent_id}]"):
                    replaced_lines.append(f"[{clean_counterpart_fact.fact_id}] {clean_text}")
                else:
                    replaced_lines.append(l)
            new_user_prompt = "\n".join(replaced_lines)
        else:
            new_user_prompt = user_prompt

        cf_spec = orig_spec.model_copy(update={
            "user_prompt": new_user_prompt,
            "seed": seed,
        })

        # 3. Execute counterfactual call
        cf_call_result = self.client.chat(cf_spec)

        # 4. Fetch original claim from db
        orig_claim_row = self.db.conn.execute(
            "SELECT * FROM claims WHERE node_id = ?", (child_node_id,)
        ).fetchone()
        if orig_claim_row:
            orig_claim = EvaluatedClaim(
                claim_id=orig_claim_row["claim_id"],
                subject=orig_claim_row["subject"],
                predicate=orig_claim_row["predicate"],
                object=orig_claim_row["object"],
                parse_status=orig_claim_row["parse_status"],
                truth_status=TruthStatus(orig_claim_row["truth_status"]),
                infection_status=orig_claim_row["infection_status"],
                reported_parent_ids=[],
                raw_response_text=orig_call["response_text"] or "",
            )
        else:
            orig_claim = EvaluatedClaim(
                claim_id="unknown",
                subject="UNKNOWN",
                predicate="unknown",
                object="UNKNOWN",
                parse_status="unparseable",
                truth_status=TruthStatus.UNSUPPORTED,
                infection_status="unresolved",
                reported_parent_ids=[],
            )

        # 5. Evaluate counterfactual claim
        cf_oracle = oracle or (Oracle(world) if world else None)
        cf_claim = (
            ClaimEvaluator.evaluate_response(
                raw_text=cf_call_result.raw_response_text,
                parsed_json=cf_call_result.parsed_json,
                oracle=cf_oracle,
            )
            if cf_oracle
            else EvaluatedClaim(
                claim_id="unknown",
                subject="UNKNOWN",
                predicate="unknown",
                object="UNKNOWN",
                parse_status="unparseable",
                truth_status=TruthStatus.UNSUPPORTED,
                infection_status="unresolved",
                reported_parent_ids=[],
            )
        )

        # 6. Compare outcomes
        outcome, score, details = self._classify_causal_outcome(orig_claim, cf_claim, intervention_type)

        # 7. Persist counterfactual call and causal test to SQLite
        cf_call_id = f"call_cf_{uuid.uuid4().hex[:10]}"
        causal_test_id = f"ctest_{uuid.uuid4().hex[:10]}"
        now = cf_call_result.created_at

        with self.db.conn:
            self.db.conn.execute(
                """
                INSERT INTO calls (
                    call_id, run_id, generation, task_id, request_json,
                    response_text, response_json, prompt_tokens, completion_tokens,
                    latency_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cf_call_id,
                    orig_call["run_id"],
                    orig_call["generation"],
                    f"{orig_call['task_id']}_cf",
                    cf_spec.model_dump_json(),
                    cf_call_result.raw_response_text,
                    json.dumps(cf_call_result.parsed_json) if cf_call_result.parsed_json else None,
                    cf_call_result.prompt_tokens,
                    cf_call_result.completion_tokens,
                    cf_call_result.latency_ms,
                    now,
                ),
            )

            self.db.conn.execute(
                """
                INSERT INTO causal_tests (
                    causal_test_id, parent_node_id, child_node_id, original_call_id,
                    intervention_type, intervention_seed, counterfactual_call_id,
                    outcome, score, comparison_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    causal_test_id,
                    target_parent_id,
                    child_node_id,
                    original_call_id,
                    intervention_type,
                    seed,
                    cf_call_id,
                    outcome,
                    score,
                    json.dumps(details),
                ),
            )

        return CausalTestResult(
            causal_test_id=causal_test_id,
            parent_node_id=target_parent_id,
            child_node_id=child_node_id,
            original_call_id=original_call_id,
            intervention_type=intervention_type,
            intervention_seed=seed,
            counterfactual_call_id=cf_call_id,
            original_claim=orig_claim,
            counterfactual_claim=cf_claim,
            outcome=outcome,
            score=score,
            comparison_details=details,
        )

    @staticmethod
    def _classify_causal_outcome(
        orig: EvaluatedClaim,
        cf: EvaluatedClaim,
        intervention_type: str,
    ) -> tuple[Literal["strong", "partial", "none", "indeterminate"], float, dict[str, Any]]:
        """Classify counterfactual shift into strong, partial, none, or indeterminate evidence."""
        details: dict[str, Any] = {
            "orig_subject": orig.subject,
            "orig_predicate": orig.predicate,
            "orig_object": orig.object,
            "orig_truth": orig.truth_status.value,
            "cf_subject": cf.subject,
            "cf_predicate": cf.predicate,
            "cf_object": cf.object,
            "cf_truth": cf.truth_status.value,
            "cf_parse": cf.parse_status,
        }

        if cf.parse_status != "success":
            return "indeterminate", 0.0, details

        orig_triple = (orig.subject, orig.predicate, orig.object)
        cf_triple = (cf.subject, cf.predicate, cf.object)

        if intervention_type == "noop":
            # Sham replay: outcome is "none" if stable, "strong" if stochastic shift
            if orig_triple == cf_triple:
                return "none", 0.0, details
            else:
                return "strong", 1.0, details

        if intervention_type == "remove":
            # If removing candidate parent caused previously true claim to change or become unsupported
            if orig_triple != cf_triple:
                return "strong", 1.0, details
            else:
                return "none", 0.0, details

        if intervention_type == "replace_clean":
            if orig_triple != cf_triple and cf.truth_status == TruthStatus.TRUE:
                return "strong", 1.0, details
            elif orig_triple != cf_triple:
                return "partial", 0.5, details
            else:
                return "none", 0.0, details

        return "indeterminate", 0.0, details
