# Exploration Round 2 — Stage-1 Adversarial Review & Process Post-Mortem

## 1. Executive Summary
This document records the Stage-1 Registered-Report Design Audit for Exploration Round 2 alongside the **post-execution audit findings** detailing which confounds were successfully caught and which subtle assay errors slipped through.

```
                              STAGE-1 AUDIT vs POST-EXECUTION REALITY
                              
┌──────────┬──────────────────────┬──────────────────┬────────────────────────────────────────────────────────┐
│ Track    │ Stage-1 Verdict      │ Post-Execution   │ Post-Mortem Finding                                    │
├──────────┼──────────────────────┼──────────────────┼────────────────────────────────────────────────────────┤
│ Track G  │ PASS                 │ CONFOUNDED       │ MISSED: Schema contained auxiliary answer leak         │
│          │                      │                  │ ("surviving_paths_count": 0); missing positive control.│
├──────────┼──────────────────────┼──────────────────┼────────────────────────────────────────────────────────┤
│ Track B2 │ PASS WITH CAVEAT     │ PARTIAL CONFOUND │ MISSED: Majority documents coupled to earlier          │
│          │                      │                  │ positions; residual token preference asymmetry.        │
├──────────┼──────────────────────┼──────────────────┼────────────────────────────────────────────────────────┤
│ Track A2 │ PASS                 │ OVERCLAIMED COST │ MISSED: Eager repair wrote direct strings to SQLite;   │
│          │                      │                  │ lazy revalidation was read filtering, not DB repair.   │
├──────────┼──────────────────────┼──────────────────┼────────────────────────────────────────────────────────┤
│ Track M  │ PASS                 │ VALIDATED RESULT │ CAUGHT: Model non-invariance demonstrated cleanly.     │
└──────────┴──────────────────────┴──────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Post-Mortem: Why Stage 1 Missed the Three Confounds

1. **Track G Auxiliary Schema Leak:**
   - The Stage-1 review verified that target string `PROTO_X7` was not leaked in the schema.
   - However, it failed to check auxiliary numeric fields: `"surviving_paths_count": 0` was hardcoded in the schema for both conditions, providing the wrong answer ($0$ instead of $1$) for `independent_survival`.
2. **Track B2 Positional Coupling:**
   - The Stage-1 review verified $N=5$ doc-count invariance and removed the word "independent".
   - However, it failed to verify that document presentation order was permuted independently from majority claim assignment.
3. **Track A2 Cost Logging:**
   - The Stage-1 review verified that SQL operations were active rather than static text files.
   - However, it failed to audit whether `update_eager_repair()` called `client.chat()` or directly inserted pre-baked target strings.

---

## 3. The Mechanical Stage-1 Audit Checklist for Round 3+

To prevent these failure modes, future Stage-1 reviews must execute a **mechanical code-level audit**:

```
[ ] 1. Schema Field Audit: Does EVERY field in the requested output schema use generic 
       placeholders (e.g. "surviving_paths_count": "INTEGER") rather than specific literal values?
[ ] 2. Positive Control Baseline: Is there an un-manipulated positive control prompt that 
       demonstrates the neural model can derive the target under the exact prompt syntax?
[ ] 3. Position Permutation: Are document presentation positions randomly permuted or 
       counterbalanced independently from claim majority?
[ ] 4. Cost Verification: Does every claimed computational metric correspond to an 
       actively executed, logged API call or memory write?
[ ] 5. Evaluation Layer Enforcement: Does the runner invoke record_evaluation() for every 
       live call (N_evaluations == N_calls)?
```
