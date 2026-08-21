# Exploration Round 6 Stage 6B Benchmark Report: Contract-Guided State Adjudication

**Assay Name**: Contract-Guided State Adjudication & Predicate Transition Semantics (Stage 6B)  
**Dataset Artifact**: [`../../data/exploration_round6_stage6b_cases.jsonl`](../../data/exploration_round6_stage6b_cases.jsonl) ($N=200$ cases)  
**Summary Artifact**: [`../../data/exploration_round6_stage6b_results_summary.json`](../../data/exploration_round6_stage6b_results_summary.json)  
**Execution Timestamp**: `2026-08-21T04:32:30Z`  

---

## Executive Summary

Stage 6B evaluates how memory systems adjudicate incoming factual observations without explicit transition labels (`ASSERT`, `SUPERSEDES`, `RETRACT`). 

Across a factorial matrix of **200 test cases** ($4 \text{ PredicateModes} \times 5 \text{ UpdatePatterns} \times 2 \text{ SourceRelations} \times 5 \text{ SupportTopologies}$), we compare 6 memory architectures to isolate three essential capabilities:
1. **Temporal Validity Modeling** ($t_v \times t_k$)
2. **Predicate Contract Semantics** (Functional vs Multivalued vs Episodic vs Interval)
3. **Downstream Antichain Support Algebra** ($\mathcal{S}_t(c)$ vs Flat Dependencies)

```
+===========================================================================================================================================+
|                                    STAGE 6B FACTORIAL BENCHMARK COMPARATIVE RESULTS (N=200)                                               |
+================================+=============+====================+======================+================+==================+=========+
| Memory Architecture Arm        | Stale Ret % | False Supersede %  | Revision Autoimmune %| Zombie Ret %   | Support Fidelity | Ent Acc |
+================================+=============+====================+======================+================+==================+=========+
| `ARM_1_APPEND_ONLY` | 15.0% | 0.0% | 0.0% | 2.5% | 0.0% | **79.0%** |
| `ARM_2_KNOWLEDGE_TIME_LWW` | 0.0% | 50.0% | 20.0% | 10.0% | 0.0% | **80.0%** |
| `ARM_3_VALID_TIME_LWW` | 5.0% | 50.0% | 0.0% | 10.0% | 0.0% | **100.0%** |
| `ARM_4_BITEMPORAL_LATEST` | 0.0% | 50.0% | 0.0% | 10.0% | 0.0% | **100.0%** |
| `ARM_5_PREDICATE_CONTRACT_FLAT` | 0.0% | 0.0% | 6.0% | 0.0% | 94.0% | **94.0%** |
| `ARM_6_GENE_KERNEL` | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% | **100.0%** |
+================================+=============+====================+======================+================+==================+=========+
```

---

## Key Scientific Discoveries

1. **Time Alone Is Insufficient ($LWW \implies 50.0\%$ False Supersessions)**:
   Pure temporal policies (`ARM_2_KNOWLEDGE_TIME_LWW`, `ARM_3_VALID_TIME_LWW`, `ARM_4_BITEMPORAL_LATEST`) treat all value updates as replacements, wiping out $50.0\%$ of valid multivalued skills and episodic history.
2. **Append-Only Produces Stale & Zombie Entitlement ($15.0\%$ Stale, $2.5\%$ Zombie)**:
   Naive append-only memory (`ARM_1`) never cleanses replaced functional states and fails to isolate contemporaneous contradictions from competing sources, dropping Entitlement Accuracy to $79.0\%$.
3. **Predicate Contracts Alone Suffer Revision Autoimmunity ($6.0\%$)**:
   `ARM_5_PREDICATE_CONTRACT_FLAT` correctly adjudicates state transitions at the premise level ($0\%$ stale, $0\%$ false supersessions), but its flat dependency model triggers **$6.0\%$ false retractions** on multi-path derivations when one alternative premise is superseded (limiting Support Fidelity to $94.0\%$).
4. **GENE Epistemic Kernel Achieves Dual-Layer Optimality ($100.0\%$ Accuracy)**:
   By uniting **Predicate Contract Adjudication** with **Bitemporal Antichain Support Algebra** ($\mathcal{S}_t \to \mathcal{S}_{L,t}$), `ARM_6_GENE_KERNEL` eliminates all four failure channels ($0\%$ stale, $0\%$ false supersession, $0\%$ autoimmune, $0\%$ zombie), achieving **$100.0\%$ Support Fidelity and $100.0\%$ Entitlement Accuracy**.
