"""Standardized Exploration Harness for parallel agentic exploration.

Enforces uniform provenance tracking, full CallSpec hashing, model digest auditing,
pre-execution lexical leakage prevention, structured evaluation logging, and immutable append-only persistence.
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


class LexicalLeakageError(RuntimeError):
    """Raised when an experimental prompt template contains forbidden ground-truth tokens in its schema section."""


class ExplorationCallRecord(BaseModel):
    """Auditable atomic record of an exploratory LLM invocation."""
    model_config = {"protected_namespaces": ()}

    call_id: str
    run_id: str
    track_name: str
    model_name: str
    model_digest: str
    call_spec_sha256: str
    prompt_sha256: str
    system_prompt: str
    user_prompt: str
    temperature: float = 0.0
    seed: int | None = 42
    format: str = "json"
    raw_response_text: str
    parsed_json: dict[str, Any] | None = None
    emitted_claim: str = "UNKNOWN"
    evidence_status: str = "insufficient"
    cited_memory_ids: list[str] = Field(default_factory=list)
    has_lexical_leak: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExplorationEvaluationRecord(BaseModel):
    """Structured evaluation record linking a call to canonical/local oracle phenotypes."""
    model_config = {"protected_namespaces": ()}

    eval_id: str
    call_id: str
    run_id: str
    canonical_status: str = "UNKNOWN"
    local_status: str = "UNKNOWN"
    dual_oracle_phenotype: str = "UNKNOWN"
    is_contract_compliant: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExplorationHarness:
    """Unified execution harness preventing assay-layer wrapper drift in exploratory experiments."""

    def __init__(
        self,
        db_path: Path,
        track_name: str,
        client: OllamaClient | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.db_path = Path(db_path)
        self.track_name = track_name
        self.client = client or OllamaClient()
        self.run_id = f"run_{track_name}_{int(time.time())}"
        self.config = config or {}
        self._init_db()

    def _init_db(self) -> None:
        """Initialize standard exploration database tables with foreign keys and indexes."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")

        # 1. Runs Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS exploration_runs (
                run_id TEXT PRIMARY KEY,
                track_name TEXT NOT NULL,
                started_at TEXT NOT NULL,
                config_json TEXT NOT NULL
            )
        """)

        # 2. Calls Table (Append-Only)
        c.execute("""
            CREATE TABLE IF NOT EXISTS exploration_calls (
                call_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                track_name TEXT NOT NULL,
                model_name TEXT NOT NULL,
                model_digest TEXT NOT NULL,
                call_spec_sha256 TEXT NOT NULL,
                prompt_sha256 TEXT NOT NULL,
                system_prompt TEXT NOT NULL,
                user_prompt TEXT NOT NULL,
                temperature REAL NOT NULL,
                seed INTEGER,
                format TEXT NOT NULL,
                raw_response_text TEXT NOT NULL,
                parsed_json TEXT,
                emitted_claim TEXT NOT NULL,
                evidence_status TEXT NOT NULL,
                cited_memory_ids TEXT NOT NULL,
                has_lexical_leak INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES exploration_runs(run_id)
            )
        """)

        # 3. Evaluations Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS exploration_evaluations (
                eval_id TEXT PRIMARY KEY,
                call_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                canonical_status TEXT NOT NULL,
                local_status TEXT NOT NULL,
                dual_oracle_phenotype TEXT NOT NULL,
                is_contract_compliant INTEGER NOT NULL,
                eval_metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (call_id) REFERENCES exploration_calls(call_id),
                FOREIGN KEY (run_id) REFERENCES exploration_runs(run_id)
            )
        """)

        c.execute("CREATE INDEX IF NOT EXISTS idx_exp_calls_track ON exploration_calls(track_name)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_exp_calls_run ON exploration_calls(run_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_exp_evals_call ON exploration_evaluations(call_id)")

        # Record Run Entry
        c.execute("""
            INSERT OR IGNORE INTO exploration_runs
            VALUES (?, ?, ?, ?)
        """, (
            self.run_id,
            self.track_name,
            datetime.now(timezone.utc).isoformat(),
            json.dumps(self.config),
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def audit_prompt_for_lexical_leakage(user_prompt: str, forbidden_tokens: list[str]) -> tuple[bool, list[str]]:
        """Audit prompt schema section for literal leakage of ground-truth answers or target IDs.
        
        Note: This is a surface-level lexical leak audit, not an exhaustive semantic leak detector.
        """
        leaked = []
        prompt_lower = user_prompt.lower()
        schema_marker_idx = max(prompt_lower.rfind("schema"), prompt_lower.rfind("return strictly"))

        if schema_marker_idx != -1:
            schema_section = user_prompt[schema_marker_idx:]
            for tok in forbidden_tokens:
                if not tok or len(tok) < 3:
                    continue
                # If the exact token appears in the schema specification block
                if f'"{tok}"' in schema_section or f"'{tok}'" in schema_section or tok in schema_section:
                    leaked.append(tok)

        return len(leaked) > 0, leaked

    @staticmethod
    def compute_call_spec_sha256(spec: CallSpec) -> str:
        """Compute authoritative SHA-256 digest over the full canonical CallSpec payload."""
        payload = spec.to_request_payload()
        canonical_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def execute_call(
        self,
        call_id: str,
        spec: CallSpec,
        forbidden_schema_leaks: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        fail_on_lexical_leak: bool = True,
    ) -> ExplorationCallRecord:
        """Execute call via OllamaClient with pre-execution leak prevention and append-only persistence."""
        meta = dict(metadata or {})
        call_spec_sha256 = self.compute_call_spec_sha256(spec)
        prompt_sha256 = hashlib.sha256(spec.user_prompt.encode("utf-8")).hexdigest()

        # 1. Pre-Execution Lexical Leak Audit
        has_leak = False
        leaked_tokens = []
        if forbidden_schema_leaks:
            has_leak, leaked_tokens = self.audit_prompt_for_lexical_leakage(spec.user_prompt, forbidden_schema_leaks)
            if has_leak and fail_on_lexical_leak:
                raise LexicalLeakageError(
                    f"Pre-execution lexical leak audit failed for call '{call_id}': "
                    f"Forbidden tokens {leaked_tokens} found in prompt schema template."
                )

        # 2. Execute through OllamaClient
        call_res = self.client.chat(spec)
        data = call_res.parsed_json or {}

        # 3. Extract Normalized Output Fields
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
        raw_cited = (
            data.get("cited_memory_ids")
            or data.get("cited_reports")
            or data.get("parent_memory_ids")
            or []
        )
        if isinstance(raw_cited, list):
            cited_list = [str(x) for x in raw_cited]
        else:
            cited_list = []

        format_str = spec.format if isinstance(spec.format, str) else json.dumps(spec.format)

        record = ExplorationCallRecord(
            call_id=call_id,
            run_id=self.run_id,
            track_name=self.track_name,
            model_name=call_res.model_name,
            model_digest=call_res.model_digest,
            call_spec_sha256=call_spec_sha256,
            prompt_sha256=prompt_sha256,
            system_prompt=spec.system_prompt,
            user_prompt=spec.user_prompt,
            temperature=spec.temperature,
            seed=spec.seed,
            format=format_str,
            raw_response_text=call_res.raw_response_text,
            parsed_json=data,
            emitted_claim=val_str,
            evidence_status=status_str,
            cited_memory_ids=cited_list,
            has_lexical_leak=has_leak,
            metadata=meta,
            latency_ms=call_res.latency_ms,
        )

        # 4. Strict Immutable Append-Only Persistence (Fail on duplicate call_id)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""
            INSERT INTO exploration_calls
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.call_id,
            record.run_id,
            record.track_name,
            record.model_name,
            record.model_digest,
            record.call_spec_sha256,
            record.prompt_sha256,
            record.system_prompt,
            record.user_prompt,
            record.temperature,
            record.seed,
            record.format,
            record.raw_response_text,
            json.dumps(record.parsed_json),
            record.emitted_claim,
            record.evidence_status,
            json.dumps(record.cited_memory_ids),
            1 if record.has_lexical_leak else 0,
            json.dumps(record.metadata),
            record.latency_ms,
            record.created_at,
        ))
        conn.commit()
        conn.close()

        return record

    def record_evaluation(
        self,
        call_id: str,
        canonical_status: str,
        local_status: str,
        dual_oracle_phenotype: str,
        is_contract_compliant: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> ExplorationEvaluationRecord:
        """Persist structured DualOracle classification for a completed call."""
        eval_id = f"eval_{call_id}"
        meta = dict(metadata or {})
        rec = ExplorationEvaluationRecord(
            eval_id=eval_id,
            call_id=call_id,
            run_id=self.run_id,
            canonical_status=canonical_status,
            local_status=local_status,
            dual_oracle_phenotype=dual_oracle_phenotype,
            is_contract_compliant=is_contract_compliant,
            metadata=meta,
        )

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""
            INSERT INTO exploration_evaluations
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec.eval_id,
            rec.call_id,
            rec.run_id,
            rec.canonical_status,
            rec.local_status,
            rec.dual_oracle_phenotype,
            1 if rec.is_contract_compliant else 0,
            json.dumps(rec.metadata),
            rec.created_at,
        ))
        conn.commit()
        conn.close()

        return rec
