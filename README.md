# GENE: Genealogical Epistemic Network Experiments

**A Support-First, Lineage-Informed Epistemic Runtime for Persistent AI and Entitlement Maintenance Under Change**

---

## Executive Overview

GENE is a scientific research instrument and epistemic runtime designed to study how information changes, reproduces, persists, evades governance, and dies inside persistent language-model memory ecologies.

Rather than treating persistence as a loose bag of retrieved text or treating memory failures as transient hallucinations, GENE decomposes the epistemic lifecycle into an explicit systems pipeline:
$$\text{Ancestry} \longrightarrow \text{Retrieval Exposure} \longrightarrow \text{Neural Reasoning} \longrightarrow \text{Support Minimization} \longrightarrow \text{Lineage Projection} \longrightarrow \text{Action Governance}$$

```
                                      THE GENE EPISTEMIC PIPELINE
                                      
  [ Ancestral Root Node ] 
            │
            ▼
  ┌───────────────────┐    Layer 1: Memory Governance (Lineage Immunity)
  │ Retrieval Filter  │ ──► Prunes discredited ancestry branches (Modulates X_path)
  └───────────────────┘     R_inherited ≈ b · X_path · τ_S · W_S  (Eliminates inherited transmission)
            │ (Retrieved Context)
            ▼
  ┌───────────────────┐
  │ Neural Reasoner   │ ──► Stochastic candidate proposal engine (Emits answer + reported R(c))
  └───────────────────┘
            │
            ▼
  ┌───────────────────┐    Layer 2: Support Minimization & Conformance Validation
  │ Epistemic Kernel  │ ──► Extracts minimal entitling support S(c) from explanatory bloat R(c)
  └───────────────────┘     Prevents 100% false retractions on damaged-but-entitled states
            │
            ▼
  ┌───────────────────┐    Layer 3: Lineage-Projected Action Governance
  │ Governance Engine │ ──► Projects S(c) into root hypergraph S_L(c) and resilience rho_L(c)
  └───────────────────┘     Enforces 7 formal governance axioms before high-stakes actuation
            │
            ▼ (Admitted & Maintained)
  [ Persistent Epistemic Node ] ──► Entitlement under change: WHAT_IF(c, a) & THEN_WHAT(a)
```

---

## The Core Scientific Discoveries of GENE

1. **Exposure Is Not Ancestry (Experiment 0)**:
   Informational ancestry decomposes into three non-equivalent relations: **exposure lineage** (context presence), **reported-support lineage** (model citations), and **causal lineage** (interventional necessity). Model self-reports are never causal ground truth.

2. **Bad Reasoning Is Not Required for Falsehood Propagation (Experiment 1A)**:
   A corrupted ancestral premise transforms across multiple semantic representations (*supervisor* $\to$ *protocol* $\to$ *transit route*) with 100% transmission fidelity ($\tau = 1.000$) while every intermediate step remains locally logically valid. Falsehood reproduces through sound local deduction.

3. **Retrieval Regulates Reproductive Opportunity (Experiment 1B-B)**:
   Memory existence does not imply reproductive opportunity. Full multi-premise support-path retrieval availability ($X_{\text{path}}$) governs branching reproduction. Retrieval surface area scales subcritical/supercritical branching thresholds.

4. **Lineage Enables Selective Delayed Quarantine (Experiment 1B-C1b)**:
   When an ancestor is discredited post-reproduction, lineage-blind forgetting is bound by $C_H = C_I$. Lineage-aware quarantine breaks this symmetry, delivering selective containment $S = C_H - C_I = \text{TPR} - \text{FPR}$. Genealogy preserves the target of a trust judgment across semantic drift.

5. **Memory Containment $\ne$ Behavioral Containment (Experiment 1B-C2a)**:
   Removing the legitimate support path ($X_{\text{path}} = 0$) does not guarantee behavioral suppression. Neural reasoners manufacture unsupported pseudo-paths from surviving fragments. Memory governance (Layer 1) requires structural proofreading (Layer 2).

6. **Structural Proofreading Prevents Germline Infection (Experiment 1B-C2b)**:
   A mechanical first-order support-certificate validator checks whether cited memories structurally unify with deductive rule antecedents. In live calls on Gemma 3:12B, the validator reduced phenotypic expression of broken paths ($\mu_U = 0.375$) to zero heritable mutations ($\mu_{U, \text{heritable}} = \mathbf{0.000}$).

7. **Four-Layer Epistemic Conformance Taxonomy & Explanatory Bloat (Round 4)**:
   Neural reported justification $R(c)$ is not a faithful representation of minimal entitling support $\mathcal{S}(c)$. Epistemic outputs decompose into four independent layers: **symbol realization $\ne$ contract coherence $\ne$ justification precision $\ne$ formal derivability**. In entitled ecologies, models exhibited non-exact bloated support in 7/8 cases (mean excess 1.625) and 20.8% cross-field contract violations.

8. **Loss of Alternative-Support Algebra Causes Revision Autoimmunity (Round 5 Stage 5A)**:
   Representing alternative support $\mathcal{S}(c) = \{S_1, \dots, S_k\}$ as a flat conjunctive dependency union causes **100% false retractions (104/104)** on damaged-but-still-entitled states. Explanatory bloat causes 50% false retractions on untouched states. Support-first algebra eliminates 100% of revision errors across 432 scenarios without live compute.

9. **Intervention-Sufficient Representation & Lineage-Projected Action Governance (Round 5 Stage 5B)**:
   The Hierarchy of Epistemic Incompleteness ($\text{binary} \to \kappa \to \rho \to |\text{Roots}| \to \rho_L \to \mathcal{S}_L(c)$) proves that all scalar and tuple signatures suffer lossy representation collisions under change. In shared origin ancestry ($A,D \leftarrow R_1, B,E \leftarrow R_2$), nominal multiplicity masquerades as independence. Action governance requires the **antichain-minimized lineage-projected support hypergraph $\mathcal{S}_L(c)$**, achieving 100% compliance across 7 formal governance axioms.

10. **Support-First Epistemic Runtime Rescues Neural Revision & Governs Action (Round 5 Stage 5C)**:
    In a 32-call live Gemma 3:12B assay, belief maintenance under change revealed two distinct failure channels: unassisted neural revision failed on 2/4 degraded worlds ($50\%$) due to support-boundary confusion, while naïve reported-dependency tracking ($R(c)$) triggered retraction on 3/4 degraded worlds ($75\%$) and introduced 2 marginal errors beyond the neural baseline (combined runtime $0/4$ retention). Compiling minimal first-order entitling support $\mathcal{S}_F(c)$ restored **100% entitlement retention ($4/4$)** and **100% clean abstention ($4/4$)**. Lineage-projected authority $\text{Auth}(\mathcal{S}_L)$ demonstrated **dual-layer containment**: maintaining belief entitlement while enforcing preregistered action thresholds when structural root lineage was degraded.

---

## Frozen Milestone Roadmap Status

| Phase | Milestone Name | Key Objective | Status | Execution Commit |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0–4** | Instrumentation & Invariants | Deterministic SQLite persistence, dual oracles, causal interventions | **FROZEN** | `3b59368` |
| **Phase 5–6** | Experiment 0 | Lineage Observability, Causal Parentage, & 2x2 Factorial Matrix | **FROZEN** | `79b94cd` / `3c102bf` |
| **Phase 7** | Experiment 1A | Multi-Generational Mutation Cascades ($G_0 \to G_2$) | **FROZEN** | `69d3570` |
| **Phase 8** | Experiment 1B-A / B1 | Allele Fidelity, Multi-Hop Retrieval Dynamics ($X_{\text{path}}$), & Causal Rescue | **FROZEN** | `9c9e7ca` |
| **Phase 9 / 9.5** | Preflight & Matched Expression | Shape Map, Persistence Hardening, & 16-Call Live Matched Assay | **FROZEN** | `b7182d3` |
| **Phase 10** | Experiment 1B-C0 / C1b | Analytic Calibration & 12-Ecology Delayed Adjudication Sandbox | **FROZEN** | `9f58315` |
| **Phase 10.5** | Experiment 1B-C2 / C2a / C2b | Live Behavioral Immunity, Replay Stability, & Support-Certificate Validator | **FROZEN** | `a1474d6` / `1f62908` |
| **Round 4** | Exploration Round 4 | Epistemic Context Compiler & Four-Layer Conformance Assay | **FROZEN** | `cf472ee` |
| **Round 5A** | Exploration Round 5 Stage 5A | Revision Precision Assay & Loss of Support Algebra (432 cases) | **FROZEN** | `aff1baa` |
| **Round 5B** | Exploration Round 5 Stage 5B | Action Governance & Lineage-Projected Epistemic Resilience (368 cases) | **FROZEN** | `round5-stage5b-freeze-v3` |
| **Round 5C** | Exploration Round 5 Stage 5C | Neural Revision Bridge (32-Call Live Model Revision Assay) | **FROZEN** | `round5-stage5c-runner-freeze` |

---

## Primary Documentation & Results Artifacts

- **Authoritative Metrics Manifest:** [`data/canonical_results_manifest.json`](data/canonical_results_manifest.json)
- **Claim & Evidence Ledger:** [`data/claim_ledger.json`](data/claim_ledger.json) (Exact empirical provenance of all scientific claims GENE-C01 through GENE-C12)
- **Foundational Project Vision:** [`docs/GENE_MOONSHOT.md`](docs/GENE_MOONSHOT.md)
- **Canonical Scientific Narrative:** [`docs/GENE_STORY_MEMO.md`](docs/GENE_STORY_MEMO.md)
- **System Architecture & Formalisms:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Interactive Research Exhibit:** [`docs/atlas/index.html`](docs/atlas/index.html)
- **Round 5 Results Reports:**
  - [Stage 5A Revision Precision Report](docs/results/EXPLORATION_ROUND5_STAGE5A_REPORT.md)
  - [Stage 5B Action Governance Report](docs/results/EXPLORATION_ROUND5_STAGE5B_REPORT.md)
  - [Stage 5C Neural Revision Bridge Report](docs/results/EXPLORATION_ROUND5_STAGE5C_REPORT.md)
  - [Round 5 Master Walkthrough](docs/results/EXPLORATION_ROUND5_WALKTHROUGH.md)

---

## Test Suite Execution

All experimental fixtures, oracle closures, statistical analyzers, revision engines, and governance evaluators run under pytest:

```bash
pytest -v
```
*Current test health: 164 passed in 23.76s (Zero warnings/errors).*
