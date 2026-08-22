---
contract_id: CONTRACT-R8-8C-R1
status: DRAFT
proposed_by: antigravity
design_review: null
reviewed_by: chatgpt-pro
authorized_by: null
base_sha: e7d921dfce8d5101f6f8758570a86ecbeac52e66
execution_base_sha: null
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
---

# Research Contract Proposal: CONTRACT-R8-8C-R1 (Non-Durable Identity Hypotheses, Evidence Accumulation & Disconfirmation)

## Title
Stage 8C-R1: Non-Durable Identity Hypotheses, Multi-Source Evidence Accumulation, and Delayed Commitment Under Streaming Feeds

## 1. Context & Research Question
In Stage 8C (`PROMOTION-CONTRACT-R8-8C`), GENE established that while epistemic deferral on bare generic nouns succeeds ($86.7\%$ Gate 4) and provisional entity fragmentation remains at zero ($0/30$ Gate 3), the system exhibited a critical failure mode: **canonicalization pressure on composite surface forms**.

When presented with unseen composite mentions containing known entity names (e.g. `"Cluster One Enclave"`, `"SAN Alpha Unit"`), the neural model exhibited strong lexical attraction to the known stem and proposed immediate canonical links, which bypassed the initial deterministic guardrails and produced 2 durable false merges ($1.67\%$).

Stage 8C-R1 tests the core architectural remedy: **Propose Early, Commit Late via Non-Durable Identity Hypotheses & Disconfirmation**.

```
EPISTEMIC INGRESS PIPELINE (Stage 8C-R1):
Incoming Stream Mention x_t (Source S_1)
        │
        ├── 1. Exact Registered Alias? (Normalized Whole-Mention Match) ──► Immediate Durable LINK
        │
        ├── 2. Preregistered Partition Syntax? ───────────────────────────► Link to Provisional Partition / Block Merge
        │
        ├── 3. Bare Generic Token? ───────────────────────────────────────► Epistemic DEFER (durable_mutation: NONE)
        │
        └── 4. Unseen Composite with Known Stem? 
                    │
                    ▼
          [NON-DURABLE IDENTITY HYPOTHESIS]
          candidate_target = canonical_id
          status           = UNRESOLVED_HYPOTHESIS
          evidence_count   = 1
          durable_mutation = NONE
          (hash(CanonicalRegistry) strictly invariant; hypothesis ledger isolated)
                    │
                    │ Subsequent Corroborating Stream Evidence Arrives (Source S_2)
                    ▼
          [EVIDENCE ACCUMULATION & DISCONFIRMATION GATE]
          Explicit Identifying Context in S_2:
          ├── CONFIRMS Candidate A ──────────► Promote Hypothesis to Durable LINK (Target: A)
          ├── CONTRADICTS / Points to B ─────► Retarget & Link to B; Discard Hypothesis A (0 residue on A)
          └── ESTABLISHES Novel Entity ──────► Create Provisional Entity; Discard Hypothesis A (0 residue on A)
```

### Core Research Question
Does decoupling non-durable identity hypothesizing from durable registry mutation eliminate composite false merges ($\text{FDAR}_{\text{merge}} \equiv 0.0\%$) while achieving $\ge 80.0\%$ paired resolution recovery and $100\%$ clean disconfirmation when contradictory or novel clarifying evidence arrives?

---

## 2. Ingress Architecture & Epistemic Invariants

### 1. Mechanical Exact-Alias Normalization Rule
- Let normalizer $N(s)$ map a string to lowercase, strip leading/trailing whitespace, and collapse punctuation/hyphens (e.g. `"cc-1"` $\to$ `"cc1"`, `"cc 1"` $\to$ `"cc1"`).
- Immediate durable `LINK` is authorized **only if**:
  $$N(\text{mention}) \equiv N(\text{canonical\_name}) \quad \lor \quad N(\text{mention}) \in \{N(a) \mid a \in \text{registered\_aliases}\}$$
- A known alias appearing merely as a substring of an unseen composite (e.g. `"Cluster One"` inside `"Cluster One Enclave"`) **must NEVER satisfy Rule 1**.

### 2. Observable Hypothesis Isolation
For every Arm 4 clarifying sequence:
- The SHA-256 digest of the canonical registry state $\text{hash}(\text{CanonicalRegistry})$ is recorded immediately before and after Doc 1.
- Doc 1 creates **only an `UNRESOLVED_HYPOTHESIS`** in the session ledger:
  ```json
  {
    "hypothesis_id": "hyp_w54_cluster1_backup",
    "candidate_target": "compute_cluster_1",
    "surface_form": "Cluster 1 Backup",
    "status": "UNRESOLVED",
    "evidence_sources": ["source_doc1_feed"],
    "corroboration_required": true
  }
  ```
- Entity rows, durable aliases, provenance edges, and $\text{hash}(\text{CanonicalRegistry})$ must remain strictly unchanged (`durable_mutation: NONE`).
- Unresolved surface forms must never enter the canonical alias table or be presented to the neural model as established identity.

### 3. Multi-Source Evidence Promotion & Disconfirmation Semantics
- Ingest documents carry distinct source identifiers (`source_id: "ingest_stream_A"` for Doc 1 vs `source_id: "audit_stream_B"` for Doc 2).
- The 7 clarifying worlds (Sub-Arm 4B) are explicitly split into:
  - **4 Confirmations**: Doc 1 hypothesizes Canonical A; Doc 2 explicitly confirms Canonical A $\implies$ hypothesis promoted to durable `LINK` to Canonical A.
  - **3 Contradictions / Retargetings**: Doc 1 hypothesizes Canonical A; Doc 2 explicitly establishes Canonical B or a novel entity $\implies$ original candidate hypothesis is rejected/retargeted with **zero durable contamination of Canonical A**.

---

## 3. Fresh Sealed 60-World Evaluation Benchmark

All 60 evaluation worlds from R8-8C are treated as permanently burned. R8-8C-R1 evaluates a fresh, independently generated sealed benchmark of 60 worlds ($N = 120$ sequential document invocations) disjoint from all burned 8C worlds and Scouts A/B/C:

1. **Arm 1: Unseen Novel Hardware Systems (15 Worlds = 30 Decisions)**
   - Fresh novel entity names (e.g., `Vector Core Alpha`, `Hydra Node 4`, `Prism Switch 9`).
   - Evaluates provisional entity instantiation without parent namespace collisions.
2. **Arm 2: Morphological & Syntactic Known Aliases (15 Worlds = 30 Decisions)**
   - Known canonical entities with complex syntax variants, hyphenations, and descriptive expansions present in the registered alias table.
   - Evaluates immediate high-precision durable linking on registered aliases under normalizer $N(s)$.
3. **Arm 3: Near-Collisions, Partitions & Sibling Enclosures (15 Worlds = 30 Decisions)**
   - Sibling clusters, sub-blade enclosures, and numbered partition slices.
   - Evaluates deterministic partition syntax blocking and provisional partition tracking.
4. **Arm 4: Epistemic Deferral & Multi-Source Evidence Accumulation (15 Worlds = 30 Decisions)**
   - **Sub-Arm 4A: Permanent Ambiguity (8 Worlds = 16 Decisions)**: Ungrounded generic nouns requiring permanent deferral.
   - **Sub-Arm 4B: Deferred-Then-Resolved (7 Worlds = 14 Decisions)**:
     - 4 Confirmation Worlds (Doc 1: hypothesis $\to$ Doc 2: confirmed $\to$ `LINK`)
     - 3 Contradiction Worlds (Doc 1: hypothesis $\to$ Doc 2: contradicted $\to$ clean retarget/reject with 0 residue).

---

## 4. Confirmatory Estimands & Acceptance Gates

| Gate / Estimand | Metric / Definition | Verification Method | Preregistered Floor |
| :--- | :--- | :--- | :--- |
| **Gate 1: Diagnostic Neural Proposal Quality** | Raw neural proposal accuracy reported across all 4 arms | Secondary diagnostic telemetry | Report-only telemetry (non-blocking; diagnostic baseline $\ge 60\%$) |
| **Gate 2: Hybrid Durable False Merge Floor** | False merges into incorrect canonical entities ($\text{FDAR}_{\text{merge}}$) | Independent verifier replay | $\equiv \mathbf{0.0\%}$ ($0 / 120$ false merges) |
| **Gate 3: Provisional Entity Fragmentation** | Duplicate provisional entities for the same novel entity | Reconstructed from raw SQLite mutation log | $\equiv \mathbf{0 / 30}$ duplicate provisional entities |
| **Gate 4: Permanent Ambiguity Invariant** | Non-durable deferral rate on ungrounded bare tokens (Sub-Arm 4A) | World-level evaluation across both docs | $\ge \mathbf{7 / 8}$ worlds ($87.5\%$) remain non-durable |
| **Gate 5: Evidence Accumulation & Disconfirmation** | Paired recovery in Sub-Arm 4B: Doc 1 non-durable hypothesis $\land$ Doc 2 correct resolution | Paired sequence verification | $\ge \mathbf{6 / 7}$ correct final resolutions, $0$ premature Doc 1 mutations, $\mathbf{3/3}$ clean disconfirmations |
| **Gate 6: Useful Resolvable Coverage** | Useful admissions across all non-bare mentions ($N = 97$) | Exact binomial denominator | $\ge \mathbf{85.0\%}$ ($83 / 97$ useful admissions) |
| **Gate 7: Database & Gold-Manifest Integrity** | SQLite PRAGMA checks + full reconciliation of registry and hypothesis ledger against gold | Automated schema & graph assertion | $\equiv \mathbf{100.0\%}$ (zero cycles, zero orphan records, discarded hypotheses verified discarded) |

---

## 5. Epistemic Scope Ceilings
- **Claim Ceiling**: Claims safe, zero-false-merge streaming entity induction, non-durable hypothesis tracking, and multi-source evidence accumulation with disconfirmation in a hybrid neural-deterministic architecture.
- **Exclusions**:
  - Does NOT claim general unconstrained open-domain coreference across unstructured natural text.
  - Does NOT claim fully autonomous schema induction or dynamic predicate ontology generation.
