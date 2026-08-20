# Experiment Card — Track H: Coalition Causality & Overdetermination

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** In the presence of redundant independent justification ($S(C) = \{\{A,B\}, \{D,E\}\}$), single-parent counterfactual knockout tests ($A \leadsto 0$ or $D \leadsto 0$) fail to detect causal relevance because the backup support path masks the effect. Causal parenthood cannot be measured as an isolated binary edge ($A \to C$); it must be measured as membership in a minimal causally sufficient coalition ($S_C(C)$).
- **Why It Matters:** This directly tests whether GENE's foundational Experiment 0 causal parent assay breaks under multi-justification, formalizing the distinction between formal support $S_F(C)$ and actual neural causal coalitions $S_C(C)$.

## 2. Experimental Design & 11-Point Intervention Lattice
We focus entirely on the clean recombinant geometry:

```
                            GEOMETRY: RECOMBINANT SUPPORT
                                    A ─── B ─┐
                                             ├── C
                                    D ─── E ─┘
```

### Intervention Lattice Points ($AB + DE \to C$):
1. **Baseline Control ($\emptyset$):** $\{A, B, D, E\}$ all valid $\implies$ Formal: $C = \text{PROTO\_X7}$.
2. **Single Knockouts (4):**
   - $\{A\}$: $\{B, D, E\}$ valid $\implies$ Formal: $C = \text{PROTO\_X7}$ (via $DE$).
   - $\{B\}$: $\{A, D, E\}$ valid $\implies$ Formal: $C = \text{PROTO\_X7}$ (via $DE$).
   - $\{D\}$: $\{A, B, E\}$ valid $\implies$ Formal: $C = \text{PROTO\_X7}$ (via $AB$).
   - $\{E\}$: $\{A, B, D\}$ valid $\implies$ Formal: $C = \text{PROTO\_X7}$ (via $AB$).
3. **Path Isolation Knockouts (2):**
   - $\{A, B\}$: $\{D, E\}$ valid $\implies$ Formal: $C = \text{PROTO\_X7}$ (tests path $DE$ in isolation).
   - $\{D, E\}$: $\{A, B\}$ valid $\implies$ Formal: $C = \text{PROTO\_X7}$ (tests path $AB$ in isolation).
4. **Cross-Path Minimal Hitting Sets (4):**
   - $\{A, D\}$: $\{B, E\}$ valid $\implies$ Formal: $C \to \text{UNKNOWN}$ (both paths broken).
   - $\{A, E\}$: $\{B, D\}$ valid $\implies$ Formal: $C \to \text{UNKNOWN}$.
   - $\{B, D\}$: $\{A, E\}$ valid $\implies$ Formal: $C \to \text{UNKNOWN}$.
   - $\{B, E\}$: $\{A, D\}$ valid $\implies$ Formal: $C \to \text{UNKNOWN}$.

## 3. Measurable Endpoints & Analysis
- **Single-Parent False-Negative Rate:** Rate at which single knockouts conclude $A \not\to C$ and $D \not\to C$ despite $A$ and $D$ being essential components of the justification structure.
- **Coalition Closure:** Whether removing minimal hitting sets ($\{A,D\}$) produces behavioral transition to `UNKNOWN` ($P(\text{UNKNOWN}\mid \{A,D\}=0) = 1.0$).
- **$S_F(C)$ vs $S_C(C)$ Concordance:** Call `CoalitionCausalityEngine.extract_minimal_causal_coalitions()` to recover empirical minimal coalitions and compare against $S_F(C) = \{\{A,B\}, \{D,E\}\}$.

## 4. Live Call Allocation
- 11 Lattice Points $\times$ 2 Stations (`VELORA`, `KESTREL`) = **22 calls** on Gemma 3:12B.
- Budget ceiling: **22 calls**.
