---
contract_id: CONTRACT-R8-8C-R1
status: DRAFT
proposed_by: antigravity
design_review: null
reviewed_by: chatgpt-pro
authorized_by: null
base_sha: 352a16d80429f4bc07455d315efcf9509ee15bb8
execution_base_sha: null
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
---

# Research Contract Proposal: CONTRACT-R8-8C-R1 (Non-Durable Identity Hypotheses & Delayed Commitment Under Streaming Feeds)

## Title
Stage 8C-R1: Non-Durable Identity Hypotheses, Multi-Source Evidence Accumulation, and Delayed Commitment Under Streaming Multi-Document Feeds

## 1. Context & Research Question
In Stage 8C (`PROMOTION-CONTRACT-R8-8C`), GENE tested autonomous open-world entity induction and epistemic deferral. While epistemic deferral for bare generic tokens succeeded ($86.7\%$ Gate 4) and provisional entity fragmentation remained at zero ($0/30$ Gate 3), the confirmatory run revealed a critical failure mode: **canonicalization pressure on composite surface forms**.

When presented with unseen composite mentions containing known entity names (e.g. `"Cluster One Enclave"`, `"SAN Alpha Unit"`), the neural model exhibited strong lexical attraction to the known stem and proposed immediate canonical links, which bypassed the initial deterministic guardrails and produced 2 durable false merges ($1.67\%$).

Stage 8C-R1 tests the core architectural remedy: **Propose Early, Commit Late via Non-Durable Identity Hypotheses**.

```
EPISTEMIC INGRESS PIPELINE (Stage 8C-R1):
Incoming Stream Mention x_t
        │
        ├── 1. Exact Registered Alias? ──────────► Immediate Durable LINK
        │
        ├── 2. Preregistered Partition Syntax? ──► Link to Provisional Partition / Block Merge
        │
        ├── 3. Bare Generic Token? ──────────────► Epistemic DEFER (durable_mutation: NONE)
        │
        └── 4. Unseen Composite with Known Stem? 
                    │
                    ▼
          [NON-DURABLE IDENTITY HYPOTHESIS]
          candidate_target = canonical_id
          status           = UNRESOLVED_HYPOTHESIS
          evidence_count   = 1
          durable_mutation = NONE (Canonical Registry Remains Pristine)
                    │
                    │ Subsequent Corroborating Stream Evidence Arrives
                    ▼
          [EVIDENCE ACCUMULATION GATE]
          Corroborating context / parent confirmation present?
          ├── YES ──► Promote Hypothesis to Durable LINK
          └── NO  ──► Retain Non-Durable Status / Clean Isolation
```

### Core Research Question
Does decoupling non-durable identity hypothesizing from durable registry mutation eliminate composite false merges ($\text{FDAR}_{\text{merge}} \equiv 0.0\%$) while achieving $\ge 80.0\%$ paired resolution recovery when explicit corroborating evidence subsequently arrives?

---

## 2. Experimental Design & Independent Variables

### Fresh Sealed 60-World Evaluation Set (All R8-8C Worlds Burned)
To maintain strict epistemic independence, all 60 evaluation worlds from R8-8C are permanently burned. R8-8C-R1 evaluates a fresh, independently generated sealed benchmark of 60 worlds ($N = 120$ sequential document invocations):

1. **Arm 1: Unseen Novel Hardware Systems (15 Worlds = 30 Decisions)**
   - Fresh novel entity names (e.g., `Vector Core Alpha`, `Hydra Node 4`, `Prism Switch 9`).
   - Evaluates provisional entity instantiation without parent namespace collisions.
2. **Arm 2: Morphological & Syntactic Known Aliases (15 Worlds = 30 Decisions)**
   - Known canonical entities with complex syntax variants, hyphenations, and descriptive expansions.
   - Evaluates immediate high-precision durable linking on registered aliases.
3. **Arm 3: Near-Collisions, Partitions & Sibling Enclosures (15 Worlds = 30 Decisions)**
   - Sibling clusters, sub-blade enclosures, and numbered partition slices.
   - Evaluates deterministic partition syntax blocking and provisional partition tracking.
4. **Arm 4: Epistemic Deferral & Multi-Source Evidence Accumulation (15 Worlds = 30 Decisions)**
   - **Sub-Arm 4A: Permanent Ambiguity (8 Worlds = 16 Decisions)**: Ungrounded generic nouns requiring permanent deferral.
   - **Sub-Arm 4B: Deferred-Then-Resolved (7 Worlds = 14 Decisions)**: Initial ungrounded composite mentions emitting non-durable hypotheses in Doc 1, followed by explicit identifying corroboration in Doc 2.

---

## 3. Two-Tier Ingress Architecture & Epistemic Invariants

### 1. The Non-Durable Hypothesis Layer
When an ungrounded composite surface form is encountered:
- An ephemeral hypothesis record is stored in the session ledger:
  ```json
  {
    "hypothesis_id": "hyp_w54_cluster1_backup",
    "candidate_target": "compute_cluster_1",
    "surface_form": "Cluster 1 Backup",
    "status": "UNRESOLVED",
    "evidence_sources": ["Doc1_Initial_Report"],
    "corroboration_required": true
  }
  ```
- The durable canonical registry is untouched (`durable_mutation: NONE`).

### 2. The Evidence Accumulation & Consolidation Gate
When a subsequent document provides explicit parent grounding (e.g. `"Cluster 1 Backup (CC-1 Standby Instance)"`):
- The hypothesis is matched against the explicit corroborating evidence.
- The state transitions from `UNRESOLVED` to `RESOLVED`, executing a durable `LINK` mutation.

---

## 4. Confirmatory Estimands & Acceptance Gates

| Gate / Estimand | Metric / Definition | Verification Method | Preregistered Floor |
| :--- | :--- | :--- | :--- |
| **Gate 1: Diagnostic Neural Proposal Quality** | Raw neural proposal accuracy across all 4 arms | Secondary diagnostic telemetry | Reported by arm (diagnostic floor $\ge 60.0\%$) |
| **Gate 2: Hybrid Durable False Merge Floor** | False merges into incorrect canonical entities ($\text{FDAR}_{\text{merge}}$) | Independent verifier replay | $\equiv \mathbf{0.0\%}$ ($0 / 120$ false merges) |
| **Gate 3: Provisional Entity Fragmentation** | Duplicate provisional entities for the same novel entity | Reconstructed from SQLite mutation log | $\equiv \mathbf{0 / 30}$ duplicate provisional entities |
| **Gate 4: Ambiguous Deferral Accuracy** | Non-durable deferral rate on ungrounded bare tokens (Sub-Arm 4A) | Exact binomial against gold manifest | $\ge \mathbf{85.0\%}$ ($13 / 15$ bare tokens deferred) |
| **Gate 5: Paired Deferral-to-Evidence Resolution** | Paired recovery: Doc 1 deferred $\land$ Doc 2 correctly resolved (Sub-Arm 4B) | Paired sequence verification | $\ge \mathbf{80.0\%}$ ($6 / 7$ paired sequences) |
| **Gate 6: Useful Resolvable Coverage** | Useful admissions across all non-bare mentions ($N = 97$) | Exact binomial denominator | $\ge \mathbf{85.0\%}$ ($83 / 97$ useful admissions) |
| **Gate 7: Database & Gold-Manifest Integrity** | SQLite integrity check + full reconciliation against gold world manifest | Automated schema & graph assertion | $\equiv \mathbf{100.0\%}$ (zero cycles, zero orphan records) |

---

## 5. Epistemic Scope Ceilings
- **Claim Ceiling**: Claims safe, zero-false-merge streaming entity induction and multi-source evidence accumulation via non-durable identity hypotheses in a hybrid neural-deterministic architecture.
- **Exclusions**:
  - Does NOT claim general unconstrained open-domain coreference across unstructured natural text.
  - Does NOT claim fully autonomous schema induction or dynamic predicate ontology generation.
