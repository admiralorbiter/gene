# Experiment Card — Track C: Epistemic Context Compiler Conformance Benchmark

## 1. Core Systems Hypothesis & Privilege Audit
- **Systems Hypothesis:** An Epistemic Context Compiler translating explicit Intermediate Representations (`EpistemicState`) into structured neural contexts can eliminate permutation spread, preserve root counts, and prevent authority amplification without retraining frozen models.
- **Privilege-Audited Pipeline Spectrum:**

```
                            COMPILER PRIVILEGE MATRIX
                            
┌────────────────────────────┬──────────────┬──────────────┬──────────────┬──────────────────┐
│ Pipeline                   │ Changes Order│ Drops/Merges │ Uses S_F     │ Emits Judgment   │
├────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────────┤
│ RAW_SERIALIZATION          │ No           │ No           │ No           │ No               │
│ TOPOLOGY_AWARE_GROUPING    │ Yes          │ Yes (Unlinked│ Yes          │ No               │
│ GENEALOGICAL_NORMALIZATION │ Yes          │ Yes (Copies) │ No           │ No               │
│ PROOF_CARRYING_CERTIFICATE │ Yes          │ No           │ Yes          │ Yes (Entitlement)│
└────────────────────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘
```

## 2. Structured Conformance Matrix & Applicability Vector
Rather than forcing all metrics onto every call, conformance dimensions $\mathcal{K} = (K_A, K_S, K_L, K_I)$ are evaluated according to a formal applicability matrix:

```
                            CONFORMANCE APPLICABILITY MATRIX
                            
┌──────────────────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Evaluation Ecology           │ K_A (Answer)    │ K_S (Support)   │ K_L (Lineage)   │ K_I (Invariance)│
├──────────────────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 1. Entitled Proof (AB+DE)    │ Evaluated (X7)  │ Evaluated (S_F) │ N/A             │ Evaluated       │
│ 2. Pruned Support (AB only)  │ Evaluated (X7)  │ Evaluated (AB)  │ N/A             │ Evaluated       │
│ 3. 4-Copy Laundering (4x A)  │ Evaluated (X7)  │ N/A             │ Evaluated (N=1) │ Evaluated       │
│ 4. Unentitled Null (Ø / Foil)│ Evaluated (UNK) │ N/A             │ N/A             │ Evaluated       │
└──────────────────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### Dimensional Definitions:
1. **$K_A$ (Answer Conformance):** Does output match the formal entitlement status of the state?
2. **$K_S$ (Support Conformance):** Does reported evidence match a valid minimal proof pathway?
3. **$K_L$ (Lineage Conformance):** Under 4-copy paraphrase reproduction, does the compiler prevent root count inflation ($\widehat{N}=1$ vs $\widehat{N}=4$)?
4. **$K_I$ (Invariance Conformance):** Does model behavior remain invariant across semantically equivalent serializations?

## 3. Experimental Evaluation Matrix
We evaluate 4 Compiler Pipelines $\times$ 4 Ecologies $\times$ 2 Stations (`VELORA`, `KESTREL`) = **32 calls**.

## 4. Measurable Endpoints & Analysis
- **Structured Vector Conformance:** Evaluated as a structured vector $(K_A, K_S, K_L, K_I)$ per pipeline.
- **Lineage Inflation Suppression:** Perceived root counts under `RAW_SERIALIZATION` vs `GENEALOGICAL_NORMALIZATION`.
- **Unsupported Concrete Rate:** Frequency of emitting concrete answers when $S_F(c) = \emptyset$.
