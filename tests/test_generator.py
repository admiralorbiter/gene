"""Property and invariant tests for procedural world generator."""

from __future__ import annotations

from gene.worlds.generator import WorldGenerator
from gene.worlds.oracle import Oracle


def test_seed_reproducibility():
    w1 = WorldGenerator.generate(seed=101)
    w2 = WorldGenerator.generate(seed=101)
    assert w1.validation_hash() == w2.validation_hash()
    assert w1.canonical_json() == w2.canonical_json()


def test_different_seeds_produce_different_worlds():
    w1 = WorldGenerator.generate(seed=101)
    w2 = WorldGenerator.generate(seed=202)
    assert w1.validation_hash() != w2.validation_hash()


def test_clean_mutated_pair_invariant():
    for seed in [1, 42, 100, 777]:
        clean_world, mutated_world, mutation = WorldGenerator.generate_paired(seed=seed)

        # Entities and rules must be identical
        assert clean_world.entities == mutated_world.entities
        assert [r.canonical_dict() for r in clean_world.rules] == [r.canonical_dict() for r in mutated_world.rules]

        # Total number of facts must be identical
        assert len(clean_world.facts) == len(mutated_world.facts)

        # Difference between clean and mutated facts must be exactly 1 fact
        clean_ids = {f.fact_id for f in clean_world.facts}
        mutated_ids = {f.fact_id for f in mutated_world.facts}

        clean_only = clean_ids - mutated_ids
        mutated_only = mutated_ids - clean_ids

        assert len(clean_only) == 1
        assert len(mutated_only) == 1

        assert list(clean_only)[0] == mutation.true_fact.fact_id
        assert list(mutated_only)[0] == mutation.mutated_fact.fact_id


def test_generated_worlds_have_oracle_closure():
    for seed in [10, 20, 30]:
        world = WorldGenerator.generate(seed=seed)
        oracle = Oracle(world)
        assert len(oracle.closure_facts) >= len(world.facts)
        # Ensure rules were applied and produced derived facts
        derived_facts = [f for f in oracle.closure_facts.values() if f.source_type == "derived"]
        assert len(derived_facts) > 0
