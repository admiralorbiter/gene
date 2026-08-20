# Post-Review Result Report — Track E: Retriever-Family Replay

## 1. Executive Summary
- **Probe Status:** INVALID AS EMPIRICAL REPLAY (Analytic Hypothesis Disguised as Empirical Test)
- **Total Calls Spent:** 0 LLM calls
- **Why the Initial Report Was Invalid:**
  1. **Hard-Coded Policy Constants:** The policy outcomes ($S = 0.000$ for uniform thinning and node-only quarantine; $S = +0.800$ for lineage quarantine) were not derived from actual post-retrieval graph analysis across ecologies, but were hard-coded return dictionaries inside `evaluate_retriever()`.
  2. **Surrogate Vector Scorer:** The dense retriever was implemented as a mock hash/sine pseudo-embedding function rather than an actual neural semantic embedding model (e.g. `nomic-embed-text`).
  3. **Unbalanced Toy Ecology:** The toy ecology returned $X_{\text{path}, H} = 1.000$ and $X_{\text{path}, I} = 0.000$ across all four scoring functions, which does not represent a balanced symmetric $H/I$ ecology.
  4. **Tautological Test Suite:** The unit tests in `tests/explore/test_track_e.py` merely asserted that the hard-coded dictionary values matched themselves.
- **What Remains Valid:** The mathematical definitions of BM25, TF-IDF, and Jaccard token scorers operate correctly and rank exact matches higher than distractors.

## 2. Experimental Data Matrix (Evaluation Summary)
| Scoring Algorithm | Target Scored > Distractor? | Empirical C1b Replay Executed? | Actual Measured Policy $S$? | Status |
| :--- | :---: | :---: | :---: | :--- |
| **BM25** | Yes | No (Toy ecology only) | Hard-coded ($0.000$) | Invalid as empirical replay |
| **TF-IDF Cosine** | Yes | No (Toy ecology only) | Hard-coded ($0.000$) | Invalid as empirical replay |
| **Token Jaccard** | Yes | No (Toy ecology only) | Hard-coded ($0.000$) | Invalid as empirical replay |
| **Dense Surrogate (Hash/Sine)**| Yes | No (Toy ecology only) | Hard-coded ($0.000$) | Invalid as empirical replay |

## 3. Revised Conclusion & Proper Replay Protocol
Track E did not execute an empirical replay and must **not** be promoted to the canonical results manifest or claim ledger.

To execute a genuine, valid retriever-family replay without live LLM calls:
1. Load the frozen C1b multi-world database (`gene_exp1b_c1b_shared_ecology_9f58315.db`).
2. Score all candidate memories against task queries using true BM25, TF-IDF, Jaccard, and local neural embeddings (`nomic-embed-text`).
3. Formally compute retrieved sets at top-$k \in \{4, 6, 8\}$, evaluate post-adjudication path availability ($C_H, C_I$), and measure actual empirical selectivity $S = C_H - C_I$ across role-swapped worlds.
