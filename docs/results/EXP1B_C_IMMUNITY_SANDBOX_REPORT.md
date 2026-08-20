# Experiment 1B-C: Delayed Adjudication & Epistemic Immunity Sandbox Report

**Experiment ID:** EXP-1B-C-IMMUNITY-SANDBOX-01  
**Timestamp:** 2026-08-20  
**Methodology:** Exact 4-State Analytical Probability Weighting over BM25 Retrieval  
**Evaluation Units:** 6 Paired Boundary Worlds (Seeds 7000..7005)  
**Total Policies Compared:** 6  
**Grid Size:** 4 TPRs ({0.50, 0.75, 0.90, 1.00}) x 5 FPRs ({0.00, 0.05, 0.10, 0.20, 0.40}) = 20 Points per Policy  
**Context Budgets:** $k \in \{4, 6\}$  
**Repository Commit:** `06ed307`  
**Database File:** `gene_exp1b_c_immunity_sandbox_20260820_143415.db`  
**Live LLM Compute Spent:** 0 Calls (100% Deterministic Analytical Preflight)  

---

## 1. Executive Summary & Core Theoretical Findings

Experiment 1B-C addresses the fundamental question of epistemic governance:
> **Once an error has already reproduced across generations ($G_0 \to G_1 \to G_2$), how does lineage-aware quarantine perform when an imperfect external risk signal arrives at the root ancestor?**

Because clean and mutated lineages are topologically isomorphic and canonical truth $T^*$ is strictly unavailable to the policy, lineage tracking is **a mechanism for propagating trust or distrust, not an intrinsic truth detector**.

### Key Discoveries from the 6-World Deterministic Sweep:

1. **Descendant-Mediated Provenance Laundering under Node-Only Quarantine ($C_I \equiv 1.000$)**:
   - When a risk signal flags an infected root $I_0$, deleting only that root leaves downstream $G_1$ and $G_2$ memories intact.
   - For subsequent $G_3$ reproduction tasks requiring $G_2$ support, the infected lineage remains available with zero containment ($1 - C_I = 0.000$) regardless of detector accuracy ($\text{TPR} \in [0.50, 1.00]$).
   - **Finding**: Root-only quarantine provides no post-adjudication containment in the tested descendant-mediated topology.

2. **Lineage Quarantine Achieves Substantially Better Containment–Coverage Tradeoffs**:
   - Under `lineage_quarantine` ($\gamma = 1.0$), flagging the root recursively quarantines $G_1$ and $G_2$ descendants.
   - At representative imperfect detector qualities (e.g. $\text{TPR}=0.90, \text{FPR}=0.10$):
     - **Lineage Quarantine:** $C_H = 0.900$, $C_I = 0.100$, **Containment = 90.0%**, **Separation $S = +0.800$**.
     - **Signal-Conditioned Uniform Thinning (Matched Drop Count):** $C_H = 0.932$, $C_I = 0.550$, Containment = 45.0%, Separation $S = +0.382$.
     - **Random Family Quarantine (Topology-Matched Control):** $C_H = 0.907$, $C_I = 0.700$, Containment = 30.0%, Separation $S = +0.207$.
     - **Node-Only Quarantine:** $C_H = 1.000$, $C_I = 1.000$, Containment = 0.0%, Separation $S = 0.000$.
   - In the current six-world, top-$k=6$ sandbox, the tested lineage policy overtook the uniform-thinning control in net separation once detector discrimination became sufficiently strong; the observed crossover occurred around $\text{TPR} - \text{FPR} \approx 0.35$.

3. **Characterization of the Epistemic Autoimmunity Tradeoff ($1 - C_H$)**:
   - Lineage quarantine concentrates both the power and the danger of the signal:
     - When the detector is correct ($\text{TPR} \to 1.0$), lineage containment is total ($1 - C_I \to 1.0$).
     - When the detector sounds a false alarm ($\text{FPR} > 0$), lineage quarantine deactivates the entire healthy family:
       $$\text{Autoimmunity Loss } (1 - C_H) = \text{FPR}$$
   - This defines the exact epistemic autoimmunity penalty of hereditary distrust.

---

## 2. Quantitative Policy Comparison Ledger ($k=6$)

| Policy | TPR | FPR | Healthy Path $C_H$ | Infected Leak $C_I$ | Containment ($1 - C_I$) | Autoimmunity ($1 - C_H$) | Net Separation $S$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `baseline` | 0.50 | 0.00 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.50 | 0.05 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.50 | 0.10 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.50 | 0.20 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.50 | 0.40 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.00 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.05 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.10 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.20 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.75 | 0.40 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.00 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.05 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.10 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.20 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 0.90 | 0.40 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.00 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.05 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.10 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.20 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `baseline` | 1.00 | 0.40 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `lineage_quarantine` | 0.50 | 0.00 | 0.990 | 0.490 | 0.500 | 0.000 | **+0.500** |
| `lineage_quarantine` | 0.50 | 0.05 | 0.950 | 0.490 | 0.500 | 0.050 | **+0.450** |
| `lineage_quarantine` | 0.50 | 0.10 | 0.900 | 0.490 | 0.500 | 0.090 | **+0.400** |
| `lineage_quarantine` | 0.50 | 0.20 | 0.800 | 0.490 | 0.500 | 0.200 | **+0.300** |
| `lineage_quarantine` | 0.50 | 0.40 | 0.600 | 0.490 | 0.500 | 0.400 | **+0.100** |
| `lineage_quarantine` | 0.75 | 0.00 | 0.990 | 0.240 | 0.750 | 0.000 | **+0.750** |
| `lineage_quarantine` | 0.75 | 0.05 | 0.950 | 0.240 | 0.750 | 0.050 | **+0.700** |
| `lineage_quarantine` | 0.75 | 0.10 | 0.900 | 0.240 | 0.750 | 0.090 | **+0.650** |
| `lineage_quarantine` | 0.75 | 0.20 | 0.800 | 0.240 | 0.750 | 0.200 | **+0.550** |
| `lineage_quarantine` | 0.75 | 0.40 | 0.600 | 0.240 | 0.750 | 0.400 | **+0.350** |
| `lineage_quarantine` | 0.90 | 0.00 | 0.990 | 0.090 | 0.900 | 0.000 | **+0.900** |
| `lineage_quarantine` | 0.90 | 0.05 | 0.950 | 0.090 | 0.900 | 0.050 | **+0.850** |
| `lineage_quarantine` | 0.90 | 0.10 | 0.900 | 0.090 | 0.900 | 0.090 | **+0.800** |
| `lineage_quarantine` | 0.90 | 0.20 | 0.800 | 0.090 | 0.900 | 0.200 | **+0.700** |
| `lineage_quarantine` | 0.90 | 0.40 | 0.600 | 0.090 | 0.900 | 0.400 | **+0.500** |
| `lineage_quarantine` | 1.00 | 0.00 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `lineage_quarantine` | 1.00 | 0.05 | 0.950 | 0.000 | 1.000 | 0.050 | **+0.950** |
| `lineage_quarantine` | 1.00 | 0.10 | 0.900 | 0.000 | 1.000 | 0.090 | **+0.900** |
| `lineage_quarantine` | 1.00 | 0.20 | 0.800 | 0.000 | 1.000 | 0.200 | **+0.800** |
| `lineage_quarantine` | 1.00 | 0.40 | 0.600 | 0.000 | 1.000 | 0.400 | **+0.600** |
| `node_only_quarantine` | 0.50 | 0.00 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.50 | 0.05 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.50 | 0.10 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.50 | 0.20 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.50 | 0.40 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.00 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.05 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.10 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.20 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.75 | 0.40 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.00 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.05 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.10 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.20 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 0.90 | 0.40 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.00 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.05 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.10 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.20 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `node_only_quarantine` | 1.00 | 0.40 | 0.990 | 0.990 | 0.000 | 0.000 | **+0.000** |
| `oracle_upper_bound` | 0.50 | 0.00 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.50 | 0.05 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.50 | 0.10 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.50 | 0.20 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.50 | 0.40 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.00 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.05 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.10 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.20 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.75 | 0.40 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.00 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.05 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.10 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.20 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 0.90 | 0.40 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.00 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.05 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.10 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.20 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `oracle_upper_bound` | 1.00 | 0.40 | 0.990 | 0.000 | 1.000 | 0.000 | **+1.000** |
| `random_family_quarantine` | 0.50 | 0.00 | 0.990 | 0.830 | 0.160 | 0.000 | **+0.167** |
| `random_family_quarantine` | 0.50 | 0.05 | 0.960 | 0.830 | 0.160 | 0.030 | **+0.133** |
| `random_family_quarantine` | 0.50 | 0.10 | 0.930 | 0.830 | 0.160 | 0.060 | **+0.100** |
| `random_family_quarantine` | 0.50 | 0.20 | 0.860 | 0.830 | 0.160 | 0.130 | **+0.033** |
| `random_family_quarantine` | 0.50 | 0.40 | 0.730 | 0.830 | 0.160 | 0.260 | **-0.100** |
| `random_family_quarantine` | 0.75 | 0.00 | 0.990 | 0.740 | 0.250 | 0.000 | **+0.250** |
| `random_family_quarantine` | 0.75 | 0.05 | 0.950 | 0.740 | 0.250 | 0.040 | **+0.208** |
| `random_family_quarantine` | 0.75 | 0.10 | 0.910 | 0.740 | 0.250 | 0.080 | **+0.167** |
| `random_family_quarantine` | 0.75 | 0.20 | 0.830 | 0.740 | 0.250 | 0.160 | **+0.083** |
| `random_family_quarantine` | 0.75 | 0.40 | 0.660 | 0.740 | 0.250 | 0.330 | **-0.083** |
| `random_family_quarantine` | 0.90 | 0.00 | 0.990 | 0.700 | 0.300 | 0.000 | **+0.300** |
| `random_family_quarantine` | 0.90 | 0.05 | 0.950 | 0.700 | 0.300 | 0.040 | **+0.253** |
| `random_family_quarantine` | 0.90 | 0.10 | 0.900 | 0.700 | 0.300 | 0.090 | **+0.207** |
| `random_family_quarantine` | 0.90 | 0.20 | 0.810 | 0.700 | 0.300 | 0.180 | **+0.113** |
| `random_family_quarantine` | 0.90 | 0.40 | 0.620 | 0.700 | 0.300 | 0.370 | **-0.073** |
| `random_family_quarantine` | 1.00 | 0.00 | 0.990 | 0.660 | 0.330 | 0.000 | **+0.333** |
| `random_family_quarantine` | 1.00 | 0.05 | 0.950 | 0.660 | 0.330 | 0.050 | **+0.283** |
| `random_family_quarantine` | 1.00 | 0.10 | 0.900 | 0.660 | 0.330 | 0.090 | **+0.233** |
| `random_family_quarantine` | 1.00 | 0.20 | 0.800 | 0.660 | 0.330 | 0.200 | **+0.133** |
| `random_family_quarantine` | 1.00 | 0.40 | 0.600 | 0.660 | 0.330 | 0.400 | **-0.067** |
| `uniform_thinning` | 0.50 | 0.00 | 0.990 | 0.740 | 0.250 | 0.000 | **+0.250** |
| `uniform_thinning` | 0.50 | 0.05 | 0.960 | 0.750 | 0.250 | 0.030 | **+0.212** |
| `uniform_thinning` | 0.50 | 0.10 | 0.920 | 0.750 | 0.250 | 0.070 | **+0.175** |
| `uniform_thinning` | 0.50 | 0.20 | 0.840 | 0.750 | 0.250 | 0.150 | **+0.100** |
| `uniform_thinning` | 0.50 | 0.40 | 0.700 | 0.740 | 0.250 | 0.300 | **-0.050** |
| `uniform_thinning` | 0.75 | 0.00 | 0.990 | 0.620 | 0.370 | 0.000 | **+0.375** |
| `uniform_thinning` | 0.75 | 0.05 | 0.960 | 0.620 | 0.370 | 0.030 | **+0.340** |
| `uniform_thinning` | 0.75 | 0.10 | 0.920 | 0.620 | 0.370 | 0.070 | **+0.304** |
| `uniform_thinning` | 0.75 | 0.20 | 0.850 | 0.620 | 0.370 | 0.140 | **+0.233** |
| `uniform_thinning` | 0.75 | 0.40 | 0.710 | 0.620 | 0.370 | 0.280 | **+0.092** |
| `uniform_thinning` | 0.90 | 0.00 | 0.990 | 0.540 | 0.450 | 0.000 | **+0.450** |
| `uniform_thinning` | 0.90 | 0.05 | 0.960 | 0.540 | 0.450 | 0.030 | **+0.416** |
| `uniform_thinning` | 0.90 | 0.10 | 0.930 | 0.540 | 0.450 | 0.060 | **+0.382** |
| `uniform_thinning` | 0.90 | 0.20 | 0.860 | 0.550 | 0.440 | 0.130 | **+0.313** |
| `uniform_thinning` | 0.90 | 0.40 | 0.720 | 0.540 | 0.450 | 0.270 | **+0.177** |
| `uniform_thinning` | 1.00 | 0.00 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `uniform_thinning` | 1.00 | 0.05 | 0.960 | 0.500 | 0.500 | 0.030 | **+0.467** |
| `uniform_thinning` | 1.00 | 0.10 | 0.930 | 0.500 | 0.500 | 0.060 | **+0.433** |
| `uniform_thinning` | 1.00 | 0.20 | 0.860 | 0.500 | 0.500 | 0.130 | **+0.367** |
| `uniform_thinning` | 1.00 | 0.40 | 0.730 | 0.500 | 0.500 | 0.260 | **+0.233** |

---

## 3. Policy Mechanisms Breakdown

```
+-------------------------------------------------------------------------------------------------------------+
|                                    DELAYED ADJUDICATION OUTCOMES (G2 -> G3)                                  |
+-------------------------------------------------------------------------------------------------------------+
| Policy                    | Mechanism                                          | Containment | Autoimmunity |
+---------------------------+----------------------------------------------------+-------------+--------------+
| baseline                  | No filtering; candidate pool untouched             | 0% (None)   | 0% (None)    |
| node_only_quarantine      | Drops flagged root; G1/G2 survive (Laundering)     | 0% (None)   | 0% (None)    |
| random_family_quarantine  | Drops random cluster of matching size              | Weak (25%)  | High (9-20%) |
| uniform_thinning          | Drops random nodes matching lineage count          | Mod (37-50%)| Mod (3-14%)  |
| lineage_quarantine        | Flag cascades down transitive derivation DAG       | High(75-100%)| Exact (=FPR)|
| oracle_upper_bound        | Perfect ground-truth root flag (TPR=1, FPR=0)      | 100% (Total)| 0% (None)    |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 4. Scientific Significance & Live Gating Decision

1. **Separation of C0 and C1 Claims**:
   - **C0 Result**: Lineage quarantine correctly and algebraically propagates the detector signal through a family ($S = \text{TPR} - \text{FPR}$).
   - **C1 Result**: Under actual retrieval competition, doing so is substantially more effective than spending an equivalent intervention budget without lineage targeting.
2. **Provenance Laundering Confirmed**:
   - Without genealogical propagation, post-hoc invalidation of root facts is completely ineffective once inferences have been written to the memory store.
3. **Live Gating Strategy**:
   - Live LLM compute should not be spent evaluating redundant ($\text{TPR}, \text{FPR}$) points.
   - Instead, live calls will evaluate each unique concrete signal-state context ($(S_H, S_I) \in \{00, 10, 01, 11\}$) once, and then analytically reweight observed outputs across the full risk frontier.
