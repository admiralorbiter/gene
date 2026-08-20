# Experiment Card — Track P: Permutation Invariance & Serialization Spread

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** Because autoregressive language models process linear token sequences rather than unordered graphs, serializing the identical epistemic state $\mathcal{E}$ under different premise orderings $\pi \in \Pi$ produces substantial behavioral variation (the *Lost in Serialization* effect).
- **Deterministic Compiler Invariance vs Live Neural Measurement:**
  - A structured context compiler operating at `TOPOLOGY_AWARE_GROUPING` canonically groups premises into deterministic proof pathways. We prove **100% hash-identical prompt invariance deterministically with 0 live compute** ($\forall \pi_1, \pi_2 \in \Pi, \text{SHA256}(\mathcal{C}_{\text{blocks}}(\pi_1)) = \text{SHA256}(\mathcal{C}_{\text{blocks}}(\pi_2))$).
  - Live LLM calls are deployed strictly to measure the **unmitigated neural serialization spread** under raw flat serialization ($\mathcal{C}_{\text{flat}}$), contrasted with the stability of the canonical compiled context.

## 2. Experimental Design & Permutation Allocation
For the recombinant support state $S_F = \{\{A,B\}, \{D,E\}\}$:
1. **Raw Flat Serialization Panel ($N=24$ calls):** Evaluate all $4! = 24$ permutations of premise presentation order $[A,B,D,E]$ under `raw_flat` compilation.
2. **Canonical Compiled Baseline ($N=1$ call):** Evaluate the canonical `canonical_support_blocks` compiled context.
3. **Exact Replay Stability Panel ($N=4$ calls):** 4 exact CallSpec replays on the canonical compiled prompt to establish baseline stochasticity ($\epsilon_{\text{replay}}$).

## 3. Measurable Endpoints & Categorical Metrics
- **Permutation Output Entropy ($H_{\text{perm}}$):** Shannon entropy of categorical model predictions across the 24 permutations.
- **Serialization Disagreement Rate ($\mathcal{D}_{\text{perm}}$):** Proportion of permutation pairs yielding differing answers:
  $$\mathcal{D}_{\text{perm}} = \frac{1}{\binom{24}{2}} \sum_{i < j} \mathbf{1}[y(\pi_i) \ne y(\pi_j)]$$
- **Abstention Flip Count ($N_{\text{flip}}$):** Number of permutations that flip between concrete answer (`PROTO_X7`) and `UNKNOWN` abstention.
- **Worst-Case Correctness ($\text{Acc}_{\text{worst}}$):** Minimum accuracy across all 24 permutations under the raw flat backend compared against the canonical compiler.
