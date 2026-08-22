---
contract_id: CONTRACT-R8-8C-R3
status: DRAFT
base_sha: 1f3b0207345563ce903d00777455e1f8ed0f46f0
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
proposed_by: antigravity
design_review: CHANGES_REQUESTED
reviewed_by: chatgpt-pro
authorized_by: null
---

# Research Contract: CONTRACT-R8-8C-R3 (Two-Stage Epistemic Ingress with Refined Precedence)

## 1. Executive Summary & Moonshot Objective

This contract establishes the confirmatory benchmark protocol for **Stage 8C-R3**, validating two-stage hybrid entity resolution and ontology ingress under the architectural decoupling of **Existence $\neq$ Identity**. It incorporates the single precedence policy clarification exposed by burned development evidence in Stage 8C-R2 (World 55), while preserving deterministic existence authority.

### The Architectural Foundation: Existence $\neq$ Identity Decoupling
- **Existence Authority (Deterministic)**: Explicit asserted commissioning notices deterministically create provisional entity records without requiring neural agreement. Neural LLM proposals serve strictly as advisory telemetry.
- **Identity Resolution (Precedence-Gated)**: Ingress mentions are resolved against the durable entity graph following a strictly ordered, frozen precedence hierarchy.

---

## 2. Refined Precedence Policy & Frozen Grammar

$$\text{Mention } s \longrightarrow \begin{cases} 
\text{Rule 1: Exact Registered Alias} & \text{if } N(s) \in \text{Aliases}(E) \\
\text{Rule 2: Structural First Refusal} & \text{if } \text{Parent}(s) \in \text{Entities} \land \text{SubID}(s) \neq \emptyset \\
\text{Rule 3: Parenthetical Identity Evidence} & \text{if } \text{Parenthetical}(s \lor \text{Ctx}) \in \text{Aliases}(E) \\
\text{Rule 4: Novel Standalone Commissioning} & \text{if } \text{Asserted}(s) \land \text{New}(s) \\
\text{Rule 5: Fail-Closed Deferral} & \text{otherwise}
\end{cases}$$

### Literal Frozen Structural Grammar
- **Recognized Partition Markers**: `["partition", "blade", "slice", "tray", "socket", "pool", "rack", "enclosure", "lun", "bay"]`
- **Discriminating Sub-Identifier Definition**: An integer or a single letter `A`–`D` matching `(?:\b|\s)(?:[0-9]+|[a-d])\b`.
- **Precedence Rule Interaction**:
  - Structural first refusal (Rule 2) activates **only** when a mention contains both a grounded parent entity and a recognized discriminating sub-identifier (e.g. `Partition 1`, `Blade 2`, `Slice B`).
  - Structural-looking mentions lacking a discriminating sub-identifier (e.g. `"Edge Gateway Alpha Reserve Bay (Router-Beta)"`) bypass Rule 2 and are evaluated under Rule 3. If explicit registered parenthetical identity evidence (e.g. `(Router-Beta)`) is present, they resolve to that entity; otherwise they fail closed to `DEFER` without durable registry mutation.

---

## 3. Statistical Acceptance Gates ($N=120$ Decisions, $N=97$ Resolvable)

| Gate ID | Metric & Statistical Boundary | Target Threshold |
| :--- | :--- | :--- |
| **Gate 1** | Neural Proposal Logging Telemetry | Logged across all $N=120$ decisions |
| **Gate 2a** | False Canonical Merge Floor | $\equiv 0.0\%$ ($0/120$ false merges) |
| **Gate 2b** | False Provisional Existence Floor on Unasserted | $\equiv 0.0\%$ ($0/16$ unasserted mentions) |
| **Gate 3** | Provisional Entity Fragmentation | $\equiv 0$ duplicate provisional creations |
| **Gate 4** | Permanent Deferral Invariant (Arm 4A World-Level) | $\ge 7/8$ ($87.5\%$) fully deferred worlds |
| **Gate 5** | Evidence Accumulation Lifecycle Matrix (Arm 4B) | $\equiv 7/7$ exact world lifecycle transitions ($100.0\%$) |
| **Gate 6** | Useful Resolvable Coverage ($N=97$ Resolvable) | $\ge 85.0\%$ across $N=97$ resolvable decisions |
| **Gate 7** | Relational DB & Hypothesis Ledger Reconciliation | SQLite integrity ok, 0 FK errors, full edge/hypo ledger |

---

## 4. Paired Offline Comparative Replay Benchmark

The verification pipeline executes a mandatory paired offline comparative replay:
- Replays persisted Stage 8C-R3 neural proposals against the frozen **Stage 8C-R2 deterministic resolver** (`EpistemicIngressSessionR2`) initialized with the identical Stage 8C-R3 base registry.
- Quantifies the exact marginal coverage increase ($\Delta$) attributable solely to the refined structural/parenthetical precedence rule on identical documents and telemetry.

---

## 5. Claim Ceiling & Explicit Exclusions

### Authorized Claim Ceiling
> In a controlled synthetic streaming hardware benchmark ($N=60$ worlds, $120$ decisions), refining structural-first-refusal so that explicit registered parenthetical identity evidence can resolve structural-looking mentions without discriminating sub-identifiers preserves zero false canonical and provisional commitments while maintaining $\ge 85.0\%$ useful admission coverage on resolvable events.

### Explicit Epistemic Exclusions
This contract does **NOT** authorize claims of:
1. Open-world unstructured natural language entity resolution.
2. Free-form existence inference from ambiguous or unasserted prose.
3. Autonomous unsupervised ontology induction.
4. Out-of-vocabulary cross-domain transfer beyond the benchmark ontology.

---

## 6. Execution Environment & Cryptographic Assets

- **Model**: Gemma 3 12B Instruct (Q4_K_M) via local Ollama endpoint (`http://127.0.0.1:11434/api/generate`).
- **Worlds Generator**: `src/gene/benchmarks/r8_stage8c_r3/worlds.py` with PRNG seed `3141592653` ($N=60$ fresh worlds, $N=120$ decisions, $N=97$ resolvable).
- **Sealing Manifest**: [`research/contracts/SEALING_MANIFEST-R8-8C-R3.json`](SEALING_MANIFEST-R8-8C-R3.json).
