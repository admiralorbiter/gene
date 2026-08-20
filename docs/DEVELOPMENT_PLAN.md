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

# Current Phase: Phase 9 — Infrastructure Hardening & Retrieval Boundary Preflight

## Objectives (Zero Live LLM Calls)
1. **Persistence Hardening**:
   - Ensure every G1 and G2 model output creates an occurrence node in `memory_nodes` (`is_active=1` if written, `is_active=0` if `UNKNOWN`/abstention).
   - Ensure `dual_oracle_evaluations` points directly to `node_id`.
   - Update `runs.status` to `"completed"` (with `completed_at`) upon finishing, or `"failed"` on unhandled exceptions.
   - Add `retrieval_sweep_results` table in SQLite so all sweep metrics are queryable from SQLite.
2. **Pure B2 Baseline Semantics**:
   - Implement `mode="pure"` for the B2 surface-area assay (removing the clean counterpart at the founder locus so only the mutated founder is present).
   - Rerun 4-world pure multiplicity sweep (deterministic BM25) and verify whether monotonic surface-area scaling holds.
3. **Deterministic Retrieval Boundary Shape Map**:
   - Execute a 6-world paired clean/infected preflight over $k \in \{3, 4, 5, 6, 8\}$ and $N_{\text{hard}} \in \{0, 2, 4, 8, 12\}$ with 4 easy distractors.
   - Persist all rankings, compute exploratory assembly gap $G_{\text{assembly}} = \min(X_F, X_A) - X_{\text{path}}$, ranks, and margins.
   - Identify 2–4 boundary candidate worlds for live follow-up gating.

---

# Next Phase: Phase 10 — Experiment 1B-C (Lineage-Aware Selective Immunity Sandbox)

## 10.1 Deterministic Policy Sandbox (Offline First, Zero LLM Calls)
- Test non-oracle lineage filters against equal-budget baselines (BM25, uniform thinning, lineage-aware diversity rerankers).
- Linage policy receives ancestry metadata only (no ground truth $T^*$, no secret false flags).
- Evaluate separation:
  $$X_{\text{path},H} \gg X_{\text{path},I}$$
- If deterministic lineage rules cannot shift this frontier offline, do not spend live model compute.

## 10.2 Gated Tiny Live Follow-Up
- If and only if the deterministic sandbox shows clear frontier separation, execute a minimal paired pilot (e.g. 2 boundary worlds, ~48 live calls) on `gemma3:12b`.

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

