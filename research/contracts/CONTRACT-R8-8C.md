---
contract_id: CONTRACT-R8-8C
status: DRAFT
proposed_by: antigravity
design_review: null
reviewed_by: chatgpt-pro
authorized_by: null
base_sha: add7574737a88f43570d645a1a8e0dcae4b099d8
execution_base_sha: null
resource_class: llm_inference
long_running: false
exclusive_gpu: false
interruptible: true
---

# Research Contract Proposal: CONTRACT-R8-8C (Sequential Registry Evolution & Epistemic Deferral)

## Title
Stage 8C: Open-World Entity Induction, Two-Stage Registry Mutation, and Epistemic Deferral Under Streaming Multi-Document Feeds

## 1. Context & Research Question
In Stage 8B-R1 (`CHECKPOINT-R8-8B`), GENE established zero-defect multi-document coreference and strict non-retroactive bitemporal supersession across a static closed-world entity registry ($60/60$ alias coreference, $100/100$ bitemporal queries, $\text{FDAR} \equiv 0.0\%$).

However, open-world deployment introduces three critical epistemic failure modes identified in empirical Scouts A, B, and C:
1. **Unseen Novel Entities**: New entities entering the stream must be provisionally instantiated without corrupting the canonical namespace.
2. **Hard-Negative Near-Collisions & Partitions**: Entities sharing lexical prefixes or parent names (e.g., `Compute Cluster 1 Partition 1-B` vs `Compute Cluster 1`, or `Cluster 10` vs `Cluster 1`) must NOT be falsely merged into known units. Scout-C demonstrated that raw LLM proposals suffer a $25.0\%$ false merge rate on partition boundaries, requiring deterministic ingress guardrails.
3. **Ambiguous Bare Tokens**: Under-specified mentions (e.g., `The Array`, `The Node`, `The System`) lack sufficient identification entropy and must be epistemically deferred rather than guessed, with the ability to resolve once subsequent documents provide clarifying context.

```
HYBRID STREAMING MULTI-DOCUMENT INGESTION ARCHITECTURE:
Doc Mention -> Neural Identity Proposal (gemma3:12b)
                     │
                     ▼
        Deterministic Ingress Guardrail
  (Exact Alias Priority -> Partition Grammar -> Bare Token Filter)
                     │
                     ▼
  Registry Mutation (LINK | CREATE_PROVISIONAL + MUST_NOT_LINK | DEFER)
                     │
                     ▼
  Stream Progression -> Contextual Deferral Resolution -> Verified Ingress
```

### Core Research Question
Can a **hybrid neural + deterministic epistemic ingress system** extend a hardware entity registry under open-world uncertainty across a 2-document stream, resolving deferred entities upon arrival of clarifying evidence while maintaining an absolute false discovery merge rate of $\text{FDAR}_{\text{merge}} \equiv 0.0\%$?

---

## 2. Experimental Design: Four-Arm Stratified Sequential Registry Benchmark

The benchmark comprises **60 synthetic worlds**, each evaluated across a sequential 2-document stream ($60 \times 2 = 120$ document decisions).

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           120 TOTAL DOCUMENT DECISIONS                                  │
├──────────────────────────┬──────────────────────────┬───────────────────────────────────┤
│ Arm 1: Novel Discovery   │ 15 worlds x 2 docs = 30  │ Doc 1: CREATE_PROV -> Doc 2: LINK │
├──────────────────────────┼──────────────────────────┼───────────────────────────────────┤
│ Arm 2: Unmapped Aliases  │ 15 worlds x 2 docs = 30  │ Doc 1: LINK_CANON  -> Doc 2: LINK │
├──────────────────────────┼──────────────────────────┼───────────────────────────────────┤
│ Arm 3: Near-Collisions   │ 15 worlds x 2 docs = 30  │ Doc 1: CREATE_PROV + MUST_NOT_LINK│
├──────────────────────────┼──────────────────────────┼───────────────────────────────────┤
│ Arm 4: Epistemic Defer   │ 15 worlds x 2 docs = 30  │ 4A: DEFER -> DEFER (8 worlds, 16) │
│                          │                          │ 4B: DEFER -> RESOLVE (7 w, 14)    │
└──────────────────────────┴──────────────────────────┴───────────────────────────────────┘
```

### Arm 1: Novel Entity Discovery & Provisional Evolution ($N = 30$ decisions)
- **Doc 1**: Unambiguous mention of an unmapped hardware entity (e.g. `Aurora Node 7`).
  - *Expected Action*: `identity: NOVEL`, `mutation: CREATE_PROVISIONAL` ($P_7$).
- **Doc 2**: Secondary alias variant of the newly created provisional entity (e.g. `A-Node Seven`).
  - *Expected Action*: `identity: EXISTING`, `mutation: LINK` ($P_7$).

### Arm 2: Unmapped Alias & Temporal Evolution ($N = 30$ decisions)
- **Doc 1**: Unseen syntactic alias variant of an existing canonical entity (e.g. `Compute Cluster Unit One` for `compute_cluster_1`).
  - *Expected Action*: `identity: EXISTING`, `mutation: LINK` (`compute_cluster_1`).
- **Doc 2**: Second distinct alias variant of the same canonical entity (e.g. `Cluster Unit 1-Main`).
  - *Expected Action*: `identity: EXISTING`, `mutation: LINK` (`compute_cluster_1`).

### Arm 3: Near-Collision & Partition Disambiguation ($N = 30$ decisions)
- **Doc 1**: Hard-negative partition or adjacent numbered unit (e.g. `Compute Cluster 1 Partition 1-B` vs `Compute Cluster 1`, or `Compute Cluster 10` vs `Cluster 1`).
  - *Expected Action*: `identity: NOVEL`, `mutation: CREATE_PROVISIONAL` ($P_{1B}$), `must_not_link: ["compute_cluster_1"]`.
- **Doc 2**: Variant alias of the provisional partition entity (e.g. `CC1-B Standby`).
  - *Expected Action*: `identity: EXISTING`, `mutation: LINK` ($P_{1B}$).

### Arm 4: Epistemic Deferral & Delayed Resolution ($N = 30$ decisions)
- **Sub-arm 4A (Permanent Ambiguity, 8 worlds = 16 decisions)**:
  - **Doc 1**: Bare generic token (e.g. `The Array`, `The Node`, `The System`).
    - *Expected Action*: `identity: AMBIGUOUS`, `mutation: DEFER`.
  - **Doc 2**: Continued under-specified generic mention.
    - *Expected Action*: `identity: AMBIGUOUS`, `mutation: DEFER`.
- **Sub-arm 4B (Deferred-Then-Resolved, 7 worlds = 14 decisions)**:
  - **Doc 1**: Ambiguous under-specified mention (e.g. `Cluster 1 Backup`).
    - *Expected Action*: `identity: AMBIGUOUS`, `mutation: DEFER`.
  - **Doc 2**: Clarifying evidence arriving in second document (e.g. `Cluster 1 Backup (CC-1 Standby Partition)` confirming canonical identity).
    - *Expected Action*: `identity: EXISTING`, `mutation: LINK` (`compute_cluster_1`).

---

## 3. Two-Stage Epistemic Schema & Deterministic Ingress Policy

All entity resolution calls return a structured payload adhering to the schema:

```json
{
  "identity_judgment": "EXISTING" | "NOVEL" | "AMBIGUOUS",
  "registry_mutation": "LINK" | "CREATE_PROVISIONAL" | "DEFER",
  "target_id": "string_or_null",
  "must_not_link": ["list_of_forbidden_ids"],
  "confidence": 0.0,
  "rationale": "structured reasoning string"
}
```

### Preregistered Deterministic Ingress Grammar & Policy Precedence
The deterministic ingress policy executes the following order of precedence to guarantee zero false merges:

1. **Rule 0 (Exact Known Alias Precedence)**:
   - If mention string matches an existing entry in `registry[target].aliases` or `canonical_name` (e.g. `CC-4` for `Compute Cluster 4`), validate as legitimate alias and preserve `LINK`.
2. **Rule 1 (Preregistered Partition Syntax Grammar)**:
   - Matches regex: `(?i)\b(partition|part|sub|slice|module|aux|secondary|core\s+\d+|blade)\b|[-_](?:part|slice|mod|sub|blade|sec|aux|\d+-[A-Z]|[A-Z]-\d+|[A-Z])$`
   - If matched and proposal attempts to link to a parent unit, deterministic policy overrides to:
     - `identity_judgment = "NOVEL"`
     - `registry_mutation = "CREATE_PROVISIONAL"`
     - `target_id = null`
     - `must_not_link = [parent_entity_id]`
3. **Rule 2 (Sibling Number Collision Invariant)**:
   - If mention digits differ from target canonical digits (e.g. `Node 10` vs `Node 1`, `Cluster 40` vs `Cluster 4`), block merge and override to `CREATE_PROVISIONAL` + `MUST_NOT_LINK`.
4. **Rule 3 (Bare Generic Token Filter)**:
   - If mention belongs to the closed set of ungrounded bare tokens (`{"the system", "the node", "the cluster", "the array", "host unit", "primary unit", "backup node", "standby cluster", "hardware appliance", "target device"}`), enforce `DEFER`.

---

## 4. Preregistered Acceptance Gates & Frozen Denominators

| Gate / Metric | Floor / Requirement | Verification Method | Pass Threshold |
| :--- | :--- | :--- | :--- |
| **Gate 1: Neural Proposal Decision Quality** | Pre-policy raw neural accuracy across all 120 decisions and per-arm floor | Recomputed from raw JSONL proposal records | Overall $\ge 90.0\%$ ($108 / 120$), Per-Arm floor $\ge 80.0\%$ ($24 / 30$) |
| **Gate 2: Durable False Merge Invariant** | Absolute zero false merges into incorrect canonical or provisional entities | $\text{FDAR}_{\text{merge}} = \frac{\text{False Merges}}{\text{Total Ingresses}}$ | $\equiv 0.0\%$ ($0 / 120$) |
| **Gate 3: Provisional Fragmentation Floor** | Duplicate provisional creations for the same real entity across 2-doc stream | Arms 1 & 3 provisional deduplication ($N=30$) | $\le 5.0\%$ ($\le 1 / 30$) |
| **Gate 4: Ambiguous Deferral Accuracy** | Correct `DEFER` rate under under-specified mentions in Doc 1 | Arm 4 Doc 1 decisions ($N=15$) | $\ge 85.0\%$ ($13 / 15$) |
| **Gate 5: Delayed Resolution Recovery** | Correct resolution rate after initial deferral upon arrival of Doc 2 | Sub-arm 4B Doc 2 decisions ($N=7$) | $\ge 80.0\%$ ($6 / 7$) |
| **Gate 6: Resolvable Useful Coverage** | Successful linking of all resolvable mentions across stream | Pre-registered $N=97$ resolvable decisions (Arm 1 Doc 2 [15] + Arm 2 Docs 1 & 2 [30] + Arm 3 Doc 2 [15] + Sub-arm 4B Doc 2 [7] + Arm 1 & 3 Doc 1 creations [30]) | $\ge 85.0\%$ ($83 / 97$) |
| **Gate 7: Post-Stream Registry & Partition Manifest Integrity** | Final registry verification against immutable gold entity-partition manifest (referential integrity, zero orphaned links, zero cycle mutations) | Graph & SQLite manifest validator | $\equiv 100.0\%$ |

---

## 5. Execution Environment & Compute Budget
- **Model**: `gemma3:12b` via Ollama local inference (`http://localhost:11434/api/generate`).
- **Total Invocations**: $120$ structured LLM calls ($60 \text{ worlds} \times 2 \text{ docs}$).
- **Estimated Runtime**: $\approx 60\text{--}90$ seconds.
- **Durable Artifacts Generated**:
  - `data/r8_stage8c_candidate_evidence.jsonl` (raw 120-call traces containing raw neural proposals, guardrail actions, and final decisions).
  - `data/r8_stage8c_summary.json` (canonical metric aggregations).
  - `data/r8_stage8c_registry.sqlite` (final post-stream relational database).
  - `data/r8_stage8c_evidence_manifest.json` (content-addressed SHA-256 hashes).

---

## 6. Epistemic Scope Ceilings
- **Claim Ceiling**: A hybrid neural + deterministic epistemic ingress system can extend a hardware entity registry under open-world uncertainty while preventing unsafe durable merges across streaming multi-document feeds.
- **Exclusions**:
  - Does NOT claim general open-domain ontology hierarchy induction (e.g. arbitrary multi-level inheritance trees).
  - Does NOT claim multi-party distributed consensus.
