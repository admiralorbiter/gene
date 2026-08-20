# Exploration Round 3 — Stage-1 Registered-Report & Machine-Diff Audit

## 1. Executive Summary & Review Mandate
This document executes the mandatory pre-execution **Stage-1 Registered-Report Audit** for **Exploration Round 3: *When One Belief Has Many Reasons*** across all five tracks.

All 10 mechanical checklist items are verified prior to live compute:

```
                           STAGE-1 MECHANICAL AUDIT MATRIX
                           
┌──────────┬─────────────────────────────┬─────────────────┬──────────────────────────────────────────┐
│ Track    │ Focus Area                  │ Stage-1 Verdict │ 10-Item Mechanical Audit Status          │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track H  │ Coalition Causality         │ PASS            │ 11-point lattice; S_C extraction wired;  │
│          │ (Overdetermination Lattice) │                 │ runner smoke test passed (N_eval=N_call).│
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track G2 │ Non-Destructive Immunity    │ PASS            │ Real policy context filters; shared CTL; │
│          │ (Clean Governance Policies) │                 │ runner smoke test passed (N_eval=N_call).│
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track B3 │ Monoculture Multiverse      │ PASS            │ Pure lexical isolation; 16 cells+8 repl; │
│          │ (Factorial Multiverse)      │                 │ runner smoke test passed (N_eval=N_call).│
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track S  │ Support Acquisition         │ PASS            │ OR/AND backward compiler verified (0 cal)│
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track L  │ Independence Laundering     │ PASS            │ 5 stages with 4-root CTL; parsed sources;│
│          │ (Diversity Inflation)       │                 │ runner smoke test passed (N_eval=N_call).│
└──────────┴─────────────────────────────┴─────────────────┴──────────────────────────────────────────┘
```

---

## 2. Ten-Item Mechanical Checklist Verification

```
[x] 1. Schema Field Audit: All requested output schemas use generic placeholders only.
[x] 2. Positive Control Baseline: Un-manipulated baseline arms included in all tracks.
[x] 3. Position Permutation: Factorially permuted in Track B3 ([1,2,3,4,5] vs [4,1,5,2,3]).
[x] 4. Cost Verification: All runners execute actual client calls; zero direct-write bypassing.
[x] 5. Evaluation Layer Enforcement: Verified contemporaneous record_evaluation() in all runners.
[x] 6. Causal-Role Equivariance: Token identities and station entities counterbalanced.
[x] 7. Contrast Reconstruction: Machine diff between Track B3 conditions shows strictly root token changes:
       - DOC_02: Source root_R2 ... -> + DOC_02: Source root_R1 ...
       - DOC_03: Source root_R3 ... -> + DOC_03: Source root_R1 ...
[x] 8. Executable Runner Smoke Tests: Verified in tests/explore_round3/test_runners_smoke.py.
       All 4 live runners complete 1 call under FakeOllamaClient with N_calls == N_evaluations == 1.
[x] 9. Endpoint Traceability Audit: Track L parses and persists estimated_independent_sources into eval_metadata_json.
[x] 10. Representation Expressiveness Audit: Track S TraceSupportCompiler expresses both AND-conjunctive
        and OR-disjunctive derivation environments, extracting {{fact_A, fact_B}, {fact_D, fact_E}}.
```

---

## 3. Revised Live Compute Allocation (Ceiling $\le 82$ Calls)
- **Track H (Coalition Causality):** 22 calls
- **Track G2 (Non-Destructive Immunity):** 16 calls
- **Track B3 (Monoculture Multiverse):** 24 calls
- **Track S (Support Acquisition):** 0 calls (deterministic formal verification)
- **Track L (Independence Laundering):** 20 calls
- **Total Portfolio Live Compute Allocation:** **82 calls** (below original 84 ceiling).

---

## 4. Gating Verdict
All five Round-3 designs satisfy the 10-item registered-report checklist:
$$\text{Audit Passed} \implies \text{Ready for Live Canary & Parallel Execution.}$$
