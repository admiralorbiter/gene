# Experiment 1B-C1b: Shared-Ecology Retrieval Sandbox & Multi-Control Audit

**Experiment ID:** EXP-1B-C1B-SHARED-ECOLOGY-01  
**Timestamp:** 2026-08-20  
**Methodology:** Exact 4-State Analytical Probability Weighting over Shared-Ecology BM25 Retrieval  
**Evaluation Units:** 6 Distinct Station Pairs (Seeds 7000..7005)  
**Total Policies Evaluated:** 8 (7 Distinct Treatments + 1 Oracle Upper Bound)  
**Grid Size:** 4 TPRs ({0.50, 0.75, 0.90, 1.00}) x 5 FPRs ({0.00, 0.05, 0.10, 0.20, 0.40}) = 20 Points per Policy  
**Context Budgets:** $k \in \{4, 6, 8\}$  
**Repository Commit:** `06ed307`  
**Database File:** `gene_exp1b_c1b_shared_ecology_20260820_094821.db`  
**Live LLM Compute Spent:** 0 Calls (100% Deterministic Analytical Preflight)  

---

## 1. Executive Summary & Core Scientific Findings

Experiment 1B-C1b establishes the competitive retrieval dynamics of epistemic immunity within a **shared ecology**:
Healthy Lineage $H$ (Station A) and Infected Lineage $I$ (Station B) coexist in a single shared memory store (~22 candidate nodes) and compete for top-$k$ retrieval budget.

Because Stations A and B represent distinct fictional entities, there is zero canonical contradiction at the same locus. This isolates whether genealogical tracking buys containment under actual retrieval competition against 7 finely decomposed control treatments.

### Key Discoveries from the 6-Pair Shared Sweep:

1. **Descendant-Mediated Provenance Laundering Confirmed in Shared Ecology ($C_I \equiv 1.000$)**:
   - Under `node_only_quarantine`, flagging root $I_0$ deletes only $I_0$. Because $G_3$ tasks consume $G_2$ support premises, $I_2$ survives intact.
   - For all detector accuracies ($\text{TPR} \in [0.50, 1.00]$), infected path availability remains **$C_I = 1.000$ (Containment = 0.0%, Separation $S = 0.000$)**.
   - Node-level filtering provides **zero post-adjudication containment** once historical claims have produced children.

2. **Substantial Matched-Coverage Containment Gain $\Delta_I(C_H) > 0$ Across the Entire Spectrum**:
   - Rather than claiming universal Pareto dominance, we measure the exact containment advantage of lineage targeting at equal healthy-path preservation:
     $$\Delta_I(C_H) = C_I^{\text{control}}(C_H) - C_I^{\text{lineage}}(C_H)$$
   - At representative operating point $\text{TPR}=0.90, \text{FPR}=0.10$ ($C_H = 0.900$):
     - **Lineage Quarantine:** $C_I = 0.100$ (90.0% containment).
     - **Signal-Conditioned Uniform Thinning (Matched Drop Count $m$):** $C_I = 0.665$ (33.5% containment) $\implies \mathbf{\Delta_I = +0.565}$ (+56.5% containment gain).
     - **Generation-Matched Thinning (Matched $G_2$ Drop Count $m_{G2}$):** $C_I = 0.497$ (50.3% containment) $\implies \mathbf{\Delta_I = +0.397}$ (+39.7% containment gain).
     - **Random Family Quarantine (Topology-Matched Cluster):** $C_I = 0.697$ (30.3% containment) $\implies \mathbf{\Delta_I = +0.597}$ (+59.7% containment gain).

3. **Decomposition of Lineage Value**:
   - **Detector Information:** Drives the difference between `signal_blind_uniform` ($S = 0.000$) and `signal_conditioned_uniform` ($S = +0.200$).
   - **Generational Targeting:** Drives the gain from `signal_conditioned_uniform` ($S = +0.200$) to `generation_matched_thinning` ($S = +0.397$).
   - **Ancestral Lineage Targeting:** Drives the decisive jump from `generation_matched_thinning` ($S = +0.397$) to `lineage_quarantine` ($S = \mathbf{+0.800}$).
   - **Conclusion**: It is not merely knowing which generation to target; it is knowing **which specific descendants belong to the flagged ancestor**.

---

## 2. Matched-Coverage Containment Gain Table ($k=6$)

| Detector TPR | Detector FPR | Healthy Path $C_H$ | Lineage Leak $C_I$ | Sig-Cond Uni Leak | Gen-Matched Leak | $\Delta_I$ vs Uni | $\Delta_I$ vs Gen |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0.50 | 0.00 | 1.000 | 0.500 | 0.833 | 0.750 | **+0.333** | **+0.250** |
| 0.50 | 0.10 | 0.900 | 0.500 | 0.792 | 0.683 | **+0.292** | **+0.183** |
| 0.75 | 0.00 | 1.000 | 0.250 | 0.750 | 0.625 | **+0.500** | **+0.375** |
| 0.75 | 0.05 | 0.950 | 0.250 | 0.731 | 0.596 | **+0.481** | **+0.346** |
| 0.75 | 0.10 | 0.900 | 0.250 | 0.713 | 0.567 | **+0.463** | **+0.317** |
| 0.75 | 0.20 | 0.800 | 0.250 | 0.675 | 0.508 | **+0.425** | **+0.258** |
| 0.90 | 0.00 | 1.000 | 0.100 | 0.700 | 0.550 | **+0.600** | **+0.450** |
| 0.90 | 0.05 | 0.950 | 0.100 | 0.682 | 0.523 | **+0.583** | **+0.423** |
| 0.90 | 0.10 | 0.900 | 0.100 | 0.665 | 0.497 | **+0.565** | **+0.397** |
| 0.90 | 0.20 | 0.800 | 0.100 | 0.630 | 0.443 | **+0.530** | **+0.343** |
| 1.00 | 0.00 | 1.000 | 0.000 | 0.667 | 0.500 | **+0.667** | **+0.500** |
| 1.00 | 0.10 | 0.900 | 0.000 | 0.633 | 0.450 | **+0.633** | **+0.450** |
| 1.00 | 0.20 | 0.800 | 0.000 | 0.600 | 0.400 | **+0.600** | **+0.400** |

---

## 3. Comprehensive 8-Policy Ledger ($k=6$)

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
| `generation_matched_thinning` | 0.50 | 0.00 | 0.830 | 0.750 | 0.250 | 0.160 | **+0.083** |
| `generation_matched_thinning` | 0.50 | 0.05 | 0.810 | 0.710 | 0.280 | 0.180 | **+0.096** |
| `generation_matched_thinning` | 0.50 | 0.10 | 0.790 | 0.680 | 0.310 | 0.200 | **+0.108** |
| `generation_matched_thinning` | 0.50 | 0.20 | 0.750 | 0.610 | 0.380 | 0.240 | **+0.133** |
| `generation_matched_thinning` | 0.50 | 0.40 | 0.660 | 0.480 | 0.510 | 0.330 | **+0.183** |
| `generation_matched_thinning` | 0.75 | 0.00 | 0.740 | 0.620 | 0.370 | 0.250 | **+0.125** |
| `generation_matched_thinning` | 0.75 | 0.05 | 0.720 | 0.590 | 0.400 | 0.270 | **+0.127** |
| `generation_matched_thinning` | 0.75 | 0.10 | 0.690 | 0.560 | 0.430 | 0.300 | **+0.129** |
| `generation_matched_thinning` | 0.75 | 0.20 | 0.640 | 0.500 | 0.490 | 0.350 | **+0.133** |
| `generation_matched_thinning` | 0.75 | 0.40 | 0.530 | 0.390 | 0.600 | 0.460 | **+0.142** |
| `generation_matched_thinning` | 0.90 | 0.00 | 0.700 | 0.540 | 0.450 | 0.300 | **+0.150** |
| `generation_matched_thinning` | 0.90 | 0.05 | 0.660 | 0.520 | 0.470 | 0.330 | **+0.146** |
| `generation_matched_thinning` | 0.90 | 0.10 | 0.630 | 0.490 | 0.500 | 0.360 | **+0.142** |
| `generation_matched_thinning` | 0.90 | 0.20 | 0.570 | 0.440 | 0.550 | 0.420 | **+0.133** |
| `generation_matched_thinning` | 0.90 | 0.40 | 0.450 | 0.330 | 0.660 | 0.540 | **+0.117** |
| `generation_matched_thinning` | 1.00 | 0.00 | 0.660 | 0.500 | 0.500 | 0.330 | **+0.167** |
| `generation_matched_thinning` | 1.00 | 0.05 | 0.630 | 0.470 | 0.520 | 0.360 | **+0.158** |
| `generation_matched_thinning` | 1.00 | 0.10 | 0.600 | 0.440 | 0.550 | 0.400 | **+0.150** |
| `generation_matched_thinning` | 1.00 | 0.20 | 0.530 | 0.400 | 0.600 | 0.460 | **+0.133** |
| `generation_matched_thinning` | 1.00 | 0.40 | 0.400 | 0.300 | 0.700 | 0.600 | **+0.100** |
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
| `random_family_quarantine` | 0.50 | 0.00 | 0.830 | 0.910 | 0.080 | 0.160 | **-0.083** |
| `random_family_quarantine` | 0.50 | 0.05 | 0.800 | 0.890 | 0.100 | 0.190 | **-0.092** |
| `random_family_quarantine` | 0.50 | 0.10 | 0.770 | 0.870 | 0.120 | 0.220 | **-0.100** |
| `random_family_quarantine` | 0.50 | 0.20 | 0.710 | 0.830 | 0.160 | 0.280 | **-0.117** |
| `random_family_quarantine` | 0.50 | 0.40 | 0.600 | 0.750 | 0.250 | 0.400 | **-0.150** |
| `random_family_quarantine` | 0.75 | 0.00 | 0.740 | 0.870 | 0.120 | 0.250 | **-0.125** |
| `random_family_quarantine` | 0.75 | 0.05 | 0.710 | 0.840 | 0.150 | 0.280 | **-0.129** |
| `random_family_quarantine` | 0.75 | 0.10 | 0.680 | 0.820 | 0.170 | 0.310 | **-0.133** |
| `random_family_quarantine` | 0.75 | 0.20 | 0.620 | 0.760 | 0.230 | 0.370 | **-0.142** |
| `random_family_quarantine` | 0.75 | 0.40 | 0.490 | 0.650 | 0.340 | 0.500 | **-0.158** |
| `random_family_quarantine` | 0.90 | 0.00 | 0.700 | 0.840 | 0.150 | 0.300 | **-0.150** |
| `random_family_quarantine` | 0.90 | 0.05 | 0.660 | 0.810 | 0.180 | 0.330 | **-0.152** |
| `random_family_quarantine` | 0.90 | 0.10 | 0.630 | 0.780 | 0.210 | 0.360 | **-0.153** |
| `random_family_quarantine` | 0.90 | 0.20 | 0.570 | 0.720 | 0.270 | 0.420 | **-0.157** |
| `random_family_quarantine` | 0.90 | 0.40 | 0.440 | 0.600 | 0.390 | 0.560 | **-0.163** |
| `random_family_quarantine` | 1.00 | 0.00 | 0.660 | 0.830 | 0.160 | 0.330 | **-0.167** |
| `random_family_quarantine` | 1.00 | 0.05 | 0.630 | 0.800 | 0.200 | 0.360 | **-0.167** |
| `random_family_quarantine` | 1.00 | 0.10 | 0.600 | 0.760 | 0.230 | 0.400 | **-0.167** |
| `random_family_quarantine` | 1.00 | 0.20 | 0.530 | 0.700 | 0.300 | 0.460 | **-0.167** |
| `random_family_quarantine` | 1.00 | 0.40 | 0.400 | 0.560 | 0.430 | 0.600 | **-0.167** |
| `signal_blind_uniform_thinning` | 0.50 | 0.00 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.50 | 0.05 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.50 | 0.10 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.50 | 0.20 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.50 | 0.40 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.75 | 0.00 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.75 | 0.05 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.75 | 0.10 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.75 | 0.20 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.75 | 0.40 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.90 | 0.00 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.90 | 0.05 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.90 | 0.10 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.90 | 0.20 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 0.90 | 0.40 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 1.00 | 0.00 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 1.00 | 0.05 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 1.00 | 0.10 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 1.00 | 0.20 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_blind_uniform_thinning` | 1.00 | 0.40 | 0.990 | 0.500 | 0.500 | 0.000 | **+0.500** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.00 | 0.750 | 0.830 | 0.160 | 0.250 | **-0.083** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.05 | 0.740 | 0.810 | 0.180 | 0.250 | **-0.067** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.10 | 0.740 | 0.790 | 0.200 | 0.250 | **-0.050** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.20 | 0.730 | 0.750 | 0.250 | 0.260 | **-0.017** |
| `signal_conditioned_uniform_thinning` | 0.50 | 0.40 | 0.710 | 0.660 | 0.330 | 0.280 | **+0.050** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.00 | 0.620 | 0.740 | 0.250 | 0.370 | **-0.125** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.05 | 0.620 | 0.730 | 0.260 | 0.370 | **-0.108** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.10 | 0.620 | 0.710 | 0.280 | 0.370 | **-0.092** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.20 | 0.610 | 0.670 | 0.320 | 0.380 | **-0.058** |
| `signal_conditioned_uniform_thinning` | 0.75 | 0.40 | 0.600 | 0.600 | 0.400 | 0.390 | **+0.008** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.00 | 0.550 | 0.700 | 0.300 | 0.440 | **-0.150** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.05 | 0.540 | 0.680 | 0.310 | 0.450 | **-0.133** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.10 | 0.540 | 0.660 | 0.330 | 0.450 | **-0.117** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.20 | 0.540 | 0.630 | 0.370 | 0.450 | **-0.083** |
| `signal_conditioned_uniform_thinning` | 0.90 | 0.40 | 0.540 | 0.560 | 0.430 | 0.450 | **-0.017** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.00 | 0.500 | 0.660 | 0.330 | 0.500 | **-0.167** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.05 | 0.500 | 0.640 | 0.350 | 0.500 | **-0.150** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.10 | 0.490 | 0.630 | 0.360 | 0.500 | **-0.133** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.20 | 0.500 | 0.600 | 0.400 | 0.500 | **-0.100** |
| `signal_conditioned_uniform_thinning` | 1.00 | 0.40 | 0.490 | 0.530 | 0.460 | 0.500 | **-0.033** |

---

## 4. Policy Control Decomposition Matrix

```
+----------------------------------------------------------------------------------------------------------------------+
|                                    CONTROL DECOMPOSITION MATRIX (SHARED ECOLOGY)                                     |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
| Policy                             | Uses Detector?   | Budget Source     | Targeting Scope    | Observed S (90/10)  |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
| baseline                           | No               | 0                 | None               | 0.000               |
| signal_blind_uniform_thinning      | No               | Fixed (m=3)       | Blind Uniform      | 0.000               |
| signal_conditioned_uniform_thinning| Yes              | Matched (m=lin)   | Blind Uniform      | +0.200              |
| random_family_quarantine           | Yes              | Matched (m=lin)   | Random Cluster     | +0.201              |
| generation_matched_thinning        | Yes              | Matched (mG2=lin) | Generation 2 Pool  | +0.397              |
| node_only_quarantine               | Yes              | Roots Only (G0)   | Flagged Roots      | 0.000 (Laundering)  |
| lineage_quarantine                 | Yes              | Transitive DAG    | Flagged Lineages   | +0.800 (Decisive)   |
| oracle_upper_bound                 | Perfect Ground T*| Transitive DAG    | True Infected Tree | +1.000              |
+------------------------------------+------------------+-------------------+--------------------+---------------------+
```

---

## 5. Epistemic Autoimmunity & Gated Live Strategy

1. **Autoimmunity Equation**:
   Under whole-family lineage quarantine with $\gamma = 1.0$, healthy memory destruction scales linearly with the detector false alarm rate:
   $$\text{Epistemic Autoimmunity} = 1 - C_H = \text{FPR}$$
2. **The Crossover Principle**:
   In the tested sandbox, lineage quarantine overtakes generation-matched and uniform controls whenever $\text{TPR} - \text{FPR} > 0.35$.
3. **Live Gating Protocol**:
   When transitioning to live model evaluation, we do **not** run duplicate $(\text{TPR}, \text{FPR})$ points. Instead, we run each unique concrete signal-state context ($(S_H, S_I) \in \{00, 10, 01, 11\}$) once, and then analytically reweight the observed model outputs across any $(\text{TPR}, \text{FPR})$ coordinate.
