---
contract_id: CONTRACT-R8-8C-R2
promotion_id: PROMOTION-CONTRACT-R8-8C-R2
status: CANDIDATE
proposed_by: antigravity
reviewed_by: chatgpt-pro
authorized_by: human
base_sha: f7e178bf979a3ebcec95d4c16269cf43f34cb77b
execution_base_sha: 3694277012da8dae69bf185750d7f51b8d8a9931
candidate_sha: 7f164a5c4015f8be7e1dc58778f6ec4ec250c6ca
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
| **Gate 7** | Relational DB Schema & FK Audit | Integrity OK, 0 FK errors | **Integrity: ok, FK Violations: 0** | **PASS** |

---

## 2. Core Epistemic Findings & Invariant Verification

1. **Safety Floors Are Absolute ($100\%$ Met)**:
   - **Gate 2a**: $0/120$ false merges into canonical entities. Zero canonical registry corruption.
   - **Gate 2b**: $0/120$ false provisional creations on negated or unasserted mentions.
   - **Gate 3**: Zero duplicate provisional entities created within any world.
   - **Gate 4**: $8/8$ non-resolvable adversarial cases deferred without premature durable mutation.
   - **Gate 7**: Relational database passed all SQLite PRAGMA integrity and foreign key constraints.

2. **Root-Cause Analysis of Gate 6 Discrepancy**:
   - In **Arm 1 (Novel Systems)**: Doc 1 created `prov_vector_core_alpha` under Rule 4. However, Doc 2 presented the bare acronym `mention = "VCA"` with `context = "Secondary interface telemetry active on VCA (Vector Core Alpha)"`. Because `runner.py` only checked parentheticals inside `mention` rather than extracting context parentheticals `(Vector Core Alpha)`, Doc 2 fell through to Rule 5 (`DEFER`) instead of linking to the created provisional entity.
   - In **Arm 3 (Structural Partitions)**: Doc 1 created `prov_cc_4_node_12`. In Doc 2, Rule 2 re-evaluated before Rule 1 could link to the registered provisional partition.
   - In **Arm 4B (World 55)**: `mention = "SAN Alpha Mirror Pool (SAN-Beta)"` matched the structural partition keyword `"pool"`, triggering structural first refusal instead of parenthetical canonical linking to `storage_array_beta`.

---

## 3. Implementation Auditor Verdict

- **Disposition**: `CANDIDATE` presented with audit verdict `FIX` (Mechanical Context-Parenthetical Extraction & Partition Alias Linking).
- **Provenance**: Candidate branch `mb/CONTRACT-R8-8C-R2` pinned at commit `7f164a5c4015f8be7e1dc58778f6ec4ec250c6ca`.
