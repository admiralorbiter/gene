"""Unit tests for controlled memory retrieval policy and fail-closed guarantees."""

from __future__ import annotations

import pytest
from gene.memory.retrieval import ControlledRetriever, InstrumentationError
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

    ranks = [em.retrieval_rank for em in res.exposed_memories]
    positions = [em.context_position for em in res.exposed_memories]
    assert sorted(ranks) == [0, 1, 2, 3, 4]
    assert sorted(positions) == [0, 1, 2, 3, 4]


def test_controlled_retriever_fails_closed_on_missing_support():
    nodes = [
        MemoryNode(node_id="mem_01", run_id="run_1", world_id="w_1", generation=0, node_type="source", natural_text="Mem 1")
    ]
    required_ids = ["mem_01", "mem_missing_999"]

    with pytest.raises(InstrumentationError, match="Required support ID 'mem_missing_999' was not available"):
        ControlledRetriever.retrieve(
            candidate_nodes=nodes,
            required_support_ids=required_ids,
            num_distractors=1,
            seed=42,
        )
