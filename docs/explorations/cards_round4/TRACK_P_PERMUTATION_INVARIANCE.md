# Experiment Card — Track P: Permutation Invariance & Serialization Spread

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** Because neural language models process linear token sequences rather than unordered sets, serializing the identical epistemic state $E$ under different premise permutations $\pi \in \Pi$ can produce substantial behavioral variance (the "Lost in Serialization" effect).
- **Compilation Mitigation:** A structured context compiler (e.g. `canonical_support_blocks` or `support_certificate`) eliminates arbitrary permutation spread by organizing premises into deterministic proof pathways before serialization.

## 2. Experimental Arms & Permutation Set
We evaluate all $4! = 24$ permutations of active premises in the recombinant geometry $AB+DE$:
1. **Raw Flat Serialization Backend ($\mathcal{C}_{\text{flat}}$):** 24 permutations serialized as raw lists of documents.
2. **Canonical Support Block Backend ($\mathcal{C}_{\text{blocks}}$):** 24 permutations compiled into grouped derivation pathways.

## 3. Measurable Endpoints & Analysis
- **Serialization Output Spread ($\Delta_{\text{perm}}$):** Standard deviation and disagreement rate of model predictions across the 24 permutations.
- **Abstention Flips ($N_{\text{flip}}$):** Number of permutations that flip between valid answer and UNKNOWN abstention.
- **Compiler Invariance Recovery:** Reduction in serialization disagreement under the compiler backend compared to raw flat serialization.
