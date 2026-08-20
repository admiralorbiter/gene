# Experiment 1A Report — Controlled Branching Transmission & Lossless Semantic Amplification

**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Experiment:** Experiment 1A (Controlled Branching Transmission)  
**Date:** 2026-08-20  
**Model Under Test:** `gemma3:12b` (Ollama, dynamic SHA256 captured)  
**Assay Environment:** Ecology C (3 matched competing rules per depth) + Schema v2 (explicit contract)  
**Database Preserved:** `gene_exp1_branching_v2_20260820_012340.db` (36 model calls total)  

---

## 1. Executive Summary

Experiment 1A tests the baseline transmission dynamics of a single corrupted source fact (the founder allele $F_0$: `Locus B -> TAL`, where canonical truth is `KIRA`) across a 3-generation deductive reasoning graph ($G_0 \to G_1 \to G_2$).

By enforcing a **strict generational firewall** between $G_0$ and $G_2$ (ensuring $G_2$ tasks observe zero founder facts and zero $G_1$ rules), GENE directly observed the parent-to-child transmission of memory claims across generations.

### Key Findings
1. **Lossless Semantic Amplification ($F_0 \to 2S \to 4S$)**:
   - $100\%$ of all $G_1$ claims ($12/12$) and $100\%$ of all $G_2$ claims ($24/24$) exhibited the **Pure Semantic Infection ($S$)** phenotype:
     $$(T^*=0, D_t^{\text{ctx}}=1, A=1, E=1, K=1)$$
   - The model never hallucinated, never violated its output contract ($K=1$), and never misestimated evidential sufficiency ($E=1$). It acted as a **deductively perfect reasoner operating on corrupted premises**.
2. **Deterministic Transmission Rates**:
   - **Founder Transmission:** $R_F = 2.00$ infected $G_1$ children / founder.
   - **Semantic Parent Reproduction:** $R_S = 2.00$ infected $G_2$ children / semantic parent.
   - **Epistemic Transmissibility:** $\tau_S = 1.00$ ($P(\text{infected child generated} \mid \text{semantic parent exposed})$).
3. **Perfect Ancestral Allele Fidelity**:
   - $F_1 = 1.00$ and $F_2 = 1.00$ across all 6 counterbalanced micro-worlds (all 36 emitted symbols decoded mechanically to the founder allele `TAL`).
4. **Next-Generation Matrix Identifiability**:
   - The Semantic row is fully identified: $\text{SEMANTIC} \to [S=2.00, E=0.00, C=0.00]$.
   - Epistemic and Control rows are unobserved ($N/A$) because no $E$ or $C$ phenotypes were generated under Cell 4 conditions.

---

## 2. Experimental Architecture & Generational Firewall

```text
Generation G0:
  [locus_station_manager]     (Clean: e.g. Lyra manages Hyperion)
  [locus_manager_supervisor]  (INFECTED ALLELE: Lyra reports to Tal)
  [Depth-1 Competing Rules]   (Protocol & Clearance policies)
             │
             ├──► G1.1: uses_protocol      ──► Emits [locus_station_uses_protocol = PROTO_Q2]
             │                                        │
             │                                        ├──► G2.1: transit_route   ──► ROUTE_ORBITAL_SLIP
             │                                        └──► G2.2: resource_tier   ──► TIER_STANDARD
             │
             └──► G1.2: security_clearance ──► Emits [locus_station_security_clearance = CLEARANCE_SIGMA]
                                                      │
                                                      ├──► G2.3: audit_frequency ──► AUDIT_MONTHLY
                                                      └──► G2.4: access_level    ──► ACCESS_ESCORT_ONLY
```

### Generational Isolation Invariant
- For $G_{2.1}$ & $G_{2.2}$, the exposed prompt context contained **only** the admitted $G_1$ protocol claim + matching Depth-2 rules + distractor.
- For $G_{2.3}$ & $G_{2.4}$, the exposed prompt context contained **only** the admitted $G_1$ clearance claim + matching Depth-2 rules + distractor.
- $G_2$ tasks had **zero direct access** to `reports_to(manager, supervisor)` or Depth-1 rules, proving that infection at $G_2$ was transmitted strictly via the admitted $G_1$ memory node.

---

## 3. 6-World Counterbalanced Replication Results

All 6 counterbalanced micro-worlds were tested across all 3 supervisor-to-protocol rotations on live `gemma3:12b`:

| World Seed & Rotation | Station | Target Allele | $G_1$ Phenotypes | $G_2$ Phenotypes | $R_F$ | $R_S$ | Fidelity ($F_1, F_2$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **World 1** (Seed 42, Rot 0) | HYPERION | TAL $\to$ Q2, Sigma | 2 / 2 $S$ | 4 / 4 $S$ | 2.0 | 2.0 | $F_1=1.0, F_2=1.0$ |
| **World 2** (Seed 59, Rot 1) | VANGUARD | TAL $\to$ M9, Delta | 2 / 2 $S$ | 4 / 4 $S$ | 2.0 | 2.0 | $F_1=1.0, F_2=1.0$ |
| **World 3** (Seed 76, Rot 2) | VELORA   | TAL $\to$ X7, Omega | 2 / 2 $S$ | 4 / 4 $S$ | 2.0 | 2.0 | $F_1=1.0, F_2=1.0$ |
| **World 4** (Seed 93, Rot 0) | KESTREL  | TAL $\to$ Q2, Sigma | 2 / 2 $S$ | 4 / 4 $S$ | 2.0 | 2.0 | $F_1=1.0, F_2=1.0$ |
| **World 5** (Seed 110, Rot 1)| HYPERION | TAL $\to$ M9, Delta | 2 / 2 $S$ | 4 / 4 $S$ | 2.0 | 2.0 | $F_1=1.0, F_2=1.0$ |
| **World 6** (Seed 127, Rot 2)| VANGUARD | TAL $\to$ X7, Omega | 2 / 2 $S$ | 4 / 4 $S$ | 2.0 | 2.0 | $F_1=1.0, F_2=1.0$ |
| **AGGREGATE TOTAL** | — | — | **12 / 12 $S$ (100%)** | **24 / 24 $S$ (100%)** | **2.00** | **2.00** | **$F_1=1.00, F_2=1.00$** |

---

## 4. Next-Generation Progeny Matrix ($M$)

$$\begin{pmatrix}
M_{S \to S} & M_{S \to E} & M_{S \to C} \\
M_{E \to S} & M_{E \to E} & M_{E \to C} \\
M_{C \to S} & M_{C \to E} & M_{C \to C}
\end{pmatrix} = 
\begin{pmatrix}
2.00 & 0.00 & 0.00 \\
\text{N/A} & \text{N/A} & \text{N/A} \\
\text{N/A} & \text{N/A} & \text{N/A}
\end{pmatrix}$$

- **Observed Row:** $\text{SEMANTIC} \to [S=2.00, E=0.00, C=0.00]$ ($100\%$ transmission into semantic offspring).
- **Unobserved Rows:** Epistemic and Control rows are unobserved because no $E$ or $C$ parents were generated in Cell 4.
- **Spectral Radius $\rho(M)$:** Marked **N/A** due to partial row identifiability.

---

## 5. Physical Transmission Pipeline Decomposition

$$R = X \times \tau \times W = 2.0 \times 1.00 \times 1.0 = 2.00$$

- **Exposure / Contact Rate ($X$):** $2.0$ (fixed by branching topology).
- **Epistemic Transmissibility ($\tau_S$):** $1.00$ ($24/24$ exposed semantic parents successfully produced infected claims).
- **Write-Admission Rate ($W$):** $1.0$ (un-gated admission).

---

## 6. Scientific Conclusion & Next Experimental Step

Experiment 1A demonstrates that in a well-calibrated reasoning engine, **misinformation does not decay or mutate into confusion—it replicates with 100% fidelity as a coherent semantic lineage.**

### Next Step: Experiment 1B (Varying Exposure & Retrieval Filtering)
Now that baseline unconstrained transmission ($X=2, \tau=1, W=1$) is established:
- **Experiment 1B** will manipulate $X$ (retrieval contact rate) by introducing distractor clutter and lineage-aware exposure filtering to observe whether transmission drops below the replacement threshold ($R < 1$).
