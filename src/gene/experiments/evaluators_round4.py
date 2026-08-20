"""Round 4 Epistemic Conformance Evaluators and Append-Only SQLite Persistence Layer (v3).

Provides:
1. Backend-neutral evidence support evaluation (K_S) mapping reported DOC/EVID indices to S_F.
2. Relational panel evaluators with baseline replication guards and epsilon_replay computation.
3. Schema compliance and strict contract validation.
4. Relational evaluation persistence table (round4_relational_evaluations).
"""

from __future__ import annotations

import json
import math
import sqlite3
from typing import Any, Literal
from pydantic import BaseModel, Field
from gene.ollama_client import CallSpec, ModelCallResult


FROZEN_ROUND4_SYSTEM_PROMPT = (
    "You are an epistemic reasoning assistant. "
    "Analyze the provided authorization rules and retrieved episodic evidence strictly. "
    "Do not extrapolate or assume unstated facts. "
    "Return your analysis strictly formatted as a valid JSON object matching the requested schema."
)


class ParsedModelResponse(BaseModel):
    """Normalized response parsed from model JSON output."""
    station: str = ""
    protocol: str = "UNKNOWN"
    reported_support_evidence: list[str] = Field(default_factory=list)
    independence_status: str = "indeterminable"  # "determinable" | "indeterminable"
    perceived_independent_roots: int | None = None
    evidence_status: str = "insufficient"
    raw_text: str = ""
    is_valid_json: bool = False


class TrackPMetrics(BaseModel):
    """Relational permutation panel metrics across permutations of the same state."""
    sample_size: int
    output_distribution: dict[str, int]
    output_entropy: float  # H_perm
    disagreement_rate: float  # D_perm
    flip_count: int  # N_flip from modal output
    k_i: float  # Invariance score = 1.0 - D_perm
    worst_case_accuracy: float
    canonical_replay_sample_size: int = 0
    canonical_replay_disagreement_rate: float = 0.0  # epsilon_replay


class TrackMMetrics(BaseModel):
    """Relational chain metrics across augmentation steps."""
    chain_name: str
    steps_count: int
    step_predictions: list[str]
    success_to_error_count: int  # S -> E transitions
    is_monotonically_preserved: bool
    k_mono: int  # 1 if preserved else 0


class TrackRMetrics(BaseModel):
    """Relational role equivariance dissection metrics across representation conditions."""
    canonical_shortcut_active: bool  # BD == PROTO_X7 and AE == UNKNOWN
    swapped_shortcut_inverted: bool  # AE == PROTO_X7 and BD == UNKNOWN (semantic role driven)
    swapped_slot_retained: bool      # BD == PROTO_X7 and AE == UNKNOWN (graph slot driven)
    opaque_shortcut_suppressed: bool # BD == UNKNOWN and AE == UNKNOWN (lexical prior suppressed)
    role_follow_ratio: float
    classification: Literal[
        "baseline_shortcut_not_replicated",
        "semantic_role_driven",
        "graph_slot_driven",
        "lexical_prior_suppressed",
        "mixed_or_unclassified",
    ]


class CallRecord(BaseModel):
    """Immutable record of an individual LLM invocation."""
    call_id: str
    track: str
    call_spec_sha256: str
    model_name: str
    model_digest: str | None = None
    system_prompt: str
    user_prompt: str
    temperature: float
    seed: int | None = None
    format: str = "json"
    raw_response_text: str
    latency_ms: float = 0.0


class EvaluationRecord(BaseModel):
    """Contemporaneous evaluation record linked to a call."""
    call_id: str
    track: str
    condition_id: str
    station: str
    expected_protocol: str
    predicted_protocol: str
    reported_support_evidence: list[str] = Field(default_factory=list)
    independence_status: str = "indeterminable"
    perceived_independent_roots: int | None = None
    is_valid_json: int = 1
    k_a: int  # 1 if predicted == expected and is_valid_json == 1 else 0
    k_s: int | None = None  # 1 if reported evidence satisfies valid S_F else 0
    k_l: int | None = None  # 1 if perceived roots matches ground truth else 0
    prompt_hash: str
    state_hash: str
    compiler_pipeline: str


def parse_round4_model_output(raw_text: str) -> ParsedModelResponse:
    """Parse strict JSON output into ParsedModelResponse."""
    clean_text = raw_text.strip()
    if "```json" in clean_text:
        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
    elif "```" in clean_text:
        clean_text = clean_text.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(clean_text)
        
        roots_val = data.get("perceived_independent_roots")
        if isinstance(roots_val, str):
            try:
                roots_val = int(roots_val)
            except ValueError:
                roots_val = None

        # Parse reported evidence support
        evid = data.get("reported_support_evidence", [])
        if isinstance(evid, str):
            evid = [evid]
        elif not isinstance(evid, list):
            evid = []

        return ParsedModelResponse(
            station=str(data.get("station", "")).strip(),
            protocol=str(data.get("protocol", "UNKNOWN")).strip(),
            reported_support_evidence=[str(x).strip() for x in evid],
            independence_status=str(data.get("independence_status", "indeterminable")).strip(),
            perceived_independent_roots=roots_val,
            evidence_status=str(data.get("evidence_status", "insufficient")).strip(),
            raw_text=raw_text,
            is_valid_json=True,
        )
    except Exception:
        return ParsedModelResponse(
            protocol="UNKNOWN",
            raw_text=raw_text,
            is_valid_json=False,
        )


def evaluate_conformance_k_a(predicted: str, expected: str, is_valid_json: bool = True) -> int:
    """K_A: Answer conformance (requires strict valid JSON)."""
    if not is_valid_json:
        return 0
    return 1 if predicted.strip().upper() == expected.strip().upper() else 0


def evaluate_conformance_k_s_neutral(
    reported_evidence: list[str],
    evidence_to_claim_map: dict[str, str],
    valid_support_paths_claim_sets: list[set[str]],
) -> int:
    """Backend-neutral K_S evaluation:
    Maps reported evidence tags (e.g. DOC_01, EVID_A) to semantic claims,
    and checks if the reported claims contain any valid minimal support path.
    """
    if not reported_evidence or not valid_support_paths_claim_sets:
        return 0

    reported_claims = set()
    for tag in reported_evidence:
        clean_tag = tag.strip("[] ,")
        if clean_tag in evidence_to_claim_map:
            reported_claims.add(evidence_to_claim_map[clean_tag])

    # Check if reported claims contain at least one complete minimal support path
    for path_claims in valid_support_paths_claim_sets:
        if path_claims.issubset(reported_claims):
            return 1
    return 0


def evaluate_conformance_k_l(independence_status: str, perceived_roots: int | None, expected_roots: int | None) -> tuple[bool, int | None]:
    """K_L: Lineage conformance (perceived root count matches ground truth when determinable)."""
    if independence_status == "indeterminable" or perceived_roots is None or expected_roots is None:
        return False, None
    return True, (1 if perceived_roots == expected_roots else 0)


def evaluate_track_p_panel(
    raw_predictions: list[str],
    canonical_replay_predictions: list[str] | None = None,
    expected: str = "PROTO_X7",
) -> TrackPMetrics:
    """Evaluate relational permutation metrics across 24 raw flat permutations + canonical replays."""
    n = len(raw_predictions)
    if n == 0:
        return TrackPMetrics(sample_size=0, output_distribution={}, output_entropy=0.0, disagreement_rate=0.0, flip_count=0, k_i=1.0, worst_case_accuracy=0.0)

    dist: dict[str, int] = {}
    for p in raw_predictions:
        dist[p] = dist.get(p, 0) + 1

    entropy = 0.0
    for count in dist.values():
        prob = count / n
        entropy -= prob * math.log2(prob)

    pairs_count = 0
    disagreements = 0
    for i in range(n):
        for j in range(i + 1, n):
            pairs_count += 1
            if raw_predictions[i] != raw_predictions[j]:
                disagreements += 1

    d_perm = disagreements / pairs_count if pairs_count > 0 else 0.0
    k_i = 1.0 - d_perm

    modal_output = max(dist.keys(), key=lambda k: dist[k])
    flips = sum(1 for p in raw_predictions if p != modal_output)

    accs = [1.0 if p == expected else 0.0 for p in raw_predictions]
    worst_acc = min(accs) if accs else 0.0

    # Calculate epsilon_replay for canonical replays
    eps_replay = 0.0
    n_rep = 0
    if canonical_replay_predictions and len(canonical_replay_predictions) > 1:
        n_rep = len(canonical_replay_predictions)
        rep_pairs = 0
        rep_disagreements = 0
        for i in range(n_rep):
            for j in range(i + 1, n_rep):
                rep_pairs += 1
                if canonical_replay_predictions[i] != canonical_replay_predictions[j]:
                    rep_disagreements += 1
        eps_replay = rep_disagreements / rep_pairs if rep_pairs > 0 else 0.0

    return TrackPMetrics(
        sample_size=n,
        output_distribution=dist,
        output_entropy=round(entropy, 4),
        disagreement_rate=round(d_perm, 4),
        flip_count=flips,
        k_i=round(k_i, 4),
        worst_case_accuracy=worst_acc,
        canonical_replay_sample_size=n_rep,
        canonical_replay_disagreement_rate=round(eps_replay, 4),
    )


def evaluate_track_m_chain(chain_predictions: list[str], chain_name: str = "chain", expected: str = "PROTO_X7") -> TrackMMetrics:
    """Evaluate relational monotonicity transitions along an augmentation sequence."""
    s_to_e = 0
    for k in range(len(chain_predictions) - 1):
        curr_p = chain_predictions[k]
        next_p = chain_predictions[k + 1]
        if curr_p == expected and next_p != expected:
            s_to_e += 1

    is_preserved = (s_to_e == 0 and all(p == expected for p in chain_predictions))
    return TrackMMetrics(
        chain_name=chain_name,
        steps_count=len(chain_predictions),
        step_predictions=chain_predictions,
        success_to_error_count=s_to_e,
        is_monotonically_preserved=is_preserved,
        k_mono=1 if is_preserved else 0,
    )


def evaluate_track_r_panel(
    canonical_preds: dict[str, str],
    swapped_preds: dict[str, str],
    opaque_preds: dict[str, str],
) -> TrackRMetrics:
    """Evaluate relational role equivariance dissection across conditions with baseline replication guard."""
    can_bd = canonical_preds.get("point_cross_BD", "UNKNOWN")
    can_ae = canonical_preds.get("point_cross_AE", "UNKNOWN")

    swp_bd = swapped_preds.get("point_cross_BD", "UNKNOWN")
    swp_ae = swapped_preds.get("point_cross_AE", "UNKNOWN")

    opq_bd = opaque_preds.get("point_cross_BD", "UNKNOWN")
    opq_ae = opaque_preds.get("point_cross_AE", "UNKNOWN")

    can_shortcut = (can_bd == "PROTO_X7" and can_ae == "UNKNOWN")
    swp_inverted = (swp_ae == "PROTO_X7" and swp_bd == "UNKNOWN")
    swp_retained = (swp_bd == "PROTO_X7" and swp_ae == "UNKNOWN")
    opq_suppressed = (opq_bd == "UNKNOWN" and opq_ae == "UNKNOWN")

    # Guard: Require canonical shortcut replication before declaring mechanisms!
    if not can_shortcut:
        classification = "baseline_shortcut_not_replicated"
        ratio = 0.0
    elif swp_inverted and not swp_retained:
        classification = "semantic_role_driven"
        ratio = 1.0
    elif swp_retained and not swp_inverted:
        classification = "graph_slot_driven"
        ratio = 0.0
    elif opq_suppressed:
        classification = "lexical_prior_suppressed"
        ratio = 0.5
    else:
        classification = "mixed_or_unclassified"
        ratio = 0.0

    return TrackRMetrics(
        canonical_shortcut_active=can_shortcut,
        swapped_shortcut_inverted=swp_inverted,
        swapped_slot_retained=swp_retained,
        opaque_shortcut_suppressed=opq_suppressed,
        role_follow_ratio=ratio,
        classification=classification,
    )


def init_round4_db(db_path: str) -> None:
    """Initialize strictly append-only SQLite tables for Round 4."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS round4_calls (
            call_id TEXT PRIMARY KEY,
            track TEXT NOT NULL,
            call_spec_sha256 TEXT NOT NULL,
            model_name TEXT NOT NULL,
            model_digest TEXT,
            system_prompt TEXT NOT NULL,
            user_prompt TEXT NOT NULL,
            temperature REAL NOT NULL,
            seed INTEGER,
            format TEXT NOT NULL,
            raw_response_text TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS round4_evaluations (
            call_id TEXT PRIMARY KEY,
            track TEXT NOT NULL,
            condition_id TEXT NOT NULL,
            station TEXT NOT NULL,
            expected_protocol TEXT NOT NULL,
            predicted_protocol TEXT NOT NULL,
            reported_support_evidence TEXT,
            independence_status TEXT NOT NULL,
            perceived_independent_roots INTEGER,
            is_valid_json INTEGER NOT NULL,
            k_a INTEGER NOT NULL,
            k_s INTEGER,
            k_l INTEGER,
            prompt_hash TEXT NOT NULL,
            state_hash TEXT NOT NULL,
            compiler_pipeline TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (call_id) REFERENCES round4_calls(call_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS round4_relational_evaluations (
            track TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value_numeric REAL,
            metric_value_text TEXT,
            payload_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (track, metric_name)
        )
    """)
    conn.commit()
    conn.close()


def persist_round4_call_and_evaluation(
    db_path: str,
    call_rec: CallRecord,
    eval_rec: EvaluationRecord,
) -> None:
    """Persist an immutable call and evaluation record to SQLite using strict INSERT."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO round4_calls (
            call_id, track, call_spec_sha256, model_name, model_digest, system_prompt,
            user_prompt, temperature, seed, format, raw_response_text, latency_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        call_rec.call_id, call_rec.track, call_rec.call_spec_sha256, call_rec.model_name,
        call_rec.model_digest, call_rec.system_prompt, call_rec.user_prompt,
        call_rec.temperature, call_rec.seed, call_rec.format,
        call_rec.raw_response_text, call_rec.latency_ms
    ))
    cur.execute("""
        INSERT INTO round4_evaluations (
            call_id, track, condition_id, station, expected_protocol, predicted_protocol,
            reported_support_evidence, independence_status, perceived_independent_roots,
            is_valid_json, k_a, k_s, k_l, prompt_hash, state_hash, compiler_pipeline
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        eval_rec.call_id, eval_rec.track, eval_rec.condition_id, eval_rec.station,
        eval_rec.expected_protocol, eval_rec.predicted_protocol, json.dumps(eval_rec.reported_support_evidence),
        eval_rec.independence_status, eval_rec.perceived_independent_roots,
        eval_rec.is_valid_json, eval_rec.k_a, eval_rec.k_s, eval_rec.k_l, eval_rec.prompt_hash,
        eval_rec.state_hash, eval_rec.compiler_pipeline
    ))
    conn.commit()
    conn.close()


def persist_round4_relational_evaluation(
    db_path: str,
    track: str,
    metric_name: str,
    metric_value_numeric: float | None,
    metric_value_text: str | None,
    payload: BaseModel | dict[str, Any],
) -> None:
    """Persist an immutable relational evaluation record to SQLite."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    payload_str = payload.model_dump_json() if isinstance(payload, BaseModel) else json.dumps(payload)
    cur.execute("""
        INSERT OR REPLACE INTO round4_relational_evaluations (
            track, metric_name, metric_value_numeric, metric_value_text, payload_json
        ) VALUES (?, ?, ?, ?, ?)
    """, (track, metric_name, metric_value_numeric, metric_value_text, payload_str))
    conn.commit()
    conn.close()
