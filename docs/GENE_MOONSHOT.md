# GENE Moonshot: The Epistemic Runtime for Persistent AI

> *"A persistent AI should not merely remember what it believes. It should be able to maintain why it is entitled to believe it as the world changes."*

---

## 1. The Core Vision

Contemporary AI memory systems treat persistence as a **bag of retrieved text**: embeddings, recency weights, and similarity scoring. When a memory changes, systems either silently leave stale facts active, blindly append contradictory updates, or execute coarse cascading deletes.

GENE's long-term objective is to make **epistemic belief maintenance a first-class systems primitive for persistent artificial intelligence**.

An agent operating over durable memory must be able to answer five fundamental questions for any claim $c$:

| Kernel Query | Semantic Meaning | Classic Analogy |
| :--- | :--- | :--- |
| **`WHY(c)`** | What minimal support environments justify $c$? | ATMS Assumption Environments |
| **`WHENCE(c)`** | What causal provenance lineages produced those supports? | Database Provenance Semirings |
| **`WHAT_IF(c, a)`** | If source or assumption $a$ is retracted, does $c$ survive? | Non-Destructive Support Evaluation |
| **`THEN_WHAT(a)`** | If $a$ changes, which downstream beliefs, retrievals, and actions must be revised? | Self-Adjusting Dependency Recomputation |
| **`DID_YOU_ACTUALLY_USE(c, a)`** | Did the neural reasoner's output causally depend on $a$, or was $a$ merely cited / coincidental? | GENE Causal Intervention Engine |

```
                              THE EPISTEMIC RUNTIME ARCHITECTURE
                              
                             HUMAN / WORLD / TOOLS / SENSORS
                                            │
                                            ▼
                                    NEW OBSERVATIONS
                                            │
                                            ▼
                        ┌───────────────────────────────────────┐
                        │           EPISTEMIC KERNEL            │
                        │                                       │
                        │  • Provenance Semirings               │
                        │  • Minimal Support Sets S(c)          │
                        │  • Epistemic Cut Sets κ(c)            │
                        │  • Effective Diversity Neff           │
                        │  • Revision & Truth Maintenance       │
                        │  • Reproductive Admission             │
                        │  • Action Authority Gating            │
                        └───────────────────┬───────────────────┘
                                            │
                                 retrieve   │   propose candidate
                                 context    │   belief & certificate
                                            ▼   │
                                ┌───────────────────────┐
                                │ Neural Reasoner (LLM) │
                                └───────────────────────┘
                                            │
                                            ▼
                                   CANDIDATE OCCURRENCE
                                            │
                                     validate & commit
                                            │
                                            ▼
                                 PERSISTENT EPISTEMIC STATE
```

The neural model is free to propose candidate beliefs and intermediate inferences. **The model does not unilaterally define durable truth.** The Epistemic Kernel mediates memory admission, change propagation, and action authority.

---

## 2. Theoretical Ancestry: Connecting Four Traditions

GENE does not claim to have invented truth maintenance or provenance. Rather, GENE investigates **what belief maintenance must become when the reasoner is a stochastic neural network** operating over approximate retrieval, lossy semantic transformations, and self-referential generations.

```
                    THE FOUR INTELLECTUAL ANCESTORS OF GENE
                    
    ┌──────────────────────────────┐              ┌──────────────────────────────┐
    │ Truth Maintenance (TMS/ATMS) │              │  Database Provenance Theory  │
    │ (Doyle 1979, de Kleer 1986)  │              │ (Green, Karvounarakis 2007)  │
    │ • Justification networks     │              │ • Provenance semirings       │
    │ • Multiple assumption sets   │              │ • Polynomial derivations     │
    │ • Non-monotonic revision     │              │ • Alternative vs conjunctive │
    └──────────────┬───────────────┘              └──────────────┬───────────────┘
                   │                                             │
                   └──────────────────────┬──────────────────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │   GENE EPISTEMIC    │
                               │       RUNTIME       │
                               └──────────┬──────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
    ┌──────────────▼───────────────┐              ┌──────────────▼───────────────┐
    │  Self-Adjusting Computation  │              │ Modern Agent Memory Systems  │
    │    (Acar, Blelloch 2002+)    │              │  (2025–2026 Emerging Work)   │
    │ • Dynamic dependency graphs  │              │ • Supersede, STALE           │
    │ • Selective change replay    │              │ • MemTX, ChronoMem, TOKI     │
    │ • Minimal recomputation      │              │ • Correlated error / RAG div │
    └──────────────────────────────┘              └──────────────────────────────┘
```

### Why Classic Formalisms Break in Neural Persisted Memory:
1. **Reported Support $\ne$ Causal Influence:** In classic TMS, a logical rule guarantees deduction. In LLMs, a cited parent ID in output text does not prove the model actually utilized that parent to generate the token (Experiment 0).
2. **Local Correctness $\ne$ Global Truth:** A valid syllogism evaluated over corrupted premises produces locally derivable falsehoods (Experiment 1A).
3. **Nominal Diversity $\ne$ Epistemic Independence:** Five distinct documents in a vector database may all descend from a single corrupted upstream root (Exploration Round 1 Track B).
4. **Lineage Laundering:** Summarization and semantic paraphrasing strip provenance metadata, creating the illusion of de novo consensus (Phase 10.5).

---

## 3. The Mathematics of Multi-Justification Support

In a realistic memory ecology, a persistent claim $c$ is rarely a pure single-lineage leaf. It may possess multiple independent derivations.

### Minimal Epistemic Support Sets $S(c)$
Every durable claim $c$ is associated with a set of minimal sufficient ancestral premises:
$$S(c) = \{S_1, S_2, \dots, S_k\}$$
where each $S_i = \{a_{i,1}, a_{i,2}, \dots, a_{i,m}\}$ is an irredundant conjunctive set of root assumptions such that:
$$\bigwedge_{a \in S_i} a \implies c$$

Algebraically, the provenance polynomial is represented as:
$$P(c) = \sum_{i=1}^k \prod_{a \in S_i} a$$

### The Three Descendant Types Under Upstream Corruption
When an ancestor $A$ is discredited or mutated ($A \leadsto 0$):

1. **Pure Infected Descendant ($I \to X$):**
   $$P(X) = A \implies P(X)\mid_{A=0} = 0 \quad \text{(Quarantine / Invalidate)}$$
2. **Recombinant Conjunctive Descendant ($IH \to X$):**
   $$P(X) = A \cdot H \implies P(X)\mid_{A=0} = 0 \cdot H = 0 \quad \text{(Quarantine / Invalidate)}$$
3. **Multiply Supported Alternative Descendant ($IA + HB \to X$):**
   $$P(X) = A \cdot M_1 + H \cdot M_2 \implies P(X)\mid_{A=0} = 0 + H \cdot M_2 = H \cdot M_2 > 0 \quad \text{\textbf{(PRESERVE)}}$$

> [!IMPORTANT]
> **Non-Destructive Lineage Immunity:** A naive lineage quarantine deletes any node with an infected ancestor. Under multi-justification support, the Epistemic Kernel prunes the corrupted derivation path $A \cdot M_1$ while **preserving the active claim $X$** via its surviving healthy support path $H \cdot M_2$, preventing epistemic autoimmunity.

### Epistemic Cut Set Size $\kappa(c)$
We define the structural epistemic resilience of a belief:
$$\kappa(c) = \min_{C \subseteq \mathcal{A}} \{|C| : \forall S_i \in S(c), S_i \cap C \ne \emptyset\}$$
- $\kappa(c) = 1$: **Epistemically Fragile.** A single source failure or retraction eliminates all valid support.
- $\kappa(c) \ge 2$: **Epistemically Resilient.** Multiple independent ancestral retractions are required before the belief loses justification.

---

## 4. The Seven Invariants of an Epistemic Kernel

Analogous to the ACID properties in relational database transactions, an Epistemic Kernel enforces seven core invariants:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE SEVEN EPISTEMIC INVARIANTS                                  │
├──────────────────────────┬─────────────────────────────────────────────────────────────┤
│ 1. Provenance            │ A descendant cannot gain evidential authority merely by     │
│    Preservation          │ being summarized, repeated, or reformatted.                 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 2. Support Completeness  │ Every durable belief must possess at least one valid,       │
│    and Grounding         │ unretracted minimal support set in S(c).                    │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 3. Independent-Support   │ Ten repetitions descended from one observation do not       │
│    Accounting            │ constitute ten independent observations (Neff <= Nvisible). │
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

---

## 5. The Five Research Pillars

GENE organizes its multi-year experimental program across five foundational pillars:

```
                            THE FIVE PILLARS OF GENE
                            
       PILLAR 1: EPISTEMIC IDENTITY & PROVENANCE
       • Exposure vs report vs causal ancestry (Exp 0)
       • Semantic transformation & lineage tracking (Exp 1A)
       • Resistance to provenance laundering (Phase 10.5)
       
       PILLAR 2: EPISTEMIC SUPPORT & MULTI-JUSTIFICATION
       • Minimal support sets S(c) and provenance polynomials
       • Epistemic cut sets κ(c) and resilience
       • Effective sample size Neff vs nominal count (Track B)
       
       PILLAR 3: EPISTEMIC CHANGE & REVISION
       • Non-destructive correction (surviving path retention)
       • Lazy revalidation vs eager support-aware repair (Track A)
       • Temporal validity & explicit retraction handling
       
       PILLAR 4: EPISTEMIC REPRODUCTION & GOVERNANCE
       • Lineage immunity & selective quarantine (Exp 1B-C)
       • Structural proofreading & write certificates (Exp 1B-C2b)
       • Reproductive gating (R0 < 1 containment)
       
       PILLAR 5: EPISTEMIC ACTION AUTHORITY
       • Action eligibility as a function of support resilience κ(c)
       • Separation of working memory from external actuation
       • Conformance testing for autonomous persistent agents
```

---

## 6. What GENE Has Established vs What Remains Open

```
                                  GENE PROGRESSION MATRIX
                                  
    [ESTABLISHED & FROZEN]
    ├── Exp 0: Lineage Observability & Causal Interventions (P(active|complete)=1, P(active|broken)=0)
    ├── Exp 1A: Transitive Mutation Transmission across Multi-Generational Horn-DAGs
    ├── Exp 1B-A: Allele Fidelity & Critical Branching Extinction R0
    ├── Exp 1B-B: Endogenous Retrieval Dynamics (X_path) & Surface-Area Scaling Feedback
    ├── Exp 1B-C: Lineage Quarantine (Selectivity S=+0.800) vs Node-Only Laundering (S=0.000)
    └── Phase 10.5: Dual-Layer Governance (Lineage Immunity + Structural Proofreading Gate)
    
    [DISCOVERED IN EXPLORATION ROUND 1]
    ├── Stale-Descendant Hysteresis: Root overwrite alone leaves cached lemmas active (H_g=1.0)
    ├── Nominal Multiplicity Bias: Models count repetition unless independent roots are explicit
    ├── Measurement Non-Invariance: Prompts calibrated on 12B fail contracts on 3B models
    └── Measurement Kernel Law: "Parallelize the experiment, centralize the audit trail"
    
    [THE NEXT SCIENTIFIC HORIZON — EXPLORATION ROUND 2]
    ├── Multi-Justification Engine: Alternative vs conjunctive support algebras (AB + CD)
    ├── Non-Destructive Quarantine: Retaining valid claims during partial ancestor invalidation
    ├── Epistemic Sample Size Assay: Measuring Neff discounting under opaque root metadata
    └── Model Calibration Gateway: Conformance test suite across heterogeneous LLM families
```

---

## 7. Ten-Year Success Criteria

In ten years, GENE's success will not be measured by package download counts, but by whether the AI community treats belief maintenance as an indispensable systems requirement:

1. **Vocabulary:** AI architects routinely distinguish nominal memory occurrences from independent epistemic roots ($N_{\text{eff}}$).
2. **Runtime Governance:** Persistent agent frameworks evaluate minimal support sets $S(c)$ and cut sets $\kappa(c)$ before executing high-stakes actions or cascading deletions.
3. **Reproducibility Standard:** Autonomous agent benchmarks evaluate not only retrieval accuracy, but **revision correctness under upstream change**.
4. **Architectural Separation:** Systems cleanly separate the neural reasoner (a stochastic candidate generator) from the epistemic kernel (the deterministic provenance ledger).

> **Core Research Creed:**
> *Cheap deterministic measurement $\to$ tiny live mechanism test $\to$ adversarial review $\to$ only then scale.*
