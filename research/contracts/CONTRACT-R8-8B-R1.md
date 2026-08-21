---
contract_id: CONTRACT-R8-8B-R1
status: DRAFT
proposed_by: antigravity
design_review: null
reviewed_by: chatgpt-pro
authorized_by: null
base_sha: 3861de935a8f4c2e6840004ff41c59bb79bc6102
execution_base_sha: null
---

# Research Contract Proposal: CONTRACT-R8-8B-R1

## Title
Exploration Round 8 Stage 8B-R1: Multi-Document Coreference Resolution & Asynchronous Bitemporal Supersession Fusion

## 1. Context & Research Question
In exploration stage 8A, `gemma3:12b` demonstrated high extraction fidelity within single document contexts. Stage 8B-R1 evaluates the next epistemic frontier: **multi-document streams** where entities are referenced across multiple asynchronous documents using aliases and coreferent expressions, with late-arriving out-of-order telemetry that introduces genuine valid-time state conflicts requiring bitemporal supersession.

### Core Research Question
Can an autonomous neural agent (`gemma3:12b`) accurately extract and resolve multi-document coreferent mentions against a pre-registered canonical entity registry and correctly reconcile out-of-order temporal conflicts through formal bitemporal supersession without inducing false merges ($\text{FDAR} \equiv 0.0\%$)?

---

## 2. Experimental Design ($2 \times 2$ Factorial Grid)

The benchmark evaluates 50 sealed procedural worlds, each presenting an asynchronous multi-document stream of exactly 2 documents ($N = 100$ evaluation documents):

```
                       In-Order (tk matches tv)    Out-of-Order / Superseding (tk inverted)
Literal Mentions      [Cell 1: 10 Worlds (20 docs)]  [Cell 3: 10 Worlds (20 docs)]
Aliased Coreference   [Cell 2: 15 Worlds (30 docs)]  [Cell 4: 15 Worlds (30 docs)]
```

### Stream Architecture per Cell
1. **Cell 1 (Literal $\times$ In-Order)**: 10 Worlds ($20$ docs, $40$ mention slots).
   - Doc 1 ($t_k = 1, t_v \in [1.0, 5.0]$): `Cluster Unit i` held state `Active`.
   - Doc 2 ($t_k = 2, t_v \in [5.0, 10.0]$): `Cluster Unit i` shifted to state `Operational`.
2. **Cell 2 (Alias $\times$ In-Order)**: 15 Worlds ($30$ docs, $60$ mention slots, $30$ gold alias subject mentions).
   - Doc 1 ($t_k = 1, t_v \in [1.0, 5.0]$): Alias `Relay Primus i` (resolves to `Cluster Unit i`) held state `Active`.
   - Doc 2 ($t_k = 2, t_v \in [5.0, 10.0]$): Secondary hardware tag `Cluster Unit i Alpha` (resolves to `Cluster Unit i`) shifted to `Operational`.
3. **Cell 3 (Literal $\times$ Out-of-Order / Superseding)**: 10 Worlds ($20$ docs, $40$ mention slots).
   - Doc 1 ($t_k = 1, t_v \in [5.0, 10.0]$): `Cluster Unit i` reported state `Active`.
   - Doc 2 ($t_k = 2, t_v \in [1.0, 7.0]$): Late-arriving historical record: `Cluster Unit i` was `Degraded` on $[1.0, 7.0]$ (conflicting overlap in $[5.0, 7.0]$).
4. **Cell 4 (Alias $\times$ Out-of-Order / Superseding)**: 15 Worlds ($30$ docs, $60$ mention slots, $30$ gold alias subject mentions).
   - Doc 1 ($t_k = 1, t_v \in [5.0, 10.0]$): Alias `Relay Secundus i` reported state `Operational`.
   - Doc 2 ($t_k = 2, t_v \in [1.0, 7.0]$): Secondary tag `Cluster Unit i Beta` late arrival: state was `Degraded` on $[1.0, 7.0]$.
5. **Adversarial Distractor Controls**: 30 near-collision worlds ($30$ docs) testing phonetically/lexically adjacent entity pairs (`Cluster Unit i-A` vs `Cluster Unit i-B`).

---

## 3. Four-Point Bitemporal Timeline Queries for Out-of-Order Worlds

For every out-of-order world in Cells 3 & 4 ($N = 25$ worlds $\times 4$ query points $= 100$ bitemporal queries), the independent verifier evaluates:
1. **Initial State ($t_k=1, t_v=6.0$)**: Returns initial state (`Active` or `Operational`).
2. **Late Historical State ($t_k=2, t_v=1.5$)**: Returns late-arriving historical fact (`Degraded`).
3. **Conflicting Overlap Supersession ($t_k=2, t_v=6.0$)**: Reconciles superseding fact (`Degraded`) via explicit `EventType.SUPERSEDES` event.
4. **Un-superseded Future Tail ($t_k=2, t_v=8.0$)**: Returns initial state (`Active` or `Operational`).

---

## 4. Frozen Acceptance Criteria & Exact Denominators

| Gate / Estimand | Formal Definition & Exact Denominator | Pre-registered Acceptance Threshold |
| :--- | :--- | :--- |
| **Gate 1: Coreference Recall ($M_{1\text{coref}}$)** | $\frac{\text{TP}_{\text{alias}}}{\text{Total Alias Mentions}}$ ($N = 60$ mentions across Cells 2 & 4) | $\ge 85.0\%$ ($51 / 60$) |
| **Gate 2: Candidate Precision ($M_2$)** | $\frac{\text{TP}_{\text{extracted}}}{\text{Total Proposed Candidates}}$ ($N = 200$ candidate slots) | $\ge 85.0\%$ ($170 / 200$) |
| **Gate 3: False Merge Rate** | $\frac{\text{False Merges}}{\text{Total Collision Trials}}$ ($N = 30$ distractor trials) | $\equiv 0.0\%$ ($0 / 30$) |
| **Gate 4: False Split Rate** | $\frac{\text{False Splits}}{\text{Total Alias Mentions}}$ ($N = 60$ mentions across Cells 2 & 4) | $\le 5.0\%$ ($3 / 60$) |
| **Gate 5: Bitemporal Supersession Correctness** | $\frac{\text{Correct 4-Point Timeline Queries}}{\text{Total Bitemporal Queries}}$ ($N = 100$ queries in Cells 3 & 4) | $\ge 90.0\%$ ($90 / 100$) |
| **Gate 6: Useful Admission Coverage ($M_3$)** | $\frac{\text{Useful Admitted Mention Slots}}{\text{Total Gold Mention Slots}}$ ($N = 200$ mention slots) | $\ge 80.0\%$ ($160 / 200$) |
| **Gate 7: Global False Discovery Rate ($\text{FDAR}_{\text{global}}$)** | $\frac{\text{Incorrect Durable Admissions}}{\text{Total Durable Admissions}}$ | $\equiv 0.0\%$ ($0 / N$) |
| **Gate 8: Downstream Query Probes Q1..Q4** | $\frac{\text{Passed Probes}}{\text{Total Probes Evaluated}}$ ($N = 400$ probe queries) | $\equiv 100.0\%$ |

---

## 5. Execution Parameters & Constraints
- **Model**: `gemma3:12b` (`temperature: 0.0`, `seed: 42`, `format: json`).
- **No Autonomous Freezing**: Requires Human Director Authorization following Scientific Review Desk evaluation.
- **Independent Raw Verifier**: Acceptance verifier must independently parse raw model JSON spans, resolve entities, emit `SUPERSEDES` events, and replay timeline states with zero runner boolean dependencies.
