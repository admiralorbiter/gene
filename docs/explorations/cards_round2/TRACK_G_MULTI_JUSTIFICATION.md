# Round 2 Experiment Card — Track G: Multi-Justification & Epistemic Recombination

## 1. Scientific Objective
- **Core Research Question:** Can a persistent belief survive the invalidation or quarantine of one ancestral support path if an independent, valid alternative support path remains ($P(C) = AB + CD$)?
- **Hypothesis:** When an ancestor $A$ in path $AB$ is discredited ($A \leadsto 0$), an Epistemic Kernel evaluating minimal support sets will retain claim $C$ via path $CD$, preventing naive lineage autoimmunity ($P(\text{active} \mid 1 \text{ clean path remains}) = 1.0$, whereas $P(\text{active} \mid 0 \text{ clean paths}) = 0.0$).

## 2. Theoretical Formulation & Four Support Geometries
For every claim $c$, the kernel evaluates minimal support sets $S(c) = \{S_1, \dots, S_k\}$:
1. **Geometry 1: Single-Path ($AB \to C$)**
   - $S(C) = \{\{A, B\}\}$. Invalidate $A \implies S'(C) = \emptyset \implies C \text{ unsupported}$.
2. **Geometry 2: Redundant Independent Support ($AB + DE \to C$)**
   - $S(C) = \{\{A, B\}, \{D, E\}\}$. Invalidate $A \implies S'(C) = \{\{D, E\}\} \implies C \text{ survives}$.
3. **Geometry 3: Shared-Root Apparent Redundancy ($AX + AY \to C$)**
   - $S(C) = \{\{A, X\}, \{A, Y\}\}$. Invalidate $A \implies S'(C) = \emptyset \implies C \text{ unsupported}$.
4. **Geometry 4: Recombinant Support ($AI + BH \to C$)**
   - $I$ is infected, $H$ is healthy. Invalidate $I \implies S'(C) = \{\{B, H\}\} \implies C \text{ preserved}$.

## 3. Four Core Operations in Deterministic Engine
```python
def support_sets(claim: str) -> set[frozenset[str]]: ...
def invalidate_ancestor(ancestor: str) -> None: ...
def claim_survives(claim: str) -> bool: ...
def minimal_cut_sets(claim: str) -> set[frozenset[str]]: ...
```

## 4. Empirical Protocol (Post-Deterministic Phase)
- **Model:** `gemma3:12b` via `ExplorationHarness`
- **Manipulation:**
  - **Condition A (Independent Survival):** Context contains $AB \text{ (invalidated)} + DE \text{ (valid)}$ for $C$.
  - **Condition B (Full Invalidation):** Context contains $AB \text{ (invalidated)} + AX \text{ (invalidated)}$ for $C$.
- **Call Allocation:** 2 worlds × 3 support geometries × 2 conditions = **12 live calls** (max 18 with 1 replication).
- **Falsifier:** If Gemma abstains equally on Condition A and Condition B ($P(\text{active} \mid \text{independent}) = P(\text{active} \mid \text{shared}) = 0.0$), then neural reasoners cannot exploit surviving alternative justifications in prompt working memory.
