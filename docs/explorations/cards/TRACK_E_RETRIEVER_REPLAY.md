# Experiment Card — Track E: Retriever-Family Replay

## QUESTION
Which GENE conclusions are general mathematical properties of genealogical memory governance and which are artifacts of BM25 lexical token matching geometry?

## PRIMARY MANIPULATION
Replay the frozen 12-ecology retrieval dataset across 4 distinct retrieval algorithms:
1. **BM25** (Lexical token frequency with length normalization).
2. **TF-IDF Cosine** (Term frequency - inverse document frequency vector cosine similarity).
3. **Token Jaccard / Overlap** (Set-theoretic word token overlap).
4. **Dense Semantic Embedding** (Local `nomic-embed-text` dense vector embeddings via cosine distance).

For each retriever algorithm, evaluate:
- Path assembly availability: $X_F, X_A, X_{\text{path}}$ across top-$k \in \{4, 6, 8\}$.
- Delayed adjudication policy metrics: $C_H, C_I, S = C_H - C_I$ under uniform thinning, node-only filtering, and lineage quarantine.

## FROZEN CONTROLS
- 12 frozen synthetic ecologies (identical text, distractor sets, queries, and ground truth DAGs).
- Identical candidate memory pools.
- **Zero live LLM compute (100% deterministic mathematical evaluation)**.

## PRIMARY ENDPOINT
- Verification of the **Lineage-Blind Null-Selectivity Baseline Law**: Does $C_H \equiv C_I \implies S \equiv 0.000$ hold across all 4 retriever architectures?
- Comparison of lineage quarantine selectivity $S_{\text{lineage}}$ across algorithms.

## FALSIFIER
If any lineage-blind memory reduction policy achieves non-zero selectivity ($S > 0$) under any retriever in a balanced symmetric ecology, the Lineage-Blind Null-Selectivity Law is broken.

## ZERO-COMPUTE GATE
This entire experiment is zero-compute ($N = 0$ LLM calls).

## LIVE CALL CEILING
0 calls.

## STOP RULE
Compute complete ranking curves across all 4 retrievers and generate report.

## STATUS
PROVISIONAL — EXPLORATORY ROUND 1
