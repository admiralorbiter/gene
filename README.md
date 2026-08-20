# GENE: Genealogical Epistemic Network Experiments

**An Experimental Instrument for the Inheritance, Retrieval Dynamics, and Selective Governance of Persistent LLM Memory**

---

## Executive Overview

GENE is a scientific research instrument designed to study how information changes, reproduces, persists, evades governance, and dies inside persistent language-model memory ecologies. 

Rather than treating memory failures simply as transient hallucinations or black-box attack rates, GENE experimentally decomposes the informational transmission pipeline:
$$\text{Ancestry} \longrightarrow \text{Retrieval Exposure} \longrightarrow \text{Local Reasoning} \longrightarrow \text{Reproduction} \longrightarrow \text{Lineage Governance} \longrightarrow \text{Structural Admission}$$

```
                                      THE GENE TRANSMISSION PIPELINE
                                      
  [ Ancestral Root Node ] 
            │
            ▼
  ┌───────────────────┐    Layer 1: Memory Governance (Lineage Immunity)
  │ Retrieval Filter  │ ──► Prunes discredited ancestry branches (Modulates X_path)
  └───────────────────┘
            │ (Retrieved Context)
            ▼
  ┌───────────────────┐
  │ Neural Reasoner   │ ──► Executes multi-hop deduction (May generate pseudo-paths)
  └───────────────────┘
            │ (Candidate Output Claim)
            ▼
  ┌───────────────────┐    Layer 2: Structural Epistemic Proofreader
  │ Support Validator │ ──► Formally unifies cited premises against rules (Modulates W_proofread)
  └───────────────────┘
            │
            ▼ (Admitted if Valid)
  [ Persistent Occurrence Node ] ──► Eligible for future generation inheritance (R ≈ b · X_path · τ · W_proofread)
```

---

## The Six Core Discoveries of GENE

1. **Exposure Is Not Ancestry (Experiment 0)**:
   Informational ancestry cannot be treated as a single observable. GENE formally separates **exposure lineage** (what was in context), **reported-support lineage** (what the model claimed to cite), and **causal lineage** (what counterfactually changed the output). Model self-reports are never causal ground truth.

2. **Bad Reasoning Is Not Required for Falsehood Propagation (Experiment 1A)**:
   A corrupted ancestral premise can be transformed across multiple semantic forms (e.g. *false supervisor* $\to$ *protocol* $\to$ *transit route* $\to$ *terminal authorization*) while each intermediate step remains locally logically valid. Globally false information reproduces through locally correct reasoning without requiring repeated hallucinations.

3. **Retrieval Regulates Reproductive Contact (Experiment 1B-B)**:
   Memory existence does not imply reproductive opportunity. Full multi-premise support-path retrieval availability ($X_{\text{path}}$) governs branching reproduction. Retrieval surface area scales subcritical/supercritical branching thresholds.

4. **Lineage Enables Selective Delayed Quarantine (Experiment 1B-C1b)**:
   When an ancestor is discredited after it has already reproduced, lineage-blind forgetting is bound by $C_H = C_I$ (it cannot reduce corrupted availability without destroying healthy coverage at the same rate). Lineage-aware quarantine breaks this symmetry, delivering selective containment $S = C_H - C_I = \text{TPR} - \text{FPR}$. Genealogy preserves the target of a trust judgment across semantic transformation.

5. **Memory Containment Is Not Behavioral Containment (Experiment 1B-C2 / C2a)**:
   Removing the legitimate support path ($X_{\text{path}} = 0$) does not guarantee behavioral suppression ($P(\text{unsupported expression}) = 0$). Neural reasoners can manufacture unsupported pseudo-paths from surviving fragments. Memory Governance (Layer 1) requires an independent Inference Integrity layer (Layer 2).

6. **Structural Proofreading Prevents Phenotypic Errors from Becoming Heritable (Experiment 1B-C2b)**:
   A mechanical first-order support-certificate validator checks whether cited memories structurally unify with deductive rule antecedents. In 30 live calls on Gemma 3:12B, the validator reduced a phenotypic expression rate of $\mu_{\text{expression}} = 0.300$ ($0.375$ on broken paths) to a heritable mutation rate of $\mu_{\text{heritable}} = \mathbf{0.000}$ ($0 / 24$ false admissions), admitting 100% of valid derivations. Transient reasoning errors are prevented from entering the germline.

---

## Frozen Milestone Roadmap Status

| Phase | Milestone Name | Key Objective | Status | Execution Commit |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0–4** | Instrumentation & Invariants | Deterministic SQLite persistence, dual oracles, causal interventions | **FROZEN** | `3b59368` |
| **Phase 5–6** | Experiment 0 | Lineage Observability, Causal Parentage, & Ecological Contracts | **FROZEN** | `3b59368` |
| **Phase 7** | Experiment 1A | Multi-Generational Mutation Cascades ($G_0 \to G_2$) | **FROZEN** | `68c3447` |
| **Phase 8** | Experiment 1B-A / B1 | Allele Fidelity, Multi-Hop Retrieval Dynamics ($X_{\text{path}}$), & Causal Rescue | **FROZEN** | `f6d6cbe` |
| **Phase 9 / 9.5** | Preflight & Matched Expression | Shape Map, Persistence Hardening, & 16-Call Live Matched Assay | **FROZEN** | `b7182d3` |
| **Phase 10** | Experiment 1B-C0 / C1b | Analytic Calibration & 12-Ecology Delayed Adjudication Sandbox | **FROZEN** | `15abd87` |
| **Phase 10.5** | Experiment 1B-C2 / C2a / C2b | Live Behavioral Immunity, Replay Stability, & Support-Certificate Validator | **FROZEN** | [`1f62908`](scripts/run_exp1b_c2b_binding_assay.py) / [`acd6660`](docs/ARCHITECTURE.md) |

---

## Primary Documentation & Results Artifacts

- **Authoritative Metrics Manifest:** [`data/canonical_results_manifest.json`](data/canonical_results_manifest.json) (Machine-generated from frozen SQLite databases)
- **Claim & Evidence Ledger:** [`data/claim_ledger.json`](data/claim_ledger.json) (Exact empirical provenance of all scientific claims)
- **Canonical Scientific Narrative:** [`docs/GENE_STORY_MEMO.md`](docs/GENE_STORY_MEMO.md)
- **System Architecture & Formalisms:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Interactive Research Exhibit:** [`docs/atlas/index.html`](docs/atlas/index.html)
- **Phase Reports:**
  - [Exp 0 Assay Report](docs/results/EXPERIMENT_0_WALKTHROUGH.md)
  - [Exp 1A Report](docs/results/EXPERIMENT_1A_REPORT.md)
  - [Exp 1B-B1c Matched Expression Report](docs/results/EXP1B_B1C_MATCHED_EXPRESSION_REPORT.md)
  - [Exp 1B-C1b Shared Ecology Report](docs/results/EXP1B_C1B_SHARED_ECOLOGY_REPORT.md)
  - [Exp 1B-C2a Live Behavioral Report](docs/results/EXP1B_C2A_LIVE_ASSAY_REPORT.md)
  - [Exp 1B-C2b Binding & Proofreading Report](docs/results/EXP1B_C2B_BINDING_REPORT.md)

---

## Test Suite Execution

All experimental fixtures, oracle closures, statistical analyzers, and proofreaders run under pytest:

```bash
pytest
```
*Current test health: 97 passed in 22.23s (Zero warnings/errors).*
