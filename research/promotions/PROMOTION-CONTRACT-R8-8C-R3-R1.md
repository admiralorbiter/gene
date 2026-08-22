---
promotion_id: PROMOTION-CONTRACT-R8-8C-R3-R1
contract_id: CONTRACT-R8-8C-R3-R1
status: CANDIDATE
candidate_sha: 295d1c78fd3ee2e11a5990f49e3520680a676ac5
generated_at: "2026-08-22 11:54:00Z"
repair_rounds: 1
reviewed_by: chatgpt-pro
authorized_by: null
---

# Promotion Candidate Record: PROMOTION-CONTRACT-R8-8C-R3-R1 (Definitive Stage 8 Closure & Epistemic Ingress Decoupling)

**Lifecycle Status**: `CANDIDATE` (Implementation Repair Round 1: ALL 10 GATES PASS; Awaiting Review Desk Evaluation & Human Strategic Promotion Authorization)

---

## 1. Execution & Provenance

- **Target Contract**: `CONTRACT-R8-8C-R3-R1` ([`research/contracts/CONTRACT-R8-8C-R3-R1.md`](../contracts/CONTRACT-R8-8C-R3-R1.md))
- **Base SHA**: `92400bf22a24316e5c1522489a1a003c365fe848`
- **Execution Base SHA**: `c13fae42bfb064a01b7be5c205350038997fb97b`
- **Candidate Evidence SHA**: `295d1c78fd3ee2e11a5990f49e3520680a676ac5`
- **Model**: Gemma 3 12B Instruct (Q4_K_M) via local Ollama endpoint.
- **Hardware Environment**: NVIDIA GeForce RTX 3060 12GB (Exclusive GPU execution).
- **Execution Performance**: 120 sequential decisions completed in **333.23s (5.55 minutes)** on uncontested GPU (averaging **2.78s per decision**).
- **Evidence Package**: Committed in tree at:
  - Evidence JSONL: [`data/r8_stage8c_r3_r1_candidate_evidence.jsonl`](../../data/r8_stage8c_r3_r1_candidate_evidence.jsonl)
  - Relational Database: [`data/r8_stage8c_r3_r1_registry.sqlite`](../../data/r8_stage8c_r3_r1_registry.sqlite)

---

## 2. Statistical Acceptance Gates ($N=120$ Decisions, $N=97$ Resolvable)

| Gate ID | Target Metric | Preregistered Boundary | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Neural Proposal Telemetry Logging | Logged across all $N=120$ decisions | **120 / 120 logged (100.0%)** | **PASS** |
| **Gate 2a** | False Canonical Merge Floor | $\equiv 0.0\%$ ($0/120$ false merges) | **0 / 120 false merges (0.0%)** | **PASS** |
| **Gate 2b** | False Provisional on Unasserted (Arm 4A Sentinel) | $\equiv 0.0\%$ ($0/16$ unasserted) | **0 / 16 false creations (0.0%)** | **PASS** |
| **Gate 2c** | Global False Provisional Invariant (Claim Ceiling) | $\equiv 0.0\%$ ($0/120$ decisions) | **0 / 120 false creations (0.0%)** | **PASS** |
| **Gate 3** | Provisional Entity Fragmentation | $\equiv 0$ duplicate provisional creations | **0 duplicate creations** | **PASS** |
| **Gate 4** | Permanent Deferral Invariant (Arm 4A) | $\ge 7/8$ ($87.5\%$) fully deferred worlds | **8 / 8 worlds fully deferred (100.0%)** | **PASS** |
| **Gate 5** | Live Lifecycle State Machine (Arm 4B) | $\equiv 7/7$ sound transitions | **7 / 7 sound transitions (100.0%)** | **PASS** |
| **Gate 5b** | Deterministic CPU Branch Coverage | $\equiv \text{PASS}$ across all 5 branches | **All 5 branches PASS (100.0%)** | **PASS** |
| **Gate 6** | Useful Resolvable Coverage ($N=97$ Resolvable) | $\ge 85.0\%$ across $N=97$ resolvable events | **97 / 97 (100.0% Coverage)** | **PASS** |
| **Gate 7** | Relational DB & Ledger Reconciliation | Strict 8 UNRESOLVED + 7 Resolved == 15 Total | **15 / 15 Hypotheses, 120 Records, 0 FK Errors** | **PASS** |
| **Audit** | Dual Freshness Audit vs Frozen R3 | $\equiv \text{PASS}$ (0 mention & 0 pair overlap) | **0 mention overlap, 0 pair overlap** | **PASS** |

---

## 3. Dual Paired Replay & Causal Isolation Analysis

$$\begin{array}{l|c|c|c|c|c}
\textbf{Resolver Condition} & \textbf{Coverage} & \mathbf{\Delta} \textbf{ vs R3-R1} & n_{11} & n_{01} \text{ (Recoveries)} & n_{10} \text{ (Regressions)} \\
\hline
\text{Candidate Ingress Kernel (R3-R1)} & \mathbf{100.0\%} \ (97/97) & \text{Baseline} & 97 & - & - \\
\text{Matched Precedence Ablation} & 95.9\% \ (93/97) & \mathbf{+4.1\%} & 93 & \mathbf{4} & \mathbf{0} \\
\text{Historical Frozen Stage 8C-R2} & 84.5\% \ (82/97) & \mathbf{+15.5\%} & 82 & \mathbf{15} & \mathbf{0}
\end{array}$$

- **Isolated Precedence Attribution**: $+4.1\%$ ($4$ recovered cases, $0$ regressions) directly isolated by the matched ablation.
- **Total Historical Gain over R2**: $+15.5\%$ ($15$ recovered cases, $0$ regressions).

---

## 4. Scientific Claim Ceiling

### Certified Finding Authorized Upon Promotion
> In a controlled synthetic streaming hardware benchmark ($N=60$ fresh worlds, $120$ decisions), hybrid neural-symbolic ingress with refined precedence achieves $100.0\%$ useful admission coverage on resolvable events with $0.0\%$ false canonical merges and $0.0\%$ false provisional creations globally across the entire benchmark, while the deterministic hypothesis ledger maintains $100.0\%$ sound evidence accumulation across all lifecycle transitions.

### Explicit Exclusions
This contract does **NOT** authorize claims of unstructured open-world entity resolution, unsupervised ontology discovery, or autonomous claim-level truth maintenance (which begins in Stage 9).
