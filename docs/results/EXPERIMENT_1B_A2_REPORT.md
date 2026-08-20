# Experiment 1B-A2 Final Report — Multi-Generation Stochastic Branching & Extinction Dynamics

**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Experiment:** Experiment 1B-A2 (Galton–Watson Stochastic Branching Process Simulation)  
**Status:** **VERIFIED & FROZEN**  
**Date:** 2026-08-20  
**Simulated Realizations:** 150,000 independent family trees (25,000 trials per condition across $G_1 \to G_4$)  

---

## 1. Executive Summary & Core Theoretical Insight

Experiment 1B-A1 established the single-step mechanism ($R_S = 2p$) under deterministic contact scheduling. Experiment 1B-A2 investigates the **stochastic multi-generation family-tree dynamics** ($G_1 \to G_4$) under the Galton–Watson branching model with offspring distribution $K \sim \text{Binomial}(2, p)$.

### Key Mathematical & Empirical Findings:
1. **Supercritical Mean Does Not Guarantee Survival ($p=0.60 \implies q_\infty = 44.4\%$)**:
   At $p = 0.60$, the mean reproduction number is supercritical ($R_S = \mu = 1.20 > 1.0$). However, solving the probability generating function fixed point equation $s = ((1-p) + ps)^2$ proves that **$44.4\%$ of all supercritical lineages die out purely from stochastic sampling** ($q_\infty = (\frac{0.4}{0.6})^2 = \frac{4}{9}$). Simulated empirical extinction matches theory ($q_4 = 33.6\% \to q_\infty = 44.4\%$).
2. **Critical Martingale Property ($p = 0.50 \implies R_S = 1.00$)**:
   At the replacement boundary ($p = 0.50$), the mean population size is strictly conserved across generations ($\mathbb{E}[Z_g] = 1.00$). However, extinction steadily climbs toward certainty ($q_1 = 25.0\% \to q_2 = 39.1\% \to q_3 = 48.3\% \to q_4 = 55.3\% \to q_\infty = 100\%$). Surviving lineages conditionally expand ($\mathbb{E}[Z_4 \mid Z_4 > 0] = 2.24$) to balance the extinct majority.
3. **Jackpot Lineage Emergence ($p \ge 0.75$)**:
   In strongly supercritical regimes ($p = 0.75, R_S = 1.50$), extinction drops to $q_\infty = 11.1\%$, with $17.8\%$ of lineages achieving perfect maximal capacity at $G_2$ ($Z_2 = 4$), and surviving lineages expanding exponentially toward capacity at $G_4$ (surviving mean $= 5.66$; full $G_4$ capacity $Z_4 = 16$ occurs in $0.0179\%$ of trees).

---

## 2. Multi-Generation Stochastic Ledger

| Dose ($p$) | Mean Offspring $\mu = 2p$ | Regime | Asymptotic Extinction $q_\infty$ | $G_1$ Extinction ($q_1$) | $G_2$ Extinction ($q_2$) | $G_3$ Extinction ($q_3$) | $G_4$ Extinction ($q_4$) | $G_4$ Surviving Mean Pop | $G_2$ Jackpot Rate |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$p = 0.25$** | **0.50** | **Subcritical** | **100.0%** | 56.1% | 79.2% | 90.0% | 95.2% | 1.28 | 0.0% |
| **$p = 0.40$** | **0.80** | **Subcritical** | **100.0%** | 36.2% | 55.3% | 67.5% | 75.7% | 1.67 | 0.5% |
| **$p = 0.50$** | **1.00** | **Critical** | **100.0%** | 25.4% | 39.2% | 48.4% | 55.1% | 2.21 | 1.6% |
| **$p = 0.60$** | **1.20** | **Supercritical** | **44.4%** | 16.3% | 24.8% | 30.1% | 33.7% | 3.10 | 4.5% |
| **$p = 0.75$** | **1.50** | **Supercritical** | **11.1%** | 6.4% | 9.1% | 10.2% | 10.7% | 5.66 | 17.8% |
| **$p = 1.00$** | **2.00** | **Supercritical** | **0.0%** | 0.0% | 0.0% | 0.0% | 0.0% | 16.00 | 100.0% |

---

## 3. Mathematical Foundations: The Generating Function

For offspring distribution $K \sim \text{Binomial}(2, p)$, the probability generating function (PGF) is:

$$G(s) = \sum_{k=0}^2 P(K=k) s^k = (1-p)^2 + 2p(1-p)s + p^2 s^2 = ((1-p) + ps)^2$$

The extinction probability at generation $g$ is the $g$-fold functional composition:
$$q_g = G_g(0) = G(G_{g-1}(0))$$

The ultimate extinction probability $q_\infty$ solves the fixed point $s = G(s)$:
$$s = ((1-p) + ps)^2 \implies (s-1)\left(p^2 s - (1-p)^2\right) = 0$$

$$q_\infty = \begin{cases} 1.0 & \text{if } p \le 0.50 \\ \left(\frac{1-p}{p}\right)^2 & \text{if } p > 0.50 \end{cases}$$

```text
         Asymptotic Lineage Extinction q_inf vs Contact Probability p
 100% ┼───────────────● [Critical Boundary: p = 0.50, q = 100%]
      │               ╲
  80% ┤                ╲
      │                 ╲
  60% ┤                  ╲
      │                   ● [p = 0.60, R = 1.20, q = 44.4%]
  40% ┤                    ╲
      │                     ╲
  20% ┤                      ● [p = 0.75, R = 1.50, q = 11.1%]
      │                       ╲
   0% ┼────────────────────────● [p = 1.00, R = 2.00, q = 0%]
     p = 0.00   0.25    0.50    0.60    0.75    1.00
```

---

## 4. Bridge to Experiment 1B-B (Endogenous Retrieval Dynamics)

In 1B-A2, each node has an independent probability $p$ of exposure. In **Experiment 1B-B**, contact probability $X$ is no longer an environmental constant—it is generated dynamically by a vector/lexical retrieval engine.

Surviving jackpot lineages expand their total retrieval surface area ($N_{\text{descendants}} \propto 2^g$), creating a **positive feedback loop** where reproduction increases subsequent contact probability ($X_g = f(Z_{g-1})$). This evolutionary dynamic will be directly assayed in Experiment 1B-B.
