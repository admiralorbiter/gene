# Experiment Card — Track B3: Monoculture Measurement Multiverse

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** After holding prompt syntax strictly invariant (pure lexical root token substitution) and factorially balancing token identities, document positions, and station roles, models will continue to ignore opaque common-root metadata (`root_R1`), demonstrating that neural evidence integration defaults to surface heuristics rather than spontaneous genealogical discounting.
- **Why It Matters:** Round 2 exposed token/position asymmetry. Track B3 constructs a pure factorial multiverse with exact replays and seed perturbations to isolate $\Delta_{\text{root}}$, $\epsilon_{\text{replay}}$, and $\epsilon_{\text{seed}}$.

## 2. Multiverse Factorial Design (16 Cells + 4 Exact Replays + 4 Seed Perturbations = 24 Calls)
We factorialize across 4 orthogonal dimensions:
1. **Root Structure (2 levels):**
   - Independent Roots: 3 distinct roots for majority (`root_R1`, `root_R2`, `root_R3`) vs 2 distinct roots for minority (`root_R4`, `root_R5`).
   - Monoculture Roots: 1 shared root repeated 3 times (`root_R1`, `root_R1`, `root_R1`) vs 2 distinct roots for minority (`root_R4`, `root_R5`).
2. **Token Identity Assignment (2 levels):**
   - Mapping 1: Majority claim = `PROTO_M4`, Minority claim = `PROTO_Q7`.
   - Mapping 2: Majority claim = `PROTO_Q7`, Minority claim = `PROTO_M4`.
3. **Document Order / Positional Interleaving (2 levels):**
   - Forward order: Majority docs in positions [1, 2, 3], Minority in [4, 5].
   - Interleaved / Reverse order: Majority docs in positions [2, 4, 5], Minority in [1, 3].
4. **Station Context (2 levels):** `VELORA` vs `KESTREL`.
5. **Replication & Perturbation Layer:**
   - 4 Exact CallSpec Replays: identical prompt, `seed=42`, `temperature=0.0` $\implies \epsilon_{\text{replay}}$.
   - 4 Seed Perturbations: identical prompt, `seed=43`, `temperature=0.0` $\implies \epsilon_{\text{seed}}$.

$$\text{Full Design} = 16 \text{ factorial cells} + 4 \text{ exact replays} + 4 \text{ seed perturbations} = 24 \text{ calls}$$

## 3. Measurable Endpoints
- **Marginal Ancestral Discounting Effect ($\Delta_{\text{root}}$):**
  $$\Delta_{\text{root}} = P(\text{Majority}\mid \text{Independent Roots}) - P(\text{Majority}\mid \text{Monoculture Roots})$$
- **Exact CallSpec Replay Instability ($\epsilon_{\text{replay}}$):** Disagreement rate under identical CallSpec.
- **Seed Sensitivity ($\epsilon_{\text{seed}}$):** Disagreement rate under seed perturbation.

## 4. Live Call Allocation
- 16 factorial cells + 4 exact replays + 4 seed perturbations = **24 calls** on Gemma 3:12B.
- Budget ceiling: **24 calls**.
