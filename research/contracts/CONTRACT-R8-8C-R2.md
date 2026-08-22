---
contract_id: CONTRACT-R8-8C-R2
status: DRAFT
proposed_by: antigravity
design_review: null
reviewed_by: chatgpt-pro
authorized_by: null
base_sha: 69949528d22736125026df16e91cb39f50e8b2ea
execution_base_sha: null
resource_class: local_gpu
long_running: true
exclusive_gpu: true
interruptible: false
---

# Research Contract Proposal: CONTRACT-R8-8C-R2 (Two-Stage Epistemic Ingress: Existence vs Identity Decoupling)

## Title
Stage 8C-R2 Confirmatory Benchmark: Two-Stage Epistemic Ingress via Existence vs Identity Decoupling, Grounded Structural Partitions, and Nullable Hypothesis Candidates

## 1. Context & Research Problem
In `PROMOTION-CONTRACT-R8-8C-R1` (rescored with world-local identity binding), the hybrid epistemic architecture established:
- Zero canonical false merges ($0/120, 0.0\%$, Gate 2 PASS).
- Zero provisional entity fragmentation (Gate 3 PASS).
- 93.3% accuracy on structural partitions ($28/30$, Arm 3) and 100% on canonical alias linking ($30/30$, Arm 2).
- Zero premature mutations on Document 1 and 92.9% resolution on Document 2 ($13/14$, Arm 4B).

However, R1 revealed two structural boundaries:
1. **Conflating Existence with Identity (Arm 1 Coverage Bottleneck)**:
   In Arm 1, documents explicitly establish the existence of newly deployed hardware (e.g. `"Initial deployment of Vector Core Alpha initiated in datacenter hall B"`). But because Gemma 3 12B often defaulted to `DEFER` on bare standalone names without parentheticals, the R1 hybrid policy failed closed into deferral ($12/30, 40.0\%$), blocking legitimate provisional creation.
2. **Ambiguous Partition Markers (World 53)**:
   R1 treated bare structural markers (`"sub-unit"`) as sufficient for partition creation, conflicting with gold benchmarks when distinct sub-identifiers were absent (`"Tensor Pod Three Sub-Unit"`).
3. **Forced Candidate Targets in Hypotheses**:
   R1 required hypotheses to have a non-null `candidate_target`, causing unevidenced composites without clear stems (World 59/60) to bypass hypothesis tracking.

---

## 2. Core Epistemic Architecture for Stage 8C-R2

### Principle A: Decouple Existence Authority from Identity Authority
- **Question 1: Does strong evidence establish that a distinct object EXISTS?**
  Explicit deployment, commissioning, provisioning, or standalone hardware assertions in the source document provide sufficient evidence of existence to authorize **reversible provisional entity creation** (`CREATE_PROVISIONAL`), without requiring neural model keyword agreement.
- **Question 2: Does strong evidence establish CANONICAL IDENTITY?**
  Strict whole-field exact matching or explicit identifying parenthetical corroboration is required to authorize a durable canonical `LINK`.

```
                    [Document Mention Ingress]
                                │
         ┌──────────────────────┴──────────────────────┐
         ▼                                             ▼
[Evidence of Existence]                      [Evidence of Identity]
- Deployment / Commissioning notice          - Exact registered alias match
- Standalone hardware assertion              - Explicit parenthetical corroboration
         │                                             │
         ▼                                             ▼
[CREATE_PROVISIONAL (Reversible)]             [LINK to Canonical / Provisional]
```

### Principle B: Grounded Structural Partition Grammar
A partition provisional creation requires three conjuncts:
1. **Grounded Parent**: A recognized canonical entity stem (e.g. `"Compute Cluster 1"`).
2. **Structural Marker**: Partition syntax keyword (`"Partition"`, `"Shelf"`, `"Pool"`, `"Blade"`, `"Bay"`).
3. **Distinct Sub-Identifier**: Explicit alphanumeric designator (e.g. `"1-A"`, `"Shelf 1"`, `"Pool 3"`, `"Blade 5"`).

If a mention contains parent + marker but **lacks a distinct sub-identifier** (e.g. `"Tensor Pod Three Sub-Unit"`), it is classified as an ambiguous composite and tracked as an `UNRESOLVED` hypothesis without mutating the registry.

### Principle C: First-Class Nullable Hypothesis Candidates
The hypothesis ledger supports unevidenced composites natively:
$$\text{Hypothesis}(\text{surface\_form}, \text{candidate\_target} = \text{null}, \text{status} = \text{UNRESOLVED})$$
When subsequent corroborating or clarifying evidence arrives in Document 2:
- **Confirmation**: Links to candidate (if candidate existed and matches).
- **Retargeting**: Links to existing canonical entity.
- **Novelty Establishment**: Creates new provisional entity if explicit novelty text arrives.
- **Permanent Deferral**: Remains unresolved if no new evidence is provided.

---

## 3. Confirmatory Experimental Protocol & Statistical Gates

### Evaluation Benchmark
- 60 Fresh Synthetic Worlds (120 Decisions total across 5 sub-arms):
  - **Arm 1: Novel Standalone Entities** (15 worlds, 30 decisions)
  - **Arm 2: Known Exact Aliases** (15 worlds, 30 decisions)
  - **Arm 3: Grounded Structural Partitions** (15 worlds, 30 decisions)
  - **Arm 4A: Permanent Deferral (Ambiguous & Sub-Identifier Lacking)** (8 worlds, 16 decisions)
  - **Arm 4B: Deferred $\to$ Resolved (Evidence Accumulation)** (7 worlds, 14 decisions)

### Frozen Acceptance Gates

| Gate | Name | Preregistered Condition / Floor | Epistemic Significance |
| :--- | :--- | :--- | :--- |
| **Gate 1** | Diagnostic Neural Proposal Quality | Telemetry report-only (no floor/ceiling) | Diagnoses raw Gemma 3 12B baseline |
| **Gate 2** | Hybrid Durable False Merge Floor | $\text{FDAR}_{\text{merge}} \equiv 0.0\%$ (0/120 canonical false merges) | Zero durable false merges into existing canonical entities |
| **Gate 3** | Provisional Entity Fragmentation | 0 duplicate creations across all worlds | Prevents multiple provisional IDs for same entity within a world |
| **Gate 4** | Permanent Non-Resolution Invariant | $\ge 7/8$ worlds ($87.5\%$) in Sub-Arm 4A | Both Doc 1 and Doc 2 remain non-durable |
| **Gate 5** | Evidence Accumulation & Disconfirmation | - Doc 2 Resolution $\ge 6/7$<br>- Zero premature Doc 1 mutations<br>- Clean Retargeting ($3/3$, 0 residue) | Validates hypothesis lifecycle and non-durable accumulation |
| **Gate 6** | Useful Resolvable Coverage | $\ge 85.0\%$ across $N=97$ resolvable decisions | Solves Arm 1 & Arm 3 coverage bottleneck |
| **Gate 7** | Relational DB Schema & Ledger Audit | `PRAGMA integrity_check` (ok), FK check (0 violations), Full Ledger reconciliation | Verifies relational integrity and complete ledger audit trail |

---

## 4. Architectural Boundaries & Fail-Closed Invariants
- All 60 evaluation worlds execute with isolated `EpistemicIngressSession` instances.
- World-local semantic provisional identity binding is permanently integrated into the verifier.
- Acceptance requires satisfying all 6 mandatory gates (Gates 2–7).
