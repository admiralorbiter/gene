# Stage 6B Preregistration: Implicit State Adjudication & Predicate Transition Semantics

**Document URI**: `docs/experiments/STAGE_6B_PREREGISTRATION.md`  
**Milestone**: Exploration Round 6 (Stage 6B)  
**Parent Foundation**: `Stage 6A-v2` Bitemporal Engine  
**Compute Mode**: Deterministic Benchmark (Zero Live LLM Calls First)  
**Status**: Preregistered Protocol  

---

## 1. Research Problem & Scientific Motivation

Stage 6A-v2 implemented the formal bitemporal state transition semantics given already-classified events (`SUPERSEDES(new, old)`, `RETRACT(f)`). 

However, persistent AI memory receives natural language or structured observation streams **without explicit event labels**. The runtime must solve **Implicit State Adjudication**:
> *Given a newly observed proposition $(s, p, o, t_v)$ arriving at knowledge time $t_k$, what exact state transition does this observation represent relative to the agent's existing memory?*

Crucially, **transition semantics cannot be inferred from value differences alone**—they depend fundamentally on the **predicate contract**:
- `"Alice lives in Chicago"` **supersedes** `"Alice lives in Kansas City"` because `lives_in` is functional and time-varying.
- `"Alice speaks French"` **accumulates with** `"Alice speaks German"` because `speaks_language` is multivalued.
- `"Alice visited Tokyo"` **supersedes nothing** because `visited_city` is an episodic occurrence.
- Contradictory contemporaneous reports from competing sources must trigger **unresolved conflict isolation**, not silent overwriting.

---

## 2. Ground-Truth Predicate Contract Schema

Each predicate $p$ in the ontology carries an immutable formal contract:
$$\text{PredicateContract}(p) = \langle \text{Cardinality}, \text{TemporalMode}, \text{SupersessionKey}, \text{ConflictPolicy} \rangle$$

```
+========================================================================================================================+
|                                    PREDICATE ONTOLOGY CONTRACTS (STAGE 6B)                                            |
+======================+================+===================+========================+===================================+
| Predicate Category   | Cardinality    | Temporal Mode     | Supersession Key       | Conflict Policy                   |
+======================+================+===================+========================+===================================+
| Functional Residence | SINGLE (1:1)   | TIME_VARYING      | (subject, predicate)   | ISOLATE contemporaneous conflicts |
| (`lives_in`, `role`) |                |                   |                        |                                   |
+----------------------+----------------+-------------------+------------------------+-----------------------------------+
| Multivalued Skills   | MULTI (1:N)    | ADDITIVE          | NONE (accumulate)      | ALLOW concurrent values           |
| (`skills`, `topics`) |                |                   |                        |                                   |
+----------------------+----------------+-------------------+------------------------+-----------------------------------+
| Episodic Activity    | MULTI (1:N)    | EPISODIC (Points) | NONE (event occurrences| ALLOW overlapping events          |
| (`visited`, `saw`)   |                |                   |                        |                                   |
+----------------------+----------------+-------------------+------------------------+-----------------------------------+
| Interval Validity    | SINGLE (1:1)   | INTERVAL_BOUNDED  | (subject, predicate)   | EXPIRE on window boundary         |
| (`clearance_tier`)   |                |                   |                        |                                   |
+======================+================+===================+========================+===================================+
```

---

## 3. Evaluated Memory Policy Arms (Zero LLM Compute)

We evaluate 6 candidate memory architectures on a factorial suite of 200 synthetic observation streams:

1. **`ARM_1_APPEND_ONLY`**: Appends all incoming observations naively without modification.
2. **`ARM_2_KNOWLEDGE_TIME_LWW`**: Last-Write-Wins based on transaction time $t_k$.
3. **`ARM_3_VALID_TIME_LWW`**: Last-Write-Wins based on occurrence time $t_v$.
4. **`ARM_4_BITEMPORAL_LATEST`**: Selects highest $(t_v, t_k)$ tuple.
5. **`ARM_5_PREDICATE_CONTRACT_ADJUDICATOR`**: Uses predicate contracts to generate typed events (`ADD`, `SUPERSEDES`, `CONTRADICTS`), but maintains a flat dependency graph.
6. **`ARM_6_GENE_KERNEL`**: Predicate contract adjudication $+$ Bitemporal Engine $+$ Antichain Support Maintenance $+$ Lineage Action Governance.

---

## 4. Evaluation Metrics & Primary Failure Modes

1. **Stale Retention Rate ($R_{\text{stale}}$)**: Prior functional values incorrectly surviving after a superseding update.
2. **False Supersession Rate ($R_{\text{false\_sup}}$)**: Multivalued skills or historical episodes incorrectly wiped out by a subsequent observation.
3. **Downstream Revision Autoimmunity ($R_{\text{autoimmune}}$)**: Still-valid multi-path derived conclusions falsely retracted when an unshared premise is revised.
4. **Zombie Retention Rate ($R_{\text{zombie}}$)**: Invalidated derived conclusions falsely retained due to flat dependency leakage.
5. **Exact Support Fidelity ($F_{\mathcal{S}}$)**: Balanced accuracy against ground-truth $\mathcal{S}(c)$ and $\mathcal{S}_L(c)$.
