"""First-class biological interventions and Counterfactual Oracle engine."""

from __future__ import annotations

from enum import Enum
import json
from typing import Any, Literal
from pydantic import BaseModel, Field

from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.schema import Fact, Rule, World, compute_fact_id


class InterventionType(str, Enum):
    """First-class biological intervention categories."""
    NOOP = "noop"
    KNOCKOUT = "knockout"
    EPISTASIS = "epistasis"
    MUTATION = "mutation"
    RESCUE = "rescue"
    CONTROL_DISTRACTOR = "control_distractor"


class InterventionSpec(BaseModel):
    """Structured specification of a causal/biological intervention."""
    intervention_id: str
    intervention_type: InterventionType
    target_node_ids: list[str] = Field(default_factory=list)
    mutated_facts: list[Fact] = Field(default_factory=list)
    mutated_memories: dict[str, str] = Field(default_factory=dict, description="node_id -> new text (preserving slot ID)")
    rescue_source_call_id: str | None = None
    expected_counterfactual_object: str | None = None
    expected_evidence_status: str | None = None
    description: str = ""


class CounterfactualOracle:
    """Computes ground truth in both the original and counterfactually intervened worlds."""

    def __init__(self, base_world: World, intervention: InterventionSpec):
        self.base_world = base_world
        self.intervention = intervention
        self.base_oracle = Oracle(base_world)
        self.counterfactual_world = self._build_counterfactual_world()
        self.counterfactual_oracle = Oracle(self.counterfactual_world)

    def _build_counterfactual_world(self) -> World:
        """Construct the counterfactual world resulting from the intervention."""
        itype = self.intervention.intervention_type
        target_ids = set(self.intervention.target_node_ids)

        # Start with base facts and rules
        cf_facts: list[Fact] = []
        cf_rules: list[Rule] = []

        # 1. Filter facts
        for f in self.base_world.facts:
            if f.fact_id in target_ids or any(t.endswith(f.fact_id) for t in target_ids):
                if itype in (InterventionType.KNOCKOUT, InterventionType.EPISTASIS):
                    continue
                elif itype in (InterventionType.MUTATION, InterventionType.RESCUE):
                    continue
            cf_facts.append(f)

        # 2. Add mutated facts if present
        for mf in self.intervention.mutated_facts:
            cf_facts.append(mf)

        # 3. Filter rules
        for r in self.base_world.rules:
            if r.rule_id in target_ids or any(t.endswith(r.rule_id) for t in target_ids):
                if itype in (InterventionType.KNOCKOUT, InterventionType.EPISTASIS):
                    continue
            cf_rules.append(r)

        return World(
            world_id=f"{self.base_world.world_id}_cf_{self.intervention.intervention_id}",
            world_seed=self.base_world.world_seed,
            world_version=self.base_world.world_version,
            facts=cf_facts,
            rules=cf_rules,
            mutation=None,
        )

    def evaluate(self, subject: str, predicate: str, object_val: str) -> tuple[TruthStatus, TruthStatus]:
        """Evaluate claim against (original_world_truth, counterfactual_world_truth)."""
        orig_truth = self.base_oracle.evaluate_triple(subject, predicate, object_val)
        cf_truth = self.counterfactual_oracle.evaluate_triple(subject, predicate, object_val)
        return orig_truth, cf_truth
