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
                             THE EPISTEMIC INTERFACE STACK
                             
            +-------------------------------------------------------------+
            |                 Neural Semantic Reasoner                    |
            |   * Flexible synthesis across natural language evidence     |
            |   * Proposes candidate beliefs and semantic answers         |
            |   * Unreliable at exact support boundary resolution (SBR)   |
            +------------------------------+------------------------------+
                                           | Proposals & Evidence Emitted
                                           v
            +-------------------------------------------------------------+
            |                  State Adjudication Layer                   |
            |   * Deduces state transitions (ADD, SUPERSEDES, EXPIRES)    |
            |   * Bitemporal validity tracking: Valid Time (t_v) x Trans  |
            |   * Isolates unresolved contradictions & temporal intervals |
            +------------------------------+------------------------------+
                                           | Authoritative Facts F(t_v | t_k)
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
1. **Support Acquisition:** Given prompt evidence $E(c)$, how does the kernel extract a sound, complete, and antichain-minimized premise family $\mathcal{S}_F(c)$ from model proposals? (Addressed in Rounds 1-4).
2. **Support Maintenance:** Given $\mathcal{S}_F(c)$, how does the entitlement hypergraph and action authority evolve as upstream premises are added, superseded, expired, or retracted? (Addressed in Round 5 and Round 6).

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
| 6. Reproductive          | Model emissions may be recorded for audit, but do not gain  |
|    Admission Gating      | reproductive memory privileges without a valid certificate. |
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
        
        PILLAR 4: EPISTEMIC REPRODUCTION & GOVERNANCE [MATURE]
        * Lineage immunity & selective quarantine (Exp 1B-C)
        * Structural proofreading & write certificates (Exp 1B-C2b)
        * Reproductive gating (R0 < 1 containment)
        
        PILLAR 5: EPISTEMIC ACTION AUTHORITY & LINEAGE PROJECTION [MATURE — STAGE 5B VALIDATED]
        * Hierarchy of epistemic incompleteness: binary -> kappa -> rho -> |Roots| -> rho_L -> S_L(c)
        * Proved that nominal multiplicity masquerades as independence in shared origin ancestry
        * Dual-layer containment: Belief Entitlement != Action Authorization (Stage 5C)
        * 100% compliance across 7 formal governance axioms via antichain-minimized S_L(c)
        
        PILLAR 6: EPISTEMIC STATE ADJUDICATION & TEMPORAL VALIDITY [EMERGING — ROUND 6]
        * Implicit supersession algebra: SUPERSEDES, EXPIRES, CONTRADICTS, RETRACT
        * Temporal validity state V_t, temporal support S_t(c), and lineage S_{L,t}(c)
        * Epistemic queries under natural change: WHY_t, WHAT_IF_t, THEN_WHAT_t
```

---

## 6. The Foundational Principle: Intervention-Sufficient Epistemic Representation

> **The Principle of Intervention-Sufficiency:**
> *Whenever two distinct epistemic states collapse to the same stored summary representation, but require different responses to some future causal intervention or external action, that summary is too lossy for the runtime.*

### The Class-Relative Sufficiency Form:
- $\mathcal{S}(c)$ is the **canonical intervention-sufficient normal form for premise revisions** (`WHAT_IF(premise)`).
- $\mathcal{S}_L(c)$ is the **canonical intervention-sufficient normal form for root-lineage revisions** (`WHAT_IF(root)`).
- The runtime maintains the explicit typed projection:
  $$\mathcal{S}(c) \xrightarrow{\mathcal{L}} \mathcal{S}_L(c) = \min_{\subseteq} \{ \{ \mathcal{L}(p) : p \in S_i \} : S_i \in \mathcal{S}(c) \}$$

---

## 7. The Two Open Boundaries (Known Dragons)

1. **Lineage Integrity & Adversarial Provenance Laundering:**
   GENE's formal guarantees assume lineage metadata $\mathcal{L}(p)$ is trustworthy. In multi-agent systems, lineage can be laundered via summarization, copy multiplication, or trusted-tool echoes. Write-time cryptographic origin binding is required.
2. **ATMS Support-Family Combinatorial Explosion:**
   Antichain labels $\mathcal{S}(c)$ can experience exponential growth in dense multi-path graphs. The runtime must empirically profile exact scale envelopes and define principled approximation thresholds.

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
    └── Exploration Round 5 Stage 5C: Neural Revision Bridge & Failure Decomposition (32 calls)
    
    [THE ACTIVE SCIENTIFIC MAINLINE — ROUND 6: STATE UNDER CHANGE]
    ├── Stage 6A: Supersession Algebra & Temporal Validity Transitions (0 LLM compute)
    ├── Stage 6B: Implicit Change Benchmark (Append-Only vs LWW vs Support-Aware) (0 LLM compute)
    └── Stage 6C: Neural State-Adjudication Bridge (~24-48 live calls)
```

---

## 9. Ten-Year Success Criteria

1. **Vocabulary:** AI architects routinely distinguish nominal memory occurrences from independent epistemic roots, and explanatory reported justification from minimal entitling support.
2. **Runtime Governance:** Persistent agent frameworks evaluate minimal support sets $\mathcal{S}(c)$ and lineage-projected hypergraphs $\mathcal{S}_L(c)$ before executing high-stakes actions or cascading deletions.
3. **Reproducibility Standard:** Autonomous agent benchmarks evaluate **revision correctness, non-destructive retention, and Support-Boundary Resolution under upstream change**.
4. **Architectural Separation:** Systems cleanly separate the neural reasoner (a stochastic candidate proposal engine) from the epistemic kernel (the deterministic entitlement runtime).

> **Core Research Creed:**
> *Cheap deterministic measurement -> tiny live mechanism test -> adversarial review -> only then scale.*
