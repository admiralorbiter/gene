---
promotion_id: PROMOTION-CONTRACT-R8-8A
contract_id: CONTRACT-R8-8A
status: PROMOTED
candidate_sha: c7c9ef641393adf6687f9ce05eda0b8776e2e32d
promoted_at: "2026-08-21 22:16:00Z"
repair_rounds: 2
reviewed_by: chatgpt-pro
authorized_by: human
---

# Promotion Record: PROMOTION-CONTRACT-R8-8A (Promoted)

**Lifecycle Status**: `PROMOTED` (Authorized by Human Research Director & ChatGPT Pro Scientific Review Desk)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8A`
- **Phase / Milestone**: Exploration Round 8 Stage 8A (Autonomous Open Ingress)
- **Promoted Candidate Commit SHA**: `c7c9ef641393adf6687f9ce05eda0b8776e2e32d`
- **Contract Acceptance Verifier**: `PASS` (`scripts/verify_contract_r8_8a.py` executed and cleanly passed)
- **Scientific Review Verdict**: `APPROVED` (with one follow-up verifier hardening debt recorded)
- **Governance**: Human Director Promotion Merge.

## 2. Benchmark Verification & Estimands Audit

| Estimand / Metric | Pre-registered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Candidate Recall ($M_1$)** | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 ($100.0\%$)** | **PASS** |
| **High-Salience Recall** | $\ge 90.0\%$ | **50 / 50 ($100.0\%$)** | **PASS** |
| **Low-Salience Recall** | $\ge 85.0\%$ | **50 / 50 ($100.0\%$)** | **PASS** |
| **Candidate Precision ($M_2$)** | $\ge 85.0\%$ | **$100.0\%$** against gold relevant set | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $\ge 85.0\%$ | **100 / 100 ($100.0\%$)** admitted & probe-verified | **PASS** |
| **Global False Discovery ($\text{FDAR}_{\text{global}}$)** | $\equiv 0.0\%$ ($0 / N$) | **0 incorrect durable admissions ($0.0\%$)** | **PASS** |
| **Paired Relative Drop vs Menu Control** | $\le 10.0\%$ | **$0.0\%$ drop** across 50 paired worlds | **PASS** |
| **Downstream Probes Q1..Q4** | $\equiv 100.0\%$ | **100.0% passed** (Point-in-time, interval support, active facts, certificates) | **PASS** |

## 3. Epistemic Invariants & Methodological Debt
- **Belief Update**: In this controlled synthetic single-document domain, removing the explicit finite candidate menu did not reduce candidate extraction or downstream safe-admission performance for `gemma3:12b`.
- **Claim Ceiling**: Does not establish unrestricted open-world entity induction. Predicate schema is supplied, ontology exists downstream, and narratives are single-document synthetic telemetry.
- **Follow-up Hardening Debt**: Future Stage 8+ acceptance verifiers should recompute primary estimands directly from raw persisted evidence rather than trusting canonical-summary metric fields.
