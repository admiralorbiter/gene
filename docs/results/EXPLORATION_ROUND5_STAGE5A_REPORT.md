# GENE Exploration Round 5 — Stage 5A Results Report
### *Entitlement Under Change: Loss of Alternative-Support Structure Induces Revision Error*

**Execution Date:** 2026-08-20  
**Evidence Class:** `deterministic_zero_live_llm`  
**Execution Freeze Git Tag:** `round5-stage5a-freeze-v2`  
**Total Evaluated Scenarios:** **432 cases** (368 local $5A_1$ + 64 DAG $5A_2$)  
**Case Ledger:** `data/exploration_round5_stage5a_cases.jsonl` (`SHA256: 1499305d197cf53ad624fc65a6626a0d5fc9ea87993184583930ce952692548e`)  
**Summary JSON:** `data/exploration_round5_stage5a_summary.json` (`SHA256: dc39becc57dfed03ee772095d75a1fd7342f84342745428a1cedb7b7231e56eb`)  

---

## 1. Executive Summary & Core Theoretical Findings

Stage 5A characterized the mathematical failure regions of lossy dependency representations under a frozen minimal-support entitlement semantics ($\text{Ent}^*(c, I)$). It systematically proved that **loss of alternative-support algebra causes massive epistemic autoimmunity (false retractions)** under partial premise invalidations.

```
                  STAGE 5A LOCAL REVISION SCORECARD (N = 368 CASES)
                  
┌──────────────────────────────┬──────────────┬──────────────────┬─────────────────────────────┬───────────────────────────┐
│ Revision Policy              │ Accuracy     │ False Retracts   │ Autoimmunity on Degraded    │ Autoimmunity on Entitled  │
├──────────────────────────────┼──────────────┼──────────────────┼─────────────────────────────┼───────────────────────────┤
│ Reference Support-First S(c) │ 100.0%       │ 0 / 120 (0.0%)    │ 0.0% (0 / 104)           │ 0.0% (0 / 120)         │
│ Single Reported Witness (AB) │ 83.7%        │ 60  / 120      │ 57.7% (60 / 104)     │ 50.0% (60  / 120)    │
│ Flat Union (ABDE)            │ 71.7%        │ 104 / 120      │ 100.0% (104 / 104)   │ 86.7% (104 / 120)    │
│ Bloated Union (+Distractor)  │ 69.6%        │ 112 / 120      │ 100.0% (104 / 104)   │ 93.3% (112 / 120)*   │
│ Lineage Quarantine (Ancestry)│ 71.7%        │ 104 / 120      │ 100.0% (104 / 104)   │ 86.7% (104 / 120)    │
└──────────────────────────────┴──────────────┴──────────────────┴─────────────────────────────┴───────────────────────────┘
```
*\* Note: Bloated Union falsely retracts 100% of degraded cases (104/104) plus 8 incremental false retractions on previously UNCHANGED states when distractor F is invalidated, yielding 112/120 (93.3%) total autoimmunity.*

---

## 2. The Formal Theorem: Inadequacy of Flat Conjunctive Dependencies

For any claim $c$ with multiple distinct incomparable minimal support environments $|\mathcal{S}(c)| \ge 2$, the Boolean entitlement function:
$$\text{Ent}^*(c, I) = \bigvee_{i=1}^k \mathbf{1}[S_i \cap I = \emptyset]$$
**cannot in general be represented by any single flat conjunctive set** $\mathbf{1}[R \cap I = \emptyset]$.

### Two Distinct Failure Regimes:
1. **Undercomplete Representation Failure (Single Witness $R = S_1$):**
   - Storing a single valid neural explanation ($R = \{A,B\}$) falsely kills $c$ upon $\text{do}(A=0)$ even though alternative support $DE$ remains valid.
   - **Autoimmunity on Degraded States:** **57.7%** (60 / 104 false retractions).
2. **Overinclusive Representation Failure (Flat Union $R = \bigcup S_i$):**
   - Storing the flat union of all reported evidence ($R = \{A,B,D,E\}$) falsely kills $c$ whenever *any* single assumption in *any* path is invalidated.
   - **Autoimmunity on Degraded States:** **100.0%** (Preserved **0 / 104** partially damaged-but-still-entitled states).
3. **Incremental Distractor Bloat ($E_S > 0$):**
   - When an irrelevant explanatory distractor $F$ is invalidated ($I = \{F\}$), flat union correctly survives while bloated union falsely kills the claim, yielding **112 total false retractions** (8 incremental false retractions directly caused by $E_S > 0$).

---

## 3. Factorial Breakdown by Support Topology

```
                  AUTOIMMUNITY BY SUPPORT TOPOLOGY (DEGRADED STATES)
                  
┌────────────────────────────────┬──────────────┬──────────────┬────────────────────┬────────────────────┐
│ Topology                       │ Total Cases  │ Degraded (N) │ Flat Union Auto    │ Single Wit. Auto   │
├────────────────────────────────┼──────────────┼──────────────┼────────────────────┼────────────────────┤
│ single_conjunctive             │ 16           │ 0            │ 0.0% (N/A)         │ 0.0% (N/A)         │
│ independent_alternatives       │ 64           │ 24           │ 100.0% (24/24)     │ 50.0% (12/24)      │
│ shared_root_alternatives       │ 32           │ 8            │ 100.0% (8/8)       │ 50.0% (4/8)        │
│ recombinant_tri_path           │ 256          │ 72           │ 100.0% (72/72)     │ 61.1% (44/72)      │
└────────────────────────────────┴──────────────┴──────────────┴────────────────────┴────────────────────┘
```

---

## 4. Sub-Assay 5A_1: The Resilience Signature $\rho(c) = (|S(c)|, \kappa(c))$

Stage 5A proved that **support degradation does not necessarily lower cut-set size $\kappa(c)$**:

```
                  RESILIENCE TRANSITION MATRIX RHO -> RHO'
                  
┌────────────────────────────────┬──────────────┬────────────────────────────────────────────────────────────────┐
│ Transition rho -> rho'         │ Occurrences  │ Epistemic Meaning                                              │
├────────────────────────────────┼──────────────┼────────────────────────────────────────────────────────────────┤
│ (1, 1)->(0, 0)                 │ 12           │ Complete loss of entitlement (all support paths broken).       │
│ (1, 1)->(1, 1)                 │ 4            │ Baseline support untouched (UNCHANGED).                        │
│ (2, 1)->(0, 0)                 │ 20           │ Complete loss of entitlement (all support paths broken).       │
│ (2, 1)->(1, 1)                 │ 8            │ Shared-root alternative lost: |S| drops (2->1), kappa STABLE (1->1). │
│ (2, 1)->(2, 1)                 │ 4            │ Baseline support untouched (UNCHANGED).                        │
│ (2, 2)->(0, 0)                 │ 36           │ Complete loss of entitlement (all support paths broken).       │
│ (2, 2)->(1, 1)                 │ 24           │ Independent alternative lost: both |S| and kappa drop.         │
│ (2, 2)->(2, 2)                 │ 4            │ Baseline support untouched (UNCHANGED).                        │
│ (3, 2)->(0, 0)                 │ 180          │ Complete loss of entitlement (all support paths broken).       │
│ (3, 2)->(1, 1)                 │ 60           │ Two tri-path branches lost: both |S| and kappa drop.           │
│ (3, 2)->(2, 1)                 │ 12           │ Tri-path branch lost: |S| drops (3->2), kappa drops (2->1) due to shared premise D. │
│ (3, 2)->(3, 2)                 │ 4            │ Baseline support untouched (UNCHANGED).                        │
└────────────────────────────────┴──────────────┴────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Resilience Signature vs Scalar Cut-Set:** In the shared-root topology ($\mathcal{S}(C) = \{\{A,B\}, \{A,D\}\}$), invalidating $B$ causes a valid alternative justification to be lost while $\kappa$ remains constant ($|S|$ drops $2 \to 1$, $\kappa = 1 \to 1$, in 8 cases). Scalar cut-set $\kappa(c)$ is insufficient to capture epistemic degradation; the epistemic state requires the full signature $\rho(c) = (|S(c)|, \kappa(c))$.

---

## 5. Sub-Assay 5A_2: Multi-Tier DAG Cascades & Staleness Factorial

Evaluating the 3-tier recombinant diamond DAG across all $2^6 = 64$ root invalidation subsets and intermediate cache staleness regimes:

```
                  DAG CASCADE STALENESS FACTORIAL (64 SUBSETS)
                  
┌───────────────────────────┬────────────────────────────────┬──────────────────────────────┐
│ Stale Cache Configuration │ Stale Zombie Retractions (FG)  │ Exact Reference Agreement    │
├───────────────────────────┼────────────────────────────────┼──────────────────────────────┤
│ None (Exact Reference)    │ 0   / 48 (0.0%) │ 64  / 64 (100.0%) │
│ M1                        │ 12  / 48 (25.0%) │ 52  / 64 (81.2%) │
│ M2                        │ 12  / 48 (25.0%) │ 52  / 64 (81.2%) │
│ M1, M2                    │ 48  / 48 (100.0%) │ 16  / 64 (25.0%) │
└───────────────────────────┴────────────────────────────────┴──────────────────────────────┘
```

### Cascade Discovery:
When intermediate lemmas become stale, downstream goals falsely survive as **zombie beliefs** (up to **100% of retracted cases** when both intermediates are stale). Root-expanded support derivation ($\mathcal{S}_{\text{root}}$) eliminates 100% of zombie derivations without premature retractions.

---

## 6. Artifact & Provenance Record

- **Case Ledger (JSONL):** `data/exploration_round5_stage5a_cases.jsonl` (`SHA256: 1499305d197cf53ad624fc65a6626a0d5fc9ea87993184583930ce952692548e`)
- **Summary Statistics:** `data/exploration_round5_stage5a_summary.json` (`SHA256: dc39becc57dfed03ee772095d75a1fd7342f84342745428a1cedb7b7231e56eb`)
- **Unit Tests:** `tests/explore_round5/test_revision_engine.py` (8/8 passing)
- **Zero Live LLM Compute:** Deterministic mathematical characterization.
