"""Standardized Exploration Harness for parallel agentic exploration.

Enforces uniform provenance tracking, model digest auditing, prompt hash verification,
schema answer-leak detection, and atomic persistence across all exploratory branches.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import time
from typing import Any
from pydantic import BaseModel, Field

from gene.ollama_client import CallSpec, OllamaClient, ModelCallResult


class ExplorationCallRecord(BaseModel):
    """Auditable atomic record of an exploratory LLM invocation."""
    model_config = {"protected_namespaces": ()}

    call_id: str
    run_id: str
    track_name: str
    model_name: str
    model_digest: str
    prompt_sha256: str
    system_prompt: str
    user_prompt: str
    raw_response_text: str
    parsed_json: dict[str, Any] | None = None
    emitted_claim: str = "UNKNOWN"
    evidence_status: str = "insufficient"
    cited_memory_ids: list[str] = Field(default_factory=list)
    has_answer_leak: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExplorationHarness:
    """Unified execution harness preventing assay-layer wrapper drift in exploratory experiments."""

    def __init__(self, db_path: Path, track_name: str, client: OllamaClient | None = None):
        self.db_path = Path(db_path)
        self.track_name = track_name
        self.client = client or OllamaClient()
        self.run_id = f"run_{track_name}_{int(time.time())}"
        self._init_db()

    def _init_db(self) -> None:
        """Initialize standard exploration database tables with foreign keys and indexes."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS exploration_calls (
                call_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                track_name TEXT NOT NULL,
                model_name TEXT NOT NULL,
                model_digest TEXT NOT NULL,
                prompt_sha256 TEXT NOT NULL,
                system_prompt TEXT NOT NULL,
                user_prompt TEXT NOT NULL,
                raw_response_text TEXT NOT NULL,
                parsed_json TEXT,
                emitted_claim TEXT NOT NULL,
                evidence_status TEXT NOT NULL,
                cited_memory_ids TEXT NOT NULL,
                has_answer_leak INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_exp_calls_track ON exploration_calls(track_name)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_exp_calls_run ON exploration_calls(run_id)")
        conn.commit()
        conn.close()

    @staticmethod
    def audit_prompt_for_leakage(user_prompt: str, forbidden_answers: list[str]) -> bool:
        """Detect whether expected target answer strings or citation IDs are leaked into output schemas."""
        for ans in forbidden_answers:
            if not ans or len(ans) < 3:
                continue
            # Check if answer appears inside schema example blocks
            if f'"{ans}"' in user_prompt or f"'{ans}'" in user_prompt:
                # Disregard if it only appears in RULES or RETRIEVED MEMORIES
                prompt_lower = user_prompt.lower()
                schema_marker_idx = prompt_lower.rfind("schema")
                if schema_marker_idx != -1:
                    schema_section = user_prompt[schema_marker_idx:]
                    if ans in schema_section:
                        return True
        return False

    def execute_call(
        self,
        call_id: str,
        spec: CallSpec,
        forbidden_schema_leaks: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExplorationCallRecord:
        """Execute call via OllamaClient and persist standardized record."""
        meta = dict(metadata or {})
        prompt_sha256 = hashlib.sha256(spec.user_prompt.encode("utf-8")).hexdigest()

        # Audit prompt for schema leaks
        has_leak = False
        if forbidden_schema_leaks:
            has_leak = self.audit_prompt_for_leakage(spec.user_prompt, forbidden_schema_leaks)

        # Execute through OllamaClient
        call_res = self.client.chat(spec)
        data = call_res.parsed_json or {}

        # Extract normalized claim & citations
        val = (
            data.get("protocol")
            or data.get("route")
            or data.get("auth_code")
            or data.get("adjudicated_protocol")
            or data.get("derived_value")
            or "UNKNOWN"
        )
        val_str = str(val).strip().upper()
        status_str = str(data.get("evidence_status", "insufficient")).strip().lower()
        raw_cited = data.get("cited_memory_ids") or data.get("cited_reports") or data.get("parent_memory_ids") or []
        if isinstance(raw_cited, list):
            cited_list = [str(x) for x in raw_cited]
        else:
            cited_list = []

        record = ExplorationCallRecord(
            call_id=call_id,
            run_id=self.run_id,
            track_name=self.track_name,
            model_name=call_res.model_name,
            model_digest=call_res.model_digest,
            prompt_sha256=prompt_sha256,
            system_prompt=spec.system_prompt,
            user_prompt=spec.user_prompt,
            raw_response_text=call_res.raw_response_text,
            parsed_json=data,
            emitted_claim=val_str,
            evidence_status=status_str,
            cited_memory_ids=cited_list,
            has_answer_leak=has_leak,
            metadata=meta,
            latency_ms=call_res.latency_ms,
        )

        # Persist to standard table
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO exploration_calls
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.call_id,
            record.run_id,
            record.track_name,
            record.model_name,
            record.model_digest,
            record.prompt_sha256,
            record.system_prompt,
            record.user_prompt,
            record.raw_response_text,
            json.dumps(record.parsed_json),
            record.emitted_claim,
            record.evidence_status,
            json.dumps(record.cited_memory_ids),
            1 if record.has_answer_leak else 0,
            json.dumps(record.metadata),
            record.latency_ms,
            record.created_at,
        ))
        conn.commit()
        conn.close()

        return record
