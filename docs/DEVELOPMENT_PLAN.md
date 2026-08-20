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

# Current Phase: Phase 10.5 — Experiment 1B-C2 (Live Behavioral Immunity Verification)

## 10.5.1 Scientific Objective
Test whether retrieval-level path availability translates directly into behavioral LLM expression in a shared memory pool:
$$\text{Does } C_I^{\text{retrieval}} = 0 \implies C_I^{\text{behavior}} = 0 \text{ under live neural reasoning?}$$

## 10.5.2 Design & Protocol Constraints (Minimal ~20-Call Gated Assay)
1. **Zero Redundant Probability Grid Evaluations**:
   - The LLM never observes detector probabilities $(\text{TPR}, \text{FPR})$; it only observes the concrete retained prompt context.
2. **Two Role-Swapped Ecologies**:
   - Ecology 1: Pair `(VELORA, KESTREL)` — Forward: Clean $H=\text{VELORA}$, Infected $I=\text{KESTREL}$
   - Ecology 2: Pair `(VELORA, KESTREL)` — Swapped: Clean $H=\text{KESTREL}$, Infected $I=\text{VELORA}$
3. **Five Concrete Post-Policy Contexts**:
   - **Context 1 (`baseline`)**: Full candidate pool retained ($H_2$ and $I_2$ complete).
   - **Context 2 (`node_only`)**: Flagged root removed, but $G_2$ descendant present.
   - **Context 3 (`lineage_quarantine`)**: Flagged root + descendants removed ($G_2$ absent).
   - **Context 4 (`autoimmunity_false_alarm`)**: Healthy root falsely flagged + lineage removed ($H_2$ absent).
   - **Context 5 (`generation_matched_control`)**: Random $G_2$ node removed without lineage guidance.
4. **The $G_3$ Multi-Hop Inference Task**:
   - The model must execute a rule inference combining a $G_2$ transit route with a facility grid premise:
     `If station has transit_route ROUTE_X and facility_grid GRID_Y -> terminal_auth AUTH_Z`
   - **Predictions**:
     - Complete $G_3$ support path $\implies$ active terminal authorization phenotype (e.g. `AUTH_Q7`).
     - Broken $G_3$ support path $\implies$ `UNKNOWN` abstention.
5. **Analytical Reweighting**:
   - Empirically observed discrete model behaviors are analytically reweighted across the continuous $(\text{TPR}, \text{FPR})$ plane.


---

# Inactive Roadmap Backlog (Do Not Build Yet)

The following experiments and features are documented for later research stages and are **strictly inactive**:

- **Experiment 2 — Confirmatory Scale Replication**: Multi-model cross-family replication (e.g. Qwen, Llama, Mistral) on 50–100 worlds.
- **Experiment 3 — Epistemic Monoculture vs. Root Diversity**: Comparing apparent evidence volume from replicated clones versus independent epistemically distinct roots.
- **Experiment 4 — Biological Memory Interventions**: Apoptosis, senescence, write-time proofreading, source anchoring.
- **Experiment 5 — Closed-Loop Multi-Agent Network Ecology**: Multi-agent graph networks with asynchronous message passing and memory transmission.
- **Experiment 6 — Recovery & Epistemic Hysteresis**: Correcting an established root error and measuring lingering contaminated descendants.
- **Experiment 7 — Spontaneous Evolution**: Unseeded multi-generation drift and de novo mutation rates.
- **Dense/Hybrid Retrieval**: Embedding-based retrieval or hybrid BM25 + dense retrieval comparisons.

