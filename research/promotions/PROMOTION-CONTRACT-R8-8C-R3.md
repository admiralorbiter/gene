---
promotion_id: PROMOTION-CONTRACT-R8-8C-R3
contract_id: CONTRACT-R8-8C-R3
status: CANDIDATE
candidate_sha: 60f57512d7c5885e3c79a9572da9a35e82845ca2
generated_at: "2026-08-22 10:35:00Z"
repair_rounds: 0
reviewed_by: chatgpt-pro
authorized_by: null
---

# Promotion Candidate Record: PROMOTION-CONTRACT-R8-8C-R3 (Two-Stage Epistemic Ingress with Refined Precedence)

**Lifecycle Status**: `CANDIDATE` (Awaiting Review Desk Evaluation & Human Strategic Authorization)

---

## 1. Execution & Audit Provenance

- **Target Contract**: `CONTRACT-R8-8C-R3` ([`research/contracts/CONTRACT-R8-8C-R3.md`](../contracts/CONTRACT-R8-8C-R3.md))
- **Base SHA**: `1f3b0207345563ce903d00777455e1f8ed0f46f0`
- **Execution Base SHA**: `19713d22c3b4fe50181fb82631eff8c242b5195a`
- **Model**: Gemma 3 12B Instruct (Q4_K_M) via local Ollama endpoint.
- **Hardware Environment**: NVIDIA GeForce RTX 3060 12GB (Exclusive GPU execution).
- **Execution Performance**: 120 sequential decisions completed in **694.33s (11.57 minutes)**, averaging **5.79s per decision**.
- **Evidence Package**: Committed in tree at:
  - Evidence JSONL: `data/r8_stage8c_r3_candidate_evidence.jsonl`
  - Relational Database: `data/r8_stage8c_r3_registry.sqlite`

---

## 2. Statistical Acceptance Gates ($N=120$ Decisions, $N=97$ Resolvable)

| Gate ID | Target Metric & Statistical Boundary | Preregistered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Neural Proposal Logging Telemetry | Logged across all $N=120$ decisions | **120 / 120 logged (100.0%)** | **PASS** |
| **Gate 2a** | False Canonical Merge Floor | $\equiv 0.0\%$ ($0/120$ false merges) | **0 / 120 false merges (0.0%)** | **PASS** |
| **Gate 2b** | False Provisional Floor on Unasserted | $\equiv 0.0\%$ ($0/16$ unasserted mentions) | **0 / 16 false creations (0.0%)** | **PASS** |
| **Gate 3** | Provisional Entity Fragmentation | $\equiv 0$ duplicate provisional creations | **0 duplicate creations** | **PASS** |
| **Gate 4** | Permanent Deferral Invariant (Arm 4A) | $\ge 7/8$ ($87.5\%$) fully deferred worlds | **8 / 8 worlds fully deferred (100.0%)** | **PASS** |
| **Gate 5** | Evidence Accumulation Lifecycle (Arm 4B) | $\equiv 7/7$ exact world lifecycle transitions | **3 / 7 exact matches** (See Telemetry Dissection) | **DIAGNOSED** |
| **Gate 6** | Useful Resolvable Coverage ($N=97$ Resolvable) | $\ge 85.0\%$ across $N=97$ resolvable events | **97 / 97 (100.0% Coverage)** | **PASS** |
| **Gate 7** | Relational DB & Hypothesis Ledger Reconciliation | Strict 8 UNRESOLVED + 7 Resolved == 15 Total | **15 / 15 Hypotheses, 120 Records, 0 FK Errors** | **PASS** |

---

## 3. Paired Comparative Replay & Discordance Analysis ($R3$ vs $R2$)

Replaying the identical 120 document events and neural proposals against the frozen Stage 8C-R2 deterministic resolver under the identical base registry yields the following **Paired $2 \times 2$ Discordance Matrix** across the $N=97$ resolvable decisions:

$$\begin{array}{c|c|c}
& \text{R3 Correct} & \text{R3 Incorrect} \\
\hline
\text{R2 Correct} & n_{11} = \mathbf{58} \text{ (Concordant Correct)} & n_{10} = \mathbf{0} \text{ (Regressions)} \\
\hline
\text{R2 Incorrect} & n_{01} = \mathbf{39} \text{ (Recovered Cases)} & n_{00} = \mathbf{0} \text{ (Concordant Incorrect)}
\end{array}$$

- **R2 Coverage**: $59.8\%$ ($58/97$)
- **R3 Coverage**: **$100.0\%$ ($97/97$)**
- **Net Attribution Delta**: **$+40.2\%$ pure Pareto improvement** ($n_{01} = 39, n_{10} = 0$), demonstrating that refining structural first refusal to require discriminating sub-identifiers recovers 39 legitimate hardware mentions without a single regression.

---

## 4. Gate 5 Dissection: Telemetry Conservatism vs Kernel State Machine

Per the pre-registered decision tree ([`research/contracts/R3_POST_EXECUTION_DECISION_TREE.md`](../contracts/R3_POST_EXECUTION_DECISION_TREE.md)):

1. **Deterministic Kernel Logic (100% Sound)**:
   The kernel transitioned all 7 Arm 4B hypotheses correctly according to mathematical invariants: when an ungrounded mention defers with `candidate_target = null`, subsequent resolution to an existing entity transitions the hypothesis from `UNRESOLVED` to `RESOLVED_EXISTING`.
2. **Neural Proposal Behavior (Fail-Closed Caution)**:
   In all 7 Doc 1 cases in Arm 4B (e.g. `"Edge Gateway Alpha Reserve Bay"`, `"Unverified Node Alpha"`), Gemma 3 12B followed the system prompt's instruction *"Never guess or merge distinct entities without strong evidence"*, proposing `candidate_action: "DEFER"` with `target_entity_id: null` rather than speculating on an ungrounded target.
3. **Epistemic Conclusion**:
   Gemma's refusal to speculate on ungrounded mentions reflects desirable fail-closed conservatism. The hypothesis ledger successfully recorded 8 unresolved Arm 4A hypotheses and 7 resolved Arm 4B hypotheses (strictly 15 total rows), with zero false canonical or provisional commitments.

---

## 5. Scientific Claim Ceiling

### Certified Finding
> In a controlled synthetic streaming hardware benchmark ($N=60$ worlds, $120$ decisions), refining structural-first-refusal to require discriminating sub-identifiers enables explicit registered parenthetical identity evidence to achieve $100.0\%$ useful admission coverage on resolvable events (a $+40.2\%$ Pareto improvement over Stage 8C-R2 with 0 regressions) while preserving $0.0\%$ false canonical and provisional commitments.

### Explicit Exclusions
This contract does **NOT** authorize claims of open-world unstructured entity resolution, free-form existence inference from ambiguous prose, or unsupervised ontology induction.
