"""Round 4 Epistemic Conformance Evaluators and Persistence Layer.

Provides structured response parsing, numeric conformance metrics (K_A, K_S, K_L, K_role, K_mono, K_I),
and SQLite persistence for Round 4 experimental evaluations.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any
from pydantic import BaseModel, Field


class ParsedModelResponse(BaseModel):
    """Normalized response parsed from model JSON output."""
    station: str = ""
    protocol: str = "UNKNOWN"
    reported_support_path: str | None = None
    perceived_independent_roots: int | None = None
    evidence_status: str = "insufficient"
    raw_text: str = ""
    is_valid_json: bool = False


class ConformanceEvaluation(BaseModel):
    """Contemporaneous evaluation record for an individual call."""
    call_id: str
    track: str
    condition_id: str
    station: str
    expected_protocol: str
    predicted_protocol: str
    k_a: int  # 1 if predicted == expected else 0
    k_s: int | None = None  # 1 if reported support matches valid S_F else 0
    k_l: int | None = None  # 1 if perceived roots matches ground truth else 0
    k_role: int | None = None
    k_mono: int | None = None
    k_i: int | None = None
    prompt_hash: str
    state_hash: str
    compiler_pipeline: str
    raw_output: str


def parse_round4_model_output(raw_text: str) -> ParsedModelResponse:
    """Parse strict or markdown-fenced JSON output into ParsedModelResponse."""
    clean_text = raw_text.strip()
    if "```json" in clean_text:
        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
    elif "```" in clean_text:
        clean_text = clean_text.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(clean_text)
        return ParsedModelResponse(
            station=str(data.get("station", "")).strip(),
            protocol=str(data.get("protocol", "UNKNOWN")).strip(),
            reported_support_path=data.get("reported_support_path"),
            perceived_independent_roots=data.get("perceived_independent_roots"),
            evidence_status=str(data.get("evidence_status", "insufficient")).strip(),
            raw_text=raw_text,
            is_valid_json=True,
        )
    except Exception:
        # Fallback heuristic extraction
        protocol = "UNKNOWN"
        if "PROTO_X7" in raw_text:
            protocol = "PROTO_X7"
        return ParsedModelResponse(
            protocol=protocol,
            raw_text=raw_text,
            is_valid_json=False,
        )


def evaluate_conformance_k_a(predicted: str, expected: str) -> int:
    """K_A: Answer conformance."""
    return 1 if predicted.strip().upper() == expected.strip().upper() else 0


def evaluate_conformance_k_s(reported_path: str | None, valid_paths: list[str]) -> int:
    """K_S: Support conformance (reported path must belong to valid S_F paths)."""
    if not reported_path or reported_path.lower() in ["none", "null"]:
        return 0
    return 1 if reported_path in valid_paths else 0


def evaluate_conformance_k_l(perceived_roots: int | None, expected_roots: int) -> int:
    """K_L: Lineage conformance (perceived root count matches ground truth)."""
    if perceived_roots is None:
        return 0
    return 1 if perceived_roots == expected_roots else 0


def init_round4_db(db_path: str) -> None:
    """Initialize SQLite tables for Round 4 evaluations."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS round4_conformance_evaluations (
            call_id TEXT PRIMARY KEY,
            track TEXT NOT NULL,
            condition_id TEXT NOT NULL,
            station TEXT NOT NULL,
            expected_protocol TEXT NOT NULL,
            predicted_protocol TEXT NOT NULL,
            k_a INTEGER NOT NULL,
            k_s INTEGER,
            k_l INTEGER,
            k_role INTEGER,
            k_mono INTEGER,
            k_i INTEGER,
            prompt_hash TEXT NOT NULL,
            state_hash TEXT NOT NULL,
            compiler_pipeline TEXT NOT NULL,
            raw_output TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def persist_round4_evaluation(db_path: str, eval_record: ConformanceEvaluation) -> None:
    """Persist an evaluation record to SQLite."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO round4_conformance_evaluations (
            call_id, track, condition_id, station, expected_protocol, predicted_protocol,
            k_a, k_s, k_l, k_role, k_mono, k_i, prompt_hash, state_hash, compiler_pipeline, raw_output
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        eval_record.call_id, eval_record.track, eval_record.condition_id, eval_record.station,
        eval_record.expected_protocol, eval_record.predicted_protocol, eval_record.k_a,
        eval_record.k_s, eval_record.k_l, eval_record.k_role, eval_record.k_mono, eval_record.k_i,
        eval_record.prompt_hash, eval_record.state_hash, eval_record.compiler_pipeline, eval_record.raw_output
    ))
    conn.commit()
    conn.close()
