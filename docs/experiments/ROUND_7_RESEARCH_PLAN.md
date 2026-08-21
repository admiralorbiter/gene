# Exploration Round 7 Research Plan: Epistemic Ingress — Binding, Attestation & Write Admission

**Document Status**: Preregistered Research Specification & Architectural Plan (Wave 0.1 Hardened)  
**Author**: Antigravity Research / GENE Core  
**Associated Target Commit**: `round7-wave0-freeze`  
**Prerequisites**: Exploration Round 6 Post-Review Freeze ([`round6-stage6c-postreview-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round6-stage6c-postreview-freeze))  

---

## 1. Executive Research Problem & Foundational Scope

Following the completion of Round 6 (which established the deterministic core of bitemporal state adjudication, predicate contracts, and antichain support maintenance), the central scientific bottleneck of persistent AI has migrated from internal truth maintenance to the **neural-formal ingress boundary**:

> *What proof and authority must accompany incoming natural language information before persistent intelligence is allowed to believe it?*

Rather than allowing unconstrained neural generation to write directly to persistent memory, Round 7 establishes **Proof-Carrying Epistemic Write Admission**:
$$\text{SourceRecord} \xrightarrow[\text{Parsing}]{\text{Neural}} \text{ParsedAttestation} \xrightarrow[\text{Linking}]{\text{Deterministic}} \text{Binding Hypotheses } \mathcal{B}(x) \xrightarrow[\text{Validation}]{\text{Certificate}} \text{AdmissionGate} \xrightarrow{} \text{AdmittedFact}$$

---

## 2. Core Epistemic Invariants & Theoretical Foundations

### 2.1 The Three-Tier Ingress Incontrovertibility Hierarchy
$$\text{SourceRecord} \ne \text{ParsedAttestation} \ne \text{AdmittedFact}$$
1. **`SourceRecord`**: The immutable, incontrovertible historical event $\langle \text{raw\_span}, \text{authenticated\_origin\_id}, t_k \rangle$.
2. **`ParsedAttestation`**: The fallible syntactic and semantic claim that the raw record expresses proposition $\hat{P} = \langle s, p, o, [t_{v,\text{start}}, t_{v,\text{end}}) \rangle$.
3. **`AdmittedFact`**: The validated, authoritative world-model `OccurrenceNode` instantiated into active memory after passing the admission gate.

*Recoverability Invariant*: Preserving the immutable `SourceRecord` ensures that future improved semantic parsers or updated ontologies can re-evaluate original evidence without inheriting obsolete neural extraction errors.

### 2.2 Hypothesis Preservation over Ambiguity Collapse
$$\text{Preserve alternatives when future interventions may distinguish them}$$
- When a natural language mention admits multiple candidate bindings $\mathcal{B}(x) = \{b_1, \dots, b_k\}$ (e.g. `Server_1` vs `Server_1_Backup`), collapsing the state to an opaque `AMBIGUOUS` label performs a lossy, irreversible destruction of evidence.
- Round 7 establishes **Hypothesis Preservation**: unresolved writes are stored under status **`DEFERRED_BINDING`**, preserving the explicit candidate set $\mathcal{B}(x)$, source spans, and provenance constraints. Subsequent evidence can prune the candidate set without having discarded the hypothesis space.

### 2.3 Class-Relative Candidate Intervention-Sufficient Binding
> **Principle:** Two candidate bindings $b_i, b_j \in \mathcal{B}(x)$ are intervention-equivalent with respect to a frozen finite intervention family $\mathcal{I}_7$ if and only if:
> $$\forall \iota \in \mathcal{I}_7: \; \text{Response}(b_i, \iota) = \text{Response}(b_j, \iota)$$
- **Query-Scoped Equivalence ($b_i \equiv_{\mathcal{I}_7} b_j$)**: Allows temporary pragmatic resolution solely for answers evaluated under class $\mathcal{I}_7$.
- **Durable Identity Equivalence ($b_i = b_j$)**: Requires true ontology identity before instantiating a permanent, canonical `OccurrenceNode`.

### 2.4 Multidimensional Capability & Provenance (`SourceContext`)
$$\text{Authenticity} \ne \text{Reliability} \ne \text{Authorization Scope} \ne \text{Independence Class}$$
Authority at ingress cannot be represented as a scalar score ($1.0, 0.85, 0.30$). The runtime represents source context as a structured capability tuple:
$$\text{SourceContext} = \langle \text{Authenticity}, \text{AuthorizationScope}, \text{ReliabilityClass}, \text{IndependenceClass}, \text{ClaimType} \rangle$$
- An authenticated sensor is authorized to attest physical measurements within its declared domain, but possesses zero authorization to attest administrative roles.
- A direct user instruction may create an authoritative `PREFERENCE_NODE`, but cannot unilaterally establish third-party factual truth.
- **Source Authority Non-Amplification**: $\text{Authority}(\text{AdmittedFact}) \le \text{Authority}(\text{Origin})$.

### 2.5 Nested Admission Gates: Entity Admission $\ne$ Fact Admission
- Novel entities outside the current namespace must not be rejected outright, nor should they pollute the canonical ontology.
- Round 7 introduces **`PROVISIONAL_ENTITY`** (or `UNRESOLVED_ENTITY_MENTION`): preserving raw mention spans, temporal intervals, and provenance in a provisional namespace without assigning premature canonical database IDs.

### 2.6 Proof-Carrying Admission Certificates
The admission gate emits a structured, audit-verifiable certificate rather than an opaque boolean or enum:
- **`ADMIT`**: Carries $\langle \text{binding\_witness}, \text{schema\_witness}, \text{temporal\_witness}, \text{auth\_witness}, \text{lineage\_roots} \rangle$.
- **`DEFER`**: Carries $\langle \text{candidates\_remaining}, \text{failed\_constraint}, \text{evidence\_needed\_to\_resolve} \rangle$.
- **`REJECT`**: Carries $\langle \text{violation\_witness}, \text{rejection\_cause} \rangle$.

---

## 3. Comparative Deterministic Architectures (`A0` to `A4`)

To isolate the causal contribution of each ingress abstraction, the deterministic benchmark evaluates five distinct architectural arms:

| Architecture Arm | Ingress & Binding Policy | Authority & Validation Policy | Downstream Epistemic Runtime |
|:---|:---|:---|:---|
| **`A0: Always-Admit / Top-1`** | Binds top-1 lexical candidate; rejects novelty. | Blind admission (no authority or scope checks). | Single-clock Last-Write-Wins (LWW). |
| **`A1: Canonicalization-Only`** | Deterministic alias normalization; collapses ambiguity. | Blind admission. | Single-clock LWW. |
| **`A2: Candidate-Aware Gate`** | Preserves candidate set $\mathcal{B}(x)$; defers unresolved. | Blind admission. | Bitemporal Engine + Antichain Support. |
| **`A3: Authority-Aware Gate`** | Deterministic normalization. | Capability-scoped authorization checks. | Bitemporal Engine + Antichain Support. |
| **`A4: Full GENE Ingress`** | Hypothesis preservation ($\text{DEFERRED\_BINDING}$) + provisional entities. | Capability-scoped authorization + proof-carrying admission certificates. | Bitemporal Engine + Antichain Support + Action Governance. |

---

## 4. Benchmark Composition: 120-World Factorial Suite ($N=480$ Probes)

### 4.1 Factorial Grid ($4 \times 5 \times 3 \times 2 = 120$ Worlds)
1. **Predicate Modes (4)**: `TIME_VARYING`, `ADDITIVE`, `EPISODIC`, `INTERVAL_BOUNDED`.
2. **Binding Conditions (5)**:
   - `EXACT_CANONICAL`: Exact string match to canonical entity ID.
   - `SURFACE_ALIAS`: Normalizable lexical alias (e.g. `"Auditor"`, `"Transport Unit 3"`).
   - `CANDIDATE_COLLISION`: Two equally plausible entities in namespace (e.g. `Server_Node_1` vs `Server_Node_1_Backup`).
   - `ROLE_AMBIGUITY`: Reporter vs Subject confusion (e.g. `Sensor Alpha reported Server 1 degraded`).
   - `NOVEL_ENTITY`: Entity absent from candidate namespace.
3. **Temporal Relations (3)**: Forward Update, Retroactive Backfill, Contemporaneous Dispute.
4. **Source Role Forms (2)**: Direct Observation vs Attributed Third-Party Report.

### 4.2 The Strictly Formal Four-Probe Evaluation Protocol
All four probes are evaluated via formal state and algebraic queries ($0$ live LLM compute in deterministic phase):
- **$Q_1$ (Active State Probe)**: Does the active premise set $F(t_v \mid t_k)$ match canonical ground truth?
- **$Q_2$ (Structured Premise-Challenge Probe)**: Evaluates whether the runtime rejects a formal query asserting a stale or unadmitted premise:
  $$\text{Query}(q_{\text{stale}}) \implies \text{UNKNOWN / UNENTITLED}$$
- **$Q_3$ (Downstream Policy Action Probe)**: Does the action governance engine authorize the correct policy action based on lineage authority?
- **$Q_4$ (Causal Invalidation / WHAT_IF Probe)**: Under a formal `WHAT_IF(source=0)` ablation, do surviving derivations correctly persist?

Total Deterministic Evaluations: $120 \text{ worlds} \times 4 \text{ probes} = \mathbf{480 \text{ probe evaluations}}$.

---

## 5. Paired Authority Sidecar Assay ($\text{do}(\text{SourceClass} = s_i)$)

Following the AuthMem-Bench methodology, the authority sidecar isolates source authorization by holding the focal proposition $P$, valid time $t_v$, initial state, and query invariant while varying only $\text{SourceContext}$:
$$\text{do}(\text{SourceClass} \in \{\text{PLATFORM\_ATTESTED}, \text{USER\_DIRECT}, \text{THIRD\_PARTY\_QUOTED}, \text{MODEL\_DERIVED}\})$$
- Evaluates whether out-of-scope assertions (e.g. third-party sensor attempting to set user security clearances) are strictly blocked from achieving `ROOT_FACT` status.

---

## 6. Live Neural Assay: 3 Interfaces $\times$ 16 Hard Cases ($N=52$ Calls)

To evaluate neural candidate selection on pinned model `gemma3:12b` (digest `f4031aab...`), 16 stratified hard cases ($4 \text{ Modes} \times 4 \text{ Ingress Phenomena}$) are evaluated across three distinct interfaces:

| Arm | Interface Responsibility | Model Constraints & Counterbalancing |
|:---|:---|:---|
| **Arm N1: Free Generation** | Free generation of canonical entity IDs from scratch (Stage 6C baseline). | Open JSON generation. |
| **Arm N2: Candidate Selection** | Neural model extracts mention span, then selects from a prompt-supplied candidate set $\mathcal{B}(x) \cup \{\text{AMBIGUOUS}, \text{NOVEL}\}$. | Unconstrained JSON; candidate options **counterbalanced across 4 ordinal positions**. |
| **Arm N3: Constrained Selection** | Same candidate selection task, but model output is grammar-constrained to valid enum options. | Constrained grammar decoding; candidate options counterbalanced. |

Total Live Call Budget: $16 \text{ cases} \times 3 \text{ arms} + 4 \text{ replay canaries} = \mathbf{52 \text{ calls}}$.

---

## 7. Primary Evaluation Metrics

1. **Decomposed False Durable Admission Rate ($\text{FDAR}$)** (Primary Safety Metric):
   $$\text{FDAR} = \text{FDAR}_{\text{wrong-binding}} + \text{FDAR}_{\text{ambiguity-collapse}} + \text{FDAR}_{\text{novel-mislinking}} + \text{FDAR}_{\text{unauthorized-promotion}}$$
   *Optimization Constraint: $\mathbf{\text{FDAR} = 0.0\%}$ (Strictly Fail-Closed).*

2. **Safe Admission Coverage ($\text{SAC}$)**:
   $$\text{SAC} = P(\text{ADMIT}_{\text{correct}} \mid \text{Admissible Ground Truth})$$
   *Objective: Maximize $\text{SAC}$ subject to $\text{FDAR} = 0.0\%$.*

3. **Downstream 4-Probe Composite Accuracy**:
   $$\text{Acc}_{\text{4-Probe}} = \frac{1}{4} \left[ \text{Acc}(Q_1) + \text{Acc}(Q_2) + \text{Acc}(Q_3) + \text{Acc}(Q_4) \right]$$

4. **Replay Determinism Endpoint**:
   - Replay determinism is evaluated as an **empirical endpoint** across the 4 canaries under temperature $0.0$, seed $42$.

---

## 8. Preregistered Stopping Rules & Gating Invariants

1. **Deterministic Gate**: No live LLM calls may be executed until the 120-world deterministic benchmark achieves **$100.0\%$ oracle pass rate** on Arm A4 and **$\text{FDAR} = 0.0\%$**.
2. **Replay Empirical Reporting**: Replay stability is reported exactly as observed without selective retries.
3. **Holdout Validation**: The final architecture must be evaluated against external holdout scenarios derived from STALE and Supersede benchmarks before declaring the ingress layer mature.
