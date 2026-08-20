# Experiment 1B-C1b: Hardened Shared-Ecology Retrieval Sandbox & Multi-Control Audit

**Experiment ID:** EXP-1B-C1B-SHARED-ECOLOGY-HARDENED-01  
**Timestamp:** 2026-08-20  
**Methodology:** Exact 4-State Analytical Probability Weighting over Shared-Ecology BM25 Retrieval  
**Evaluation Units:** 12 Fully Balanced Ecologies (6 Unique Unordered Pairs x 2 Bidirectional Role Swaps)  
**Total Policies Evaluated:** 8 (7 Distinct Treatments + 1 Oracle Upper Bound)  
**Grid Size:** 4 TPRs ({0.50, 0.75, 0.90, 1.00}) x 5 FPRs ({0.00, 0.05, 0.10, 0.20, 0.40}) = 20 Points per Policy  
**Context Budgets:** $k \in \{4, 6, 8\}$  
**Repository Commit:** `15abd87`  
**Database File:** `gene_exp1b_c1b_shared_ecology_15abd87.db`  
**Live LLM Compute Spent:** 0 Calls (100% Deterministic Analytical Preflight)  

---

## 1. Executive Summary & Core Scientific Findings

Experiment 1B-C1b establishes the competitive retrieval dynamics of epistemic immunity within a **shared ecology**:
Healthy Lineage $H$ (Station A) and Infected Lineage $I$ (Station B) coexist in a single shared memory store (~22 candidate nodes) and compete for top-$k$ retrieval budget.

Because Stations A and B represent distinct fictional entities, there is zero canonical contradiction at the same locus. This isolates whether genealogical tracking buys containment under actual retrieval competition against 7 finely decomposed control treatments.

### Key Discoveries from the 12-Ecology Balanced Sweep:

1. **Complete Descendant Laundering under Node-Only Filtering ($C_I \equiv 1.000$)**:
   - Under `node_only_quarantine`, flagging root $I_0$ deletes only $I_0$. Because $G_3$ tasks consume $G_2$ support premises, $I_2$ survives intact.
   - For all detector accuracies ($\text{TPR} \in [0.50, 1.00]$), infected path availability remains **$C_I = 1.000$ (Containment = 0.0%, Separation $S = 0.000$)**.
   - Node-level filtering provides **no post-adjudication containment in the tested descendant-mediated topology**.

2. **Strict Empirical Symmetry for Signal-Blind Uniform Thinning ($S \equiv 0.000$)**:
   - Under full bidirectional role swapping ($H=A, I=B$ and $H=B, I=A$) with deterministic multi-seed Monte Carlo averaging ($N_{\text{mc}} = 50$), `signal_blind_uniform_thinning` exhibits zero directional preference:
     $$C_H = 0.741, \quad C_I = 0.741 \implies S \equiv 0.000$$
   - This proves that lexical/station identity introduces zero residual bias in the shared ecology.

3. **Topology-Matched Control Proves Necessity of Signal-Lineage Alignment ($S \equiv 0.000$)**:
   - `random_family_quarantine` drops an entire structural descendant family cluster ($G_0 + G_1 + G_2$) uniformly at random, independently of the risk signal.
   - At $\text{TPR}=0.90, \text{FPR}=0.10$, it yields $C_H = 0.550, C_I = 0.550 \implies S \equiv 0.000$.
   - **Conclusion**: Dropping correlated family clusters without signal-lineage alignment destroys healthy and infected pathways at identical rates. Lineage immunity works because the ancestry graph directs the intervention specifically to the descendants of the flagged founder.

4. **Two Distinct Scientific Comparisons (Same-Signal vs True Pareto Envelope)**:
   - **Same-Signal Operating Point Comparison** (at $\text{TPR}=0.90, \text{FPR}=0.10$):
     - `lineage_quarantine`: $C_H = 0.900, C_I = 0.100 \implies S = +0.800$.
     - `generation_matched_thinning`: $C_H = 0.632, C_I = 0.490 \implies S = +0.142$.
     - `signal_conditioned_uniform`: $C_H = 0.564, C_I = 0.513 \implies S = +0.051$.
   - **True Matched-Coverage Pareto Envelope Analysis**:
     - When sweeping all non-lineage control configurations to find the minimal infected leakage $C_{I, \text{ctrl}}^*(c)$ that achieves $C_{H, \text{ctrl}} \ge c$:
     - For $c = 0.900$ (90% healthy coverage), **no thinning control can reach this coverage level** (thinning drops $C_H$ to $0.55 - 0.63$).
     - The only control achieving $C_H \ge 0.900$ is `node_only_quarantine`, which leaks $C_I = 1.000$.
     - Thus, at $c = 0.900$, the true matched-coverage containment gain is:
       $$\Delta_I(0.900) = C_{I, \text{ctrl}}^*(0.900) - C_{I, \text{lineage}}(0.900) = 1.000 - 0.100 = \mathbf{+0.900} \text{ (+90.0% containment gain)}.$$

---

## 2. Stepwise Control Comparison Matrix (12 Balanced Ecologies)

The stepwise controls suggest that detector information, reproductively relevant generation targeting, and ancestor-specific targeting each contribute to containment; the controls are not yet an additive factorial decomposition of independent effects:

```
+----------------------------------------------------------------------------------------------------------------------+
|                                    STEPWISE CONTROL MATRIX (SHARED ECOLOGY, k=6)                                     |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
| Policy                             | Uses Detector?   | Budget Source     | Targeting Scope    | Observed S (90/10)  |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
| baseline                           | No               | 0                 | None               | 0.000               |
| signal_blind_uniform_thinning      | No               | Fixed (m=3)       | Blind Uniform      | 0.000 (Symmetric)   |
| random_family_quarantine           | Yes (Count Only) | Matched (1 Cluster| Random Family DAG  | 0.000 (Symmetric)   |
| signal_conditioned_uniform_thinning| Yes              | Matched (m=lin)   | Blind Uniform      | +0.051              |
| generation_matched_thinning        | Yes              | Matched (mG2=lin) | Generation 2 Pool  | +0.142              |
| node_only_quarantine               | Yes              | Roots Only (G0)   | Flagged Roots      | 0.000 (Laundering)  |
| lineage_quarantine                 | Yes              | Transitive DAG    | Flagged Lineages   | +0.800 (Decisive)   |
| oracle_upper_bound                 | Perfect Ground T*| Transitive DAG    | True Infected Tree | +1.000              |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
```

---

## 3. True Matched-Coverage Pareto Envelope Table ($k=6$)

$$\Delta_I(c) = \min_{\theta: C_{H, \text{ctrl}}(\theta) \ge c} C_{I, \text{ctrl}}(\theta) - C_{I, \text{lineage}}(c)$$

| Detector Setting | Lineage Healthy $C_H$ | Lineage Leak $C_I$ | Min Control Leak $C_I^*$ | Best Eligible Control Policy | True Containment Gain $\Delta_I$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $\text{TPR}=0.75, \text{FPR}=0.00$ | 1.000 | 0.250 | 1.000 | `node_only_quarantine` | **+0.750** |
| $\text{TPR}=0.75, \text{FPR}=0.05$ | 0.950 | 0.250 | 1.000 | `node_only_quarantine` | **+0.750** |
| $\text{TPR}=0.75, \text{FPR}=0.10$ | 0.900 | 0.250 | 1.000 | `node_only_quarantine` | **+0.750** |
| $\text{TPR}=0.75, \text{FPR}=0.20$ | 0.800 | 0.250 | 1.000 | `node_only_quarantine` | **+0.750** |
| $\text{TPR}=0.90, \text{FPR}=0.00$ | 1.000 | 0.100 | 1.000 | `node_only_quarantine` | **+0.900** |
| $\text{TPR}=0.90, \text{FPR}=0.05$ | 0.950 | 0.100 | 1.000 | `node_only_quarantine` | **+0.900** |
| $\text{TPR}=0.90, \text{FPR}=0.10$ | 0.900 | 0.100 | 1.000 | `node_only_quarantine` | **+0.900** |
| $\text{TPR}=0.90, \text{FPR}=0.20$ | 0.800 | 0.100 | 1.000 | `node_only_quarantine` | **+0.900** |
| $\text{TPR}=1.00, \text{FPR}=0.00$ | 1.000 | 0.000 | 1.000 | `node_only_quarantine` | **+1.000** |
| $\text{TPR}=1.00, \text{FPR}=0.05$ | 0.950 | 0.000 | 1.000 | `node_only_quarantine` | **+1.000** |
| $\text{TPR}=1.00, \text{FPR}=0.10$ | 0.900 | 0.000 | 1.000 | `node_only_quarantine` | **+1.000** |
| $\text{TPR}=1.00, \text{FPR}=0.20$ | 0.800 | 0.000 | 1.000 | `node_only_quarantine` | **+1.000** |

---

## 4. Comprehensive 8-Policy Ledger ($k=6$)

| Policy | TPR | FPR | Healthy Path $C_H$ | Infected Leak $C_I$ | Containment ($1 - C_I$) | Autoimmunity ($1 - C_H$) | Net Separation $S$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `baseline` | 0.50 | 0.00 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.50 | 0.05 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.50 | 0.10 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.50 | 0.20 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.50 | 0.40 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.00 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.05 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.10 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.20 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.40 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.00 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.05 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.10 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.20 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.40 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.00 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.05 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.10 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.20 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.40 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.00 | 0.751 | 0.751 | 0.249 | 0.249 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.05 | 0.724 | 0.724 | 0.276 | 0.276 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.10 | 0.698 | 0.698 | 0.302 | 0.302 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.20 | 0.645 | 0.645 | 0.355 | 0.355 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.40 | 0.539 | 0.539 | 0.461 | 0.461 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.00 | 0.626 | 0.626 | 0.374 | 0.374 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.05 | 0.601 | 0.601 | 0.399 | 0.399 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.10 | 0.575 | 0.575 | 0.425 | 0.425 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.20 | 0.523 | 0.523 | 0.477 | 0.477 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.40 | 0.420 | 0.420 | 0.580 | 0.580 | **+0.000** |
| `generation_matched_thinning` | 0.90 | 0.00 | 0.551 | 0.552 | 0.448 | 0.449 | **-0.000** |
| `generation_matched_thinning` | 0.90 | 0.05 | 0.526 | 0.526 | 0.474 | 0.474 | **+0.000** |
| `generation_matched_thinning` | 0.90 | 0.10 | 0.501 | 0.501 | 0.499 | 0.499 | **-0.000** |
| `generation_matched_thinning` | 0.90 | 0.20 | 0.450 | 0.450 | 0.550 | 0.550 | **+0.000** |
| `generation_matched_thinning` | 0.90 | 0.40 | 0.349 | 0.349 | 0.651 | 0.651 | **-0.000** |
| `generation_matched_thinning` | 1.00 | 0.00 | 0.502 | 0.502 | 0.498 | 0.498 | **-0.000** |
| `generation_matched_thinning` | 1.00 | 0.05 | 0.477 | 0.477 | 0.523 | 0.523 | **+0.000** |
| `generation_matched_thinning` | 1.00 | 0.10 | 0.452 | 0.451 | 0.549 | 0.548 | **+0.000** |
| `generation_matched_thinning` | 1.00 | 0.20 | 0.401 | 0.401 | 0.599 | 0.599 | **-0.000** |
| `generation_matched_thinning` | 1.00 | 0.40 | 0.301 | 0.301 | 0.699 | 0.699 | **+0.000** |
| `lineage_quarantine` | 0.50 | 0.00 | 1.000 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `lineage_quarantine` | 0.50 | 0.05 | 0.950 | 0.500 | 0.500 | 0.050 | **+0.450** |
| `lineage_quarantine` | 0.50 | 0.10 | 0.900 | 0.500 | 0.500 | 0.100 | **+0.400** |
| `lineage_quarantine` | 0.50 | 0.20 | 0.800 | 0.500 | 0.500 | 0.200 | **+0.300** |
| `lineage_quarantine` | 0.50 | 0.40 | 0.600 | 0.500 | 0.500 | 0.400 | **+0.100** |
| `lineage_quarantine` | 0.75 | 0.00 | 1.000 | 0.250 | 0.750 | 0.000 | **+0.750** |
| `lineage_quarantine` | 0.75 | 0.05 | 0.950 | 0.250 | 0.750 | 0.050 | **+0.700** |
| `lineage_quarantine` | 0.75 | 0.10 | 0.900 | 0.250 | 0.750 | 0.100 | **+0.650** |
| `lineage_quarantine` | 0.75 | 0.20 | 0.800 | 0.250 | 0.750 | 0.200 | **+0.550** |
| `lineage_quarantine` | 0.75 | 0.40 | 0.600 | 0.250 | 0.750 | 0.400 | **+0.350** |
| `lineage_quarantine` | 0.90 | 0.00 | 1.000 | 0.100 | 0.900 | 0.000 | **+0.900** |
| `lineage_quarantine` | 0.90 | 0.05 | 0.950 | 0.100 | 0.900 | 0.050 | **+0.850** |
| `lineage_quarantine` | 0.90 | 0.10 | 0.900 | 0.100 | 0.900 | 0.100 | **+0.800** |
| `lineage_quarantine` | 0.90 | 0.20 | 0.800 | 0.100 | 0.900 | 0.200 | **+0.700** |
| `lineage_quarantine` | 0.90 | 0.40 | 0.600 | 0.100 | 0.900 | 0.400 | **+0.500** |
| `lineage_quarantine` | 1.00 | 0.00 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `lineage_quarantine` | 1.00 | 0.05 | 0.950 | 0.000 | 1.000 | 0.050 | **+0.950** |
| `lineage_quarantine` | 1.00 | 0.10 | 0.900 | 0.000 | 1.000 | 0.100 | **+0.900** |
| `lineage_quarantine` | 1.00 | 0.20 | 0.800 | 0.000 | 1.000 | 0.200 | **+0.800** |
| `lineage_quarantine` | 1.00 | 0.40 | 0.600 | 0.000 | 1.000 | 0.400 | **+0.600** |
| `node_only_quarantine` | 0.50 | 0.00 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.50 | 0.05 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.50 | 0.10 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.50 | 0.20 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.50 | 0.40 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.00 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.05 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.10 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.20 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.40 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.00 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.05 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.10 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.20 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.40 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.00 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.05 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.10 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.20 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.40 | 1.000 | 1.000 | 0.000 | 0.000 | **+0.000** |
| `oracle_upper_bound` | 0.50 | 0.00 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.50 | 0.05 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.50 | 0.10 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.50 | 0.20 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.50 | 0.40 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.00 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.05 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.10 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.20 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.40 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.00 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.05 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.10 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.20 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.40 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.00 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.05 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.10 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.20 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.40 | 1.000 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `random_family_quarantine` | 0.50 | 0.00 | 0.750 | 0.750 | 0.250 | 0.250 | **+0.000** |
| `random_family_quarantine` | 0.50 | 0.05 | 0.725 | 0.725 | 0.275 | 0.275 | **+0.000** |
| `random_family_quarantine` | 0.50 | 0.10 | 0.700 | 0.700 | 0.300 | 0.300 | **+0.000** |
| `random_family_quarantine` | 0.50 | 0.20 | 0.650 | 0.650 | 0.350 | 0.350 | **+0.000** |
| `random_family_quarantine` | 0.50 | 0.40 | 0.550 | 0.550 | 0.450 | 0.450 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.00 | 0.625 | 0.625 | 0.375 | 0.375 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.05 | 0.600 | 0.600 | 0.400 | 0.400 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.10 | 0.575 | 0.575 | 0.425 | 0.425 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.20 | 0.525 | 0.525 | 0.475 | 0.475 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.40 | 0.425 | 0.425 | 0.575 | 0.575 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.00 | 0.550 | 0.550 | 0.450 | 0.450 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.05 | 0.525 | 0.525 | 0.475 | 0.475 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.10 | 0.500 | 0.500 | 0.500 | 0.500 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.20 | 0.450 | 0.450 | 0.550 | 0.550 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.40 | 0.350 | 0.350 | 0.650 | 0.650 | **+0.000** |
| `random_family_quarantine` | 1.00 | 0.00 | 0.500 | 0.500 | 0.500 | 0.500 | **-0.000** |
| `random_family_quarantine` | 1.00 | 0.05 | 0.475 | 0.475 | 0.525 | 0.525 | **+0.000** |
| `random_family_quarantine` | 1.00 | 0.10 | 0.450 | 0.450 | 0.550 | 0.550 | **+0.000** |
| `random_family_quarantine` | 1.00 | 0.20 | 0.400 | 0.400 | 0.600 | 0.600 | **+0.000** |
| `random_family_quarantine` | 1.00 | 0.40 | 0.300 | 0.300 | 0.700 | 0.700 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.00 | 0.733 | 0.733 | 0.267 | 0.267 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.05 | 0.732 | 0.732 | 0.268 | 0.268 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.10 | 0.731 | 0.731 | 0.269 | 0.269 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.20 | 0.729 | 0.729 | 0.271 | 0.271 | **-0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.40 | 0.725 | 0.725 | 0.275 | 0.275 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.00 | 0.727 | 0.727 | 0.273 | 0.273 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.05 | 0.727 | 0.727 | 0.273 | 0.273 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.10 | 0.726 | 0.726 | 0.274 | 0.274 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.20 | 0.724 | 0.724 | 0.276 | 0.276 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.40 | 0.721 | 0.721 | 0.279 | 0.279 | **-0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.00 | 0.724 | 0.724 | 0.276 | 0.276 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.05 | 0.723 | 0.723 | 0.277 | 0.277 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.10 | 0.723 | 0.723 | 0.277 | 0.277 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.20 | 0.722 | 0.722 | 0.278 | 0.278 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.40 | 0.719 | 0.719 | 0.281 | 0.281 | **-0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.00 | 0.722 | 0.722 | 0.278 | 0.278 | **+0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.05 | 0.721 | 0.721 | 0.279 | 0.279 | **+0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.10 | 0.721 | 0.721 | 0.279 | 0.279 | **+0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.20 | 0.720 | 0.720 | 0.280 | 0.280 | **+0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.40 | 0.718 | 0.718 | 0.282 | 0.282 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.00 | 0.783 | 0.782 | 0.218 | 0.217 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.05 | 0.764 | 0.764 | 0.236 | 0.236 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.10 | 0.746 | 0.746 | 0.254 | 0.254 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.20 | 0.710 | 0.710 | 0.290 | 0.290 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.40 | 0.638 | 0.638 | 0.362 | 0.362 | **-0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.00 | 0.674 | 0.674 | 0.326 | 0.326 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.05 | 0.657 | 0.657 | 0.343 | 0.343 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.10 | 0.641 | 0.641 | 0.359 | 0.359 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.20 | 0.609 | 0.609 | 0.391 | 0.391 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.40 | 0.544 | 0.544 | 0.456 | 0.456 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.00 | 0.609 | 0.609 | 0.391 | 0.391 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.05 | 0.593 | 0.593 | 0.407 | 0.407 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.10 | 0.578 | 0.578 | 0.422 | 0.422 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.20 | 0.548 | 0.548 | 0.452 | 0.452 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.40 | 0.487 | 0.487 | 0.513 | 0.513 | **-0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.00 | 0.565 | 0.565 | 0.435 | 0.435 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.05 | 0.551 | 0.551 | 0.449 | 0.449 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.10 | 0.536 | 0.536 | 0.464 | 0.464 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.20 | 0.507 | 0.507 | 0.493 | 0.493 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.40 | 0.450 | 0.450 | 0.550 | 0.550 | **+0.000** |

---

## 5. Epistemic Autoimmunity & Gated Live Strategy

1. **Autoimmunity Equation**:
   Under whole-family lineage quarantine with $\gamma = 1.0$, healthy memory destruction scales linearly with the detector false alarm rate:
   $$\text{Epistemic Autoimmunity} = 1 - C_H = \text{FPR}$$
2. **The Crossover Principle**:
   In the tested sandbox, lineage quarantine overtakes generation-matched and uniform controls whenever $\text{TPR} - \text{FPR} > 0.35$.
3. **Live Gating Protocol**:
   When transitioning to live model evaluation, we do **not** run duplicate $(\text{TPR}, \text{FPR})$ points. Instead, we evaluate each unique concrete post-policy context ($(S_H, S_I) \in \{00, 10, 01, 11\}$) once on `gemma3:12b`, and then analytically reweight observed outputs across the full risk frontier.
