# Exploration Round 4: Stage 0 Overview & Research Charter

## 1. Title: *Compiling Belief — Preserving Epistemic Structure Across Neural Interfaces*

## 2. Executive Rationale & Scientific Opportunity
Exploration Round 3 revealed a fundamental representational gap:
- **The Epistemic Kernel** maintains machine-readable **sets, graphs, and support hypergraphs** ($S_F$).
- **The Neural Reasoner** operates over **linear token sequences** ($\Phi(\sigma)$).
- **The Serialization Problem:** Serializing an unordered graph into an ordered sequence introduces non-monotonicity (Track H), presentation-order collapse (Track B3), and context-conditioned epistemic divergence (Track L).

Round 4 does not attempt to "optimize prompts" or claim generic discovery of order effects (well-documented in *Lost in Serialization*, *GraphDO*, *Stable-RAG*, *GroupQA*). Instead, Round 4 establishes the systems discipline of **Epistemic Context Compilation**: compiling explicit machine-readable states ($\mathcal{E} \in \text{EpistemicIR}$) into neural contexts that strictly conform to semantic invariants.

---

## 3. Four Parallel Research Threads (Round 4 Portfolio)

```
                            ROUND 4 PARALLEL RESEARCH PORTFOLIO
                            
┌──────────┬─────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Track    │ Thread Name                 │ Central Scientific Question & Conformance Property                     │
├──────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Track R  │ Role Equivariance           │ Does Track H's shortcut follow the semantic role 'sector_lead',        │
│          │ (Semantic Dissection)       │ the graph slot D, or disappear under synthetic opaque tokens?          │
├──────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Track P  │ Permutation Invariance      │ Across semantically identical support states, how large is the output  │
│          │ (Serialization Spread)      │ spread over evidence permutations, and does compilation eliminate it?  │
├──────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Track M  │ Support-Preserving          │ Can adding formally compatible, non-contradictory evidence turn a      │
│          │ Monotonicity                │ correct answer into an error/abstention (Success-to-Error flips)?      │
├──────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Track C  │ Epistemic Compiler          │ Can deterministic context compilation reduce worst-case representation │
│          │ Conformance Benchmark       │ failures and preserve root counts without modifying model weights?     │
└──────────┴─────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Architectural Component: The Epistemic Context Compiler

```
                    EPISTEMIC KERNEL
          formal support (S_F) / lineage (G)
                          │
                          ▼
                    EPISTEMIC IR
     claims • minimal support sets • roots • status
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
   EXTERNAL COMPILER             INVARIANT MODEL
   (frozen sequence LLMs)        (Set-LLM positional encodings)
   * Validity pruning
   * Support path grouping
   * Lineage deduplication
   * Audit certificates
            │                           │
            └─────────────┬─────────────┘
                          ▼
                  SEMANTICS-PRESERVED
                     NEURAL USE
```

---

## 5. Pre-Execution Gating & Zero-Compute Discipline
- All shared schemas (`EpistemicIR`), transformation generators (`PermutationTransform`, `RoleEquivarianceTransform`, `SupportAugmentationTransform`), and compiler backends (`EpistemicContextCompiler`) are centralized in `src/gene/experiments/`.
- Zero live compute is spent until the Stage-1 registered report is reviewed and audited.
