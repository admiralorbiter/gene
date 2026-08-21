# Exploration Round 6 Stage 6A: Supersession Algebra & Temporal Validity Preregistration

**Assay Name**: Stage 6A (Temporal State Transition & Supersession Algebra)  
**Assay Type**: Exact Deterministic Mathematical Specification & Closed-Form Oracle  
**Compute Allocation**: 0 Live Model Compute (Pure Python Deterministic Assay)  
**Parent Milestone**: `round5-stage5c-postreview-freeze` (`28a897b`)  
**Target Module**: `src/gene/supersession_engine.py`  
**Test Suite**: `tests/test_supersession_algebra.py`

---

## 1. Research Motivation & Problem Statement

In Exploration Rounds 1 through 5, upstream change was provided to the Epistemic Kernel via an explicit, pre-classified retraction marker: $\text{do}(x = 0)$. In real-world persistent agent environments, however, knowledge updates arrive as **new natural information** rather than explicit retractions.

For example, an agent receiving the new observation `"Alice moved to Chicago at t=5"` must determine that:
1. `"Alice lives in Kansas City"` is **superseded** at $t=5$.
2. Dependent conclusions (e.g. `"Alice's commute is 20 minutes"`) lose their Kansas City support path.
3. If an independent alternative derivation exists (e.g. Alice has a second home with a 20-minute train route in Chicago), the conclusion **survives non-destructively**.

Stage 6A establishes the **deterministic formal foundation** for temporal validity, implicit supersession, expiration, and unresolved conflict without requiring live LLM compute.

---

## 2. Formal Temporal State Model

Let $\mathcal{E}$ be an append-only timeline of discrete temporal events $e_1, e_2, \dots, e_N$ occurring at integer timestamps $t \in \mathbb{N}_0$.

### 2.1 Fact & Rule Representations
- **Fact**: $f = (\text{id}, \text{predicate}, \text{arguments}, t_{\text{asserted}}, \mathcal{L}(f))$ where $\mathcal{L}(f) \subseteq \text{Roots}$.
- **Rule**: $r = (\text{id}, \text{head}, \text{body})$, where $\text{body} = \{p_1, \dots, p_k\}$.

### 2.2 Discrete Event Types
1. **`ADD(fact, t)`**: Asserts a new fact at timestamp $t$.
2. **`SUPERSEDES(new_fact_id, old_fact_id, t)`**: Declares that `new_fact` replaces `old_fact` at timestamp $t$. The validity window of `old_fact` terminates at $t$.
3. **`RETRACT(fact_id, t)`**: Explicitly revokes `fact_id` at timestamp $t$.
4. **`EXPIRES(fact_id, t_expire)`**: Declares a finite validity horizon $[t_{\text{asserted}}, t_{\text{expire}})$.
5. **`CONTRADICTS(fact_a_id, fact_b_id, t)`**: Declares an unresolved conflict between `fact_a` and `fact_b` at timestamp $t$. In the default cautious mode, both facts become inactive until resolved; in optimistic mode, both remain marked pending adjudication.

### 2.3 Temporal Validity State $\mathcal{V}_t$
A fact $f$ is **active and valid at timestamp $t$** ($f \in \mathcal{F}_t$) if and only if:
1. $t_{\text{asserted}} \le t$,
2. $\neg \exists e = \text{SUPERSEDES}(f', f, t') \in \mathcal{E}$ such that $t' \le t$,
3. $\neg \exists e = \text{RETRACT}(f, t') \in \mathcal{E}$ such that $t' \le t$,
4. If $f$ has an expiration $t_{\text{expire}}$, then $t < t_{\text{expire}}$,
5. $\neg \exists e = \text{CONTRADICTS}(f, f'', t') \in \mathcal{E}$ with $t' \le t$ (under cautious conflict resolution).

---

## 3. Temporal Epistemic Support & Lineage Projection

At any timestamp $t$:
1. **Active Premise Universe**: $\mathcal{F}_t = \{ f \in \mathcal{F} : \text{is\_valid}(f, t) \}$.
2. **Temporal Entitling Support $\mathcal{S}_t(c)$**:
   $$\mathcal{S}_t(c) = \min_{\subseteq} \{ S_i \subseteq \mathcal{F}_t : S_i \cup \mathcal{R} \vdash c \}$$
   where $\min_{\subseteq}$ enforces antichain minimality across active premise sets.
3. **Temporal Lineage-Projected Hypergraph $\mathcal{S}_{L,t}(c)$**:
   $$\mathcal{S}_{L,t}(c) = \min_{\subseteq} \{ \{ \mathcal{L}(p) : p \in S_i \} : S_i \in \mathcal{S}_t(c) \}$$
4. **Temporal Action Authority $\text{Auth}_t(c)$**:
   $$\text{Auth}_t(c) = \frac{1}{2} \left( \frac{\kappa_{L,t}}{\kappa_{\text{init}}} + \frac{|\mathcal{S}_{L,t}|}{|\mathcal{S}_{L,\text{init}}|} \right)$$

---

## 4. First-Order Temporal Query Interfaces

The `SupersessionEngine` exposes five deterministic queries:

1. **`WHY_t(c)`**:
   Returns the current active support family $\mathcal{S}_t(c)$, lineage hypergraph $\mathcal{S}_{L,t}(c)$, and authority score $\text{Auth}_t(c)$.
2. **`WHAT_IF_t(c, event)`**:
   Computes counterfactual support $\mathcal{S}_{t+1}(c \mid \text{event})$ without mutating persistent state.
3. **`THEN_WHAT_t(event)`**:
   Returns the complete set of downstream propositions $\{c\}$ whose entitlement status (ACTIVE vs INACTIVE) or authority score changes upon applying `event`.
4. **`TIMELINE(c)`**:
   Returns the chronological history of entitlement transitions for claim $c$ across all recorded timestamps $[0, t_{\max}]$.
5. **`AUDIT_CONFLICTS(t)`**:
   Returns all currently unresolved contradiction pairs and ungrounded claims at timestamp $t$.

---

## 5. Formal Invariants & Test Specification

Stage 6A must satisfy five formal mathematical invariants:

1. **Monotonic Event Progression**: Applying events at increasing timestamps strictly preserves historical validity states ($t_1 < t_2 \implies \mathcal{V}_{t_1}$ reproducible exactly).
2. **Supersession Non-Destructive Survival**: If $c$ has two independent support paths $P_1 = \{A, B\}$ and $P_2 = \{D, E\}$, superseding $D$ with $D'$ (where $D'$ does not support $c$) leaves $c$ active at $t$ via $P_1$ with degraded authority.
3. **Temporal Expiration Determinism**: An expiring premise $f$ automatically transitions from active to inactive at $t = t_{\text{expire}}$ without requiring an explicit retraction event.
4. **Unresolved Conflict Isolation**: A contradiction event between two premises isolates the affected branch without contaminating orthogonal derivation paths.
5. **Antichain Minimality Invariant**: At every timestamp $t$ and for every claim $c$, $\mathcal{S}_t(c)$ and $\mathcal{S}_{L,t}(c)$ contain zero strict supersets.
