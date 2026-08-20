# GENE Exploration Round 1 — Portfolio Batch Review & Phase 11 Decision Card

## 1. Executive Portfolio Scorecard
Executed under strict substrate freeze (`gene-exploration-round1-base` at `9353005`) with a total budget cap of $\le 100$ live calls. Total live compute spent: **76 calls** across 6 parallel probes.

| Track | Focus Area | Live Calls Spent | Scientific Value (0-5) | Robustness (0-5) | Novelty (0-5) | Hardening Cost (0-5, 5=low) | Recommendation |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Track A** | Recovery & Epistemic Hysteresis | 16 | 5.0 | 5.0 | 4.5 | 4.0 | **PRIMARY CANDIDATE FOR PHASE 11** |
| **Track B** | Epistemic Monoculture & Roots | 12 | 4.5 | 5.0 | 4.5 | 4.0 | **MERGE INTO PHASE 11 (Channel 2 Co-Factor)** |
| **Track C** | Provenance Depth Decay | 12 | 3.5 | 4.0 | 3.0 | 2.5 | **ARCHIVE (Foundational Boundary Established)** |
| **Track D** | Cross-Model Sentinel Battery | 24 | 4.0 | 4.0 | 3.5 | 3.5 | **HARDEN AS PERMANENT SENTINEL SUITE** |
| **Track E** | Retriever-Family Replay | 0 | 4.5 | 5.0 | 4.0 | 5.0 | **PROMOTE TO CANONICAL EVIDENCE LAYER** |
| **Track F** | Reported-ID Equivariance | 12 | 3.5 | 5.0 | 3.0 | 5.0 | **CLOSE & ARCHIVE (Invariant Established)** |

---

## 2. Synthesis of Discoveries Across the Six Tracks

### Track A: Recovery & Epistemic Hysteresis (Winner for Phase 11)
- **Finding:** Correcting a false premise at the root ($G_0: \text{TAL} \leadsto \text{KIRA}$) **fails completely** to cure epistemic infection downstream if intermediate descendants remain in the memory pool ($H_g = 1.000, C_{\text{repair}} = 0.000$). Downstream reasoners retrieve the cached intermediate lemmas and continue expressing the false phenotype.
- **Solution:** While proactive eager recomputation (`lineage_repair`) works ($C_{\text{repair}} = 1.000$), lazy **`revalidate_on_use`** achieves identical $100\%$ recovery at $1/3$ the computational cost ($K = 1.0$ vs $3.0$).
- **Recommendation:** **Promote to Phase 11.** Build the formal mechanics of lazy vs eager lineage repair.

### Track B: Epistemic Monoculture vs Independent Roots
- **Finding:** Language models are vulnerable to genealogical monoculture when citations cite a single authority ($3:1$ raw vs $1:1$ roots $\implies$ falls back to repetition), but counterfactually flip to the minority count when the minority possesses **multiple independent authorities** ($3:2$ raw in favor of X vs $1:2$ roots in favor of Y $\implies P(Y) = 1.000$).
- **Recommendation:** **Merge with Track A in Phase 11** as an evidence aggregation metric ($N_{\text{eff}} = 1/\sum p_r^2$).

### Track C: Transformation Depth & Causal Provenance Decay
- **Finding:** Zero-shot multi-hop derivation without intermediate scratchpad tokens collapses into universal abstention ($P(\text{abstain}) = 1.000$) when intermediate lemmas are not materialized in memory.
- **Recommendation:** **Archive.** Proves that intermediate node persistence in the DAG is a non-optional requirement for deep reasoning.

### Track D: Cross-Model Sentinel Battery
- **Finding:** Core semantic inheritance ($0 \to 1$ transmission) and retrieval gating replicate across model families (Gemma 3:12B, Qwen 2.5:3B). However, sub-7B models require grammar-constrained JSON decoding to prevent schema reproduction.
- **Recommendation:** Maintain the 4-pair sentinel battery in CI as a regression benchmark across model updates.

### Track E: Retriever-Family Replay (Zero Compute)
- **Finding:** The **Lineage-Blind Null-Selectivity Baseline Law ($C_H \equiv C_I \implies S \equiv 0.000$)** is 100% mathematically invariant across BM25, TF-IDF Cosine, Token Jaccard, and Dense Semantic Embeddings.
- **Recommendation:** Update `data/claim_ledger.json` and manifest with multi-retriever invariance proofs during the next formal release cycle.

### Track F: Reported-Lineage Identifier Equivariance
- **Finding:** The self-reported support lineage interface ($\mathcal{R}$) is perfectly equivariant to ID naming schemes ($A_{\text{ID}} = 1.000, E_{\text{ID}} = 0.000$) across natural words, short codes, and random hashes.
- **Recommendation:** Close and archive as an established invariant.

---

## 3. Phase 11 Milestone Recommendation

### **Proposed Phase 11: Active Lineage Repair, Dynamic Recovery & Epistemic Re-Adjudication**
1. **Core Problem:** When an upstream premise is retracted or updated, how does a persistent memory system actively heal corrupted descendant trees without incurring prohibitive recomputation costs or retaining ghost hysteresis?
2. **Key Mechanisms to Formalize:**
   - **Lazy Revalidate-on-Use ($R_{\text{lazy}}$):** Ancestral invalidation flags checked at retrieval time; recomputation triggered only on cache miss.
   - **Effective Evidence Diversity ($N_{\text{eff}}$):** Multi-root corroboration discount function $N_{\text{eff}} = 1/\sum p_r^2$ integrated into retrieval ranking.
   - **Repair Selectivity Envelope:** Measuring repair precision $\text{Prec}_{\text{repair}}$ and compute savings $\Delta K$ across multi-generation branching ecologies.
