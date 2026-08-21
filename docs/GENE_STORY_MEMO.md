# The GENE Scientific Story Memo
**A Unified Narrative of Error Inheritance, Retrieval Epidemiology, Selective Lineage Immunity, Support Algebra, and Action Governance in Persistent AI Memory**

**Document Version:** 2.0.0 (Support-First Epistemic Runtime & Round 5 Expansion)  
**Status:** Canonical Scientific Narrative  
**Authoritative Manifest:** [`data/canonical_results_manifest.json`](../data/canonical_results_manifest.json)  
**Core Reference Implementation:** [`src/gene/`](../src/gene/)  

---

## Executive Abstract

Modern AI systems increasingly rely on persistent memory to retain knowledge, context, and operational state across sessions and interactions. When an erroneous or poisoned premise enters persistent memory, how does it spread, and how can an agent maintain why it is entitled to believe a claim as the world changes?

Standard benchmarks treat memory errors as static retrieval failures or transient model hallucinations. In contrast, the **Genealogical Epistemic Network Experiments (GENE)** project treats persistent memory as an *evolutionary epistemic runtime*. Across fifteen experimental phases and five exploratory rounds, GENE systematically decomposes the lifecycle of memory, reasoning, revision, and action:
$$\text{Ancestral Root} \longrightarrow \text{Retrieval Path Assembly} \longrightarrow \text{Neural Reasoning} \longrightarrow \text{Support Minimization} \longrightarrow \text{Lineage Projection} \longrightarrow \text{Action Governance}$$

This memo synthesizes the **nine core discoveries** that define the project's canonical scientific contribution:
1. Exposure $\ne$ reported justification $\ne$ causal lineage (Experiment 0).
2. Globally false premises reproduce through locally valid deduction (Experiment 1A).
3. Retrieval availability ($X_{\text{path}}$) governs reproductive branching (Experiment 1B-B).
4. Lineage metadata enables selective delayed quarantine ($S = \text{TPR} - \text{FPR}$) across semantic drift (Experiment 1B-C1b).
5. Memory containment does not guarantee behavioral containment (Experiment 1B-C2a).
6. Structural proofreading prevents pseudo-path reasoning from entering the germline (Experiment 1B-C2b).
7. Neural reported justification exhibits 100% explanatory bloat ($E_S > 0$), and epistemic output decomposes into four independent conformance layers (Round 4).
8. Flattening alternative support hypergraphs $\mathcal{S}(c)$ causes 100% false retractions on damaged-but-still-entitled states under partial invalidation (Stage 5A).
9. The Principle of Intervention-Sufficiency: scalar cut-sets ($\kappa$), tuple signatures ($\rho$), and global root counts are lossy representations; action governance requires the lineage-projected minimal support hypergraph $\mathcal{S}_L(c)$ and root resilience $\rho_L(c)$ (Stage 5B).

```
                                  THE THREE-LAYER EPISTEMIC ARCHITECTURE
                                  
   +───────────────────────────────────+
   │   Ancestral Memory Pool (G_0)     │
   +───────────────────────────────────+
                     │
                     ▼
   ┌───────────────────────────────────┐  LAYER 1: Memory Governance (Lineage Immunity)
   │     Retriever / Lineage Filter    │  - Prunes discredited ancestry branches
   │      [ Controls X_path ]          │  - Eliminates inherited transmission (R_inherited -> 0)
   └───────────────────────────────────┘  - Delivers selective containment S = TPR - FPR
                     │
                     ▼ (Retrieved Prompt Context)
   ┌───────────────────────────────────┐
   │     Downstream Neural Reasoner    │  - Executes multi-hop deductive rules
   │       [ Stochastic Proposal ]     │  - Emits candidate answer + reported citation R(c)
   └───────────────────────────────────┘
                     │
                     ▼ (Candidate Claim + Cited Parent IDs)
   ┌───────────────────────────────────┐  LAYER 2: Support Minimizer & Proofreader
   │    Epistemic Conformance Kernel   │  - Extracts minimal entitling support S(c) from bloat R(c)
   │        [ Controls W_U ]           │  - Rejects underivable pseudo-paths (W_U = 0.000)
   └───────────────────────────────────┘
                     │
                     ▼ (Admitted if Structurally Warranted)
   ┌───────────────────────────────────┐  LAYER 3: Lineage-Projected Action Governance
   │     Governance Engine (S_L, rho_L)│  - Projects S(c) into root hypergraph S_L(c)
   │        [ Enforces 7 Axioms ]      │  - Gates high-stakes actions with mathematical proportionality
   └───────────────────────────────────┘
```

---

## 1. Discovery 1: Exposure Is Not Ancestry (Experiment 0)

Before studying how memory errors reproduce, the experimental instrument had to solve a foundational measurement problem: **What is a parent memory?**

In complex agent workflows, an information trace may appear in an agent's context window without influencing the output, or the agent may cite a plausible-looking fact that played no causal role in generating its answer. Experiment 0 established that informational ancestry cannot be collapsed into a single observable. GENE formally distinguishes three distinct ancestral relations:

1. **Exposure Lineage ($\mathcal{E}$)**: The set of memory nodes physically rendered into the prompt context.
2. **Reported-Support Lineage ($\mathcal{R}$)**: The set of memory IDs explicitly claimed by the model as its justification.
3. **Causal Lineage ($\mathcal{C}$)**: The set of memory nodes whose interventional ablation or counterfactual replacement strictly changes the emitted claim.

```
       EXPOSURE LINEAGE             REPORTED-SUPPORT LINEAGE             CAUSAL LINEAGE
   ┌───────────────────────┐        ┌───────────────────────┐       ┌───────────────────────┐
   │  All nodes physically │        │  Nodes cited in JSON  │       │  Nodes whose ablation │
   │   rendered in prompt  │        │  self-reported answer │       │  counterfactually     │
   │        context        │        │      certificate      │       │  changes the output   │
   └───────────────────────┘        └───────────────────────┘       └───────────────────────┘
               ▲                                ▲                               ▲
               │                                │                               │
               └────────────────────────────────┴───────────────────────────────┘
                                  P_reported ≠ P_causal
```

### Key Empirical Findings:
- Model self-citations are **not causal ground truth**. Under uncalibrated prompts, language models frequently exhibit *post-hoc citation confabulation*—citing exposed distractor nodes while ignoring causal parents, or deriving answers without citing required premises.
- Calibration requires an explicit **structured evidence contract** with a valid reject option (`UNKNOWN`).
- Across counterbalanced procedural micro-worlds, GENE achieved **100% causal lineage calibration** ($C_{\text{nec}} = 1.000, H_D = 0.000$ across 276 total matrix calls, with Cell 4 passing 66/66 causal intervention tests), establishing the deterministic baseline required to measure multi-generation transmission.

---

## 2. Discovery 2: Bad Reasoning Is Not Required for Falsehood Propagation (Experiment 1A)

The standard intuition regarding AI misinformation assumes that falsehoods spread primarily through repeated model hallucinations or degraded reasoning. Experiment 1A provides a controlled counterexample: **falsehood propagation does not require repeated reasoning failures**.

When a corrupted root fact (e.g. `Station VELORA operates under supervisor KIRA` $\to$ `TAL`) was seeded at Generation 0 ($G_0$), the model was tasked with executing multi-hop deduction across successive generations ($G_1, G_2$):
$$\text{False Supervisor } (G_0) \xrightarrow[\text{Rule 1}]{} \text{False Protocol / Clearance } (G_1) \xrightarrow[\text{Rule 2}]{} \text{False Route / Access Tier } (G_2)$$

To evaluate this dynamic, GENE introduced the **Dual-Oracle Framework**, evaluating every emitted claim simultaneously against two independent oracles:
- **Canonical Oracle ($T^* \in \{0, 1, \emptyset\}$)**: Evaluates truth relative to the machine-readable ground-truth world closure ($W^*$).
- **Context Derivability Oracle ($D_{\text{ctx}} \in \{0, 1\}$)**: Evaluates whether the claim is strictly derivable from the prompt context exposed to the model.

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    THE DUAL-ORACLE EVALUATION MATRIX                                    |
+-------------------+-------------------+-------------------+---------------------------------------------+
| Canonical (T*)    | Context (D_ctx)   | Phenotype         | Epistemic Meaning                           |
+-------------------+-------------------+-------------------+---------------------------------------------+
| 1 (True in W*)    | 1 (Derivable)     | Healthy           | Globally and locally true                   |
| 0 (False in W*)   | 1 (Derivable)     | Semantic Infection| Globally false, but locally sound deduction |
| 1 (True in W*)    | 0 (Underivable)   | Epistemic Error   | Locally unwarranted lucky guess / pseudo-path|
| 0 (False in W*)   | 0 (Underivable)   | De Novo Error     | Locally unwarranted false assertion         |
| ∅ (N/A)           | 0 (Underivable)   | Clean Abstention  | Warranted UNKNOWN response                  |
+-------------------+-------------------+-------------------+---------------------------------------------+
```

### Key Empirical Findings:
- **Semantic Infection**: Corrupted lineages achieved **100% transmission fidelity** ($\tau = 1.000$) across $G_0 \to G_1 \to G_2$ while maintaining state vector $(0, 1, 1, 1, 1)$ across 72 evaluations.
- At every single generational step, the model's local reasoning was **100% logically valid and derivationally sound** ($D_{\text{ctx}} = 1, A = 1, E = 1, K = 1$).
- **Core Principle**: *A false memory does not require bad reasoning to spread. Correct local deduction faithfully reproduces and transforms globally false ancestry.*

---

## 3. Discovery 3: Retrieval Regulates Reproductive Contact (Experiment 1B-A & 1B-B)

In realistic agent systems, memories do not automatically enter context; they must be retrieved from a shared pool. Experiment 1B separated *memory existence* from *reproductive exposure*.

Multi-hop deductive tasks require the concurrent retrieval of multiple independent premises (e.g. Premise $A$ + Premise $B$). If retrieval returns only Premise $A$ alongside irrelevant clutter, the deductive path is broken.

GENE formulated the **Retrieval-Path Availability** metric:
\[
X_{\text{path}} = P(\text{Premise } A \in \text{Context} \land \text{Premise } B \in \text{Context})
\]

```
                          RETRIEVAL AS REPRODUCTIVE CONTACT
                          
   [ Memory Store ] ──► [ Lexical Retriever (top-k) ] ──► Context: { Premise A, Clutter 1, Clutter 2 }
                                                                 │
                                                                 ▼
                                                    Path is BROKEN (Premise B missing)
                                                                 │
                                                                 ▼
                                                    Model Abstains: UNKNOWN (R = 0)
```

### Key Empirical Findings:
- **Branching Dynamics & Extinction Threshold**: In a branching process model with capacity $b=2$, offspring generating function $G(s) = ((1-p) + ps)^2$ yields ultimate extinction probability $q_\infty(p) = ((1-p)/p)^2$ for $p > 0.50$. When path availability drops to or below $X_{\text{crit}} = 1/b = 0.50$, **extinction occurs almost surely in the limit** ($q_\infty = 1.000$).
- **Causal Retrieval Rescue**: Increasing the retrieval budget from $k=4$ to $k=6$ restored complete $G_1$ path assembly from 0/4 to 4/4 in both arms and restored downstream expression; a clean/infected expression asymmetry then motivated the matched B1c control.
- **Matched Expression Assay (Exp 1B-B1c)**: Across 16 counterbalanced live calls, model expression was strictly path-conditioned:
  \[
  P(\text{active} \mid \text{complete path}) = \frac{8}{8} = 1.000, \quad P(\text{active} \mid \text{broken path}) = \frac{0}{8} = 0.000
  \]

---

## 4. Discovery 4: Lineage Enables Selective Delayed Quarantine (Experiment 1B-C1b)

In real-world deployments, an information source is rarely identified as malicious or inaccurate at the moment of creation. Discrediting judgments arrive **late**—after the root fact has already reproduced into multiple downstream generations.

In Experiment 1B-C1b, GENE evaluated a shared memory pool where healthy ($H$) and infected ($I$) lineages coexisted across 12 fully counterbalanced, role-swapped ecologies (1,200 evaluations across a full budget sweep). An external detector supplied an imperfect binary risk signal $S \in \{0, 1\}$ at the root with True Positive Rate ($\text{TPR}$) and False Positive Rate ($\text{FPR}$).

```
                             LINEAGE QUARANTINE VS. NODE-ONLY FILTERING
                             
     ROOT CORRUPTED (G_0) [Flagged by Risk Signal]
              │
              ├──────────────────────────────────┐
              ▼                                  ▼
     [ NODE-ONLY FILTER ]             [ LINEAGE QUARANTINE ]
     Removes G_0 root only.            Removes G_0 + G_1 + G_2 descendants.
              │                                  │
              ▼                                  ▼
     G_1 & G_2 Survives in Memory!     Corrupted Family Quarantined!
              │                                  │
              ▼                                  ▼
     PROVENANCE LAUNDERING (C_I = 1.0) SELECTIVE CONTAINMENT (C_I = 1 - TPR)
```

### Key Empirical Findings:
1. **The Lineage-Blind Baseline Law**:
   All lineage-blind interventions (uniform thinning, random-family quarantine, generation-targeted pruning) fall strictly on the diagonal:
   \[
   C_H = C_I \implies \text{Selectivity } S = C_H - C_I \equiv 0.000
   \]
   Lineage-blind forgetting cannot reduce corrupted availability without destroying healthy knowledge at the exact same rate ($C_H = C_I = 0.7177$ for uniform thinning at $k=6$).
2. **Provenance Laundering Under Node-Only Filtering**:
   Removing only the flagged root node yielded **100% descendant survival** ($C_I \equiv 1.000, S \equiv 0.000$). Downstream generations successfully laundered away their disreputable origin.
3. **The Golden Identity of Selective Lineage Immunity**:
   Lineage quarantine leverages ancestry edges to propagate the root judgment downstream, achieving:
   \[
   C_H = 1 - \text{FPR}, \quad C_I = 1 - \text{TPR} \implies S = \text{TPR} - \text{FPR}
   \]
   At a 90% TPR / 10% FPR operating point, lineage quarantine delivered an **80.0% selective containment advantage** ($S = +0.800$) over the control frontier.
4. **Core Principle**: *Genealogy does not detect truth. Genealogy preserves the address of a trust judgment through semantic transformation.*

---

## 5. Discovery 5: Memory Containment Is Insufficient for Behavioral Containment (Experiment 1B-C2 & C2a)

When the retrieval sandbox was connected to live neural generation on `gemma3:12b` (50 calls in Experiment 1B-C2a), a critical gap emerged:

Under complete double quarantine (where all route facts were removed, $X_{\text{path}} = 0$), the model abstained as expected in the forward ecology, but in the role-swapped ecology, it manufactured **unsupported concrete claims** from surviving memory fragments.

```
                    THE BEHAVIORAL PSEUDO-PATH GAP
                    
   Memory Pool: { Station KESTREL is in Facility Grid 1 }  (Route memory QUARANTINED)
   Rule: If Station operates on Route X AND Grid 1 -> Auth Code Alpha
                               │
                               ▼
                    [ Gemma 3:12B Reasoner ]
                               │
                               ▼
   Output: "AUTH_ALPHA_KESTREL" (Sufficient Evidence)  ◄── UNSUPPORTED PSEUDO-PATH!
```

### Key Empirical Discoveries:
1. **The Memory-Behavior Gap**:
   - Memory Governance (Layer 1) successfully removed legitimate derivation paths ($X_{\text{path}} = 0$).
   - However, **Behavioral Containment** failed in 2/4 executions under initial testing and produced 9/10 epistemic errors on repeated prompt tests.
   - **Conclusion**: *Memory containment alone was insufficient for behavioral containment in the tested ecology.*
2. **The Replay Stability Principle**:
   - Replaying the identical frozen prompt 10 times under temperature 0.0 and fixed seed 42 on local GPU inference yielded **9 active epistemic errors and 1 contract-failure abstention**.
   - **Principle**: *Fixed prompt + temperature 0 + fixed seed cannot be assumed deterministic without empirical verification on that execution runtime.*

---

## 6. Discovery 6: Structural Proofreading Prevents Phenotypic Errors from Becoming Heritable (Experiment 1B-C2b)

Experiment 1B-C2b was designed to map the exact trigger surface of pseudo-path formation and evaluate a mechanical **Layer 2 Structural Epistemic Proofreader** (Support-Certificate Validator).

Across 30 live invocations on Gemma 3:12B testing 5 factorial conditions across forward and swapped ecologies:
1. **Mismatched Routes Elicit Clean Abstention ($12 / 12 = 1.000$)**:
   When an explicit mismatching route was visible in context, the model recognized that the rule antecedent was not satisfied and produced **12 / 12 observed clean abstentions**.
2. **Zero-Route Contexts Induce Single-Premise Jumping ($6 / 6 = 1.000$)**:
   When route facts were completely absent, the model jumped from the single facility grid premise to the rule conclusion across both ecologies ($6 / 6$ active errors).
3. **Foreign Exact-Route Matches Elicit Asymmetric Cross-Binding**:
   When a foreign station carried the target's required route, it triggered cross-entity variable binding in the swapped configuration ($3 / 3$ errors) while the forward configuration produced $3 / 3$ clean abstentions.

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    LAYER 2 PROOFREADING AUDIT (30 CALLS)                                |
+------------------------------+----+--------------------+--------------------+---------------------------+
| Condition                    | N  | Raw Model Behavior | Layer 2 Verdict    | Admitted to Memory?       |
+------------------------------+----+--------------------+--------------------+---------------------------+
| valid_target_route (Ctrl)    | 6  | 6/6 Active Valid   | PASS_VALID_DERIV   | YES (6/6 Admitted)        |
| target_station_wrong_route   | 6  | 6/6 UNKNOWN        | PASS_ABSTENTION    | NO  (6/6 Inactive)        |
| foreign_station_wrong_route  | 6  | 6/6 UNKNOWN        | PASS_ABSTENTION    | NO  (6/6 Inactive)        |
| foreign_station_target_route | 6  | 3 Active, 3 UNK    | 3 REJECT, 3 PASS   | NO  (0/6 Admitted)        |
| no_route                     | 6  | 6/6 Active Errors  | 6/6 REJECT_UNIF    | NO  (0/6 Admitted)        |
+------------------------------+----+--------------------+--------------------+---------------------------+
```

### The Structural Support-Certificate Validator:
Layer 2 performs first-order triple unification over the cited parent facts:
\[
\sigma = \{?s \mapsto \text{target\_station}\} \quad \text{such that} \quad \forall (p, o) \in \text{Rule.Antecedents}, \quad (\text{target\_station}, p, o) \in \text{CitedFacts}
\]

### Evolutionary Transmission Dynamics:
GENE decomposes population transmission into two distinct channels:
1. **Inherited Transmission Channel**:
   \[
   R_{\text{inherited}} \approx b \cdot X_{\text{path}} \cdot \tau_S \cdot W_S
   \]
2. **Spontaneous / Underivable Channel**:
   \[
   \mu_U = P(\text{unsupported output emitted} \mid D_{\text{ctx}} = 0) = \frac{9}{24} = \mathbf{0.375}
   \]
   \[
   \mu_{U, \text{heritable}} = \mu_U \cdot W_U = 0.375 \times 0.000 = \mathbf{0.000}
   \]
3. **Total Population Evolution**:
   \[
   \mathbb{E}[I_{g+1}] \approx R_{\text{inherited}} \cdot I_g + \Lambda_{\text{de\_novo}, g}
   \]

Layer 1 controls $X_{\text{path}} \to 0$ (quarantining inherited falsehoods), and Layer 2 controls $W_U \to 0$ (preventing pseudo-path admission).

---

## 7. Discovery 7: The Four-Layer Epistemic Conformance Taxonomy & Explanatory Bloat (Round 4)

In Exploration Round 4, GENE connected live neural models (Gemma 3:12B) to complex multi-path support environments. The audit revealed that neural self-reported justification $R(c)$ is fundamentally unfaithful to minimal entitling support $\mathcal{S}(c)$.

Epistemic outputs decompose into four independent layers:
$$\text{Symbol Realization} \ne \text{Contract Coherence} \ne \text{Justification Precision} \ne \text{Formal Derivability}$$

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
│                                 FOUR-LAYER CONFORMANCE TAXONOMY (ROUND 4)                               │
+──────────────────────────┬─────────────────────────────────────────────────────────────┬────────────────+
│ Conformance Layer        │ Failure Surface Modeled                                     │ Observed Rate  │
+──────────────────────────┼─────────────────────────────────────────────────────────────┼────────────────+
│ 1. Symbol Realization    │ Token-level formatting drift (e.g. PROTOCOL_X7 vs PROTO_X7) │ 6 / 24 (25.0%) │
│ 2. Contract Coherence    │ Semantic contradiction across JSON fields (det vs N=null)   │ 5 / 24 (20.8%) │
│ 3. Justification Precise │ Explanatory bloat (citing irrelevant distractors E_S > 0)    │ 24/24 (100.0%) │
│ 4. Formal Derivability   │ Deriving concrete answers from empty/broken support         │ 0.300 - 0.375  │
+──────────────────────────┴─────────────────────────────────────────────────────────────┴────────────────+
```

---

## 8. Discovery 8: Loss of Support Algebra Causes 100% Revision Autoimmunity (Stage 5A)

In Stage 5A, GENE evaluated how persistent memory systems update beliefs when an upstream premise is retracted (`WHAT_IF(c, a)`).

When a claim is supported by alternative disjunctive paths (e.g. $\mathcal{S}(C) = \{\{A,B\}, \{D,E\}\}$), invalidating premise $D$ leaves the claim damaged but still entitled via surviving path $\{A,B\}$:
$$\text{Ent}^*(C, \{D\}) = \mathbf{1}[\{A,B\} \cap \{D\} = \emptyset] \lor \mathbf{1}[\{D,E\} \cap \{D\} = \emptyset] = 1 \lor 0 = 1$$

Across 368 factorial revision scenarios:
- **Flat Dependency Unions ($R_{\text{union}} = \{A,B,D,E\}$)** falsely retracted **100% of damaged-but-entitled states (104/104)**, destroying beliefs that retained valid alternative support.
- **Single-Witness Tracking ($R_{\text{single}} = \{D,E\}$)** falsely retracted **57.7% of damaged states (60/104)**.
- **Explanatory Bloat ($E_S > 0$)** caused **50% false retractions (8/16)** on completely untouched states when an irrelevant distractor was retracted.
- **Support-First Epistemic Kernel ($\mathcal{S}(c)$)** achieved **100% exact revision accuracy** with **0% autoimmunity**.

---

## 9. Discovery 9: Intervention-Sufficient Representation & Lineage-Projected Action Governance (Stage 5B)

In Stage 5B, GENE investigated: *What information about surviving support is minimally necessary to govern action authority under change?*

The benchmark proved that all existing scalar and tuple summaries suffer from **lossy representation collisions**:
1. **Binary Entitlement ($\text{Auth} \in \{0, 1\}$)** is blind to degradation, granting 100% full authority ($1.000$) to damaged beliefs.
2. **Scalar Cut-Set Resilience ($\kappa$)** fails on shared-root degradation ($(2,1) \to (1,1)$), granting full authority ($1.000$) even when an entire alternative path is destroyed.
3. **Tuple Resilience ($\rho = (|S|, \kappa)$)** fails to distinguish correlated single-root alternative paths from independent multi-root paths.
4. **Global Root Counts ($|\text{Roots}|$)** fail in shared origin ancestry ($A,D \leftarrow R_1, B,E \leftarrow R_2$): global counting sees 2 roots and 2 paths, but both paths share conjunctive root vulnerability.

**The Resolution:** Projecting premise support into root-lineage space yields the **lineage-projected minimal support hypergraph**:
$$\mathcal{S}_L(c) = \min_{\subseteq} \{ \{ \mathcal{L}(p) : p \in S_i \} : S_i \in \mathcal{S}(c) \}$$
Lineage-projected resilience $\rho_L(c) = (|\mathcal{S}_L(c)|, \kappa_L(c))$ resolves all collisions and achieves **100% compliance across 7 formal governance axioms**.

---

## 10. Positioning in 2026 Literature & The Lineage Integrity Boundary

### 10.1 Contemporary Literature Matrix

| Research Area | Recent Key Works (2025–2026) | Existing Focus | GENE's Distinct Contribution |
| :--- | :--- | :--- | :--- |
| **Persistent Memory Poisoning** | *Hidden in Memory*, *Remembering More, Risking More*, *Memory Contagion* | Measures attack success rates and downstream task degradation over long sessions. | Analytically decomposes transmission into exact constituent probabilities ($R_{\text{inherited}}$ and $\mu_U$), separating local deductive validity from global truth. |
| **Provenance-Aware Memory** | *MemLineage*, *MAP-Graph*, *PPMF* | Attaches derivation DAGs and graphs for governance and access control. | Proves the theoretical limits of memory governance, showing that lineage quarantine achieves $S = \text{TPR} - \text{FPR}$ while exposing the pseudo-path reasoning gap. |
| **Write-Time Defense & Origin Binding** | *ConsistencyGate*, *MemGuard*, *Louck's Origin-Binding Analysis* | Gating candidate memories via model self-reflection or typed boundaries. | Formally operationalizes write defense as an evolutionary filter ($W_U$) that reduces heritable corruption ($\mu_{U, \text{heritable}} = 0$) via first-order certificate unification. |
| **Epistemic Runtime & Support Maintenance** | *GENE (2026)* | Support-first belief revision, lineage-projected minimal hypergraphs, and action governance under change. | Solves revision autoimmunity via minimal support sets $\mathcal{S}(c)$ and establishes the Principle of Intervention-Sufficiency for persistent agent runtime governance. |

### 10.2 The Lineage Integrity Assumption
GENE currently evaluates what lineage can achieve under the assumption that ancestry metadata is faithfully recorded by the experimental substrate. It does not yet claim that real-world multi-agent systems maintain trustworthy provenance under adversarial lineage forgery or lossy recursive summarization. Measuring provenance degradation over deep lineages ($G_5+$) defines the primary objective of future work.

---

## 11. Summary Table of Primary Empirical Results

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
│                                    GENE CANONICAL EXPERIMENTAL SUMMARY                                  │
+────────────+──────+─────────────────────────────────────────+──────────────+────────────+───────────────+
│ Experiment │ N    │ Primary Quantitative Endpoint           │ Metric Value │ Baseline   │ Status        │
+────────────+──────+─────────────────────────────────────────+──────────────+────────────+───────────────+
│ Exp 0-B    │ 276  │ 2x2 Factorial Causal Necessity (Cell 4) │ 66/66 (100%) │ Uncalib.   │ FROZEN        │
│ Exp 1A     │ 72   │ Multi-Generation Semantic Transmission  │ 100.0% (τ=1) │ N/A        │ FROZEN        │
│ Exp 1B-B1c │ 16   │ Path-Conditioned Expression Symmetry    │ 1.000 / 0.000│ N/A        │ FROZEN        │
│ Exp 1B-C1b │ 1200 │ Lineage Quarantine Selectivity (90/10)  │ S = +0.800   │ Blind: 0.0 │ FROZEN        │
│ Exp 1B-C2a │ 50   │ Live Lineage Containment vs Laundering  │ 100% vs 0%   │ Node: 0%   │ FROZEN        │
│ Exp 1B-C2b │ 30   │ Structural Proofreader Heritable Rate   │ μ_herit = 0.0│ μ_U = 0.375│ FROZEN        │
│ Round 4    │ 116  │ Four-Layer Conformance & Bloat Assay    │ E_S > 0: 100%│ Zero Bloat │ FROZEN        │
│ Stage 5A   │ 432  │ Revision Precision & Support Algebra    │ Degraded: 0% │ Flat: 100% │ FROZEN        │
│ Stage 5B   │ 368  │ Lineage-Projected Action Governance     │ 7/7 Axioms   │ Rho: 6/7   │ FROZEN        │
+────────────+──────+─────────────────────────────────────────+──────────────+────────────+───────────────+
```

---

## 12. Conclusion & Horizon

GENE demonstrates that persistent AI memory requires an **epistemic runtime for maintaining entitlement under change**. By maintaining minimal entitling support $\mathcal{S}(c)$ and lineage-projected hypergraphs $\mathcal{S}_L(c)$, persistent agents can perform non-destructive belief revision, avoid explanatory bloat autoimmunity, and govern high-stakes actions with mathematical proportionality.
