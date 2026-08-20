# Experiment Card — Track L: Independence Laundering & Inflated Diversity

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** As an ancestral observation reproduces through successive downstream generations (paraphrasing, summarization, metadata stripping), naive independence estimators progressively inflate the apparent effective root count ($\widehat{N}_{\text{eff}}: 1.0 \leadsto 4.0$) even though true root diversity remains strictly $N_{\text{true}} = 1.0$.
- **Why It Matters:** Independence laundering is the evolutionary mechanism that enables epistemic monoculture. Tracking how semantic reproduction launders single-source provenance into manufactured consensus connects lineage epidemiology directly to multi-agent memory reliability.

## 2. Experimental Transformation Cascade
Starting from a single ground-truth observation $R_1$:
1. **$G_0$ Root Generation:** $R_1$ authored. ($N_{\text{true}} = 1.0$).
2. **$G_1$ Reproduction (Paraphrasing):** Four parallel agent nodes ($M_1, M_2, M_3, M_4$) rephrase $R_1$ with citation metadata.
3. **$G_2$ Reproduction (Summarization & Rewriting):** Nodes $M_1..M_4$ are summarized into synthetic secondary reports ($S_1..S_4$) where explicit parent pointers are omitted.
4. **$G_3$ Downstream Adjudication:** An evaluator receives $\{S_1, S_2, S_3, S_4\}$ and estimates evidence independence.

```
                     R_1 (True Root, N_true = 1)
                     ┌────┬────┬────┐
                     ▼    ▼    ▼    ▼
                    M_1  M_2  M_3  M_4  (G1: Cited Paraphrase)
                     │    │    │    │
                     ▼    ▼    ▼    ▼
                    S_1  S_2  S_3  S_4  (G2: Summarized / Laundering)
                     └────┴────┴────┘
                            │
                            ▼
              Downstream AI sees N_visible = 4
```

## 3. Measurable Endpoints
- **Diversity Inflation Metric ($\mathcal{I}_{\text{laundering}}$):**
  $$\mathcal{I}_{\text{laundering}} = \frac{\widehat{N}_{\text{eff}}(G_2)}{N_{\text{true}}}$$
- **Downstream Consensus Vulnerability:** Probability that downstream agent accepts $S_{1..4}$ as confirmed multi-source truth vs single uncorroborated claim.

## 4. Live Call Allocation
- 2 Transformation Chains $\times$ 4 Generations $\times$ 2 Replications = 16 calls on Gemma 3:12B.
- Budget ceiling: **16 calls**.
