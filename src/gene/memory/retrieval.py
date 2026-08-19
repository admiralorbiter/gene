"""Controlled memory retrieval policy for Experiment 0 and 1."""

from __future__ import annotations

import random
from typing import Any
from pydantic import BaseModel
from gene.memory.store import MemoryNode


class ExposedMemory(BaseModel):
    """An individual memory node exposed in prompt context with rank and ground truth role."""
    memory_id: str
    text: str
    is_required_support: bool
    retrieval_rank: int
    context_position: int


class RetrievalResult(BaseModel):
    """Auditable output of a controlled retrieval operation."""
    candidate_node_ids: list[str]
    exposed_memories: list[ExposedMemory]
    required_support_ids: list[str]
    distractor_ids: list[str]


class ControlledRetriever:
    """Deterministic controlled retrieval policy (Required Support + N Distractors)."""

    @classmethod
    def retrieve(
        cls,
        candidate_nodes: list[MemoryNode],
        required_support_ids: list[str],
        num_distractors: int = 3,
        seed: int = 42,
    ) -> RetrievalResult:
        """Select required support nodes plus N distractors, shuffled deterministically."""
        rng = random.Random(seed)
        candidate_map = {node.node_id: node for node in candidate_nodes}
        candidate_node_ids = list(candidate_map.keys())

        # 1. Identify support nodes
        support_nodes: list[MemoryNode] = []
        for sid in required_support_ids:
            if sid in candidate_map:
                support_nodes.append(candidate_map[sid])

        # 2. Identify distractor pool (nodes not in required support)
        support_id_set = set(required_support_ids)
        distractor_pool = [
            node for node in candidate_nodes if node.node_id not in support_id_set
        ]

        # 3. Sample distractors
        sampled_count = min(num_distractors, len(distractor_pool))
        sampled_distractors = rng.sample(distractor_pool, sampled_count) if sampled_count > 0 else []
        distractor_ids = [d.node_id for d in sampled_distractors]

        # 4. Combine and assign retrieval rank
        selected_nodes = support_nodes + sampled_distractors
        # Retrieval rank based on selection order
        rank_map = {node.node_id: idx for idx, node in enumerate(selected_nodes)}

        # 5. Deterministically shuffle presentation order (context position)
        shuffled_nodes = list(selected_nodes)
        rng.shuffle(shuffled_nodes)

        exposed_memories: list[ExposedMemory] = []
        for pos, node in enumerate(shuffled_nodes):
            exposed_memories.append(
                ExposedMemory(
                    memory_id=node.node_id,
                    text=node.natural_text,
                    is_required_support=(node.node_id in support_id_set),
                    retrieval_rank=rank_map[node.node_id],
                    context_position=pos,
                )
            )

        return RetrievalResult(
            candidate_node_ids=candidate_node_ids,
            exposed_memories=exposed_memories,
            required_support_ids=required_support_ids,
            distractor_ids=distractor_ids,
        )
