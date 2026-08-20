"""End-to-End Production Smoke & Relational Metric Property Tests for Round 4."""

import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.ollama_client import CallSpec, ModelCallResult
from gene.experiments.evaluators_round4 import (
    evaluate_track_m_chain,
    evaluate_track_p_panel,
    evaluate_track_r_panel,
    parse_round4_model_output,
)
from scripts.explore_round4.run_track_r import run_track_r
from scripts.explore_round4.run_track_p import run_track_p
from scripts.explore_round4.run_track_m import run_track_m
from scripts.explore_round4.run_track_c import run_track_c


class ProductionCompatibleFakeClient:
    """Fake client adhering 100% to production OllamaClient.chat(CallSpec) -> ModelCallResult."""
    def __init__(self, fixed_protocol: str = "PROTO_X7"):
        self.fixed_protocol = fixed_protocol
        self.call_specs: list[CallSpec] = []

    def chat(self, spec: CallSpec) -> ModelCallResult:
        self.call_specs.append(spec)
        response_json = json.dumps({
            "station": "VELORA",
            "protocol": self.fixed_protocol,
            "reported_support_path": "path_AB",
            "independence_status": "determinable",
            "perceived_independent_roots": 1,
            "evidence_status": "sufficient",
        })
        spec_sha = hashlib.sha256(spec.model_dump_json().encode("utf-8")).hexdigest()
        return ModelCallResult(
            model_name=spec.model_name,
            model_digest="fake_sha256_digest_12345",
            call_spec=spec,
            request_payload={"model": spec.model_name, "prompt": spec.user_prompt},
            raw_response_text=response_json,
            parsed_json=json.loads(response_json),
            latency_ms=45.2,
        )


def test_relational_metric_evaluators_synthetic_patterns():
    """Verify that relational metrics K_I, K_mono, and K_role evaluate panel-level properties correctly."""
    # 1. Track P: Invariance violation when 1 of 24 permutations flips to UNKNOWN
    predictions_23_1 = ["PROTO_X7"] * 23 + ["UNKNOWN"]
    metrics_p = evaluate_track_p_panel(predictions_23_1)
    assert metrics_p.disagreement_rate > 0.0, "D_perm failed to detect flip!"
    assert metrics_p.k_i < 1.0, "K_I should be less than 1.0 under disagreement"
    assert metrics_p.flip_count == 1

    # Invariance perfect when 24 of 24 are UNKNOWN
    predictions_all_unk = ["UNKNOWN"] * 24
    metrics_p_unk = evaluate_track_p_panel(predictions_all_unk)
    assert metrics_p_unk.disagreement_rate == 0.0
    assert metrics_p_unk.k_i == 1.0, "K_I must be 1.0 when perfectly invariant, even if UNKNOWN!"

    # 2. Track M: Success-to-Error transition in X7 -> UNKNOWN -> X7 -> X7
    chain_with_collapse = ["PROTO_X7", "UNKNOWN", "PROTO_X7", "PROTO_X7"]
    metrics_m = evaluate_track_m_chain(chain_with_collapse)
    assert metrics_m.success_to_error_count == 1, "Failed to count S->E transition!"
    assert metrics_m.is_monotonically_preserved is False
    assert metrics_m.k_mono == 0

    # Perfect monotonic chain
    chain_clean = ["PROTO_X7", "PROTO_X7", "PROTO_X7", "PROTO_X7"]
    metrics_m_clean = evaluate_track_m_chain(chain_clean)
    assert metrics_m_clean.success_to_error_count == 0
    assert metrics_m_clean.is_monotonically_preserved is True
    assert metrics_m_clean.k_mono == 1

    # 3. Track R: Semantic role inversion classification
    canonical_preds = {"point_cross_BD": "PROTO_X7", "point_cross_AE": "UNKNOWN"}
    swapped_preds = {"point_cross_BD": "UNKNOWN", "point_cross_AE": "PROTO_X7"}  # Inverted!
    opaque_preds = {"point_cross_BD": "UNKNOWN", "point_cross_AE": "UNKNOWN"}
    metrics_r = evaluate_track_r_panel(canonical_preds, swapped_preds, opaque_preds)
    assert metrics_r.swapped_shortcut_inverted is True
    assert metrics_r.classification == "semantic_role_driven"

    # Graph slot retained classification
    swapped_slot_preds = {"point_cross_BD": "PROTO_X7", "point_cross_AE": "UNKNOWN"}  # Retained at BD!
    metrics_r_slot = evaluate_track_r_panel(canonical_preds, swapped_slot_preds, opaque_preds)
    assert metrics_r_slot.swapped_slot_retained is True
    assert metrics_r_slot.classification == "graph_slot_driven"


def test_production_callspec_smoke_all_runners_end_to_end():
    """End-to-end production smoke test proving CallSpec -> ModelCallResult -> parse -> immutable DB."""
    client = ProductionCompatibleFakeClient(fixed_protocol="PROTO_X7")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_production_smoke_r4.db")

        # Track R
        evals_r, m_r = run_track_r(client, db_path, max_calls=1)
        assert len(evals_r) == 1
        assert evals_r[0].k_a == 1

        # Track P
        evals_p, m_p = run_track_p(client, db_path, max_calls=1)
        assert len(evals_p) == 1
        assert evals_p[0].k_a == 1

        # Track M
        evals_m, m_m = run_track_m(client, db_path, max_calls=1)
        assert len(evals_m) == 1
        assert evals_m[0].k_a == 1

        # Track C
        evals_c = run_track_c(client, db_path, max_calls=1)
        assert len(evals_c) == 1
        assert evals_c[0].k_a == 1
        assert evals_c[0].k_s == 1

        # Verify SQLite tables (both round4_calls and round4_evaluations)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM round4_calls")
        call_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM round4_evaluations")
        eval_count = cur.fetchone()[0]

        assert call_count == 4
        assert eval_count == 4

        # Verify foreign key / call_id linkage
        cur.execute("""
            SELECT c.call_id, c.call_spec_sha256, c.model_digest, e.k_a
            FROM round4_calls c
            JOIN round4_evaluations e ON c.call_id = e.call_id
        """)
        rows = cur.fetchall()
        assert len(rows) == 4
        for row in rows:
            assert row[1] is not None  # call_spec_sha256 present
            assert row[2] == "fake_sha256_digest_12345"  # model_digest present
            assert row[3] == 1  # k_a == 1

        conn.close()
