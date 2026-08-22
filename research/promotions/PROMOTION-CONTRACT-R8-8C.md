---
promotion_id: PROMOTION-CONTRACT-R8-8C
contract_id: CONTRACT-R8-8C
status: REVISED_CONTRACT_REQUIRED
candidate_sha: 7b781ff553333cbfe7ec07b9087a5528d4a09016
generated_at: "2026-08-22 02:04:00Z"
repair_rounds: 0
reviewed_by: chatgpt-pro
authorized_by: human
---

# Promotion Record: PROMOTION-CONTRACT-R8-8C (Open-World Entity Induction & Epistemic Deferral)

**Lifecycle Status**: `REVISED_CONTRACT_REQUIRED` (Falsified Confirmatory Checkpoint Preserved; Revised Contract Required)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8C`
- **Phase / Milestone**: Exploration Round 8 Stage 8C Confirmatory Benchmark
- **Candidate Branch**: `mb/CONTRACT-R8-8C`
- **Scientific Candidate Commit SHA**: `7b781ff9286d9b4b0e5ee05c0ec2826cfdb3c19e`
- **Execution Base SHA**: `352a16d80429f4bc07455d315efcf9509ee15bb8`
- **Contract Acceptance Verifier**: `FAIL` (`python -m gene.benchmarks.r8_stage8c.verifier` evaluated all 7 preregistered gates; Gates 3, 4, 7 passed; Gates 1, 2, 5 (paired), 6 failed)
- **Evidence Package**: Committed and verified in tree:
  - `data/r8_stage8c_candidate_evidence.jsonl` (120 sequential document decisions on `gemma3:12b`, SHA256: `655d491d...`)
  - `data/r8_stage8c_summary.json` (Canonical metrics summary, SHA256: `a937fc1e...`)
  - `data/r8_stage8c_evidence_manifest.json` (Full content-addressed evidence manifest)
  - `data/r8_stage8c_registry.sqlite` (Sequential registry SQLite database)
- **Scientific Review Desk Verdict**: `REVISED_CONTRACT_REQUIRED`
- **Human Director Verdict**: `REVISED_CONTRACT_REQUIRED` (Preserve `7b781ff` as durable negative result; burn 60 evaluation worlds; draft R1 with fresh worlds)

## 2. Confirmatory Estimands & 7-Gate Outcome Breakdown

| Gate / Estimand | Pre-registered Condition / Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Gate 1: Neural Proposal Quality** | Overall $\ge 90.0\%$ ($108 / 120$); Min Arm $\ge 80.0\%$ | **83 / 120 ($69.2\%$)**; Min Arm: **$36.7\%$** | **FAIL** |
| **Gate 2: Durable False Merge Floor ($\text{FDAR}_{\text{merge}}$)** | $\equiv 0.0\%$ ($0 / 120$) false merges | **2 / 120 ($1.67\%$)** false merges | **FAIL** |
| **Gate 3: Provisional Entity Fragmentation Floor** | $0 / 30$ duplicate provisional entities | **0 / 30 duplicates ($0.0\%$)** | **PASS** |
| **Gate 4: Ambiguous Deferral Accuracy** | $\ge 85.0\%$ ($13 / 15$) on ungrounded bare mentions | **13 / 15 ($86.7\%$)** deferred | **PASS** |
| **Gate 5: Delayed Resolution Recovery** | Paired $\text{DEFER} \to \text{RESOLVE} \ge 80.0\%$ ($6 / 7$) | **4 / 7 paired ($57.1\%$)** [Unconditioned Doc 2: $6/7$ ($85.7\%$)] | **FAIL** |
| **Gate 6: Useful Resolvable Coverage** | $\ge 85.0\%$ ($83 / 97$) across non-bare mentions | **72 / 97 ($74.2\%$)** useful coverage | **FAIL** |
| **Gate 7: Database & Graph Invariant** | Clean SQLite state, zero cyclic lineages | **SQLite & Graph Integrity True** | **PASS** |

## 3. Failure Analysis & Scientific Insights

### 1. The Canonicalization Pressure Hazard
The model exhibited strong lexical attraction to known entity names embedded within unseen composite descriptors:
- **Case W59-D1 (Arm 4B)**: `"Cluster One Enclave"` in Doc 1 $\to$ neural proposal `EXISTING LINK compute_cluster_1` (confidence 0.95) $\to$ durable false merge.
- **Case W60-D1 (Arm 4B)**: `"SAN Alpha Unit"` in Doc 1 $\to$ neural proposal `EXISTING LINK storage_array_alpha` (confidence 0.95) $\to$ durable false merge.

Because the frozen deterministic policy only filtered exact aliases, partition tokens, and digit clashes, it did not block unseen modifiers attached to known entity stems. This demonstrates that in an epistemic system:
> *A known alias embedded inside an unseen composite surface form is not sufficient evidence for identity continuity; absence of proof that the modifier changes identity cannot be treated as proof of identity continuity.*

### 2. Paired Deferral Recovery (Gate 5)
While unconditioned Doc 2 accuracy in Arm 4B was $6/7$ ($85.7\%$), true paired recovery ($\text{DEFER} \to \text{RESOLVE}$) was only $4/7$ ($57.1\%$) because W59 and W60 suffered false merges in Doc 1 rather than deferring, and W54 misfired on Doc 2.

### 3. Verifier Debt Identified for R1
- **Gate 3**: The acceptance verifier should independently reconstruct provisional clusters from the raw SQLite mutation log rather than relying on runner tracking.
- **Gate 7**: Verifier should execute gold-manifest reconciliation against the immutable world specification rather than SQLite PRAGMA checks alone.

## 4. Epistemic Governance Disposition
1. **Preserve Commit `7b781ff`**: Maintained in git history as an immutable confirmatory negative result.
2. **Burn World Set**: All 60 original evaluation worlds are burned to prevent evaluation-driven tuning.
3. **Advance to `CONTRACT-R8-8C-R1`**: Architected around **non-durable identity hypotheses**, multi-source evidence accumulation, and delayed commitment.
