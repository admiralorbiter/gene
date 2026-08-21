# GENE Exploration Round 5 Retrospective: Truth Maintenance, Support Algebras, and the 2026 Epistemic Frontier

**Authors**: GENE Core Research Group  
**Date**: August 2026  
**Status**: Authoritative Scientific Positioning Memo  
**Document URI**: `docs/results/EXPLORATION_ROUND5_RETROSPECTIVE.md`  
**Reference Assays**: Exploration Round 5 (Stages 5A, 5B, 5C) & Experiments 0–1B-C2b

---

## Executive Abstract

Exploration Round 5 began with a focused operational question: *When an upstream premise changes, how should persistent AI memory revise downstream beliefs without either preserving invalidated falsehoods or destroying still-valid conclusions?*

Across three formal stages (432 cases in 5A, 368 cases in 5B, and 32 live model calls in 5C), the project decomposed belief maintenance under change into four distinct layers:
1. **Representation**: Flat dependency sets fail to represent alternative reasons, causing $100\%$ revision autoimmunity under degradation.
2. **Neural Boundary**: Real language models fail to resolve support boundaries accurately under perturbation, displaying both false retention ($F^+$) on broken paths and false retraction ($F^-$) on surviving paths.
3. **Provenance**: Nominally distinct multi-path supports can secretly share the same ancestral vulnerability, requiring antichain-minimized lineage-projected hypergraphs $\mathcal{S}_L(c)$.
4. **Action Governance**: Logical belief entitlement ($\mathcal{S}' \ne \emptyset$) is operationally distinct from action authorization ($\text{Auth}(\mathcal{S}_L') \ge \tau$).

This memo synthesizes what Round 5 established, anchors GENE in classical AI foundations (de Kleer's ATMS, database provenance semirings, AGM belief revision, and causal abstraction), connects its findings to the emerging 2026 agent memory literature (STALE, Memora, MOSAIC, and origin-bound memory authority), introduces the **Support-Boundary Resolution ($SBR$)** metric, and formulates the core thesis for modern persistent AI architecture.

---

## 1. The Core Research Thesis

Classical AI assumed an idealized interface: the reasoning engine produced sound, minimal justifications and handed them reliably to an external truth maintenance system. Modern neural agent research frequently makes the opposite assumption: the language model itself can dynamically manage, retrieve, and self-correct its own persistent memory stream.

Round 5 demonstrates that both assumptions fail in practice:
- The neural model cannot be trusted to reconstruct the exact support boundary every time it is prompted under change.
- A lossy deterministic memory policy (such as flat dependency tracking) is even more catastrophic, because it executes its representational errors with deterministic perfection ($0/4$ retention on degraded states).

This leads to the foundational thesis of GENE:

> ### The Central Architectural Thesis of GENE
> **Neural systems are powerful proposers of semantic conclusions but unreliable custodians of their own epistemic state. Persistent artificial intelligence therefore requires an external, intervention-sufficient truth-maintenance layer that preserves minimal support and causal provenance across change.**

```
                               THE EPISTEMIC INTERFACE
                               
        +-------------------------------------------------------------+
        |                 Neural Semantic Reasoner                    |
        |   * Flexible synthesis across natural language evidence     |
        |   * Proposes candidate beliefs and semantic answers         |
        |   * Unreliable at exact support boundary resolution (SBR)   |
        +------------------------------+------------------------------+
                                       | Proposals & Evidence Emitted
                                       v
        +-------------------------------------------------------------+
        |                  Epistemic Interface Layer                  |
        |   * Separates authoritative support S_F(c) from process R(c)|
        |   * Extracts minimal entitling premise environments         |
        |   * Antichain minimization & lineage projection S_L(c)      |
        +------------------------------+------------------------------+
                                       | Verified Support & Lineage
                                       v
        +-------------------------------------------------------------+
        |                 Persistent Truth Maintenance                |
        |   * Tracks temporal validity V_t and implicit supersession  |
        |   * Non-destructive belief revision under change (do(x=0))  |
        |   * Governs downstream retrieval context & action gating    |
        +-------------------------------------------------------------+
```

---

## 2. Classical AI Foundations: Reclaiming Prior Art

Rather than presenting support algebra as a de novo mathematical invention, GENE's strength lies in bringing mature, classical formalisms to bear on the messy interface of modern neural models.

```
+========================================================================================================================+
|                                    CLASSICAL FOUNDATIONS & GENE MAPPINGS                                               |
+================================+================================+======================================================+
| Classical Literature           | Foundational Contribution      | GENE Specialization & Neural Interface Mapping      |
+================================+================================+======================================================+
| Assumption-Based Truth         | De Kleer (1986): Every fact    | GENE's minimal support family S(c) = {S_1, ..., S_k} |
| Maintenance Systems (ATMS)     | carries a label of sound,      | corresponds to an ATMS label with antichain          |
|                                | complete, and minimal (under   | minimization, constructed over neural memory nodes.  |
|                                | set inclusion) environments.   |                                                      |
+--------------------------------+--------------------------------+------------------------------------------------------+
| Database Provenance            | Green, Karvounarakis, Tannen   | GENE provenance polynomials P(c) = ∑ ∏ a treat       |
| Semirings                      | (2007): (K, +, ·, 0, 1)        | conjunctions as product and alternative derivations   |
|                                | semirings where · represents   | as addition, enabling exact algebraic invalidation.  |
|                                | conjunctive dependency and +   |                                                      |
|                                | represents alternative paths.  |                                                      |
+--------------------------------+--------------------------------+------------------------------------------------------+
| AGM Belief Revision            | Alchourrón, Gärdenfors,        | Stage 5A validates the AGM contraction postulate of  |
| Postulates                     | Makinson (1985): Contraction   | recovery/minimality: invalidation of premise D must  |
|                                | should preserve as much of the | retain belief C if an alternative path AB survives.  |
|                                | prior belief state as possible.|                                                      |
+--------------------------------+--------------------------------+------------------------------------------------------+
| Causal & State Abstraction     | Beckers & Halpern (2019);      | Intervention-Sufficiency Principle: An epistemic     |
|                                | Li, Walsh, Littman (2006):     | representation is sufficient relative to the class   |
|                                | Compress state only when all   | of premise revisions (S) and root revisions (S_L)    |
|                                | causal interventions hold.     | the runtime must support without behavioral error.   |
+================================+================================+======================================================+
```

### 2.1 ATMS and Antichain Minimization
In de Kleer's 1986 formulation, the ATMS tracks dependency networks where propositions are tied to sets of assumptions. A label must satisfy four properties:
1. **Soundness**: The proposition is logically derivable from each environment in the label.
2. **Completeness**: Every environment from which the proposition is derivable is a superset of some environment in the label.
3. **Consistency**: No environment in the label is known to be inconsistent (nogood).
4. **Minimality**: No environment in the label is a strict superset of another environment in the label.

GENE's support family $\mathcal{S}(c)$ and lineage-projected family $\mathcal{S}_L(c)$ directly instantiate this structure:
$$\mathcal{S}_L(c) = \min_{\subseteq} \{ \{ \mathcal{L}(p) : p \in S_i \} : S_i \in \mathcal{S}(c) \}$$
Stage 5B proved that omitting strict subset pruning after projection creates phantom authority and violates governance monotonicity.

### 2.2 Provenance Polynomials
Database provenance semirings (Green et al., 2007) model query derivations by assigning provenance annotations. For a commutative semiring $(K, +, \cdot, 0, 1)$, conjunctive join queries compute products ($A \cdot B$), while union queries compute sums ($AB + DE$). Under partial premise invalidation $\text{do}(D=0)$, evaluation on the semiring yields:
$$P(c)\mid_{D=0} = (A \cdot B) + (0 \cdot E) = A \cdot B > 0$$
This cleanly formalizes why flat dependency graphs ($R(c) = A \cup B \cup D \cup E$) fail: they collapse the polynomial sum into a single monolithic product $A \cdot B \cdot D \cdot E$, making any single deletion annihilate the entire state ($0 \cdot B \cdot D \cdot E = 0$).

---

## 3. Adjacent 2026 Memory Literature: Where GENE Sits

The year 2026 has witnessed a major pivot in AI agent memory benchmarks away from static retrieval recall toward dynamic state evolution, mutation, and staleness:

```
+========================================================================================================================+
|                                    MODERN 2026 MEMORY BENCHMARKS VS GENE                                               |
+================================+================================+======================================================+
| 2026 Benchmark / System        | Core Focus                     | How GENE Differs & Extends Beyond                    |
+================================+================================+======================================================+
| STALE (May 2026)               | Evaluates resistance to stale  | STALE evaluates whether an agent picks the latest    |
|                                | premises, state resolution,    | fact. GENE asks *what formal derivational structure  |
|                                | and policy adaptation. Best    | entitled the belief, and which alternative support   |
|                                | agent achieved only 55.2%.     | environments survive upstream change*.               |
+--------------------------------+--------------------------------+------------------------------------------------------+
| Memora (April 2026)            | Tests memory mutation across   | Memora introduces a forgetting penalty for reusing   |
|                                | 4 LLMs and 6 memory agents.    | obsolete facts. GENE provides the algebraic runtime  |
|                                | Finds severe reuse of invalid  | that computes exact non-destructive revision without |
|                                | memories and weak reconciliation.| reliance on model self-reporting.                  |
+--------------------------------+--------------------------------+------------------------------------------------------+
| MOSAIC (May 2026)              | Structured graph memory with   | MOSAIC uses graph heuristics to detect conflicts.    |
|                                | explicit conflict detection to | GENE uses exact antichain support hypergraphs and    |
|                                | prevent silent contradiction   | causal lineage projection to gate external actions.  |
|                                | accumulation.                  |                                                      |
+--------------------------------+--------------------------------+------------------------------------------------------+
| Origin-Bound Memory Authority  | Analyzes derivational lineage  | Identifies that lineage itself can be forged or      |
| & Provenance Guardrails (2026) | laundering through summaries,  | laundered. Sets the stage for GENE's Lineage         |
|                                | tool echoes, and re-writes.    | Integrity threat matrix and write-time certificates. |
+================================+================================+======================================================+
```

---

## 4. Support-Boundary Resolution ($SBR$): A Unified Metric

Stage 5C resolved an apparent paradox in neural memory research. Earlier GENE experiments (Exp 1B-C2) found that models often hallucinate derivations from broken evidence ($F^+ > 0$). Stage 5C found the reverse: when unassisted models face retraction notices, they frequently become over-conservative and falsely abandon intact beliefs ($F^- > 0$).

The underlying phenomenon is not a simple bias toward credulity or skepticism, but **poor support-boundary resolution**: the neural reasoner struggles to locate the precise logical boundary between what is entitled and what is invalidated.

We formalize this with two complementary error rates:

1. **False Expression Rate ($F^+$)**:
   $$F^+ = P(\text{ACTIVE} \mid \text{RETRACTED})$$
   *(Model claims a conclusion is true when all formal support paths have been severed; hallucinated derivation / pseudo-path).*

2. **False Retraction Rate ($F^-$)**:
   $$F^- = P(\text{UNKNOWN} \mid \text{DEGRADED})$$
   *(Model abandons a conclusion when at least one formal support path remains intact; over-abstention / revision paralysis).*

3. **Support-Boundary Resolution ($SBR$)**:
   $$\text{SBR} = \frac{1}{2} \left[ P(\text{ACTIVE} \mid \text{DEGRADED}) + P(\text{UNKNOWN} \mid \text{RETRACTED}) \right] = 1 - \frac{F^+ + F^-}{2}$$

```
+===================================================================================================+
|                                SUPPORT-BOUNDARY RESOLUTION (SBR)                                  |
+================================+========================+=======================+==================+
| Runtime Condition              | False Retention (F+)   | False Retraction (F-) | Overall SBR      |
+================================+========================+=======================+==================+
| Raw Gemma 3:12B (Arm 1)        | 0.0% (0/4)             | 50.0% (2/4)           | 75.0%            |
| Naïve Reported Policy (Arm 2)  | 0.0% (0/4)             | 100.0% (4/4)          | 50.0%            |
| GENE Epistemic Kernel (Arm 3)  | 0.0% (0/4)             | 0.0% (0/4)            | 100.0%           |
+================================+========================+=======================+==================+
```

---

## 5. Rich Citation Typology: $R(c)$ Belongs in the Audit Layer

Stage 5C produced a definitive empirical classification of self-reported citation vectors $R(c)$ emitted by `gemma3:12b`:

1. **Overcomplete / Explanatory Bloat ($W_{\text{IND}}, W_{\text{SHO}}$)**: $R(c) = \{A, B, D, E\}$. Cites all salient evidence across multiple paths. If stored as a flat dependency graph, invalidating $D$ destroys the belief despite surviving path $AB$.
2. **Undercomplete / Insufficient ($W_{\text{SHP}}$)**: $R(c) = \{A\}$. Cites only the shared root premise, which is insufficient on its own to form a valid Horn derivation.
3. **Single Exact Witness ($W_{\text{REC}}$)**: $R(c) = \{A, B\}$. Locally minimal and sound, but globally incomplete because it ignores alternative paths ($BC, CD$), blinding downstream memory to surviving support when $A, B$ are retracted.

### The Architectural Separation Rule:
> **Neural citations $R(c)$ belong strictly in the process telemetry and explanation layer.** Authoritative belief maintenance must rely on dynamically evaluated, antichain-minimized formal support $\mathcal{S}_F(c)$ compiled by the Epistemic Kernel.

```
       Context E(c) --> Neural Reasoner --> Explanation R(c) [TELEMETRY / AUDIT ONLY]
            |
            v
       Epistemic Kernel --> Minimal Support S_F(c) --> Lineage Hypergraph S_L(c) [AUTHORITATIVE STATE]
```

---

## 6. The Two Looming Frontiers (Known Dragons)

As GENE advances from micro-world mechanism isolation to larger ecologies, two major challenges define the research roadmap:

### Dragon 1: Lineage Integrity & Provenance Laundering
GENE currently assumes that recorded lineage $\mathcal{L}(p)$ is authentic. Recent 2026 security literature demonstrates that adversarial actors or uncalibrated summarization tools can easily launder untrusted claims through:
- **Summarization compression**: Dropping intermediate provenance tags.
- **Trusted-tool echoes**: Passing an unverified premise through a trusted calculator or formatter to inherit a synthetic root ID.
- **Manufactured corroboration**: Creating artificial multi-path structures by cross-citing ungrounded claims.

*Roadmap Response*: Develop write-time cryptographic origin binding and tamper-evident lineage chains.

### Dragon 2: ATMS Support-Family Combinatorial Explosion
In de Kleer's classic ATMS, the number of minimal assumption environments in a label can grow exponentially with graph depth and branching ($O(2^n)$ in worst-case bipartite matching). While GENE's micro-worlds have operated safely within small envelopes ($k \le 4$), scaling to thousands of multi-agent beliefs requires mapping the exact boundary where exact antichain minimization remains computationally tractable.

---

## 7. Systematic Positioning Matrix

```
+========================================================================================================================+
|                                    GENE COMPREHENSIVE POSITIONING MATRIX                                               |
+================================+================================+======================================================+
| Category                       | Concept / Mechanism            | Scientific Status & Positioning                      |
+================================+================================+======================================================+
| **Classical AI Foundations**   | ATMS Labels & Antichains       | Classical foundation (de Kleer 1986).                |
|                                | Provenance Semirings           | Classical foundation (Green et al. 2007).            |
|                                | AGM Contraction Minimality     | Classical foundation (Alchourrón et al. 1985).       |
|                                | Causal & State Abstraction     | Theoretical foundation (Beckers & Halpern 2019).     |
+--------------------------------+--------------------------------+------------------------------------------------------+
| **Modern 2026 Adjacent Work**  | Stale Memory Invalidation      | Explored by STALE & Memora (2026). GENE adds exact   |
|                                |                                | derivational support algebra.                        |
|                                | Structured Graph Memory        | Explored by MOSAIC (2026). GENE adds causal lineage  |
|                                |                                | projection and action authority thresholds.          |
|                                | Lineage Laundering Threats     | Explored in agent provenance security (2026).        |
+--------------------------------+--------------------------------+------------------------------------------------------+
| **GENE Empirical Discoveries** | Support-Boundary Resolution    | Empirical finding: models fail at both F+ and F-.    |
|                                | Revision Autoimmunity          | Disproved flat dependency tracking: 100% false       |
|                                |                                | retractions on degraded states (Stage 5A).           |
|                                | Shared-Origin Masquerade       | Disproved scalar/tuple metrics (Stage 5B).           |
|                                | Dual-Layer Action Containment  | Empirical demonstration: Entitlement != Auth (5C).   |
+--------------------------------+--------------------------------+------------------------------------------------------+
| **Open Frontiers**             | Implicit Supersession Algebra  | Exploration Round 6 mainline (Stage 6A).             |
|                                | Exact Support Scale Envelope   | Deterministic profiling of ATMS label growth.        |
|                                | Adversarial Lineage Integrity  | Origin-bound memory certificates under attack.       |
+================================+================================+======================================================+
```

---

## 8. Transition to Exploration Round 6

With Stage 5C frozen and fully audited, GENE transitions directly to **Exploration Round 6: State Under Change (Implicit Supersession, Temporal Validity, and Downstream Entitlement)**.

Instead of receiving artificial, pre-classified retraction signals (`do(D=0)`), Round 6 asks how an epistemic runtime can deduce temporal validity when change arrives as new information (`"I moved to Chicago"` superseding `"My commute from Kansas City is 20 minutes"`), maintaining downstream entitlement without leaving zombies or triggering revision autoimmunity.
