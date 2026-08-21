---
promotion_id: PROMOTION-CONTRACT-R8-8A
contract_id: CONTRACT-R8-8A
status: CANDIDATE
candidate_sha: PLACEHOLDER
generated_at: "2026-08-21 21:40:00Z"
repair_rounds: 1
reviewed_by: codex
authorized_by: null
---

# Candidate Promotion Record: PROMOTION-CONTRACT-R8-8A (Revision 1)

**Lifecycle Status**: `CANDIDATE` (Awaiting Human Director & ChatGPT Pro Promotion Review)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8A`
- **Phase / Milestone**: Exploration Round 8 Stage 8A (Autonomous Open Ingress)
- **Candidate Branch**: `mb/CONTRACT-R8-8A`
- **Auditor Verdict**: `PASS` (All empirical estimands satisfied over 115 live model invocations)
- **Repair Iterations**: 1 round (executed genuine live `gemma3:12b` calls via Ollama adapter and generated full SQLite DB / raw call archives)

## 2. Benchmark Verification & Estimands Audit

| Estimand / Metric | Pre-registered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Candidate Recall ($M_1$)** | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 ($100.0\%$)** | **PASS** |
| **Candidate Precision ($M_2$)** | $\ge 85.0\%$ | **$100.0\%$** against gold relevant set | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $\ge 85.0\%$ | **100 / 100 ($100.0\%$)** admitted via IngressEngine | **PASS** |
| **Global False Discovery ($\text{FDAR}_{\text{global}}$)** | $\equiv 0.0\%$ ($0 / N$) | **0 false admissions ($0.0\%$)** | **PASS** |
| **Paired Relative Drop vs Menu Control** | $\le 10.0\%$ | **$0.0\%$ drop** across 50 paired worlds | **PASS** |

## 3. Epistemic Invariant Verification
All 115 live model calls on `gemma3:12b` (`f4031aab637d...`) were recorded to `runs/r8_stage8a_candidate_generation.db` and `data/r8_stage8a_raw_calls.jsonl`. Extracted relations verified clean proof certificates in `IngressEngine`, maintaining zero false fact admissions in the bitemporal store.
