# GENE Exploration Round 5 — Stage 5A Results Report
### *Entitlement Under Change: Loss of Alternative-Support Structure Induces Revision Error*

**Execution Date:** 2026-08-20  
**Evidence Class:** `deterministic_zero_live_llm`  
**Execution Freeze Git Commit:** `HEAD`  
**Total Evaluated Scenarios:** **248 cases** (184 local $5A_1$ + 64 DAG $5A_2$)  
**Case Ledger:** `data/exploration_round5_stage5a_cases.jsonl` (`SHA256: 19ca50e07f970c221e15f151529ffcd6ae03b08e7a44e4666f9485a44dd81906`)  
**Summary JSON:** `data/exploration_round5_stage5a_summary.json` (`SHA256: 568698dac17b1b879d55780c56c3c8d7cd6b028f71cd3fad265bf10708e98f15`)  

---

## 1. Executive Summary & Core Theoretical Findings

Stage 5A characterized the mathematical boundary conditions of persistent memory revision. It systematically proved that **flattening multiple alternative minimal support environments ($\\mathcal{S}_F(c)$) into lossy dependency representations causes massive epistemic autoimmunity (false retractions)** under partial premise invalidations.

```
                  STAGE 5A LOCAL REVISION SCORECARD (N = 184 CASES)
                  
┌──────────────────────────────┬──────────────┬──────────────────┬─────────────────────────────┐
│ Revision Policy              │ Accuracy     │ False Retracts   │ Autoimmunity on Entitled    │
├──────────────────────────────┼──────────────┼──────────────────┼─────────────────────────────┤
│ Reference Support-First S(c) │ 100.0%       │ 0 / 60 (0.0%)    │ 0.0% (Zero Autoimmunity)    │
│ Single Reported Witness (AB) │ 83.7%        │ 30  / 60       │ 50.0% (Undercomplete)       │
│ Flat Union (ABDE)            │ 71.7%        │ 52  / 60       │ 86.7% (Overinclusive)         │
│ Bloated Union (+Distractor)  │ 71.7%        │ 52  / 60       │ 86.7% (Bloat-Amplified)      │
│ Lineage Quarantine (Ancestry)│ 71.7%        │ 52  / 60       │ 86.7% (Coarse Quarantine)   │
└──────────────────────────────┴──────────────┴──────────────────┴─────────────────────────────┘
```

---

## 2. The Formal Theorem: Inadequacy of Flat Conjunctive Dependencies

For any claim $c$ with multiple distinct minimal support environments $|\\mathcal{S}(c)| \\ge 2$, the Boolean entitlement function:
$$\\text{Ent}^*(c, I) = \\bigvee_{i=1}^k \\mathbf{1}[S_i \\cap I = \\emptyset]$$
**cannot in general be represented by any single flat conjunctive set** $\\mathbf{1}[R \\cap I = \\emptyset]$.

Stage 5A demonstrates two distinct failure regimes:
1. **Undercomplete Representation Failure (Single Witness $R = S_1$):**
   - When an alternative path $S_2$ remains valid but an assumption in $S_1$ is invalidated ($I \\cap S_1 \\ne \\emptyset, I \\cap S_2 = \\emptyset$), the single witness policy falsely kills $c$.
   - **Autoimmunity Rate:** **50.0%**.
2. **Overinclusive Representation Failure (Flat Union $R = \\bigcup S_i$):**
   - When any single assumption in any path is invalidated, the union policy falsely treats the loss of one path as the death of the entire belief.
   - **Autoimmunity Rate:** **86.7%** (86.7% when explanatory distractors $E_S > 0$ are present).

---

## 3. Sub-Assay 5A_1: Tripartite State Transitions & Resilience Degradation

Across the 184 factorial local test cases:
- **`UNCHANGED`:** **8 cases** (No assumption in any support environment was hit; $\\kappa' = \\kappa$).
- **`DEGRADED`:** **52 cases** (At least one support environment survived, but resilience degraded; $\\emptyset \\subset \\mathcal{S}' \\subset \\mathcal{S}, \\kappa' < \\kappa$).
- **`RETRACTED`:** **124 cases** (All support environments broken; $\\mathcal{S}' = \\emptyset, \\kappa' = 0$).

> [!IMPORTANT]
> **Dynamic Resilience Tracking ($\kappa(c) \\to \\kappa'(c)$):** In all 52 degraded cases, the support-first runtime correctly retained the active belief while lowering its epistemic cut set size ($\kappa: 2 \\to 1$). This bridges non-destructive revision directly to **Action Proportionality (Pillar 5)**: the belief survives in working memory, but its authority to execute irreversible external actions is automatically throttled.

---

## 4. Sub-Assay 5A_2: Multi-Tier DAG Cascades ($G_0 \\to G_1 \\to G_2$)

Evaluating the 3-tier recombinant diamond DAG across all $2^6 = 64$ root invalidation subsets:

```
                  DAG CASCADE IMPACT DISTRIBUTION (64 SUBSETS)
                  
┌────────────────────────┬────────────────┬──────────────────────┬──────────────────────┐
│ Node ID (Level)        │ UNAFFECTED     │ METADATA_UPDATE_ONLY │ RETRACTION_REQUIRED  │
├────────────────────────┼────────────────┼──────────────────────┼──────────────────────┤
│ M1 (Tier G1 Lead)      │ 4                          │ 24                                   │ 36                                   │
│ FinalGoal (Tier G2 Exec│ 1                          │ 15                                   │ 48                                   │
└────────────────────────┴────────────────┴──────────────────────┴──────────────────────┘
```

### Key Cascade Finding:
Root-expanded support derivation ($\\mathcal{S}_{\\text{root}}(G_2)$) prevents the **stale-descendant illusion**: downstream goals survive if and only if valid root-level paths connect through surviving intermediate lemmas, eliminating both false retractions and stale zombie derivations.

---

## 5. Artifact & Provenance Record

- **Case Ledger (JSONL):** `data/exploration_round5_stage5a_cases.jsonl` (`SHA256: 19ca50e07f970c221e15f151529ffcd6ae03b08e7a44e4666f9485a44dd81906`)
- **Summary Statistics:** `data/exploration_round5_stage5a_summary.json` (`SHA256: 568698dac17b1b879d55780c56c3c8d7cd6b028f71cd3fad265bf10708e98f15`)
- **Unit Tests:** `tests/explore_round5/test_revision_engine.py` (5/5 passing)
- **Zero Live LLM Compute:** Deterministic mathematical characterization.
