"""Unit and property tests for task generator."""

from __future__ import annotations

from gene.worlds.generator import WorldGenerator
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.tasks import TaskGenerator


def test_d0_tasks_validity(golden_world):
    oracle = Oracle(golden_world)
    tasks = TaskGenerator.generate_d0_tasks(golden_world, oracle)

    assert len(tasks) > 0
    for task in tasks:
        assert task.reasoning_depth == 0
        assert oracle.evaluate_claim(task.target_fact) == TruthStatus.TRUE
        assert len(task.valid_support_path_ids) == 1
        assert task.valid_support_path_ids[0] == [task.target_fact.fact_id]


def test_d1_tasks_validity(golden_world):
    oracle = Oracle(golden_world)
    tasks = TaskGenerator.generate_d1_tasks(golden_world, oracle)

    assert len(tasks) == 2  # 2 derived protocol facts in golden world
    for task in tasks:
        assert task.reasoning_depth == 1
        assert oracle.evaluate_claim(task.target_fact) == TruthStatus.TRUE
        assert len(task.valid_support_path_ids) >= 1
        # Target fact must be in oracle closure
        assert task.target_fact.fact_id in oracle.closure_facts


def test_procedural_tasks_validity():
    world = WorldGenerator.generate(seed=42)
    oracle = Oracle(world)
    all_tasks = TaskGenerator.generate_all_tasks(world, oracle)

    assert len(all_tasks) > 0
    d0_tasks = [t for t in all_tasks if t.reasoning_depth == 0]
    d1_tasks = [t for t in all_tasks if t.reasoning_depth == 1]

    assert len(d0_tasks) > 0
    assert len(d1_tasks) > 0

    for task in all_tasks:
        assert oracle.evaluate_claim(task.target_fact) == TruthStatus.TRUE
        assert len(task.valid_support_path_ids) >= 1
