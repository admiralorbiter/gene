# Exploration Round 4 — Stage-1 Registered-Report & Conformance Audit

## 1. Executive Summary & Gating Status
This document executes the comprehensive **Stage-1 Registered-Report & Executable Preflight Audit** for **Exploration Round 4: *Compiling Belief — Preserving Epistemic Structure Across Neural Interfaces***.

All 7 mechanical and executable preflight gates are fully verified prior to live compute:

```
                            STAGE-1 MECHANICAL & EXECUTABLE AUDIT MATRIX
                            
┌──────────────────────────────┬────────┬────────────────────────────────────────────────────────────────────────┐
│ Mechanical / Executable Gate │ Status │ Verification Evidence & Implementation Guarantee                      │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────────────────────┤
│ 1. IR Proof Consistency      │ PASS   │ validate_ir_consistency() performs first-order variable unification    │
│                              │        │ (subject/entity binding) and minimality enforcement. Cross-entity and  │
│                              │        │ non-minimal sets are mechanically rejected.                           │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────────────────────┤
│ 2. State Identity (H_state)  │ PASS   │ Complete hash covers occurrence IDs, roots, parentage, citations,      │
│                              │        │ validity, authority, generation, rules, and support paths.             │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────────────────────┤
│ 3. Typed Equivalence Invar.  │ PASS   │ Invariants verified: H_perm (order invariance), H_rep (reproduction   │
│                              │        │ copy invariance with root discrimination), H_alpha (topological role   │
│                              │        │ slot invariance under alpha-renaming).                                 │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────────────────────┤
│ 4. Provenance Conservation   │ PASS   │ Full-pass conservation asserted: forall o in source, o in emitted (+) │
│                              │        │ merged (+) dropped with zero overlap, zero omission, and validity drop │
│                              │        │ reasons recorded.                                                      │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────────────────────┤
│ 5. Substate Consistency      │ PASS   │ subselect_occurrences() produces truthful substates with recomputed    │
│                              │        │ surviving paths passing partial-state validation.                      │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────────────────────┤
│ 6. Executable Endpoints      │ PASS   │ Production CallSpec/ModelCallResult integration, relational evaluators │
│                              │        │ (K_I panel entropy/disagreement, K_mono S->E transitions, K_role       │
│                              │        │ classification), immutable round4_calls/round4_evaluations tables, and │
│                              │        │ fake smoke tests verified across all 4 runners.                        │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────────────────────┤
│ 7. Privilege Audit Matrix    │ PASS   │ Explicitly audits passes (validity, dedup, ordering, certificate) for  │
│                              │        │ RAW, TOPOLOGY_AWARE, GENEALOGICAL_NORM, and PROOF_CARRYING pipelines.  │
└──────────────────────────────┴────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Integrated Conformance Program (Total Allocation: 116 Live Calls)

```
                            ROUND 4 INTEGRATED CONFORMANCE PROGRAM
                            
┌──────────┬─────────────────────────────┬───────────┬───────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Track    │ Focus Area                  │ Calls (N) │ Primary Metric Measured           │ Executable Runner Implementation                       │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track R  │ Role Equivariance           │ 24 calls  │ K_role (Role Follow vs Slot)      │ scripts/explore_round4/run_track_r.py                  │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track P  │ Permutation Invariance      │ 28 calls  │ K_I (Permutation Invariance)      │ scripts/explore_round4/run_track_p.py                  │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track M  │ Support-Preserving          │ 32 calls  │ K_mono (Monotonic Scaffolding)    │ scripts/explore_round4/run_track_m.py                  │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track C  │ Epistemic Compiler          │ 32 calls  │ K_A (Answer), K_S (Support Path), │ scripts/explore_round4/run_track_c.py                  │
│          │ Conformance Benchmark       │           │ K_L (Lineage Root Count)          │                                                        │
└──────────┴─────────────────────────────┴───────────┴───────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Preflight Gating & Canary Strategy
- **Master Orchestrator:** [`scripts/explore_round4/run_round4_master.py`](../../scripts/explore_round4/run_round4_master.py)
- **Canary Protocol:** Before spending the 116 live calls, 4 isolated canary calls (1 per track) will be executed into a disposable canary database (`data/canary_round4.db`) using the production `OllamaClient` to verify real Gemma 3:12B JSON formatting and schema conformance.
- **Stage 1 Status:** **100% Passed (145/145 unit tests passing across repo).**
