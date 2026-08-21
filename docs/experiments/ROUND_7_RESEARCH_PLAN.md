# Exploration Round 7 Research Plan: Epistemic Ingress — Binding, Attestation & Write Admission

**Document Status**: Preregistered Research Specification & Architectural Plan (Wave 0.2 Master Freeze)  
**Author**: Antigravity Research / GENE Core  
**Associated Target Commit**: `round7-wave0-freeze`  
**Prerequisites**: Exploration Round 6 Post-Review Freeze ([`round6-stage6c-postreview-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round6-stage6c-postreview-freeze))  

---

## 1. Executive Research Problem & Foundational Scope

Following the completion of Round 6 (which established the deterministic core of bitemporal state adjudication, predicate contracts, and antichain support maintenance), the central scientific bottleneck of persistent AI has migrated from internal truth maintenance to the **neural-formal ingress boundary**:

> *What proof, authority, and referential guarantees must accompany incoming natural language information before persistent intelligence is allowed to believe it?*

Rather than allowing unconstrained neural generation to write directly to persistent memory, Round 7 establishes **Proof-Carrying Epistemic Write Admission**:
$$\text{SourceRecord} \xrightarrow[\text{Parsing}]{\text{Neural}} \text{ParsedAttestation} \xrightarrow[\text{Linking}]{\text{Deterministic}} \text{Binding Hypotheses } \mathcal{B}(x) \xrightarrow[\text{Validation}]{\text{Certificate}} \text{AdmissionGate} \xrightarrow{} \text{AdmittedFact}$$

---

## 2. Core Epistemic Invariants & Theoretical Foundations

### 2.1 The Epistemic Alternative-Preservation Principle
> **Universal Architecture Law:**
> *Whenever unresolved alternatives may induce divergent future intervention responses, an epistemic runtime must preserve their structure until sufficient evidence justifies collapse.*
> - **Round 5 (Derivational Symmetry)**: Preserves alternative derivational support paths ($\mathcal{S}(c)$) so that invalidating one path does not falsely extinguish an independently supported fact.
> - **Round 7 (Referential Symmetry)**: Preserves alternative referential bindings ($\mathcal{B}(x)$) under **`DEFERRED_BINDING`** so that subsequent disambiguating evidence can prune hypotheses without having lost the hypothesis space.

### 2.2 The Three-Tier Ingress Incontrovertibility Hierarchy
$$\text{SourceRecord} \ne \text{ParsedAttestation} \ne \text{AdmittedFact}$$
1. **`SourceRecord`**: The immutable, incontrovertible historical event:
   $$\text{SourceRecord} = \langle \text{raw\_span}, \text{CaptureProvenance}, \text{ClaimedOrigin}, \text{AuthenticatedOrigin}, t_k \rangle$$
   - Distinguishes what the platform observed (`CaptureProvenance`) from what the content claims (`ClaimedOrigin`) vs cryptographically verified identity (`AuthenticatedOrigin`).
2. **`ParsedAttestation`**: The fallible syntactic and semantic claim that the raw record expresses proposition $\hat{P} = \langle s, p, o, [t_{v,\text{start}}, t_{v,\text{end}}) \rangle$.
3. **`AdmittedFact`**: The validated, authoritative world-model `OccurrenceNode` instantiated into active memory after passing the admission gate.

*Recoverability Invariant*: Preserving the raw `SourceRecord` ensures that future improved semantic parsers or updated ontologies can re-evaluate original evidence without inheriting obsolete neural extraction errors.

### 2.3 Class-Relative Candidate Intervention-Sufficient Binding
> **Principle:** Two candidate bindings $b_i, b_j \in \mathcal{B}(x)$ are intervention-equivalent with respect to a frozen finite intervention family $\mathcal{I}_7$ if and only if:
> $$\forall \iota \in \mathcal{I}_7: \; \text{Response}(b_i, \iota) = \text{Response}(b_j, \iota)$$

The frozen finite intervention family $\mathcal{I}_7$ consists of four orthogonal runtime queries:
- **$\iota_1$ (Active State Evaluation)**: Evaluate active premise set $F(t_v \mid t_k)$ at temporal coordinate $(t_v, t_k)$.
- **$\iota_2$ (Structured Premise Challenge)**: Formal query testing whether a contradictory/stale candidate is admitted.
- **$\iota_3$ (Action Policy Authorization)**: Policy authorization threshold evaluation under lineage projection $\text{Auth}(S_L)$.
- **$\iota_4$ (Causal Invalidation / WHAT_IF)**: Counterfactual parent ablation $\text{do}(\text{source} = 0)$ and alternative path survival.

**Equivalence Distinctions**:
- **Query-Scoped Equivalence ($b_i \equiv_{\mathcal{I}_7} b_j$)**: Allows temporary pragmatic resolution solely for answers evaluated under class $\mathcal{I}_7$.
- **Durable Identity Equivalence ($b_i = b_j$)**: Requires true ontology identity before instantiating a permanent, canonical `OccurrenceNode`.

### 2.4 Multidimensional Capability & Provenance (`SourceContext`)
$$\text{Authenticity} \ne \text{Reliability} \ne \text{Authorization Scope} \ne \text{Independence Class}$$
Authority at ingress cannot be represented as a scalar score ($1.0, 0.85, 0.30$). The runtime represents source context as a structured capability tuple:
$$\text{SourceContext} = \langle \text{Authenticity}, \text{AuthorizationScope}, \text{ReliabilityClass}, \text{IndependenceClass}, \text{ClaimType} \rangle$$

**Typed Non-Amplification Invariants**:
1. **Scope Confinement**: $\text{AuthorizationScope}_{\text{out}} \subseteq \text{AuthorizationScope}_{\text{origin}}$ (unless an explicit elevation certificate exists).
2. **Origin Preservation**: $\text{OriginIdentity}_{\text{out}} = \text{OriginIdentity}_{\text{source}}$ (preserving derivation edges).
3. **Independence Preservation**: $\text{IndependenceClass}$ cannot be promoted or amplified through summarization or copying.
4. **Reliability Calibration**: $\text{Reliability}$ may only be upgraded by a declared multi-witness corroboration procedure.

### 2.5 Operational Semantics of `PROVISIONAL_ENTITY` (Nested Write Gates)
$$\text{Entity Admission} \ne \text{Fact Admission}$$
When a novel entity is encountered outside the canonical ontology:
- **Allowed Operations**: Can accumulate attestations, candidate mentions, and provisional relations; can be retrieved for clarification and disambiguation.
- **Forbidden Operations**: **Cannot** acquire independent action authority; **cannot** participate as a canonical root fact.
- **Promotion Rule**: Promotion ($\text{ProvisionalEntity} \to \text{CanonicalEntity}$) must preserve all original `SourceRecord` provenance and *cannot* create a fresh independence root.

### 2.6 Proof-Carrying Admission Certificates & Independent Verifier
The admission gate emits a structured, audit-verifiable certificate:
- **`ADMIT`**: Carries $\langle \text{binding\_witness}, \text{schema\_witness}, \text{temporal\_witness}, \text{auth\_witness}, \text{lineage\_roots} \rangle$.
- **`DEFER`**: Carries $\langle \text{candidates\_remaining}, \text{failed\_constraint}, \text{evidence\_needed\_to\_resolve} \rangle$.
- **`REJECT`**: Carries $\langle \text{violation\_witness}, \text{rejection\_cause} \rangle$.

**Independent Verifier Contract**:
$$\text{CertificateVerifier}(\text{SourceRecord}, \text{Ontology}, \text{CapabilityPolicy}, \text{Certificate}) \to \{\text{VALID}, \text{INVALID}\}$$
- The verifier is pure, lightweight, and tested against deterministic certificate mutations to guarantee that invalid or forged certificates fail closed.

---

## 3. Unconfounded Comparative Architectures (`A0` to `A4`)

To isolate the causal contribution of each ingress abstraction, **all arms feed the identical frozen Round 6 downstream runtime**:
$$\text{IngressPolicy} \to \text{BitemporalEngine} \to S_{t_v}(q \mid t_k) \to S_{L,t_v}(q \mid t_k) \to \text{ActionGovernance}$$

| Architecture Arm | Ingress & Binding Policy | Authority & Capability Policy | Entity Ingress Mode | Downstream Epistemic Runtime |
|:---|:---|:---|:---|:---|
| **`A0: Always-Admit / Top-1`** | Binds top-1 lexical candidate; blind admission. | None (blind write). | Rejects novelty. | Frozen Bitemporal Engine + Antichain Support + Governance |
| **`A1: Canonicalization-Only`** | Deterministic alias normalization; collapses ambiguity. | None (blind write). | Rejects novelty. | Frozen Bitemporal Engine + Antichain Support + Governance |
| **`A2: Candidate-Aware Gate`** | Preserves candidate set $\mathcal{B}(x)$; creates `DEFERRED_BINDING`. | None (blind write). | Provisional tracking. | Frozen Bitemporal Engine + Antichain Support + Governance |
| **`A3: Authority-Aware Gate`** | Deterministic normalization; collapses ambiguity to Top-1. | Capability-scoped authorization checks. | Rejects novelty. | Frozen Bitemporal Engine + Antichain Support + Governance |
| **`A4: Full GENE Ingress`** | Hypothesis preservation ($\text{DEFERRED\_BINDING}$) over $\mathcal{B}(x)$. | Capability-scoped authorization + Proof-Carrying Certificates. | `PROVISIONAL_ENTITY` | Frozen Bitemporal Engine + Antichain Support + Governance |

---

## 4. Benchmark Composition: 120-World Factorial Suite ($N=480$ Probes)

### 4.1 Factorial Grid ($4 \times 5 \times 3 \times 2 = 120$ Worlds)
1. **Predicate Modes (4)**: `TIME_VARYING`, `ADDITIVE`, `EPISODIC`, `INTERVAL_BOUNDED`.
2. **Binding Conditions (5)**:
   - `EXACT_CANONICAL`: Exact string match to canonical entity ID.
   - `SURFACE_ALIAS`: Normalizable lexical alias (e.g. `"Auditor"`, `"Transport Unit 3"`).
   - `CANDIDATE_COLLISION`: Two equally plausible entities in namespace (`Server_1` vs `Server_1_Backup`).
   - `ROLE_DISTRACTOR`: Multiple entities present, but semantic role is structurally resolvable (`Sensor Alpha reported Server 1 degraded` $\to$ monitored entity is Subject).
   - `NOVEL_ENTITY`: Entity absent from candidate namespace.
3. **Temporal Relations (3)**: Forward Update, Retroactive Backfill, Contemporaneous Dispute.
4. **Source Role Forms (2)**: Direct Observation vs Attributed Third-Party Report.

### 4.2 Disaggregated Phenomenon Sidecars
- **Novelty Sidecar**: Distinguishes `NOVEL_TRUE` (true absent entity) from `KNOWN_BUT_CANDIDATE_MISS` (retriever missed existing entity).
- **Ambiguity Sidecar**: Distinguishes `ROLE_DISTRACTOR` (resolvable semantic role) from `TRUE_AMBIGUITY` (unresolvable text $\to \text{DEFERRED\_BINDING}$).

### 4.3 Strictly Formal Four-Probe Evaluation Protocol
All four probes are evaluated via formal state and algebraic queries ($0$ live LLM compute):
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

### Neural Output Schema for Hypothesis Preservation:
```json
{
  "mention_span": "Server Node 1",
  "candidate_ids": ["Server_Node_1", "Server_Node_1_Backup"],
  "selection_status": "SELECT" | "DEFER" | "NOVEL"
}
```

Total Live Call Budget: $16 \text{ cases} \times 3 \text{ arms} + 4 \text{ replay canaries} = \mathbf{52 \text{ calls}}$.

---

## 7. Primary Evaluation Metrics & Geometry Preservation

### 7.1 Preserved Failure Geometry
For every world $w$, record the complete 4-probe binary outcome vector:
$$P(w) = (Q_1, Q_2, Q_3, Q_4) \in \{0, 1\}^4$$
$$\text{WorldPass}(w) = Q_1 \land Q_2 \land Q_3 \land Q_4$$
- Primary headline metric: $\text{Rate}(\text{WorldPass}) = \frac{1}{N} \sum_{w=1}^N \text{WorldPass}(w)$.
- Report full distribution over all $2^4 = 16$ failure profiles. Scalar composite $\text{Acc}_{\text{4-Probe}}$ is reported as a secondary summary only.

### 7.2 Mathematically Valid $\text{FDAR}$ & Safe Admission Coverage ($\text{SAC}$)
1. **Global False Durable Admission Rate ($\text{FDAR}$)**:
   $$\text{FDAR} = \frac{N(\text{Inadmissible candidate durably admitted as Active Fact})}{N(\text{Inadmissible admission opportunities})}$$
   *Target Invariant: $\mathbf{\text{FDAR} = 0.0\%}$ (Strictly Fail-Closed).*

2. **Disaggregated Diagnostic Phenotypes (Multi-Label Rates)**:
   - $\text{FDAR}_{\text{bind}} = P(\text{ADMIT}_{\text{wrong}} \mid \text{Admissible ground truth with candidate distractor})$
   - $\text{FDAR}_{\text{ambiguity}} = P(\text{ADMIT}_{\text{collapsed}} \mid \text{True ambiguous candidate set})$
   - $\text{FDAR}_{\text{novel}} = P(\text{ADMIT}_{\text{mislinked}} \mid \text{Novel entity})$
   - $\text{FDAR}_{\text{authority}} = P(\text{ADMIT}_{\text{unauthorized}} \mid \text{Out-of-scope or unverified source})$

3. **Safe Admission Coverage ($\text{SAC}$)**:
   $$\text{SAC} = P(\text{ADMIT}_{\text{correct}} \mid \text{Admissible Ground Truth})$$

4. **Runtime Optimization Objective**:
   $$\max \text{SAC} \quad \text{subject to } \text{FDAR} = 0.0\%$$

5. **Replay Determinism Endpoint**:
   - Replay determinism is evaluated as an **empirical endpoint** across the 4 canaries under temperature $0.0$, seed $42$, without selective reruns.

---

## 8. Preregistered Stopping Rules & Gating Invariants

1. **Deterministic Gate**: No live LLM calls may be executed until the 120-world deterministic benchmark achieves **$100.0\%$ $\text{WorldPass}$** on Arm A4 and **$\text{FDAR} = 0.0\%$**.
2. **Replay Empirical Reporting**: Replay stability is reported exactly as observed without selective retries.
3. **Holdout Validation**: The final architecture must be evaluated against external holdout scenarios derived from STALE and Supersede benchmarks before declaring the ingress layer mature.
