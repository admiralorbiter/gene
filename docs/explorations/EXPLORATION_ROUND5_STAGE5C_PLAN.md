# Exploration Round 5 — Stage 5C Preregistered Experimental Plan
### *Neural Revision Bridge: End-to-End Evaluation of Support-First Belief Maintenance Under Live Model Reasoning*

**Document Version:** 2.0.0 (Execution Freeze & Complete Assay Manifest)  
**Status:** Preregistered Execution Freeze  
**Evidence Class:** `live_neural_assay`  
**Target Model:** `gemma3:12b` (Ollama Local Inference, Temperature 0.0, Seed 42, Digest: `f4031aab...`)  
**Preregistered Execution Budget:** **32 Total Live Model Calls** ($4 \text{ Acquisition} + 24 \text{ Factorial Revision} + 4 \text{ Replay Canaries}$)  
**Machine-Readable Execution Manifest:** [`data/exploration_round5_stage5c_manifest.json`](../../data/exploration_round5_stage5c_manifest.json)  

---

## 1. Scientific Motivation & Core Hypotheses

Stages 5A and 5B established the mathematical necessity of the **Support-First Epistemic Runtime**:
1. **Stage 5A:** Flattening alternative support paths causes **100% false retractions** on damaged-but-still-entitled states.
2. **Stage 5B:** The **lineage-projected minimal support hypergraph $\mathcal{S}_L(c)$** is the canonical normal form required to avoid representation collisions and satisfy all 7 formal governance axioms.

**Stage 5C (The Neural Revision Bridge)** closes the loop between deterministic theory and live neural generation:
> **Core Research Question:** *When upstream premises are retracted, does a neural reasoner governed by an Epistemic Kernel (which performs support enumeration over active rules and maintains lineage-projected resilience $\mathcal{S}_L(c)$) successfully resist false retractions and properly gate actions compared to ungrounded raw memory and naive reported-dependency tracking?*

### 1.1 Key Conceptual Clarification: Support Minimization vs Support Enumeration
- **Support Minimization** reduces a known support family or bloated citation to irredundant subsets.
- **Support Enumeration / Completion** discovers all valid minimal proof environments $\mathcal{S}_F(c)$ from active world premises and inference rules.
- In Arm 3, the Epistemic Kernel constructs the full entitling family $\mathcal{S}_F(c)$ via first-order backward-chaining enumeration, then applies antichain minimization $\mathcal{S}_L(c) = \min_{\subseteq} \{\{\mathcal{L}(p) : p \in S_i\}\}$.
- The neural model's observed citation $R(c)$ is recorded as an empirical audit artifact (and drives Arm 2), but does **not** unilaterally limit the kernel's support family.

### 1.2 Formal Hypotheses:
1. **Hypothesis 1 (Raw Neural Confusion):** Without external support tracking, raw neural models exposed to multi-premise histories and partial invalidations will suffer from context pollution and fail to consistently distinguish degraded entitlement from complete retraction.
2. **Hypothesis 2 (Reported-Dependency Autoimmunity):** The Naïve Reported-Dependency arm will trigger false retractions on degraded states whenever the model's actual Phase 1 acquisition citation $R(c)$ overlaps the invalidated premise set $I$:
   $$\text{NaiveRetract}(c, I) = \mathbf{1}[R(c) \cap I \ne \emptyset]$$
   This empirically measures how often real neural explanatory bloat produces the revision error predicted by Stage 5A.
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
   Prompt contains raw         Flat dependency union         Kernel enumerates S_F(c),
   history + invalidation      retracts claim if any         projects S_L(c), recomputes
   statement (No Kernel)       p in R(c) is invalidated      minimal context & gates Auth
```

### 2.1 The Four Structural Micro-Worlds
1. **World 1: Independent Alternatives (`W_IND`)**
   - Query: Station `KESTREL` Operating Protocol $\to$ `PROTOCOL_OMEGA`.
   - Paths: $\mathcal{S}(C) = \{\{\text{Fact\_A}, \text{Fact\_B}\}, \{\text{Fact\_D}, \text{Fact\_E}\}\}$.
   - Lineage: $\text{Fact\_A}, \text{Fact\_B} \leftarrow R_1; \text{Fact\_D}, \text{Fact\_E} \leftarrow R_2$.
   - Interventions: `DEGRADED` ($I = \{\text{Fact\_D}\}$); `RETRACTED` ($I = \{\text{Fact\_A}, \text{Fact\_D}\}$).
2. **World 2: Shared-Premise Alternatives (`W_SHP`)**
   - Query: Station `ORION` Clearance Tier $\to$ `TIER_SIGMA`.
   - Paths: $\mathcal{S}(C) = \{\{\text{Fact\_A}, \text{Fact\_B}\}, \{\text{Fact\_A}, \text{Fact\_D}\}\}$.
   - Lineage: $\text{Fact\_A} \leftarrow R_1; \text{Fact\_B} \leftarrow R_2; \text{Fact\_D} \leftarrow R_3$.
   - Interventions: `DEGRADED` ($I = \{\text{Fact\_B}\}$); `RETRACTED` ($I = \{\text{Fact\_A}\}$).
3. **World 3: Shared-Origin Ancestry (`W_SHO`)**
   - Query: Station `VANGUARD` Access Code $\to$ `CODE_EPSILON`.
   - Paths: $\mathcal{S}(C) = \{\{\text{Fact\_A}, \text{Fact\_B}\}, \{\text{Fact\_D}, \text{Fact\_E}\}\}$.
   - Lineage: $\text{Fact\_A}, \text{Fact\_D} \leftarrow R_1; \text{Fact\_B}, \text{Fact\_E} \leftarrow R_2$ ($\mathcal{S}_L = \{\{R_1, R_2\}\}$).
   - Interventions: `DEGRADED` ($I = \{\text{Fact\_D}\}$); `RETRACTED` ($I = \{\text{Fact\_A}, \text{Fact\_D}\}$).
4. **World 4: Recombinant Tri-Path (`W_REC`)**
   - Query: Station `DRAKE` Transit Lane $\to$ `LANE_THETA`.
   - Paths: $\mathcal{S}(C) = \{\{\text{Fact\_A}, \text{Fact\_B}\}, \{\text{Fact\_B}, \text{Fact\_C}\}, \{\text{Fact\_C}, \text{Fact\_D}\}\}$.
   - Lineage: $\text{Fact\_A} \leftarrow R_1; \text{Fact\_B} \leftarrow R_2; \text{Fact\_C} \leftarrow R_3; \text{Fact\_D} \leftarrow R_4$.
   - Interventions: `DEGRADED` ($I = \{\text{Fact\_A}, \text{Fact\_B}\}$); `RETRACTED` ($I = \{\text{Fact\_B}, \text{Fact\_C}\}$).

---

## 3. Matched Serialization Grammar & Control Rules

To prevent confounding prompt style with epistemic reasoning, all prompts follow a frozen matched serialization grammar:
- **Evidence Header:** Fixed JSON-compatible markdown block containing `[FACT_ID]: <content>`.
- **Rule Definitions:** Formally identical Horn-clause rule representations across all arms.
- **Output Contract:** Valid JSON matching schema:
  ```json
  {
    "status": "DETERMINABLE" | "INDETERMINABLE",
    "answer": "<STRING>" | null,
    "cited_facts": ["<FACT_ID>", ...],
    "proposed_action": "<ACTION_NAME>" | null,
    "action_confidence": "<FLOAT 0.0 - 1.0>"
  }
  ```
- **Arm-Specific Controls:**
  - *Arm 1 (Raw Neural):* Full historical evidence list + explicit invalidation notice: `"[SYSTEM ALERT]: The following facts have been retracted: <FACT_IDS>"`.
  - *Arm 2 (Naïve Reported):* Automatically computes `NaiveRetract` over Phase 1 $R(c)$.
  - *Arm 3 (GENE Kernel):* Context contains only the surviving minimal support $\mathcal{S}'(c)$. Kernel evaluates $\text{Auth}(\mathcal{S}_L')$ and gates `proposed_action`.

---

## 4. The 32-Call Factorial Assay Matrix

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

## 5. Quantitative Endpoints & Formal Semantics

### 5.1 Primary Endpoints:
1. **Degraded Entitlement Fidelity ($P(\text{active} \mid \text{DEGRADED})$):**
   - Proportion of degraded scenarios where the system maintains the contextually entitled claim.
2. **Retraction Abstention Rate ($P(\text{UNKNOWN} \mid \text{RETRACTED})$):**
   - Proportion of retracted scenarios where the system emits a clean `UNKNOWN` abstention.
3. **Naïve Invalidation Correlation:**
   - Empirical match between Stage 5A theoretical prediction and real live $R(c)$ overlap.

### 5.2 Governance Telemetry:
For every execution, the runtime records:
- $\text{Action}_{\text{proposed}}$: Neural reasoner's suggested operational action.
- $\text{Auth}(\mathcal{S}_L)$: Deterministic lineage-projected authority score $\in [0.0, 1.0]$.
- $\text{Verdict}_{\text{gate}}$: Gate decision (`PERMIT` if $\text{Auth} \ge \tau$, `BLOCK` otherwise).
- $\text{Disagreement}$: Whether neural confidence exceeded mathematical authority.
- $\text{Action}_{\text{final}}$: Actual executed outcome.
