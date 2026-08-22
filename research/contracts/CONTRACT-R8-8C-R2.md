---
contract_id: CONTRACT-R8-8C-R2
status: DRAFT
proposed_by: antigravity
design_review: null
reviewed_by: chatgpt-pro
authorized_by: null
base_sha: f7e178b871cffaf97f1f0a20468962629b3c4349
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
In `PROMOTION-CONTRACT-R8-8C-R1` (checkpointed to durable base `f7e178b`), the hybrid epistemic architecture established:
- Zero canonical false merges ($0/120, 0.0\%$, Gate 2 PASS).
- Zero provisional entity fragmentation (Gate 3 PASS).
- 93.3% accuracy on structural partitions ($28/30$, Arm 3) and 100% on canonical alias linking ($30/30$, Arm 2).
- Zero premature mutations on Document 1 and 92.9% resolution on Document 2 ($13/14$, Arm 4B).

However, R1 identified the following safety and structural boundaries:
1. **Conflating Existence with Identity (Arm 1 Coverage Bottleneck)**:
   In Arm 1, documents explicitly establish the existence of newly deployed hardware (e.g. `"Initial deployment of Vector Core Alpha initiated in datacenter hall B"`). Because Gemma 3 12B often defaulted to `DEFER` on bare standalone names without parentheticals, the R1 hybrid policy failed closed into deferral ($12/30, 40.0\%$), blocking legitimate provisional creation.
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

### Principle B: Grounded Structural Partition Grammar & Literal Precedence
Deterministic evaluation strictly follows this frozen precedence order:
1. **Exact Registered Alias Match**: Whole-field normalized match against durable canonical registry $\implies$ `LINK`.
2. **Parenthetical Corroboration**: Explicit `"Surface (Identifier)"` matching active hypothesis or registered entity $\implies$ `LINK` / `RETARGET`.
3. **Grounded Structural Partition Parse**:
   - Requires ALL THREE conjuncts:
     1. *Grounded Parent*: Exact prefix match to an existing registered canonical entity (e.g. `"Compute Cluster 1"`).
     2. *Structural Marker*: `{"partition", "shelf", "pool", "blade", "bay", "node", "unit", "subunit", "sub-unit", "core", "switch"}`.
     3. *Distinct Sub-Identifier*: Explicit designator matching `\b(shelf|pool|blade|bay|node|unit|core|switch)?\s*([0-9]+[a-z0-9\-_]*|[a-z0-9\-_]+)\b` (e.g. `"1-A"`, `"Shelf 1"`, `"Pool 3"`).
   - If parent + marker exist but **sub-identifier is absent** (e.g. `"Tensor Pod Three Sub-Unit"`), rule transitions directly to `UNRESOLVED` hypothesis without provisional creation.
4. **Standalone Existence Parse**:
   - Matches affirmative deployment/commissioning phrases:
     `{"initial deployment of", "newly installed", "standalone system", "provisioning notice", "commissioned in", "hardware deployment", "new physical device"}`
   - Must NOT contain conditional/negated blockers:
     `{"proposed", "planned", "if deployed", "deployment cancelled", "virtual replica", "testing stub", "concept", "future", "simulation"}`
   - Authorizes `CREATE_PROVISIONAL` for the standalone novel entity.
5. **Unresolved Hypothesis Ledger**:
   - Captures unevidenced composites with `candidate_target = null` or candidate guesses, emitting non-durable `DEFER`.

### Principle C: First-Class Nullable Hypothesis Candidates & World-Local Uniqueness
The hypothesis ledger supports unevidenced composites natively:
$$\text{Hypothesis}(\text{surface\_form}, \text{candidate\_target} = \text{null}, \text{status} = \text{UNRESOLVED})$$
- When subsequent corroborating or clarifying evidence arrives in Document 2:
  - **Confirmation**: Links to candidate (if candidate existed and matches).
  - **Retargeting**: Links to existing canonical entity.
  - **Novelty Establishment**: Creates new provisional entity if explicit novelty text arrives.
  - **Permanent Deferral**: Remains unresolved if no new evidence is provided.
- **World-Local Uniqueness**: Repeated mentions of the same unresolved surface form append evidence to the existing hypothesis record rather than creating duplicate hypothesis entries.

---

## 3. Confirmatory Experimental Protocol & Statistical Gates

### Evaluation Benchmark
- 60 Fresh Synthetic Worlds (120 Decisions total across 5 sub-arms):
  - **Arm 1: Novel Standalone Entities** (15 worlds, 30 decisions)
  - **Arm 2: Known Exact Aliases** (15 worlds, 30 decisions)
  - **Arm 3: Grounded Structural Partitions** (15 worlds, 30 decisions)
  - **Arm 4A: Adversarial Existence Negatives & Permanent Deferrals** (8 worlds, 16 decisions: spans bare ambiguity, ungrounded structural markers without sub-IDs, and conditional/negated existence language)
  - **Arm 4B: Deferred $\to$ Resolved (Evidence Accumulation with Nullable Candidates)** (7 worlds, 14 decisions)

### Frozen Acceptance Gates

| Gate | Name | Preregistered Condition / Floor | Epistemic Significance |
| :--- | :--- | :--- | :--- |
| **Gate 1** | Diagnostic Neural Proposal Quality | Telemetry report-only (no floor/ceiling) | Diagnoses raw Gemma 3 12B baseline |
| **Gate 2a** | Hybrid Durable False Merge Floor | $\text{FDAR}_{\text{merge}} \equiv 0.0\%$ (0/120 canonical false merges) | Zero durable false merges into existing canonical entities |
| **Gate 2b** | False Provisional Existence Floor | $\text{FDAR}_{\text{prov}} \equiv 0.0\%$ (0/16 false provisionals in Arm 4A) | Zero false provisional creations on non-asserted/negated hardware |
| **Gate 3** | Provisional Entity Fragmentation | 0 duplicate creations across all worlds | Prevents multiple provisional IDs for same entity within a world |
| **Gate 4** | Permanent Non-Resolution Invariant | $\ge 7/8$ worlds ($87.5\%$) in Sub-Arm 4A | Both Doc 1 and Doc 2 remain non-durable |
| **Gate 5** | Evidence Accumulation & Disconfirmation | - Doc 2 Resolution $\ge 6/7$<br>- Zero premature Doc 1 mutations<br>- Clean Retargeting ($3/3$, 0 residue)<br>- Nullable Hypothesis Resolution ($2/2$) | Validates hypothesis lifecycle and nullable candidate resolution |
| **Gate 6** | Useful Resolvable Coverage | $\ge 85.0\%$ across $N=97$ resolvable decisions | Solves Arm 1 & Arm 3 coverage bottleneck |
| **Gate 7** | Relational DB Schema & Ledger Audit | `PRAGMA integrity_check` (ok), FK check (0 violations), Full Ledger reconciliation | Verifies relational integrity and complete ledger audit trail |

---

## 4. Sealing Section & Cryptographic Hash Manifest

All Stage 8C-R2 experimental assets are cryptographically sealed prior to execution:

- **Base SHA**: `f7e178b871cffaf97f1f0a20468962629b3c4349`
- **World Generator Seed**: `0x8C8C8C8C_R2`
- **Model Target**: `gemma3:12b` (Ollama digest verified)
- **Prompt Specification**: `src/gene/benchmarks/r8_stage8c_r2/prompts.py`
- **Grammar & State Machine**: `src/gene/benchmarks/r8_stage8c_r2/runner.py`
- **Acceptance Verifier**: `src/gene/benchmarks/r8_stage8c_r2/verifier.py`
