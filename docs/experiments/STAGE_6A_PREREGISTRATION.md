# Stage 6A Preregistration: Bitemporal Supersession Algebra & Epistemic State Transition Semantics

**Document URI**: `docs/experiments/STAGE_6A_PREREGISTRATION.md`  
**Milestone**: Exploration Round 6 (Stage 6A-v2)  
**Parent Freeze**: `round5-stage5c-postreview-freeze` (`28a897b`)  
**Status**: Formally Specified & Verified  

---

## 1. Mathematical & Architectural Specification

Stage 6A-v2 formalizes persistent epistemic state transitions under world evolution, retroactive corrections, expiration, and multi-pair contradictions using a **bitemporal event-sourced model**.

### 1.1 The Bitemporal Coordinate System
Persistent beliefs exist in a 2-dimensional temporal coordinate space:
1. **Valid Time ($t_v \in \mathbb{R}$)**: The time at which a factual proposition or relation holds true in the target world.
2. **Knowledge Time ($t_k \in \mathbb{N}_0$)**: The transaction time when the agent learned, recorded, or revised the event.

Queries ask either:
- **$\text{STATE}(c, t_v)$**: *What is true in the world at time $t_v$?*
- **$\text{BELIEVED\_STATE}(c, t_v \mid t_k)$**: *What did the agent believe held at valid time $t_v$, as known at transaction time $t_k$?*

---

## 2. Formal Event Algebra

The state of persistent memory is governed by an immutable, append-only event log $\mathcal{E} = [e_1, \dots, e_N]$. Each event carries a transaction timestamp $t_k$ and a valid-time interval $[t_{v,\text{start}}, t_{v,\text{end}})$:

1. **`ASSERT(fact_id, t_k, t_v_start, t_v_end=None, occurrence_id=None)`**:
   Instantiates an occurrence episode for `fact_id` valid in interval $[t_{v,\text{start}}, t_{v,\text{end}})$. Reassertion across disjoint intervals (e.g. $[0, 5)$ and $[10, \infty)$) is natively supported without historical clipping.
2. **`SUPERSEDES(new_fact_id, old_fact_id, t_k, t_v_start)`**:
   Truncates the validity of `old_fact_id` at $t_{v,\text{start}}$ and activates `new_fact_id`.
3. **`RETRACT(fact_id, t_k, t_v_start)`**:
   Explicitly terminates the validity of `fact_id` for $t_v \ge t_{v,\text{start}}$.
4. **`EXPIRES(fact_id, t_k, t_v_expire)`**:
   Caps fact validity at $t_v < t_{v,\text{expire}}$.
5. **`CONTRADICTS(fact_a_id, fact_b_id, t_k, t_v_start, t_v_end=None)`**:
   Registers an active contradiction pair $\{f_a, f_b\}$ holding for $t_v \in [t_{v,\text{start}}, t_{v,\text{end}})$. Under cautious conflict resolution, involved facts are disqualified during this window without contaminating earlier undisputed history.
6. **`RESOLVE_CONFLICT(fact_a_id, fact_b_id, t_k, t_v_start, t_v_end=None)`**:
   Removes $\{f_a, f_b\}$ from active conflicts. Resolving $\{f_a, f_b\}$ strictly preserves any concurrent conflict $\{f_a, f_c\}$.

---

## 3. Epistemic Support & Authority Functions

Given active facts $\mathcal{F}(t_v \mid t_k)$ derived by replaying events where $e.t_k \le t_k$:

1. **Minimal Support Hypergraph $\mathcal{S}_{t_v}(c \mid t_k)$**:
   $$\mathcal{S}_{t_v}(c \mid t_k) = \min_{\subseteq} \{ S_i \subseteq \mathcal{F}(t_v \mid t_k) : S_i \cup \mathcal{R} \vdash c \}$$
2. **Lineage-Projected Hypergraph $\mathcal{S}_{L,t_v}(c \mid t_k)$**:
   $$\mathcal{S}_{L,t_v}(c \mid t_k) = \min_{\subseteq} \{ \{ \mathcal{L}(p) : p \in S_i \} : S_i \in \mathcal{S}_{t_v}(c \mid t_k) \}$$
3. **Relative Action Authority ($\text{RelAuth}$)**:
   $$\text{RelAuth}_{t_v \mid t_k}(c) = \frac{1}{2} \left( \frac{\kappa_L(\mathcal{S}_{L,t_v})}{\kappa_L(\mathcal{S}_{L,\text{init}})} + \frac{|\mathcal{S}_{L,t_v}|}{|\mathcal{S}_{L,\text{init}}|} \right)$$
   *(Relative index where $1.0 = \text{baseline}, < 1.0 = \text{degraded}, > 1.0 = \text{reinforced}$).*
4. **Bounded Action Authority ($\text{BoundedAuth}$)**:
   $$\text{BoundedAuth}_{t_v \mid t_k}(c) = \min(1.0, \max(0.0, \text{RelAuth})) \in [0.0, 1.0]$$

---

## 4. Query Contracts & Deep Dirty-State Discovery

- **`WHY(c, t_v, t_k)`**: Returns boolean entitlement, $\mathcal{S}_{t_v}$, $\mathcal{S}_{L,t_v}$, $\kappa_L$, $\text{RelAuth}$, and $\text{BoundedAuth}$.
- **`WHAT_IF(c, event, t_v, t_k)`**: Evaluates hypothetical entitlement under counterfactual event without state mutation.
- **`THEN_WHAT(event, t_v, t_k)`**: Automatically discovers all affected downstream propositions in the deductive closure. A proposition is classified as impacted if:
  $$\Delta \text{Ent} \lor \Delta \mathcal{S} \lor \Delta \mathcal{S}_L \lor \Delta \text{Auth}$$
  Classifications include `LOST_ENTITLEMENT`, `GAINED_ENTITLEMENT`, `SUPPORT_GEOMETRY_CHANGED`, `LINEAGE_GEOMETRY_CHANGED`, `DEGRADED_AUTHORITY`, `AUGMENTED_AUTHORITY`.
- **`TIMELINE(c, valid_timestamps, t_k)`**: Computes chronological progression of entitlement states across valid time.
- **`AUDIT_CONFLICTS(t_v, t_k)`**: Lists active contradiction pairs.
