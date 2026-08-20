# Experiment Card — Track C: Epistemic Context Compiler Conformance Benchmark

## 1. Core Systems Hypothesis & Privilege Audit
- **Systems Hypothesis:** An Epistemic Context Compiler translating explicit Intermediate Representations (`EpistemicState`) into structured neural contexts can eliminate permutation spread, preserve root counts, and prevent duplicate authority amplification without retraining frozen models.
- **Privilege-Audited Pipeline Spectrum:**

```
                            COMPILER PRIVILEGE MATRIX
                            
┌────────────────────────────┬──────────────┬──────────────┬──────────────┬───────────────────────────────┐
│ Pipeline                   │ Changes Order│ Drops/Merges │ Uses S_F     │ Emits Judgment                │
├────────────────────────────┼──────────────┼──────────────┼──────────────┼───────────────────────────────┤
│ RAW_SERIALIZATION          │ No           │ No           │ No           │ No                            │
│ TOPOLOGY_AWARE_GROUPING    │ Yes          │ Yes (Unlinked│ Yes          │ No                            │
│ GENEALOGICAL_NORMALIZATION │ Yes          │ Yes (Copies) │ No           │ No                            │
│ PROOF_CARRYING_CERTIFICATE │ Yes          │ No           │ Yes          │ Yes (Entitlement + Root Count)│
└────────────────────────────┴──────────────┴──────────────┴──────────────┴───────────────────────────────┘
```

*Note on Proof-Carrying Certificate:* The `PROOF_CARRYING_CERTIFICATE` backend explicitly emits both formal entitlement status and distinct ancestral root counts. Its results evaluate behavioral compliance with an explicit epistemic certificate, in contrast to lower-privilege backends where the model must independently preserve lineage semantics.

---

## 2. Non-Leaking Backend-Neutral Output Schema & Conformance Applicability
The model is presented with a backend-neutral generic schema indexing retrieved evidence lines (`DOC_01`, `DOC_02`, etc.):
```json
{
  "station": "STATION_NAME",
  "protocol": "PROTOCOL_NAME_OR_UNKNOWN",
  "reported_support_evidence": ["DOC_01", "DOC_02"],
  "independence_status": "determinable|indeterminable",
  "perceived_independent_roots": "INTEGER_OR_NULL",
  "evidence_status": "sufficient|insufficient"
}
```

```
                            CONFORMANCE APPLICABILITY MATRIX
                            
┌─────────────────────────────────┬─────────────────┬─────────────────┬───────────────────────────────┬─────────────────┐
│ Evaluation Ecology              │ K_A (Answer)    │ K_S (Support)   │ K_L (Lineage | Determinable)  │ K_I (Invariance)│
├─────────────────────────────────┼─────────────────┼─────────────────┼───────────────────────────────┼─────────────────┤
│ 1. Entitled Proof (AB+DE)       │ Evaluated (X7)  │ Evaluated (S_F) │ N/A                           │ Evaluated (P)   │
│ 2. Pruned Support (AB only)     │ Evaluated (X7)  │ Evaluated (AB)  │ N/A                           │ Evaluated (P)   │
│ 3. Exact-Copy Multiplication    │ Evaluated (X7)  │ N/A             │ Evaluated (N_root=1)          │ Evaluated (P)   │
│    (4 identical copies of A)    │                 │                 │                               │                 │
│ 4. Unentitled Null (Ø / Distr.) │ Evaluated (UNK) │ N/A             │ N/A                           │ Evaluated (P)   │
└─────────────────────────────────┴─────────────────┴─────────────────┴───────────────────────────────┴─────────────────┘
```

### Dimensional Definitions:
1. **$K_A$ (Answer Conformance):** Does strict JSON output match the formal entitlement status of the state?
2. **$K_S$ (Support Conformance):** Does reported evidence (mapped from `DOC_xx` tags back to semantic claims) contain a valid minimal proof pathway in $S_F$?
3. **$K_L$ (Lineage Conformance):** Under exact-copy reproduction ($1A \to 4A$ with shared root $R1$), does the compiler preserve root count truth ($\widehat{N}=1$ vs $\widehat{N}=4$)?
4. **$K_I$ (Invariance Conformance):** Measured in Track P across 24 permutations ($K_I = 1.0 - \mathcal{D}_{\text{perm}}$).

---

## 3. Experimental Evaluation Matrix
We evaluate 4 Compiler Pipelines $\times$ 4 Ecologies $\times$ 2 Stations (`VELORA`, `KESTREL`) = **32 calls**.

## 4. Measurable Endpoints & Analysis
- **Structured Vector Conformance:** Evaluated as a structured vector $(K_A, K_S, K_L)$ per pipeline.
- **Copy Multiplication Suppression:** Perceived root counts under `RAW_SERIALIZATION` vs `GENEALOGICAL_NORMALIZATION`.
- **Unsupported Concrete Rate:** Frequency of emitting concrete answers when $S_F(c) = \emptyset$.
