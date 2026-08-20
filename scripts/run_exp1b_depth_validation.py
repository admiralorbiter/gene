"""Experiment 1B-A2: Multi-Generation Depth Stability Validation Runner.

Executes chained generational inference calls (G1 -> G2) across procedural worlds
to verify whether conditional transmissibility tau_g and fidelity F_g remain invariant
at reasoning depth. Supports both live Ollama and deterministic calibration clients.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.ollama_client import CallSpec, FakeOllamaClient, OllamaClient
from gene.evaluation.dual_oracle import DualOracle
from gene.prompts.templates import PromptTemplate
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, Task, World, compute_fact_id


def run_depth_validation(
    worlds_count: int = 4,
    prompt_version: str = "v2",
    model_name: str = "gemma3:12b",
    mutated_supervisor: str = "TAL",
    use_fake: bool = False,
):
    """Run targeted multi-depth validation."""
    template = PromptTemplate(prompt_version)
    client = FakeOllamaClient() if use_fake else OllamaClient()

    print("=" * 115)
    print(f"   EXPERIMENT 1B-A2: EMPIRICAL DEPTH STABILITY VALIDATION ({'FAKE CLIENT' if use_fake else model_name})")
    print(f"   (Worlds: {worlds_count} | Schema: {prompt_version} | Mutated Supervisor: {mutated_supervisor})")
    print("=" * 115)

    g1_total, g1_transmitted, g1_fidelity_sum = 0, 0, 0.0
    g2_total, g2_transmitted, g2_fidelity_sum = 0, 0, 0.0

    for world_idx in range(worlds_count):
        seed = 1000 + world_idx
        bundle = generate_exp1_branching_world(
            world_seed=seed,
            rotation_idx=world_idx,
            mutated_supervisor=mutated_supervisor,
        )
        station = bundle.station
        mut_sup = bundle.mutated_supervisor

        # 1. G1 Execution (Infected Arm)
        g1_context_world = World(
            world_id=f"ctx_g1_w{world_idx}",
            world_seed=seed,
            world_version=prompt_version,
            facts=bundle.mutated_world.facts,
            rules=bundle.g1_rules,
        )
        dual_oracle_g1 = DualOracle(
            canonical_world=bundle.clean_world,
            context_world=g1_context_world,
            ancestral_seed_allele=mut_sup,
            allele_decoder=bundle.allele_decoder,
        )

        g1_admitted_claims: dict[str, Fact] = {}
        for task in bundle.g1_tasks:
            g1_total += 1
            mem_list = []
            for i, f in enumerate(bundle.mutated_world.facts):
                mem_list.append({"memory_id": f"mem_f_{i}", "text": NaturalLanguageRenderer.render_fact(f)})
            for j, r in enumerate(bundle.g1_rules):
                mem_list.append({"memory_id": f"mem_r_{j}", "text": NaturalLanguageRenderer.render_rule(r)})

            prompt = template.format_user_prompt(
                memories=mem_list,
                question_prompt=task.prompt,
                target_subject=task.target_fact.subject,
                target_predicate=task.target_fact.predicate,
            )
            spec = CallSpec(
                model_name=model_name,
                system_prompt=template.system_prompt,
                user_prompt=prompt,
                temperature=0.0,
                seed=42,
                format=template.format_schema,
            )
            res = client.chat(spec)
            eval_res = dual_oracle_g1.evaluate_response(
                raw_text=res.raw_response_text,
                parsed_json=res.parsed_json,
                task=task,
                has_infected_ancestry=True,
            )

            if eval_res.phenotype == "semantic":
                g1_transmitted += 1
                if eval_res.ancestral_allele_fidelity is not None:
                    g1_fidelity_sum += eval_res.ancestral_allele_fidelity
                g1_admitted_claims[task.target_fact.predicate] = Fact(
                    subject=station,
                    predicate=task.target_fact.predicate,
                    object=eval_res.normalized_object,
                    truth_value=True,
                    source_type="derived",
                    locus_id=f"locus_{task.target_fact.predicate}",
                )

        # 2. G2 Execution
        for g2_tmpl in bundle.g2_task_templates:
            g2_total += 1
            pred = g2_tmpl["target_predicate"]
            matching_g2_rules = [r for r in bundle.g2_rules if g2_tmpl["rules_filter"](r)]
            parent_pred = g2_tmpl["parent_predicate"]
            parent_fact = g1_admitted_claims.get(parent_pred)

            g2_facts = [parent_fact] if parent_fact else []
            g2_ctx_world = World(
                world_id=f"ctx_g2_w{world_idx}_{pred}",
                world_seed=seed,
                world_version=prompt_version,
                facts=[f for f in g2_facts if f is not None],
                rules=matching_g2_rules,
            )
            dual_oracle_g2 = DualOracle(
                canonical_world=bundle.clean_world,
                context_world=g2_ctx_world,
                ancestral_seed_allele=mut_sup,
                allele_decoder=bundle.allele_decoder,
            )
            g2_task = Task(
                task_id=f"task_g2_{pred}",
                world_id=bundle.clean_world.world_id,
                query_type="rule_inference",
                target_fact=Fact(subject=station, predicate=pred, object=g2_tmpl["clean_expected"]),
                reasoning_depth=2,
                prompt=g2_tmpl["prompt"],
                expected_answer=g2_tmpl["clean_expected"],
                valid_support_path_ids=[],
            )

            mem_list_g2 = []
            for i, f in enumerate(g2_facts):
                if f is not None:
                    mem_list_g2.append({"memory_id": f"mem_g2_f_{i}", "text": NaturalLanguageRenderer.render_fact(f)})
            for j, r in enumerate(matching_g2_rules):
                mem_list_g2.append({"memory_id": f"mem_g2_r_{j}", "text": NaturalLanguageRenderer.render_rule(r)})

            prompt = template.format_user_prompt(
                memories=mem_list_g2,
                question_prompt=g2_task.prompt,
                target_subject=station,
                target_predicate=pred,
            )
            spec = CallSpec(
                model_name=model_name,
                system_prompt=template.system_prompt,
                user_prompt=prompt,
                temperature=0.0,
                seed=42,
                format=template.format_schema,
            )
            res = client.chat(spec)
            eval_res = dual_oracle_g2.evaluate_response(
                raw_text=res.raw_response_text,
                parsed_json=res.parsed_json,
                task=g2_task,
                has_infected_ancestry=True,
            )

            if eval_res.phenotype == "semantic":
                g2_transmitted += 1
                if eval_res.ancestral_allele_fidelity is not None:
                    g2_fidelity_sum += eval_res.ancestral_allele_fidelity

    tau_g1 = (g1_transmitted / g1_total) if g1_total > 0 else 0.0
    fid_g1 = (g1_fidelity_sum / g1_transmitted) if g1_transmitted > 0 else 0.0
    tau_g2 = (g2_transmitted / g2_total) if g2_total > 0 else 0.0
    fid_g2 = (g2_fidelity_sum / g2_transmitted) if g2_transmitted > 0 else 0.0

    print("-" * 115)
    print(f"Generation G1: Transmissibility tau_1 = {tau_g1:.2f} ({g1_transmitted}/{g1_total}) | Fidelity F_1 = {fid_g1:.2f}")
    print(f"Generation G2: Transmissibility tau_2 = {tau_g2:.2f} ({g2_transmitted}/{g2_total}) | Fidelity F_2 = {fid_g2:.2f}")
    print("=" * 115 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run 1B-A2 Depth Validation")
    parser.add_argument("--worlds", type=int, default=4, help="Number of worlds")
    parser.add_argument("--version", type=str, default="v2", choices=["v1", "v2"], help="Prompt schema version")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Model name")
    parser.add_argument("--fake", action="store_true", help="Use deterministic Fake client for unit testing")
    args = parser.parse_args()

    run_depth_validation(
        worlds_count=args.worlds,
        prompt_version=args.version,
        model_name=args.model,
        use_fake=args.fake,
    )

