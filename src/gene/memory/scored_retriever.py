"""Deterministic BM25 Scored Top-k Retriever for GENE Experiments.

Provides auditable, mathematically transparent lexical ranking over candidate memory pools
without requiring external vector databases or non-deterministic embeddings:
- Standard Okapi BM25 scoring: k1=1.5, b=0.75.
- Deterministic paired-arm stable tie-breaking using paired_slot_id (independent of allele hash).
- Multi-hop support tracking: founder recall X_F, co-support recall X_A, and full-path recall X_path.
- Full candidate ledger persistence output.
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
from gene.worlds.schema import Fact


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric tokens."""
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())


class EvaluatedCandidate(BaseModel):
    """An individual memory node evaluated by the scored retriever."""
    memory_id: str
    paired_slot_id: str
    text: str
    bm25_score: float
    retrieval_rank: int
    is_selected: bool = False
    context_position: int | None = None
    structured_fact: Fact | None = None
    is_founder: bool = False
    is_co_support: bool = False
    is_required_path: bool = False
    is_infected: bool = False
    is_distractor: bool = False
    generation: int = 0


class ScoredRetrievalResult(BaseModel):
    """Auditable output of a scored top-k retrieval operation."""
    query_text: str
    top_k: int
    candidate_pool_size: int
    selected_memories: list[EvaluatedCandidate]
    all_evaluated_candidates: list[EvaluatedCandidate]
    
    # Multi-hop support recall indicators
    founder_retrieved: bool = False
    founder_retrieval_rank: int | None = None
    co_support_retrieved: bool = False
    co_support_retrieval_rank: int | None = None
    path_retrieved: bool = False
    
    # Top-k composition breakdown
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
        founder_node_id: str | None = None,
        co_support_node_ids: set[str] | None = None,
        infected_node_ids: set[str] | None = None,
        distractor_node_ids: set[str] | None = None,
        shuffle_context: bool = True,
        seed: int = 42,
    ) -> ScoredRetrievalResult:
        """Score candidate nodes against query using BM25 and select top_k memories."""
        co_support_ids = co_support_node_ids or set()
        infected_ids = infected_node_ids or set()
        distractor_ids = distractor_node_ids or set()
        N = len(candidate_nodes)

        if N == 0:
            return ScoredRetrievalResult(
                query_text=query,
                top_k=top_k,
                candidate_pool_size=0,
                selected_memories=[],
                all_evaluated_candidates=[],
                founder_retrieved=False,
                co_support_retrieved=False,
                path_retrieved=False,
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

            # Stable paired tie-breaker key (independent of allele value/hash)
            # Uses locus_id, generation, and node_type
            paired_slot = f"{node.generation}_{node.locus_id or 'none'}_{node.node_type}_{idx}"
            scored_candidates.append((score, paired_slot, node, idx))

        # 4. Sort descending by score, then paired slot tie-breaker
        scored_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)

        # 5. Build full evaluated candidate list and ranks
        evaluated_all: list[EvaluatedCandidate] = []
        founder_rank: int | None = None
        co_support_ranks: list[int] = []

        for rank, (score, paired_slot, node, _) in enumerate(scored_candidates):
            is_founder = (node.node_id == founder_node_id) if founder_node_id else False
            is_co_sup = (node.node_id in co_support_ids)
            is_req_path = is_founder or is_co_sup
            is_inf = (node.node_id in infected_ids)
            is_dist = (node.node_id in distractor_ids)

            if is_founder:
                founder_rank = rank
            if is_co_sup:
                co_support_ranks.append(rank)

            struct_fact = None
            if node.structured_json:
                try:
                    struct_fact = Fact.model_validate(node.structured_json)
                except Exception:
                    struct_fact = None

            evaluated_all.append(
                EvaluatedCandidate(
                    memory_id=node.node_id,
                    paired_slot_id=paired_slot,
                    text=node.natural_text,
                    bm25_score=score,
                    retrieval_rank=rank,
                    is_selected=False,
                    context_position=None,
                    structured_fact=struct_fact,
                    is_founder=is_founder,
                    is_co_support=is_co_sup,
                    is_required_path=is_req_path,
                    is_infected=is_inf,
                    is_distractor=is_dist,
                    generation=node.generation or 0,
                )
            )

        # 6. Evaluate multi-hop support recall
        founder_retrieved = (founder_rank is not None and founder_rank < top_k)
        co_support_retrieved = False
        if co_support_ids:
            # Check if all required co-support nodes are in top-k
            co_support_retrieved = (
                len(co_support_ranks) == len(co_support_ids)
                and all(r < top_k for r in co_support_ranks)
            )
        else:
            co_support_retrieved = True

        path_retrieved = founder_retrieved and co_support_retrieved

        # 7. Select top_k subset
        top_k_candidates = evaluated_all[:top_k]

        # 8. Deterministically shuffle presentation order (context position)
        rng = random.Random(seed)
        shuffled_indices = list(range(len(top_k_candidates)))
        if shuffle_context:
            rng.shuffle(shuffled_indices)

        selected_memories: list[EvaluatedCandidate] = []
        num_inf, num_clean, num_dist = 0, 0, 0

        for ctx_pos, orig_pos in enumerate(shuffled_indices):
            cand = top_k_candidates[orig_pos]
            cand.is_selected = True
            cand.context_position = ctx_pos

            if cand.is_infected:
                num_inf += 1
            elif cand.is_distractor:
                num_dist += 1
            else:
                num_clean += 1

            selected_memories.append(cand)

        return ScoredRetrievalResult(
            query_text=query,
            top_k=top_k,
            candidate_pool_size=N,
            selected_memories=selected_memories,
            all_evaluated_candidates=evaluated_all,
            founder_retrieved=founder_retrieved,
            founder_retrieval_rank=founder_rank,
            co_support_retrieved=co_support_retrieved,
            co_support_retrieval_rank=min(co_support_ranks) if co_support_ranks else None,
            path_retrieved=path_retrieved,
            num_infected_in_top_k=num_inf,
            num_clean_in_top_k=num_clean,
            num_distractors_in_top_k=num_dist,
        )


