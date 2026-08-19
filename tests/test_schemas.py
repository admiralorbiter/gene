"""Unit tests for domain schemas, hashing, and canonical serialization."""

from __future__ import annotations

import json
from gene.worlds.schema import Fact, Rule, Task, World, compute_fact_id


def test_fact_id_determinism():
    id1 = compute_fact_id("VELORA", "manager", "NERIN")
    id2 = compute_fact_id("velora", "MANAGER", "nerin")
    assert id1 == id2
    assert id1.startswith("fact_")


def test_fact_canonical_json_roundtrip():
    fact = Fact(subject="VELORA", predicate="manager", object="NERIN", source_type="generated")
    json_str = fact.canonical_json()
    data = json.loads(json_str)
    assert data["subject"] == "VELORA"
    assert data["predicate"] == "manager"
    assert data["object"] == "NERIN"
    assert data["truth_value"] is True
    assert data["source_type"] == "generated"


def test_world_canonical_json_and_hash_stability(golden_world: World):
    hash1 = golden_world.validation_hash()
    hash2 = golden_world.validation_hash()
    assert hash1 == hash2
    assert len(hash1) == 64

    # Verify deserialization from canonical JSON
    serialized = golden_world.canonical_json()
    deserialized = World.model_validate_json(serialized)
    assert deserialized.world_id == golden_world.world_id
    assert deserialized.validation_hash() == hash1
