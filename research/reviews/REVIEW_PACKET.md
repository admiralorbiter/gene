# Evidence Review Packet: GENE (gene)
**Active Contract**: `CONTRACT-R8-8C-R1`
**Repository HEAD**: `78d41710eaa4885b5052f185848de81229ecd5a0`

## 1. Project Context & Moonshot (from BOOTSTRAP.md)
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


---

## 2. Promoted & Completed Checkpoints
### CHECKPOINT-R8-8A.md
---
checkpoint_id: CHECKPOINT-R8-8A
contract_id: CONTRACT-R8-8A
status: PROMOTED
promoted_sha: c7c9ef641393adf6687f9ce05eda0b8776e2e32d
created_at: "2026-08-21 22:16:00Z"
---

# Research Checkpoint: Stage 8A Autonomous Open Ingress (Promoted)

## 1. Verified Scientific State
- **Hypothesis Confirmed**: Removing explicit candidate menus does not degrade relation candidate generation or downstream safe bitemporal admission for `gemma3:12b` on synthetic single-document telemetry.
- **Empirical Baseline**:
  - 115 live model invocations, 0 fallbacks
  - Recall ($M_1$): $100\%$ ($100/100$)
  - Precision ($M_2$): $100\%$
  - Useful Admission Coverage ($M_3$): $100\%$ ($100/100$)
  - Global False Discovery ($\text{FDAR}$): $0\%$
  - Downstream Probes Q1..Q4: $100\%$ passed
- **Next Frontier**: Stage 8B — Multi-Document Entity Resolution and Cross-Document Temporal Fusion under Ambiguity.



### CHECKPOINT-R8-8B.md
---
checkpoint_id: CHECKPOINT-R8-8B
contract_id: CONTRACT-R8-8B-R1
promotion_id: PROMOTION-CONTRACT-R8-8B-R1
timestamp: "2026-08-21 23:46:00Z"
base_sha: add7574737a88f43570d645a1a8e0dcae4b099d8
status: PROMOTED
authorized_by: human
---

# Checkpoint Record: CHECKPOINT-R8-8B (Multi-Document Stream Coreference & Occurrence Splitting)

## 1. Verified Scientific State
- **Contract Promoted**: `CONTRACT-R8-8B-R1`
- **Promotion Artifact**: [`research/promotions/PROMOTION-CONTRACT-R8-8B-R1.md`](../promotions/PROMOTION-CONTRACT-R8-8B-R1.md)
- **Verified Code Baseline**: `add7574737a88f43570d645a1a8e0dcae4b099d8`
- **Empirical Confirmation**:
  - In multi-document asynchronous telemetry streams, `gemma3:12b` successfully resolves coreferent entity mentions and hardware aliases against a pre-registered canonical entity registry ($60/60$ alias mentions resolved across Cells 2 and 4, $100\%$ precision on $200$ candidate mention slots).
  - Out-of-order contradictory telemetry is cleanly integrated via deterministic bitemporal occurrence splitting ($100/100$ 4-point bitemporal timeline queries satisfied with unique active state).
  - Zero false merges ($0/30$) across adversarial near-collision distractor controls; zero false splits ($0/60$); zero false durable admissions ($\text{FDAR} \equiv 0.0\%$).

## 2. Epistemic Architecture & Scope Ceilings
- **Established Architecture**: Neural model extracts uncertain raw entity spans and temporal intervals $\to$ hypothesis binding against canonical registry $\to$ proof-carrying admission policy $\to$ deterministic bitemporal supersession algebra $\to$ durable epistemic state.
- **Unresolved / Next Frontier**: Autonomous open-world ontology induction without pre-registered alias mappings, or higher-order multi-hop lineage reasoning under epistemic uncertainty.



## 3. Latest Promotion Records
### PROMOTION-CONTRACT-R8-8A.md
---
promotion_id: PROMOTION-CONTRACT-R8-8A
contract_id: CONTRACT-R8-8A
status: PROMOTED
candidate_sha: c7c9ef641393adf6687f9ce05eda0b8776e2e32d
promoted_at: "2026-08-21 22:16:00Z"
repair_rounds: 2
reviewed_by: chatgpt-pro
authorized_by: human
---

# Promotion Record: PROMOTION-CONTRACT-R8-8A (Promoted)

**Lifecycle Status**: `PROMOTED` (Authorized by Human Research Director & ChatGPT Pro Scientific Review Desk)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8A`
- **Phase / Milestone**: Exploration Round 8 Stage 8A (Autonomous Open Ingress)
- **Promoted Candidate Commit SHA**: `c7c9ef641393adf6687f9ce05eda0b8776e2e32d`
- **Contract Acceptance Verifier**: `PASS` (`scripts/verify_contract_r8_8a.py` executed and cleanly passed)
- **Scientific Review Verdict**: `APPROVED` (with one follow-up verifier hardening debt recorded)
- **Governance**: Human Director Promotion Merge.

## 2. Benchmark Verification & Estimands Audit

| Estimand / Metric | Pre-registered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Candidate Recall ($M_1$)** | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 ($100.0\%$)** | **PASS** |
| **High-Salience Recall** | $\ge 90.0\%$ | **50 / 50 ($100.0\%$)** | **PASS** |
| **Low-Salience Recall** | $\ge 85.0\%$ | **50 / 50 ($100.0\%$)** | **PASS** |
| **Candidate Precision ($M_2$)** | $\ge 85.0\%$ | **$100.0\%$** against gold relevant set | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $\ge 85.0\%$ | **100 / 100 ($100.0\%$)** admitted & probe-verified | **PASS** |
| **Global False Discovery ($\text{FDAR}_{\text{global}}$)** | $\equiv 0.0\%$ ($0 / N$) | **0 incorrect durable admissions ($0.0\%$)** | **PASS** |
| **Paired Relative Drop vs Menu Control** | $\le 10.0\%$ | **$0.0\%$ drop** across 50 paired worlds | **PASS** |
| **Downstream Probes Q1..Q4** | $\equiv 100.0\%$ | **100.0% passed** (Point-in-time, interval support, active facts, certificates) | **PASS** |

## 3. Epistemic Invariants & Methodological Debt
- **Belief Update**: In this controlled synthetic single-document domain, removing the explicit finite candidate menu did not reduce candidate extraction or downstream safe-admission performance for `gemma3:12b`.
- **Claim Ceiling**: Does not establish unrestricted open-world entity induction. Predicate schema is supplied, ontology exists downstream, and narratives are single-document synthetic telemetry.
- **Follow-up Hardening Debt**: Future Stage 8+ acceptance verifiers should recompute primary estimands directly from raw persisted evidence rather than trusting canonical-summary metric fields.



### PROMOTION-CONTRACT-R8-8B-R1.md
---
promotion_id: PROMOTION-CONTRACT-R8-8B-R1
contract_id: CONTRACT-R8-8B-R1
status: PROMOTED
candidate_sha: add7574737a88f43570d645a1a8e0dcae4b099d8
generated_at: "2026-08-21 23:46:00Z"
repair_rounds: 0
reviewed_by: chatgpt-pro
authorized_by: human
---

# Promotion Record: PROMOTION-CONTRACT-R8-8B-R1 (Multi-Document Stream Coreference & Occurrence Splitting)

**Lifecycle Status**: `PROMOTED` (Authorized by Human Research Director following Scientific Promotion Review)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8B-R1`
- **Phase / Milestone**: Exploration Round 8 Stage 8B-R1 Confirmatory Benchmark
- **Candidate Branch**: `mb/CONTRACT-R8-8B-R1`
- **Scientific Candidate Commit SHA**: `add7574737a88f43570d645a1a8e0dcae4b099d8`
- **Execution Base SHA**: `3da636d9ddd649160f24e8eb1074d8c7d260e2e8`
- **Contract Acceptance Verifier**: `PASS` (`scripts/verify_contract_r8_8b_r1.py` executed with zero runner booleans, fresh sealed world manifest assertion, multi-document stream invariants, verified model digest consistency, and independent occurrence-splitting bitemporal replay)
- **Evidence Package**: Committed and verified in tree:
  - `data/r8_stage8b_r1_raw_calls.jsonl` (145 raw model calls on `gemma3:12b`, SHA256: `16f7b679...`)
  - `runs/r8_stage8b_r1_candidate_generation.db` (SQLite archive, SHA256: `873446a4...`)
  - `data/r8_stage8b_r1_summary.json` (Canonical metrics summary, SHA256: `179cb160...`)
  - `data/r8_stage8b_r1_evidence_manifest.json` (Full content-addressed evidence manifest)
- **Scientific Review Desk Verdict**: `APPROVED`
- **Human Director Verdict**: `PROMOTED`
- **Repair Iterations**: 0 rounds (clean first-pass confirmatory execution on fresh manifest).

## 2. Confirmatory Estimands & Factorial Gate Outcomes

| Estimand / Metric | Exact Denominator | Pre-registered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Coreference Recall ($M_{1\text{coref}}$)** | $N = 60$ alias mentions (Cells 2 & 4) | $\ge 85.0\%$ ($51 / 60$) | **60 / 60 mentions ($100.0\%$)** | **PASS** |
| **Candidate Precision ($M_2$)** | Total proposed candidates | $\ge 85.0\%$ | **$100.0\%$** against canonical targets | **PASS** |
| **False Merge Rate** | $N = 30$ distractor trials | $\equiv 0.0\%$ ($0 / 30$) | **0 false merges ($0.0\%$)** | **PASS** |
| **False Split Rate** | $N = 60$ coreference mentions | $\le 5.0\%$ | **0 false splits ($0.0\%$)** | **PASS** |
| **Temporal Correctness (Out-of-Order)** | $N = 100$ 4-point queries (Cells 3 & 4) | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 queries ($100.0\%$)** | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $N = 200$ total gold mention slots | $\ge 80.0\%$ ($160 / 200$) | **200 / 200 slots ($100.0\%$)** | **PASS** |
| **Global False Discovery ($\text{FDAR}_{\text{global}}$)** | Total durable admissions | $\equiv 0.0\%$ ($0 / N$) | **0 false durable admissions ($0.0\%$)** | **PASS** |
| **Downstream Probes Q1..Q4** | $N = 4 \times N_{\text{admitted}}$ ($400$ queries) | $\equiv 100.0\%$ | **400 / 400 queries ($100.0\%$)** | **PASS** |

## 3. Epistemic Invariants & Scope Ceilings
- **Claim**: In a controlled synthetic domain, registry-assisted neural extraction feeds a proof-carrying deterministic bitemporal system that safely resolves repeated entity mentions across asynchronous documents and correctly maintains overlap-specific supersession under late-arriving contradictory information without false merges ($\text{FDAR} \equiv 0.0\%$).
- **Occurrence Splitting**: Conflicting overlapping telemetry $[5.0, 7.0]$ cleanly supersedes historical occurrence $[5.0, 10.0]$ from $t_v = 5.0$ while preserving un-superseded future tail $[7.0, 10.0]$ as a distinct active occurrence.
- **Exclusions**: Does NOT claim unconstrained open-world entity induction or autonomous ontology expansion (unresolvable novel mentions trigger safe `DEFER`/`UNRESOLVED`). Predicate definitions remain fixed.



### PROMOTION-CONTRACT-R8-8B.md
---
promotion_id: PROMOTION-CONTRACT-R8-8B
contract_id: CONTRACT-R8-8B
status: REVISED_CONTRACT_REQUIRED
candidate_sha: 98e556f99bf08207377f0e29c5de3e3cdc1bb400
generated_at: "2026-08-21 23:12:00Z"
repair_rounds: 2
reviewed_by: chatgpt-pro
authorized_by: human
---

# Promotion Record: PROMOTION-CONTRACT-R8-8B (Multi-Document Resolution & Ingress Fusion)

**Lifecycle Status**: `REVISED_CONTRACT_REQUIRED` (Scientific Review Desk & Human Director Disposition)

## 1. Executive Summary & Review Desk Disposition
- **Target Contract**: `CONTRACT-R8-8B`
- **Candidate Commit SHA**: `98e556f99bf08207377f0e29c5de3e3cdc1bb400`
- **Scientific Review Desk Verdict**: `REVISED_CONTRACT_REQUIRED`
- **Disposition**:
  - The 145 live model calls on `gemma3:12b` are preserved as valuable exploratory evidence demonstrating high extraction fidelity, zero false merges ($0/30$), and $100\%$ mention resolution ($60/60$ alias mentions).
  - However, the frozen contract `CONTRACT-R8-8B` contained an internal unit-of-analysis inconsistency (preregistered $N=100$ total gold mentions for $M_3$, while specifying 50 multi-document worlds with $N=60$ alias mentions across 30 worlds, requiring $N=200$ mention slots).
  - Furthermore, Gate 5 requires explicit point-in-time and superseding timeline queries in the conflicting overlap region ($(t_k=2, t_v=6.0)$) and execution of explicit bitemporal `SUPERSEDES` events rather than dual assertions.
  - Therefore, `CONTRACT-R8-8B` is superseded by `CONTRACT-R8-8B-R1.md`.

## 2. Exploratory Pilot Benchmark Evidence (145 Live Calls on `gemma3:12b`)

| Estimand / Metric | Exact Denominator | Pre-registered Floor | Observed Empirical Result | Pilot Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Coreference Recall ($M_{1\text{coref}}$)** | $N = 60$ alias mentions (Cells 2 & 4) | $\ge 85.0\%$ ($51 / 60$) | **60 / 60 ($100.0\%$)** | **VALIDATED** |
| **Candidate Precision ($M_2$)** | Total proposed candidates | $\ge 85.0\%$ | **$100.0\%$** against canonical targets | **VALIDATED** |
| **False Merge Rate** | $N = 30$ distractor trials | $\equiv 0.0\%$ ($0 / 30$) | **0 false merges ($0.0\%$)** | **VALIDATED** |
| **False Split Rate** | $N = 60$ coreference mentions | $\le 5.0\%$ | **0 false splits ($0.0\%$)** | **VALIDATED** |
| **Temporal Correctness (Out-of-Order)** | $N = 50$ temporal queries across $t_k=1,2$ (Cells 3 & 4) | $\ge 90.0\%$ ($45 / 50$) | **50 / 50 ($100.0\%$)** | **VALIDATED** |
| **Useful Admission Coverage ($M_3$)** | $N = 200$ total gold mention slots | $\ge 80.0\%$ ($160 / 200$) | **200 / 200 ($100.0\%$)** admitted & probe-verified | **VALIDATED** |
| **Global False Discovery ($\text{FDAR}_{\text{global}}$)** | Total durable admissions | $\equiv 0.0\%$ ($0 / N$) | **0 false durable admissions ($0.0\%$)** | **VALIDATED** |
| **Downstream Probes Q1..Q4** | Total probe queries | $\equiv 100.0\%$ | **100.0% passed (400/400 queries)** | **VALIDATED** |

## 3. Next Steps: CONTRACT-R8-8B-R1
A revised contract proposal `CONTRACT-R8-8B-R1.md` is drafted with corrected unit formalisms, explicit 4-point bitemporal timeline queries, and fresh sealed evaluation worlds for confirmatory execution.



### PROMOTION-CONTRACT-R8-8C-R1.md
---
promotion_id: PROMOTION-CONTRACT-R8-8C-R1
contract_id: CONTRACT-R8-8C-R1
status: REVISED_CONTRACT_REQUIRED
candidate_sha: f0219989b5c2aeb3eb8903c7379d460e5dfcfbc2
generated_at: "2026-08-22 03:00:00Z"
repair_rounds: 0
reviewed_by: chatgpt-pro
authorized_by: null
---

# Promotion & Scientific Audit Record: CONTRACT-R8-8C-R1 (Non-Durable Hypothesis Ledger & Fail-Closed Ingress)

**Lifecycle Status**: `REVISED_CONTRACT_REQUIRED` (Confirmatory Run Completed; 5/7 Acceptance Gates Passed, Non-Promotable on Coverage and Disconfirmation Edge-Cases)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8C-R1`
- **Candidate Branch**: `mb/CONTRACT-R8-8C-R1`
- **Scientific Candidate Commit SHA**: `f0219989b5c2aeb3eb8903c7379d460e5dfcfbc2`
- **Execution Base SHA**: `69949528d22736125026df16e91cb39f50e8b2ea`
- **Model Endpoint**: `gemma3:12b` via local Ollama API (`http://127.0.0.1:11434/api/generate`)
- **Evaluation Surface**: 60 Fresh Synthetic Worlds (120 Decisions total across 5 experimental sub-arms)
- **Execution Time**: 553.72s (120 neural inference calls + deterministic guardrail arbitration)
- **Persisted Evidence Package**:
  - `data/r8_stage8c_r1_candidate_evidence.jsonl` (120 decision records with input prompt, neural response, and hybrid resolution)
  - `data/r8_stage8c_r1_summary.json` (Structured benchmark metrics and arm-level statistics)
  - `data/r8_stage8c_r1_registry.sqlite` (Relational SQLite entity registry and provenance edge database)
  - `data/r8_stage8c_r1_evidence_manifest.json` (Content-addressed SHA-256 cryptographic manifest)

---

## 2. Frozen Statistical Gates & Verification Verdicts

| Gate / Estimand | Preregistered Condition / Floor | Observed Result | Statistical Test | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Manifest Integrity** | Cryptographic hash match across all artifacts | SHA-256 Verified | Content digest check | **PASS** |
| **Gate 1: Diagnostic Neural Proposal Quality** | Telemetry tracking only (no ceiling/floor) | **61 / 120 ($50.8\%$)** | Raw accuracy vs gold (world-local binding) | **TELEMETRY** |
| **Gate 2: Hybrid Durable False Merge Floor** | Zero false merges into existing canonical entities ($0.0\%$) | **0 / 120 canonical false merges ($0.0\%$)** | Exact canonical false merge floor | **PASS** |
| **Gate 3: Provisional Entity Fragmentation** | Zero duplicate provisional entities for same real-world entity | **0 duplicates across provisionals** | Duplicate name check | **PASS** |
| **Gate 4: Permanent Non-Resolution Invariant** | Non-durable deferral across both documents in Sub-Arm 4A | **7 / 8 worlds ($87.5\%$)** | Floor $\ge 7/8$ ($87.5\%$) | **PASS** |
| **Gate 5: Evidence Accumulation & Disconfirmation** | - Doc 2 Resolution $\ge 6/7$<br>- Zero premature Doc 1 mutations<br>- Clean Retargeting ($3/3$) | - Doc 2: $6/7$ ($85.7\%$)<br>- 0 premature mutations<br>- Retarget: $1/3$ ($33.3\%$) | Multi-criteria invariant | **FAIL** |
| **Gate 6: Useful Resolvable Coverage** | Hybrid accuracy on resolvable entities ($N=97$) | **76 / 97 ($78.4\%$)** | Floor $\ge 85.0\%$ ($N=97$) | **FAIL** |
| **Gate 7: SQLite DB Schema, FKs & Reconciliation** | `PRAGMA foreign_key_check`, `integrity_check`, and entity reconciliation | 0 FK violations, PRAGMA ok, full ledger audit | SQLite integrity & ledger check | **PASS** |

---

## 3. Arm-by-Arm Empirical Breakdown (Rescored with World-Local Provisional Identity Binding)

| Experimental Sub-Arm | Total Decisions | Neural Proposal Accuracy | Hybrid Resolution Accuracy | Primary Characteristic |
| :--- | :--- | :--- | :--- | :--- |
| **Arm 1: Novel Standalone Entities** | 30 decisions (15 worlds) | 8 / 30 ($26.7\%$) | 12 / 30 ($40.0\%$) | Gemma emitted `DEFER` on 9/15 worlds without parentheticals; hybrid policy failed closed |
| **Arm 2: Known Exact Aliases** | 30 decisions (15 worlds) | 30 / 30 ($100.0\%$) | 30 / 30 ($100.0\%$) | $100\%$ precision on canonical alias linking |
| **Arm 3: Partition / Sibling Nodes** | 30 decisions (15 worlds) | 0 / 30 ($0.0\%$) | **28 / 30 ($93.3\%$)** | Deterministic partition guardrail intercepted and resolved partitions cleanly |
| **Arm 4A: Permanent Deferral (Ambiguous)** | 16 decisions (8 worlds) | 12 / 16 ($75.0\%$) | 14 / 16 ($87.5\%$) | World 53 (`Tensor Pod Three Sub-Unit`) triggered partition creation instead of deferral |
| **Arm 4B: Deferred $\to$ Resolved (Evidence)** | 14 decisions (7 worlds) | 11 / 14 ($78.6\%$)| 13 / 14 ($92.9\%$) | Zero premature Doc 1 mutations; clean Doc 2 resolution on 6/7 worlds |

---

## 4. Scientific Audit & Benchmark Findings
1. **World 53 Contract/Gold Specification Conflict**:
   - The frozen deterministic policy defines `"sub-unit"` as a structural partition marker $\implies$ `CREATE_PROVISIONAL`.
   - Gold manifest in World 53 (`Tensor Pod Three Sub-Unit`) specified `DEFER`.
   - The runner executed the frozen deterministic partition rule as specified in the contract. While not a false canonical merge, this represents a benchmark/contract inconsistency that will be resolved in R2.
2. **Mechanistic Confirmation of the Hypothesis Layer**:
   - Zero premature durable mutations occurred across all 60 worlds.
   - Hypothesis accumulation allowed 6/7 Arm 4B worlds to resolve cleanly upon arriving Document 2 evidence.
   - Disconfirmation successfully retargeted the entity without leaving durable residue.
3. **Disposition**: Candidate remains `REVISED_CONTRACT_REQUIRED` (non-promotable under R1). Preparing R2 architecture around risk-tiered epistemic authority: explicit evidence for provisional existence without requiring neural `NOVEL`, grounded partition sub-identifiers, and optional candidate targets in unresolved hypotheses (`candidate_target = null`).



### PROMOTION-CONTRACT-R8-8C.md
---
promotion_id: PROMOTION-CONTRACT-R8-8C
contract_id: CONTRACT-R8-8C
status: REVISED_CONTRACT_REQUIRED
candidate_sha: 7b781ff9286d9b4b0e5ee05c0ec2826cfdb3c19e
generated_at: "2026-08-22 02:04:00Z"
repair_rounds: 0
reviewed_by: chatgpt-pro
authorized_by: human
---

# Promotion Record: PROMOTION-CONTRACT-R8-8C (Open-World Entity Induction & Epistemic Deferral)

**Lifecycle Status**: `REVISED_CONTRACT_REQUIRED` (Falsified Confirmatory Checkpoint Preserved; Revised Contract Required)

## 1. Execution & Audit Summary
- **Target Contract**: `CONTRACT-R8-8C`
- **Phase / Milestone**: Exploration Round 8 Stage 8C Confirmatory Benchmark
- **Candidate Branch**: `mb/CONTRACT-R8-8C`
- **Scientific Candidate Commit SHA**: `7b781ff9286d9b4b0e5ee05c0ec2826cfdb3c19e`
- **Execution Base SHA**: `352a16d80429f4bc07455d315efcf9509ee15bb8`
- **Contract Acceptance Verifier**: `FAIL` (`python -m gene.benchmarks.r8_stage8c.verifier` evaluated all 7 preregistered gates; Gates 3, 4, 7 passed; Gates 1, 2, 5 (paired), 6 failed)
- **Evidence Package**: Committed and verified in tree:
  - `data/r8_stage8c_candidate_evidence.jsonl` (120 sequential document decisions on `gemma3:12b`, SHA256: `655d491d...`)
  - `data/r8_stage8c_summary.json` (Canonical metrics summary, SHA256: `a937fc1e...`)
  - `data/r8_stage8c_evidence_manifest.json` (Full content-addressed evidence manifest)
  - `data/r8_stage8c_registry.sqlite` (Sequential registry SQLite database)
- **Scientific Review Desk Verdict**: `REVISED_CONTRACT_REQUIRED`
- **Human Director Verdict**: `REVISED_CONTRACT_REQUIRED` (Preserve `7b781ff` as durable negative result; burn 60 evaluation worlds; draft R1 with fresh worlds)

## 2. Confirmatory Estimands & 7-Gate Outcome Breakdown

| Gate / Estimand | Pre-registered Condition / Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Gate 1: Neural Proposal Quality** | Overall $\ge 90.0\%$ ($108 / 120$); Min Arm $\ge 80.0\%$ | **83 / 120 ($69.2\%$)**; Min Arm: **$36.7\%$** | **FAIL** |
| **Gate 2: Durable False Merge Floor ($\text{FDAR}_{\text{merge}}$)** | $\equiv 0.0\%$ ($0 / 120$) false merges | **2 / 120 ($1.67\%$)** false merges | **FAIL** |
| **Gate 3: Provisional Entity Fragmentation Floor** | $0 / 30$ duplicate provisional entities | **0 / 30 duplicates ($0.0\%$)** | **PASS** |
| **Gate 4: Ambiguous Deferral Accuracy** | $\ge 85.0\%$ ($13 / 15$) on ungrounded bare mentions | **13 / 15 ($86.7\%$)** deferred | **PASS** |
| **Gate 5: Delayed Resolution Recovery** | Paired $\text{DEFER} \to \text{RESOLVE} \ge 80.0\%$ ($6 / 7$) | **4 / 7 paired ($57.1\%$)** [Unconditioned Doc 2: $6/7$ ($85.7\%$)] | **FAIL** |
| **Gate 6: Useful Resolvable Coverage** | $\ge 85.0\%$ ($83 / 97$) across non-bare mentions | **72 / 97 ($74.2\%$)** useful coverage | **FAIL** |
| **Gate 7: Database & Graph Invariant** | Clean SQLite state, zero cyclic lineages | **SQLite & Graph Integrity True** | **PASS** |

## 3. Failure Analysis & Scientific Insights

### 1. The Canonicalization Pressure Hazard
The model exhibited strong lexical attraction to known entity names embedded within unseen composite descriptors:
- **Case W59-D1 (Arm 4B)**: `"Cluster One Enclave"` in Doc 1 $\to$ neural proposal `EXISTING LINK compute_cluster_1` (confidence 0.95) $\to$ durable false merge.
- **Case W60-D1 (Arm 4B)**: `"SAN Alpha Unit"` in Doc 1 $\to$ neural proposal `EXISTING LINK storage_array_alpha` (confidence 0.95) $\to$ durable false merge.

Because the frozen deterministic policy only filtered exact aliases, partition tokens, and digit clashes, it did not block unseen modifiers attached to known entity stems. This demonstrates that in an epistemic system:
> *A known alias embedded inside an unseen composite surface form is not sufficient evidence for identity continuity; absence of proof that the modifier changes identity cannot be treated as proof of identity continuity.*

### 2. Paired Deferral Recovery (Gate 5)
While unconditioned Doc 2 accuracy in Arm 4B was $6/7$ ($85.7\%$), true paired recovery ($\text{DEFER} \to \text{RESOLVE}$) was only $4/7$ ($57.1\%$) because W59 and W60 suffered false merges in Doc 1 rather than deferring, and W54 misfired on Doc 2.

### 3. Verifier Debt Identified for R1
- **Gate 3**: The acceptance verifier should independently reconstruct provisional clusters from the raw SQLite mutation log rather than relying on runner tracking.
- **Gate 7**: Verifier should execute gold-manifest reconciliation against the immutable world specification rather than SQLite PRAGMA checks alone.

## 4. Epistemic Governance Disposition
1. **Preserve Commit `7b781ff`**: Maintained in git history as an immutable confirmatory negative result.
2. **Burn World Set**: All 60 original evaluation worlds are burned to prevent evaluation-driven tuning.
3. **Advance to `CONTRACT-R8-8C-R1`**: Architected around **non-durable identity hypotheses**, multi-source evidence accumulation, and delayed commitment.




---

## 4. Reorientation Prompt (Independent Synthesis)
> **Instructions for Review Desk**:
> 1. Reconstruct: What do we actually know from the evidence above?
> 2. Reinterpret: What do recent results/falsifications imply mechanistically?
> 3. Reconnect: What direct, neighboring, or analogical literature solves this shape?
> 4. Rebranch: What plausible explanations remain?
> 5. Compress: What single experiment eliminates the most roadmap?