# GENE Moonshot: The Epistemic Runtime for Persistent AI

> *"Neural systems are powerful proposers of semantic conclusions but unreliable custodians of their own epistemic state. Persistent artificial intelligence therefore requires an external, intervention-sufficient truth-maintenance layer that preserves minimal support and causal provenance across change."*

---

## 1. The Core Vision: Support-First, Lineage-Informed Epistemic Runtime

Contemporary AI memory systems treat persistence as a **bag of retrieved text**: embeddings, recency weights, and similarity scoring. When a memory changes, systems either silently leave stale facts active, blindly append contradictory updates, or execute coarse cascading deletes.

GENE's long-term objective is to make **epistemic belief maintenance a first-class systems primitive for persistent artificial intelligence**.

GENE is an **epistemic runtime for maintaining entitlement under change**:
- **Support-First:** For any durable belief $c$, the primary kernel object is its set of currently valid minimal support environments $\mathcal{S}_t(c) = \{S_1, \dots, S_k\}$. Support structure determines whether a belief is entitled to survive when the world changes.
- **Lineage-Informed:** Ancestry, authority, and provenance metadata annotate the elements of those support environments—determining source independence, action authority, and contamination boundaries.
- **Causally Auditable:** Counterfactual parent interventions distinguish genuine behavioral dependency from coincidental or hallucinated citation.

An agent operating over durable memory must be able to answer five fundamental questions for any claim $c$:

| Kernel Query | Semantic Meaning | Classical Foundation & Formalization |
| :--- | :--- | :--- |
| **`WHY(c)`** | What minimal support environments $\mathcal{S}(c)$ justify $c$? | De Kleer ATMS Assumption Labels |
| **`WHENCE(c)`** | What causal provenance lineages produced those supports? | Database Provenance Semirings $(K, +, \cdot, 0, 1)$ |
| **`WHAT_IF(c, a)`** | If source or assumption $a$ is retracted, does $c$ survive via surviving support? | AGM Non-Destructive Support Evaluation |
| **`THEN_WHAT(a)`** | If $a$ changes, which downstream beliefs, retrievals, and actions must be revised? | Self-Adjusting Dependency Recomputation |
| **`DID_YOU_ACTUALLY_USE(c, a)`** | Did the neural reasoner's output causally depend on $a$, or was $a$ merely cited / coincidental? | Causal Intervention Sufficiency Engine |

```
                              THE EPISTEMIC COMPILER STACK
                              
             +-------------------------------------------------------------+
             |                 Natural Language Ingress                    |
             |   * Stochastic semantic parsing & entity mention extraction |
             |   * Temporal interval extraction & prompt reproduction      |
             +------------------------------+------------------------------+
                                            | Extracted Mentions & Spans
                                            v
             +-------------------------------------------------------------+
             |           Ontology Binding & Ingress Admission             |
             |   * SourceRecord != ParsedAttestation != AdmittedFact       |
             |   * Hypothesis preservation (DEFERRED_BINDING over B(x))    |
             |   * Proof-carrying certificates: ADMIT, DEFER, REJECT       |
             +------------------------------+------------------------------+
                                            | Validated Observation ⟨s, p, o, tv_s, tv_e⟩
                                            v
             +-------------------------------------------------------------+
             |                  State Adjudication Layer                   |
             |   * Contract-guided state transitions (ASSERT, SUPERSEDES)  |
             |   * Bitemporal validity tracking: Valid Time (t_v) x Trans  |
             |   * Cautious conflict isolation & pairwise dispute tracking |
             +------------------------------+------------------------------+
                                            | Authoritative Events & Facts F(t_v | t_k)
                                            v
             +-------------------------------------------------------------+
             |             Support Minimizer & Lineage Kernel              |
             |   * Extracts formal minimal S_F; routes R(c) to telemetry   |
             |   * Exact graph-computed ancestral root statistics (S_L)    |
             +------------------------------+------------------------------+
                                            | Support Hypergraph S_L,t(c)
                                            v
             +-------------------------------------------------------------+
             |                 Persistent Action Governance                |
             |   * Non-destructive belief revision under change            |
             |   * Evaluates lineage authority Auth(S_L) against threshold |
             |   * Governs downstream context compilation & action gating  |
             +-------------------------------------------------------------+
```

The neural model is a **flexible candidate proposal engine operating inside a governed epistemic runtime**. **The model does not unilaterally define durable truth, compute graph statistics, or govern belief revision.** The Epistemic Kernel mediates state adjudication, temporal validity, change propagation, and action authority.

---

## 2. Theoretical Foundations: Support Distinctions & Dual-Phase Architecture

### The Four Meanings of Support & The Telemetry Boundary
For any neural output or belief $c$, GENE distinguishes four non-interchangeable support relations:

1. **$E(c)$ (Exposed Evidence):** The set of documents or memory nodes present in the prompt context.
2. **$R(c)$ (Reported Justification / Process Telemetry):** The set of citations or evidence tags the model explicitly emits in its explanation.
3. **$C(c)$ (Causal Support):** The subset of evidence demonstrated counterfactually to alter the model's behavior under intervention ($\text{do}(x=0)$).
4. **$\mathcal{S}(c)$ (Minimal Entitling Support / Authoritative State):** The irredundant formal premise environments $\{\mathcal{S}_1, \dots, \mathcal{S}_k\}$ that logically entitle the claim.

```
                  E(c) [Context Exposure]
                   |--- R(c) [Reported Justification -> TELEMETRY / AUDIT LAYER ONLY]
                         |--- S(c) [Minimal Entitling Support -> AUTHORITATIVE STATE]
                         |--- C(c) [Counterfactually Verified Causal Influence]
```

> [!IMPORTANT]
> **The Epistemic Telemetry Separation Rule:** Human-facing explanations citing all salient evidence ($R(c) = \{A,B,D,E\}$) belong in the process audit layer. Persistent memory must record dynamically evaluated, antichain-minimized formal support $\mathcal{S}_F(c) = \{\{A,B\}, \{D,E\}\}$. Confusing $R(c)$ with authoritative state causes $100\%$ revision autoimmunity under change.

### Support Acquisition vs. Support Maintenance
Belief governance divides cleanly into two operational phases:
1. **Support Acquisition & Ingress:** Given prompt evidence $E(c)$, how does the runtime extract a validated, antichain-minimized premise family $\mathcal{S}_F(c)$ from natural language observations without silent binding errors? (Rounds 1–4, 6C, and Round 7).
2. **Support Maintenance:** Given $\mathcal{S}_F(c)$, how does the entitlement hypergraph and action authority evolve as upstream premises are added, superseded, expired, or retracted? (Rounds 5, 6A, and 6B).

---

## 3. The Mathematics of Multi-Justification Support & Resilience

In a realistic memory ecology, a persistent claim $c$ possesses multiple alternative derivations.

### Minimal Epistemic Support Environments $\mathcal{S}(c)$
We model durable claim $c$ as associated with minimal sufficient premise environments (ATMS assumption label):
$$\mathcal{S}(c) = \{S_1, S_2, \dots, S_k\}$$
where each $S_i = \{a_{i,1}, a_{i,2}, \dots, a_{i,m}\}$ is an irredundant conjunctive set of root assumptions such that $\bigwedge_{a \in S_i} a \implies c$.

Provenance polynomial over semiring $(K, +, \cdot, 0, 1)$:
$$P(c) = \sum_{i=1}^k \prod_{a \in S_i} a$$

### Descendant Types Under Upstream Invalidation
When an ancestor $A$ is discredited or mutated ($A \leadsto 0$):
1. **Pure Infected Descendant ($I \to X$):** $P(X) = A \implies P(X)\mid_{A=0} = 0$ (Quarantine / Invalidate).
2. **Recombinant Conjunctive Descendant ($IH \to X$):** $P(X) = A \cdot H \implies P(X)\mid_{A=0} = 0 \cdot H = 0$ (Quarantine / Invalidate).
3. **Multiply Supported Alternative Descendant ($IA + HB \to X$):** $P(X) = A \cdot M_1 + H \cdot M_2 \implies P(X)\mid_{A=0} = H \cdot M_2 > 0$ (**PRESERVE** via surviving path).

### Support-Boundary Resolution ($SBR$)
Neural belief revision under change exhibits dual error channels:
- **False Expression Rate ($F^+$):** $P(\text{ACTIVE} \mid \text{RETRACTED})$ (pseudo-path hallucination).
- **False Retraction Rate ($F^-$):** $P(\text{UNKNOWN} \mid \text{DEGRADED})$ (over-retraction under perturbation).
- **Support-Boundary Resolution ($SBR$):**
  $$\text{SBR} = \frac{1}{2} \left[ P(\text{ACTIVE} \mid \text{DEGRADED}) + P(\text{UNKNOWN} \mid \text{RETRACTED}) \right] = 1 - \frac{F^+ + F^-}{2}$$

---

## 4. Seven Candidate Invariants of an Epistemic Kernel

```
+----------------------------------------------------------------------------------------+
|                   SEVEN CANDIDATE EPISTEMIC INVARIANTS                                 |
+--------------------------+-------------------------------------------------------------+
| 1. Provenance            | A descendant cannot gain evidential authority merely by     |
|    Preservation          | being summarized, repeated, or reformatted.                 |
+--------------------------+-------------------------------------------------------------+
| 2. Support Completeness  | Every durable belief must possess at least one valid,       |
|    and Grounding         | unretracted minimal support set in S(c).                    |
+--------------------------+-------------------------------------------------------------+
| 3. Independent-Support   | Ten repetitions descended from one observation do not       |
|    Accounting            | constitute ten independent observations.                    |
+--------------------------+-------------------------------------------------------------+
| 4. Revision Closure      | If an assumption changes, all dependent beliefs are either  |
|                          | justified by surviving paths, marked dirty, or inactivated. |
+--------------------------+-------------------------------------------------------------+
| 5. Non-Destructive       | Invalidation of one support path does not destroy a claim   |
|    Correction            | if an alternative valid support path remains active.        |
+--------------------------+-------------------------------------------------------------+
| 6. Reproductive & Write  | Model emissions and external observations do not gain       |
|    Admission Gating      | durable memory privileges without a validated certificate.  |
+--------------------------+-------------------------------------------------------------+
| 7. Action                | Evidential thresholds for storing a working note differ     |
|    Proportionality       | from those required to authorize an irreversible action.    |
+--------------------------+-------------------------------------------------------------+
```

---

## 5. The Six Research Pillars

```
                             THE SIX PILLARS OF GENE
                             
        PILLAR 1: EPISTEMIC IDENTITY & PROVENANCE [MATURE]
        * Exposure vs report vs causal ancestry (Exp 0)
        * Occurrence identity vs semantic claim identity
        * Resistance to exact-copy & structural provenance laundering
        
        PILLAR 2: EPISTEMIC SUPPORT & MULTI-JUSTIFICATION [MATURE]
        * Minimal support sets S(c) and database provenance semirings
        * Epistemic cut sets κ(c) and structural resilience
        * Four-layer conformance taxonomy: symbol != contract != justification != derivability (Round 4)
        
        PILLAR 3: EPISTEMIC CHANGE & REVISION [MATURE — ROUND 5 VALIDATED]
        * Non-destructive correction (surviving path retention under partial invalidation)
        * Proved that flat dependency sets cause 100% false retractions on degraded states (Stage 5A)
        * Characterized Support-Boundary Resolution (SBR) across live neural revision (Stage 5C)
        
        PILLAR 4: EPISTEMIC REPRODUCTION & WRITE ADMISSION [MATURE CORE / ROUND 7 EXPANDING]
        * Lineage immunity & selective quarantine (Exp 1B-C)
        * Structural proofreading & write certificates (Exp 1B-C2b)
        * Epistemic Write Admission: Attestation != Admitted Fact (Round 7 Ingress Frontier)
        
        PILLAR 5: EPISTEMIC ACTION AUTHORITY & LINEAGE PROJECTION [MATURE — STAGE 5B VALIDATED]
        * Hierarchy of epistemic incompleteness: binary -> kappa -> rho -> |Roots| -> rho_L -> S_L(c)
        * Proved that nominal multiplicity masquerades as independence in shared origin ancestry
        * Dual-layer containment: Belief Entitlement != Action Authorization (Stage 5C)
        * 100% compliance across 7 formal governance axioms via antichain-minimized S_L(c)
        
        PILLAR 6: EPISTEMIC STATE ADJUDICATION & TEMPORAL VALIDITY [MATURE — ROUND 6 VALIDATED]
        * Bitemporal supersession algebra: Valid Time (t_v) x Knowledge Time (t_k) (Stage 6A)
        * Predicate ontology contracts: TIME_VARYING, ADDITIVE, EPISODIC, INTERVAL_BOUNDED (Stage 6B)
        * Fault localization & error boundary externalization at neural interface (Stage 6C)
```

---

## 6. The Foundational Principle: Intervention-Sufficient Epistemic Representation

> **The Principle of Intervention-Sufficiency:**
> *Whenever two distinct epistemic states collapse to the same stored summary representation, but require different responses to some future causal intervention or external action, that summary is too lossy for the runtime.*

### The Ingress Extension: Candidate Intervention-Sufficient Binding Principle
$$\forall b_i, b_j \in \mathcal{B}(x), \; \forall \iota \in \mathcal{I}: \; \text{Response}(b_i, \iota) = \text{Response}(b_j, \iota)$$
Two candidate entity or role bindings may be safely collapsed to one durable representation if and only if they yield identical responses across all future queries and interventions in class $\mathcal{I}$. Otherwise, storing $\text{AMBIGUOUS}$ is strictly superior to premature commitment.

---

## 7. The Three Open Frontiers ("The Three Dragons")

```
+========================================================================================================+
|                                    THE THREE DRAGONS OF PERSISTENT AI                                  |
+============================+===========================================================================+
| 1. Ingress Integrity       | How messy, ambiguous, authority-laden language becomes a canonical,       |
|    (Round 7 Active Frontier)| authorized fact without silent binding, role, or authority errors.        |
+----------------------------+---------------------------------------------------------------------------+
| 2. Lineage Integrity       | Whether origin identities and independence classes can be trusted under   |
|    (Security Sidecar)      | multi-agent copying, summarization, Sybil attacks, and tool echoes.       |
+----------------------------+---------------------------------------------------------------------------+
| 3. Representation Scale    | How to preserve intervention-sufficient support hypergraphs without       |
|    (Systems Sidecar)       | exponential materialization in dense, multi-path dependency networks.    |
+============================+===========================================================================+
```

---

## 8. What GENE Has Established & The Next Frontier

```
                                  GENE PROGRESSION MATRIX
                                  
    [ESTABLISHED & FROZEN]
    ├── Exp 0: Lineage Observability & Causal Interventions (P(active|complete)=1, P(active|broken)=0)
    ├── Exp 1A: Transitive Mutation Transmission across Multi-Generational Horn-DAGs
    ├── Exp 1B-A: Allele Fidelity & Critical Branching Extinction R0
    ├── Exp 1B-B: Endogenous Retrieval Dynamics (X_path) & Surface-Area Scaling Feedback
    ├── Exp 1B-C: Lineage Quarantine (Selectivity S=+0.800) vs Node-Only Laundering (S=0.000)
    ├── Phase 10.5: Dual-Layer Governance (Lineage Immunity + Structural Proofreading Gate)
    ├── Exploration Round 4: Epistemic Context Compiler & Four-Layer Conformance Taxonomy
    ├── Exploration Round 5 Stage 5A: Revision Precision Assay & Loss of Support Algebra (432 cases)
    ├── Exploration Round 5 Stage 5B: Action Governance & Lineage-Projected Resilience (368 cases)
    ├── Exploration Round 5 Stage 5C: Neural Revision Bridge & Failure Decomposition (32 calls)
    ├── Exploration Round 6 Stage 6A: Bitemporal Supersession Algebra & Conflict Windows (0 compute)
    ├── Exploration Round 6 Stage 6B / 6B.1: Contract-Guided Adjudication & Temporal Ordering (200 cases)
    └── Exploration Round 6 Stage 6C: Neural Extraction Bridge, Fault Localization, & Replay (28 calls)
    
    [THE ACTIVE SCIENTIFIC MAINLINE — ROUND 7: EPISTEMIC INGRESS & WRITE ADMISSION]
    ├── Wave 1: Binding Algebra, Attestation Certificates, & 120-World 4-Probe Benchmark
    ├── Wave 2: Authority Sidecar & Provenance Non-Amplification Invariants
    ├── Wave 3: Adversarial Review & Holdout Mapping
    └── Wave 4: 52-Call Live Interface Assay (Free Gen vs Candidate Selection vs Constrained Grammar)
```

---

## 9. Ten-Year Success Criteria

1. **Vocabulary:** AI architects routinely distinguish nominal memory occurrences from independent epistemic roots, and explanatory reported justification from minimal entitling support.
2. **Runtime Governance:** Persistent agent frameworks evaluate minimal support sets $\mathcal{S}(c)$ and lineage-projected hypergraphs $\mathcal{S}_L(c)$ before executing high-stakes actions or cascading deletions.
3. **Reproducibility Standard:** Autonomous agent benchmarks evaluate **revision correctness, non-destructive retention, and Support-Boundary Resolution under upstream change**.
4. **Architectural Separation:** Systems cleanly separate the neural reasoner (a stochastic candidate proposal engine) from the epistemic kernel (the deterministic entitlement runtime).

> **Core Research Creed:**
> *Cheap deterministic measurement -> tiny live mechanism test -> adversarial review -> only then scale.*
