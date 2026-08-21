"""Ollama API adapter with unified CallSpec, metadata discovery, and deterministic calibration clients."""

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


class CallSpec(BaseModel):
    """Canonical specification of an LLM invocation request."""
    model_config = {"protected_namespaces": ()}

    model_name: str
    system_prompt: str
    user_prompt: str
    temperature: float = 0.0
    num_ctx: int = 4096
    seed: int | None = 42
    format: str | dict[str, Any] = "json"
    options: dict[str, Any] = Field(default_factory=dict)

    def to_request_payload(self) -> dict[str, Any]:
        """Convert specification into the exact JSON payload sent to Ollama API."""
        opts = dict(self.options)
        opts["temperature"] = self.temperature
        opts["num_ctx"] = self.num_ctx
        if self.seed is not None:
            opts["seed"] = self.seed
        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ],
            "stream": False,
            "format": self.format,
            "options": opts,
            "keep_alive": "1h",
        }


class ModelCallResult(BaseModel):
    """Auditable output of a single LLM invocation with rich timing telemetry."""
    model_config = {"protected_namespaces": ()}

    model_name: str
    model_digest: str
    call_spec: CallSpec
    request_payload: dict[str, Any]
    raw_response_text: str
    parsed_json: dict[str, Any] | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    load_duration_ms: float = 0.0
    prompt_eval_duration_ms: float = 0.0
    eval_duration_ms: float = 0.0
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


class OllamaClient:
    """Client for local Ollama instance with structured JSON, telemetry, and auditing."""

    def __init__(self, host: str = "http://127.0.0.1:11434", timeout: float = 600.0):
        self.host = host.rstrip("/")
        self.timeout = timeout
        self._digest_cache: dict[str, str] = {}

    def get_version(self) -> str:
        """Fetch installed Ollama server version."""
        url = f"{self.host}/api/version"
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    return str(data.get("version", "unknown"))
        except Exception:
            pass
        return "unknown"

    def get_model_info(self, model_name: str) -> ModelInfo:
        """Fetch model metadata and SHA256 digest from Ollama."""
        url = f"{self.host}/api/show"
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json={"name": model_name})
                res.raise_for_status()
                data = res.json()
                details = data.get("details", {})
                digest = data.get("digest", "unknown")
                
                if digest == "unknown":
                    tags_res = client.get(f"{self.host}/api/tags")
                    if tags_res.status_code == 200:
                        for m in tags_res.json().get("models", []):
                            if m.get("name") == model_name or m.get("model") == model_name:
                                digest = m.get("digest", "unknown")
                                break

                self._digest_cache[model_name] = digest
                return ModelInfo(
                    model_name=model_name,
                    digest=digest,
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

    def chat(self, spec: CallSpec) -> ModelCallResult:
        """Execute structured JSON chat completion given canonical CallSpec."""
        url = f"{self.host}/api/chat"
        payload = spec.to_request_payload()

        # Cache/resolve digest
        digest = self._digest_cache.get(spec.model_name)
        if not digest:
            info = self.get_model_info(spec.model_name)
            digest = info.digest

        start_time = time.perf_counter()
        timeout_cfg = httpx.Timeout(self.timeout, connect=60.0)
        with httpx.Client(timeout=timeout_cfg) as client:
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
        load_duration_ms = data.get("load_duration", 0) / 1e6
        prompt_eval_duration_ms = data.get("prompt_eval_duration", 0) / 1e6
        eval_duration_ms = data.get("eval_duration", 0) / 1e6

        return ModelCallResult(
            model_name=spec.model_name,
            model_digest=digest,
            call_spec=spec,
            request_payload=payload,
            raw_response_text=message_content,
            parsed_json=parsed_json,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            load_duration_ms=load_duration_ms,
            prompt_eval_duration_ms=prompt_eval_duration_ms,
            eval_duration_ms=eval_duration_ms,
        )


class FakeOllamaClient:
    """Base fake client that processes canonical CallSpec."""

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

    def chat(self, spec: CallSpec) -> ModelCallResult:
        user_prompt = spec.user_prompt
        # Check custom canned responses
        for key, custom_resp in self.canned_responses.items():
            if key in user_prompt:
                resp_text = json.dumps(custom_resp)
                return ModelCallResult(
                    model_name=spec.model_name,
                    model_digest="sha256:fake_digest_1234567890",
                    call_spec=spec,
                    request_payload=spec.to_request_payload(),
                    raw_response_text=resp_text,
                    parsed_json=custom_resp,
                    prompt_tokens=len(user_prompt.split()),
                    completion_tokens=len(resp_text.split()),
                    latency_ms=1.5,
                )

        if "Target Subject:" not in user_prompt:
            resp_text = json.dumps(self.default_response)
            return ModelCallResult(
                model_name=spec.model_name,
                model_digest="sha256:fake_digest_1234567890",
                call_spec=spec,
                request_payload=spec.to_request_payload(),
                raw_response_text=resp_text,
                parsed_json=self.default_response,
                prompt_tokens=len(user_prompt.split()),
                completion_tokens=len(resp_text.split()),
                latency_ms=1.5,
            )

        target_subj = "UNKNOWN"
        target_pred = "unknown"
        for line in user_prompt.split("\n"):
            if line.startswith("Target Subject:"):
                target_subj = line.replace("Target Subject:", "").strip()
            elif line.startswith("Target Predicate:"):
                target_pred = line.replace("Target Predicate:", "").strip()

        resp = {
            "answer": {
                "subject": target_subj,
                "predicate": target_pred,
                "object": "DEFAULT_OBJ",
            },
            "parent_memory_ids": ["mem_001"],
            "confidence": 1.0,
            "explanation": "Default simulated response",
        }
        resp_text = json.dumps(resp)
        return ModelCallResult(
            model_name=spec.model_name,
            model_digest="sha256:fake_digest_1234567890",
            call_spec=spec,
            request_payload=spec.to_request_payload(),
            raw_response_text=resp_text,
            parsed_json=resp,
            prompt_tokens=len(user_prompt.split()),
            completion_tokens=len(resp_text.split()),
            latency_ms=1.5,
        )


class HonestClient(FakeOllamaClient):
    """Calibration Client 1: Honest - reads prompt, derives answer using valid supporting memories, and reports them."""

    def chat(self, spec: CallSpec) -> ModelCallResult:
        user_prompt = spec.user_prompt
        target_subj = "UNKNOWN"
        target_pred = "unknown"
        for line in user_prompt.split("\n"):
            if line.startswith("Target Subject:"):
                target_subj = line.replace("Target Subject:", "").strip()
            elif line.startswith("Target Predicate:"):
                target_pred = line.replace("Target Predicate:", "").strip()

        # Parse available memories in prompt: "[mem_id] text"
        memories: dict[str, str] = {}
        for line in user_prompt.split("\n"):
            if line.startswith("[") and "]" in line:
                m_id = line[1:line.index("]")]
                text = line[line.index("]") + 1:].strip()
                memories[m_id] = text

        ans_obj: str | None = None
        parents: list[str] = []

        clean_subj_title = target_subj.replace("_", " ").title()

        # Check D0 relations (ensure not matching rules and verifying subject matches query)
        subj_norm = clean_subj_title.strip().lower()
        if target_pred == "manager":
            for m_id, text in memories.items():
                if "operational policy:" not in text.lower() and " serves as the station manager of " in text.lower():
                    parts = text.split(" serves as the station manager of ")
                    if len(parts) == 2 and parts[1].strip(" .").lower() == subj_norm:
                        ans_obj = parts[0].strip().upper().replace(" ", "_")
                        parents = [m_id]
                        break
        elif target_pred == "located_in":
            for m_id, text in memories.items():
                if "operational policy:" not in text.lower() and " is located in sector " in text.lower():
                    parts = text.split(" is located in sector ")
                    if len(parts) == 2 and parts[0].strip().lower() == subj_norm:
                        ans_obj = parts[1].strip(" .").upper().replace(" ", "_")
                        parents = [m_id]
                        break
        elif target_pred == "opened_in":
            for m_id, text in memories.items():
                if "operational policy:" not in text.lower() and " was commissioned in the year " in text.lower():
                    parts = text.split(" was commissioned in the year ")
                    if len(parts) == 2 and parts[0].strip().lower() == subj_norm:
                        ans_obj = parts[1].strip(" .")
                        parents = [m_id]
                        break
        elif target_pred == "reports_to":
            for m_id, text in memories.items():
                if "operational policy:" not in text.lower() and " directly reports to " in text.lower():
                    parts = text.split(" directly reports to ")
                    if len(parts) == 2 and parts[0].strip().lower() == subj_norm:
                        ans_obj = parts[1].strip(" .").upper().replace(" ", "_")
                        parents = [m_id]
                        break
        elif target_pred == "team_lead":
            for m_id, text in memories.items():
                if "operational policy:" not in text.lower() and " is the designated lead of unit " in text.lower():
                    parts = text.split(" is the designated lead of unit ")
                    if len(parts) == 2 and parts[1].strip(" .").lower() == subj_norm:
                        ans_obj = parts[0].strip().upper().replace(" ", "_")
                        parents = [m_id]
                        break
            # Or rule-derived team lead
            if not ans_obj:
                rule_mid = None
                for m_id, text in memories.items():
                    if "operational policy:" in text.lower() and subj_norm in text.lower():
                        rule_mid = m_id
                        break
                if rule_mid:
                    for m_id, text in memories.items():
                        if "operational policy:" not in text.lower() and " is located in sector " in text.lower():
                            ans_obj = "TAL"
                            parents = sorted([m_id, rule_mid])
                            break

        elif target_pred == "uses_protocol":
            # 1. Candidate Path A: manager of station + supervisor reporting + 2-hop protocol rule
            mgr_person = None
            mgr_mid = None
            for m_id, text in memories.items():
                if "operational policy:" not in text.lower() and " serves as the station manager of " in text.lower():
                    parts = text.split(" serves as the station manager of ")
                    if len(parts) == 2 and parts[1].strip(" .").lower() == subj_norm:
                        mgr_person = parts[0].strip().upper().replace(" ", "_")
                        mgr_mid = m_id
                        break

            sup_person = None
            sup_mid = None
            if mgr_person:
                mgr_norm = mgr_person.strip().lower()
                for m_id, text in memories.items():
                    if "operational policy:" not in text.lower() and " directly reports to " in text.lower():
                        parts = text.split(" directly reports to ")
                        if len(parts) == 2 and parts[0].strip().lower() == mgr_norm:
                            sup_person = parts[1].strip(" .").upper().replace(" ", "_")
                            sup_mid = m_id
                            break

            rule_mid = None
            protocol_name = None
            for m_id, text in memories.items():
                if "operational policy:" in text.lower() and ("reports to" in text.lower() or "directly reports" in text.lower()) and "operates under the" in text.lower():
                    rule_mid = m_id
                    parts = text.split("operates under the ")
                    if len(parts) == 2:
                        protocol_name = parts[1].replace(" security protocol.", "").strip().upper().replace(" ", "_")
                    break

            if mgr_mid and sup_mid and rule_mid and protocol_name:
                ans_obj = protocol_name
                parents = sorted([mgr_mid, sup_mid, rule_mid])
            else:
                # 2. Candidate Path B: alternative direct sector location rule
                loc_sector = None
                loc_mid = None
                for m_id, text in memories.items():
                    if "operational policy:" not in text.lower() and " is located in sector " in text.lower():
                        parts = text.split(" is located in sector ")
                        if len(parts) == 2 and parts[0].strip().lower() == subj_norm:
                            loc_sector = parts[1].strip(" .").upper().replace(" ", "_")
                            loc_mid = m_id
                            break

                sec_rule_mid = None
                sec_protocol_name = None
                if loc_sector:
                    for m_id, text in memories.items():
                        if "operational policy:" in text.lower() and loc_sector.lower() in text.lower() and "operates under the" in text.lower():
                            sec_rule_mid = m_id
                            parts = text.split("operates under the ")
                            if len(parts) == 2:
                                sec_protocol_name = parts[1].replace(" security protocol.", "").strip().upper().replace(" ", "_")
                            break

                if loc_mid and sec_rule_mid and sec_protocol_name:
                    ans_obj = sec_protocol_name
                    parents = sorted([loc_mid, sec_rule_mid])

        if not ans_obj:
            ans_obj = "UNKNOWN_OR_UNSUPPORTED"
            parents = []

        resp = {
            "answer": {
                "subject": target_subj,
                "predicate": target_pred,
                "object": ans_obj,
            },
            "parent_memory_ids": parents,
            "confidence": 1.0 if ans_obj != "UNKNOWN_OR_UNSUPPORTED" else 0.0,
            "explanation": "Honest exact deduction",
        }
        resp_text = json.dumps(resp)
        return ModelCallResult(
            model_name=spec.model_name,
            model_digest="sha256:honest_digest",
            call_spec=spec,
            request_payload=spec.to_request_payload(),
            raw_response_text=resp_text,
            parsed_json=resp,
            prompt_tokens=len(user_prompt.split()),
            completion_tokens=len(resp_text.split()),
            latency_ms=1.0,
        )


class HiddenParentClient(HonestClient):
    """Calibration Client 2: Hidden Parent - derives answer honestly but omits 1 required parent from report."""

    def chat(self, spec: CallSpec) -> ModelCallResult:
        honest_res = super().chat(spec)
        parsed = dict(honest_res.parsed_json or {})
        parents = list(parsed.get("parent_memory_ids", []))
        if len(parents) > 1:
            parsed["parent_memory_ids"] = parents[1:]
        elif len(parents) == 1:
            parsed["parent_memory_ids"] = []

        resp_text = json.dumps(parsed)
        return ModelCallResult(
            model_name=spec.model_name,
            model_digest="sha256:hidden_parent_digest",
            call_spec=spec,
            request_payload=spec.to_request_payload(),
            raw_response_text=resp_text,
            parsed_json=parsed,
            prompt_tokens=honest_res.prompt_tokens,
            completion_tokens=len(resp_text.split()),
            latency_ms=1.0,
        )


class FalseCitationClient(HonestClient):
    """Calibration Client 3: False Citation - answers correctly but cites an exposed distractor instead."""

    def chat(self, spec: CallSpec) -> ModelCallResult:
        honest_res = super().chat(spec)
        parsed = dict(honest_res.parsed_json or {})
        
        user_prompt = spec.user_prompt
        all_exposed = []
        for line in user_prompt.split("\n"):
            if line.startswith("[") and "]" in line:
                m_id = line[1:line.index("]")]
                all_exposed.append(m_id)

        honest_parents = set(parsed.get("parent_memory_ids", []))
        distractors = [m for m in all_exposed if m not in honest_parents]

        if distractors:
            parsed["parent_memory_ids"] = [distractors[0]]
        else:
            parsed["parent_memory_ids"] = ["mem_hallucinated_001"]

        resp_text = json.dumps(parsed)
        return ModelCallResult(
            model_name=spec.model_name,
            model_digest="sha256:false_citation_digest",
            call_spec=spec,
            request_payload=spec.to_request_payload(),
            raw_response_text=resp_text,
            parsed_json=parsed,
            prompt_tokens=honest_res.prompt_tokens,
            completion_tokens=len(resp_text.split()),
            latency_ms=1.0,
        )


class StochasticClient(HonestClient):
    """Calibration Client 4: Stochastic - exhibits random non-deterministic variation to calibrate S0."""

    def __init__(self, flip_probability: float = 0.5):
        super().__init__()
        self.flip_probability = flip_probability

    def chat(self, spec: CallSpec) -> ModelCallResult:
        honest_res = super().chat(spec)
        parsed = dict(honest_res.parsed_json or {})

        import random
        rng = random.Random()
        if rng.random() < self.flip_probability:
            if "answer" in parsed and isinstance(parsed["answer"], dict):
                parsed["answer"]["object"] = f"STOCHASTIC_FLIPPED_{rng.randint(10000, 99999)}"

        resp_text = json.dumps(parsed)
        return ModelCallResult(
            model_name=spec.model_name,
            model_digest="sha256:stochastic_digest",
            call_spec=spec,
            request_payload=spec.to_request_payload(),
            raw_response_text=resp_text,
            parsed_json=parsed,
            prompt_tokens=honest_res.prompt_tokens,
            completion_tokens=len(resp_text.split()),
            latency_ms=1.0,
        )


class RedundantSupportClient(HonestClient):
    """Calibration Client 5: Redundant Support - solves via alternative complete paths if one path is removed."""

    def chat(self, spec: CallSpec) -> ModelCallResult:
        # Honest deduction already searches all present memories
        # If alternative independent memories exist, it successfully derives from them
        return super().chat(spec)

