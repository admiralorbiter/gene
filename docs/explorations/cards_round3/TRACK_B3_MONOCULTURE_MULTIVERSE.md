# Experiment Card — Track B3: Monoculture Measurement Multiverse

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** When non-semantic token names (`PROTO_M4` vs `PROTO_Q7`), document presentation positions, and candidate roles are strictly counterbalanced in a full measurement multiverse, models will continue to ignore opaque common-root metadata (`root_R1`), demonstrating that neural evidence integration defaults to surface heuristics rather than spontaneous genealogical discounting.
- **Why It Matters:** Round 2 exposed massive token/position asymmetry ($P(X)=0$ vs $P(Y)=0.75$). Rather than tweaking prompts ad-hoc, Track B3 constructs a full factorial multiverse to isolate the pure marginal effect of root-sharing ($\Delta_{\text{root}}$).

## 2. Multiverse Factorial Design
We factorialize across 4 orthogonal dimensions:
1. **Root Structure (2 levels):**
   - Independent Roots: 3 documents from 3 distinct roots vs 2 documents from 2 distinct roots ($3:2$ raw ratio, $3:2$ root ratio).
   - Monoculture Roots: 3 documents from 1 shared root vs 2 documents from 2 distinct roots ($3:2$ raw ratio, $1:2$ root ratio).
2. **Token Identity Assignment (2 levels):**
   - Mapping 1: Majority claim = `PROTO_M4`, Minority claim = `PROTO_Q7`.
   - Mapping 2: Majority claim = `PROTO_Q7`, Minority claim = `PROTO_M4`.
3. **Document Order / Positional Interleaving (2 levels):**
   - Forward order: Majority docs in positions [1, 2, 3], Minority in [4, 5].
   - Interleaved / Reverse order: Majority docs in positions [2, 4, 5], Minority in [1, 3].
4. **Station Context (2 levels):** `VELORA` vs `KESTREL`.

$$\text{Full Matrix} = 2 \times 2 \times 2 \times 2 = 16 \text{ balanced cells}$$

## 3. Measurable Endpoints
- **Marginal Ancestral Discounting Effect ($\Delta_{\text{root}}$):**
  $$\Delta_{\text{root}} = P(\text{Majority}\mid \text{Independent Roots}) - P(\text{Majority}\mid \text{Monoculture Roots})$$
  - If $\Delta_{\text{root}} \approx 0$: Provenance metadata has zero spontaneous behavioral discounting effect after controlling for nuisance factors.
  - If $\Delta_{\text{root}} > 0$: Neural reasoners exhibit genuine, un-confounded genealogical discounting.
- **Positional Bias ($\Delta_{\text{pos}}$) & Token Bias ($\Delta_{\text{token}}$):** Marginal main effects of nuisance variables.

## 4. Live Call Allocation
- 16 balanced multiverse cells $\times$ 1 call + 4 replications = 20 calls on Gemma 3:12B.
- Budget ceiling: **24 calls**.
