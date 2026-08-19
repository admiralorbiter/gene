"""Ollama API adapter capturing model metadata, digests, latencies, and token counts."""

from __future__ import annotations

import json
import time
from typing import Any
import httpx
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Metadata describing the target Ollama model."""
    model_config = {"protected_namespaces": ()}

    model_name: str
    digest: str
    parameter_size: str | None = None
    quantization_level: str | None = None
    family: str | None = None
    modified_at: str | None = None


class ModelCallResult(BaseModel):
    """Auditable output of a single LLM invocation."""
    model_config = {"protected_namespaces": ()}

    model_name: str
    model_digest: str
    request_payload: dict[str, Any]
    raw_response_text: str
    parsed_json: dict[str, Any] | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


class OllamaClient:
    """Client for local Ollama instance with structured JSON and auditing."""

    def __init__(self, host: str = "http://127.0.0.1:11434", timeout: float = 120.0):
        self.host = host.rstrip("/")
        self.timeout = timeout

    def get_model_info(self, model_name: str) -> ModelInfo:
        """Fetch model metadata and SHA256 digest from Ollama."""
        url = f"{self.host}/api/show"
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json={"name": model_name})
                res.raise_for_status()
                data = res.json()
                details = data.get("details", {})
                return ModelInfo(
                    model_name=model_name,
                    digest=data.get("digest", "unknown"),
                    parameter_size=details.get("parameter_size"),
                    quantization_level=details.get("quantization_level"),
                    family=details.get("family"),
                    modified_at=data.get("modified_at"),
                )
        except Exception as e:
            return ModelInfo(
                model_name=model_name,
                digest=f"error_{type(e).__name__}",
            )

    def chat(
        self,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        num_ctx: int = 4096,
        seed: int | None = 42,
    ) -> ModelCallResult:
        """Execute structured JSON chat completion and capture audit metadata."""
        url = f"{self.host}/api/chat"
        options: dict[str, Any] = {
            "temperature": temperature,
            "num_ctx": num_ctx,
        }
        if seed is not None:
            options["seed"] = seed

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": options,
        }

        start_time = time.perf_counter()
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000.0
        message_content = data.get("message", {}).get("content", "")

        parsed_json = None
        try:
            parsed_json = json.loads(message_content)
        except Exception:
            parsed_json = None

        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        # Retrieve digest or use placeholder
        model_digest = data.get("model", model_name)

        return ModelCallResult(
            model_name=model_name,
            model_digest=model_digest,
            request_payload=payload,
            raw_response_text=message_content,
            parsed_json=parsed_json,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
        )


class FakeOllamaClient:
    """Deterministic fake client for unit testing and fast plumbing simulations."""

    def __init__(self, canned_responses: dict[str, dict[str, Any]] | None = None):
        self.canned_responses = canned_responses or {}
        self.default_response: dict[str, Any] = {
            "answer": {
                "subject": "VELORA",
                "predicate": "uses_protocol",
                "object": "PROTOCOL_GREEN",
            },
            "parent_memory_ids": ["mem_001", "mem_002"],
            "confidence": 0.95,
            "explanation": "Derived from station manager reporting hierarchy.",
        }

    def get_model_info(self, model_name: str) -> ModelInfo:
        return ModelInfo(
            model_name=model_name,
            digest="sha256:fake_digest_1234567890",
            parameter_size="12B",
            quantization_level="Q4_K_M",
            family="gemma3",
        )

    def chat(
        self,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        num_ctx: int = 4096,
        seed: int | None = 42,
    ) -> ModelCallResult:
        # Check custom canned responses first
        for key, custom_resp in self.canned_responses.items():
            if key in user_prompt:
                resp_text = json.dumps(custom_resp)
                return ModelCallResult(
                    model_name=model_name,
                    model_digest="sha256:fake_digest_1234567890",
                    request_payload={"model": model_name, "prompt": user_prompt},
                    raw_response_text=resp_text,
                    parsed_json=custom_resp,
                    prompt_tokens=120,
                    completion_tokens=45,
                    latency_ms=1.5,
                )

        # If prompt does not contain Target Subject, fall back to default_response
        if "Target Subject:" not in user_prompt:
            resp_text = json.dumps(self.default_response)
            return ModelCallResult(
                model_name=model_name,
                model_digest="sha256:fake_digest_1234567890",
                request_payload={"model": model_name, "prompt": user_prompt},
                raw_response_text=resp_text,
                parsed_json=self.default_response,
                prompt_tokens=120,
                completion_tokens=45,
                latency_ms=1.5,
            )

        # Dynamic deduction from prompt for simulated pipeline runs
        target_subj = "UNKNOWN"
        target_pred = "unknown"
        for line in user_prompt.split("\n"):
            if line.startswith("Target Subject:"):
                target_subj = line.replace("Target Subject:", "").strip()
            elif line.startswith("Target Predicate:"):
                target_pred = line.replace("Target Predicate:", "").strip()

        # Find memories matching target subject
        matched_mem_ids: list[str] = []
        ans_object = "UNKNOWN"

        clean_subj_title = target_subj.replace("_", " ").title()
        for line in user_prompt.split("\n"):
            if line.startswith("[") and "]" in line:
                mem_id = line[1:line.index("]")]
                text = line[line.index("]") + 1:].strip()
                if clean_subj_title.lower() in text.lower():
                    matched_mem_ids.append(mem_id)
                    # Extract last word/entity as object candidate
                    words = [w.strip(".,;:!?") for w in text.split() if w.strip(".,;:!?")]
                    if words:
                        ans_object = words[-1].upper()

        if not matched_mem_ids:
            ans_object = "DEFAULT_VAL"

        resp = {
            "answer": {
                "subject": target_subj,
                "predicate": target_pred,
                "object": ans_object,
            },
            "parent_memory_ids": matched_mem_ids[:2] if matched_mem_ids else ["mem_default"],
            "confidence": 0.95,
            "explanation": f"Simulated deduction for {target_subj} {target_pred}.",
        }

        resp_text = json.dumps(resp)
        return ModelCallResult(
            model_name=model_name,
            model_digest="sha256:fake_digest_1234567890",
            request_payload={"model": model_name, "prompt": user_prompt},
            raw_response_text=resp_text,
            parsed_json=resp,
            prompt_tokens=120,
            completion_tokens=45,
            latency_ms=1.5,
        )
