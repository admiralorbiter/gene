---
promotion_id: PROMOTION-CONTRACT-R8-8C-R1
contract_id: CONTRACT-R8-8C-R1
status: REVISED_CONTRACT_REQUIRED
candidate_sha: aafd21f66d4dbd2a233633e89551d5ca3a8e0f17
generated_at: "2026-08-22 03:00:00Z"
repair_rounds: 0
reviewed_by: chatgpt-pro
authorized_by: null
---

# Promotion & Scientific Audit Record: CONTRACT-R8-8C-R1 (Non-Durable Hypothesis Ledger & Fail-Closed Ingress)

**Lifecycle Status**: `REVISED_CONTRACT_REQUIRED` (Confirmatory Run Completed; 4/7 Acceptance Gates Passed, 3 Gates Failed on Coverage and Disconfirmation Edge-Cases)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8C-R1`
- **Candidate Branch**: `mb/CONTRACT-R8-8C-R1`
- **Scientific Candidate Commit SHA**: `aafd21f66d4dbd2a233633e89551d5ca3a8e0f17`
- **Execution Base SHA**: `69949528d22736125026df16e91cb39f50e8b2ea`
- **Model Endpoint**: `gemma3:12b` via local Ollama API (`http://127.0.0.1:11434/api/generate`)
- **Evaluation Surface**: 60 Fresh Synthetic Worlds (120 Decisions total across 5 experimental sub-arms)
- **Execution Time**: 553.72s (120 neural inference calls + deterministic guardrail arbitration)
- **Persisted Evidence Package**:
  - `data/r8_stage8c_r1_candidate_evidence.jsonl` (120 decision records with input prompt, neural response, and hybrid resolution)
  - `data/r8_stage8c_r1_summary.json` (Structured benchmark metrics and arm-level statistics)
  - `data/r8_stage8c_r1_registry.sqlite` (Relational SQLite entity registry and provenance edge database)
  - `data/r8_stage8c_r1_evidence_manifest.json` (Content-addressed SHA-256 cryptographic manifest)

---

## 2. Frozen Statistical Gates & Verification Verdicts

| Gate / Estimand | Preregistered Condition / Floor | Observed Result | Statistical Test | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Manifest Integrity** | Cryptographic hash match across all artifacts | SHA-256 Verified | Content digest check | **PASS** |
| **Gate 1: Diagnostic Neural Proposal Quality** | Telemetry tracking only (no ceiling/floor) | **61 / 120 ($50.8\%$)** | Raw accuracy vs gold (world-local binding) | **TELEMETRY** |
| **Gate 2: Hybrid Durable False Merge Floor** | Zero false merges into existing canonical entities ($0.0\%$) | **1 / 120 false merges** ($0.8\%$) | World 53 Contract/Gold conflict | **FAIL** |
| **Gate 3: Provisional Entity Fragmentation** | Zero duplicate provisional entities for same real-world entity | **0 duplicates across provisionals** | Duplicate name check | **PASS** |
| **Gate 4: Permanent Non-Resolution Invariant** | Non-durable deferral across both documents in Sub-Arm 4A | **7 / 8 worlds ($87.5\%$)** | Floor $\ge 7/8$ ($87.5\%$) | **PASS** |
| **Gate 5: Evidence Accumulation & Disconfirmation** | - Doc 2 Resolution $\ge 6/7$<br>- Zero premature Doc 1 mutations<br>- Clean Retargeting ($3/3$) | - Doc 2: $6/7$ ($85.7\%$)<br>- 0 premature mutations<br>- Retarget: $1/3$ ($33.3\%$) | Multi-criteria invariant | **FAIL** |
| **Gate 6: Useful Resolvable Coverage** | Hybrid accuracy on resolvable entities ($N=97$) | **76 / 97 ($78.4\%$)** | Floor $\ge 85.0\%$ ($N=97$) | **FAIL** |
| **Gate 7: SQLite DB Schema, FKs & Reconciliation** | `PRAGMA foreign_key_check`, `integrity_check`, and entity reconciliation | 0 FK violations, PRAGMA ok, full ledger audit | SQLite integrity & ledger check | **PASS** |

---

## 3. Arm-by-Arm Empirical Breakdown (Rescored with World-Local Provisional Identity Binding)

| Experimental Sub-Arm | Total Decisions | Neural Proposal Accuracy | Hybrid Resolution Accuracy | Primary Characteristic |
| :--- | :--- | :--- | :--- | :--- |
| **Arm 1: Novel Standalone Entities** | 30 decisions (15 worlds) | 8 / 30 ($26.7\%$) | 12 / 30 ($40.0\%$) | Gemma emitted `DEFER` on 9/15 worlds without parentheticals; hybrid policy failed closed |
| **Arm 2: Known Exact Aliases** | 30 decisions (15 worlds) | 30 / 30 ($100.0\%$) | 30 / 30 ($100.0\%$) | $100\%$ precision on canonical alias linking |
| **Arm 3: Partition / Sibling Nodes** | 30 decisions (15 worlds) | 0 / 30 ($0.0\%$) | **28 / 30 ($93.3\%$)** | Deterministic partition guardrail intercepted and resolved partitions cleanly |
| **Arm 4A: Permanent Deferral (Ambiguous)** | 16 decisions (8 worlds) | 12 / 16 ($75.0\%$) | 14 / 16 ($87.5\%$) | World 53 (`Tensor Pod Three Sub-Unit`) triggered partition creation instead of deferral |
| **Arm 4B: Deferred $\to$ Resolved (Evidence)** | 14 decisions (7 worlds) | 11 / 14 ($78.6\%$)| 13 / 14 ($92.9\%$) | Zero premature Doc 1 mutations; clean Doc 2 resolution on 6/7 worlds |

---

## 4. Scientific Audit & Benchmark Findings
1. **World 53 Contract/Gold Specification Conflict**:
   - The frozen deterministic policy defines `"sub-unit"` as a structural partition marker $\implies$ `CREATE_PROVISIONAL`.
   - Gold manifest in World 53 (`Tensor Pod Three Sub-Unit`) specified `DEFER`.
   - The runner executed the frozen deterministic partition rule as specified in the contract. While not a false canonical merge, this represents a benchmark/contract inconsistency that will be resolved in R2.
2. **Mechanistic Confirmation of the Hypothesis Layer**:
   - Zero premature durable mutations occurred across all 60 worlds.
   - Hypothesis accumulation allowed 6/7 Arm 4B worlds to resolve cleanly upon arriving Document 2 evidence.
   - Disconfirmation successfully retargeted the entity without leaving durable residue.
3. **Disposition**: Candidate remains `REVISED_CONTRACT_REQUIRED` (non-promotable under R1). Preparing R2 architecture around risk-tiered epistemic authority: explicit evidence for provisional existence without requiring neural `NOVEL`, grounded partition sub-identifiers, and optional candidate targets in unresolved hypotheses (`candidate_target = null`).
