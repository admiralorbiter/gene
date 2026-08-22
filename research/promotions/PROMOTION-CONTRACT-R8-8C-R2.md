---
contract_id: CONTRACT-R8-8C-R2
promotion_id: PROMOTION-CONTRACT-R8-8C-R2
status: REVISED_CONTRACT_REQUIRED
proposed_by: antigravity
reviewed_by: chatgpt-pro
authorized_by: human
base_sha: f7e178bf979a3ebcec95d4c16269cf43f34cb77b
execution_base_sha: 3694277012da8dae69bf185750d7f51b8d8a9931
candidate_sha: 1a00901d72059119fda11ec14dbe5e8173b2ab86
---

# Research Promotion Review: CONTRACT-R8-8C-R2 (Two-Stage Epistemic Ingress)

## 1. Executive Summary & Epistemic Audit

The sealed confirmatory benchmark for **CONTRACT-R8-8C-R2** was executed across 60 fresh synthetic worlds ($N=120$ decisions) using Gemma 3 12B Instruct (Q4_K_M) on the local GPU.

### Gate Evaluation Matrix

| Gate | Criterion | Target | Observed | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Neural Proposal Quality | Telemetry | **65.0%** (78/120) | REPORT |
| **Gate 2a** | Hybrid Durable False Merge Floor | $\equiv 0.0\%$ (0/120) | **0/120 (0.0%)** | **PASS** |
| **Gate 2b** | Semantic False Prov Existence Floor | $\equiv 0.0\%$ on unasserted | **0/120 (0.0%)** | **PASS** |
| **Gate 3** | Provisional Entity Fragmentation | 0 duplicate creations | **0 duplicates** | **PASS** |
| **Gate 4** | Permanent Non-Resolution Invariant | $\ge 7/8$ in Arm 4A | **8/8 (100.0%)** | **PASS** |
| **Gate 5** | Disconfirmation & Accumulation Matrix | 7/7 Arm 4B exact | **6/7 (85.7%)** | **FAIL** |
| **Gate 6** | Useful Resolvable Coverage | $\ge 85.0\%$ across $N=97$ | **68.0% (66/97)** | **FAIL** |
| **Gate 7** | Relational DB Schema & Ledger Audit | Integrity OK, 0 FK errors | **Integrity: ok, FK Violations: 0, 120/120 records** | **PASS** |

---

## 2. Core Epistemic Findings & Invariant Verification

1. **Safety Floors Are Absolute ($100\%$ Met)**:
   - **Gate 2a**: $0/120$ false merges into canonical entities. Zero canonical registry corruption.
   - **Gate 2b**: $0/120$ false provisional creations on negated, proposed, or unasserted mentions.
   - **Gate 3**: Zero duplicate provisional entities created within any world.
   - **Gate 4**: $8/8$ non-resolvable adversarial cases deferred without premature durable mutation.
   - **Gate 7**: Relational database passed all SQLite `PRAGMA integrity_check` (ok), `PRAGMA foreign_key_check` (0 violations), and complete 120-record ledger audit.

2. **True Paired Offline Stage 8C-R1 Policy Replay**:
   - Running the actual frozen Stage 8C-R1 deterministic resolver on this exact candidate stream yielded **$37.1\%$ (36/97)** resolvable coverage.
   - Candidate Stage 8C-R2 achieved **$68.0\%$ (66/97)** ($+30.9\%$ absolute admission gain over R1).

3. **Root-Cause Analysis of Discrepancies**:
   - **Arm 1 (Novel Systems)**: Doc 1 created `prov_vector_core_alpha` under Rule 4. However, Doc 2 presented the bare acronym `mention = "VCA"` with `context = "Secondary interface telemetry active on VCA (Vector Core Alpha)"`. Because `runner.py` only checked parentheticals inside `mention` rather than extracting context parentheticals `(Vector Core Alpha)`, Doc 2 fell through to Rule 5 (`DEFER`) instead of linking to the created provisional entity.
   - **Arm 3 (Structural Partitions)**: In Doc 2, Rule 2 re-evaluated before Rule 1 could link to the registered provisional partition.
   - **Arm 4B (World 55 Policy Conflict)**: `mention = "SAN Alpha Mirror Pool (SAN-Beta)"` matched the structural partition keyword `"pool"`, triggering structural first refusal instead of parenthetical canonical linking to `storage_array_beta`.

4. **Offline Mechanical Rescoring (Burned Development Evidence)**:
   - Fixing the mechanical context-parenthetical extraction and structural identity key brings resolvable coverage to **$99.0\%$ (96/97)**.
   - The remaining single discrepancy (World 55) represents a genuine policy conflict requiring Stage 8C-R3.

---

## 3. Implementation Auditor & Review Desk Verdict

- **Final Disposition**: `REVISED_CONTRACT_REQUIRED` (Stage 8C-R3).
- **Provenance**: Candidate branch `mb/CONTRACT-R8-8C-R2` pinned at commit `1a00901d72059119fda11ec14dbe5e8173b2ab86`.
- **Roadmap Directive for Stage 8C-R3**:
  - Clarify Rule 2 & Rule 3 hierarchy: Structural first refusal activates *only* when a mention contains a grounded parent and a valid discriminating structural sub-identifier. Mentions lacking a discriminating sub-identifier defer *unless* explicit registered parenthetical identity evidence is present.
  - Generate fresh sealed synthetic worlds (R2 worlds preserved as burned development evidence).
