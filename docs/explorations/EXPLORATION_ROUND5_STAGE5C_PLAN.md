# Exploration Round 5 — Stage 5C Preregistered Experimental Plan
### *Neural Revision Bridge: End-to-End Evaluation of Support-First Belief Maintenance Under Live Model Reasoning*

**Document Version:** 1.0.0 (Preregistered Design Freeze)  
**Status:** Preregistered & Frozen Design  
**Evidence Class:** `live_neural_assay`  
**Target Model:** `gemma3:12b` (Ollama Local Inference, Temperature 0.0, Seed 42)  
**Preregistered Execution Budget:** **32 Total Live Model Calls** ($4 \text{ Acquisition} + 24 \text{ Factorial Revision} + 4 \text{ Replay Canaries}$)  

---

## 1. Scientific Motivation & Core Hypotheses

Stages 5A and 5B established the mathematical necessity of the **Support-First Epistemic Runtime**:
1. **Stage 5A:** Flattening alternative support paths causes **100% false retractions** on damaged-but-still-entitled states.
2. **Stage 5B:** The **lineage-projected minimal support hypergraph $\mathcal{S}_L(c)$** is the canonical normal form required to avoid representation collisions and satisfy all 7 formal governance axioms.

**Stage 5C (The Neural Revision Bridge)** closes the loop between deterministic theory and live neural generation:
> **Core Research Question:** *When upstream premises are retracted, does a neural reasoner governed by an Epistemic Kernel (which extracts minimal support $\mathcal{S}(c)$ and maintains lineage-projected resilience $\mathcal{S}_L(c)$) successfully resist false retractions and properly gate actions compared to ungrounded raw memory and naive reported-dependency tracking?*

### Formal Hypotheses:
1. **Hypothesis 1 (Raw Neural Confusion):** Without external support tracking, raw neural models exposed to multi-premise histories and partial invalidations will suffer from context pollution and fail to consistently distinguish degraded entitlement from complete retraction.
2. **Hypothesis 2 (Reported-Dependency Autoimmunity):** Storing self-reported citations $R(c)$ as durable flat dependency edges will cause catastrophic false retractions on degraded states whenever any cited premise is retracted, reproducing the 5A prediction on real neural justifications.
3. **Hypothesis 3 (Support-First Entitlement Invariance):** The GENE Support-First Runtime ($\mathcal{S}(c) \to \mathcal{S}_L(c)$) will achieve **100% active retention on degraded states** ($P(\text{active} \mid \text{DEGRADED}) = 1.0$) and **100% clean abstentions on severed states** ($P(\text{UNKNOWN} \mid \text{RETRACTED}) = 1.0$).
4. **Hypothesis 4 (Decoupled Governance Integrity):** The deterministic action gate will enforce $\text{Auth}(\mathcal{S}_L)$ independently of neural overconfidence, blocking unauthorized actions on degraded beliefs while permitting actions backed by robust lineage redundancy.

---

## 2. Experimental Architecture & Factorial Design

```
                               STAGE 5C THREE-ARM ASSAY PIPELINE
                               
                  +───────────────────────────────────────────────+
                  |  Phase 1: Acquisition (4 Structural Worlds)  |
                  |  Generate Initial Claim + Capture Neural R(c) |
                  +───────────────────────────────────────────────+
                                          │
                                          ▼
                  +───────────────────────────────────────────────+
                  |    Phase 2: Causal Invalidation do(x = 0)     |
                  |   Degraded (Ent* = 1) vs Retracted (Ent* = 0) |
                  +───────────────────────────────────────────────+
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
   [ Arm 1: Raw Neural ]       [ Arm 2: Naive Flat R(c) ]    [ Arm 3: GENE Support-First ]
   Prompt contains raw         Flat dependency union         Kernel validates S(c),
   history + invalidation      retracts claim if any         projects S_L(c), recomputes
   statement (No Kernel)       p in R(c) is invalidated      minimal context & gates Auth
```

### 2.1 The Four Structural Micro-Worlds
To ensure structural identifiability rather than lexical bias, four distinct topological boundary worlds are evaluated:
1. **World 1: Independent Alternatives (`W_IND`)**
   - Support: $\mathcal{S}(C) = \{\{A, B\}, \{D, E\}\}$
   - Lineage: $A, B \leftarrow R_1; D, E \leftarrow R_2$ (Two independent multi-premise paths).
2. **World 2: Shared-Premise Alternatives (`W_SHP`)**
   - Support: $\mathcal{S}(C) = \{\{A, B\}, \{A, D\}\}$
   - Lineage: $A \leftarrow R_1; B \leftarrow R_2; D \leftarrow R_3$ ($\kappa$-blindness boundary $(2, 1) \to (1, 1)$).
3. **World 3: Shared-Origin Ancestry (`W_SHO`)**
   - Support: $\mathcal{S}(C) = \{\{A, B\}, \{D, E\}\}$
   - Lineage: $A, D \leftarrow R_1; B, E \leftarrow R_2$ (Nominal multiplicity collapsing to $\mathcal{S}_L = \{\{R_1, R_2\}\}$).
4. **World 4: Recombinant Tri-Path (`W_REC`)**
   - Support: $\mathcal{S}(C) = \{\{A, B\}, \{B, C\}, \{C, D\}\}$
   - Lineage: $A \leftarrow R_1; B \leftarrow R_2; C \leftarrow R_3; D \leftarrow R_4$ (Complex multi-path recovery).

### 2.2 Causal Invalidation Conditions
For each world, two causal interventions are applied:
1. **Condition `DEGRADED` ($\text{Ent}^*(C) = 1$):** Invalidate a premise in one path while at least one alternative path remains completely intact.
2. **Condition `RETRACTED` ($\text{Ent}^*(C) = 0$):** Invalidate a cut-set of premises such that no entitling path survives.

---

## 3. The 32-Call Assay Matrix

```
+───────────────────────────────────────────────────────────────────────────────────────────────────+
│                                STAGE 5C CALL BUDGET & PROTOCOL                                    │
+───────────────┬────────────┬─────────────┬───────────┬──────────────┬─────────────────────────────+
│ Phase / Arm   │ Worlds (N) │ Inval (N)   │ Replay(N) │ Total Calls  │ Evaluation Objective        │
+───────────────┼────────────┼─────────────┼───────────┼──────────────┼─────────────────────────────+
│ 1. Acquisit.  │ 4          │ Baseline    │ 1         │ 4            │ Capture initial R(c) & S(c) │
│ 2. Arm 1 (Raw)│ 4          │ 2 (Deg/Ret) │ 1         │ 8            │ Raw neural revision         │
│ 3. Arm 2 (R)  │ 4          │ 2 (Deg/Ret) │ 1         │ 8            │ Naive dependency graph      │
│ 4. Arm 3 (GENE│ 4          │ 2 (Deg/Ret) │ 1         │ 8            │ Support-first kernel        │
│ 5. Replay Can.│ 2          │ 2           │ 1         │ 4            │ Replay determinism check    │
+───────────────┴────────────┴─────────────┴───────────┴──────────────┴─────────────────────────────+
│ TOTAL BUDGET  │            │             │           │ 32 Calls     │ Live Gemma 3:12B Executions │
+───────────────┴────────────┴─────────────┴───────────┴──────────────┴─────────────────────────────+
```

---

## 4. Quantitative Endpoints & Formal Semantics

### 4.1 Primary Endpoints:
1. **Degraded Entitlement Fidelity ($P(\text{active} \mid \text{DEGRADED})$):**
   - Proportion of degraded scenarios where the system maintains the contextually entitled claim.
   - Expected: $\text{Arm 1} \le 0.50$, $\text{Arm 2} = 0.00$ (100% false retractions), $\text{Arm 3} = 1.00$.
2. **Retraction Abstention Rate ($P(\text{UNKNOWN} \mid \text{RETRACTED})$):**
   - Proportion of retracted scenarios where the system emits a clean `UNKNOWN` abstention.
   - Expected: $\text{Arm 1} \le 0.70$ (risk of hallucinated pseudo-paths), $\text{Arm 2} = 1.00$, $\text{Arm 3} = 1.00$.

### 4.2 Governance Telemetry:
For every execution, the runtime records:
- $\text{Action}_{\text{proposed}}$: Neural reasoner's suggested operational action.
- $\text{Auth}(\mathcal{S}_L)$: Deterministic lineage-projected authority score $\in [0.0, 1.0]$.
- $\text{Verdict}_{\text{gate}}$: Gate decision (`PERMIT` if $\text{Auth} \ge \tau$, `BLOCK` otherwise).
- $\text{Disagreement}$: Whether neural confidence exceeded mathematical authority.
- $\text{Action}_{\text{final}}$: Actual executed outcome.

---

## 5. Execution Preflight & Promotion Gate

1. **Step 1: Deterministic Harness & Mocks:** Complete zero-compute test suite (`tests/explore_round5/test_neural_revision_bridge.py`) verifying prompt formats, schema compliance, and kernel state transitions.
2. **Step 2: Live Execution:** Execute the 32 calls sequentially with full SQLite logging (`calls`, `prompts`, `responses`, `kernel_evaluations`).
3. **Step 3: Verification & Freeze:** Compute artifact checksums, generate summary JSON and report markdown, and freeze `round5-stage5c-freeze`.
