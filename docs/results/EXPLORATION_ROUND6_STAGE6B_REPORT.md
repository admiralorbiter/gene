# Exploration Round 6 Stage 6B Benchmark Report: Contract-Guided State Adjudication

**Assay Name**: Contract-Guided State Adjudication & Predicate Transition Semantics (Stage 6B)  
**Dataset Artifact**: [`../../data/exploration_round6_stage6b_cases.jsonl`](../../data/exploration_round6_stage6b_cases.jsonl) ($N=200$ cases)  
**Summary Artifact**: [`../../data/exploration_round6_stage6b_results_summary.json`](../../data/exploration_round6_stage6b_results_summary.json)  
**Execution Timestamp**: `2026-08-21T04:42:09Z`  

---

## Executive Summary

Stage 6B evaluates how memory systems adjudicate incoming factual observations without explicit transition labels (`ASSERT`, `SUPERSEDES`, `RETRACT`). 

Across a factorial matrix of **200 test cases** ($4 \text{ PredicateModes} \times 5 \text{ UpdatePatterns} \times 2 \text{ SourceRelations} \times 5 \text{ SupportTopologies}$), we compare 6 **fully executed memory policy implementations** across three distinct layers:
1. **Layer A (Adjudication Transition Fidelity)**: Does the policy emit the correct formal state transitions?
2. **Layer B (Premise State Fidelity)**: Does the policy maintain the correct active premise universe $\mathcal{F}(t_v \mid t_k)$?
3. **Layer C (Downstream Epistemic Maintenance)**: Does the policy correctly maintain downstream minimal support $\mathcal{S}_t(c)$ and entitlement $\text{Ent}(c)$?

```
+===================================================================================================================================================================+
|                                              STAGE 6B FACTORIAL BENCHMARK COMPARATIVE RESULTS (N=200)                                                             |
+================================+=============+=============+========================+========================+========================+==============+=========+
| Memory Architecture Arm        | Layer A Tr %| Layer B St %| Stale Ret (Cond/Opp)   | FalseSup (Cond/Opp)    | Autoimmune (Cond/Opp)  | Supp Fidelity| Ent Acc |
+================================+=============+=============+========================+========================+========================+==============+=========+
| `ARM_1_APPEND_ONLY` | 60.0% | 40.0% | 100.0% (120/120) | 0.0% (0/80) | 0.0% (0/72) | N/A | **76.0%** |
| `ARM_2_KNOWLEDGE_TIME_LWW` | 60.0% | 55.0% | 0.0% (0/120) | 100.0% (80/80) | 66.7% (48/72) | N/A | **76.0%** |
| `ARM_3_VALID_TIME_LWW` | 60.0% | 55.0% | 0.0% (0/120) | 100.0% (80/80) | 66.7% (48/72) | N/A | **76.0%** |
| `ARM_4_BITEMPORAL_LATEST` | 60.0% | 55.0% | 0.0% (0/120) | 100.0% (80/80) | 66.7% (48/72) | N/A | **76.0%** |
| `ARM_5_PREDICATE_CONTRACT_FLAT` | 100.0% | 100.0% | 0.0% (0/120) | 0.0% (0/80) | 100.0% (72/72) | N/A | **64.0%** |
| `ARM_6_GENE_KERNEL` | 100.0% | 100.0% | 0.0% (0/120) | 0.0% (0/80) | 0.0% (0/72) | 100.0% | **100.0%** |
+================================+=============+=============+========================+========================+========================+==============+=========+
```

---

## Key Scientific Discoveries & 3-Layer Decomposition

### 1. Layer A: Temporal Order Cannot Infer Transition Types
- Pure temporal stores (`ARM_2_KNOWLEDGE_TIME_LWW`, `ARM_3_VALID_TIME_LWW`, `ARM_4_BITEMPORAL_LATEST`) possess **$60.0\%$ transition fidelity** (matching only trivial assertions) because timestamps alone cannot distinguish a replacement from an additive accumulation or a contemporaneous dispute.
- The shared `PredicateContractAdjudicator` achieves **$100.0\%$ transition fidelity** on Arms 5 and 6, proving that predicate ontologies provide the necessary transition schema.

### 2. Layer B: Generic LWW Causes $100\%$ Conditional False Supersessions
- Across the $80$ additive and episodic cases, generic LWW policies incorrectly wipe out historical occurrences in **$100.0\%$ of opportunities** ($80/80$, $40.0\%$ global incidence).
- Naive append-only (`ARM_1`) causes **$100.0\%$ conditional stale retention** ($120/120$, $60.0\%$ global incidence) when functional or interval states are updated.

### 3. Layer C: Flat Dependencies Suffer $100\%$ Revision Autoimmunity on Alternative Support
- `ARM_5_PREDICATE_CONTRACT_FLAT` correctly adjudicates transitions (Layer A: $100.0\%$) and maintains flawless premise states (Layer B: $100.0\%$), but its flat dependency model suffers **$100.0\%$ conditional revision autoimmunity** ($72/72$ cases, $36.0\%$ global incidence) when one unshared alternative premise is updated.
- Flat dependency tracking fails in 100% of the 72 designated alternative-support supersession cells, which comprise 36% of the balanced 200-case factorial.

### 4. GENE Epistemic Kernel Achieves Full 3-Layer Optimality
- `ARM_6_GENE_KERNEL` unites **Contract-Guided Adjudication** with **Bitemporal Antichain Support Algebra** ($\mathcal{S}_t \to \mathcal{S}_{L,t}$), delivering **$100.0\%$ Transition Fidelity, $100.0\%$ Premise State Fidelity, $100.0\%$ Support Fidelity, and $100.0\%$ Entitlement Accuracy** across all 200 cases.
