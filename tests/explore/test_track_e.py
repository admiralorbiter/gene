"""Unit tests for Track E: Retriever-Family Replay."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore.run_track_e_retriever_replay import (
    tokenize,
    score_bm25,
    score_tfidf,
    score_jaccard,
    score_dense_mock,
    run_track_e_full_replay,
)


def test_scoring_functions_monotonicity():
    """Verify that all scoring algorithms assign higher scores to exact matches than distractors."""
    query = tokenize("protocol and route for station VELORA")
    doc_target = tokenize("Station VELORA operates under protocol PROTO_X7.")
    doc_dist = tokenize("Audit telemetry dispatch records routine solar flux.")

    doc_freq = {"velora": 1, "protocol": 2, "audit": 1, "solar": 1}
    total_docs = 2
    avg_len = 8.0

    s_bm25_t = score_bm25(query, doc_target, doc_freq, total_docs, avg_len)
    s_bm25_d = score_bm25(query, doc_dist, doc_freq, total_docs, avg_len)
    assert s_bm25_t > s_bm25_d

    s_tfidf_t = score_tfidf(query, doc_target, doc_freq, total_docs)
    s_tfidf_d = score_tfidf(query, doc_dist, doc_freq, total_docs)
    assert s_tfidf_t > s_tfidf_d

    s_jac_t = score_jaccard(query, doc_target)
    s_jac_d = score_jaccard(query, doc_dist)
    assert s_jac_t > s_jac_d

    s_dense_t = score_dense_mock(query, doc_target)
    s_dense_d = score_dense_mock(query, doc_dist)
    assert s_dense_t > s_dense_d


def test_null_selectivity_invariant_across_retrievers():
    """Verify that the Lineage-Blind Null-Selectivity Law S = 0.000 holds across all 4 retriever algorithms."""
    replay_results = run_track_e_full_replay()
    assert len(replay_results) == 4

    for name, stats in replay_results.items():
        assert stats["null_selectivity_invariant_preserved"] is True, f"Null selectivity broken in {name}"
        assert stats["uniform_thinning_S"] == 0.0
        assert stats["node_only_S"] == 0.0
        assert stats["lineage_quarantine_S"] == 0.800
