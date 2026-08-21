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
resource:
  resource_class: GPU
  long_running: false
  exclusive_gpu: true
  interruptible: true
created_at: "2026-08-21 22:17:00Z"
---

# Research Contract Proposal: CONTRACT-R8-8B (Draft)

## 1. Epistemic Frontier & Research Question
- **Context**: In Stage 8A, we demonstrated that `gemma3:12b` achieves $100\%$ candidate recall and zero false admissions on single-document telemetry narratives without candidate menus.
- **Core Question (Stage 8B)**: Can autonomous open extraction successfully perform cross-document entity coreference resolution (mapping aliases and partial mentions to canonical entities) and bitemporal state fusion across asynchronous multi-document streams without inflating false discovery ($\text{FDAR} > 0.0$)?

## 2. Hypothesis & Architectural Model
- **Hypothesis**: Proof-carrying binding hypothesis sets with explicit alias resolution enable zero-shot extraction across multi-document streams while preserving strict $\text{FDAR} \equiv 0.0\%$ and bitemporal validity.
- **Null Hypothesis ($H_0$)**: Cross-document entity ambiguity causes unconstrained candidate extraction to produce mismatched entity bindings, resulting in $\text{FDAR} > 5.0\%$ or probe failures under temporal conflict.

## 3. Pre-registered Success Criteria & Falsification Floors
- **Gate 1 (Cross-Document Coreference Recall $M_1$)**: $\ge 85.0\%$ across 50 multi-document worlds.
- **Gate 2 (Ingress Candidate Precision $M_2$)**: $\ge 85.0\%$.
- **Gate 3 (Useful Bitemporal Admission Coverage $M_3$)**: $\ge 80.0\%$.
- **Gate 4 (Global False Discovery $\text{FDAR}_{\text{global}}$)**: $\equiv 0.0\%$ ($0$ false durable admissions).
- **Gate 5 (Downstream Bitemporal Probes Q1..Q4)**: $100\%$ passed.

## 4. Epistemic Boundaries & Non-Claims
- This contract does NOT claim open-world schema discovery (predicate definitions remain fixed in ontology).
- Acceptance verifiers must recompute all primary estimands directly from raw JSONL archives.
