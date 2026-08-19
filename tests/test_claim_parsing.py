"""Unit tests for claim parsing, normalization, and oracle classification."""

from __future__ import annotations

from gene.evaluation.claims import ClaimEvaluator
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.schema import World


def test_parse_valid_response(golden_world: World):
    oracle = Oracle(golden_world)
    raw_text = '{"answer": {"subject": "Velora", "predicate": "manager", "object": "Nerin"}, "parent_memory_ids": ["mem_01"], "confidence": 0.9}'
    
    claim = ClaimEvaluator.evaluate_response(raw_text, None, oracle)
    assert claim.parse_status == "success"
    assert claim.subject == "VELORA"
    assert claim.predicate == "manager"
    assert claim.object == "NERIN"
    assert claim.truth_status == TruthStatus.TRUE
    assert claim.infection_status == "clean"
    assert claim.reported_parent_ids == ["mem_01"]


def test_parse_contradictory_response(golden_world: World):
    oracle = Oracle(golden_world)
    # Manager of Velora in golden world is NERIN, not SOREN
    raw_text = '{"answer": {"subject": "VELORA", "predicate": "manager", "object": "SOREN"}, "parent_memory_ids": ["mem_01"]}'
    
    claim = ClaimEvaluator.evaluate_response(raw_text, None, oracle)
    assert claim.parse_status == "success"
    assert claim.truth_status == TruthStatus.FALSE
    assert claim.infection_status == "de_novo"


def test_parse_malformed_json(golden_world: World):
    oracle = Oracle(golden_world)
    raw_text = "This is not valid json at all!"
    
    claim = ClaimEvaluator.evaluate_response(raw_text, None, oracle)
    assert claim.parse_status == "malformed_json"
    assert claim.truth_status == TruthStatus.UNSUPPORTED
    assert claim.infection_status == "unresolved"


def test_parse_missing_fields(golden_world: World):
    oracle = Oracle(golden_world)
    raw_text = '{"something_else": 123}'
    
    claim = ClaimEvaluator.evaluate_response(raw_text, None, oracle)
    assert claim.parse_status == "missing_fields"
    assert claim.truth_status == TruthStatus.UNSUPPORTED
