# GENE Development Plan

## Objective

Get from an empty repository to trustworthy, reproducible results on epistemic lineage propagation, retrieval dynamics, and selective immunity with the fewest moving parts possible.

The plan is strictly gated:
> **Cheap deterministic measurement $\to$ tiny live mechanism test $\to$ review $\to$ only then scale.**

---

# Completed Phases

### Phase 0 — Repository and Invariants (Completed)
- Package scaffold, SQLite persistence, deterministic hashing, foreign keys.

### Phase 1 — Synthetic World + Forward-Chaining Oracle (Completed)
- Deterministic world generator, clean/mutated paired invariant, golden closure tests.

### Phase 2 — Auditable Ollama Adapter (Completed)
- Structured schema extraction, token/latency timing, dynamic digest capture.

### Phase 3 — Memory & Lineage Instrumentation (Completed)
- Append-only memory store, exposure logger, reported-support edges.

### Phase 4 — Counterfactual Causal Runner (Completed)
- Parent-removal interventions, clean-counterpart replacements, causal evidence classifications.

### Phase 5 & 6 — Experiment 0 (Lineage Observability) (Completed & Validated)
- Lineage observability, parent reporting accuracy, reject option, causal parent validation.

### Phase 7 — Experiment 1A (Single Mutation Cascades) (Completed & Validated)
- Multi-generation propagation across generations 0–2, de novo vs. transmitted errors.

### Phase 8 — Experiment 1B-A & 1B-B (Transmission, Multi-Hop Retrieval & Surface-Area Scaling) (Completed & Validated)
- 1B-A: Multi-generation branching processes, allele fidelity, analytic next-generation extinction matrix.
- 1B-B1: Endogenous multi-hop retrieval ($X_F, X_A, X_{\text{path}}$), hard-negative lexical competition, causal retrieval rescue ($k=4 \to k=6$).
- 1B-B2: Lineage surface-area scaling ($N_{\text{lin}} \in \{0,1,2,4,8\}$).

---

### Phase 9 & 9.5 — Hardening, Boundary Preflight, Live Rescue & Matched Expression (Completed & Frozen)
- Phase 9: Occurrence node linkage for all outputs (active vs inactive `UNKNOWN`), run lifecycle tracking, pure B2 single-allele semantics, deterministic retrieval shape map ($k \in \{3..8\} \times N_{\text{hard}} \in \{0..12\}$), and 48-call live causal rescue verification on Gemma 3:12B ($k=4 \to k=6$).
- Phase 9.5: Exp 1B-B1c matched path sufficiency assay (16 live calls) demonstrating perfect path-conditioned expression symmetry ($P(\text{active}\mid\text{complete}, H) = P(\text{active}\mid\text{complete}, I) = 1.00$ and $P(\text{active}\mid\text{broken}, H) = P(\text{active}\mid\text{broken}, I) = 0.00$) under stable slot IDs (`mem_{locus_id}`) and matched 6-memory geometry.

---

### Phase 10 — Experiment 1B-C0 & 1B-C1b (Selective Epistemic Immunity Sandbox) (Completed & Frozen)
- **1B-C0 (Policy Calibration Engine)**: Exact 4-state analytical verification of 8 policies across continuous $(\text{TPR}, \text{FPR})$ risk space.
- **1B-C1b (Shared-Ecology Sandbox & Full Control Envelope)**:
  - 12 fully balanced, role-swapped ecologies across all 6 station pairs.
  - Demonstrated strict empirical null selectivity ($S \equiv 0.000$) for all stochastic lineage-blind controls ($N_{\text{mc}} = 100$).
  - Proved complete descendant laundering under node-only quarantine ($C_I \equiv 1.000$).
  - Full budget sweep ($m \in \{0..14\}$) establishing the convexified theoretical control frontier $C_I^*(c) = c$.
  - Proved the Golden Identity: $\Delta_I(c) = \text{TPR} - \text{FPR} = S$, demonstrating a $+80.0\%$ matched-coverage containment advantage ($\Delta_I = +0.800$ at 90/10) over the lineage-blind theoretical diagonal.

---

### Phase 10.5 — Experiment 1B-C2 (Live Behavioral Immunity, Replay Stability & Epistemic Proofreading) (Completed & Frozen)
- **1B-C2 & C2a (50 Live Calls on Gemma 3:12B)**:
  - Validated that selective lineage quarantine achieves 100% live behavioral containment ($C_I^{\text{behavior}} = 0.000$) while preserving healthy coverage ($C_H^{\text{behavior}} = 1.000$).
  - Proved that node-only quarantine suffers 100% descendant-mediated laundering ($C_I^{\text{behavior}} = 1.000$).
  - Established the **Replay Stability Principle**: empirical response branching observed under identical prompts ($T=0$, seed=42) in local GPU runtimes.
  - Decoupled **Reproductive Status** (`active` vs `inactive`) from **Epistemic State Vector** $(T^*, D_{\text{ctx}}, A, E, K)$ with nullable canonical truth $T^* \in \{0, 1, \emptyset\}$.
- **1B-C2b (30 Live Calls on Gemma 3:12B — Binding Disambiguation & Layer 2 Proofreading)**:
  - Mapped the pseudo-path trigger surface: explicit mismatched routes induce 100% clean abstention ($12/12$), while zero routes induce single-premise conclusion jumping ($6/6$).
  - Validated the **Two-Layer Epistemic Defense Architecture**:
    - Layer 1 (Memory Governance) removes transmission paths ($X_{\text{path}} = 0$).
    - Layer 2 (Structural Epistemic Proofreader / Support-Certificate Validator) mechanically verifies rule antecedent unification from cited memories.
    - Measured Evolutionary Admission Dynamics: $\mu_{\text{expression}} = 0.400$ ($1.000$ on broken paths) reduced to $\mu_{\text{heritable}} = \mathbf{0.000}$ ($0 / 12$ false admissions).

---

# Inactive Roadmap Backlog (Do Not Build Yet)

The following experiments and features are documented for later research stages and are **strictly inactive**:

- **Experiment 2 — Confirmatory Scale Replication**: Multi-model cross-family replication (e.g. Qwen, Llama, Mistral) across 50–100 procedural worlds.
- **Experiment 3 — Epistemic Monoculture vs. Root Diversity**: Comparing apparent evidence volume from replicated clones versus independent epistemically distinct roots.
- **Experiment 4 — Deep Provenance Decay & Epistemic Laundering**: Measuring multi-generation transformation drift and causal attribution loss over deep derivation graphs ($G_5+$).
- **Experiment 5 — Recovery & Epistemic Hysteresis**: Correcting an established root error and measuring lingering contaminated descendants after rectification.
- **Experiment 6 — Closed-Loop Multi-Agent Network Ecology**: Multi-agent graph networks with asynchronous message passing and memory transmission.
- **Dense/Hybrid Retrieval**: Embedding-based retrieval or hybrid BM25 + dense retrieval comparisons.


