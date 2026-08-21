# The GENE Scientific Story Memo
**A Unified Narrative of Error Inheritance, Retrieval Epidemiology, Selective Lineage Immunity, Support Algebra, Bitemporal Truth Maintenance, and The Epistemic Compiler**

**Document Version:** 3.0.0 (The Epistemic Compiler & Round 6 Synthesis)  
**Status:** Canonical Scientific Narrative  
**Authoritative Manifest:** [`data/canonical_results_manifest.json`](../data/canonical_results_manifest.json)  
**Core Reference Implementation:** [`src/gene/`](../src/gene/)  

---

## Executive Abstract

Modern AI systems increasingly rely on persistent memory to retain knowledge, context, and operational state across sessions and interactions. When an erroneous or poisoned premise enters persistent memory, how does it spread, and how can an agent maintain why it is entitled to believe a claim as the world changes?

Standard benchmarks treat memory errors as static retrieval failures or transient model hallucinations. In contrast, the **Genealogical Epistemic Network Experiments (GENE)** project treats persistent memory as an *evolutionary epistemic runtime*. Across fifteen experimental phases and six exploratory rounds, GENE systematically decomposes the lifecycle of memory, reasoning, revision, and action:
$$\text{Natural Language Ingress} \longrightarrow \text{Ontology Binding} \longrightarrow \text{Write Admission} \longrightarrow \text{State Adjudication} \longrightarrow \text{Bitemporal State} \longrightarrow \text{Support Minimization} \longrightarrow \text{Lineage Action}$$

This memo synthesizes the **twelve core discoveries** that define the project's canonical scientific contribution:
1. **Exposure $\ne$ reported justification $\ne$ causal lineage** (Experiment 0).
2. **Globally false premises reproduce through locally valid deduction** (Experiment 1A).
3. **Retrieval availability ($X_{\text{path}}$) governs reproductive branching** (Experiment 1B-B).
4. **Lineage metadata enables selective delayed quarantine ($S = \text{TPR} - \text{FPR}$)** across semantic drift (Experiment 1B-C1b).
5. **Memory containment does not guarantee behavioral containment** (Experiment 1B-C2a).
6. **Structural proofreading prevents pseudo-path reasoning from entering the germline** (Experiment 1B-C2b).
7. **Neural reported justification exhibits 100% explanatory bloat ($E_S > 0$)**, and epistemic output decomposes into four independent conformance layers (Round 4).
8. **Flattening alternative support hypergraphs $\mathcal{S}(c)$ causes 100% false retractions** on damaged-but-still-entitled states under partial invalidation (Stage 5A).
9. **The Principle of Intervention-Sufficiency**: scalar cut-sets ($\kappa$), tuple signatures ($\rho$), and global root counts are lossy representations; action governance requires the lineage-projected minimal support hypergraph $\mathcal{S}_L(c)$ and root resilience $\rho_L(c)$ (Stage 5B).
10. **State under change requires bitemporal validity and predicate-aware ontology contracts**: single-clock LWW heuristics structurally collapse, while contract adjudication preserves $100\%$ state and transition fidelity (Stages 6A, 6B, 6B.1).
11. **Epistemic Error Boundary Externalization & The Symbol Realization Boundary**: modular extraction localizes neural uncertainty strictly to Layer 0 without downstream runtime autoimmunity ($0/12$), where the dominant bottleneck is not temporal comprehension ($12/12$ accurate intervals) but compilation into canonical symbolic vocabularies (Stage 6C).
12. **The Epistemic Compiler Architecture & Attestation vs Admission**: persistent epistemic state requires treating the neural-formal boundary as a formal compiler pipeline, enforcing the fundamental distinction between an attestation (*Source $S$ asserted $P$*) and an admitted fact (*$P$ is an active world fact*) (Round 6 Synthesis).

```
                                  THE EPISTEMIC COMPILER ARCHITECTURE
                                  
   +───────────────────────────────────+
   │   Natural Language Ingress        │  - Mention extraction & temporal interval parsing
   +───────────────────────────────────+
                     │
                     ▼
   ┌───────────────────────────────────┐  LAYER 1: Epistemic Ingress & Write Admission (Round 7)
   │   Ontology Binding & Gating       │  - Resolves surface mentions to candidate namespace
   │   [ Attestation != Admitted Fact ]│  - Gating: ADMIT, AMBIGUOUS, NOVEL, REJECT
   └───────────────────────────────────┘  - Evaluates Candidate Intervention-Sufficiency
                     │
                     ▼ (Validated Observation ⟨s, p, o, tv_s, tv_e⟩)
   ┌───────────────────────────────────┐  LAYER 2: State Adjudication & Temporal Validity (Stage 6A/6B)
   │  Contract-Guided Adjudicator      │  - Evaluates Predicate Contracts: TIME_VARYING, ADDITIVE, etc.
   │    [ Bitemporal Engine (t_v, t_k)]│  - Emits formal transition batch [ASSERT, SUPERSEDES, etc.]
   └───────────────────────────────────┘  - Maintains active occurrence records F(t_v | t_k)
                     │
                     ▼ (Authoritative Occurrences)
   ┌───────────────────────────────────┐  LAYER 3: Support Minimizer & Conformance Kernel (R4/R5)
   │   Antichain Support Engine        │  - Extracts formal minimal S_F(c); routes R(c) to telemetry
   │     [ Non-Destructive Revision ]  │  - Projects support to root hypergraph S_L,t(c)
   └───────────────────────────────────┘  - Prevents 100% false retractions on degraded states
                     │
                     ▼ (Lineage-Projected Support Hypergraph S_L)
   ┌───────────────────────────────────┐  LAYER 4: Lineage-Projected Action Governance (Stage 5B)
   │   Governance Engine (S_L, rho_L)  │  - Dual-layer containment: Belief Entitlement != Action Auth
   │      [ Enforces 7 Axioms ]        │  - Gates high-stakes actions with mathematical proportionality
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
- **Canonical Ground-Truth Oracle ($\mathcal{O}^*$)**: Evaluates objective factual accuracy against the uncorrupted base world.
- **Exposure-Consistent Lineage Oracle ($\mathcal{O}_{\mathcal{E}}$)**: Evaluates whether the emitted claim is a formally sound deductive consequence of the memories actually retrieved and placed into context.

### Key Empirical Findings:
- Under pristine deduction, falsehood propagated across three generations with **100% transmission fidelity** ($\tau = 1.000, N=24$ live calls).
- Every intermediate inference was scored as **100% locally sound** by $\mathcal{O}_{\mathcal{E}}$, while being **100% objectively false** under $\mathcal{O}^*$.
- **Takeaway**: Once an unverified premise is admitted to persistent memory, perfectly sound logical deduction acts as an error amplifier rather than an error corrector.

---

## 3. Discovery 3: Retrieval Availability Governs Reproductive Branching (Experiment 1B-B)

Memory persistence does not imply reproductive opportunity. In persistent multi-hop reasoning, an agent only derives a downstream conclusion if *all* required premises are simultaneously co-retrieved into context ($X_{\text{path}} = \prod_{p \in \text{Premises}} X_p = 1$).

### Key Empirical Findings:
- Evaluated across 240 structured retrieval trials, the effective reproductive number $R_{\text{eff}}$ scaled strictly with multi-hop retrieval availability $X_{\text{path}}$.
- Lexical surface-area feedback created sharp non-linear phase transitions: expanding a mutated premise into multiple downstream notes increased its collective BM25 surface area, triggering runaway supercritical propagation ($R_0 > 1.0$) unless explicitly constrained.

---

## 4. Discovery 4: Lineage Enables Selective Delayed Quarantine (Experiment 1B-C1b)

When a root memory is discovered to be corrupted *after* downstream reproduction has occurred, how can an agent purge the contagion without destroying healthy knowledge?

### Key Empirical Findings:
- Lineage-blind forgetting mechanisms (uniform thinning, recency pruning) are bounded by $C_H = C_I$: purging infected nodes ($1 - C_I$) destroys healthy memories ($1 - C_H$) at an identical rate (selectivity $S = C_H - C_I = 0.000$).
- **Lineage-Aware Quarantine** queries the provenance DAG to prune the infected ancestral cone. Across 12 paired ecologies, lineage quarantine achieved **$S = +0.800$ selectivity** ($C_H = 1.000, C_I = 0.200$), perfectly matching the theoretical calibration identity $S = \text{TPR} - \text{FPR}$.

---

## 5. Discovery 5: Memory Containment Does Not Guarantee Behavioral Containment (Experiment 1B-C2a)

Can an agent safely operate if an infected premise is removed from context ($X_{\text{path}} = 0$)?

### Key Empirical Findings:
- In a 30-call live assay on Gemma 3:12B, breaking the legitimate support path resulted in the model manufacturing **unsupported pseudo-paths** in $37.5\%$ of cases ($\mu_U = 0.375$), citing isolated fragments to justify conclusions.
- **Takeaway**: Memory governance (Layer 1) is necessary but insufficient. The runtime requires active validation to ensure emitted conclusions structurally unify with valid support.

---

## 6. Discovery 6: Structural Proofreading Prevents Germline Infection (Experiment 1B-C2b)

To eliminate pseudo-path hallucination, GENE implemented an automated **First-Order Structural Proofreader** that mechanically validates whether cited memory IDs formally satisfy rule antecedents.

### Key Empirical Findings:
- In 30 live calls on Gemma 3:12B, the proofreader intercepted all 9 unsupported pseudo-path emissions, admitting only valid derivations ($6/6$) and clean abstentions ($15/15$).
- Heritable mutation transmission dropped from $\mu_U = 0.375$ to **$\mu_{U, \text{heritable}} = \mathbf{0.000}$**, successfully establishing **Layer 2 Reproductive Admission Gating**.

---

## 7. Discovery 7: The Four-Layer Epistemic Conformance Taxonomy & Explanatory Bloat (Round 4)

Round 4 investigated the internal fidelity of model-generated justifications, evaluating 116 live calls across entitled and unentitled worlds.

### Key Empirical Findings:
- Epistemic output decomposes into four independent layers:
  $$\text{Symbol Realization} \ne \text{Contract Coherence} \ne \text{Justification Precision} \ne \text{Formal Derivability}$$
- Models exhibited **$87.5\%$ explanatory bloat** ($7/8$ cases, mean excess $1.625$ redundant citations) in entitled ecologies, alongside $20.8\%$ cross-field contract violations and $25.0\%$ symbol drift.
- **Takeaway**: Self-reported justification $R(c)$ belongs in human-facing telemetry; persistent memory state requires antichain-minimized formal support $\mathcal{S}_F(c)$.

---

## 8. Discovery 8: Flat Dependency Sets Cause 100% Revision Autoimmunity (Round 5 Stage 5A)

When a premise is partially invalidated, how does memory maintain entitlement? Standard frameworks represent dependencies as a flat conjunctive union $D(c) = \bigcup S_i$.

### Key Empirical Findings:
- Evaluated across 432 deterministic worlds, flat dependency unions suffered **$100\%$ false retractions ($104/104$)** on damaged-but-still-entitled states (revision autoimmunity).
- **Support-First Algebra** maintained the full antichain hypergraph $\mathcal{S}(c) = \{S_1, \dots, S_k\}$, achieving **$100\%$ revision precision ($432/432$)** by verifying whether at least one alternative support path remained active.

---

## 9. Discovery 9: Intervention-Sufficiency & Lineage Action Governance (Round 5 Stage 5B & 5C)

How does an agent govern real-world actions when upstream evidence is degraded?

### Key Empirical Findings:
- The **Hierarchy of Epistemic Incompleteness** proved that scalar cut-sets ($\kappa$), tuple signatures ($\rho$), and global root counts suffer catastrophic representation collisions under change.
- In shared origin ancestry ($A, D \leftarrow R_1$), nominal multiplicity masquerades as independence. Action governance requires the **lineage-projected support hypergraph $\mathcal{S}_L(c)$**, achieving **$100\%$ compliance across 7 formal governance axioms**.
- In live Stage 5C ($N=32$ calls), the support-first runtime achieved **$100\%$ entitlement retention** and **$100\%$ clean abstention**, enforcing preregistered lineage thresholds to block high-stakes actions when structural lineage was degraded.

---

## 10. Discovery 10: State Under Change Requires Bitemporality & Predicate Contracts (Round 6 Stage 6A & 6B)

How does memory distinguish between a replacement, an accumulation, an episodic event, and a temporary lease?

### Key Empirical Findings:
- **Bitemporality is Mandatory**: Tracking Valid Time ($t_v$) and Knowledge Transaction Time ($t_k$) independently is structurally necessary. The Stage 6B.1 micro-assay demonstrated that Knowledge-Time LWW achieved only $33.3\%$ accuracy, Valid-Time LWW achieved $75.0\%$, while the GENE Bitemporal Engine achieved **$100.0\%$ ($12/12$)**.
- **Predicate Ontology Contracts**: Adjudicating updates requires explicit contracts (`TIME_VARYING`, `ADDITIVE`, `EPISODIC`, `INTERVAL_BOUNDED`). In a 200-case factorial benchmark, contract adjudication achieved **$100.0\%$ transition and state fidelity**, while generic LWW policies collapsed to $55.0\%$.

---

## 11. Discovery 11: Epistemic Error Boundary Externalization & Symbol Realization (Round 6 Stage 6C)

Can a neural model emit state transitions directly, or should it extract structured observations for formal adjudication?

### Key Empirical Findings:
- **Neural Transition Collapse**: Direct neural transition generation (Arm N1) suffered a spontaneous collapse toward replacement semantics (`SUPERSEDES` in 10/12 cases, $0/12$ valid batches).
- **Fault Localization**: Modular extraction (Arm N2) strictly externalized neural uncertainty to Layer 0 (the extraction boundary), preventing downstream runtime corruption and eliminating runtime autoimmunity ($0/12$).
- **The Symbol Realization Bottleneck**: Gemma 3:12B extracted temporal intervals with **$100.0\%$ accuracy ($12/12$)**, but scored $8.3\%$ on exact canonical tuple extraction due to un-normalized entity strings (`"Auditor"` vs `Value_Auditor`). A deterministic normalization audit recovered **$11/12$ ($91.7\%$)** extraction fidelity.

---

## 12. Discovery 12: The Epistemic Compiler & Attestation vs Admission (Round 6 Synthesis)

The overarching discovery of Round 6 is that persistent memory is a **formal compiler for epistemic state**:
$$\text{Natural Language} \xrightarrow{\text{Parsing}} \text{Mention} \xrightarrow{\text{Linking}} \text{Canonical Symbol} \xrightarrow{\text{Validation}} \text{Admitted Candidate} \xrightarrow{\text{Contract}} \text{Event Batch} \xrightarrow{\text{Engine}} \text{Bitemporal State} \xrightarrow{\text{Kernel}} \text{Support \& Lineage} \xrightarrow{\text{Governance}} \text{Action}$$

Because $\text{Fault Localization} \ne \text{Error Containment}$, the deterministic kernel faithfully records whatever candidate is admitted. This elevates the fundamental distinction between an **Attestation** and an **Admitted Fact**:
- **$\text{Exposure} \ne \text{Report} \ne \text{Causal Support}$** (Experiment 0).
- **$\text{OriginIdentity} \ne \text{DerivationLineage} \ne \text{IndependenceClass}$** (Stage 5B).
- **$\text{SemanticClaim} \ne \text{OccurrenceNode}$** (Stage 6A).
- **$\text{Attestation} \ne \text{AdmittedFact}$** (Round 6 Synthesis & Round 7 Ingress Frontier).

An attestation (*Source $S$ asserted proposition $P$*) does not automatically create an active world fact. Epistemic integrity requires an explicit **Write Admission Gate** evaluating candidate intervention-sufficiency before a candidate achieves durable factual status.
