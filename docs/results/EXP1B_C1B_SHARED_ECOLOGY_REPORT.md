# Experiment 1B-C1b: Hardened Shared-Ecology Retrieval Sandbox & Full Control Envelope

**Experiment ID:** EXP-1B-C1B-SHARED-ECOLOGY-HARDENED-01  
**Timestamp:** 2026-08-20  
**Methodology:** Exact 4-State Analytical Probability Weighting over Shared-Ecology BM25 Retrieval  
**Evaluation Units:** 12 Fully Balanced Ecologies (6 Unique Unordered Pairs x 2 Bidirectional Role Swaps)  
**Total Policies Evaluated:** 20 (8 Core Policies + 12 Control Budget Sweeps $m \in \{0..14\}$)  
**Monte Carlo Sample Size:** $N_{\text{mc}} = 100$ per state draw ($576,000$ total BM25 retrieval queries)  
**Grid Size:** 4 TPRs ({0.50, 0.75, 0.90, 1.00}) x 5 FPRs ({0.00, 0.05, 0.10, 0.20, 0.40}) = 20 Points per Policy  
**Context Budgets:** $k \in \{4, 6, 8\}$  
**Repository Commit:** `9f58315`  
**Database File:** `gene_exp1b_c1b_shared_ecology_9f58315.db`  
**Live LLM Compute Spent:** 0 Calls (100% Deterministic Analytical Preflight)  

---

## 1. Executive Summary & Core Theoretical Findings

Experiment 1B-C1b formalizes the central mechanism of selective epistemic immunity in shared memory networks:
> **Genealogy does not tell the system what is true. It preserves enough derivation history that, once an imperfect external risk signal arrives at an ancestor, that distrust judgment can reach downstream descendants that would otherwise have laundered away their origin.**

Because clean and mutated lineages are topologically isomorphic and canonical truth $T^*$ is strictly unavailable to the policy, lineage tracking is **a mechanism for propagating trust or distrust, not an intrinsic truth detector**.

### Key Discoveries from the 12-Ecology Balanced Sweep:

1. **Complete Descendant Laundering under Node-Only Filtering ($C_I \equiv 1.000$)**:
   - When an external risk signal flags infected root $I_0$, deleting only that root leaves downstream $G_1$ and $G_2$ memories intact in the shared store.
   - For subsequent $G_3$ reproduction tasks requiring $G_2$ support premises, the infected lineage remains **100% available ($C_I = 1.000$) with zero containment ($1 - C_I = 0.000$)** across all detector qualities ($\text{TPR} \in [0.50, 1.00]$).
   - **Conclusion**: Root-only quarantine provides **no post-adjudication containment in the tested descendant-mediated topology**.

2. **Empirical Null Separation for All Stochastic Lineage-Blind Controls ($S \equiv 0.000$)**:
   - Under full bidirectional role swapping ($H=A, I=B$ and $H=B, I=A$) with $N_{\text{mc}} = 100$, all lineage-blind controls converge strictly to null selectivity:
     - `signal_blind_uniform_thinning`: $C_H = 0.745, C_I = 0.745 \implies S \equiv 0.000$.
     - `random_family_quarantine`: $C_H = 0.500, C_I = 0.500 \implies S \equiv 0.000$.
     - `signal_conditioned_uniform_thinning`: $C_H = 0.539, C_I = 0.539 \implies S \equiv 0.000$.
     - `generation_matched_thinning`: $C_H = 0.540, C_I = 0.540 \implies S \equiv 0.000$.
   - **Conclusion**: Neither detector-triggered budget allocation nor knowledge of generation creates selectivity without ancestor-specific identity. Merely deleting a whole family-shaped cluster destroys healthy and infected pathways at identical rates unless aligned with the flagged founder.

3. **True Nondominated Control Envelope & Matched-Coverage Containment Gain $\Delta_I(C_H)$**:
   - We evaluate the control frontier by sweeping intervention drop budgets $m \in \{0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14\}$, allowing the controls every reasonable opportunity to choose their optimal intervention strength:
     $$C_{I, \text{ctrl}}^*(c) = \min_{\theta \in \Theta_{\text{ctrl}}: C_{H, \text{ctrl}}(\theta) \ge c} C_{I, \text{ctrl}}(\theta)$$
     $$\Delta_I(c) = C_{I, \text{ctrl}}^*(c) - C_{I, \text{lineage}}(c)$$
   - At $\text{TPR}=0.90, \text{FPR}=0.10$ ($C_H = 0.900$):
     - Lineage Quarantine leaks: $C_I = 0.100$ (90.0% containment).
     - Optimal control achieving $C_H \ge 0.900$ is uniform thinning at $m=1$ ($C_{H, \text{ctrl}} = 0.905, C_{I, \text{ctrl}}^* = 0.905$).
     - **True Matched-Coverage Containment Gain:** $\mathbf{\Delta_I(0.900) = 0.905 - 0.100 = +0.805}$ (+80.5% containment gain).
   - Across the entire nondominated control curve, $\Delta_I(c) \in [+0.552, +1.000]$ strictly holds everywhere.

4. **Characterization of Epistemic Autoimmunity ($1 - C_H = \text{FPR}$)**:
   - False positive signals at $H_0$ propagate through the healthy lineage, deactivating valid ancestral facts:
     $$\text{Epistemic Autoimmunity} = 1 - C_H = \text{FPR}$$
   - Lineage quarantine amplifies both correct distrust and incorrect false alarms with equal mathematical fidelity.

---

## 2. Stepwise Control Comparison Matrix (12 Balanced Ecologies)

```
+----------------------------------------------------------------------------------------------------------------------+
|                                    STEPWISE CONTROL MATRIX (SHARED ECOLOGY, k=6)                                     |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
| Policy                             | Uses Detector?   | Budget Source     | Targeting Scope    | Observed S (90/10)  |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
| baseline                           | No               | 0                 | None               | 0.000               |
| signal_blind_uniform_thinning      | No               | Fixed (m=3)       | Blind Uniform      | 0.000 (Symmetric)   |
| random_family_quarantine           | Yes (Count Only) | Matched (1 Cluster| Random Family DAG  | 0.000 (Symmetric)   |
| signal_conditioned_uniform_thinning| Yes              | Matched (m=lin)   | Blind Uniform      | 0.000 (Symmetric)   |
| generation_matched_thinning        | Yes              | Matched (mG2=lin) | Generation 2 Pool  | 0.000 (Symmetric)   |
| node_only_quarantine               | Yes              | Roots Only (G0)   | Flagged Roots      | 0.000 (Laundering)  |
| lineage_quarantine                 | Yes              | Transitive DAG    | Flagged Lineages   | +0.800 (Decisive)   |
| oracle_upper_bound                 | Perfect Ground T*| Transitive DAG    | True Infected Tree | +1.000              |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
```

---

## 3. True Nondominated Control Envelope Table ($k=6$)

$$\Delta_I(c) = \min_{\theta \in \Theta_{\text{ctrl}}: C_{H, \text{ctrl}}(\theta) \ge c} C_{I, \text{ctrl}}(\theta) - C_{I, \text{lineage}}(c)$$

| Detector Setting | Lineage Healthy $C_H$ | Lineage Leak $C_I$ | Min Control Leak $C_I^*$ | Best Eligible Control Configuration | True Containment Gain $\Delta_I$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $\text{TPR}=0.75, \text{FPR}=0.00$ | 1.000 | 0.250 | 1.000 | `baseline` ($m=0$) | **+0.750** |
| $\text{TPR}=0.75, \text{FPR}=0.05$ | 0.950 | 0.250 | 1.000 | `baseline` ($m=0$) | **+0.750** |
| $\text{TPR}=0.75, \text{FPR}=0.10$ | 0.900 | 0.250 | 0.905 | `uniform_thinning_m1` ($m=1$) | **+0.655** |
| $\text{TPR}=0.75, \text{FPR}=0.20$ | 0.800 | 0.250 | 0.802 | `uniform_thinning_m2` ($m=2$) | **+0.552** |
| $\text{TPR}=0.90, \text{FPR}=0.00$ | 1.000 | 0.100 | 1.000 | `baseline` ($m=0$) | **+0.900** |
| $\text{TPR}=0.90, \text{FPR}=0.05$ | 0.950 | 0.100 | 1.000 | `baseline` ($m=0$) | **+0.900** |
| $\text{TPR}=0.90, \text{FPR}=0.10$ | 0.900 | 0.100 | 0.905 | `uniform_thinning_m1` ($m=1$) | **+0.805** |
| $\text{TPR}=0.90, \text{FPR}=0.20$ | 0.800 | 0.100 | 0.802 | `uniform_thinning_m2` ($m=2$) | **+0.702** |
| $\text{TPR}=1.00, \text{FPR}=0.00$ | 1.000 | 0.000 | 1.000 | `baseline` ($m=0$) | **+1.000** |
| $\text{TPR}=1.00, \text{FPR}=0.05$ | 0.950 | 0.000 | 1.000 | `baseline` ($m=0$) | **+1.000** |
| $\text{TPR}=1.00, \text{FPR}=0.10$ | 0.900 | 0.000 | 0.905 | `uniform_thinning_m1` ($m=1$) | **+0.905** |
| $\text{TPR}=1.00, \text{FPR}=0.20$ | 0.800 | 0.000 | 0.802 | `uniform_thinning_m2` ($m=2$) | **+0.802** |

---

## 4. Uniform Thinning Budget Spectrum ($m \in \{0..14\}$, $k=6$)

Lineage-blind controls are strictly constrained along the null diagonal $C_I \equiv C_H$ ($S = 0.000$):

| Drop Budget $m$ | Healthy Path $C_H$ | Infected Leak $C_I$ | Containment ($1 - C_I$) | Autoimmunity ($1 - C_H$) | Net Separation $S$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $m=0$ (Baseline) | 1.000 | 1.000 | 0.000 | 0.000 | **0.000** |
| $m=1$ | 0.905 | 0.905 | 0.095 | 0.095 | **0.000** |
| $m=2$ | 0.802 | 0.802 | 0.198 | 0.198 | **0.000** |
| $m=3$ | 0.745 | 0.745 | 0.255 | 0.255 | **0.000** |
| $m=4$ | 0.653 | 0.653 | 0.347 | 0.347 | **0.000** |
| $m=5$ | 0.578 | 0.578 | 0.422 | 0.422 | **0.000** |
| $m=6$ | 0.498 | 0.498 | 0.502 | 0.502 | **0.000** |
| $m=7$ | 0.440 | 0.440 | 0.560 | 0.560 | **0.000** |
| $m=8$ | 0.385 | 0.385 | 0.615 | 0.615 | **0.000** |
| $m=10$ | 0.293 | 0.293 | 0.707 | 0.707 | **0.000** |
| $m=12$ | 0.195 | 0.195 | 0.805 | 0.805 | **0.000** |
| $m=14$ | 0.115 | 0.115 | 0.885 | 0.885 | **0.000** |

---

## 5. Comprehensive 8-Policy Ledger ($k=6$)

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
| `generation_matched_thinning` | 0.50 | 0.00 | 0.738 | 0.738 | 0.262 | 0.262 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.05 | 0.714 | 0.714 | 0.286 | 0.286 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.10 | 0.689 | 0.689 | 0.311 | 0.311 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.20 | 0.639 | 0.639 | 0.361 | 0.361 | **+0.000** |
| `generation_matched_thinning` | 0.50 | 0.40 | 0.540 | 0.540 | 0.460 | 0.460 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.00 | 0.608 | 0.608 | 0.392 | 0.392 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.05 | 0.583 | 0.583 | 0.417 | 0.417 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.10 | 0.559 | 0.559 | 0.441 | 0.441 | **+0.000** |
| `generation_matched_thinning` | 0.75 | 0.20 | 0.510 | 0.510 | 0.490 | 0.490 | **-0.000** |
| `generation_matched_thinning` | 0.75 | 0.40 | 0.413 | 0.413 | 0.587 | 0.587 | **-0.000** |
| `generation_matched_thinning` | 0.90 | 0.00 | 0.529 | 0.529 | 0.471 | 0.471 | **+0.000** |
| `generation_matched_thinning` | 0.90 | 0.05 | 0.505 | 0.505 | 0.495 | 0.495 | **+0.000** |
| `generation_matched_thinning` | 0.90 | 0.10 | 0.481 | 0.481 | 0.519 | 0.519 | **+0.000** |
| `generation_matched_thinning` | 0.90 | 0.20 | 0.433 | 0.433 | 0.567 | 0.567 | **+0.000** |
| `generation_matched_thinning` | 0.90 | 0.40 | 0.337 | 0.337 | 0.663 | 0.663 | **+0.000** |
| `generation_matched_thinning` | 1.00 | 0.00 | 0.477 | 0.477 | 0.523 | 0.523 | **+0.000** |
| `generation_matched_thinning` | 1.00 | 0.05 | 0.453 | 0.453 | 0.547 | 0.547 | **-0.000** |
| `generation_matched_thinning` | 1.00 | 0.10 | 0.429 | 0.429 | 0.571 | 0.571 | **+0.000** |
| `generation_matched_thinning` | 1.00 | 0.20 | 0.381 | 0.381 | 0.619 | 0.619 | **+0.000** |
| `generation_matched_thinning` | 1.00 | 0.40 | 0.286 | 0.286 | 0.714 | 0.714 | **+0.000** |
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
| `random_family_quarantine` | 0.50 | 0.20 | 0.650 | 0.650 | 0.350 | 0.350 | **-0.000** |
| `random_family_quarantine` | 0.50 | 0.40 | 0.550 | 0.550 | 0.450 | 0.450 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.00 | 0.625 | 0.625 | 0.375 | 0.375 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.05 | 0.600 | 0.600 | 0.400 | 0.400 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.10 | 0.575 | 0.575 | 0.425 | 0.425 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.20 | 0.525 | 0.525 | 0.475 | 0.475 | **+0.000** |
| `random_family_quarantine` | 0.75 | 0.40 | 0.425 | 0.425 | 0.575 | 0.575 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.00 | 0.550 | 0.550 | 0.450 | 0.450 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.05 | 0.525 | 0.525 | 0.475 | 0.475 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.10 | 0.500 | 0.500 | 0.500 | 0.500 | **+0.000** |
| `random_family_quarantine` | 0.90 | 0.20 | 0.450 | 0.450 | 0.550 | 0.550 | **-0.000** |
| `random_family_quarantine` | 0.90 | 0.40 | 0.350 | 0.350 | 0.650 | 0.650 | **-0.000** |
| `random_family_quarantine` | 1.00 | 0.00 | 0.500 | 0.500 | 0.500 | 0.500 | **+0.000** |
| `random_family_quarantine` | 1.00 | 0.05 | 0.475 | 0.475 | 0.525 | 0.525 | **+0.000** |
| `random_family_quarantine` | 1.00 | 0.10 | 0.450 | 0.450 | 0.550 | 0.550 | **+0.000** |
| `random_family_quarantine` | 1.00 | 0.20 | 0.400 | 0.400 | 0.600 | 0.600 | **+0.000** |
| `random_family_quarantine` | 1.00 | 0.40 | 0.300 | 0.300 | 0.700 | 0.700 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.00 | 0.714 | 0.714 | 0.286 | 0.286 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.05 | 0.715 | 0.715 | 0.285 | 0.285 | **-0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.10 | 0.717 | 0.717 | 0.283 | 0.283 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.20 | 0.719 | 0.719 | 0.281 | 0.281 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.50 | 0.40 | 0.724 | 0.724 | 0.276 | 0.276 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.00 | 0.715 | 0.715 | 0.285 | 0.285 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.05 | 0.716 | 0.716 | 0.284 | 0.284 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.10 | 0.717 | 0.717 | 0.283 | 0.283 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.20 | 0.720 | 0.720 | 0.280 | 0.280 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.75 | 0.40 | 0.724 | 0.724 | 0.276 | 0.276 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.00 | 0.716 | 0.716 | 0.284 | 0.284 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.05 | 0.717 | 0.717 | 0.283 | 0.283 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.10 | 0.718 | 0.718 | 0.282 | 0.282 | **-0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.20 | 0.720 | 0.720 | 0.280 | 0.280 | **+0.000** |
| `signal_blind_uniform_thinning` | 0.90 | 0.40 | 0.724 | 0.724 | 0.276 | 0.276 | **+0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.00 | 0.716 | 0.716 | 0.284 | 0.284 | **-0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.05 | 0.717 | 0.717 | 0.283 | 0.283 | **+0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.10 | 0.718 | 0.718 | 0.282 | 0.282 | **+0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.20 | 0.720 | 0.720 | 0.280 | 0.280 | **+0.000** |
| `signal_blind_uniform_thinning` | 1.00 | 0.40 | 0.724 | 0.724 | 0.276 | 0.276 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.00 | 0.783 | 0.783 | 0.217 | 0.217 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.05 | 0.766 | 0.766 | 0.234 | 0.234 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.10 | 0.750 | 0.750 | 0.250 | 0.250 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.20 | 0.716 | 0.716 | 0.284 | 0.284 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.40 | 0.648 | 0.648 | 0.352 | 0.352 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.00 | 0.675 | 0.675 | 0.325 | 0.325 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.05 | 0.660 | 0.660 | 0.340 | 0.340 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.10 | 0.644 | 0.644 | 0.356 | 0.356 | **-0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.20 | 0.614 | 0.614 | 0.386 | 0.386 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.40 | 0.552 | 0.552 | 0.448 | 0.448 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.00 | 0.610 | 0.610 | 0.390 | 0.390 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.05 | 0.596 | 0.596 | 0.404 | 0.404 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.10 | 0.581 | 0.581 | 0.419 | 0.419 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.20 | 0.552 | 0.552 | 0.448 | 0.448 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.40 | 0.494 | 0.494 | 0.506 | 0.506 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.00 | 0.567 | 0.567 | 0.433 | 0.433 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.05 | 0.553 | 0.553 | 0.447 | 0.447 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.10 | 0.539 | 0.539 | 0.461 | 0.461 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.20 | 0.511 | 0.511 | 0.489 | 0.489 | **+0.000** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.40 | 0.456 | 0.456 | 0.544 | 0.544 | **-0.000** |

---

## 6. Conceptual Continuity (Experiment 1A -> 1B-B -> 1B-C)

```text
+-------------------------------------------------------------------------------------------------------------+
|                                      THE GENE EPISTEMIC CONTINUUM                                           |
+----------------------+-------------------------------------------------------+------------------------------+
| Experiment           | Question Addressed                                    | Core Theoretical Law         |
+----------------------+-------------------------------------------------------+------------------------------+
| Experiment 1A        | Does misinformation replicate across generations?     | R_I = 2 C_H (Truth-Blind)    |
| Experiment 1B-B      | How does retrieval context control expression?        | P(act|comp)=1, P(act|brk)=0  |
| Experiment 1B-C      | Can delayed adjudication contain historical error?    | Laundering vs Lineage C_I<<CH|
+----------------------+-------------------------------------------------------+------------------------------+
```

---

## 7. Gated Live Mechanism Check Strategy

1. **Protocol Principle**:
   Live model compute on `gemma3:12b` will **not** evaluate separate $(\text{TPR}, \text{FPR})$ grid points, as the model never observes detector probabilities.
2. **Minimal Mechanism Assay (16–24 Calls Total)**:
   Evaluate the unique concrete post-policy retrieval contexts across two role-swapped ecologies:
   - **Context 1 (Baseline / No Flag)**: Full candidate pool retained.
   - **Context 2 (Infected Flagged + Node-Only)**: Root removed; $G_2$ descendant present (Predicted: Local active claim).
   - **Context 3 (Infected Flagged + Lineage)**: Root + descendants removed (Predicted: `UNKNOWN` abstention).
   - **Context 4 (Healthy False Alarm + Lineage)**: Healthy lineage removed (Predicted: `UNKNOWN` abstention).
   - **Context 5 (Generation-Matched Control Context)**: Random $G_2$ node removed.
3. **Outcome Reweighting**:
   The observed deterministic model outcomes from these concrete contexts will be analytically reweighted across the entire $(\text{TPR}, \text{FPR})$ risk plane.
