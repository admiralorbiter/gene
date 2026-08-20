# Exploration Round 4: Stage 0 Overview & Research Charter

## 1. Title: *Compiling Belief — Preserving Epistemic Structure Across Neural Interfaces*

## 2. Executive Rationale & Scientific Positioning
Exploration Round 3 revealed a fundamental representational gap:
- **The Epistemic Kernel** maintains machine-readable **sets, graphs, and support hypergraphs** ($S_F$).
- **The Neural Reasoner** operates over **linear token sequences** ($\Phi(\sigma)$).
- **The Serialization Problem:** The mapping $\text{Hypergraph} \to \text{Sequence}$ does not preserve semantics by default, introducing non-monotonicity (Track H), presentation-order collapse (Track B3), and context-conditioned divergence (Track L).

### Positioning Relative to Adjacent Literature:
```
                              SURROUNDING LITERATURE POSITIONING
                              
┌─────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Research Line                   │ Primary Focus & Difference from GENE                                  │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ GraphDO / Lost in Serialization │ Graph structure -> sequence ordering effects on general reasoning.     │
│ Stable-RAG                      │ Retrieved text chunk permutations -> aggregation mitigations.          │
│ Set-LLM                         │ Architectural attention modifications for permutation-invariant sets.  │
│ LGMT / Semantic Invariance      │ Metamorphic relations on queries for black-box testing.               │
│ Monotonic Scaffolding           │ Adding pedagogic context -> measuring Success-to-Error flips.          │
│ GAVEL                           │ Post-hoc evidence auditing contracts.                                  │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ GENE Round 4                    │ Provenance-aware EpistemicIR (formal support + genealogical roots)     │
│ (Epistemic Context Compiler)    │ -> privilege-audited context compilation -> multi-dimensional          │
│                                 │ conformance vector K = (K_A, K_S, K_L, K_I).                           │
└─────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Four Parallel Research Threads (Round 4 Portfolio)

```
                            ROUND 4 PARALLEL RESEARCH PORTFOLIO
                            
┌──────────┬─────────────────────────────┬───────────┬────────────────────────────────────────────────────────┐
│ Track    │ Focus Area                  │ Calls (N) │ Central Scientific Question & Conformance Property     │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track R  │ Role Equivariance           │ 24 calls  │ Invert A <-> D: does shortcut shift from {B,D} to      │
│          │ (Semantic Dissection)       │           │ {A,E} (role-driven) or stay at {B,D} (graph slot)?     │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track P  │ Permutation Invariance      │ 28 calls  │ 24 raw flat permutations (neural spread) vs 1 compiled │
│          │ (Serialization Spread)      │           │ canonical prompt + 4 exact replays (0 calls for hash). │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track M  │ Support-Preserving          │ 32 calls  │ Mirror AB & DE chains with insertion counterbalancing: │
│          │ Monotonicity                │           │ measure Success-to-Error flips under valid augments.   │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track C  │ Epistemic Compiler          │ 32 calls  │ Privilege-audited benchmark over 4 backends evaluating │
│          │ Conformance Benchmark       │           │ conformance vector K = (K_A, K_S, K_L, K_I).           │
└──────────┴─────────────────────────────┴───────────┴────────────────────────────────────────────────────────┘
```

---

## 4. Architectural Chain of Custody

```
          EPISTEMIC KERNEL
      formal support / lineage
                │
                ▼
        EPISTEMIC STATE
  premises • rules • support envs
  (zero oracle answer leaks)
                │
                ▼
        CONTEXT COMPILER
   validity -> dedup -> ordering -> certificate
   [Privilege-Audited Pipeline]
                │
                ▼
        COMPILED CONTEXT
   prompt • source_hash • passes • privilege
                │
                ▼
         NEURAL REASONER
                │
                ▼
        CANDIDATE OUTPUT
                │
                ▼
      CONFORMANCE EVALUATOR
        K = (K_A, K_S, K_L, K_I)
```

---

## 5. Pre-Execution Gating & Zero-Compute Audit
- All shared schemas (`EpistemicState`, `QueryContract`, `CompiledContext`), transformation generators (`PermutationTransform`, `RoleEquivarianceTransform`, `SupportAugmentationTransform`), and compiler pipelines (`EpistemicContextCompiler`) are centralized in `src/gene/experiments/`.
- Tested and verified deterministically with **143/143 passing unit tests**.
- Zero live compute is spent until the Stage-1 registered report is reviewed and approved.
