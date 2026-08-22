---
promotion_id: PROMOTION-CONTRACT-R8-8C-R3
contract_id: CONTRACT-R8-8C-R3
status: REVISED_CONTRACT_REQUIRED
candidate_sha: b583bffffd84f08aa59957f3278b01095c90f541
generated_at: "2026-08-22 10:42:00Z"
repair_rounds: 0
reviewed_by: chatgpt-pro
authorized_by: human
---

# Promotion Review Record: PROMOTION-CONTRACT-R8-8C-R3 (Two-Stage Epistemic Ingress with Refined Precedence)

**Lifecycle Status**: `REVISED_CONTRACT_REQUIRED` (Review Desk Evaluation: REVISED_CONTRACT_REQUIRED; Strategic Decision Authorized by Human Research Director)

---

## 1. Execution & Audit Provenance

- **Target Contract**: `CONTRACT-R8-8C-R3` ([`research/contracts/CONTRACT-R8-8C-R3.md`](../contracts/CONTRACT-R8-8C-R3.md))
- **Base SHA**: `1f3b0207345563ce903d00777455e1f8ed0f46f0`
- **Execution Base SHA**: `19713d22c3b4fe50181fb82631eff8c242b5195a`
- **Candidate Evidence SHA**: `b583bffffd84f08aa59957f3278b01095c90f541`
- **Model**: Gemma 3 12B Instruct (Q4_K_M) via local Ollama endpoint.
- **Hardware Environment**: NVIDIA GeForce RTX 3060 12GB (Exclusive GPU execution).
- **Execution Performance**: 120 sequential decisions completed in **694.33s (11.57 minutes)**, averaging **5.79s per decision**.
- **Evidence Package**: Committed in tree at:
  - Evidence JSONL: [`data/r8_stage8c_r3_candidate_evidence.jsonl`](../../data/r8_stage8c_r3_candidate_evidence.jsonl)
  - Relational Database: [`data/r8_stage8c_r3_registry.sqlite`](../../data/r8_stage8c_r3_registry.sqlite)

---

## 2. Statistical Acceptance Gates ($N=120$ Decisions, $N=97$ Resolvable)

| Gate ID | Target Metric & Statistical Boundary | Preregistered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Neural Proposal Logging Telemetry | Logged across all $N=120$ decisions | **120 / 120 logged (100.0%)** | **PASS** |
| **Gate 2a** | False Canonical Merge Floor | $\equiv 0.0\%$ ($0/120$ false merges) | **0 / 120 false merges (0.0%)** | **PASS** |
| **Gate 2b** | False Provisional Floor on Unasserted | $\equiv 0.0\%$ ($0/16$ unasserted mentions) | **0 / 16 false creations (0.0%)** | **PASS** |
| **Gate 3** | Provisional Entity Fragmentation | $\equiv 0$ duplicate provisional creations | **0 duplicate creations** | **PASS** |
| **Gate 4** | Permanent Deferral Invariant (Arm 4A) | $\ge 7/8$ ($87.5\%$) fully deferred worlds | **8 / 8 worlds fully deferred (100.0%)** | **PASS** |
| **Gate 5** | Evidence Accumulation Lifecycle (Arm 4B) | $\equiv 7/7$ exact world lifecycle transitions | **3 / 7 exact matches** (See Dissection) | **FAILED** |
| **Gate 6** | Useful Resolvable Coverage ($N=97$ Resolvable) | $\ge 85.0\%$ across $N=97$ resolvable events | **97 / 97 (100.0% Coverage)** | **PASS** |
| **Gate 7** | Relational DB & Hypothesis Ledger Reconciliation | Strict 8 UNRESOLVED + 7 Resolved == 15 Total | **15 / 15 Hypotheses, 120 Records, 0 FK Errors** | **PASS** |

---

## 3. Paired Comparative Replay ($R3$ vs Frozen $R2$)

$$\begin{array}{c|c|c}
& \text{R3 Correct} & \text{R3 Incorrect} \\
\hline
\text{R2 Correct} & n_{11} = \mathbf{58} \text{ (Concordant Correct)} & n_{10} = \mathbf{0} \text{ (Regressions)} \\
\hline
\text{R2 Incorrect} & n_{01} = \mathbf{39} \text{ (Recovered Cases)} & n_{00} = \mathbf{0} \text{ (Concordant Incorrect)}
\end{array}$$

- **R2 Coverage**: $59.8\%$ ($58/97$)
- **R3 Coverage**: **$100.0\%$ ($97/97$)**
- **Net Attribution Delta**: **$+40.2\%$ total historical improvement** ($n_{01} = 39, n_{10} = 0$).

---

## 4. Root Cause of Gate 5 Failure: Neural Conservatism vs Lifecycle Assay

Per the pre-registered decision tree ([`research/contracts/R3_POST_EXECUTION_DECISION_TREE.md`](../contracts/R3_POST_EXECUTION_DECISION_TREE.md)):

1. **The Flaw in the Preregistered Assay**:
   The contract preregistered fixed terminal statuses assuming the neural model would propose speculative candidate targets (e.g. guessing `gateway_router_alpha` for `"Edge Gateway Alpha Reserve Bay"`). However, the system prompt explicitly commanded the model: *"Never guess or merge distinct entities without strong evidence."*
2. **Observed System Behavior**:
   Gemma 3 12B acted with sound epistemic caution on all ambiguous Doc 1 mentions, returning `candidate_action: "DEFER"` with `target_entity_id: null`. When Doc 2 subsequently resolved to an existing entity, the deterministic state machine transitioned the hypothesis to `RESOLVED_EXISTING` (passing cases 4 and 5) rather than `RETARGETED` or `CONFIRMED`.
3. **Epistemic Conclusion**:
   The observed null-candidate lifecycle behaved coherently and safely, but the live experiment never exercised the full four-way lifecycle state machine (`RETARGETED`, `CONFIRMED`).

---

## 5. Closure Strategy: Revision R3-R1

To achieve definitive confirmatory promotion without lowering standards:
1. **Decouple Live Lifecycle Correctness from Speculation**: Live Gate 5 verifies that the hypothesis transition matches the *actual* candidate proposal (`cand is None` $\to$ `RESOLVED_EXISTING`, `cand == target` $\to$ `CONFIRMED`, `cand != target` $\to$ `RETARGETED`).
2. **Deterministic CPU-Only Branch-Coverage Assay**: Add a separate unit test with injected candidate states that explicitly exercises all four terminal transitions.
3. **Matched Precedence Ablation**: Implement a matched comparator ($R3_{\text{ablation}}$) restoring universal structural-first-refusal to isolate the exact causal effect of the precedence rule from general implementation differences.
4. **Fresh Evidence**: Execute on fresh sealed worlds under `CONTRACT-R8-8C-R3-R1`.
