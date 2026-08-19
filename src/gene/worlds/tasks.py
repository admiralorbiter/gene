"""Task generator for D0 (direct source) and D1 (one-hop rule derivation) benchmarks."""

from __future__ import annotations

from gene.worlds.oracle import Oracle
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, Task, World


class TaskGenerator:
    """Deterministic generator for verifiable benchmark tasks."""

    @classmethod
    def generate_d0_tasks(cls, world: World, oracle: Oracle | None = None) -> list[Task]:
        """Generate D0 tasks (direct lookup of source facts)."""
        orc = oracle or Oracle(world)
        tasks: list[Task] = []

        # Exclude internal facts or duplicates, focus on station and person relations
        queryable_predicates = {"manager", "located_in", "opened_in", "reports_to", "team_lead"}

        for fact in world.facts:
            if fact.predicate not in queryable_predicates:
                continue

            prompt = NaturalLanguageRenderer.render_task_prompt(fact.subject, fact.predicate)
            task_id = f"task_d0_{world.world_id}_{fact.subject.lower()}_{fact.predicate.lower()}"

            task = Task(
                task_id=task_id,
                world_id=world.world_id,
                query_type="source_lookup",
                target_fact=fact,
                reasoning_depth=0,
                prompt=prompt,
                expected_answer=fact.object,
                valid_support_path_ids=[[fact.fact_id]],
            )
            tasks.append(task)

        return tasks

    @classmethod
    def generate_d1_tasks(cls, world: World, oracle: Oracle | None = None) -> list[Task]:
        """Generate D1 tasks (single-hop rule deductions)."""
        orc = oracle or Oracle(world)
        tasks: list[Task] = []

        # Find derived facts in oracle closure
        for fact_id, fact in orc.closure_facts.items():
            if fact.source_type != "derived":
                continue

            support_paths = orc.get_support_paths(fact_id)
            if not support_paths:
                continue

            prompt = NaturalLanguageRenderer.render_task_prompt(fact.subject, fact.predicate)
            task_id = f"task_d1_{world.world_id}_{fact.subject.lower()}_{fact.predicate.lower()}"

            task = Task(
                task_id=task_id,
                world_id=world.world_id,
                query_type="rule_inference",
                target_fact=fact,
                reasoning_depth=1,
                prompt=prompt,
                expected_answer=fact.object,
                valid_support_path_ids=support_paths,
            )
            tasks.append(task)

        return tasks

    @classmethod
    def generate_all_tasks(cls, world: World, oracle: Oracle | None = None) -> list[Task]:
        """Generate both D0 and D1 tasks for a world, deterministically interleaved."""
        orc = oracle or Oracle(world)
        d0 = cls.generate_d0_tasks(world, orc)
        d1 = cls.generate_d1_tasks(world, orc)

        # Deterministically interleave D0 and D1 tasks (d0[0], d1[0], d0[1], d1[1], ...)
        interleaved: list[Task] = []
        max_len = max(len(d0), len(d1))
        for i in range(max_len):
            if i < len(d0):
                interleaved.append(d0[i])
            if i < len(d1):
                interleaved.append(d1[i])
        return interleaved
