# The GENE Scientific Story Memo
**A Unified Narrative of Error Inheritance, Retrieval Epidemiology, Selective Lineage Immunity, and Structural Proofreading in Persistent LLM Memory**

**Document Version:** 1.0 (Canonical Post-Phase 10.5 Release)  
**Status:** Canonical Scientific Narrative  
**Authoritative Manifest:** [`data/canonical_results_manifest.json`](../data/canonical_results_manifest.json)  
**Core Reference Implementation:** [`src/gene/`](../src/gene/)  

---

## Executive Abstract

Modern AI systems increasingly rely on persistent memory to retain knowledge, context, and operational state across sessions and interactions. When an erroneous or poisoned premise enters persistent memory, how does it spread?

Standard benchmarks treat memory errors as static retrieval failures or transient model hallucinations. In contrast, the **Genealogical Epistemic Network Experiments (GENE)** project treats persistent memory as an *evolutionary transmission ecology*. Over ten experimental phases, GENE systematically decomposes the lifecycle of a memory mutation:
$$\text{Ancestral Root} \longrightarrow \text{Retrieval Path Assembly} \longrightarrow \text{Local Reasoning} \longrightarrow \text{Lineage Governance} \longrightarrow \text{Write-Time Admission}$$

This memo synthesizes the **six core discoveries** that define the project's canonical scientific contribution, showing how globally false premises reproduce through locally valid deduction, how lineage metadata enables delayed selective quarantine, why memory governance alone fails to guarantee behavioral containment, and how structural proofreading prevents transient reasoning errors from entering the persistent memory germline.

```
                                  THE TWO-LAYER EPISTEMIC ARCHITECTURE
                                  
   +───────────────────────────────────+
   │   Ancestral Memory Pool (G_0)     │
   +───────────────────────────────────+
                     │
                     ▼
   ┌───────────────────────────────────┐  LAYER 1: Memory Governance (Lineage Immunity)
   │     Retriever / Lineage Filter    │  - Prunes discredited ancestry branches
   │      [ Controls X_path ]          │  - Breaks lineage-blind C_H = C_I symmetry
   └───────────────────────────────────┘  - Delivers selective containment S = TPR - FPR
                     │
                     ▼ (Retrieved Prompt Context)
   ┌───────────────────────────────────┐
   │     Downstream Neural Reasoner    │  - Executes multi-hop deductive rules
   │       [ Local Deductive Step ]    │  - May manufacture unsupported pseudo-paths
   └───────────────────────────────────┘
                     │
                     ▼ (Candidate Claim + Cited Parent IDs)
   ┌───────────────────────────────────┐  LAYER 2: Structural Epistemic Proofreader
   │    Support-Certificate Validator  │  - First-order rule antecedent unification
   │     [ Controls W_proofread ]      │  - Rejects cross-binding & single-premise jumps
   └───────────────────────────────────┘
                     │
                     ▼ (Admitted if Structurally Warranted)
   +───────────────────────────────────+
   │   Persistent Occurrence Node (G_3)│  - Transmission: R_bad ≈ b · X_path · τ · W_proofread
   +───────────────────────────────────+  - Result: μ_expression = 0.300 ──► μ_heritable = 0.000
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
- Across counterbalanced procedural micro-worlds, GENE achieved **100% causal lineage calibration** ($C_{\text{nec}} = 1.000, H_D = 0.000$), establishing the deterministic baseline required to measure multi-generation transmission.

---

## 2. Discovery 2: Bad Reasoning Is Not Required for Falsehood Propagation (Experiment 1A)

The standard intuition regarding AI misinformation assumes that falsehoods spread through repeated model hallucinations or degraded reasoning. Experiment 1A disproved this assumption.

When a corrupted root fact (e.g. `Station VELORA operates under supervisor KIRA` $\to$ `TAL`) was seeded at Generation 0 ($G_0$), the model was tasked with executing multi-hop deduction across successive generations ($G_1, G_2$):
$$\text{False Supervisor } (G_0) \xrightarrow[\text{Rule 1}]{} \text{False Protocol } (G_1) \xrightarrow[\text{Rule 2}]{} \text{False Clearance Code } (G_2)$$

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
- **Semantic Infection**: Corrupted lineages achieved **100% transmission fidelity** ($\tau = 1.000$) across $G_0 \to G_1 \to G_2$ while maintaining state vector $(0, 1, 1, 1, 1)$.
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
- **Epidemiological Branching Threshold**: Multi-generation transmission follows branching process dynamics:
  \[
  R_0 \approx b \cdot X_{\text{path}} \cdot \tau
  \]
  When retrieval clutter or competitive lexical surface area drops $X_{\text{path}}$ below the critical threshold $X_{\text{crit}} = 1/b$, the corrupted lineage goes deterministically extinct ($P(\text{extinction}) = 1.000$).
- **Causal Retrieval Rescue**: In a 48-call live assay on Gemma 3:12B, expanding the retrieval budget from $k=4$ ($X_{\text{path}} = 0$) to $k=6$ ($X_{\text{path}} = 1$) produced an instantaneous, 100% causal rescue from total extinction (`UNKNOWN`) to active phenotypic expression.
- **Matched Expression Assay (Exp 1B-B1c)**: Across 16 counterbalanced live calls, model expression was strictly path-conditioned:
  \[
  P(\text{active} \mid \text{complete path}) = \frac{8}{8} = 1.000, \quad P(\text{active} \mid \text{broken path}) = \frac{0}{8} = 0.000
  \]

---

## 4. Discovery 4: Lineage Enables Selective Delayed Quarantine (Experiment 1B-C1b)

In real-world deployments, an information source is rarely identified as malicious or inaccurate at the moment of creation. Discrediting judgments arrive **late**—after the root fact has already reproduced into multiple downstream generations.

In Experiment 1B-C1b, GENE evaluated a shared memory pool where healthy ($H$) and infected ($I$) lineages coexisted across 12 fully counterbalanced, role-swapped ecologies. An external detector supplied an imperfect binary risk signal $S \in \{0, 1\}$ at the root with True Positive Rate ($\text{TPR}$) and False Positive Rate ($\text{FPR}$).

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
   Lineage-blind forgetting cannot reduce corrupted availability without destroying healthy knowledge at the exact same rate.
2. **Provenance Laundering Under Node-Only Filtering**:
   Removing only the flagged root node yielded **100% descendant survival** ($C_I \equiv 1.000, S \equiv 0.000$). Downstream generations successfully laundered away their disreputable origin.
3. **The Golden Identity of Selective Lineage Immunity**:
   Lineage quarantine leverages ancestry edges to propagate the root judgment downstream, achieving:
   \[
   C_H = 1 - \text{FPR}, \quad C_I = 1 - \text{TPR} \implies S = \text{TPR} - \text{FPR}
   \]
   At a 90% TPR / 10% FPR operating point, lineage quarantine delivered an **80.0% selective containment advantage** ($\Delta_I = +0.800$) over the theoretical control frontier.
4. **Core Principle**: *Genealogy does not detect truth. Genealogy preserves the address of a trust judgment through semantic transformation.*

---

## 5. Discovery 5: Memory Containment Is Not Behavioral Containment (Experiment 1B-C2 & C2a)

When the retrieval sandbox was connected to live neural generation on `gemma3:12b` (50 calls in Experiment 1B-C2a), a surprising failure mode emerged:

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
   - Memory Governance (Layer 1) successfully removed legitimate derivation paths in 4/4 double-quarantine tasks.
   - However, **Behavioral Suppression** occurred in only 2/4 executions.
   - **Conclusion**: $X_{\text{path}} = 0 \centernot\implies P(\text{unsupported expression}) = 0$. Memory containment is a necessary but insufficient condition for behavioral safety.
2. **The Replay Stability Principle**:
   - Replaying the identical frozen prompt 10 times under temperature 0.0 and fixed seed 42 on local GPU inference yielded **9 active epistemic errors and 1 contract-failure abstention**.
   - **Methodological Law**: *Fixed prompt + temperature 0 + fixed seed cannot be assumed deterministic without empirical verification on that execution runtime.*

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
GENE establishes the formal distinction between phenotypic expression and germline heritability:
- **Phenotypic Expression Rate**:
  \[
  \mu_{\text{expression}} = P(\text{unsupported output emitted}) = \frac{9}{30} = \mathbf{0.300} \quad \left(\frac{9}{24} = \mathbf{0.375} \text{ on broken paths}\right)
  \]
- **Heritable Mutation Rate**:
  \[
  \mu_{\text{heritable}} = P(\text{unsupported output admitted to memory}) = \frac{0}{30} = \mathbf{0.000} \quad \left(\frac{0}{24} = \mathbf{0.000} \text{ on broken paths}\right)
  \]

The complete general transmission equation becomes:
\[
R_{\text{bad}} \approx b \cdot X_{\text{path}} \cdot \tau \cdot W_{\text{proofread}}
\]
Where Layer 1 governs $X_{\text{path}}$ and Layer 2 governs $W_{\text{proofread}}$.

---

## 7. Positioning in 2026 Literature & The Lineage Integrity Boundary

### 7.1 Contemporary Literature Matrix

| Research Area | Recent Key Works (2025–2026) | Existing Focus | GENE's Distinct Contribution |
| :--- | :--- | :--- | :--- |
| **Persistent Memory Poisoning** | *Hidden in Memory*, *Remembering More, Risking More*, *Memory Contagion* | Measures attack success rates and downstream task degradation over long sessions. | Analytically decomposes transmission into exact constituent probabilities ($R \approx b \cdot X_{\text{path}} \cdot \tau \cdot W$), separating local deductive validity from global truth. |
| **Provenance-Aware Memory** | *MemLineage*, *MAP-Graph*, *PPMF* | Attaches derivation DAGs and graphs for governance and access control. | Proves the theoretical limits of memory governance, showing that lineage quarantine achieves $S = \text{TPR} - \text{FPR}$ while exposing the pseudo-path reasoning gap. |
| **Write-Time Defense & Origin Binding** | *ConsistencyGate*, *MemGuard*, *Louck's Origin-Binding Analysis* | Gating candidate memories via model self-reflection or typed boundaries. | Formally operationalizes write defense as an evolutionary filter ($W_{\text{proofread}}$) that reduces heritable corruption ($\mu_{\text{heritable}} = 0$) via first-order certificate unification. |

### 7.2 The Lineage Integrity Assumption
GENE currently evaluates what lineage can achieve under the assumption that ancestry metadata is faithfully recorded by the experimental substrate. It does not yet claim that real-world multi-agent systems maintain trustworthy provenance under adversarial lineage forgery or lossy recursive summarization. Measuring provenance degradation over deep lineages ($G_5+$) defines the primary objective of future work.

---

## 8. Summary Table of Primary Empirical Results

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    GENE CANONICAL EXPERIMENTAL SUMMARY                                  |
+────────────+──────+─────────────────────────────────────────+──────────────+────────────+───────────────+
| Experiment | N    | Primary Quantitative Endpoint           | Metric Value | Baseline   | Status        |
+────────────+──────+─────────────────────────────────────────+──────────────+────────────+───────────────+
| Exp 0      | 48   | Causal Lineage Necessity / Sufficiency  | 100.0% / 0.0%| Uncalib.   | FROZEN        |
| Exp 1A     | 16   | Multi-Generation Semantic Transmission  | 100.0% (τ=1) | N/A        | FROZEN        |
| Exp 1B-B1c | 16   | Path-Conditioned Expression Symmetry    | 1.000 / 0.000| N/A        | FROZEN        |
| Exp 1B-C1b | 480  | Lineage Quarantine Selectivity (90/10)  | S = +0.800   | Blind: 0.0 | FROZEN        |
| Exp 1B-C2a | 50   | Live Lineage Containment vs Laundering  | 100% vs 0%   | Node: 0%   | FROZEN        |
| Exp 1B-C2b | 30   | Structural Proofreader Heritable Rate   | μ_herit = 0.0| μ_expr=0.30| FROZEN        |
+────────────+──────+─────────────────────────────────────────+──────────────+────────────+───────────────+
```

---

## 9. Conclusion & Horizon

GENE demonstrates that persistent LLM memory systems can be understood and governed as evolutionary ecologies. By combining **Layer 1 Memory Governance** (which prunes reproductive lineage paths based on delayed risk signals) with **Layer 2 Structural Epistemic Proofreading** (which verifies support certificates before write admission), memory ecologies can prevent transient neural reasoning errors from entering the persistent germline.
