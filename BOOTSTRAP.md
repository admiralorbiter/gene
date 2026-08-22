# BOOTSTRAP.md — GENE Project Manual & Epistemic Specification

**Project**: `gene` (General Epistemic Network Engine)  
**Moonshot**: Autonomous, provably fail-closed epistemic knowledge discovery & entity resolution for research repositories.  
**Repository**: `https://github.com/admiralorbiter/gene`  
**Governance Contract**: [`AGENTS.md`](https://github.com/admiralorbiter/mother-base/blob/main/AGENTS.md) — *Projects own truth. Mother Base owns operations.*

---

## 1. The Core Scientific Moonshot
GENE autonomously ingests unstructured scientific and system literature, constructs dynamic knowledge graphs, resolves ambiguous and multi-token entity mentions, and maintains relational integrity across document streams with **provable zero-false-merge fail-closed guarantees**.

---

## 2. Conceptual Vocabulary & Epistemic Formalism

### A. The Epistemic Ingress Pipeline
1. **Document Ingress $(D_t)$**: Streams of semi-structured hardware/system documents describing entities, aliases, deployments, and structural relationships.
2. **Neural Proposal Layer (Gemma 3 12B)**: Emits diagnostic semantic proposals (`LINK <target>`, `CREATE_PROVISIONAL`, or `DEFER`).
3. **Deterministic Epistemic Guardrail Layer**: Arbitrates durable mutations, enforcing fail-closed invariants before SQLite DB mutation.
4. **Relational Registry ($\mathcal{K}$)**: SQLite entity database maintaining canonical entities, provisional entities, and provenance edges.
5. **Non-Durable Hypothesis Ledger ($\mathcal{H}$)**: Epistemic tracking layer that records uncertain, ambiguous, or multi-token composite mentions across documents without prematurely mutating canonical state.

---

## 3. The Core Invariant: Existence Authority $\ne$ Identity Authority

- **Question 1: Does strong evidence establish that a distinct device exists?**
  Explicit deployment, commissioning, provisioning, or standalone hardware assertions in the text provide sufficient evidence of physical existence to authorize **reversible provisional entity creation** (`CREATE_PROVISIONAL`), without requiring neural model agreement.
- **Question 2: Does strong evidence establish canonical identity?**
  Strict whole-field exact matching or explicit parenthetical identifying corroboration is required to authorize a durable canonical `LINK`.

---

## 4. Lineage Progression: Stage 8A $\to$ 8B $\to$ 8C-R1 $\to$ 8C-R2

- **Stage 8A / 8B (Initial Ingress & Alias Resolution — PROMOTED)**: Established $100\%$ precision on exact registered aliases and baseline ingress fail-closed guardrails.
- **Stage 8C-R1 (Non-Durable Hypothesis Ledger — COMPLETED / REVISED_CONTRACT_REQUIRED)**:
  - Executed 120-decision confirmatory benchmark across 60 fresh synthetic worlds with Gemma 3 12B.
  - Rescored with world-local identity binding:
    - **Canonical False Merge Floor**: **$0 / 120$ ($0.0\%$, Gate 2a PASS)**.
    - **Provisional Fragmentation**: **$0$ duplicates (Gate 3 PASS)**.
    - **Structural Partitions (Arm 3)**: **$28 / 30$ ($93.3\%$)** vs Neural $0/30$.
    - **Exact Aliases (Arm 2)**: **$30 / 30$ ($100.0\%$)**.
    - **Useful Resolvable Coverage**: **$76 / 97$ ($78.4\%$)**.
  - Identified the Existence vs Identity conflation bottleneck in Arm 1 ($12/30$) and ambiguous structural markers (World 53).
- **Stage 8C-R2 (Two-Stage Epistemic Ingress — DRAFT / DESIGN APPROVED)**:
  - Hardened with explicit Existence Authority vs Identity Authority decoupling.
  - Precedence hierarchy: Registered Alias $\to$ Structural Partition $\to$ Parenthetical Corroboration $\to$ Standalone Existence $\to$ Unresolved Hypothesis.
  - Discriminating sub-identifier regex requiring at least one digit (`(?i)\b(?:[a-z]*\d[a-z0-9_-]*|\d+[a-z0-9_-]*)\b`).
  - Semantic False Provisional Existence Floor Gate 2b ($\text{FDAR}_{\text{prov}} \equiv 0.0\%$).
  - First-class nullable hypothesis candidates ($\text{UNRESOLVED}(\text{candidate}=\text{null})$).

---

## 5. Falsified Practices / DO NOT REOPEN
1. **Conflating Existence with Identity**: Forcing standalone deployment notices to require neural `NOVEL` keyword agreement suppresses resolvable coverage.
2. **Permissive Structural Partitions without Sub-Identifiers**: Treating `"sub-unit"` alone as a partition creator causes benchmark/contract conflicts on ungrounded composites (World 53).
3. **Forced Candidate Targets in Hypotheses**: Requiring non-null candidate targets forces guessing on unevidenced composites.
4. **Primary-Key Spelling Matching in Verifiers**: Evaluating primary-key string equality (`prov_vectorcorealpha` vs `prov_vector_core_alpha`) rather than world-local semantic identity binding introduces false verifier failures.

---

## 6. Canonical Evidence & Repositories
- **Durable Checkpoints**: `research/checkpoints/`
- **Research Contracts**: `research/contracts/`
- **Promotion Records**: `research/promotions/`
- **Raw Evidence Packages**: `data/`
- **Core Implementation**: `src/gene/`
