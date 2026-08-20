# Round 2 Experiment Card — Track B2: Monoculture Hardening

## 1. Scientific Objective
- **Core Research Question:** Does neural adjudication spontaneously distinguish independent epistemic roots from repeated descendants of a single root when prompt steering is eliminated and contextual geometry is strictly controlled?
- **Hypothesis:** When presented with competing claims $X$ and $Y$ under identical surface document counts ($N=5$), language models will adjudicate in favor of the claim with greater **effective root diversity** ($N_{\text{roots}}$), even when the competing claim has a higher raw repetition count ($3:2$ raw advantage with $1:2$ root disadvantage $\implies P(Y) > P(X)$).

## 2. Controls & Anti-Confound Measures (Eliminating Round 1 Flaws)
1. **Document Count Invariance:** Exactly $5$ retrieved memory records in every prompt across all conditions.
2. **Opaque Provenance Tokens:** Roots are labeled using non-semantic IDs (`source_R1`, `source_R2`, `source_R3`), eliminating status/authority cues (no "Director" vs "Auditor").
3. **Template & Sentence Symmetry:** Identical sentence structures and character lengths across competing claims.
4. **Prompt Neutrality (Zero Steering):** The prompt contains **no instruction** to "evaluate independent sources." It asks strictly: *"Based on the evidence, which protocol is best supported?"*
5. **Full $2 \times 2$ Factorial Design with X/Y Counterbalancing:**
   - Factor 1: Raw Count Advantage ($3:2$ for $X$ vs $3:2$ for $Y$)
   - Factor 2: Root Count Advantage ($1:2$ roots for $X$ vs $2:1$ roots for $X$)
   - Counterbalancing: Reverse target assignments ($X \leftrightarrow Y$) across stations.

## 3. $2 \times 2$ Experimental Design Matrix
| Cell | Condition Name | Surface Count | Ancestral Root Structure | Concurrence vs Conflict |
| :---: | :--- | :---: | :---: | :---: |
| **Cell 1** | `concur_X` | 3 X vs 2 Y | 3 roots (X) vs 2 roots (Y) | Concurrence (Raw & Roots favor X) |
| **Cell 2** | `conflict_roots_Y` | 3 X vs 2 Y | 1 root (X) vs 2 roots (Y) | **Conflict (Raw favors X, Roots favor Y)** |
| **Cell 3** | `concur_Y` | 2 X vs 3 Y | 2 roots (X) vs 3 roots (Y) | Concurrence (Raw & Roots favor Y) |
| **Cell 4** | `conflict_roots_X` | 2 X vs 3 Y | 2 roots (X) vs 1 root (Y) | **Conflict (Raw favors Y, Roots favor X)** |

## 4. Planned Call Budget
- 4 conditions × 2 stations (`VELORA`, `KESTREL`) × 2 role-swaps = **16 live calls** (max 24 with 1 replication).
- **Falsifier:** If adjudication strictly tracks surface count ($3:2 \implies 100\% X$ regardless of root structure), then language models act as pure repetition vote counters and do not track ancestral graph independence without explicit steering.
