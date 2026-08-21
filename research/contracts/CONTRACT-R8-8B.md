---
contract_id: CONTRACT-R8-8B
status: DRAFT
title: "Exploration Round 8 Stage 8B: Multi-Document Entity Resolution and Cross-Temporal Ingress Fusion"
phase: 8B
parent_contract: CONTRACT-R8-8A
base_sha: c7c9ef641393adf6687f9ce05eda0b8776e2e32d
proposed_by: antigravity
design_review: CHANGES_REQUESTED
reviewed_by: chatgpt-pro
authorized_by: null
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
created_at: "2026-08-21 22:30:00Z"
---

# Research Contract Proposal: CONTRACT-R8-8B (Draft Revision 1)

## 1. Epistemic Frontier & Scientific Context
- **Baseline (Stage 8A Promoted)**: In `CONTRACT-R8-8A`, `gemma3:12b` achieved $100\%$ candidate recall and zero false admissions on single-document synthetic telemetry narratives without candidate menus.
- **Core Question (Stage 8B)**: Can autonomous open ingress successfully perform cross-document entity coreference resolution and bitemporal state fusion across asynchronous multi-document streams without inflating false discovery ($\text{FDAR} \equiv 0.0\%$)?

## 2. Experimental Model: $2 \times 2$ Factorial Design

To isolate identity resolution from temporal fusion mechanisms, Stage 8B evaluates 50 synthetic multi-document worlds across a $2 \times 2$ factorial matrix:

| Factorial Cell | Identity Difficulty | Temporal / Arrival Structure | Primary Mechanistic Isolation |
| :--- | :--- | :--- | :--- |
| **Cell 1 (Literal $\times$ In-Order)** | Literal Canonical Names | Monotonic in-order valid time | Baseline Ingress Control |
| **Cell 2 (Alias $\times$ In-Order)** | Aliases, Codes, Partial Mentions | Monotonic in-order valid time | **Entity Resolution Isolated** |
| **Cell 3 (Literal $\times$ Out-of-Order)** | Literal Canonical Names | Asynchronous / superseding arrival | **Temporal Fusion Isolated** |
| **Cell 4 (Alias $\times$ Out-of-Order)** | Aliases, Codes, Partial Mentions | Asynchronous / superseding arrival | **Combined End-to-End Challenge** |

### Hard Negatives & Near-Collision Controls
The entity registry and candidate generation environment include adversarial near-collisions where two distinct entities share higher surface string similarity (e.g. `Cluster Unit 12-A` vs `Cluster Unit 12-B`) than an entity shares with its genuine alias (`Cluster Unit 12-A` $\leftrightarrow$ `Relay Primus 12`).

## 3. Pre-registered Success Gates & Estimands

| Gate / Estimand | Target Matrix / Scope | Pre-registered Floor | Rationale |
| :--- | :--- | :--- | :--- |
| **Gate 1 (Coreference Recall $M_{1\text{coref}}$)** | Cells 2 & 4 | $\ge 85.0\%$ ($85 / 100$) | Multi-document alias discovery |
| **Gate 2 (Candidate Precision $M_2$)** | Global | $\ge 85.0\%$ | Rejection of hallucinated entity bindings |
| **Gate 3 (False Merge Rate)** | Near-Collision Adversarial Set | $\equiv 0.0\%$ ($0$ merged distinct entities) | Prevents identity corruption |
| **Gate 4 (False Split Rate)** | Global Coreference Sets | $\le 5.0\%$ | Prevents entity fragmentation |
| **Gate 5 (Temporal Correctness Under Out-of-Order)** | Cells 3 & 4 | $\ge 90.0\%$ | Correct supersession / bitemporal resolution |
| **Gate 6 (Useful Admission Coverage $M_3$)** | Global | $\ge 80.0\%$ admitted & probe-verified | End-to-end safe ingress |
| **Gate 7 (Global False Discovery $\text{FDAR}_{\text{global}}$)** | Global | $\equiv 0.0\%$ ($0$ false durable admissions) | Bitemporal safety invariant |
| **Gate 8 (Downstream Probes Q1..Q4)** | Global Admitted Facts | $\equiv 100.0\%$ passed | Point-in-time, interval, and certificate integrity |

## 4. Acceptance Verifier & Raw Evidence Recomputation
- **Technical Debt Settlement**: The deterministic contract acceptance verifier `scripts/verify_contract_r8_8b.py` MUST parse `data/r8_stage8b_raw_calls.jsonl` and recompute all mention-level coreference links, confusion matrices, and bitemporal queries directly from raw model outputs, rather than trusting summary JSON fields.

## 5. Epistemic Boundaries & Scope Ceilings
- **Authorized Scope**: Cross-document alias and coreference resolution against a pre-registered canonical entity registry, followed by safe bitemporal ingress and supersession.
- **Explicit Exclusions**: Does NOT claim unconstrained open-world entity induction or autonomous ontology expansion (unresolvable novel mentions must trigger safe `DEFER`/`UNRESOLVED`). Predicate definitions remain fixed.
