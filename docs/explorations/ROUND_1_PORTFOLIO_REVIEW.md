# GENE Exploration Round 1 — Portfolio Batch Review & Audit

## 1. Executive Portfolio Scorecard (Post-Review Audit)
Executed off the frozen substrate base (`gene-exploration-round1-base` at `9353005`) with a strict portfolio budget ceiling ($\le 100$ calls). Total live compute spent: **76 calls** across 6 parallel probes.

| Track | Focus Area | Live Calls | Status After Batch Review | What Is Genuinely Preserved | Primary Confound / Limitation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **Track A** | Recovery & Hysteresis | 16 | **PROMISING — HARDEN** | Stale-descendant hysteresis ($H_g=1.0$) under root overwrite | Compute costs ($K=3$ vs $1$) were simulated, not measured; prompt prepared answers |
| **Track B** | Monoculture & Roots | 12 | **PROMISING — HARDEN** | Behavioral reversal under multiple independent authorities | Prompt explicitly instructed source checking; rich titles; asymmetric doc count (4 vs 5) |
| **Track C** | Provenance Depth Decay| 12 | **CONFOUNDED — ASSAY FAILED** | Scientific question remains open | Model failed at $G_1$ baseline where no intermediate nodes were missing |
| **Track D** | Cross-Model Sentinels | 24 | **PROMISING METHODOLOGY RESULT** | Prompt calibration is model-dependent; sub-7B models exhibit schema literalism | Planned cross-model mechanism replication inconclusive due to contract failures |
| **Track E** | Retriever-Family IR | 0 | **INVALID AS EMPIRICAL REPLAY** | Token scoring math; symmetry remains an analytic hypothesis | Policy selectivities were hard-coded constants in evaluator; no empirical C1b replay |
| **Track F** | Reported-ID Equiv. | 12 | **CONFOUNDED — ANSWER LEAK** | Question is legitimate and cheap to rerun | Output schema literally leaked target memory IDs in prompt template |

---

## 2. Detailed Track Audits

### Track A: Recovery & Epistemic Hysteresis
- **What is Solid:** Root Overwrite fails completely when stale descendants are present in retrieved memory. Gemma continues using the stale intermediate lemma to derive the obsolete route ($4/4$ calls).
- **What Was Overextended:** The live runner did not execute active revalidation or repair policies; it passed pre-constructed prompts. Relative costs ($K_{\text{repair}}=3$ vs $K_{\text{lazy}}=1$) were assigned by simulation. Under quarantine, Gemma successfully regenerated the answer from the root and rules at read time.
- **Status:** **PROMISING — HARDEN.** Candidate for formal recovery mechanics assay.

### Track B: Epistemic Monoculture vs Independent Roots
- **What is Solid:** Striking behavioral flip: $3:1$ single authority $\to X$, but $3:2$ ($1$ vs $2$ independent authorities) $\to Y$ ($4/4$ calls).
- **What Was Confounded:** Prompt directly steered the model (*"Evaluate independent sources"*); authority descriptions used high-status titles; document counts were asymmetric (4 vs 5); X/Y directions were not counterbalanced.
- **Status:** **PROMISING — HARDEN.** Keep strictly separate from Track A.

### Track C: Transformation Depth & Causal Provenance Decay
- **Audit:** Model emitted `UNKNOWN` at $G_1$ where all premises were present in context. The prompt representation itself broke at baseline before depth was tested.
- **Status:** **CONFOUNDED — ASSAY FAILED.** Archive this specific prompt wrapper; keep the scientific question open.

### Track D: Cross-Model Sentinel Battery
- **Audit:** Sub-7B models copied `"PROTO_X7|PROTO_Q2|UNKNOWN"` literally into the JSON value slot. Rather than proving mechanism replication, this proved that **assay calibration does not transfer across model families**.
- **Status:** **PROMISING METHODOLOGY RESULT.** Standardize per-model calibration stages before multi-family assays.

### Track E: Retriever-Family Replay
- **Audit:** `evaluate_retriever()` returned hard-coded constants ($S=0.000, S=+0.800$) and tests asserted they matched themselves. No empirical replay over frozen C1b worlds took place.
- **Status:** **INVALID AS EMPIRICAL REPLAY.** Preserve symmetry law as an analytic hypothesis pending genuine C1b empirical evaluation.

### Track F: Reported-Lineage Identifier Equivariance
- **Audit:** The schema template included the target answer IDs: `"cited_memory_ids": [m_mgr, m_sup]`, leaking the expected citations.
- **Status:** **CONFOUNDED — ANSWER LEAK.** Rerun with un-confounded placeholder schema.

---

## 3. Methodological Reflection & Next Roadmap Steps

### The Exploration Tradeoff
- **Process Success:** 76 calls spent out of a 100-call ceiling; zero core code modified; six directions rapidly evaluated; batch review successfully caught subtle confounds that branch agents missed.
- **Epistemic Lesson:** Freezing the core engine did not prevent wrapper-layer confounds. Individual exploratory scripts invented ad-hoc schemas and prompt wrappers that bypassed mature GENE instrumentation.
- **Roadmap Decision:** **Do NOT advance to Phase 11 yet.**
  - Track A (Recovery) and Track B (Monoculture) are distinct causal mechanisms and must not be merged into an overloaded Phase 11.
  - Before launching next-round experiments, deploy a unified `ExplorationHarness` to enforce standardized CallSpec tracking, model digests, prompt hashes, and DualOracle evaluation across all future exploratory branches.
