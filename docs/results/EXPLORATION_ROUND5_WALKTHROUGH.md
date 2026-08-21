# GENE Exploration Round 5 — Comprehensive Walkthrough (Stages 5A & 5B)
### *Entitlement Under Change: Support-First Epistemic Revision & Action Governance*

## 1. Executive Summary & Foundational Moonshot Progress

Exploration Round 5 establishes the mathematical and architectural bridge between **minimal entitling support $\mathcal{S}(c)$** and **epistemic maintenance under change**:
- **Stage 5A (Revision Precision):** Mathematically proved that flattening alternative support into lossy conjunctive dependencies causes **100% false retractions on damaged-but-still-entitled states (104/104)**.
- **Stage 5B (Action Governance):** Characterized the **Hierarchy of Epistemic Incompleteness** across 7 formal axioms, proving that binary entitlement, cut-set $\kappa$, tuple $\rho=(|S|, \kappa)$, and global root counts all suffer lossy collisions. Minimal governance requires the **lineage-projected support hypergraph $\mathcal{S}_L(c)$** and root resilience $\rho_L(c)$.

---

## 2. Stage 5A Verified Results: Revision Precision Scorecard

```
                  STAGE 5A LOCAL REVISION SCORECARD (N = 368 CASES)
                  
┌──────────────────────────────┬──────────────┬──────────────────┬─────────────────────────────┬───────────────────────────┐
│ Revision Policy              │ Accuracy     │ False Retracts   │ Autoimmunity on Degraded    │ Autoimmunity on Entitled  │
├──────────────────────────────┼──────────────┼──────────────────┼─────────────────────────────┼───────────────────────────┤
│ Reference Support-First S(c) │ 100.0%       │ 0 / 120 (0.0%)   │ 0.0% (0 / 104)              │ 0.0% (0 / 120)            │
│ Single Reported Witness (AB) │ 83.7%        │ 60  / 120        │ 57.7% (60 / 104)            │ 50.0% (60 / 120)          │
│ Flat Union (ABDE)            │ 71.7%        │ 104 / 120        │ 100.0% (104 / 104)          │ 86.7% (104 / 120)         │
│ Bloated Union (+Distractor)  │ 69.6%        │ 112 / 120        │ 100.0% (104 / 104)          │ 93.3% (112 / 120)*        │
│ Lineage Quarantine (Ancestry)│ 71.7%        │ 104 / 120        │ 100.0% (104 / 104)          │ 86.7% (104 / 120)         │
└──────────────────────────────┴──────────────┴──────────────────┴─────────────────────────────┴───────────────────────────┘
```
*\* Note: Bloated Union falsely retracts 100% of degraded cases (104/104) plus 8 incremental false retractions on previously UNCHANGED states when distractor F is invalidated, yielding 112/120 (93.3%) total autoimmunity.*

---

## 3. Stage 5B Verified Results: Action Governance & Axiomatic Scorecard

```
                        AXIOMATIC COMPLIANCE SCORECARD (7 FORMAL INVARIANTS)
                        
┌──────────────────────────────────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────┐
│ Governance Policy                │ Ax 1 │ Ax 2 │ Ax 3 │ Ax 4 │ Ax 5 │ Ax 6 │ Ax 7 │ Score │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼───────┤
│ P_binary (Binary Entitlement)    │ PASS │ PASS │ FAIL │ PASS │ PASS │ FAIL │ PASS │ 5/7   │
│ P_kappa (Scalar Cut-Set)         │ PASS │ PASS │ FAIL │ PASS │ PASS │ FAIL │ PASS │ 5/7   │
│ P_rho (Tuple Resilience)         │ PASS │ PASS │ PASS │ PASS │ PASS │ FAIL │ PASS │ 6/7   │
│ P_lineage (Lineage Projected S_L) │ PASS │ PASS │ PASS │ PASS │ PASS │ PASS │ PASS │ 7/7   │
└──────────────────────────────────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴───────┘
```

### The Hierarchy of Lossy Reductions:
1. **Binary Entitlement** collapses all degrees of entitlement to $\{0, 1\}$, failing degradation sensitivity (Axiom 3).
2. **$\kappa$ (Cut-Set Resilience)** collapses path redundancy: in $(2,1) \to (1,1)$, path redundancy is lost while $\kappa$ stays $1$.
3. **$\rho = (|S|, \kappa)$ (Tuple Resilience)** collapses ancestral root incidence: two paths sharing a single root have identical $\rho=(2, 2)$ to two paths derived from independent roots.
4. **$|\text{Roots}|$ (Global Root Count / Ratio)** collapses root-to-path incidence: in shared origin ancestry ($A,D \leftarrow R_1; B,E \leftarrow R_2$), global root counting sees 2 roots and 2 paths, but $\mathcal{S}_L = \{\{R_1, R_2\}\}$ has zero independent alternatives ($\kappa_L = 1$).
5. **Lineage-Projected Hypergraph $\mathcal{S}_L(c)$**: Resolves all 4 collisions and satisfies all 7 formal axioms.

---

## 4. Repository Artifacts & Verified Provenance

- **Git Freeze Tags:**
  - Stage 5A: [`round5-stage5a-freeze-v2`](https://github.com/admiralorbiter/gene/tree/round5-stage5a-freeze-v2) (`aff1baa`)
  - Stage 5B: [`round5-stage5b-freeze-v2`](https://github.com/admiralorbiter/gene/tree/round5-stage5b-freeze-v2)
- **Results Reports:**
  - [`docs/results/EXPLORATION_ROUND5_STAGE5A_REPORT.md`](EXPLORATION_ROUND5_STAGE5A_REPORT.md)
  - [`docs/results/EXPLORATION_ROUND5_STAGE5B_REPORT.md`](EXPLORATION_ROUND5_STAGE5B_REPORT.md)
- **Case Ledgers & Summary JSONs:**
  - Stage 5A Ledger: `data/exploration_round5_stage5a_cases.jsonl` (`SHA256: 1499305d197cf53ad624fc65a6626a0d5fc9ea87993184583930ce952692548e`)
  - Stage 5A Summary: `data/exploration_round5_stage5a_summary.json` (`SHA256: dc39becc57dfed03ee772095d75a1fd7342f84342745428a1cedb7b7231e56eb`)
  - Stage 5B Ledger: `data/exploration_round5_stage5b_cases.jsonl` (`SHA256: 1ada9c3b29eeb4fa32f6440bec1cfa31622fd4438f1326c806822dea056bf9da`)
  - Stage 5B Summary: `data/exploration_round5_stage5b_summary.json` (`SHA256: 871b8c17e0800b368b902e4a0982bfcd7766238febf08f2b745d1cf50b873145`)
- **Unit Tests:** **159 / 159 passing in 26.83s** (`pytest`).
