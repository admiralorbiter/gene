---
promotion_id: PROMOTION-CONTRACT-R8-8C
contract_id: CONTRACT-R8-8C
status: CANDIDATE
candidate_sha: 7b781ff9286d9b4b0e5ee05c0ec2826cfdb3c19e
generated_at: "2026-08-22 02:04:00Z"
repair_rounds: 0
reviewed_by: chatgpt-pro
authorized_by: null
---

# Promotion Candidate Record: PROMOTION-CONTRACT-R8-8C (Open-World Entity Induction & Epistemic Deferral)

**Lifecycle Status**: `CANDIDATE` (Awaiting Scientific Promotion Review by Review Desk & Strategic Authorization)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8C`
- **Phase / Milestone**: Exploration Round 8 Stage 8C Confirmatory Benchmark
- **Candidate Branch**: `mb/CONTRACT-R8-8C`
- **Scientific Candidate Commit SHA**: `7b781ff9286d9b4b0e5ee05c0ec2826cfdb3c19e`
- **Execution Base SHA**: `352a16d80429f4bc07455d315efcf9509ee15bb8`
- **Contract Acceptance Verifier**: `FAIL` (`python -m gene.benchmarks.r8_stage8c.verifier` evaluated all 7 preregistered gates; Gates 3, 4, 5, 7 passed; Gates 1, 2, 6 failed)
- **Evidence Package**: Committed and verified in tree:
  - `data/r8_stage8c_candidate_evidence.jsonl` (120 sequential document decisions on `gemma3:12b`, SHA256: `655d491d...`)
  - `data/r8_stage8c_summary.json` (Canonical metrics summary, SHA256: `a937fc1e...`)
  - `data/r8_stage8c_evidence_manifest.json` (Full content-addressed evidence manifest)
  - `data/r8_stage8c_registry.sqlite` (Sequential registry SQLite database)
- **Repair Iterations**: 0 rounds (clean first-pass confirmatory run on frozen contract).

## 2. Confirmatory Estimands & 7-Gate Outcome Breakdown

| Gate / Estimand | Pre-registered Condition / Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Gate 1: Neural Proposal Quality** | Overall $\ge 90.0\%$ ($108 / 120$); Min Arm $\ge 75.0\%$ | **83 / 120 ($69.2\%$)**; Min Arm: **$36.7\%$** | **FAIL** |
| **Gate 2: Durable False Merge Floor ($\text{FDAR}_{\text{merge}}$)** | $\equiv 0.0\%$ ($0 / 120$) false merges | **2 / 120 ($1.67\%$)** false merges | **FAIL** |
| **Gate 3: Provisional Entity Fragmentation Floor** | $0 / 30$ duplicate provisional entities | **0 / 30 duplicates ($0.0\%$)** | **PASS** |
| **Gate 4: Ambiguous Deferral Accuracy** | $\ge 85.0\%$ ($13 / 15$) on ungrounded bare mentions | **13 / 15 ($86.7\%$)** deferred | **PASS** |
| **Gate 5: Delayed Resolution Recovery** | $\ge 80.0\%$ ($6 / 7$) resolved upon clarification | **6 / 7 ($85.7\%$)** recovered | **PASS** |
| **Gate 6: Useful Resolvable Coverage** | $\ge 85.0\%$ ($83 / 97$) across non-bare mentions | **72 / 97 ($74.2\%$)** useful coverage | **FAIL** |
| **Gate 7: Database & Graph Invariant** | Clean SQLite state, zero cyclic lineages | **SQLite & Graph Integrity True** | **PASS** |

## 3. Detailed Failure Analysis & Diagnostic Observations

### 1. Gate 2 False Merges ($2 / 120 = 1.67\%$)
- **Case W59-D1 (Arm 4B)**: Mention `"Cluster One Enclave"` in Doc 1 (ungrounded initial report) was proposed by the neural model as `EXISTING LINK compute_cluster_1` without triggering an exact alias match, leading to an early merge prior to Doc 2's explicit clarification.
- **Case W60-D1 (Arm 4B)**: Mention `"SAN Alpha Unit"` in Doc 1 was similarly proposed as `EXISTING LINK storage_array_alpha` prior to Doc 2's explicit disambiguation.

### 2. Gate 1 Neural Proposal Accuracy ($69.2\%$) & Gate 6 Resolvable Coverage ($74.2\%$)
- In Arm 1 (Novel Entities), the raw neural model frequently misclassified novel provisional hardware as ambiguous or attempted to link ungrounded tokens, yielding $36.7\%$ raw neural accuracy in Arm 1 (rescued down the pipeline by deterministic guardrails to 0 fragmentation).
- In Arm 3 (Near-Collisions & Partitions), the raw neural proposal attempted parent linking on partition mentions, which the deterministic syntax guardrails successfully intercepted and redirected to provisional partition entries.

## 4. Epistemic Status & Governance Boundary
- **Epistemic Disposition**: The candidate run cleanly proves the feasibility of deterministic epistemic deferral (Gate 4: $86.7\%$, Gate 5: $85.7\%$, Gate 3: $0$ duplicates), but does not satisfy the strict zero-false-merge floor ($\text{FDAR} \equiv 0.0\%$) or raw neural quality floor ($\ge 90.0\%$).
- **Next Governance Step**: Presented to Scientific & Experimental Review Desk for promotion verdict (`REVISED_CONTRACT_REQUIRED` vs mechanical `FIX`).
