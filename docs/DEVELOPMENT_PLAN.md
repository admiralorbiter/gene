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

# Current Phase: Phase 10 — Experiment 1B-C (Delayed Adjudication & Lineage Immunity Sandbox)

## 10.1 Conceptual & Epistemic Constraints
- **Lineage Propagates Distrust, Not Truth**: Because clean and infected graph topologies are isomorphic, a policy seeing only structural metadata cannot determine truth without an oracle.
- **External Risk Signal**: An imperfect binary risk signal arrives at root memories ($S \in \{0, 1\}$) with controlled sensitivity ($\text{TPR} \in \{0.5, 0.75, 0.9, 1.0\}$) and specificity ($\text{FPR} \in \{0.0, 0.05, 0.10, 0.20, 0.40\}$).
- **Oracle Isolation**: The policy never receives canonical $T^*$. The experimental harness uses $T^*$ solely to synthesize the detector with pre-registered $(\text{TPR}, \text{FPR})$.
- **Delayed Adjudication Timeline**: $G_0 \to G_1 \to G_2$ propagation has already occurred. The risk signal arrives at $G_0$, and the system evaluates future $G_3$ reproduction path availability ($C_H = X_{\text{path},H}^{\text{post}}, C_I = X_{\text{path},I}^{\text{post}}$).

## 10.2 Staged Implementation Sequence (Zero Live Compute First)
1. **Experiment 1B-C0 (Policy Engine Golden Calibration)**:
   - Analytical verification of 6 policies (`baseline`, `uniform_thinning`, `random_family_quarantine`, `node_only_quarantine`, `lineage_quarantine`, `oracle_upper_bound`) across 4 discrete root-signal states $(S_H, S_I)$ weighted by exact joint probabilities.
   - Verify algebraic identities (e.g. $\text{TPR}=\text{FPR} \implies S = 0$, $\text{TPR}=1, \text{FPR}=0 \implies C_H=1, C_I=0$).
2. **Experiment 1B-C1 (Delayed-Adjudication Retrieval Sandbox, $G_2 \to G_3$)**:
   - Evaluate post-adjudication retrieval on frozen $G_0 \to G_2$ trees across 6 paired boundary worlds (seeds 7000..7005).
   - Measure $C_H$, $C_I$, Containment ($1 - C_I$), Epistemic Autoimmunity ($1 - C_H$), and Separation ($S = C_H - C_I$).
   - Identify whether a non-trivial region exists where lineage quarantine achieves a Pareto improvement over node-only and topology-matched controls without excessive healthy path loss.
3. **Gated Tiny Live Follow-Up**:
   - If and only if the deterministic sandbox shows a clear Pareto frontier, execute a minimal live mechanism check (2–3 informative detector points) on `gemma3:12b`.

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

