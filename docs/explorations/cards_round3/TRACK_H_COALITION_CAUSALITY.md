# Experiment Card — Track H: Coalition Causality & Overdetermination

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** In the presence of redundant independent justification ($S(C) = \{\{A,B\}, \{D,E\}\}$), single-parent counterfactual knockout tests ($A \leadsto 0$ or $D \leadsto 0$) fail to detect causal relevance because the backup support path masks the effect. Causal parenthood cannot be measured as an isolated binary edge ($A \to C$); it must be measured as membership in a minimal causally sufficient coalition ($S_C(C)$).
- **Full Identifiability via Complete $2^4 = 16$-Point Lattice:** We evaluate all 16 combinations of parent premises $\{A, B, D, E\}$ to guarantee that empirical minimal coalitions $S_C(C)$ are fully identified rather than artifacts of a restricted test set.
- **Standardized Premise Omission Semantics:** Every knockout ($do(X=0)$) is strictly executed as pure premise deletion from context.

## 2. Experimental Design & 16-Point Intervention Lattice
We focus entirely on the clean recombinant geometry:

```
                            GEOMETRY: RECOMBINANT SUPPORT
                                    A ─── B ─┐
                                             ├── C
                                    D ─── E ─┘
```

### Complete Intervention Power Set ($AB + DE \to C$):
1. **$r=0$ (1 point):** Baseline $\emptyset \implies C = \text{PROTO\_X7}$.
2. **$r=1$ (4 points):** Single knockouts $\{A\}, \{B\}, \{D\}, \{E\} \implies C = \text{PROTO\_X7}$ (via alternate path).
3. **$r=2$ (6 points):**
   - Path-isolation knockouts $\{A, B\}, \{D, E\} \implies C = \text{PROTO\_X7}$.
   - Cross-path minimal hitting sets $\{A, D\}, \{A, E\}, \{B, D\}, \{B, E\} \implies C \to \text{UNKNOWN}$.
4. **$r=3$ (4 points):** Triple knockouts $\{A,B,D\}, \{A,B,E\}, \{A,D,E\}, \{B,D,E\} \implies C \to \text{UNKNOWN}$ (tests single premise in isolation).
5. **$r=4$ (1 point):** Quadruple knockout $\{A,B,D,E\} \implies C \to \text{UNKNOWN}$ (0 premises).

## 3. Measurable Endpoints & Analysis
- **Single-Parent False-Negative Rate:** Rate at which single knockouts conclude $A \not\to C$ and $D \not\to C$ despite $A$ and $D$ being essential components of the justification structure.
- **Coalition Closure:** Whether removing minimal hitting sets ($\{A,D\}$) produces behavioral transition to `UNKNOWN` ($P(\text{UNKNOWN}\mid \{A,D\}=0) = 1.0$).
- **$S_F(C)$ vs $S_C(C)$ Concordance:** Call `CoalitionCausalityEngine.extract_minimal_causal_coalitions()` to recover empirical minimal coalitions from the full 16-point lattice and compare against $S_F(C) = \{\{A,B\}, \{D,E\}\}$.

## 4. Live Call Allocation
- 16 Lattice Points $\times$ 2 Stations (`VELORA`, `KESTREL`) = **32 calls** on Gemma 3:12B.
- Budget ceiling: **32 calls**.
