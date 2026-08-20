# GENE Exploration Round 2 — Portfolio Batch Review & Post-Execution Audit

## 1. Executive Portfolio Scorecard (Post-Review Audit)
Executed off the frozen substrate base (`gene-exploration-round2-base` at commit `2685987`) with a total budget cap of $\le 90$ live calls. Total live compute spent: **48 live calls**.

```
                              ROUND 2 POST-REVIEW SCORECARD
                              
┌──────────┬──────────────────────┬───────┬───────────────────────────┬────────────────────────────────────────┐
│ Track    │ Focus Area           │ Calls │ Final Post-Review Status  │ Core Finding / Confound Identified     │
├──────────┼──────────────────────┼───────┼───────────────────────────┼────────────────────────────────────────┤
│ Track A2 │ Dynamic Memory       │   12  │ PROMISING — HARDEN        │ Stale descendants survive overwrite;   │
│          │                      │       │                           │ read-time rederivation works on filter.│
├──────────┼──────────────────────┼───────┼───────────────────────────┼────────────────────────────────────────┤
│ Track B2 │ Monoculture Hardened │   16  │ PROMISING — HARDEN        │ Models don't spontaneously discount;   │
│          │                      │       │                           │ residual token/position bias remains.  │
├──────────┼──────────────────────┼───────┼───────────────────────────┼────────────────────────────────────────┤
│ Track G  │ Multi-Justification  │   12  │ G-Formal: VALIDATED       │ Minimal support algebra S(c) verified; │
│          │                      │       │ G-Live: CONFOUNDED        │ live run had schema count leak & no CTL│
├──────────┼──────────────────────┼───────┼───────────────────────────┼────────────────────────────────────────┤
│ Track M  │ Model Calibration    │    8  │ VALIDATED METHODOLOGY     │ Qwen/Llama fail zero-shot gateway;     │
│          │                      │       │                           │ model-specific adapters required.      │
└──────────┴──────────────────────┴───────┴───────────────────────────┴────────────────────────────────────────┘
```

---

## 2. Detailed Track-by-Track Post-Review Audits

### Track A2: Dynamic Memory Repair & Lazy Revalidation
- **What Survives:** Root overwrite fails completely ($H_{\text{stale}} = 4/4$) in active SQLite storage because stale intermediate lemmas remain retrievable. Excluding dirty records and supplying clean root context allows read-time rederivation ($4/4$ clean).
- **What Was Overextended / Corrected:** Eager repair wrote hard-coded values directly to SQLite without issuing LLM calls (`llm_calls = 0`). Lazy revalidation did not evaluate minimal support sets or rewrite persistent records; it operated as read-time dirty-state filtering.
- **Status:** **PROMISING — HARDEN.**

### Track B2: Monoculture Hardening
- **What Survives:** Under matched $N=5$ documents and opaque roots, Gemma did not spontaneously discount repeated reports when told they shared `root_R1` (abstained in both `concur_X` and `conflict_roots_Y`).
- **What Was Overextended / Corrected:** The initial conclusion that models are "pure repetition counters" was contradicted by $P(X) = 0.000$ on $X$-majority vs $P(Y) = 0.750$ on $Y$-majority. There was an un-counterbalanced positional coupling (majority claims placed in earlier slots) and token preference asymmetry (`PROTO_X` vs `PROTO_Y`).
- **Status:** **PROMISING — HARDEN.**

### Track G: Multi-Justification & Epistemic Recombination
- **G-Formal Engine:** `MinimalSupportEngine` is mathematically validated across all 4 canonical geometries ($AB \to C$, $AB + DE \to C$, $AX + AY \to C$, $AI + BH \to C$).
- **G-Live Assay:** Confounded. The prompt schema contained `"surviving_paths_count": 0` in both conditions, giving the wrong expected value ($0$ instead of $1$) for `independent_survival`. No positive control arm without revocation was tested.
- **Status:** **G-Formal: VALIDATED FORMAL PROTOTYPE; G-Live: CONFOUNDED.**

### Track M: Measurement Invariance & Model Calibration Gateway
- **What Survives:** Both `qwen2.5:3b` and `llama3.2:3b` failed the 4-case zero-shot gateway ($1/4$ pass), demonstrating that response-contract calibration is strictly model-dependent.
- **Status:** **VALIDATED METHODOLOGY RESULT.**

---

## 3. Meta-Scientific & Process Lessons

### 1. The Evaluation Layer Gap
The `ExplorationHarness` was upgraded to support structured `exploration_evaluations` records, but none of the four runners invoked `record_evaluation()`, resulting in 0 evaluation records across all 48 calls. Future batches must enforce $N_{\text{evaluations}} = N_{\text{calls}}$ in CI.

### 2. Stage-1 Adversarial Review Iteration
The Stage-1 preflight review successfully eliminated several Round-1 confounds, but missed three subtle assay-level errors:
- Track G: Auxiliary schema answer count leak (`"surviving_paths_count": 0`).
- Track B2: Un-counterbalanced document position coupling.
- Track A2: Simulated eager repair LLM costs.

Future Stage-1 reviews must execute **mechanical contrast audits**:
1. Does every schema field vary correctly across conditions?
2. Are document presentation positions independently permuted from claim majority?
3. Does every claimed cost metric correspond to an executed, logged operation?
4. Does an un-manipulated positive control pass in the exact prompt syntax?

---

## 4. Current State & Next Steps

Phase 11 has **not** been earned yet.

However, the four exploratory tracks converge upon a clear next research frontier:

> **From Lineage Trees to Minimal Support Environments:**
> A descendant's relationship to an invalidated ancestor is insufficient to determine whether the descendant should survive. Durable belief maintenance requires evaluating whether any valid independent justification remains in $S(c)$.

The single highest-value experiment on the board is now:
Testing **non-destructive lineage survival ($AB + DE \to C$) vs shared-root collapse ($AX + AY \to C$)** under a clean, un-confounded live assay without schema count leaks and with an un-manipulated positive control baseline.
