---
promotion_id: PROMOTION-CONTRACT-R8-8B
contract_id: CONTRACT-R8-8B
status: REVISED_CONTRACT_REQUIRED
candidate_sha: 98e556f99bf08207377f0e29c5de3e3cdc1bb400
generated_at: "2026-08-21 23:12:00Z"
repair_rounds: 2
reviewed_by: chatgpt-pro
authorized_by: human
---

# Promotion Record: PROMOTION-CONTRACT-R8-8B (Multi-Document Resolution & Ingress Fusion)

**Lifecycle Status**: `REVISED_CONTRACT_REQUIRED` (Scientific Review Desk & Human Director Disposition)

## 1. Executive Summary & Review Desk Disposition
- **Target Contract**: `CONTRACT-R8-8B`
- **Candidate Commit SHA**: `98e556f99bf08207377f0e29c5de3e3cdc1bb400`
- **Scientific Review Desk Verdict**: `REVISED_CONTRACT_REQUIRED`
- **Disposition**:
  - The 145 live model calls on `gemma3:12b` are preserved as valuable exploratory evidence demonstrating high extraction fidelity, zero false merges ($0/30$), and $100\%$ mention resolution ($60/60$ alias mentions).
  - However, the frozen contract `CONTRACT-R8-8B` contained an internal unit-of-analysis inconsistency (preregistered $N=100$ total gold mentions for $M_3$, while specifying 50 multi-document worlds with $N=60$ alias mentions across 30 worlds, requiring $N=200$ mention slots).
  - Furthermore, Gate 5 requires explicit point-in-time and superseding timeline queries in the conflicting overlap region ($(t_k=2, t_v=6.0)$) and execution of explicit bitemporal `SUPERSEDES` events rather than dual assertions.
  - Therefore, `CONTRACT-R8-8B` is superseded by `CONTRACT-R8-8B-R1.md`.

## 2. Exploratory Pilot Benchmark Evidence (145 Live Calls on `gemma3:12b`)

| Estimand / Metric | Exact Denominator | Pre-registered Floor | Observed Empirical Result | Pilot Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Coreference Recall ($M_{1\text{coref}}$)** | $N = 60$ alias mentions (Cells 2 & 4) | $\ge 85.0\%$ ($51 / 60$) | **60 / 60 ($100.0\%$)** | **VALIDATED** |
| **Candidate Precision ($M_2$)** | Total proposed candidates | $\ge 85.0\%$ | **$100.0\%$** against canonical targets | **VALIDATED** |
| **False Merge Rate** | $N = 30$ distractor trials | $\equiv 0.0\%$ ($0 / 30$) | **0 false merges ($0.0\%$)** | **VALIDATED** |
| **False Split Rate** | $N = 60$ coreference mentions | $\le 5.0\%$ | **0 false splits ($0.0\%$)** | **VALIDATED** |
| **Temporal Correctness (Out-of-Order)** | $N = 50$ temporal queries across $t_k=1,2$ (Cells 3 & 4) | $\ge 90.0\%$ ($45 / 50$) | **50 / 50 ($100.0\%$)** | **VALIDATED** |
| **Useful Admission Coverage ($M_3$)** | $N = 200$ total gold mention slots | $\ge 80.0\%$ ($160 / 200$) | **200 / 200 ($100.0\%$)** admitted & probe-verified | **VALIDATED** |
| **Global False Discovery ($\text{FDAR}_{\text{global}}$)** | Total durable admissions | $\equiv 0.0\%$ ($0 / N$) | **0 false durable admissions ($0.0\%$)** | **VALIDATED** |
| **Downstream Probes Q1..Q4** | Total probe queries | $\equiv 100.0\%$ | **100.0% passed (400/400 queries)** | **VALIDATED** |

## 3. Next Steps: CONTRACT-R8-8B-R1
A revised contract proposal `CONTRACT-R8-8B-R1.md` is drafted with corrected unit formalisms, explicit 4-point bitemporal timeline queries, and fresh sealed evaluation worlds for confirmatory execution.
