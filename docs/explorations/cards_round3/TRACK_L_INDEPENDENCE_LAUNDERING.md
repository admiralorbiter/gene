# Experiment Card — Track L: Independence Laundering & Inflated Diversity

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** As an ancestral observation reproduces through successive downstream generations (paraphrasing, partial citing, metadata stripping), downstream models will perceive evidence independence as progressively inflating ($\widehat{N}_{\text{model}}: 1 \leadsto 4$) even though true root diversity remains strictly $N_{\text{true}} = 1$.
- **Why It Matters:** Independence laundering is the evolutionary mechanism that enables epistemic monoculture. Tracking how semantic reproduction launders single-source provenance into manufactured consensus connects lineage epidemiology directly to multi-agent memory reliability.

## 2. Experimental Transformation Cascade & 4-Root Positive Control
We evaluate 5 discrete conditions:
1. **$G_0$ True Root:** 1 doc authored by `root_R1` ($N_{\text{true}} = 1$).
2. **$G_1$ Cited Paraphrases:** 4 docs all explicitly citing `root_R1` ($N_{\text{true}} = 1$, expected $\widehat{N}_{\text{model}} = 1$).
3. **$G_2$ Partial Laundering:** 4 docs (2 cite `root_R1`, 2 reference ambient archive).
4. **$G_3$ Laundered Consensus:** 4 docs with provenance completely stripped ($N_{\text{true}} = 1$).
5. **$G_{\text{ctrl}}$ True 4-Root Control:** 4 docs from 4 explicitly independent roots `root_R1`..`root_R4` ($N_{\text{true}} = 4$, expected $\widehat{N}_{\text{model}} = 4$).

## 3. Measurable Endpoints & Analysis
- **Perceived Independence Trajectory:** Measured values of `estimated_independent_sources` across $G_0 \to G_1 \to G_2 \to G_3 \to G_{\text{ctrl}}$.
- **Diversity Inflation Ratio:**
  $$\mathcal{I}_{\text{laundering}} = \frac{\widehat{N}_{\text{model}}(G_3)}{N_{\text{true}}}$$
- **4-Root Control Compliance:** Verification that the model accurately reports 4 sources under $G_{\text{ctrl}}$.

## 4. Live Call Allocation
- 5 Stages $\times$ 2 Stations $\times$ 2 Target Protocols = **20 calls** on Gemma 3:12B.
- Budget ceiling: **20 calls**.
