# Exploration Round 6 Stage 6B Benchmark Report: Contract-Guided State Adjudication

**Assay Name**: Contract-Guided State Adjudication & Predicate Transition Semantics (Stage 6B)  
**Dataset Artifact**: [`../../data/exploration_round6_stage6b_cases.jsonl`](../../data/exploration_round6_stage6b_cases.jsonl) ($N=200$ cases)  
**Summary Artifact**: [`../../data/exploration_round6_stage6b_results_summary.json`](../../data/exploration_round6_stage6b_results_summary.json)  
**Temporal Sidecar Artifact**: [`../../data/exploration_round6_stage6b1_temporal_summary.json`](../../data/exploration_round6_stage6b1_temporal_summary.json) ($N=12$ coordinates)  
**Execution Timestamp**: `2026-08-21T04:51:22Z`  

---

## Executive Summary

Stage 6B evaluates how memory systems adjudicate incoming factual observations without explicit transition labels (`ASSERT`, `SUPERSEDES`, `RETRACT`). 

Across a factorial matrix of **200 test cases** ($4 \text{ PredicateModes} \times 5 \text{ UpdatePatterns} \times 2 \text{ SourceRelations} \times 5 \text{ SupportTopologies}$), we compare 6 **fully executed memory policy implementations** across three distinct layers:
1. **Layer A (Adjudication Transition Fidelity)**: Does the policy emit the exact formal state transitions $(\text{type}, \text{target}, \text{secondary}, t_{v,\text{start}}, t_{v,\text{end}})$?
2. **Layer B (Premise State Fidelity)**: Does the policy maintain the correct active premise universe $\mathcal{F}(t_v \mid t_k)$?
3. **Layer C (Downstream Epistemic Maintenance)**: Does the policy correctly maintain downstream minimal support $\mathcal{S}_t(c)$ and entitlement $\text{Ent}(c)$?

```
+===================================================================================================================================================================+
|                                              STAGE 6B FACTORIAL BENCHMARK COMPARATIVE RESULTS (N=200)                                                             |
+================================+=============+=============+========================+========================+========================+==============+=========+
| Memory Architecture Arm        | Layer A Tr %| Layer B St %| F+ (False Entitled)    | F- (Lost Entitled)     | Autoimmune (Pure Rev)  | Supp Fidelity| Ent Acc |
+================================+=============+=============+========================+========================+========================+==============+=========+
| `ARM_1_APPEND_ONLY` | 55.0% | 40.0% | 100.0% (48/48) | 0.0% (0/152) | 0 / 72 (0.0%) | N/A | **76.0%** |
| `ARM_2_KNOWLEDGE_TIME_LWW` | 55.0% | 55.0% | 0.0% (0/48) | 31.6% (48/152) | 0 / 72 (0.0%) | N/A | **76.0%** |
| `ARM_3_VALID_TIME_LWW` | 55.0% | 55.0% | 0.0% (0/48) | 31.6% (48/152) | 0 / 72 (0.0%) | N/A | **76.0%** |
| `ARM_4_BITEMPORAL_LATEST` | 55.0% | 55.0% | 0.0% (0/48) | 31.6% (48/152) | 0 / 72 (0.0%) | N/A | **76.0%** |
| `ARM_5_PREDICATE_CONTRACT_FLAT` | 100.0% | 100.0% | 0.0% (0/48) | 47.4% (72/152) | 72 / 72 (100.0%) | N/A | **64.0%** |
| `ARM_6_GENE_KERNEL` | 100.0% | 100.0% | 0.0% (0/48) | 0.0% (0/152) | 0 / 72 (0.0%) | 100.0% | **100.0%** |
+================================+=============+=============+========================+========================+========================+==============+=========+
```

---

## Key Scientific Discoveries & 3-Layer Decomposition

### 1. State Correctness Does Not Imply Epistemic Correctness ($\text{State} \not\Rightarrow \text{Epistemic}$)
A central discovery of Stage 6B is that **Arm 5 achieves 100.0% Layer A transition fidelity and 100.0% Layer B premise state fidelity**, yet produces **worse end-to-end entitlement accuracy ($64.0\%$)** than naive LWW stores ($76.0\%$).
- While LWW systems sometimes arrive at the right entitlement answer for the wrong reason (retaining uninvalidated alternative branches while destroying historical states), Arm 5 maintains a flawless world-state representation and then **systematically destroys still-entitled conclusions** ($72/72$ failures, $100.0\%$ revision autoimmunity).

### 2. Decomposition of the 72 Revision Autoimmunity Failures ($\text{SemanticClaim} \ne \text{OccurrenceNode}$)
The 72 false retractions suffered by flat dependency tracking decompose into two distinct failure mechanisms:
1. **Alternative-Path Derivation Survival ($32$ cases)**: When an unshared premise in path $P_1$ is superseded, but an independent alternative derivation path $P_2$ remains fully valid.
2. **Occurrence Substitution / Recurrence Survival ($40$ cases)**: When an expired occurrence node $\text{occ}_{\text{init}}$ is replaced by a recurrent occurrence $\text{occ}_{\text{in}}$ of the *identical semantic proposition*. Because flat dependency graphs track concrete occurrence IDs rather than minimal support antichains $\mathcal{S}_t(c)$, the replacement of the occurrence triggers an automatic false retraction.

### 3. Layer A: Temporal Order Cannot Infer Transition Semantics
- Pure temporal stores (`ARM_2_KNOWLEDGE_TIME_LWW`, `ARM_3_VALID_TIME_LWW`, `ARM_4_BITEMPORAL_LATEST`) score **$55.0\%$** because timestamps alone cannot distinguish a replacement from an additive accumulation or a contemporaneous dispute, and lack interval boundaries.
- The shared `PredicateContractAdjudicator` achieves **$100.0\%$ exact semantic transition fidelity**, conforming exactly to the transition ontology.

### 4. Stage 6B.1 Temporal Sidecar: Separating KT-LWW, VT-LWW, and Bitemporality
In the Stage 6B.1 multi-update micro-assay ($N=12$ evaluation coordinates with crossed $t_v$ and $t_k$ arrival order):
- **`Knowledge-Time LWW`**: **$33.3\%$ Accuracy ($4/12$)** (fails all retroactive backfill queries).
- **`Valid-Time LWW`**: **$75.0\%$ Accuracy ($9/12$)** (fails valid-time gap and historical queries).
- **`Bitemporal Engine`**: **$100.0\%$ Accuracy ($12/12$)** (perfectly reconstructs valid-time state across knowledge-time progression).

### 5. GENE Epistemic Kernel Dual-Layer Optimality
`ARM_6_GENE_KERNEL` unites **Contract-Guided Adjudication** with **Bitemporal Antichain Support Algebra** ($\mathcal{S}_t \to \mathcal{S}_{L,t}$), delivering **$100.0\%$ Transition Fidelity, $100.0\%$ Premise State Fidelity, $100.0\%$ Support Fidelity, and $100.0\%$ Entitlement Accuracy** across all 200 cases.
