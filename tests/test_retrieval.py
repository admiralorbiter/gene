"""Unit tests for controlled memory retrieval policy."""

from __future__ import annotations

from gene.memory.retrieval import ControlledRetriever
from gene.memory.store import MemoryNode


def test_controlled_retriever_selection():
    nodes = [
        MemoryNode(node_id=f"mem_{i:02d}", run_id="run_1", world_id="w_1", generation=0, node_type="source", natural_text=f"Memory {i}")
        for i in range(10)
    ]
    required_ids = ["mem_01", "mem_03"]

    res = ControlledRetriever.retrieve(
        candidate_nodes=nodes,
        required_support_ids=required_ids,
        num_distractors=3,
        seed=42,
    )

    assert len(res.exposed_memories) == 5  # 2 support + 3 distractors
    exposed_ids = {em.memory_id for em in res.exposed_memories}
    assert "mem_01" in exposed_ids
    assert "mem_03" in exposed_ids

    # Ranks and context positions must be unique and within range [0, 4]
    ranks = [em.retrieval_rank for em in res.exposed_memories]
    positions = [em.context_position for em in res.exposed_memories]
    assert sorted(ranks) == [0, 1, 2, 3, 4]
    assert sorted(positions) == [0, 1, 2, 3, 4]
