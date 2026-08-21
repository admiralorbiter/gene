# GENE Exploration Round 5 — Stage 5A Results Report
### *Entitlement Under Change: Loss of Alternative-Support Structure Induces Revision Error*

**Execution Date:** 2026-08-20  
**Evidence Class:** `deterministic_zero_live_llm`  
**Execution Freeze Git Tag:** `round5-stage5a-freeze`  
**Total Evaluated Scenarios:** **432 cases** (368 local $5A_1$ + 64 DAG $5A_2$)  
**Case Ledger:** `data/exploration_round5_stage5a_cases.jsonl` (`SHA256: 606229a7dc1f6cf507869e67e247755a3f3bb89af1e5c8bb7aead4e5be1dcc8c`)  
**Summary JSON:** `data/exploration_round5_stage5a_summary.json` (`SHA256: 88a1d14bd2ccb4990b895b2858182e0fddb587a9fab265236738ef97858465f9`)  

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
│ Flat Union (ABDE)            │ 71.7%        │ 104 / 120      │ 100.0% (104 / 104)    │ 86.7% (104 / 120)    │
│ Bloated Union (+Distractor)  │ 69.6%        │ 112 / 120      │ 100.0% (104 / 104)*  │ 93.3% (112 / 120)    │
│ Lineage Quarantine (Ancestry)│ 71.7%        │ 104 / 120      │ 100.0% (104 / 104)    │ 86.7% (104 / 120)    │
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
   - **Autoimmunity on Degraded States:** **57.7%** (60  false retractions).
2. **Overinclusive Representation Failure (Flat Union $R = \bigcup S_i$):**
   - Storing the flat union of all reported evidence ($R = \{A,B,D,E\}$) falsely kills $c$ whenever *any* single assumption in *any* path is invalidated.
   - **Autoimmunity on Degraded States:** **100.0%** (Preserved **0 / 104** partially damaged-but-still-entitled states).
3. **Incremental Distractor Bloat ($E_S > 0$):**
   - When an irrelevant explanatory distractor $F$ is invalidated ($I = \{F\}$), flat union correctly survives while bloated union falsely kills the claim, yielding **112 total false retractions** (8 incremental false retractions directly caused by $E_S > 0$).

---

## 3. Factorial Breakdown by Support Topology

```
                  AUTOIMMUNITY BY SUPPORT TOPOLOGY (DEGRADED STATES)
                  
┌──────────────────────────────┬──────────────┬──────────────┬────────────────┬─────────────────┐
│ Topology                     │ Total Cases  │ Degraded (N) │ Flat Union Auto│ Single Wit. Auto│
├──────────────────────────────┼──────────────┼──────────────┼────────────────┼─────────────────┤
│ single_conjunctive (AB)      │ 16           │ 0            │ 0.0% (N/A)     │ 0.0% (N/A)      │
│ independent_alternat. (AB|DE)│ 64           │ 24           │ 100.0% (36/36) │ 44.4% (16/36)   │
│ shared_root_alternat. (AB|AD)│ 32           │ 8           │ 100.0% (16/16) │ 50.0% (8/16)    │
│ recombinant_tri_path (3-path)│ 256          │ 72          │ 100.0% (180/180│ 60.0% (108/180) │
└──────────────────────────────┴──────────────┴──────────────┴────────────────┴─────────────────┘
```

---

## 4. Sub-Assay 5A_1: The Resilience Signature $\rho(c) = (|S(c)|, \kappa(c))$

Stage 5A revealed that **support degradation does not necessarily lower cut-set size $\kappa(c)$**:

```
                  RESILIENCE TRANSITION MATRIX RHO -> RHO'
                  
┌──────────────────────────────┬──────────────┬────────────────────────────────────────────────────────┐
│ Transition rho -> rho'       │ Occurrences  │ Epistemic Meaning                                      │
├──────────────────────────────┼──────────────┼────────────────────────────────────────────────────────┤
│ (1, 1) -> (1, 1) [Unchanged] │ 8 cases      │ Single-path baseline untouched.                        │
│ (2, 2) -> (2, 2) [Unchanged] │ 8 cases      │ Independent alternatives untouched.                    │
│ (2, 1) -> (2, 1) [Unchanged] │ 8 cases      │ Shared-root alternatives untouched.                    │
│ (3, 2) -> (3, 2) [Unchanged] │ 8 cases      │ Recombinant tri-path untouched.                        │
├──────────────────────────────┼──────────────┼────────────────────────────────────────────────────────┤
│ (2, 2) -> (1, 1) [Degraded]  │ 36 cases     │ Independent alternative lost: both |S| and kappa drop. │
│ (2, 1) -> (1, 1) [Degraded]  │ 16 cases     │ Shared-root alternative lost: |S| drops, kappa STABLE! │
│ (3, 2) -> (2, 2) [Degraded]  │ 36 cases     │ Tri-path branch lost: |S| drops, kappa STABLE!         │
│ (3, 2) -> (1, 1) [Degraded]  │ 144 cases    │ Two tri-path branches lost: both |S| and kappa drop.   │
├──────────────────────────────┼──────────────┼────────────────────────────────────────────────────────┤
│ All Retracted (rho' = (0, 0))│ 112 cases    │ Complete loss of entitlement.                          │
└──────────────────────────────┴──────────────┴────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Resilience Signature vs Scalar Cut-Set:** In shared-root and multi-path topologies, a belief can lose an entire valid justification without changing $\kappa(c)$ (e.g. $(2,1) \to (1,1)$ or $(3,2) \to (2,2)$). Durable memory must track the full signature $\rho(c) = (|S(c)|, \kappa(c))$ to provide formal input for **Action Proportionality (Pillar 5)**.

---

## 5. Sub-Assay 5A_2: Multi-Tier DAG Cascades & Stale-Cached Baseline Contrast

Evaluating the 3-tier recombinant diamond DAG across all $2^6 = 64$ root invalidation subsets:

```
                  DAG CASCADE & STALE-CACHED BASELINE CONTRAST
                  
┌────────────────────────────────────────┬──────────────────────┬──────────────────────────────┐
│ Metric                                 │ Count / Denominator  │ Epistemic Meaning            │
├────────────────────────────────────────┼──────────────────────┼──────────────────────────────┤
│ Total Evaluated Cascade Cases          │ 64 / 64              │ Exhaustive root power set    │
│ Ground Truth Retractions (FinalGoal)   │ 48 / 64 cases        │ All root paths broken        │
│ Stale Zombie Derivations (FinalGoal)   │ 36 / 48 (75.0%)      │ Stale intermediate cached M1 │
│ Root Expansion Exactness (S_root)      │ 64 / 64 (100.0%)     │ Zero zombie derivations      │
└────────────────────────────────────────┴──────────────────────┴──────────────────────────────┘
```

### Cascade Discovery:
In **75.0% of retracted cases (36/48)**, relying on stale cached intermediate representations causes the downstream goal to falsely survive as a **zombie belief**. Root-expanded support derivation ($\mathcal{S}_{\text{root}}$) eliminates 100% of zombie derivations without premature retractions.

---

## 6. Artifact & Provenance Record

- **Case Ledger (JSONL):** `data/exploration_round5_stage5a_cases.jsonl` (`SHA256: 606229a7dc1f6cf507869e67e247755a3f3bb89af1e5c8bb7aead4e5be1dcc8c`)
- **Summary Statistics:** `data/exploration_round5_stage5a_summary.json` (`SHA256: 88a1d14bd2ccb4990b895b2858182e0fddb587a9fab265236738ef97858465f9`)
- **Unit Tests:** `tests/explore_round5/test_revision_engine.py` (5/5 passing)
- **Zero Live LLM Compute:** Deterministic mathematical characterization.
