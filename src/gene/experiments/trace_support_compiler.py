"""Track S: Trace-to-Support Compiler Engine.

Mechanically extracts minimal epistemic support environments S_F(c) from runtime execution
traces (occurrence nodes, rule templates, exposure edges) via backward slicing.
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
    parent_ids: list[str] = Field(default_factory=list)
    rule_id: str | None = None


class TraceSupportCompiler:
    """Compiles backward trace slices into minimal sufficient support environments."""

    def __init__(self):
        self.nodes: dict[str, ExecutionTraceNode] = {}

    def add_node(self, node: ExecutionTraceNode) -> None:
        self.nodes[node.node_id] = node

    def compile_minimal_support_environments(self, target_node_id: str) -> list[set[str]]:
        """Perform backward slicing to extract irredundant root assumption sets."""
        if target_node_id not in self.nodes:
            raise ValueError(f"Target node {target_node_id} not found in execution trace.")

        target = self.nodes[target_node_id]
        if target.is_root_premise:
            return [{target.node_id}]

        # Enumerate all proof trees leading to target
        proof_paths = self._find_root_paths(target_node_id)
        
        # Minimize proof paths to irredundant sets
        minimal_sets: list[set[str]] = []
        for path in sorted(proof_paths, key=len):
            path_set = set(path)
            if not any(existing.issubset(path_set) for existing in minimal_sets):
                minimal_sets.append(path_set)

        return minimal_sets

    def _find_root_paths(self, current_id: str) -> list[list[str]]:
        node = self.nodes[current_id]
        if node.is_root_premise:
            return [[node.node_id]]

        if not node.parent_ids:
            return []

        # If parents are conjunctive (all required for rule)
        parent_paths_list = [self._find_root_paths(p_id) for p_id in node.parent_ids]
        
        # Cartesian product across conjunctive branch premises
        combined_paths = []
        for combo in itertools.product(*parent_paths_list):
            merged = []
            for p_list in combo:
                merged.extend(p_list)
            combined_paths.append(sorted(list(set(merged))))

        return combined_paths
