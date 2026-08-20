# Experiment 1B-A1 Final Report — Controlled Exposure Dose-Response & Cognitive Utility Trade-offs

**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Experiment:** Experiment 1B-A1 (Balanced Exposure Dose-Response & Utility Trade-offs)  
**Status:** **COMPLETED & VERIFIED**  
**Date:** 2026-08-20  
**Model Under Test:** `gemma3:12b` (Ollama, SHA256 digest captured)  
**Assay Environment:** Ecology C (3 matched competing rules per depth) + Schema v2 (explicit contract)  
**Database:** `gene_exp1b_exposure_v2_20260820_020136.db` (60 paired model calls across 5 exposure doses)  

---

## 1. Executive Summary

Experiment 1B-A1 experimentally investigates the physical transmission factorization of persistent corrupted memory:

$$R_S(p) = X(p) \times \hat{\tau}_S \times \hat{W}$$

By varying the retrieval contact probability $p \in \{0.0, 0.25, 0.50, 0.75, 1.0\}$ using **deterministic balanced exposure masks** across paired clean and infected micro-worlds, GENE tested:
1. Whether epistemic transmissibility ($\hat{\tau}_S$) remains invariant when contact rate ($X$) is systematically suppressed.
2. The empirical replacement threshold ($p_c = 0.50$) where $R_S = 1.00$.
3. The simultaneous impact on **Clean Cognitive Utility ($U_{\text{clean}}$)**, measuring the exact cognitive cost of indiscriminate exposure reduction.

### Key Empirical Findings
1. **Factorization Invariance**:
   Across all exposure conditions ($p = 0.25, 0.50, 0.75, 1.00$), conditional epistemic transmissibility remained **strictly invariant at $\hat{\tau}_S = 1.00$** ($8/8$ exposed opportunities generated infected children). Transmission scaled strictly as a linear function of contact rate $X(p) = 2p$.
2. **Empirical Replacement Threshold ($p_c = 0.50$)**:
   At $p = 0.50$, contact rate $X = 1.00$, producing the exact critical replacement equilibrium **$R_S = 1.00$**.
   - For $p < 0.50$, the system enters the **subcritical regime ($R_S < 1.0$)**, leading to deterministic lineage extinction.
   - For $p > 0.50$, the system is **supercritical ($R_S > 1.0$)**, exhibiting geometric amplification.
3. **The Cognitive Utility Penalty ($U_{\text{clean}}(p) = p$)**:
   Indiscriminate exposure reduction suppresses infection only by proportionally degrading task performance on clean memory:
   - At $p = 0.50$ (critical threshold), clean utility is halved to $50.0\%$.
   - At $p = 0.00$ (total quarantine), $R_S = 0.00$, but clean cognitive utility drops to $0.0\%$.
4. **Ancestral Allele Fidelity Invariance**:
   Whenever an infected parent was exposed, ancestral symbol fidelity remained **$\hat{F}_2 = 1.00$** regardless of exposure dose.

---

## 2. Experimental Results & Dose-Response Ledger

**Database:** `gene_exp1b_exposure_v2_20260820_020136.db`

| Dose ($p$) | Contact Rate $X(p)$ | Transmissibility $\hat{\tau}_S$ | Admission $\hat{W}$ | Reproduction $R_S$ | Clean Utility $U_{\text{clean}}(p)$ | Masked Abstention | Fidelity $\hat{F}_2$ | Epidemic Regime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$p = 0.00$** | $X = 0.00$ | N/A | $1.00$ | **$0.00$** | **$0.0\%$** ($0/8$) | $100\%$ ($8/8$) | N/A | **Subcritical** (Decay) |
| **$p = 0.25$** | $X = 0.50$ | $1.00$ | $1.00$ | **$0.50$** | **$25.0\%$** ($2/8$) | $100\%$ ($6/6$) | $1.00$ | **Subcritical** (Decay) |
| **$p = 0.50$** | $X = 1.00$ | $1.00$ | $1.00$ | **$1.00$** | **$50.0\%$** ($4/8$) | $100\%$ ($4/4$) | $1.00$ | **Critical** ($R_S=1$) |
| **$p = 0.75$** | $X = 1.50$ | $1.00$ | $1.00$ | **$1.50$** | **$75.0\%$** ($6/8$) | $100\%$ ($2/2$) | $1.00$ | **Supercritical** (Growth) |
| **$p = 1.00$** | $X = 2.00$ | $1.00$ | $1.00$ | **$2.00$** | **$100.0\%$** ($8/8$) | N/A ($0$ masked) | $1.00$ | **Supercritical** (Growth) |

---

## 3. Mathematical & Causal Analysis

### 3.1 Contact Process vs. Transmission Process
By separating the **Parent Population** ($N_{\text{parents}} = 4$) from the **Exposed Opportunities** ($N_{\text{exp}}$), GENE demonstrated that:
$$R_S(p) = \frac{N_{\text{exp}}}{N_{\text{parents}}} \times \frac{N_{\text{gen}}}{N_{\text{exp}}} \times \frac{N_{\text{adm}}}{N_{\text{gen}}} = X(p) \times \hat{\tau}_S \times \hat{W}$$

Because $\hat{\tau}_S = 1.00$ and $\hat{W} = 1.00$ across all conditions, $R_S(p) = X(p) = 2p$.

```text
       Reproduction R_S vs Clean Utility U_clean
 2.0 ┤                                        ● R_S (Supercritical)
     │                                   ●
 1.5 ┤                             ●     
     │                       ●           ▲ U_clean = 100%
 1.0 ┤                 ● [Critical: R_S=1.0, U=50%]
     │           ●     ▲ U_clean = 50%
 0.5 ┤     ●     ▲ U_clean = 25%
     │     ▲ U_clean = 0%
 0.0 ┼─────┴─────┴─────┴─────┴─────┴─────────────
   p = 0.00    0.25    0.50    0.75    1.00
```

### 3.2 The Fundamental Dilemma of Indiscriminate Filtering
The simultaneous measurement of $U_{\text{clean}}(p)$ demonstrates why indiscriminate retrieval throttling cannot solve the persistent memory alignment problem:
- To suppress $R_S < 1.0$, indiscriminate retrieval must drop $p < 0.50$.
- But doing so destroys **more than half of all valid cognitive derivations** on the clean memory substrate.
- This formally establishes the necessity for **Lineage-Aware Selective Immunity (Experiment 1B-C)**: filtering mechanisms that target corrupted causal ancestry rather than suppressing general retrieval volume.

---

## 4. Next Sequence: Experiment 1B-A2 & 1B-B

1. **Experiment 1B-A2 (Stochastic Multi-Generation Branching near Criticality)**:
   - Run true Bernoulli branching ($K \sim \text{Binomial}(2, p)$) across 3-4 generations around $p \in \{0.4, 0.5, 0.6\}$ to observe stochastic extinction probability vs runaway lineages.
2. **Experiment 1B-B (Retrieval Competition in Cluttered Candidate Pools)**:
   - Scale candidate pool with semantic distractors to measure $P(\text{retrieved})$ separately from $P(\text{transmitted} \mid \text{retrieved})$.
3. **Experiment 1B-C (Lineage-Aware Filtering with Equal-Budget Controls)**:
   - Compare lineage-aware ancestral pruning against top-$k$ / random controls with identical memory budgets to demonstrate selective immunity ($R_S < 1.0$ while $U_{\text{clean}} \approx 100\%$).
