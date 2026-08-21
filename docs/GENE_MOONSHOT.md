# GENE Moonshot: The Epistemic Runtime for Persistent AI

> *"A persistent AI should not merely remember what it believes. It should be able to maintain why it is entitled to believe it as the world changes."*

---

## 1. The Core Vision: Support-First, Lineage-Informed Epistemic Runtime

Contemporary AI memory systems treat persistence as a **bag of retrieved text**: embeddings, recency weights, and similarity scoring. When a memory changes, systems either silently leave stale facts active, blindly append contradictory updates, or execute coarse cascading deletes.

GENE's long-term objective is to make **epistemic belief maintenance a first-class systems primitive for persistent artificial intelligence**.

GENE is an **epistemic runtime for maintaining entitlement under change**.
- **Support-First:** For any durable belief $c$, the primary kernel object is its set of currently valid minimal support environments $\mathcal{S}_t(c) = \{S_1, \dots, S_k\}$. Support structure determines whether a belief is entitled to survive when the world changes.
- **Lineage-Informed:** Ancestry, authority, and provenance metadata annotate the elements of those support environments—determining source independence, action authority, and contamination boundaries.
- **Causally Auditable:** Counterfactual parent interventions distinguish genuine behavioral dependency from coincidental or hallucinated citation.

An agent operating over durable memory must be able to answer five fundamental questions for any claim $c$:

| Kernel Query | Semantic Meaning | Classic Analogy |
| :--- | :--- | :--- |
| **`WHY(c)`** | What minimal support environments $\mathcal{S}(c)$ justify $c$? | ATMS Assumption Environments |
| **`WHENCE(c)`** | What causal provenance lineages produced those supports? | Database Provenance Semirings |
| **`WHAT_IF(c, a)`** | If source or assumption $a$ is retracted, does $c$ survive via surviving support? | Non-Destructive Support Evaluation |
| **`THEN_WHAT(a)`** | If $a$ changes, which downstream beliefs, retrievals, and actions must be revised? | Self-Adjusting Dependency Recomputation |
| **`DID_YOU_ACTUALLY_USE(c, a)`** | Did the neural reasoner's output causally depend on $a$, or was $a$ merely cited / coincidental? | GENE Causal Intervention Engine |

```
                            THE EPISTEMIC INTERFACE STACK
                            
           ┌─────────────────────────────────────────────────────────────┐
           │                    FORMAL EPISTEMIC STATE                   │
           │          (Immutable IR, Hypergraph S_F, Lineage Graph)      │
           └──────────────────────────────┬──────────────────────────────┘
                                          │
                                          ▼
           ┌─────────────────────────────────────────────────────────────┐
           │                  EPISTEMIC CONTEXT COMPILER                 │
           │  • Serialization Invariance (Topological / Canonical Blocks)│
           │  • Non-leaking, backend-neutral evidence tagging            │
           │  • Explicit privilege boundaries (Raw, Topo, Lineage, Cert) │
           └──────────────────────────────┬──────────────────────────────┘
                                          │
                                          ▼
           ┌─────────────────────────────────────────────────────────────┐
           │                   NEURAL PROPOSAL ENGINE                    │
           │  • Flexible semantic reasoning across evidence              │
           │  • Subject to token realization drift & shortcut heuristics │
           └──────────────────────────────┬──────────────────────────────┘
                                          │
                                          ▼
           ┌─────────────────────────────────────────────────────────────┐
           │                  TYPED OUTPUT CANONICALIZER                 │
           │  • Maps surface-form drift (PROTOCOL_X7 -> PROTO_X7)        │
           │  • Enforces typed enums & schema conformity                 │
           └──────────────────────────────┬──────────────────────────────┘
                                          │
                                          ▼
           ┌─────────────────────────────────────────────────────────────┐
           │                 CROSS-FIELD CONTRACT VALIDATOR              │
           │  • Enforces logical coherence across structured fields      │
           │  • (status=indeterminable => N=null; status=det => N in Nat)│
           └──────────────────────────────┬──────────────────────────────┘
                                          │
                                          ▼
           ┌─────────────────────────────────────────────────────────────┐
           │             SUPPORT MINIMIZER & LINEAGE KERNEL              │
           │  • Preserves explanatory R(c) while extracting minimal S_F  │
           │  • Exact graph-computed ancestral root statistics (K_L)     │
           └──────────────────────────────┬──────────────────────────────┘
                                          │
                                          ▼
           ┌─────────────────────────────────────────────────────────────┐
           │                   FORMAL ADMISSION & REPAIR                 │
           │  • Proof checking (rejects illicit shortcuts: AD, BD, AE)   │
           │  • Non-destructive belief maintenance (prevents autoimmunity│
           └─────────────────────────────────────────────────────────────┘
```

The neural model is a **flexible candidate proposal engine operating inside a governed epistemic runtime**. **The model does not unilaterally define durable truth, compute graph statistics, or govern belief revision.** The Epistemic Kernel mediates memory admission, change propagation, and action authority.

---

## 2. Theoretical Foundations: Four Meanings of Support & Conformance Taxonomy

### The Four Meanings of Support
For any neural output or belief $c$, GENE distinguishes four non-interchangeable support relations:

1. **$E(c)$ (Exposed Evidence):** The set of documents or memory nodes present in the prompt context.
2. **$R(c)$ (Reported Justification):** The set of citations or evidence tags the model explicitly emits in its explanation.
3. **$C(c)$ (Causal Support):** The subset of evidence demonstrated counterfactually to alter the model's behavior under intervention ($\text{do}(x=0)$).
4. **$\mathcal{S}(c)$ (Minimal Entitling Support):** The irredundant formal premise environments $\{\mathcal{S}_1, \dots, \mathcal{S}_k\}$ that logically entitle the claim.

```
                  E(c) [Context Exposure]
                   └─── R(c) [Reported Justification / Explanatory Bloat]
                         └─── S(c) [Minimal Entitling Support Environments]
                         └─── C(c) [Counterfactually Verified Causal Influence]
```

> [!IMPORTANT]
> **The Epistemic Precision Principle:** A human-facing explanation citing all salient evidence ($R(c) = \{A,B,D,E\}$) is valid communication. However, if persistent memory records $R(c)$ conjunctively instead of separating minimal entitling paths ($\mathcal{S}(c) = \{\{A,B\}, \{D,E\}\}$), subsequent invalidation of irrelevant premise $D$ causes **revision overreach / false epistemic autoimmunity**.

### The Four-Layer Neural-Interface Conformance Taxonomy
Empirical evaluation in Exploration Round 4 demonstrates that neural-interface failures fall into four distinct layers:

1. **Layer 1: Symbolic / Interface Realization:** Token-level surface-form drift ($\text{PROTO\_X7} \to \text{PROTOCOL\_X7}$) under premise permutation or position without loss of underlying semantic belief ($D_{\text{perm,symbol}} = 0.3913$ vs $D_{\text{perm,semantic}} = 0.0000$). Controlled via **typed canonicalizers**.
2. **Layer 2: Cross-Field Contract Coherence:** Syntactically valid JSON whose fields are logically contradictory (`determinable` paired with `root_count=null`). Controlled via **deterministic contract validators**.
3. **Layer 3: Justification Precision Conformance:** Models dragging all salient evidence into support when multiple paths coexist ($K_{S,\text{exact}} = 12.5\%$ in entitled ecologies, $E_S = 1.625$ excess claims). Controlled via **kernel support extraction**.
4. **Layer 4: Formal Epistemic Derivability:** Deriving concrete answers from formally insufficient coalitions ($AD \lor BD \lor AE$ shortcuts). Controlled via **formal admission proof-checking**.

---

## 3. The Mathematics of Multi-Justification Support & Resilience

In a realistic memory ecology, a persistent claim $c$ possesses multiple alternative derivations.

### Minimal Epistemic Support Environments $\mathcal{S}(c)$
We model durable claim $c$ as associated with minimal sufficient premise environments:
$$\mathcal{S}(c) = \{S_1, S_2, \dots, S_k\}$$
where each $S_i = \{a_{i,1}, a_{i,2}, \dots, a_{i,m}\}$ is an irredundant conjunctive set of root assumptions such that:
$$\bigwedge_{a \in S_i} a \implies c$$

Provenance polynomial:
$$P(c) = \sum_{i=1}^k \prod_{a \in S_i} a$$

### Descendant Types Under Upstream Invalidation
When an ancestor $A$ is discredited or mutated ($A \leadsto 0$):

1. **Pure Infected Descendant ($I \to X$):**
   $$P(X) = A \implies P(X)\mid_{A=0} = 0 \quad \text{(Quarantine / Invalidate)}$$
2. **Recombinant Conjunctive Descendant ($IH \to X$):**
   $$P(X) = A \cdot H \implies P(X)\mid_{A=0} = 0 \cdot H = 0 \quad \text{(Quarantine / Invalidate)}$$
3. **Multiply Supported Alternative Descendant ($IA + HB \to X$):**
   $$P(X) = A \cdot M_1 + H \cdot M_2 \implies P(X)\mid_{A=0} = 0 + H \cdot M_2 = H \cdot M_2 > 0 \quad \text{\textbf{(PRESERVE)}}$$

### Epistemic Cut Set Size $\kappa(c)$ & Resilience Degradation
We define the structural epistemic resilience of a belief:
$$\kappa(c) = \min_{C \subseteq \mathcal{A}} \{|C| : \forall S_i \in \mathcal{S}(c), S_i \cap C \ne \emptyset\}$$
- $\kappa(c) = 1$: **Epistemically Fragile.** A single source failure eliminates all valid support.
- $\kappa(c) \ge 2$: **Epistemically Resilient.** Multiple independent ancestral retractions are required before the belief loses justification.

> [!NOTE]
> **Entitlement Degradation Under Partial Invalidation:** When premise $D$ is invalidated in $\mathcal{S}(C) = \{\{A,B\}, \{D,E\}\}$, claim $C$ does not die. Its support updates to $\mathcal{S}'(C) = \{\{A,B\}\}$ and its resilience degrades ($\kappa(C): 2 \to 1$). The belief remains active, but its **action authority degrades**, bridging non-destructive revision to Action Proportionality.

---

## 4. Seven Candidate Invariants of an Epistemic Kernel

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   SEVEN CANDIDATE EPISTEMIC INVARIANTS                                 │
├──────────────────────────┬─────────────────────────────────────────────────────────────┤
│ 1. Provenance            │ A descendant cannot gain evidential authority merely by     │
│    Preservation          │ being summarized, repeated, or reformatted.                 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 2. Support Completeness  │ Every durable belief must possess at least one valid,       │
│    and Grounding         │ unretracted minimal support set in S(c).                    │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 3. Independent-Support   │ Ten repetitions descended from one observation do not       │
│    Accounting            │ constitute ten independent observations.                    │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 4. Revision Closure      │ If an assumption changes, all dependent beliefs are either  │
│                          │ justified by surviving paths, marked dirty, or inactivated. │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 5. Non-Destructive       │ Invalidation of one support path does not destroy a claim   │
│    Correction            │ if an alternative valid support path remains active.        │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 6. Reproductive          │ Model emissions may be recorded for audit, but do not gain  │
│    Admission Gating      │ reproductive memory privileges without a valid certificate. │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 7. Action                │ Evidential thresholds for storing a working note differ     │
│    Proportionality       │ from those required to authorize an irreversible action.    │
└──────────────────────────┴─────────────────────────────────────────────────────────────┘
```

> **Open Design Invariant (Candidate 8 — Selection Integrity):** Unauthoritative state should not be able to alter the visibility, ranking, or context compilation of authoritative evidence in a manner that modifies downstream entitlement.

---

---

## 5. The Five Research Pillars: Current Status

```
                            THE FIVE PILLARS OF GENE
                            
       PILLAR 1: EPISTEMIC IDENTITY & PROVENANCE [MATURE]
       • Exposure vs report vs causal ancestry (Exp 0)
       • Occurrence identity vs semantic claim identity
       • Resistance to exact-copy & structural provenance laundering
       
       PILLAR 2: EPISTEMIC SUPPORT & MULTI-JUSTIFICATION [MATURE]
       • Minimal support sets S(c) and provenance polynomials
       • Epistemic cut sets κ(c) and structural resilience
       • Four-layer conformance taxonomy: symbol != contract != justification != derivability (Round 4)
       
       PILLAR 3: EPISTEMIC CHANGE & REVISION [SOLID — STAGE 5A VALIDATED]
       • Non-destructive correction (surviving path retention under partial invalidation)
       • Proved that loss of support algebra causes 100% false retractions on degraded states (Stage 5A)
       • Eliminates zombie derivations via root-expanded support S_root under stale cache regimes
       
       PILLAR 4: EPISTEMIC REPRODUCTION & GOVERNANCE [MATURE]
       • Lineage immunity & selective quarantine (Exp 1B-C)
       • Structural proofreading & write certificates (Exp 1B-C2b)
       • Reproductive gating (R0 < 1 containment)
       
       PILLAR 5: EPISTEMIC ACTION AUTHORITY & LINEAGE PROJECTION [SOLID — STAGE 5B VALIDATED]
       • Hierarchy of epistemic incompleteness: binary -> kappa -> rho -> |Roots| -> rho_L -> S_L(c)
       • Proved that nominal multiplicity masquerades as independence in shared origin ancestry
       • Proved that summary tuple rho_L is itself lossy relative to the canonical hypergraph S_L(c)
       • 100% compliance across 7 formal governance axioms via antichain-minimized lineage hypergraphs S_L(c)
```

---

## 6. The Foundational Principle: Intervention-Sufficient Epistemic Representation

> **The Principle of Intervention-Sufficiency:**
> *Whenever two distinct epistemic states collapse to the same stored summary representation, but require different responses to some future causal intervention or external action, that summary is too lossy for the runtime.*

### Intervention Sufficiency is Intervention-Relative:
- $\mathcal{S}(c)$ is the **intervention-sufficient normal form for premise-level changes** (`WHAT_IF(premise)`).
- $\mathcal{S}_L(c)$ is the **canonical intervention-sufficient normal form for root-lineage changes** (`WHAT_IF(root)`).
- The runtime maintains the explicit typed projection:
  $$\mathcal{S}(c) \xrightarrow{\mathcal{L}} \mathcal{S}_L(c) = \min_{\subseteq} \{ \{ \mathcal{L}(p) : p \in S_i \} : S_i \in \mathcal{S}(c) \}$$

This single principle unifies the entire scientific trajectory of GENE:
- **Nominal Multiplicity Bias (R1):** Identical memory repetitions collapse independent roots into occurrence counts.
- **Structural Provenance Laundering (1B-C0):** Node-only forgetting collapses ancestry into flat item records.
- **Explanatory Bloat (R4):** Neural reported citations collapse minimal support with irrelevant context.
- **Revision Autoimmunity (5A):** Flat dependency unions collapse alternative disjunctive paths into a single conjunctive cut-set.
- **Resilience Blindness (5A):** Scalar cut-set $\kappa$ collapses path loss in $(2,1) \to (1,1)$ where $\kappa$ stays constant.
- **Lineage Independence Blindness (5B):** Tuple $\rho=(|S|, \kappa)$ and global root counts collapse shared origin ancestry into independent alternatives.
- **Lineage Tuple Lossiness (5B):** Summary tuple $\rho_L = (|S_L|, \kappa_L)$ collapses single-root from conjunctive multi-root paths ($\{\{R_1\}\}$ vs $\{\{R_1, R_2\}\}$).
- **The Canonical Resolution:** The Epistemic Kernel must maintain the **antichain-minimized lineage-projected support hypergraph** $\mathcal{S}_L(c)$ alongside premise support $\mathcal{S}(c)$.

---

## 7. What GENE Has Established & The Next Scientific Frontier

```
                                  GENE PROGRESSION MATRIX
                                  
    [ESTABLISHED & FROZEN]
    ├── Exp 0: Lineage Observability & Causal Interventions (P(active|complete)=1, P(active|broken)=0)
    ├── Exp 1A: Transitive Mutation Transmission across Multi-Generational Horn-DAGs
    ├── Exp 1B-A: Allele Fidelity & Critical Branching Extinction R0
    ├── Exp 1B-B: Endogenous Retrieval Dynamics (X_path) & Surface-Area Scaling Feedback
    ├── Exp 1B-C: Lineage Quarantine (Selectivity S=+0.800) vs Node-Only Laundering (S=0.000)
    ├── Phase 10.5: Dual-Layer Governance (Lineage Immunity + Structural Proofreading Gate)
    ├── Exploration Round 1: Stale-Descendant Hysteresis & Nominal Multiplicity Bias
    ├── Exploration Round 2: Recombinant Support Graphs & Dual-Oracle Epistemic Evaluation
    ├── Exploration Round 3: Multi-Generation Branching Transmission & Cross-Shortcut Discovery
    ├── Exploration Round 4: Epistemic Context Compiler & Four-Layer Conformance Taxonomy
    ├── Exploration Round 5 Stage 5A: Revision Precision Assay & Loss of Support Algebra (432 cases)
    └── Exploration Round 5 Stage 5B: Action Governance & Lineage-Projected Resilience (368 cases)
    
    [THE ACTIVE SCIENTIFIC MAINLINE — STAGE 5C: NEURAL REVISION BRIDGE]
    └── Stage 5C — Neural Revision Bridge (~12–32 live calls):
        Verify end-to-end that real LLM outputs governed by kernel support minimizers resist downstream
        premise retraction and execute non-destructive revision compared to ungrounded raw memory.
```

---

## 8. Ten-Year Success Criteria

1. **Vocabulary:** AI architects routinely distinguish nominal memory occurrences from independent epistemic roots, and explanatory reported justification from minimal entitling support.
2. **Runtime Governance:** Persistent agent frameworks evaluate minimal support sets $\mathcal{S}(c)$ and lineage-projected hypergraphs $\mathcal{S}_L(c)$ before executing high-stakes actions or cascading deletions.
3. **Reproducibility Standard:** Autonomous agent benchmarks evaluate **revision correctness and non-destructive retention under upstream change**.
4. **Architectural Separation:** Systems cleanly separate the neural reasoner (a stochastic candidate proposal engine) from the epistemic kernel (the deterministic entitlement runtime).

> **Core Research Creed:**
> *Cheap deterministic measurement $\to$ tiny live mechanism test $\to$ adversarial review $\to$ only then scale.*

