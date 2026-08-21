# Exploration Round 7 Research Plan: Epistemic Ingress — Binding, Attestation & Admission

**Document Status**: Preregistered Research Specification & Architectural Plan  
**Author**: Antigravity Research / GENE Core  
**Associated Target Commit**: `round7-wave0-freeze`  
**Prerequisites**: Exploration Round 6 Post-Review Freeze ([`round6-stage6c-postreview-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round6-stage6c-postreview-freeze))  

---

## 1. Executive Purpose & Research Problem

Following the completion of Round 6 (which established the deterministic core of bitemporal state adjudication, predicate contracts, and antichain support maintenance), the central scientific bottleneck of persistent AI has migrated from internal truth maintenance to the **neural-formal ingress boundary**:

> *Given a natural language observation and platform-trusted provenance metadata, under what formal conditions may a semantic candidate become durable epistemic state?*

Rather than allowing unconstrained neural generation to write directly to persistent memory, Round 7 establishes **Epistemic Ingress & Write Admission**:
$$\text{Natural Language} \xrightarrow[\text{Parsing}]{\text{Neural}} \text{Mention Spans} \xrightarrow[\text{Linking}]{\text{Deterministic}} \text{Candidate Set } \mathcal{B}(x) \xrightarrow[\text{Validation}]{\text{Certificate}} \text{Admission}(c) \in \{\text{ADMIT}, \text{AMBIGUOUS}, \text{NOVEL}, \text{REJECT}\}$$

Only candidates that receive an $\text{ADMIT}$ certificate are permitted to instantiate an authoritative `OccurrenceNode` in the bitemporal state engine.

---

## 2. Core Epistemic Invariants & Theoretical Foundations

### 2.1 The Attestation vs Admitted Fact Principle
$$\text{Attestation} \ne \text{Admitted Fact}$$
- An **Attestation** is an objective record that *Source $S$ asserted proposition $P$ at transaction time $t_k$*.
- An **Admitted Fact** is an authoritative, active proposition $P$ in the world model holding across valid time $[t_{v,\text{start}}, t_{v,\text{end}})$.
- An attestation is incontrovertible as historical telemetry, but does not automatically imply factual admission.

### 2.2 The Candidate Intervention-Sufficient Binding Principle
> **Principle:** Two candidate entity, value, or role bindings $b_i, b_j \in \mathcal{B}(x)$ may be safely collapsed to a single durable representation if and only if they are equivalent under the future query and intervention class $\mathcal{I}$ the runtime must preserve:
> $$\forall b_i, b_j \in \mathcal{B}(x), \; \forall \iota \in \mathcal{I}: \; \text{Response}(b_i, \iota) = \text{Response}(b_j, \iota)$$
> Whenever $b_i$ and $b_j$ yield divergent counterfactual responses under $\mathcal{I}$, committing to a single guess is lossy and hazardous. Emitting $\text{AMBIGUOUS}$ is strictly epistemically superior.

### 2.3 Source Authority Non-Amplification
$$\text{Authority}(\text{Admitted Fact}) \le \text{Authority}(\text{Origin})$$
- A quoted third-party statement cannot silently be promoted to a direct user fact.
- A model-derived hypothesis cannot be recorded as an independent root observation.
- Summarization and format transformations must preserve the minimal ancestral origin class.

---

## 3. The Four-Class Source & Authority Taxonomy (Authority Sidecar)

| Source Class | Description | Admissible Output Types | Authority Upper Bound |
|:---|:---|:---|:---|
| **`PLATFORM_ATTESTED`** | Hard cryptographic signatures, system sensor telemetry, and verified kernel logs. | `ROOT_FACT`, `OCCURRENCE_NODE` | $1.00$ (Full Authority) |
| **`USER_DIRECT`** | Direct, explicit operator instructions and user assertions. | `ROOT_FACT`, `PREFERENCE_NODE` | $0.85$ (High Authority) |
| **`THIRD_PARTY_QUOTED`** | External web search snippets, third-party user quotes, and unauthenticated inputs. | `ATTESTATION`, `AMBIGUOUS_CANDIDATE` | $0.30$ (Quoted Telemetry Only) |
| **`MODEL_DERIVED`** | Unverified chain-of-thought deductions, neural summarizations, and hypothetical projections. | `DERIVED_CLAIM` (Requires Certificate) | $0.00$ (Zero Independent Root Authority) |

---

## 4. Benchmark Composition: 120-World Factorial Suite ($N=480$ Probes)

To eliminate the risk of "query-level outcome invariance" where state errors hide behind a lucky single question, Round 7 evaluates a deterministic $4 \times 5 \times 3 \times 2 = 120$ world benchmark across **four independent probes** per world ($N=480$ total evaluations):

### 4.1 Factorial Grid
1. **Predicate Modes (4)**: `TIME_VARYING`, `ADDITIVE`, `EPISODIC`, `INTERVAL_BOUNDED`.
2. **Binding Conditions (5)**:
   - `EXACT_CANONICAL`: Exact string match to canonical entity ID.
   - `SURFACE_ALIAS`: Normalizable lexical alias (e.g. `"Auditor"`, `"Transport Unit 3"`).
   - `CANDIDATE_COLLISION`: Two equally plausible entities in namespace (e.g. `Server_Node_1` vs `Server_Node_1_Backup`).
   - `ROLE_AMBIGUITY`: Reporter vs Subject confusion (e.g. `Sensor Alpha reported Server 1 degraded`).
   - `NOVEL_ENTITY`: Entity absent from candidate namespace.
3. **Temporal Relations (3)**: Forward Update, Retroactive Backfill, Contemporaneous Dispute.
4. **Source Role Forms (2)**: Direct Observation vs Attributed Report.

### 4.2 The Four-Probe Evaluation Protocol
For every world state $(t_v, t_k)$, evaluate four orthogonal probes:
- **$Q_1$ (Active State Probe)**: Does the active premise set $F(t_v \mid t_k)$ match canonical truth?
- **$Q_2$ (Stale/False Premise Resistance Probe)**: Does the runtime reject a question embedding an unadmitted or superseded premise?
- **$Q_3$ (Downstream Action Probe)**: Does the action governance engine authorize the correct policy action?
- **$Q_4$ (Causal Invalidation Probe)**: Under a `WHAT_IF(source=0)` ablation, do surviving derivations correctly persist?

---

## 5. Live Neural Assay: 3 Interfaces $\times$ 16 Hard Cases ($N=52$ Calls)

To evaluate neural candidate selection on pinned model `gemma3:12b` (digest `f4031aab...`), 16 stratified hard cases ($4 \text{ Modes} \times 4 \text{ Ingress Phenomena}$) will be tested across three distinct architectural interfaces:

| Arm | Interface Responsibility | Model Prompting / Constraints |
|:---|:---|:---|
| **Arm N1: Free Generation** | Free generation of canonical entity IDs from scratch (Stage 6C baseline). | Open JSON generation. |
| **Arm N2: Candidate Selection** | Neural model extracts mention span, then selects from a prompt-supplied candidate set $\mathcal{B}(x) \cup \{\text{AMBIGUOUS}, \text{NOVEL}\}$. | Unconstrained JSON with candidate options. |
| **Arm N3: Constrained Selection** | Same candidate selection task, but model output is grammar-constrained to valid enum options. | Constrained grammar decoding. |

Total Live Call Budget: $16 \text{ cases} \times 3 \text{ arms} + 4 \text{ replay canaries} = \mathbf{52 \text{ calls}}$.

---

## 6. Primary Evaluation Metrics

1. **False Durable Admission Rate ($\text{FDAR}$)** (Primary Safety Metric):
   $$\text{FDAR} = P(\text{ADMIT} \mid \text{Candidate is wrong, ambiguous, or unauthorized})$$
   *Target: $\mathbf{0.0\%}$ (Strictly Fail-Closed).*

2. **Correct Admission Rate ($\text{CAR}$)**:
   $$\text{CAR} = P(\text{ADMIT}_{\text{correct}} \mid \text{Resolvable Case})$$

3. **Downstream 4-Probe Composite Accuracy**:
   $$\text{Acc}_{\text{4-Probe}} = \frac{1}{4} \left[ \text{Acc}(Q_1) + \text{Acc}(Q_2) + \text{Acc}(Q_3) + \text{Acc}(Q_4) \right]$$

---

## 7. Preregistered Stopping Rules & Gating Invariants

1. **Deterministic Gate**: No live LLM calls may be executed until the 120-world deterministic benchmark achieves **$100.0\%$ oracle pass rate** and **$\text{FDAR} = 0.0\%$**.
2. **Immutable Replay**: 4 replay canaries must achieve $100\%$ raw string and semantic JSON stability under temp $0.0$, seed $42$.
3. **Holdout Validation**: The final architecture must be evaluated against external holdout scenarios derived from STALE and Supersede benchmarks before declaring the ingress layer mature.
