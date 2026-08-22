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
| **Gate 1: Diagnostic Neural Proposal Quality** | Telemetry tracking only (no ceiling/floor) | 53 / 120 ($44.2\%$) | Raw accuracy vs gold | **TELEMETRY** |
| **Gate 2: Hybrid Durable False Merge Floor** | Zero false merges into existing canonical entities ($0.0\%$) | **1 / 120 false merges** ($0.8\%$) | Fail-closed check (World 53) | **FAIL** |
| **Gate 3: Provisional Entity Fragmentation** | Zero duplicate provisional entities for same real-world entity | **0 duplicates across 4 provisionals** | Duplicate name check | **PASS** |
| **Gate 4: Permanent Non-Resolution Invariant** | Non-durable deferral across both documents in Sub-Arm 4A | **7 / 8 worlds ($87.5\%$)** | Floor $\ge 7/8$ ($87.5\%$) | **PASS** |
| **Gate 5: Evidence Accumulation & Disconfirmation** | - Doc 2 Resolution $\ge 6/7$<br>- Zero premature Doc 1 mutations<br>- Clean Retargeting ($3/3$) | - Doc 2: $6/7$ ($85.7\%$)<br>- 0 premature mutations<br>- Retarget: $1/3$ ($33.3\%$) | Multi-criteria invariant | **FAIL** |
| **Gate 6: Useful Resolvable Coverage** | Hybrid accuracy on resolvable entities ($N=97$) | **36 / 97 ($37.1\%$)** | Floor $\ge 85.0\%$ ($N=97$) | **FAIL** |
| **Gate 7: SQLite DB Schema & Foreign Keys** | `PRAGMA foreign_key_check` and `PRAGMA integrity_check` | 0 FK violations, PRAGMA ok | SQLite integrity check | **PASS** |

---

## 3. Arm-by-Arm Empirical Breakdown

| Experimental Sub-Arm | Total Decisions | Neural Proposal Accuracy | Hybrid Resolution Accuracy | Primary Failure Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Arm 1: Novel Standalone Entities** | 30 decisions (15 worlds) | 0 / 30 ($0.0\%$) | 0 / 30 ($0.0\%$) | Neural model proposed `DEFER` on 11/15 worlds; hybrid policy deferred (blocking provisional creation) |
| **Arm 2: Known Exact Aliases** | 30 decisions (15 worlds) | 30 / 30 ($100.0\%$) | 30 / 30 ($100.0\%$) | None — $100\%$ precision on canonical aliases |
| **Arm 3: Partition / Sibling Nodes** | 30 decisions (15 worlds) | 0 / 30 ($0.0\%$) | 0 / 30 ($0.0\%$) | Neural model proposed false merges; guardrails intercepted some, but coverage remained low |
| **Arm 4A: Permanent Deferral (Ambiguous)** | 16 decisions (8 worlds) | 12 / 16 ($75.0\%$) | 14 / 16 ($87.5\%$) | World 53 (`Tensor Pod Three Sub-Unit`) triggered partition creation instead of deferral |
| **Arm 4B: Deferred $\to$ Resolved (Evidence)** | 14 decisions (7 worlds) | 11 / 14 ($78.6\%$)| 13 / 14 ($92.9\%$) | World 60 lacked explicit novelty keyword in context $\to$ deferred |

---

## 4. Scientific Conclusion & Epistemic Boundaries
1. **The Epistemic Hypothesis Layer Works Mechanistically**:
   - Zero premature durable mutations occurred on Document 1 across all 60 worlds.
   - Hypothesis accumulation and non-durable tracking allowed 6/7 Arm 4B worlds to resolve cleanly upon arriving Document 2 corroboration.
2. **The Coverage Bottleneck in Gemma 3 12B**:
   - The primary limiting factor is neural proposal accuracy ($44.2\%$), particularly on novel standalone entities (Arm 1) and partition disambiguation (Arm 3), where the model defaulted to `DEFER` or proposed incorrect parent merges.
   - When the neural model emits `DEFER`, the hybrid guardrails fail closed, suppressing durable false merges but sacrificing resolvable coverage ($37.1\%$ vs $85.0\%$ target).
3. **Disposition**: Candidate rejected for promotion under `CONTRACT-R8-8C-R1`. Awaiting Review Desk guidance for Stage 8C-R2 contract revision or prompt/model steering.
