"""Single-call execution and audit logging runner using unified CallSpec."""

from __future__ import annotations

import json
import subprocess
import time
import uuid
from typing import Any
from gene.config import ExperimentConfig
from gene.evaluation.claims import ClaimEvaluator, EvaluatedClaim
from gene.ollama_client import CallSpec, ModelCallResult, OllamaClient
from gene.persistence.db import Database
from gene.prompts.templates import PromptTemplate
from gene.worlds.oracle import Oracle
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Task, World


def get_git_commit() -> str:
    """Retrieve current git commit hash if available."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "unknown_commit"


def get_environment_info() -> dict[str, Any]:
    """Retrieve host hardware and runtime environment details for auditable experiment reproducibility."""
    import platform
    info: dict[str, Any] = {
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
    }
    try:
        import torch
        if torch.cuda.is_available():
            info["gpu_available"] = True
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_count"] = torch.cuda.device_count()
            info["cuda_version"] = torch.version.cuda
        else:
            info["gpu_available"] = False
    except ImportError:
        info["gpu_available"] = None
    return info


class SingleCallRunner:
    """Orchestrates an individual model query, parses claims, evaluates oracle truth, and persists call audit data."""

    def __init__(
        self,
        db: Database,
        client: Any | None = None,
        config: ExperimentConfig | None = None,
    ):
        self.db = db
        self.config = config or ExperimentConfig()
        self.client = client or OllamaClient()
        self.prompt_template = PromptTemplate(self.config.prompt_version)
        self.git_commit = get_git_commit()

    def create_run(self, world: World, condition: str = "clean") -> str:
        """Initialize a new experiment run in the database with full configuration persistence."""
        run_id = f"run_{uuid.uuid4().hex[:10]}"
        model_info = self.client.get_model_info(self.config.model.model_name)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Ensure world is persisted
        self.db.save_world(world)

        # Dynamic Ollama version and environment metadata
        if hasattr(self.client, "get_version"):
            ollama_ver = self.client.get_version()
        else:
            ollama_ver = self.client.__class__.__name__

        env_info = get_environment_info()
        config_data = self.config.model_dump()
        config_data["environment"] = env_info
        config_json = json.dumps(config_data, indent=2)
        config_hash = self.config.config_hash()

        with self.db.conn:
            self.db.conn.execute(
                """
                INSERT INTO runs (
                    run_id, experiment_name, experiment_version, condition, world_id,
                    model_name, model_digest, ollama_version, seed, num_ctx, temperature,
                    prompt_version, prompt_hash, retrieval_policy, memory_policy,
                    git_commit, config_json, config_hash, started_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    self.config.experiment_name,
                    self.config.experiment_version,
                    condition,
                    world.world_id,
                    self.config.model.model_name,
                    model_info.digest,
                    ollama_ver,
                    self.config.decoding_seed,
                    self.config.model.num_ctx,
                    self.config.model.temperature,
                    self.config.prompt_version,
                    self.prompt_template.prompt_hash(),
                    self.config.retrieval.policy,
                    "append_only",
                    self.git_commit,
                    config_json,
                    config_hash,
                    now,
                    "running",
                ),
            )
        return run_id

    def execute_task(
        self,
        run_id: str,
        world: World,
        task: Task,
        oracle: Oracle,
        generation: int = 1,
        exposed_memories: list[dict[str, str]] | None = None,
    ) -> tuple[ModelCallResult, EvaluatedClaim, str, str]:
        """Execute a single task call against Ollama, evaluate with oracle, and record all audit tables."""
        # 1. Prepare memory representations if not explicitly provided
        if exposed_memories is None:
            exposed_memories = []
            for fact in world.facts:
                exposed_memories.append({
                    "memory_id": fact.fact_id,
                    "text": NaturalLanguageRenderer.render_fact(fact),
                })
            for rule in world.rules:
                exposed_memories.append({
                    "memory_id": rule.rule_id,
                    "text": NaturalLanguageRenderer.render_rule(rule),
                })

        # 2. Format user prompt
        user_prompt = self.prompt_template.format_user_prompt(
            memories=exposed_memories,
            question_prompt=task.prompt,
            target_subject=task.target_fact.subject,
            target_predicate=task.target_fact.predicate,
        )

        # 3. Create canonical CallSpec
        call_spec = CallSpec(
            model_name=self.config.model.model_name,
            system_prompt=self.prompt_template.system_prompt,
            user_prompt=user_prompt,
            temperature=self.config.model.temperature,
            num_ctx=self.config.model.num_ctx,
            seed=self.config.decoding_seed,
        )

        # 4. Invoke model
        call_result = self.client.chat(call_spec)

        # 5. Mechanically evaluate claim against oracle and target fact
        evaluated_claim = ClaimEvaluator.evaluate_response(
            raw_text=call_result.raw_response_text,
            parsed_json=call_result.parsed_json,
            oracle=oracle,
            condition=self.config.condition,
        )

        # 6. Persist call, memory node, and claim to SQLite
        call_id = f"call_{uuid.uuid4().hex[:12]}"
        node_id = f"node_{uuid.uuid4().hex[:12]}"
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        with self.db.conn:
            # 6a. Save call record with serialized CallSpec
            self.db.conn.execute(
                """
                INSERT INTO calls (
                    call_id, run_id, generation, task_id, request_json,
                    response_text, response_json, prompt_tokens, completion_tokens,
                    latency_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    call_id,
                    run_id,
                    generation,
                    task.task_id,
                    call_spec.model_dump_json(),
                    call_result.raw_response_text,
                    json.dumps(call_result.parsed_json) if call_result.parsed_json else None,
                    call_result.prompt_tokens,
                    call_result.completion_tokens,
                    call_result.latency_ms,
                    now,
                ),
            )

            # 6b. Save generated memory node
            natural_text = (
                f"{evaluated_claim.subject} {evaluated_claim.predicate} {evaluated_claim.object}"
                if evaluated_claim.parse_status == "success"
                else call_result.raw_response_text
            )
            self.db.conn.execute(
                """
                INSERT INTO memory_nodes (
                    node_id, run_id, world_id, generation, node_type, natural_text,
                    structured_json, reproductive_status, created_by_call_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    run_id,
                    world.world_id,
                    generation,
                    "derived",
                    natural_text,
                    json.dumps(call_result.parsed_json) if call_result.parsed_json else None,
                    "active",
                    call_id,
                    now,
                ),
            )

            # 6c. Save evaluated claim
            unique_claim_id = f"claim_{uuid.uuid4().hex[:12]}"
            self.db.conn.execute(
                """
                INSERT INTO claims (
                    claim_id, node_id, subject, predicate, object, parse_status,
                    truth_status, infection_status, oracle_evidence_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    unique_claim_id,
                    node_id,
                    evaluated_claim.subject,
                    evaluated_claim.predicate,
                    evaluated_claim.object,
                    evaluated_claim.parse_status,
                    evaluated_claim.truth_status.value,
                    evaluated_claim.infection_status,
                    json.dumps({
                        "task_id": task.task_id,
                        "reasoning_depth": task.reasoning_depth,
                        "target_subject": task.target_fact.subject,
                        "target_predicate": task.target_fact.predicate,
                        "target_object": task.target_fact.object,
                        "valid_support_paths": task.valid_support_path_ids,
                    }),
                ),
            )

        return call_result, evaluated_claim, call_id, node_id
