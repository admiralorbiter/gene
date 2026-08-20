# Experiment Card — Track C: Epistemic Context Compiler Conformance Benchmark

## 1. Core Systems Hypothesis & Privilege Audit
- **Systems Hypothesis:** An Epistemic Context Compiler translating explicit Intermediate Representations (`EpistemicState`) into structured neural contexts can eliminate permutation spread, preserve root counts, and prevent authority amplification without retraining frozen models.
- **Privilege-Audited Pipeline Spectrum:** Rather than treating backends as opaque prompt variations, we evaluate a structured privilege spectrum:

```
                            COMPILER PRIVILEGE MATRIX
                            
┌────────────────────────────┬──────────────┬──────────────┬──────────────┬──────────────────┐
│ Pipeline                   │ Changes Order│ Drops/Merges │ Uses S_F     │ Emits Judgment   │
├────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────────┤
│ RAW_SERIALIZATION          │ No           │ No           │ No           │ No               │
│ TOPOLOGY_AWARE_GROUPING    │ Yes          │ No           │ Yes          │ No               │
│ GENEALOGICAL_NORMALIZATION │ Yes          │ Yes (Dedup)  │ Yes          │ No               │
│ PROOF_CARRYING_CERTIFICATE │ Yes          │ No           │ Yes          │ Yes (Entitlement)│
└────────────────────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘
```

## 2. Multi-Dimensional Conformance Vector $\mathcal{K} = (K_A, K_S, K_L, K_I)$
We evaluate compiler performance across four orthogonal conformance dimensions:
1. **$K_A$ (Answer Conformance):** Does the model's output match the formal entitlement status of the underlying epistemic state?
2. **$K_S$ (Support Conformance):** Does the reported evidence path correspond to a valid $S_F$ minimal proof?
3. **$K_L$ (Lineage Conformance):** Under 4-copy paraphrase reproduction ($N_{\text{vis}}=4, N_{\text{root}}=1$), does the compiler prevent root count inflation ($\widehat{N}=1$ vs $\widehat{N}=4$)?
4. **$K_I$ (Invariance Conformance):** Does model behavior remain invariant across semantically equivalent premise orderings?

## 3. Experimental Evaluation Matrix
We test 4 Compiler Pipelines $\times$ 4 Test Ecologies (Entitled Canonical, Single-Path Pruned, 4-Copy Paraphrase, Unentitled Null) $\times$ 2 Stations = **32 calls**.

## 4. Measurable Endpoints & Analysis
- **Vector Conformance Score:** Joint satisfaction rate of $\mathcal{K} = (K_A \land K_S \land K_L \land K_I)$.
- **Lineage Inflation Suppression:** Comparison of perceived root counts under `RAW_SERIALIZATION` vs `GENEALOGICAL_NORMALIZATION`.
- **Unsupported Concrete Rate:** Frequency of hallucinating a concrete protocol when $S_F(c) = \emptyset$.
