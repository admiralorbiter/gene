"""Unit tests for SQLite database persistence and round-trip world storage."""

from __future__ import annotations

from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator
from gene.worlds.schema import World


def test_sqlite_schema_init_in_memory():
    db = Database(":memory:")
    # Verify tables exist
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


def test_procedural_paired_worlds_persistence():
    clean_world, mutated_world, mutation = WorldGenerator.generate_paired(seed=1234)
    db = Database(":memory:")
    db.save_world(clean_world)
    db.save_world(mutated_world)

    loaded_clean = db.load_world(clean_world.world_id)
    loaded_mut = db.load_world(mutated_world.world_id)

    assert loaded_clean is not None
    assert loaded_mut is not None
    assert loaded_clean.validation_hash() == clean_world.validation_hash()
    assert loaded_mut.validation_hash() == mutated_world.validation_hash()
    db.close()
