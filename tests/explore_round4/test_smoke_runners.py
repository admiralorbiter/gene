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
    evaluate_conformance_k_s_neutral,
    evaluate_track_m_chain,
    evaluate_track_p_panel,
    evaluate_track_r_panel,
    parse_round4_model_output,
    persist_round4_relational_evaluation,
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
            "reported_support_evidence": ["DOC_01", "DOC_02"],
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
    metrics_p = evaluate_track_p_panel(predictions_23_1, canonical_replay_predictions=["PROTO_X7", "PROTO_X7", "PROTO_X7", "PROTO_X7"])
    assert metrics_p.disagreement_rate > 0.0, "D_perm failed to detect flip!"
    assert metrics_p.k_i < 1.0, "K_I should be less than 1.0 under disagreement"
    assert metrics_p.flip_count == 1
    assert metrics_p.canonical_replay_disagreement_rate == 0.0

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

    # 3. Track R: Guard against classifying when baseline shortcut is not replicated
    unreplicated_canonical = {"point_cross_BD": "UNKNOWN", "point_cross_AE": "UNKNOWN"}
    swapped_preds_inv = {"point_cross_BD": "UNKNOWN", "point_cross_AE": "PROTO_X7"}
    opaque_preds = {"point_cross_BD": "UNKNOWN", "point_cross_AE": "UNKNOWN"}
    metrics_r_unrep = evaluate_track_r_panel(unreplicated_canonical, swapped_preds_inv, opaque_preds)
    assert metrics_r_unrep.canonical_shortcut_active is False
    assert metrics_r_unrep.classification == "baseline_shortcut_not_replicated"

    # Semantic role inversion when baseline is active
    canonical_preds = {"point_cross_BD": "PROTO_X7", "point_cross_AE": "UNKNOWN"}
    metrics_r = evaluate_track_r_panel(canonical_preds, swapped_preds_inv, opaque_preds)
    assert metrics_r.swapped_shortcut_inverted is True
    assert metrics_r.classification == "semantic_role_driven"

    # Graph slot retained classification
    swapped_slot_preds = {"point_cross_BD": "PROTO_X7", "point_cross_AE": "UNKNOWN"}
    metrics_r_slot = evaluate_track_r_panel(canonical_preds, swapped_slot_preds, opaque_preds)
    assert metrics_r_slot.swapped_slot_retained is True
    assert metrics_r_slot.classification == "graph_slot_driven"


def test_backend_neutral_k_s_evidence_mapping():
    """Verify backend-neutral K_S evaluation via evidence-to-claim mapping."""
    evidence_to_claims = {
        "DOC_01": "claim_velora_nerin_manager",
        "DOC_02": "claim_velora_nerin_reports_s1",
        "DOC_03": "claim_velora_corin_duty",
    }
    gold_paths = [
        {"claim_velora_nerin_manager", "claim_velora_nerin_reports_s1"},  # path_AB
    ]

    # Valid reported evidence
    assert evaluate_conformance_k_s_neutral(["DOC_01", "DOC_02"], evidence_to_claims, gold_paths) == 1
    assert evaluate_conformance_k_s_neutral(["[DOC_01]", "[DOC_02]"], evidence_to_claims, gold_paths) == 1
    # Incomplete reported evidence
    assert evaluate_conformance_k_s_neutral(["DOC_01"], evidence_to_claims, gold_paths) == 0
    # Irrelevant reported evidence
    assert evaluate_conformance_k_s_neutral(["DOC_03"], evidence_to_claims, gold_paths) == 0


def test_production_callspec_smoke_all_runners_end_to_end():
    """End-to-end production smoke test proving CallSpec -> ModelCallResult -> parse -> immutable DB."""
    client = ProductionCompatibleFakeClient(fixed_protocol="PROTO_X7")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_production_smoke_r4.db")

        # Track R
        evals_r, m_r = run_track_r(client, db_path, max_calls=1)
        assert len(evals_r) == 1
        assert evals_r[0].k_a == 1
        assert evals_r[0].is_valid_json == 1

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

        # Test relational evaluations table persistence
        persist_round4_relational_evaluation(db_path, "track_p", "permutation_invariance", m_p.k_i, "ok", m_p)

        # Verify SQLite tables
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM round4_calls")
        call_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM round4_evaluations")
        eval_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM round4_relational_evaluations")
        rel_count = cur.fetchone()[0]

        assert call_count == 4
        assert eval_count == 4
        assert rel_count == 1

        # Verify foreign key / call_id linkage
        cur.execute("""
            SELECT c.call_id, c.call_spec_sha256, c.model_digest, e.k_a, e.is_valid_json
            FROM round4_calls c
            JOIN round4_evaluations e ON c.call_id = e.call_id
        """)
        rows = cur.fetchall()
        assert len(rows) == 4
        for row in rows:
            assert row[1] is not None
            assert row[2] == "fake_sha256_digest_12345"
            assert row[3] == 1  # k_a == 1
            assert row[4] == 1  # is_valid_json == 1

        conn.close()
