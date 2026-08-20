# Experiment Card — Track S: Support Acquisition from Observable Traces

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** Minimal support environments $S_F(c)$ can be derived mechanically from observable runtime execution traces (occurrence nodes, rule templates, exposure edges) distinguishing conjunctive (AND) and alternative (OR) derivation environments without manual researcher declaration.
- **Round 3 Scope:** **Deterministic Formalism Only (0 Live Calls).** We validate the mechanical Trace-to-Support compiler across disjunctive proof trees and compare its formal output $S_F(c)$ with Track H's empirical causal coalitions $S_C(c)$.

## 2. Methodology & Mechanical Support Derivation
1. **Trace Ingestion:**
   - Input: Directed graph of occurrence nodes $V$ supporting multiple conjunctive environments (`support_environments: list[list[str]]`).
   - Backward Slicing: Recursively traces all paths to root premises $\mathcal{A}$ across disjunctive and conjunctive branches.
2. **Minimal Conjunctive Environment Extraction:**
   - For target claim $c$, extracts all irredundant root assumption sets $S_F(c) = \{S_1, \dots, S_k\}$.
   - Verified on recombinant DAG: extracts $S_F(C) = \{\{\text{fact\_A}, \text{fact\_B}\}, \{\text{fact\_D}, \text{fact\_E}\}\}$.

## 3. Measurable Endpoints
- **Compiler Exactness:** 100% mathematical recovery of ground-truth minimal support sets from trace DAGs (`pytest tests/explore_round3/test_track_s.py`).

## 4. Live Call Allocation
- **0 live calls** in Round 3.
