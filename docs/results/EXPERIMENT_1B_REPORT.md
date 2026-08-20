# Experiment 1B-A1 Final Report — Controlled Balanced Exposure Dose-Response & The Uniform-Thinning Frontier

**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Experiment:** Experiment 1B-A1 (Counterbalanced Exposure Dose-Response & Answer Coverage)  
**Status:** **FROZEN & VERIFIED**  
**Date:** 2026-08-20  
**Model Under Test:** `gemma3:12b` (Ollama, SHA256 dynamic digest captured)  
**Assay Environment:** Ecology C (3 matched competing rules per depth) + Schema v2 (explicit contract)  
**Database:** `gene_exp1b_exposure_v2_20260820_022505.db` (240 individual model invocations = 120 matched clean/infected call pairs across 4 counterbalanced micro-worlds)  

---

## 1. Executive Summary

Experiment 1B-A1 experimentally investigates the physical transmission factorization of persistent corrupted memory:

$$R_S(p) = X(p) \times \hat{\tau}_S \times \hat{W}$$

By varying retrieval contact probability $p \in \{0.0, 0.25, 0.50, 0.75, 1.0\}$ using **counterbalanced task-identity exposure masks** across 4 procedural micro-worlds (rotating which cognitive predicate is exposed/masked per world to eliminate task-type confounding), GENE evaluated:
1. **Factorization Invariance**: Whether conditional epistemic transmissibility ($\hat{\tau}_S$) remains invariant when contact rate ($X$) is systematically suppressed.
2. **Empirical Replacement Recovery**: The architecture-implied replacement boundary ($p_c = 0.50 \implies R_S = 1.00$).
3. **The Uniform-Thinning Frontier ($R_S = 2 C_{\text{clean}}$)**: The clean answer coverage ($C_{\text{clean}}$) trade-off under reject-option/selective classification, establishing the baseline cost of indiscriminate memory thinning.
4. **De-Novo / Spontaneous Mutation Separation ($\mu_{\text{de\_novo}}$)**: Explicit tracking of unexposed error rates to guarantee that unprompted epistemic errors are never conflated with transmitted lineage infection.

### Key Empirical Findings
1. **Factorization Invariance ($\hat{\tau}_S = 1.00$ Everywhere Estimable)**:
   Across all exposure conditions ($p > 0$), conditional epistemic transmissibility was **strictly invariant at $\hat{\tau}_S = 1.00$** ($40 / 40$ pooled exposed opportunities generated locally derivable infected children: $4/4$ at $p=0.25$, $8/8$ at $p=0.50$, $12/12$ at $p=0.75$, $16/16$ at $p=1.00$). Transmission scaled strictly as a linear contact process: $R_{\text{trans}}(p) = X(p) \times \hat{\tau}_S \times \hat{W} = 2p$.
2. **Empirical Replacement Boundary ($p_c = 0.50$)**:
   The architecture-implied critical boundary at $p = 0.50$ was experimentally recovered ($X = 1.00 \implies R_{\text{trans}} = 1.00$). Under Galton–Watson i.i.d. branching assumptions, $p < 0.50$ defines a sub-replacement one-step regime ($R_{\text{trans}} < 1.0$), while $p > 0.50$ defines a supercritical regime ($R_{\text{trans}} > 1.0$).
3. **The Uniform-Thinning Frontier ($R_{\text{trans}} = 2 C_{\text{clean}}$)**:
   Indiscriminately thinning memory access reduces clean answer coverage proportionally: $C_{\text{clean}}(p) = p$. Under reject-option classification, unexposed clean tasks cleanly abstained ($100\%$ epistemic safety), but answer availability dropped linearly.
4. **Zero Spontaneous / De-Novo Mutations & Zero Unsupported Output ($\mu_{\text{de\_novo}} = 0.00$, $\mu_{\text{unsupp}} = 0.00$)**:
   Across all 40 unexposed opportunities ($16$ at $p=0.0$, $12$ at $p=0.25$, $8$ at $p=0.50$, $4$ at $p=0.75$), **zero false concrete claims were emitted without prompt exposure** ($\mu_{\text{de\_novo}} = 0 / 40 = 0.0\%$) and **zero ungrounded concrete outputs of any kind were generated** ($\mu_{\text{unsupp}} = 0 / 40 = 0.0\%$). Every unexposed task cleanly abstained (`UNKNOWN`) with state vector $(0, 0, 1, 1, 1)$, proving that downstream contamination was $100\%$ causal and lineage-transmitted ($R_{\text{total-corruption}} = R_{\text{trans}} = 2p$).
5. **Ancestral Allele Fidelity ($\hat{F}_2 = 1.00$)**:
   Whenever contact occurred, ancestral symbol identity was preserved across two generational transformations without observable drift ($\hat{F}_2 = 40/40 = 1.00$).

---

## 2. Experimental Ledger & Dose-Response Summary

**Database:** `gene_exp1b_exposure_v2_20260820_022505.db` (240 invocations = 120 matched pairs)

| Dose ($p$) | Contact Rate $X(p)$ | Transmissibility $\hat{\tau}_S$ | Admission $\hat{W}_{\text{hat}}$ | $R_{\text{trans}}(p)$ | $R_{\text{total}}(p)$ | Clean Coverage $C_{\text{clean}}(p)$ | De-Novo $\mu_{\text{de\_novo}}$ | Unsupp $\mu_{\text{unsupp}}$ | Fidelity $\hat{F}_2$ | Epidemic Regime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$p = 0.00$** | $X = 0.00$ | N/A | N/A ($W_{\text{pol}}=1.0$) | **$0.00$** | **$0.00$** | **$0.0\%$** ($0/16$) | **$0.0\%$** ($0/16$) | **$0.0\%$** ($0/16$) | N/A | **Sub-replacement** ($R < 1$) |
| **$p = 0.25$** | $X = 0.50$ | **$1.00$** ($4/4$) | **$1.00$** ($4/4$) | **$0.50$** | **$0.50$** | **$25.0\%$** ($4/16$) | **$0.0\%$** ($0/12$) | **$0.0\%$** ($0/12$) | **$1.00$** | **Sub-replacement** ($R < 1$) |
| **$p = 0.50$** | $X = 1.00$ | **$1.00$** ($8/8$) | **$1.00$** ($8/8$) | **$1.00$** | **$1.00$** | **$50.0\%$** ($8/16$) | **$0.0\%$** ($0/8$) | **$0.0\%$** ($0/8$) | **$1.00$** | **Critical Mean** ($R = 1$) |
| **$p = 0.75$** | $X = 1.50$ | **$1.00$** ($12/12$) | **$1.00$** ($12/12$) | **$1.50$** | **$1.50$** | **$75.0\%$** ($12/16$) | **$0.0\%$** ($0/4$) | **$0.0\%$** ($0/4$) | **$1.00$** | **Supercritical** ($R > 1$) |
| **$p = 1.00$** | $X = 2.00$ | **$1.00$** ($16/16$) | **$1.00$** ($16/16$) | **$2.00$** | **$2.00$** | **$100.0\%$** ($16/16$) | **$0.0\%$** ($0/0$) | **$0.0\%$** ($0/0$) | **$1.00$** | **Supercritical** ($R > 1$) |
| **POOLED** | — | **$1.00$** ($40/40$) | **$1.00$** ($40/40$) | — | — | — | **$0.0\%$** ($0/40$) | **$0.0\%$** ($0/40$) | **$1.00$** ($40/40$) | — |

---

## 3. Mathematical Analysis: The Uniform-Thinning Frontier

```text
       Reproduction R_S vs Clean Coverage C_clean
 2.0 ┤                                        ● R_S = 2.00, C = 100%
     │                                   ●
 1.5 ┤                             ● R_S = 1.50, C = 75%
     │                       ●
 1.0 ┤                 ● [Replacement Boundary: R_S = 1.00, C = 50%]
     │           ●
 0.5 ┤     ● R_S = 0.50, C = 25%
     │
 0.0 ┼─────● R_S = 0.00, C = 0%
   p = 0.00    0.25    0.50    0.75    1.00
```

### 3.1 Indiscriminate Retrieval Trade-off
Under uniform exposure throttling without lineage awareness:
$$R_S = 2 C_{\text{clean}}$$

- To achieve sub-replacement decay ($R_S < 1.0$), uniform thinning must reduce exposure below $p < 0.50$.
- Under the reject-option framework, the model remains $100\%$ epistemically safe (abstaining to `UNKNOWN`), but answer coverage drops to $C_{\text{clean}} < 50\%$.
- In this controlled single-parent assay, indiscriminate thinning suppresses misinformation only by proportionally reducing useful memory derivation.

### 3.2 The Target for Experiment 1B-C (Lineage-Aware Selective Immunity)
The explicit scientific goal of **Experiment 1B-C** is to **bend the frontier downward**:

$$\text{Uniform Thinning: } C_{\text{clean}} = 0.75 \implies R_S = 1.50$$
$$\text{Selective Lineage Immunity: } C_{\text{clean}} = 0.75 \implies R_S \le 0.40$$

Using ancestry metadata (provenance, authority, verification tags, cluster depth) rather than global truth oracles, selective filtering aims to suppress infected reproduction while preserving clean answer coverage.

---

## 4. Next Sequence: Experiment 1B-A2, 1B-B, & 1B-C

1. **Experiment 1B-A2 (Branching Process Simulation & Empirical Validation)**:
   - For $K \sim \text{Binomial}(2, p)$, ultimate extinction probability is $q = 1.0$ for $p \le 0.50$, and $q = (\frac{1-p}{p})^2$ for $p > 0.50$ (e.g. $q = 44.4\%$ at $p=0.60$).
   - Validate finite-generation theoretical curves ($G_3, G_4$) via hybrid live/simulation model to observe jackpot lineages near criticality.
2. **Experiment 1B-B (Retrieval Competition & Dynamic Feedback Loops)**:
   - Decouple contact rate $X$ from experimental assignment by introducing candidate retrieval pools with clutter.
   - Test whether infected descendants increase their own future retrieval probability (preferential attachment / frequency-dependent fitness).
3. **Experiment 1B-C (Lineage-Aware Filtering with Equal-Budget Controls)**:
   - Deploy non-oracle lineage filters (provenance chains, trust propagation) compared against equal-budget top-$k$ / random controls to break the uniform-thinning frontier.
