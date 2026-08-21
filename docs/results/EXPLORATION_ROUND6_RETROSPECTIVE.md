# Exploration Round 6 Retrospective: The Epistemic Compiler & The Ingress Boundary

**Document Status**: Canonical Milestone Retrospective  
**Author**: Antigravity Research / GENE Core  
**Associated Milestones**:
- Stage 6A-v2: Bitemporal Supersession Algebra ([`round6-stage6a-v2-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round6-stage6a-v2-freeze))
- Stage 6B & 6B.1: Contract-Guided Adjudication & Multi-Update Ordering ([`round6-stage6b-master-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round6-stage6b-master-freeze))
- Stage 6C: Neural Observation Extraction & Fault Localization ([`round6-stage6c-execution-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round6-stage6c-execution-freeze), [`round6-stage6c-postreview-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round6-stage6c-postreview-freeze))
- Reports: [`EXPLORATION_ROUND6_STAGE6B_REPORT.md`](EXPLORATION_ROUND6_STAGE6B_REPORT.md), [`EXPLORATION_ROUND6_STAGE6C_REPORT.md`](EXPLORATION_ROUND6_STAGE6C_REPORT.md)

---

## 1. Executive Summary & Paradigm Shift

Exploration Round 6 marks a decisive turning point in the GENE research program. 

Going into Round 6, the central unsolved challenge of persistent AI memory appeared to be **state under change**: how an agent updates its internal beliefs when a fact is superseded, contradicted, expired, or reasserted, and how downstream entitlement and action authority evolve afterward.

Coming out of Round 6, the deterministic formal core of that problem is in a remarkably mature, mathematically grounded state:
1. **Bitemporality is Structurally Necessary**: Tracking Valid Time ($t_v$) and Knowledge Transaction Time ($t_k$) independently is essential for handling out-of-order, retroactive, and disputed assertions. Knowledge-Time Last-Write-Wins (KT-LWW) achieved only $33.3\%$ accuracy on multi-update streams; Valid-Time LWW (VT-LWW) achieved $75.0\%$; the GENE Bitemporal Engine achieved **$100.0\%$ ($12/12$)**.
2. **Transition Semantics Require Predicate-Aware Contracts**: State transitions (`ASSERT`, `SUPERSEDES`, `CONTRADICTS`, `RETRACT`, `EXPIRES`) cannot be inferred from raw recency or timestamps alone. They depend on ontology contracts: single-value replacement (`TIME_VARYING`), multi-value accumulation (`ADDITIVE`), event logging (`EPISODIC`), and bounded intervals (`INTERVAL_BOUNDED`).
3. **State Fidelity $\ne$ Support Fidelity**: Perfect premise state tracking is insufficient for correct reasoning. In Stage 6B, Arm 5 achieved $100\%$ transition and state fidelity, but suffered a **$36.0\%$ error rate** on downstream entitlement because flat dependency representations destroyed surviving support paths during partial invalidations.
4. **Epistemic Error Boundary Externalization (Fault Localization)**: Direct neural transition generation (Arm N1) collapses toward generic replacement heuristics (`SUPERSEDES` in 10/12 cases, $0/12$ valid batches). Modular observation extraction (Arm N2) localizes neural uncertainty strictly to Layer 0 (the extraction boundary), preventing downstream runtime corruption and eliminating runtime autoimmunity ($0/12$).
5. **The Symbol Realization Boundary**: Gemma 3:12B extracted temporal assertion intervals with **$100.0\%$ accuracy ($12/12$)**, but scored $8.3\%$ on exact canonical tuple extraction due to un-normalized entity strings (`"Auditor"` vs `Value_Auditor`). A deterministic normalization audit recovered **$11/12$ ($91.7\%$)** extraction fidelity, isolating the sole remaining error as semantic-role assignment (`C6C_03`, reporting sensor vs monitored entity).

The most consequential discovery of Round 6 is that **the remaining uncertainty has migrated from the kernel to the ingress boundary**:
$$\text{Fault Localization} \ne \text{Error Containment}$$
The deterministic kernel guarantees that no downstream derivation or revision errors will be introduced *after* a candidate is admitted, but it faithfully records whatever candidate is admitted. This shifts GENE's center of gravity from **Support Maintenance Under Change** to **Epistemic Ingress & Write Admission**: *What is allowed to become epistemic state in the first place?*

---

## 2. What We Thought Going In vs. What We Established Coming Out

| Dimension | Initial Assumption (Pre-Round 6) | Empirical Finding (Post-Round 6) |
|:---|:---|:---|
| **Temporal State** | Temporal recency is the primary state-tracking challenge. | Recency, valid time, and transition semantics are completely separate. KT-LWW, VT-LWW, and bitemporal state answer fundamentally different questions. |
| **Bitemporality** | Bitemporality is useful database bookkeeping. | Bitemporality is structurally necessary for crossed valid-time and knowledge-time histories (6B.1: KT-LWW 4/12, VT-LWW 9/12, Bitemporal 12/12). |
| **Update Semantics** | Once timestamps are known, updating memory is purely temporal. | The nature of a state update depends on predicate ontology contracts: replacement, accumulation, episodic logging, bounded intervals, and cautious conflict isolation. |
| **State vs Support** | If premise state is correct, downstream reasoning is preserved. | **False.** Arm 5 had 100% transition and state fidelity, but only 64% entitlement accuracy because flat dependency tracking caused 100% revision autoimmunity on alternative derivations. |
| **Occurrence Identity** | Occurrence identity is an implementation detail. | $\text{SemanticClaimIdentity} \ne \text{OccurrenceNodeIdentity}$ is essential; recurrence restores the same semantic proposition under an independent occurrence node with new provenance. |
| **Neural Transition Bridge** | The neural model might emit state-transition event batches directly. | **False.** Gemma exhibited a powerful spontaneous replacement bias, emitting `SUPERSEDES` across 10/12 cases and failing 100% of exact event batches. |
| **Observation Extraction** | Structured observation extraction is a single atomic interface. | Extraction decomposes into **mention understanding, semantic-role assignment, canonical symbol binding, temporal interval extraction, provenance attachment, and ingress admission**. |
| **Temporal Language** | The neural model will struggle most with complex temporal phrasing. | **Surprisingly false.** Start times and open-vs-bounded interval structures were extracted with **12/12 (100.0%) accuracy**. The bottleneck was object symbol binding (1/12). |
| **Error Containment** | Moving neural uncertainty outside the kernel contains the problem. | **False.** Fault localization isolates error origin to Layer 0, but does not contain a false candidate once admitted. $\text{Fault Localization} \ne \text{Error Containment}$. |

---

## 3. The Epistemic Compiler Paradigm

Round 6 revealed that GENE's architecture is isomorphic to a **formal compiler pipeline for epistemic state**.

In classical computer science, a compiler does not translate raw source text directly into CPU side effects:
$$\text{Source Text} \xrightarrow{\text{Parse}} \text{AST} \xrightarrow{\text{Name Resolution}} \text{Type Checking} \xrightarrow{\text{IR Optimization}} \text{Execution}$$

Direct neural memory mutation is analogous to asking a neural parser to read English and directly write machine code to random memory addresses. The mature GENE epistemic pipeline decomposes cleanly into seven compiler stages:

```
Natural Language Observation
      │
      ▼ (Stage 1: Neural Semantic Parsing)
Extracted Entity Mentions & Temporal Intervals
      │
      ▼ (Stage 2: Deterministic Ontology Binding / Linking)
Candidate Observation Tuple ⟨s, p, o, t_v,start, t_v,end⟩
      │
      ▼ (Stage 3: Ingress Validation & Ambiguity Gating)
Validated Structured Observation
      │
      ▼ (Stage 4: Contract-Guided State Adjudication)
Formal Transition Event Batch [ASSERT, SUPERSEDES, CONTRADICTS, RETRACT]
      │
      ▼ (Stage 5: Bitemporal Occurrence State Engine)
Active Premise State Records (t_v, t_k)
      │
      ▼ (Stage 6: Antichain Minimal Support Engine)
Epistemic Support S_tv(q | t_k) & Lineage S_L,tv(q | t_k)
      │
      ▼ (Stage 7: Lineage-Projected Action Governance)
Entitlement & Action Execution
```

In this compiler stack:
- **`PredicateContract`** acts as a formal type declaration.
- **Stage 6A Event Batches** serve as the intermediate representation (IR).
- **The Bitemporal Event Log** represents the committed runtime state.
- **The Missing Frontier** is name resolution, type checking, and write authorization prior to commit.

---

## 4. Convergence with Recent Research Literature

The conclusions of Round 6 are strongly corroborated by recent independent developments in AI memory, knowledge graphs, and provenance governance:

1. **STALE (2026)**: Evaluates LLM memory under state updates and finds that agents frequently retrieve updated information but fail to resolve state, resist stale premises, or adapt downstream policy (best system reached only 55.2%). This confirms GENE's thesis that **comprehension does not equal memory maintenance**.
2. **Supersede (2026)**: Demonstrates that the memory-update gap persists even when models have high full-context reasoning performance: 92% full-context accuracy drops to 77% under bounded self-maintained memory, and expanding context size does not recover the loss.
3. **Reliable Post-Retrieval Assembly (2026)**: Reports that isolating evidence extraction from policy execution accounts for the majority of freshness gains, directly validating GENE's separation of neural semantic extraction from deterministic state adjudication.
4. **SodaMem & Graph-Native Memory (2026)**: SodaMem represents typed `FactEvents` with provenance spans, mention time, occurrence time, and `SUPERSEDES`/`CONTRADICTS`/`UPDATES` relations. Graph-native architectures independently adopt immutable occurrence nodes and bitemporal intervals, converging on GENE's Stage 6A representation.
5. **Entity Linking & Constrained Decoding (Agnus, 2026)**: Shows that restricting entity decoding to candidate namespaces eliminates hallucinated identifiers and stabilizes candidate selection, supporting GENE's transition from free generation to candidate selection.
6. **Origin-Bound Authority & AuthMem-Bench (2026)**: Formalizes that summarization, tool echoes, and manufactured corroboration cause "authority collapse" unless write-time origin binding is enforced. This validates GENE's invariant that provenance and source metadata must be injected by the runtime rather than generated by the model.

---

## 5. The Three Open Frontiers ("The Three Dragons")

As GENE transitions to Round 7, the research roadmap identifies three primary open boundaries:

```
+========================================================================================================+
|                                    THE THREE DRAGONS OF PERSISTENT AI                                  |
+============================+===========================================================================+
| 1. Ingress Integrity       | How messy, ambiguous, authority-laden language becomes a canonical,       |
|    (Round 7 Mainline)      | authorized fact without silent binding, role, or authority errors.        |
+----------------------------+---------------------------------------------------------------------------+
| 2. Lineage Integrity       | Whether origin identities and independence classes can be trusted under   |
|    (Security Sidecar)      | multi-agent copying, summarization, Sybil attacks, and tool echoes.       |
+----------------------------+---------------------------------------------------------------------------+
| 3. Representation Scale    | How to preserve intervention-sufficient support hypergraphs without       |
|    (Systems Sidecar)       | exponential materialization in dense, multi-path dependency networks.    |
+============================+===========================================================================+
```

---

## 6. The Core Theoretical Distinction: Attestation vs Admitted Fact

The foundational realization emerging from Round 6 is the distinction between an **Attestation** and an **Admitted Fact**:

- **$\text{Exposure} \ne \text{Report} \ne \text{Causal Support}$** (Experiment 0).
- **$\text{OriginIdentity} \ne \text{DerivationLineage} \ne \text{IndependenceClass}$** (Experiments 1B-C & Stage 5B).
- **$\text{SemanticClaim} \ne \text{OccurrenceNode}$** (Stage 6A).
- **$\text{Attestation} \ne \text{AdmittedFact}$** (Round 6 Synthesis & Round 7 Foundation).

An **Attestation** is incontrovertible in a descriptive sense: *Source $S$ asserted proposition $P$ at time $t$*. However, that attestation does not automatically mean that $P$ is an active, authoritative fact in the world model. 

Before an attestation becomes an active `OccurrenceNode`, it must pass an explicit **Epistemic Write Admission Gate**:
$$\text{Attestation} \xrightarrow{\text{Extraction}} \text{Candidate} \xrightarrow[\text{Authority Gating}]{\text{Ontology Binding}} \text{AdmissionCertificate} \xrightarrow{} \{\text{ADMIT}, \text{AMBIGUOUS}, \text{NOVEL}, \text{REJECT}\}$$

This unifies the write-side structural proofreading from Experiment 1B-C2b with the semantic ingress bridge of Stage 6C into a single, comprehensive systems abstraction: **Epistemic Write Admission**.
