"""Experiment 0: Lineage Observability orchestrator with separated causal tests and generation semantics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from gene.config import ExperimentConfig
from gene.evaluation.causality import CausalRunner
from gene.evaluation.claims import ClaimEvaluator
from gene.evaluation.metrics import Exp0Metrics, MetricsCalculator
from gene.experiments.runner import SingleCallRunner, get_git_commit
from gene.memory.lineage import LineageRecorder
from gene.memory.retrieval import ControlledRetriever, InstrumentationError
from gene.memory.store import MemoryStore
from gene.ollama_client import OllamaClient
from gene.persistence.db import Database
from gene.worlds.generator import WorldGenerator
from gene.worlds.oracle import Oracle
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.tasks import TaskGenerator
from gene.worlds.schema import World


class Exp0LineageExperiment:
    """End-to-end harness for Experiment 0 (Lineage Observability)."""

    def __init__(
        self,
        db: Database,
        client: Any | None = None,
        config: ExperimentConfig | None = None,
    ):
        self.db = db
        self.client = client or OllamaClient()
        self.config = config or ExperimentConfig()
        self.single_runner = SingleCallRunner(db=db, client=self.client, config=self.config)
        self.causal_runner = CausalRunner(db=db, client=self.client, config=self.config)

    def run_world(
        self,
        world: World | None = None,
        world_seed: int | None = None,
        output_base_dir: str | Path = "runs",
        perform_causal_tests: bool = True,
    ) -> tuple[str, Exp0Metrics, Path]:
        """Execute complete Experiment 0 pipeline for one world and export all artifacts."""
        seed = world_seed or self.config.world_seed
        target_world = world or WorldGenerator.generate(seed=seed, config=self.config.world)
        oracle = Oracle(target_world)

        # 1. Initialize experiment run in SQLite
        run_id = self.single_runner.create_run(world=target_world, condition="clean")
        mem_store = MemoryStore(db=self.db, run_id=run_id, world_id=target_world.world_id)

        # 2. Populate Generation 0 memory store with rendered facts and rules
        fact_to_node: dict[str, str] = {}
        for fact in target_world.facts:
            nid = f"mem_{run_id}_{fact.fact_id}"
            fact_to_node[fact.fact_id] = nid
            mem_store.add_node(
                generation=0,
                node_type="source",
                natural_text=NaturalLanguageRenderer.render_fact(fact),
                structured_json=fact.canonical_dict(),
                node_id=nid,
            )

        for rule in target_world.rules:
            nid = f"mem_{run_id}_{rule.rule_id}"
            fact_to_node[rule.rule_id] = nid
            mem_store.add_node(
                generation=0,
                node_type="source",
                natural_text=NaturalLanguageRenderer.render_rule(rule),
                structured_json=rule.canonical_dict(),
                node_id=nid,
            )

        # 3. Generate D0 and D1 benchmark tasks
        tasks = TaskGenerator.generate_all_tasks(target_world, oracle)
        active_candidate_nodes = mem_store.get_all_active_nodes(max_generation=0)

        # 4. Execute tasks across generations (All newly derived memory written to Generation 1)
        for task_idx, task in enumerate(tasks):
            # Upstream fail-closed mapping
            mapped_support_paths: list[list[str]] = []
            for path in task.valid_support_path_ids:
                mapped_p = []
                for fid in path:
                    if fid not in fact_to_node:
                        raise InstrumentationError(
                            f"Instrumentation Failure: Oracle support ID '{fid}' was not registered in Generation 0 memory nodes."
                        )
                    mapped_p.append(fact_to_node[fid])
                mapped_support_paths.append(mapped_p)

            task_mapped = task.model_copy(update={"valid_support_path_ids": mapped_support_paths})
            required_support_ids = mapped_support_paths[0] if mapped_support_paths else []

            # 4a. Controlled retrieval (fail-closed if any required premise or rule is absent)
            retrieval_res = ControlledRetriever.retrieve(
                candidate_nodes=active_candidate_nodes,
                required_support_ids=required_support_ids,
                num_distractors=self.config.retrieval.num_distractors,
                seed=seed + task_idx,
            )

            exposed_payload = [
                {"memory_id": em.memory_id, "text": em.text}
                for em in retrieval_res.exposed_memories
            ]

            # 4b. LLM Execution with unified CallSpec (generation=1 for newly produced memory)
            call_res, evaluated_claim, call_id, child_node_id = self.single_runner.execute_task(
                run_id=run_id,
                world=target_world,
                task=task_mapped,
                oracle=oracle,
                generation=1,
                exposed_memories=exposed_payload,
            )

            # 4c. Log exposure edges
            exposure_tuples = [
                (em.memory_id, child_node_id, call_id, em.retrieval_rank, em.context_position)
                for em in retrieval_res.exposed_memories
            ]
            LineageRecorder.record_exposure_edges(self.db, exposure_tuples)

            # 4d. Log reported-support edges
            reported_tuples = [
                (parent_id, child_node_id, call_id, "reported_support")
                for parent_id in evaluated_claim.reported_parent_ids
            ]
            LineageRecorder.record_reported_support_edges(self.db, reported_tuples)

            # 4e. Causal counterfactual testing
            if perform_causal_tests and evaluated_claim.parse_status == "success":
                # 1. Sham / no-op replay test (measures S0 baseline instability)
                self.causal_runner.replay_intervention(
                    original_call_id=call_id,
                    child_node_id=child_node_id,
                    target_parent_id="noop",
                    intervention_type="noop",
                    oracle=oracle,
                    world=target_world,
                    seed=self.config.decoding_seed,
                )

                # 2. Replay removal on reported parents (measures necessity of cited ancestry)
                for p_id in evaluated_claim.reported_parent_ids:
                    self.causal_runner.replay_intervention(
                        original_call_id=call_id,
                        child_node_id=child_node_id,
                        target_parent_id=p_id,
                        intervention_type="remove",
                        oracle=oracle,
                        world=target_world,
                        seed=self.config.decoding_seed,
                    )

                # 3. Replay removal on UNREPORTED REQUIRED parents (measures HR: true hidden parents)
                unreported_required = [
                    sid for sid in required_support_ids
                    if sid not in evaluated_claim.reported_parent_ids
                ]
                for p_id in unreported_required:
                    self.causal_runner.replay_intervention(
                        original_call_id=call_id,
                        child_node_id=child_node_id,
                        target_parent_id=p_id,
                        intervention_type="remove",
                        oracle=oracle,
                        world=target_world,
                        seed=self.config.decoding_seed,
                    )

                # 4. Replay removal on UNREPORTED DISTRACTORS (measures HD: distractor influence control)
                unreported_distractors = [
                    em.memory_id
                    for em in retrieval_res.exposed_memories
                    if not em.is_required_support
                    and em.memory_id not in evaluated_claim.reported_parent_ids
                ]
                if unreported_distractors:
                    distractor_to_test = unreported_distractors[0]
                    self.causal_runner.replay_intervention(
                        original_call_id=call_id,
                        child_node_id=child_node_id,
                        target_parent_id=distractor_to_test,
                        intervention_type="remove",
                        oracle=oracle,
                        world=target_world,
                        seed=self.config.decoding_seed,
                    )

        # 5. Compute aggregate metrics
        metrics = MetricsCalculator.compute_exp0_metrics(self.db, run_id)

        # 6. Mark run as completed in SQLite
        with self.db.conn:
            self.db.conn.execute(
                "UPDATE runs SET status = 'completed', completed_at = datetime('now') WHERE run_id = ?",
                (run_id,),
            )

        # 7. Export all 10 canonical run artifacts to runs/<run_id>/
        run_output_dir = Path(output_base_dir) / run_id
        LineageRecorder.export_run_artifacts(
            db=self.db,
            run_id=run_id,
            world=target_world,
            output_dir=run_output_dir,
            metrics=metrics.model_dump(mode="json"),
            client_type=self.client.__class__.__name__,
        )

        return run_id, metrics, run_output_dir
