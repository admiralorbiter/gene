# Exploration Round 7 Stage 7A Report: Epistemic Ingress & Deterministic Benchmark Assay

**Document Status**: Canonical Empirical Report  
**Author**: Antigravity Research / GENE Core  
**Associated Target Commit**: `round7-stage7a-execution-freeze`  
**Prerequisites**: Exploration Round 7 Wave 0.2 Freeze ([`round7-wave0-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round7-wave0-freeze))  
**Primary Artifact**: [`data/exploration_round7_stage7a_benchmark_summary.json`](../../data/exploration_round7_stage7a_benchmark_summary.json)  

---

## 1. Executive Summary & Paradigm Shift

Exploration Round 7 addresses the foundational boundary problem of persistent agent intelligence:
> *What proof, authority, and referential guarantees must accompany incoming information before persistent memory is allowed to believe it?*

Stage 7A implements and validates the **Proof-Carrying Epistemic Ingress Engine** across a balanced **120-world factorial benchmark** ($N=480$ formal probe evaluations) and three dedicated diagnostic sidecars.

By holding the downstream epistemic kernel (Bitemporal State Engine, Antichain Support Minimizer, and Action Governance) strictly constant, Stage 7A causally isolates the impact of five comparative ingress policies (`A0` to `A4`):

```
+========================================================================================================+
|                        STAGE 7A FACTORIAL INGRESS BENCHMARK (N=120 WORLDS / 480 PROBES)                |
+=========================+==============+==============+==============+==============+==================+
| Architecture Arm        | WorldPass    | Global FDAR  | SAC Coverage | UPR Preserve | Primary Failure  |
+=========================+==============+==============+==============+==============+==================+
| A0: Top-1 Blind Write   | 50.0% (60)   | 71.4% (60/84)| 100.0% (36)  | 0.0% (0/24)  | Blind Admission  |
| A1: Canonicalize Only   | 50.0% (60)   | 71.4% (60/84)| 100.0% (36)  | 0.0% (0/24)  | Blind Admission  |
| A2: Candidate-Aware     | 70.0% (84)   | 42.9% (36/84)| 100.0% (36)  | 100.0% (24)  | Unauthorized Auth|
| A3: Authority-Aware     | 90.0% (108)  | 14.3% (12/84)| 100.0% (36)  | 0.0% (0/24)  | Ambiguity Collapse|
| A4: Full GENE Ingress   | 100.0% (120) | 0.0% (0/84)  | 100.0% (36)  | 100.0% (24)  | None (Mastery)   |
+=========================+==============+==============+==============+==============+==================+
```

---

## 2. Core Architectural Discoveries

### 2.1 The Epistemic Alternative-Preservation Principle
$$\text{Preserve alternatives when future interventions may distinguish them}$$
- **Derivational Symmetry (Round 5)**: Antichain support sets $\mathcal{S}(c)$ preserve alternative derivation paths.
- **Referential Symmetry (Round 7)**: Candidate hypothesis sets $\mathcal{B}(x) = \{b_1, \dots, b_k\}$ are preserved under **`DEFERRED_BINDING`**.
- When new disambiguating evidence arrives at $t_2$, the runtime prunes hypotheses ($\mathcal{B}(x) \to \{B\} \to \text{ADMIT}(B)$) without reparsing or inventing new provenance roots.

### 2.2 Unconfounded Ablation Progression
Holding the downstream bitemporal engine constant cleanly unmasks the specific failure phenotypes of each missing ingress abstraction:
1. **`A0 / A1` (Blind Ingress)**: Suffer catastrophic $71.4\%$ False Durable Admission Rate ($\text{FDAR}$), admitting unauthorized third-party claims and collapsed collision candidates directly into the bitemporal occurrence log.
2. **`A2` (Candidate-Aware Only)**: Perfectly preserves ambiguous candidates and novel entities ($\text{UPR} = 100.0\%$, $\text{FDAR}_{\text{ambiguity}} = 0.0\%$, $\text{FDAR}_{\text{novel}} = 0.0\%$), but suffers $100\%$ unauthorized promotion on out-of-scope third-party claims ($\text{FDAR}_{\text{authority}} = 100.0\%$).
3. **`A3` (Authority-Aware Only)**: Perfectly eliminates unauthorized promotion ($\text{FDAR}_{\text{authority}} = 0.0\%$), but prematurely collapses candidate collisions to Top-1 ($\text{FDAR}_{\text{ambiguity}} = 50.0\%$, $\text{UPR} = 0.0\%$).
4. **`A4` (Full GENE Ingress)**: Unifies hypothesis preservation, capability-scoped authorization, `PROVISIONAL_ENTITY` tracking, and proof-carrying admission certificates, achieving **$100.0\%$ $\text{WorldPass}$**, **$\text{FDAR} = 0.0\%$**, **$\text{SAC} = 100.0\%$**, and **$\text{UPR} = 100.0\%$**.

---

## 3. Disaggregated Sidecar Results

1. **Candidate Miss vs True Novelty Sidecar**:
   - `NOVEL_TRUE` creates a `PROVISIONAL_ENTITY` with raw mention spans and provenance.
   - `KNOWN_BUT_CANDIDATE_MISS` (entity in global ontology but missed by retriever) triggers retrieval fallback without creating spurious duplicate entity IDs ($100\%$ pass).
2. **Role Distractor vs True Ambiguity Sidecar**:
   - Monitored entity vs reporting sensor ambiguity is structurally resolved to the correct Subject ($100\%$ `ADMIT`).
   - True linguistic under-specification preserves both hypotheses under `DEFERRED_BINDING` ($100\%$ `DEFER`).
3. **Paired Authority Sidecar ($\text{do}(\text{SourceClass} = s_i)$)**:
   - Evaluated across `PLATFORM_ATTESTED`, `USER_DIRECT`, `THIRD_PARTY_QUOTED`, and `MODEL_DERIVED`.
   - Out-of-scope and unauthenticated third-party claims are strictly prevented from gaining `ROOT_FACT` status ($100\%$ fail-closed).
4. **Certificate Verifier Mutation Assay**:
   - Forged binding witnesses, out-of-scope capabilities, altered valid-time intervals, and rootless certificates fail closed ($5/5$ mutation attacks rejected).

---

## 4. Verification & Audit Integrity

- **Automated Tests**: 192 total tests passed in 36.24s.
- **Artifact SHA-256**: [`data/exploration_round7_stage7a_benchmark_summary.json`](../../data/exploration_round7_stage7a_benchmark_summary.json) verified.
- **Git State**: All files tracked in repository with zero worktree drift.
