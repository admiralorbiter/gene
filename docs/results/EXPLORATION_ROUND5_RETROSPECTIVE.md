# GENE Exploration Round 5 Retrospective: Truth Maintenance, Support Algebras, and the 2026 Epistemic Frontier

**Authors**: GENE Core Research Group  
**Date**: August 2026  
**Status**: Authoritative Scientific Positioning Memo (v2)  
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

This memo synthesizes what Round 5 established, anchors GENE in classical AI foundations (de Kleer's ATMS, database provenance semirings, AGM belief revision intuitions, and causal abstraction), connects its findings to the emerging 2026 agent memory literature (STALE, Memora, MOSAIC, Supersede, SodaMem, and bitemporal stores), introduces the **Support-Boundary Resolution ($SBR$)** metric, and formulates the core thesis for modern persistent AI architecture.

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
                               THE EPISTEMIC INTERFACE STACK
                               
        +-------------------------------------------------------------+
        |                 Neural Semantic Reasoner                    |
        |   * Flexible synthesis across natural language evidence     |
        |   * Proposes candidate beliefs and semantic answers         |
        |   * Unreliable at exact support boundary resolution (SBR)   |
        +------------------------------+------------------------------+
                                       | Candidate Propositions & Citations
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
        |               Support Minimizer & Lineage Kernel            |
        |   * Extracts formal minimal S_F(c); routes R(c) to telemetry|
        |   * Antichain minimization & lineage projection S_L(c)      |
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
| Belief Revision & Contraction  | Alchourrón, Gärdenfors,        | Stage 5A operationalizes the minimal-change /        |
| Intuitions                     | Makinson (1985); Hansson       | relevance intuition: removal of an invalidated       |
|                                | (1999): Contraction should not | premise must not remove independently supported      |
|                                | remove unrelated consequences. | consequences that possess surviving derivations.     |
+--------------------------------+--------------------------------+------------------------------------------------------+
| Causal Abstraction             | Beckers & Halpern (2019):      | Intervention-Sufficiency Principle: An epistemic     |
|                                | High-level causal models must  | representation is sufficient relative to the class   |
|                                | commute with interventions on  | of premise revisions (S) and root revisions (S_L)    |
|                                | the underlying micro-system.   | the runtime must support without behavioral error.   |
+--------------------------------+--------------------------------+------------------------------------------------------+
| Decision-Theoretic State       | Li, Walsh, Littman (2006):     | Preserving exact hypergraphs S_L(c) rather than      |
| Abstraction                    | Compression must preserve the  | lossy scalar/tuple summaries (kappa, rho) ensures   |
|                                | value function of all policies.| action authority remains monotone under revision.    |
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

The year 2026 has witnessed a major pivot in AI agent memory benchmarks away from static retrieval recall toward dynamic state evolution, mutation, staleness, and bitemporal validity:

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
| Supersede (June 2026)          | Tests knowledge-update main-   | Demonstrates that memory maintenance is distinct     |
|                                | tenance in LongMemEval. Bounded| from update understanding (performance drops from    |
|                                | self-maintenance drops 92%->77%| 92% to 77%). GENE externalizes this maintenance      |
|                                | even with more context.        | into a formal truth-maintenance layer.               |
+--------------------------------+--------------------------------+------------------------------------------------------+
| Memora (April 2026)            | Tests memory mutation across   | Memora introduces a forgetting penalty for reusing   |
|                                | 4 LLMs and 6 memory agents.    | obsolete facts. GENE provides the algebraic runtime  |
|                                | Finds severe reuse of invalid  | that computes exact non-destructive revision without |
|                                | memories and weak reconciliation.| reliance on model self-reporting.                  |
+--------------------------------+--------------------------------+------------------------------------------------------+
| Reliable Post-Retrieval        | Shows separating evidence      | Independently validates GENE's architecture:         |
| Assembly (2026)                | extraction from policy         | neural proposal -> structured state -> deterministic |
|                                | execution resolves conflicts.  | policy gating.                                       |
+--------------------------------+--------------------------------+------------------------------------------------------+
| SodaMem & Bitemporal Stores    | Separates mention time, occur- | GENE extends bitemporal validity (t_v x t_k) to      |
| (July - August 2026)           | rence time, and validity window| multi-hop derivational support hypergraphs S_{t_v}(c)|
|                                | under updates and conflicts.   | and lineage-projected action governance.             |
+================================+================================+======================================================+
```

---

## 4. Support-Boundary Resolution ($SBR$): Balanced Epistemic Accuracy

Stage 5C resolved an apparent paradox in neural memory research. Earlier GENE experiments (Exp 1B-C2) found that models often hallucinate derivations from broken evidence ($F^+ > 0$). Stage 5C found the reverse: when unassisted models face retraction notices, they frequently become over-conservative and falsely abandon intact beliefs ($F^- > 0$).

The underlying phenomenon is not a simple bias toward credulity or skepticism, but **poor support-boundary resolution**: the neural reasoner struggles to locate the precise logical boundary between what is entitled and what is invalidated.

Mathematically, $SBR$ represents **balanced accuracy** across the two complementary support-boundary error classes:

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
- **Root Splitting & Merging**: Artificially inflating or deflating cut-set resilience $\kappa_L$.

### Dragon 2: ATMS Support-Family Combinatorial Explosion
In de Kleer's classic ATMS, the number of minimal assumption environments in a label can grow exponentially with graph depth and branching (maximal antichain bounds $\binom{N}{N/2}$). The runtime must empirically profile exact scale envelopes and define principled approximation thresholds.

---

## 7. Transition to Exploration Round 6

With Stage 5C frozen, GENE transitions directly to **Exploration Round 6: State Under Change (Implicit Supersession, Temporal Validity, and Downstream Entitlement)**.

The GENE-specific contribution is **support-propagating temporal adjudication**: determine which state changed, preserve alternative derivations, propagate validity through derived beliefs, preserve provenance, and independently govern action.
