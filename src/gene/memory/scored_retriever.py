"""Deterministic BM25 Scored Top-k Retriever for Experiment 1B-B.

Provides auditable, mathematically transparent lexical ranking over candidate memory pools
without requiring external vector databases or non-deterministic embeddings:
- Standard Okapi BM25 scoring: k1=1.5, b=0.75.
- Deterministic tie-breaking using SHA256 hashes of node IDs.
- Tracks parent exposure rank, infected lineage displacement, and context window positioning.
"""

from __future__ import annotations

import collections
import hashlib
import math
import random
import re
from typing import Any
from pydantic import BaseModel, Field

from gene.memory.store import MemoryNode


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric tokens."""
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())


class ScoredMemoryNode(BaseModel):
    """An individual memory node evaluated by the scored retriever."""
    memory_id: str
    text: str
    bm25_score: float
    retrieval_rank: int
    context_position: int
    is_required_parent: bool = False
    is_infected: bool = False
    generation: int = 0


class ScoredRetrievalResult(BaseModel):
    """Auditable output of a scored top-k retrieval operation."""
    query_text: str
    top_k: int
    candidate_pool_size: int
    selected_memories: list[ScoredMemoryNode]
    all_ranked_node_ids: list[str]
    parent_in_top_k: bool
    parent_retrieval_rank: int | None = None
    num_infected_in_top_k: int = 0
    num_clean_in_top_k: int = 0
    num_distractors_in_top_k: int = 0


class BM25ScoredRetriever:
    """Deterministic BM25 ranking policy over in-memory candidate pools."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def rank(
        self,
        query: str,
        candidate_nodes: list[MemoryNode],
        top_k: int = 4,
        required_parent_id: str | None = None,
        infected_node_ids: set[str] | None = None,
        distractor_node_ids: set[str] | None = None,
        shuffle_context: bool = True,
        seed: int = 42,
    ) -> ScoredRetrievalResult:
        """Score candidate nodes against query using BM25 and select top_k memories."""
        infected_ids = infected_node_ids or set()
        distractor_ids = distractor_node_ids or set()
        N = len(candidate_nodes)

        if N == 0:
            return ScoredRetrievalResult(
                query_text=query,
                top_k=top_k,
                candidate_pool_size=0,
                selected_memories=[],
                all_ranked_node_ids=[],
                parent_in_top_k=False,
                parent_retrieval_rank=None,
            )

        # 1. Tokenize corpus & query
        tokenized_corpus = [tokenize(node.natural_text) for node in candidate_nodes]
        query_tokens = tokenize(query)
        doc_lens = [len(tokens) for tokens in tokenized_corpus]
        avg_dl = sum(doc_lens) / N if N > 0 else 1.0

        # 2. Document frequency per query term
        df: dict[str, int] = collections.defaultdict(int)
        for tokens in tokenized_corpus:
            unique_terms = set(tokens)
            for q_term in query_tokens:
                if q_term in unique_terms:
                    df[q_term] += 1

        # 3. Compute BM25 score per candidate node
        scored_candidates: list[tuple[float, str, MemoryNode, int]] = []
        for idx, (node, tokens, d_len) in enumerate(zip(candidate_nodes, tokenized_corpus, doc_lens)):
            term_freqs = collections.Counter(tokens)
            score = 0.0
            for q_term in query_tokens:
                if q_term in term_freqs:
                    freq = term_freqs[q_term]
                    n_q = df[q_term]
                    # Robertson-Spärck Jones IDF with smoothing
                    idf = math.log(1.0 + (N - n_q + 0.5) / (n_q + 0.5))
                    tf_component = (freq * (self.k1 + 1.0)) / (
                        freq + self.k1 * (1.0 - self.b + self.b * (d_len / avg_dl))
                    )
                    score += idf * tf_component

            # Deterministic tie-breaker hash
            tie_breaker = hashlib.sha256(node.node_id.encode("utf-8")).hexdigest()
            scored_candidates.append((score, tie_breaker, node, idx))

        # 4. Sort descending by score, then tie-breaker
        scored_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        all_ranked_ids = [item[2].node_id for item in scored_candidates]

        # 5. Determine parent rank
        parent_rank: int | None = None
        if required_parent_id:
            for rank, item in enumerate(scored_candidates):
                if item[2].node_id == required_parent_id:
                    parent_rank = rank
                    break

        parent_in_top_k = (parent_rank is not None and parent_rank < top_k)

        # 6. Select top_k subset
        top_k_candidates = scored_candidates[:top_k]

        # 7. Optionally shuffle presentation order (context position) deterministically
        rng = random.Random(seed)
        shuffled_indices = list(range(len(top_k_candidates)))
        if shuffle_context:
            rng.shuffle(shuffled_indices)

        selected_memories: list[ScoredMemoryNode] = []
        num_inf, num_clean, num_dist = 0, 0, 0

        for ctx_pos, orig_pos in enumerate(shuffled_indices):
            score, _, node, _ = top_k_candidates[orig_pos]
            rank = orig_pos
            is_parent = (node.node_id == required_parent_id) if required_parent_id else False
            is_inf = (node.node_id in infected_ids)

            if is_inf:
                num_inf += 1
            elif node.node_id in distractor_ids:
                num_dist += 1
            else:
                num_clean += 1

            selected_memories.append(
                ScoredMemoryNode(
                    memory_id=node.node_id,
                    text=node.natural_text,
                    bm25_score=score,
                    retrieval_rank=rank,
                    context_position=ctx_pos,
                    is_required_parent=is_parent,
                    is_infected=is_inf,
                    generation=node.generation or 0,
                )
            )

        return ScoredRetrievalResult(
            query_text=query,
            top_k=top_k,
            candidate_pool_size=N,
            selected_memories=selected_memories,
            all_ranked_node_ids=all_ranked_ids,
            parent_in_top_k=parent_in_top_k,
            parent_retrieval_rank=parent_rank,
            num_infected_in_top_k=num_inf,
            num_clean_in_top_k=num_clean,
            num_distractors_in_top_k=num_dist,
        )

