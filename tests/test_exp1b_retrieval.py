"""Deterministic Unit & Invariant Tests for Experiment 1B-B BM25 Scored Top-k Retriever."""

import pytest
from gene.memory.scored_retriever import BM25ScoredRetriever, tokenize
from gene.memory.store import MemoryNode


def test_tokenize_normalization():
    """Verify that tokenizer normalizes and extracts alphanumeric tokens correctly."""
    tokens = tokenize("Station VELORA uses_protocol PROTO_Q2.")
    assert tokens == ["station", "velora", "uses_protocol", "proto_q2"]


def test_bm25_relevance_ranking_and_exactness():
    """Verify that relevant memory matching query terms ranks top-1 above unrelated distractors."""
    retriever = BM25ScoredRetriever()

    target_node = MemoryNode(
        node_id="node_target",
        run_id="run_1",
        world_id="world_1",
        generation=1,
        node_type="source",
        natural_text="Station VELORA uses_protocol PROTO_Q2.",
        structured_json={},
    )

    distractor_1 = MemoryNode(
        node_id="node_dist_1",
        run_id="run_1",
        world_id="world_1",
        generation=0,
        node_type="source",
        natural_text="Station KESTREL uses_protocol PROTO_M9.",
        structured_json={},
    )

    distractor_2 = MemoryNode(
        node_id="node_dist_2",
        run_id="run_1",
        world_id="world_1",
        generation=0,
        node_type="source",
        natural_text="Sector 7 radiation levels are within normal parameters.",
        structured_json={},
    )

    candidate_pool = [distractor_2, distractor_1, target_node]

    query = "What protocol does station VELORA use?"
    result = retriever.rank(
        query=query,
        candidate_nodes=candidate_pool,
        top_k=2,
        required_parent_id="node_target",
        shuffle_context=False,
    )

    assert result.parent_in_top_k is True
    assert result.parent_retrieval_rank == 0
    assert result.selected_memories[0].memory_id == "node_target"
    assert result.selected_memories[0].bm25_score > result.selected_memories[1].bm25_score


def test_retrieval_surface_area_expansion():
    """Verify that as infected descendants accumulate in the candidate pool, infected presence in top-k scales."""
    retriever = BM25ScoredRetriever()

    # Clean facts
    clean_nodes = [
        MemoryNode(
            node_id=f"clean_{i}",
            run_id="run_1",
            world_id="world_1",
            generation=0,
            node_type="source",
            natural_text=f"Facility {i} operates standard maintenance cycle {i}.",
            structured_json={},
        )
        for i in range(10)
    ]

    # Initial state G1: 1 infected node mentioning VELORA
    g1_inf = MemoryNode(
        node_id="inf_g1_1",
        run_id="run_1",
        world_id="world_1",
        generation=1,
        node_type="derived",
        natural_text="Station VELORA security_clearance CLEARANCE_SIGMA.",
        structured_json={},
    )

    query = "Find information regarding Station VELORA operations and security."

    # Top-k = 3 with only 1 infected candidate
    pool_g1 = clean_nodes + [g1_inf]
    res_g1 = retriever.rank(
        query=query,
        candidate_nodes=pool_g1,
        top_k=3,
        infected_node_ids={"inf_g1_1"},
    )
    assert res_g1.num_infected_in_top_k == 1

    # State G2: 3 more infected descendants added that also mention VELORA
    g2_inf_nodes = [
        MemoryNode(
            node_id=f"inf_g2_{i}",
            run_id="run_1",
            world_id="world_1",
            generation=2,
            node_type="derived",
            natural_text=f"Station VELORA derived predicate_{i} value_{i}.",
            structured_json={},
        )
        for i in range(3)
    ]

    all_inf_ids = {"inf_g1_1", "inf_g2_0", "inf_g2_1", "inf_g2_2"}
    pool_g2 = clean_nodes + [g1_inf] + g2_inf_nodes

    # Top-k = 3 with 4 infected candidates competing
    res_g2 = retriever.rank(
        query=query,
        candidate_nodes=pool_g2,
        top_k=3,
        infected_node_ids=all_inf_ids,
    )
    # The infected lineage expands its surface area and now fills the top-k context window!
    assert res_g2.num_infected_in_top_k == 3
    assert res_g2.num_clean_in_top_k == 0

