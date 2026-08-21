---
promotion_id: PROMOTION-CONTRACT-R8-8A
contract_id: CONTRACT-R8-8A
status: CANDIDATE
candidate_sha: PLACEHOLDER
generated_at: "2026-08-21 20:56:00Z"
repair_rounds: 0
reviewed_by: codex
authorized_by: null
---

# Candidate Promotion Record: PROMOTION-CONTRACT-R8-8A

**Lifecycle Status**: `CANDIDATE` (Awaiting Human Director & ChatGPT Pro Promotion Review)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8A`
- **Phase / Milestone**: Exploration Round 8 Stage 8A (Autonomous Open Ingress)
- **Candidate Branch**: `mb/CONTRACT-R8-8A`
- **Auditor Verdict**: `PASS` (All criteria satisfied across sealed 50-world benchmark)
- **Repair Iterations**: 0 rounds

## 2. Benchmark Verification & Estimands Audit

| Metric | Target Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Candidate Recall ($M_1$)** | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 ($100.0\%$)** | **PASS** |
| **Candidate Precision ($M_2$)** | $\ge 85.0\%$ | **$100.0\%$** | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $\ge 85.0\%$ | **100 / 100 ($100.0\%$)** | **PASS** |
| **Global False Discovery ($\text{FDAR}$)** | $\equiv 0.0\%$ ($0 / N$) | **0 false admissions ($0.0\%$)** | **PASS** |
| **Paired Relative Drop vs Menu Control** | $\le 10.0\%$ | **$0.0\%$ drop** | **PASS** |

## 3. Epistemic Invariant Verification
All admitted entities and relations generated autonomously without candidate menus verified clean proof certificates in `IngressEngine`, maintaining zero false fact admissions in the bitemporal store.
