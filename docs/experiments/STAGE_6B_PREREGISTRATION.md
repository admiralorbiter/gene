# Stage 6B Preregistration: Contract-Guided State Adjudication Factorial Benchmark

**Document URI**: `docs/experiments/STAGE_6B_PREREGISTRATION.md`  
**Milestone**: Exploration Round 6 (Stage 6B)  
**Parent Foundation**: `Stage 6A-v2` Bitemporal Engine  
**Dataset Artifact**: [`../../data/exploration_round6_stage6b_cases.jsonl`](../../data/exploration_round6_stage6b_cases.jsonl)  
**Manifest Hash**: `3281cd03590af7a1`  
**Compute Mode**: Deterministic Benchmark (Zero Live LLM Calls First)  
**Status**: Preregistered Protocol (Frozen)  

---

## 1. Research Problem & Scientific Motivation

Stage 6A-v2 implemented formal bitemporal state transition semantics given already-classified events (`SUPERSEDES(new, old)`, `RETRACT(f)`). 

However, persistent AI memory receives structured observation streams **without explicit event labels**. The runtime must solve **Contract-Guided State Adjudication**:
> *Given a newly observed proposition $(s, p, o, t_v)$ arriving at transaction time $t_k$ from $\text{source\_id}$, what exact state transition does this observation represent relative to the agent's existing memory?*

Crucially, **transition semantics cannot be inferred from value differences alone**—they depend fundamentally on the **predicate contract** and source relations:
- `"Alice lives in Chicago"` **supersedes** `"Alice lives in Kansas City"` because `primary_residence` is functional and time-varying.
- `"Alice speaks French"` **accumulates with** `"Alice speaks German"` because `certified_skill` is multivalued.
- `"Alice visited Tokyo"` **supersedes nothing** because `visited_facility` is an episodic occurrence.
- Contemporaneous reports from independent competing sources must trigger **unresolved conflict isolation**, not silent overwriting.

---

## 2. Input Observation Schema & Source Identity

Each incoming observation is structured as:
$$\text{Observation} = \langle \text{obs\_id}, s, p, o, t_v, t_k, \text{source\_id}, \text{origin\_id}, \text{lineage\_id} \rangle$$

- **`source_id`**: The declared author/authority identity (used to determine whether an update represents self-correction vs competing dispute).
- **`origin_id`**: The cryptographic sensor / agent identity.
- **`lineage_id`**: Ancestral root set $\mathcal{L}$.

---

## 3. Ground-Truth Predicate Contract Schema & Canonical Adjudication Rules

Each predicate $p$ in the ontology carries an immutable formal contract:
$$\text{PredicateContract}(p) = \langle \text{Cardinality}, \text{TemporalMode}, \text{SupersessionKey}, \text{ConflictPolicy} \rangle$$

```
+========================================================================================================================+
|                                    PREDICATE ONTOLOGY CONTRACTS (STAGE 6B)                                            |
+======================+================+===================+========================+===================================+
| Predicate Category   | Cardinality    | Temporal Mode     | Supersession Key       | Conflict Policy                   |
+======================+================+===================+========================+===================================+
| Functional Residence | SINGLE (1:1)   | TIME_VARYING      | (subject, predicate)   | ISOLATE contemporaneous conflicts |
| (`primary_residence`)|                |                   |                        |                                   |
+----------------------+----------------+-------------------+------------------------+-----------------------------------+
| Multivalued Skills   | MULTI (1:N)    | ADDITIVE          | NONE (accumulate)      | ALLOW concurrent values           |
| (`certified_skill`)  |                |                   |                        |                                   |
+----------------------+----------------+-------------------+------------------------+-----------------------------------+
| Episodic Activity    | MULTI (1:N)    | EPISODIC (Points) | NONE (event occurrences| ALLOW overlapping events          |
| (`visited_facility`) |                |                   |                        |                                   |
+----------------------+----------------+-------------------+------------------------+-----------------------------------+
| Interval Validity    | SINGLE (1:1)   | INTERVAL_BOUNDED  | (subject, predicate)   | EXPIRE on window boundary         |
| (`security_clearance`|                |                   |                        |                                   |
+======================+================+===================+========================+===================================+
```

### Canonical Adjudication Decision Logic:
1. **Functional Time-Varying**:
   - Later valid time ($t_v > t_{\text{prev}}$): Emit `ASSERT(new)` + `SUPERSEDES(new, old)`.
   - Contemporaneous ($t_v = t_{\text{prev}}$), same source: Emit `ASSERT(new)` + `SUPERSEDES(new, old)` (correction).
   - Contemporaneous ($t_v = t_{\text{prev}}$), independent source: Emit `ASSERT(new)` + `CONTRADICTS(new, old)`.
2. **Multivalued Additive**: Emit `ASSERT(new)` without supersession.
3. **Episodic Point**: Emit `ASSERT(new_occ)` preserving all past episodes.
4. **Interval-Bounded**: Emit `ASSERT(new, [t_v, t_v + \Delta t))`; emit `SUPERSEDES(new, old)` if replacing prior active interval.

---

## 4. Evaluated Memory Policy Arms (Zero LLM Compute)

We evaluate 6 candidate memory architectures on the factorial benchmark of 200 synthetic observation streams:

1. **`ARM_1_APPEND_ONLY`**: Appends all incoming observations naively without modification.
2. **`ARM_2_KNOWLEDGE_TIME_LWW`**: Last-Write-Wins based on transaction time $t_k$.
3. **`ARM_3_VALID_TIME_LWW`**: Last-Write-Wins based on occurrence time $t_v$.
4. **`ARM_4_BITEMPORAL_LATEST`**: Selects highest $(t_v, t_k)$ tuple.
5. **`ARM_5_PREDICATE_CONTRACT_ADJUDICATOR`**: Uses predicate contracts to generate typed events (`ADD`, `SUPERSEDES`, `CONTRADICTS`), but maintains a flat dependency graph.
6. **`ARM_6_GENE_KERNEL`**: Predicate contract adjudication $+$ Bitemporal Engine $+$ Antichain Support Maintenance $+$ Lineage Action Governance.

---

## 5. Factorial Benchmark Dataset Structure ($N=200$)

The frozen dataset spans:
$$4 \text{ PredicateModes} \times 5 \text{ UpdatePatterns} \times 2 \text{ SourceRelations} \times 5 \text{ SupportTopologies} = 200 \text{ cases}$$

- **Predicate Modes**: `functional_time_varying`, `multivalued_additive`, `episodic_point`, `interval_bounded`
- **Update Patterns**: `forward_update`, `delayed_report`, `retroactive_correction`, `contemporaneous_disagreement`, `recurrence_expiry`
- **Source Relations**: `same_source`, `independent_source`
- **Support Topologies**: `direct_fact`, `single_derived_path`, `independent_alternatives`, `shared_premise_alternatives`, `recombinant_paths`

---

## 6. Evaluation Metrics & Primary Failure Modes

1. **Stale Retention Rate ($R_{\text{stale}}$)**: Prior functional values incorrectly surviving after a superseding update.
2. **False Supersession Rate ($R_{\text{false\_sup}}$)**: Multivalued skills or historical episodes incorrectly wiped out by a subsequent observation.
3. **Downstream Revision Autoimmunity ($R_{\text{autoimmune}}$)**: Still-valid multi-path derived conclusions falsely retracted when an unshared premise is revised.
4. **Zombie Retention Rate ($R_{\text{zombie}}$)**: Invalidated derived conclusions falsely retained due to flat dependency leakage.
5. **Exact Support Fidelity ($F_{\mathcal{S}}$)**: Balanced accuracy against ground-truth $\mathcal{S}(c)$ and $\mathcal{S}_L(c)$.
