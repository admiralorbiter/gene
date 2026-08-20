# Experiment Card — Track S: Support Acquisition from Observable Traces

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** Minimal support environments $S_F(c)$ can be derived mechanically from observable runtime execution traces (occurrence nodes, rule templates, exposure edges, and admitted outputs) without requiring an omniscient researcher to hand-declare support sets.
- **Why It Matters:** The Epistemic Kernel moonshot cannot rely on manually registered support sets in production. Track S builds and validates the **Trace-to-Support Compiler** that derives $S_F(c)$ mechanically and compares it against reported support $S_R(c)$ and causal intervention support $S_C(c)$.

## 2. Methodology & Mechanical Support Derivation
1. **Trace Ingestion:**
   - Input: Directed graph of occurrence nodes $V$, rule bindings $R$, and lineage edges $E$.
   - Backward Slicing: For target node $c$, recursively trace all paths to root premises $\mathcal{A}$.
2. **Minimal Conjunctive Environment Extraction:**
   - For each independent proof tree $T_i$, compute the leaf set of assumptions: $S_i = \text{Leaves}(T_i) \cap \mathcal{A}$.
   - Eliminate non-minimal supersets: $S_F(c) = \{S_i \in \mathcal{S} : \nexists S_j \in \mathcal{S} \text{ s.t. } S_j \subset S_i\}$.
3. **Tripartite Support Comparison:**
   - Formal Minimal Support: $S_F(c)$ (derived from backward trace slice).
   - Reported Support: $S_R(c)$ (parsed from model-generated citation metadata).
   - Causal Support: $S_C(c)$ (minimal intervention coalitions from Track H).

## 3. Measurable Endpoints
- **Derivation Exactness:** Match rate between mechanically extracted $S_F(c)$ and ground-truth oracle support environments across all canonical geometries.
- **$S_F \text{ vs } S_R \text{ vs } S_C$ Concordance Matrix:** Quantitative divergence across formal, reported, and causal support.

## 4. Live Call Allocation
- 0 live calls for compiler verification; $\le 8$ calls on Gemma 3:12B for end-to-end trace validation.
- Budget ceiling: **8 calls**.
