---
promotion_id: PROMOTION-CONTRACT-R8-8B-R1
contract_id: CONTRACT-R8-8B-R1
status: CANDIDATE
candidate_sha: ddc1717103f6cde0abf757ed629638a7fedd7b88
generated_at: "2026-08-21 23:32:00Z"
repair_rounds: 0
reviewed_by: codex
authorized_by: null
---

# Candidate Promotion Record: PROMOTION-CONTRACT-R8-8B-R1 (Multi-Document Stream Coreference & Occurrence Splitting)

**Lifecycle Status**: `CANDIDATE` (Awaiting Scientific Promotion Review by ChatGPT Pro & Human Research Director Authorization)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8B-R1`
- **Phase / Milestone**: Exploration Round 8 Stage 8B-R1 Confirmatory Benchmark
- **Candidate Branch**: `mb/CONTRACT-R8-8B-R1`
- **Candidate Commit SHA**: ddc1717103f6cde0abf757ed629638a7fedd7b88
- **Execution Base SHA**: `3da636d9ddd649160f24e8eb1074d8c7d260e2e8`
- **Contract Acceptance Verifier**: `PASS` (`scripts/verify_contract_r8_8b_r1.py` executed with zero runner booleans, fresh sealed world manifest assertion, multi-document stream invariants, and independent occurrence-splitting bitemporal replay)
- **Auditor Verdict**: `PASS` (All 8 Estimands, Factorial Grid, 4-Point Timeline Queries, and Distractor Falsification Controls verified across 145 live `gemma3:12b` calls)
- **Repair Iterations**: 0 rounds (clean first-pass confirmatory execution on fresh manifest).

## 2. Confirmatory Estimands & Factorial Gate Outcomes

| Estimand / Metric | Exact Denominator | Pre-registered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Coreference Recall ($M_{1\text{coref}}$)** | $N = 60$ alias mentions (Cells 2 & 4) | $\ge 85.0\%$ ($51 / 60$) | **60 / 60 mentions ($100.0\%$)** | **PASS** |
| **Candidate Precision ($M_2$)** | Total proposed candidates | $\ge 85.0\%$ | **$100.0\%$** against canonical targets | **PASS** |
| **False Merge Rate** | $N = 30$ distractor trials | $\equiv 0.0\%$ ($0 / 30$) | **0 false merges ($0.0\%$)** | **PASS** |
| **False Split Rate** | $N = 60$ coreference mentions | $\le 5.0\%$ | **0 false splits ($0.0\%$)** | **PASS** |
| **Temporal Correctness (Out-of-Order)** | $N = 100$ 4-point queries (Cells 3 & 4) | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 queries ($100.0\%$)** | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $N = 200$ total gold mention slots | $\ge 80.0\%$ ($160 / 200$) | **200 / 200 slots ($100.0\%$)** | **PASS** |
| **Global False Discovery ($\text{FDAR}_{\text{global}}$)** | Total durable admissions | $\equiv 0.0\%$ ($0 / N$) | **0 false durable admissions ($0.0\%$)** | **PASS** |
| **Downstream Probes Q1..Q4** | $N = 4 \times N_{\text{admitted}}$ ($400$ queries) | $\equiv 100.0\%$ | **400 / 400 queries ($100.0\%$)** | **PASS** |

## 3. Epistemic Invariants & Scope Ceilings
- **Claim**: In multi-document asynchronous telemetry streams, `gemma3:12b` successfully resolves aliases against a pre-registered canonical entity registry and enables bitemporal fusion and supersession without false merges ($\text{FDAR} \equiv 0.0\%$).
- **Occurrence Splitting**: Conflicting overlapping telemetry $[5.0, 7.0]$ cleanly supersedes historical occurrence $[5.0, 10.0]$ from $t_v = 5.0$ while preserving un-superseded future tail $[7.0, 10.0]$ as a distinct active occurrence.
- **Exclusions**: Does NOT claim unconstrained open-world entity induction or autonomous ontology expansion (unresolvable novel mentions trigger safe `DEFER`/`UNRESOLVED`). Predicate definitions remain fixed.
