---
contract_id: CONTRACT-R8-8C-R1
status: SUPERSEDED
proposed_by: antigravity
design_review: APPROVED
reviewed_by: chatgpt-pro
authorized_by: human
base_sha: 52ebfe1fa4a2ee6fca55a3f12461ff36fdfd5c8a
execution_base_sha: 69949528d22736125026df16e91cb39f50e8b2ea
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
---

# Research Contract: CONTRACT-R8-8C-R1 (Non-Durable Identity Hypotheses, Multi-Source Evidence Accumulation & Disconfirmation)

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
        ├── 1. Exact Registered Alias? (Whole-Field Match under N(s)) ──► Immediate Durable LINK (Assert 1-to-1)
        │
        ├── 2. Preregistered Partition Syntax? ────────────────────────► Link to Provisional Partition / Block Merge
        │
        ├── 3. Bare Generic Token? ─────────────────────────────────────► Epistemic DEFER (durable_mutation: NONE)
        │
        └── 4. Unseen Composite with Known Stem? 
                    │
                    ▼
          [NON-DURABLE IDENTITY HYPOTHESIS]
          candidate_target = canonical_id
          status           = UNRESOLVED_HYPOTHESIS
          evidence_count   = 1
          durable_mutation = NONE
          (hash(DurableState) strictly invariant; hypothesis ledger isolated)
                    │
                    │ Subsequent Stream Document Arrives (Source S_2)
                    ▼
          [EVIDENCE ACCUMULATION & DISCONFIRMATION GATE]
          Explicit Whole-Field Identifying Construction in S_2:
          ├── REPEATED COMPOSITE (NO EVIDENCE) ──► Retain UNRESOLVED (durable_mutation: NONE)
          ├── CONFIRMS Candidate A ──────────────► Promote Hypothesis to Durable LINK (Target: A)
          ├── CONTRADICTS / Points to B ─────────► Retarget & Link to B; Discard Hypothesis A (0 residue on A)
          └── EXPLICIT NOVELTY ASSERTION ────────► Create Provisional Entity; Discard Hypothesis A (0 residue on A)
```

### Core Research Question
Does decoupling non-durable identity hypothesizing from durable registry mutation eliminate composite false merges ($\text{FDAR}_{\text{merge}} \equiv 0.0\%$) while achieving $\ge 80.0\%$ paired resolution recovery and $100\%$ clean disconfirmation when contradictory, repeated unevidenced, or novel clarifying evidence arrives?

---

## 2. Ingress Architecture & Epistemic Invariants

### 1. Literal Mechanical Exact-Alias Normalizer $N(s)$ & Collision Invariant
- The normalizer function $N(s)$ is strictly frozen across all pipeline and verifier components:
  $$N(s) = \text{re.sub}(r"[\backslash s\backslash -\_,.:;/ \backslash\backslash |()\[\]\{\}`'\" \sim *!?@\#\$\%\^\&\+\=]+", "", s.\text{strip}().\text{lower}())$$
- **Collision Invariant Assertion**: The normalized alias table maps $N(\text{alias}) \to \text{entity\_id}$. The pipeline asserts that $N(\text{alias})$ maps to strictly exactly one entity. If ambiguous, it fails closed to `AMBIGUOUS_DEFER` and never links.
- Immediate durable `LINK` is authorized **only if**:
  $$N(\text{mention}) \equiv N(\text{canonical\_name}) \quad \lor \quad N(\text{mention}) \in \{N(a) \mid a \in \text{registered\_aliases}\}$$
- A known alias appearing merely as a substring of an unseen composite (e.g. `"Cluster One"` inside `"Cluster One Enclave"`) **must NEVER satisfy Rule 1**.

### 2. Observable Hypothesis Isolation & Complete Durable State Hashing
- For every evaluation sequence, the cryptographic SHA-256 digest of the entire durable epistemic state $\text{hash}(\text{DurableState})$ is recorded immediately before and after Doc 1:
  $$\text{DurableState} = \{\text{canonical\_entities}, \text{provisional\_entities}, \text{durable\_aliases}, \text{provenance\_edges}, \text{durable\_links}\}$$
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
- Entity rows, provisional rows, durable aliases, provenance edges, and $\text{hash}(\text{DurableState})$ must remain strictly unchanged (`durable_mutation: NONE`).
- Unresolved surface forms must never enter the canonical alias table or be presented to the neural model as established identity.

### 3. Whole-Field Evidence Promotion, Disconfirmation & Symmetric Novelty Controls
- Ingest documents carry distinct source identifiers (`source_id: "ingest_stream_A"` for Doc 1 vs `source_id: "audit_stream_B"` for Doc 2).
- Corroboration requires extracting the explicit parenthetical identifying string and performing a **whole-field match under $N(s)$**. Substring matching is strictly prohibited.
- **Symmetric Novelty Requirement (Unknown $\ne$ Novel)**:
  - An unmatched parenthetical identifier does NOT automatically authorize `CREATE_PROVISIONAL`.
  - Creation requires: whole-field identifier unmatched $+$ explicit document novelty assertion (e.g. `"newly installed"`, `"new unit"`, `"standalone"`) $+$ neural judgment `NOVEL`.
  - Otherwise, it fails closed to `UNRESOLVED_DEFER`.
- The 15 Arm-4 worlds are structured as:
  - **Sub-Arm 4A: Permanent Non-Resolution (8 Worlds = 16 Decisions)**:
    - 4 Bare Generic Noun Worlds (permanent generic deferral across both docs).
    - 4 Repeated Unresolved Composite Worlds (Doc 1: unseen composite hypothesis $\to$ Doc 2: repeated composite without identifying context $\to$ remains `UNRESOLVED`, zero durable mutation across both docs).
  - **Sub-Arm 4B: Evidence Accumulation & Disconfirmation (7 Worlds = 14 Decisions)**:
    - 4 Confirmation Worlds (Doc 1: hypothesis $\to$ Doc 2: confirmed $\to$ durable `LINK`).
    - 2 Contradiction-to-Existing Worlds (Doc 1: hypothesis Canonical A $\to$ Doc 2: points to Canonical B $\to$ durable `LINK` to B, clean discard of A with 0 residue).
    - 1 Contradiction-to-Novel World (Doc 1: hypothesis Canonical A $\to$ Doc 2: points to Novel Entity C $\to$ `CREATE_PROVISIONAL` C, clean discard of A with 0 residue).

---

## 3. Fresh Sealed 60-World Evaluation Benchmark

All 60 evaluation worlds from R8-8C are treated as permanently burned. R8-8C-R1 evaluates a fresh, independently generated sealed benchmark of 60 worlds ($N = 120$ sequential document invocations) disjoint from all burned 8C worlds, Scouts A/B/C, and the R1 mini-scout:

1. **Arm 1: Unseen Novel Hardware Systems (15 Worlds = 30 Decisions)**: Fresh novel entities evaluated for provisional entity instantiation without namespace collision.
2. **Arm 2: Morphological & Syntactic Known Aliases (15 Worlds = 30 Decisions)**: Registered aliases evaluated for immediate whole-field linking under normalizer $N(s)$.
3. **Arm 3: Near-Collisions, Partitions & Sibling Enclosures (15 Worlds = 30 Decisions)**: Sibling clusters and numbered partitions evaluated for partition syntax blocking.
4. **Arm 4: Epistemic Deferral, Hypothesis Isolation & Disconfirmation (15 Worlds = 30 Decisions)**:
   - Sub-Arm 4A (8 Worlds): Permanent non-resolution (4 bare generic + 4 repeated unevidenced composites).
   - Sub-Arm 4B (7 Worlds): 4 confirmations + 2 contradictions-to-existing + 1 contradiction-to-novel.

---

## 4. Confirmatory Estimands & Acceptance Gates

| Gate / Estimand | Metric / Definition | Verification Method | Preregistered Floor |
| :--- | :--- | :--- | :--- |
| **Gate 1: Diagnostic Neural Proposal Quality** | Raw neural proposal accuracy reported across all 4 arms | Secondary diagnostic telemetry | Report-only telemetry (non-blocking; diagnostic baseline $\ge 60\%$) |
| **Gate 2: Hybrid Durable False Merge Floor** | False merges into incorrect canonical entities ($\text{FDAR}_{\text{merge}}$) | Independent verifier replay | $\equiv \mathbf{0.0\%}$ ($0 / 120$ false merges) |
| **Gate 3: Provisional Entity Fragmentation** | Duplicate provisional entities across all provisional creations (Arm 1, Arm 3, and Arm 4B novel contradictions) | Reconstructed from raw SQLite mutation log | $\equiv \mathbf{0}$ duplicate provisional entities |
| **Gate 4: Permanent Non-Resolution Invariant** | Non-durable rate across ungrounded bare tokens and repeated unevidenced composites (Sub-Arm 4A) | World-level evaluation across both docs | $\ge \mathbf{7 / 8}$ worlds ($87.5\%$) remain non-durable across both docs |
| **Gate 5: Evidence Accumulation & Disconfirmation** | Paired recovery in Sub-Arm 4B: Doc 1 non-durable hypothesis $\land$ Doc 2 correct resolution | Paired sequence verification | $\ge \mathbf{6 / 7}$ correct final resolutions, $0$ premature Doc 1 mutations, $\mathbf{3/3}$ clean disconfirmations ($0$ residue) |
| **Gate 6: Useful Resolvable Coverage** | Useful admissions across Gold-Resolvable Durable Decisions ($N = 97$) | Exact binomial denominator | $\ge \mathbf{85.0\%}$ ($83 / 97$ useful admissions) |
| **Gate 7: Database & Gold-Manifest Integrity** | SQLite PRAGMA checks + full reconciliation of registry and hypothesis ledger against gold | Automated schema & graph assertion | $\equiv \mathbf{100.0\%}$ (zero cycles, zero orphan records, discarded hypotheses verified discarded) |

---

## 5. Sealing Manifest

Before dispatching execution, the following components are cryptographically hashed and sealed:
- **Neural Model**: `gemma3:12b-instruct-q4_K_M`
- **Ingress Normalizer**: Mechanical whole-field function $N(s)$
- **Collision Invariant**: Pre-execution 1-to-1 assertion
- **Symmetric Novelty Rule**: Explicit novelty assertion gate
- **Benchmark Worlds**: 60 fresh worlds strictly disjoint from burned 8C, Scouts A/B/C, and R1 mini-scout.
- **Gold Manifest**: Immutable ground truth definitions for all 60 evaluation worlds.

---

## 6. Epistemic Scope Ceilings
- **Claim Ceiling**: Claims safe, zero-false-merge streaming entity induction, non-durable hypothesis tracking, and multi-source evidence accumulation with disconfirmation in a hybrid neural-deterministic architecture.
- **Exclusions**:
  - Does NOT claim general unconstrained open-domain coreference across unstructured natural text.
  - Does NOT claim fully autonomous schema induction or dynamic predicate ontology generation.
