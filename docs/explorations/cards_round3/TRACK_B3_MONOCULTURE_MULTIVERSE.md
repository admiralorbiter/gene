# Experiment Card — Track B3: Monoculture Measurement Multiverse

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** After holding prompt syntax strictly invariant (pure lexical root token substitution) and factorially balancing token identities, document positions, and station roles, models will continue to ignore opaque common-root metadata (`root_R1`), demonstrating that neural evidence integration defaults to surface heuristics rather than spontaneous genealogical discounting.
- **Why It Matters:** Round 2 exposed massive token/position asymmetry ($P(X)=0$ vs $P(Y)=0.75$). Track B3 constructs a pure factorial multiverse with exact replays to measure the empirical noise floor and isolate $\Delta_{\text{root}}$.

## 2. Multiverse Factorial Design (16 Cells + 8 Replays = 24 Calls)
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

$$\text{Full Matrix} = 16 \text{ balanced cells} + 8 \text{ balanced exact replays} = 24 \text{ calls}$$

## 3. Measurable Endpoints
- **Marginal Ancestral Discounting Effect ($\Delta_{\text{root}}$):**
  $$\Delta_{\text{root}} = P(\text{Majority}\mid \text{Independent Roots}) - P(\text{Majority}\mid \text{Monoculture Roots})$$
- **Empirical Replay Noise Floor:** Disagreement rate across the 8 paired exact-prompt replays.

## 4. Live Call Allocation
- 16 factorial cells + 8 replays = **24 calls** on Gemma 3:12B.
- Budget ceiling: **24 calls**.
