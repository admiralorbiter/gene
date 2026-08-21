---
promotion_id: PROMOTION-CONTRACT-R8-8B
contract_id: CONTRACT-R8-8B
status: CANDIDATE
candidate_sha: 98e556f99bf08207377f0e29c5de3e3cdc1bb400
generated_at: "2026-08-21 23:05:00Z"
repair_rounds: 2
reviewed_by: codex
authorized_by: null
---

# Candidate Promotion Record: PROMOTION-CONTRACT-R8-8B (Revision 2 — Multi-Document Streams & Supersession)

**Lifecycle Status**: `CANDIDATE` (Awaiting Human Director & ChatGPT Pro Promotion Review)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8B`
- **Phase / Milestone**: Exploration Round 8 Stage 8B (Multi-Document Entity Resolution & Temporal Ingress Fusion)
- **Candidate Branch**: `mb/CONTRACT-R8-8B`
- **Candidate Commit SHA**: `98e556f99bf08207377f0e29c5de3e3cdc1bb400`
- **Contract Acceptance Verifier**: `PASS` (`scripts/verify_contract_r8_8b.py` executed with zero runner booleans, structural invariants on multi-document streams, and independent bitemporal supersession replay)
- **Auditor Verdict**: `PASS` (All 8 Estimands, Factorial Grid, Bitemporal Supersession Queries, and Distractor Falsification Controls verified across 145 live `gemma3:12b` calls)
- **Repair Iterations**: 2 rounds (Instantiated genuine multi-document streams with 2 documents per world; verified point-in-time and superseding timelines across 25 out-of-order worlds; audited exact $N=60$ coreference mentions).

## 2. Benchmark Verification & Estimands Audit

| Estimand / Metric | Exact Denominator | Pre-registered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Coreference Recall ($M_{1\text{coref}}$)** | $N = 60$ alias mentions (Cells 2 & 4) | $\ge 85.0\%$ ($51 / 60$) | **60 / 60 ($100.0\%$)** | **PASS** |
| **Candidate Precision ($M_2$)** | Total proposed candidates | $\ge 85.0\%$ | **$100.0\%$** against canonical targets | **PASS** |
| **False Merge Rate** | $N = 30$ distractor trials | $\equiv 0.0\%$ ($0 / 30$) | **0 false merges ($0.0\%$)** | **PASS** |
| **False Split Rate** | $N = 60$ coreference mentions | $\le 5.0\%$ | **0 false splits ($0.0\%$)** | **PASS** |
| **Temporal Correctness (Out-of-Order)** | $N = 50$ temporal queries across $t_k=1,2$ (Cells 3 & 4) | $\ge 90.0\%$ ($45 / 50$) | **50 / 50 ($100.0\%$)** | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $N = 200$ total gold mention slots | $\ge 80.0\%$ ($160 / 200$) | **200 / 200 ($100.0\%$)** admitted & probe-verified | **PASS** |
| **Global False Discovery ($\text{FDAR}_{\text{global}}$)** | Total durable admissions | $\equiv 0.0\%$ ($0 / N$) | **0 false durable admissions ($0.0\%$)** | **PASS** |
| **Downstream Probes Q1..Q4** | Total probe queries | $\equiv 100.0\%$ | **100.0% passed (400/400 queries)** | **PASS** |

## 3. Epistemic Invariants & Scope Ceilings
- **Claim**: In multi-document asynchronous telemetry streams, `gemma3:12b` successfully resolves aliases and partial mentions against a pre-registered canonical entity registry and performs safe bitemporal fusion and supersession without false merges ($\text{FDAR} \equiv 0.0\%$).
- **Exclusions**: Does NOT claim unconstrained open-world entity induction or autonomous ontology expansion (unresolvable novel mentions trigger safe `DEFER`/`UNRESOLVED`). Predicate definitions remain fixed.
