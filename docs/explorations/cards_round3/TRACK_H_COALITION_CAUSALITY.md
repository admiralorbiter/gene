# Experiment Card — Track H: Coalition Causality & Overdetermination

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** In the presence of redundant independent justification ($S(C) = \{\{A,B\}, \{D,E\}\}$), single-parent counterfactual knockout tests ($A \leadsto 0$ or $D \leadsto 0$) fail to detect causal relevance because the backup support path masks the effect. Causal parenthood cannot be measured as an isolated binary edge ($A \to C$); it must be measured as membership in a minimal causally sufficient coalition ($S_C(C)$).
- **Why It Matters:** This directly tests whether GENE's foundational Experiment 0 causal parent assay breaks under multi-justification, formalizing the distinction between formal support $S_F(C)$ and actual neural causal coalitions $S_C(C)$.

## 2. Experimental Design & Intervention Lattice
We evaluate three canonical geometries across complete intervention subsets:

```
                            GEOMETRY 2: RECOMBINANT SUPPORT
                                    A ─── B ─┐
                                             ├── C
                                    D ─── E ─┘
```

### Intervention Coalition Lattice ($AB + DE \to C$):
1. **Baseline Control ($\emptyset$):** $\{A, B, D, E\}$ all valid $\implies$ Formal: $C$ valid ($S_F = \{\{A,B\}, \{D,E\}\}$).
2. **Single Knockouts:**
   - Knockout $\{A\}$: $\{B, D, E\}$ valid $\implies$ Formal: $C$ valid (via $DE$).
   - Knockout $\{D\}$: $\{A, B, E\}$ valid $\implies$ Formal: $C$ valid (via $AB$).
3. **Coalition Knockouts (Minimal Hitting Sets):**
   - Knockout $\{A, D\}$: $\{B, E\}$ valid $\implies$ Formal: $C \to \text{UNKNOWN}$ (both paths broken).
   - Knockout $\{A, E\}$: $\{B, D\}$ valid $\implies$ Formal: $C \to \text{UNKNOWN}$.
   - Knockout $\{B, D\}$: $\{A, E\}$ valid $\implies$ Formal: $C \to \text{UNKNOWN}$.
   - Knockout $\{B, E\}$: $\{A, D\}$ valid $\implies$ Formal: $C \to \text{UNKNOWN}$.

## 3. Measurable Endpoints
- **Single-Parent False-Negative Rate:** Rate at which single knockouts conclude $A \not\to C$ and $D \not\to C$ despite $A$ and $D$ being essential components of the justification structure.
- **Coalition Closure:** Whether removing minimal hitting sets ($\{A,D\}$) produces behavioral transition to `UNKNOWN` ($P(\text{UNKNOWN}\mid \{A,D\}=0) = 1.0$).
- **$S_F(C)$ vs $S_C(C)$ Concordance:** Compare whether the neural generator actually utilizes both formal paths or collapses to a single behavioral shortcut.

## 4. Live Call Allocation
- 3 Geometries $\times$ 6 Key Lattice Points = 18 calls on Gemma 3:12B.
- Budget ceiling: **18 calls**.
