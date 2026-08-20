"""Track S: Trace-to-Support Compiler Engine.

Mechanically extracts minimal epistemic support environments S_F(c) from runtime execution
traces (occurrence nodes, rule templates, exposure edges) distinguishing AND-conjunctive
premises from OR-disjunctive alternative derivations.
"""

from __future__ import annotations

import itertools
from typing import Any
from pydantic import BaseModel, Field


class ExecutionTraceNode(BaseModel):
    node_id: str
    claim_type: str
    claim_value: str
    is_root_premise: bool = False
    # A node may have multiple alternative derivation environments (OR of ANDs)
    # Each inner list is a conjunctive set of parent node IDs required for that derivation path
    support_environments: list[list[str]] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)


class TraceSupportCompiler:
    """Compiles backward trace slices into minimal sufficient support environments."""

    def __init__(self):
        self.nodes: dict[str, ExecutionTraceNode] = {}

    def add_node(self, node: ExecutionTraceNode) -> None:
        self.nodes[node.node_id] = node

    def compile_minimal_support_environments(self, target_node_id: str) -> list[set[str]]:
        """Perform backward slicing across disjunctive and conjunctive paths."""
        if target_node_id not in self.nodes:
            raise ValueError(f"Target node {target_node_id} not found in execution trace.")

        target = self.nodes[target_node_id]
        if target.is_root_premise:
            return [{target.node_id}]

        raw_proof_paths = self._find_root_paths(target_node_id)
        
        # Minimize proof paths to irredundant root assumption sets
        minimal_sets: list[set[str]] = []
        for path in sorted(raw_proof_paths, key=len):
            path_set = set(path)
            if not any(existing.issubset(path_set) for existing in minimal_sets):
                minimal_sets.append(path_set)

        return minimal_sets

    def _find_root_paths(self, current_id: str) -> list[list[str]]:
        node = self.nodes[current_id]
        if node.is_root_premise:
            return [[node.node_id]]

        if not node.support_environments:
            return []

        all_alternative_paths: list[list[str]] = []

        # Each environment in support_environments is an alternative derivation (OR)
        for conjunctive_env in node.support_environments:
            # For each conjunctive premise in this environment (AND)
            parent_paths_list = [self._find_root_paths(p_id) for p_id in conjunctive_env]
            
            # Cartesian product across conjunctive branch premises
            for combo in itertools.product(*parent_paths_list):
                merged = []
                for p_list in combo:
                    merged.extend(p_list)
                all_alternative_paths.append(sorted(list(set(merged))))

        return all_alternative_paths
