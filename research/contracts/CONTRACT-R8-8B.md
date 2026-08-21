---
contract_id: CONTRACT-R8-8B
status: FROZEN
title: "Exploration Round 8 Stage 8B: Multi-Document Entity Resolution and Cross-Temporal Ingress Fusion"
phase: 8B
parent_contract: CONTRACT-R8-8A
base_sha: c7c9ef641393adf6687f9ce05eda0b8776e2e32d
proposed_by: antigravity
design_review: APPROVED
reviewed_by: chatgpt-pro
authorized_by: human
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
created_at: "2026-08-21 22:40:00Z"
---

# Research Contract: CONTRACT-R8-8B (Frozen)

## 1. Epistemic Frontier & Scientific Context
- **Baseline (Stage 8A Promoted)**: In `CONTRACT-R8-8A`, `gemma3:12b` achieved $100\%$ candidate recall and zero false admissions on single-document synthetic telemetry narratives without candidate menus.
- **Core Question (Stage 8B)**: Can autonomous open ingress successfully perform cross-document entity coreference resolution and bitemporal state fusion across asynchronous multi-document streams without inflating false discovery ($\text{FDAR} \equiv 0.0\%$)?

## 2. Experimental Model: $2 \times 2$ Factorial Design (50 Worlds / 100 Mentions)

To isolate identity resolution from temporal fusion mechanisms, Stage 8B evaluates exactly 50 sealed multi-document evaluation worlds ($N_{\text{gold}} = 100$ total entity mentions, 2 per world) across a $2 \times 2$ factorial matrix:

| Factorial Cell | World Allocation | Mention Denominator | Identity Difficulty | Temporal Structure | Primary Isolation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cell 1** | 10 Worlds | 20 Mentions | Literal Canonical Names | Monotonic In-Order | Baseline Ingress Control |
| **Cell 2** | 15 Worlds | 30 Mentions | Aliases / Codes / Partials | Monotonic In-Order | **Entity Resolution Isolated** |
| **Cell 3** | 10 Worlds | 20 Mentions | Literal Canonical Names | Asynchronous / Superseding | **Temporal Fusion Isolated** |
| **Cell 4** | 15 Worlds | 30 Mentions | Aliases / Codes / Partials | Asynchronous / Superseding | **Combined Challenge** |
| **Total** | **50 Worlds** | **100 Mentions** | — | — | Full Benchmark Suite |

### Hard Negatives & Near-Collision Controls
The entity registry and candidate generation environment include adversarial near-collisions where two distinct entities share higher surface string similarity (e.g. `Cluster Unit 12-A` vs `Cluster Unit 12-B`) than an entity shares with its genuine alias (`Cluster Unit 12-A` $\leftrightarrow$ `Relay Primus 12`). Exactly 30 adversarial distractor trials are distributed across Cells 2 and 4.

## 3. Pre-registered Success Gates & Explicit Denominators

| Gate / Estimand | Target Matrix / Scope | Exact Denominator | Pre-registered Floor | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1 (Coreference Recall $M_{1\text{coref}}$)** | Cells 2 & 4 | $N = 60$ alias mentions | $\ge 85.0\%$ ($51 / 60$) | Multi-document alias discovery |
| **Gate 2 (Candidate Precision $M_2$)** | Global | Total proposed candidates | $\ge 85.0\%$ | Rejection of hallucinated entity bindings |
| **Gate 3 (False Merge Rate)** | Adversarial Near-Collisions | $N = 30$ distractor trials | $\equiv 0.0\%$ ($0 / 30$) | Prevents identity corruption |
| **Gate 4 (False Split Rate)** | Coreference Sets (Cells 2 & 4) | $N = 60$ coreference mentions | $\le 5.0\%$ ($\le 3 / 60$) | Prevents entity fragmentation |
| **Gate 5 (Temporal Correctness Under Out-of-Order)** | Cells 3 & 4 | $N = 50$ temporal facts (25 worlds) | $\ge 90.0\%$ ($45 / 50$) | Correct bitemporal supersession |
| **Gate 6 (Useful Admission Coverage $M_3$)** | Global (All 4 Cells) | $N = 100$ total gold mentions | $\ge 80.0\%$ ($80 / 100$) | End-to-end safe ingress |
| **Gate 7 (Global False Discovery $\text{FDAR}_{\text{global}}$)** | Global Durable Store | Total durable admissions | $\equiv 0.0\%$ ($0 / N$) | Bitemporal safety invariant |
| **Gate 8 (Downstream Probes Q1..Q4)** | Global Admitted Facts | Total admitted facts $\times 4$ | $\equiv 100.0\%$ passed | Point-in-time, interval, and certificate integrity |

## 4. Acceptance Verifier & Raw Evidence Recomputation
- The deterministic contract acceptance verifier `scripts/verify_contract_r8_8b.py` MUST parse `data/r8_stage8b_raw_calls.jsonl` and recompute all mention-level coreference links, confusion matrices, and bitemporal queries directly from raw model outputs, rather than trusting summary JSON fields.

## 5. Epistemic Boundaries & Scope Ceilings
- **Authorized Scope**: Cross-document alias and coreference resolution against a pre-registered canonical entity registry, followed by safe bitemporal ingress and supersession.
- **Explicit Exclusions**: Does NOT claim unconstrained open-world entity induction or autonomous ontology expansion (unresolvable novel mentions must trigger safe `DEFER`/`UNRESOLVED`). Predicate definitions remain fixed.
