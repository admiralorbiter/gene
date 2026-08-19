"""Unit tests for SQLite database persistence, composite keys, and round-trip world storage."""

from __future__ import annotations

from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator
from gene.worlds.schema import World


def test_sqlite_schema_init_in_memory():
    db = Database(":memory:")
    cursor = db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "worlds" in tables
    assert "world_facts" in tables
    assert "rules" in tables
    assert "mutations" in tables
    assert "runs" in tables
    assert "calls" in tables
    assert "memory_nodes" in tables
    assert "claims" in tables
    assert "exposure_edges" in tables
    assert "reported_support_edges" in tables
    assert "causal_tests" in tables
    assert "evaluations" in tables
    db.close()


def test_world_save_and_load_roundtrip(golden_world: World):
    db = Database(":memory:")
    db.save_world(golden_world)

    loaded_world = db.load_world(golden_world.world_id)
    assert loaded_world is not None
    assert loaded_world.world_id == golden_world.world_id
    assert loaded_world.world_seed == golden_world.world_seed
    assert loaded_world.validation_hash() == golden_world.validation_hash()
    assert len(loaded_world.facts) == len(golden_world.facts)
    assert len(loaded_world.rules) == len(golden_world.rules)
    assert loaded_world.mutation is not None
    assert loaded_world.mutation.mutation_id == golden_world.mutation.mutation_id
    db.close()


def test_composite_keys_across_multiple_worlds():
    """Verify that saving multiple worlds with identical rule IDs preserves all worlds independently."""
    w1 = WorldGenerator.generate(seed=101)
    w2 = WorldGenerator.generate(seed=202)

    db = Database(":memory:")
    db.save_world(w1)
    db.save_world(w2)

    # Both worlds should exist in DB with their respective facts and rules
    loaded_w1 = db.load_world(w1.world_id)
    loaded_w2 = db.load_world(w2.world_id)

    assert loaded_w1 is not None
    assert loaded_w2 is not None
    assert loaded_w1.validation_hash() == w1.validation_hash()
    assert loaded_w2.validation_hash() == w2.validation_hash()
    db.close()
