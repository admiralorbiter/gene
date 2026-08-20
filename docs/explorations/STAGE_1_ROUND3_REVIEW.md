# Exploration Round 3 — Stage-1 Registered-Report & Machine-Diff Audit

## 1. Executive Summary & Review Mandate
This document executes the mandatory pre-execution **Stage-1 Registered-Report Audit** for **Exploration Round 3: *When One Belief Has Many Reasons*** across all five tracks.

All 10 mechanical checklist items and preregistered interpretation rules are verified prior to live compute:

```
                           STAGE-1 MECHANICAL AUDIT MATRIX
                           
┌──────────┬─────────────────────────────┬─────────────────┬──────────────────────────────────────────┐
│ Track    │ Focus Area                  │ Stage-1 Verdict │ 10-Item Mechanical Audit Status          │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track H  │ Coalition Causality         │ PASS            │ Full 2^4=16-point power set lattice;     │
│          │ (Full Overdetermination)    │                 │ pure omission; S_C extraction; smoke OK. │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track G2 │ Non-Destructive Immunity    │ PASS            │ 5 arms with executed governance policy;  │
│          │ (Clean Governance Policies) │                 │ dynamic rules for AX+AY; smoke OK.       │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track B3 │ Monoculture Multiverse      │ PASS            │ Pure lexical isolation; 16 cells + 4 rep │
│          │ (Factorial Multiverse)      │                 │ + 4 seed perturb (4-factor balanced).    │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track S  │ Support Acquisition         │ PASS            │ Validated compiler prototype (0 calls).  │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track L  │ Independence Laundering     │ PASS            │ 5 stages with 4-root CTL; non-forced     │
│          │ (Epistemic Observability)   │                 │ reject-option schema; smoke OK.          │
└──────────┴─────────────────────────────┴─────────────────┴──────────────────────────────────────────┘
```

---

## 2. Preregistered Interpretation Rules
1. **Track H (Coalition Causality):** Classify outcomes into four discrete categories: (a) *formal concordance* ($S_C = S_F$), (b) *behavioral shortcut / partial concordance*, (c) *de-novo support* ($S_C = \{\emptyset\}$), or (d) *non-monotonic / discordant*. $S_C(C)$ denotes the *minimal behaviorally sufficient exposure environments*.
2. **Track G2 (Non-Destructive Immunity):** Retained valid support environments are evaluated deterministically at the kernel layer, separate from downstream LLM reasoning correctness. *Preservation* and *safe collapse* are two distinct scientific endpoints.
3. **Track B3 (Monoculture Multiverse):** Estimate the substantive root discounting effect $\Delta_{\text{root}}$ strictly from the primary 16 factorial cells. The 4 exact replays and 4 seed perturbations are reserved strictly for estimating $\epsilon_{\text{replay}}$ and $\epsilon_{\text{seed}}$.
4. **Track L (Independence Laundering):** `independence_status: "indeterminable"` is a first-class valid epistemic phenotype indicating resistance to manufactured corroboration. At $G_3$, there is no single forced "correct" integer count.

---

## 3. Ten-Item Mechanical Checklist Verification

```
[x] 1. Schema Field Audit: All requested output schemas use generic placeholders only.
[x] 2. Positive Control Baseline: Un-manipulated baseline arms included in all tracks.
[x] 3. Position Permutation: Factorially permuted in Track B3 ([1,2,3,4,5] vs [4,1,5,2,3]).
[x] 4. Cost Verification: All runners execute actual client calls; zero direct-write bypassing.
[x] 5. Evaluation Layer Enforcement: Verified contemporaneous record_evaluation() in all runners.
[x] 6. Causal-Role Equivariance: Token identities and station entities counterbalanced.
[x] 7. Contrast Reconstruction: Machine diff between Track B3 conditions shows strictly root token changes:
       -- DOC_02: Source root_R2 ... -> +- DOC_02: Source root_R1 ...
       -- DOC_03: Source root_R3 ... -> +- DOC_03: Source root_R1 ...
[x] 8. Executable Runner Smoke Tests: Verified in tests/explore_round3/test_runners_smoke.py.
       All 4 live runners complete 1 call under FakeOllamaClient with N_calls == N_evaluations == 1.
[x] 9. Endpoint Traceability Audit: Track L parses and persists both independence_status and
       estimated_independent_sources into eval_metadata_json.
[x] 10. Representation Expressiveness Audit: Track S TraceSupportCompiler expresses both AND-conjunctive
        and OR-disjunctive derivation environments, extracting {{fact_A, fact_B}, {fact_D, fact_E}}.
```

---

## 4. Live Compute Allocation (Total 96 Calls)
- **Track H (Coalition Causality):** 32 calls (16 lattice points $\times$ 2 stations)
- **Track G2 (Non-Destructive Immunity):** 20 calls (5 arms $\times$ 2 stations $\times$ 2 reps)
- **Track B3 (Monoculture Multiverse):** 24 calls (16 factorial cells + 4 exact replays + 4 seed perturbations)
- **Track S (Support Acquisition):** 0 calls (deterministic formal compiler verification)
- **Track L (Independence Laundering):** 20 calls (5 stages $\times$ 2 stations $\times$ 2 protocols)
- **Total Portfolio Live Compute Allocation:** **96 calls**.

---

## 5. Gating Verdict
All five Round-3 designs satisfy the 10-item registered-report checklist:
$$\text{Audit Passed} \implies \text{Ready for Live Canary & Parallel Execution.}$$
