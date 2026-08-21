# Exploration Round 7 Stage 7A.1 Report: Epistemic Ingress, Orthogonal Failure Channels, and Stateful Benchmark Assay

**Document Status**: Canonical Empirical Report (Stage 7A.1 Post-Review Hardening)  
**Author**: Antigravity Research / GENE Core  
**Associated Target Commit**: `round7-stage7a-postreview-freeze`  
**Prerequisites**: Exploration Round 7 Wave 0.2 Freeze ([`round7-wave0-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round7-wave0-freeze)), Stage 7A v0 Implementation ([`70b014c`](https://github.com/admiralorbiter/gene/commit/70b014c))  
**Primary Artifact**: [`data/exploration_round7_stage7a_benchmark_summary.json`](../../data/exploration_round7_stage7a_benchmark_summary.json) (`SHA-256: a903aad2c7219e9309bb576beaf5cc83fe5ae5fac210d812a219e1d746186495`)  

---

## 1. Executive Summary & Provenance Disambiguation

Exploration Round 7 investigates the boundary condition of durable epistemic storage:
> *What proof, authority, and referential guarantees must accompany incoming assertions before persistent memory is allowed to believe them?*

### 1.1 Provenance Distinctions
- **`70b014c`**: Initial Stage 7A implementation and baseline benchmark execution.
- **`4de56af` (`round7-stage7a-execution-freeze`)**: Initial repository freeze state (including an isolated Experiment 0 memory node-ID collision fix).
- **`round7-stage7a-postreview-freeze`**: Stage 7A.1 post-review hardened state containing runtime-derived `TrustedSourceContext`, multimap alias candidate indexing, object-level provisional tracking, first-class lifecycle operations, stateful baseline bitemporal seeding, and formal 4-probe evaluation.

---

## 2. Core Architectural Discoveries

### 2.1 The Orthogonality of Referential and Authorization Correctness
$$\text{Referential Correctness} \not\equiv \text{Authorization Correctness}$$

Stage 7A demonstrates that candidate ambiguity preservation and authorization gating address orthogonal failure classes. Neither subsumes the other:
1. **Candidate Preservation Alone (`A2`)**: Eliminates candidate ambiguity and novelty collapse ($\text{UPR} = 100.0\%$, $\text{FDAR}_{\text{ambiguity}} = 0.0\%$, $\text{FDAR}_{\text{novel}} = 0.0\%$), but suffers $100.0\%$ False Durable Admission on resolved unauthorized claims ($\text{FDAR}_{\text{authority}\mid\text{resolved}} = 36/36 = 100.0\%$).
2. **Authority Gating Alone (`A3`)**: Perfectly eliminates unauthorized root promotions ($\text{FDAR}_{\text{authority}} = 0.0\%$), but prematurely collapses $100.0\%$ of authorized candidate collisions to Top-1 ($\text{FDAR}_{\text{ambiguity}\mid\text{authorized}} = 12/12 = 100.0\%$, $\text{UPR} = 0.0\%$).
3. **Full Proof-Carrying Ingress (`A4`)**: Unifies hypothesis preservation ($\mathcal{B}(x) = \{b_1, \dots, b_k\}$ under `DEFERRED_BINDING`), `PROVISIONAL_ENTITY` tracking, capability-scoped authorization, and standalone certificate verification, achieving $\mathbf{100.0\% \text{ WorldPass}}$, $\mathbf{\text{FDAR} = 0.0\%}$, $\mathbf{\text{SAC} = 100.0\%}$, and $\mathbf{\text{UPR} = 100.0\%}$.

```
+================================================================================================================+
|                       STAGE 7A.1 FACTORIAL INGRESS BENCHMARK (N=120 WORLDS / 480 PROBES)                       |
+=========================+==============+==============+==================+==================+==================+
| Architecture Arm        | WorldPass    | Global FDAR  | Cond. Auth FDAR  | Cond. Ambig FDAR | SAC / UPR        |
+=========================+==============+==============+==================+==================+==================+
| A0: Top-1 Blind Write   | 58.3% (70)   | 71.4% (60/84)| 100.0% (48/48)   | 100.0% (12/12)   | 100% / 0%        |
| A1: Canonicalize Only   | 58.3% (70)   | 71.4% (60/84)| 100.0% (48/48)   | 100.0% (12/12)   | 100% / 0%        |
| A2: Candidate-Aware     | 75.0% (90)   | 42.9% (36/84)| 100.0% (36/36)   | 0.0% (0/12)      | 100% / 100%      |
| A3: Authority-Aware     | 91.7% (110)  | 14.3% (12/84)| 0.0% (0/48)      | 100.0% (12/12)   | 100% / 0%        |
| A4: Full GENE Ingress   | 100.0% (120) | 0.0% (0/84)  | 0.0% (0/48)      | 0.0% (0/12)      | 100% / 100%      |
+=========================+==============+==============+==================+==================+==================+
```

---

## 3. Ingress Trust Boundary & Hardened Architecture

### 3.1 Runtime-Derived `TrustedSourceContext`
A critical discovery in Stage 7A is that `SourceContext` cannot be supplied as an external assertion. The ingress runtime strictly derives trusted context:
$$\text{SourceRecord} + \text{AuthenticatedOrigin} + \text{CapabilityRegistry} \xrightarrow{\text{derive}} \text{TrustedSourceContext}$$
- **Origin Spoofing Detection**: If `ClaimedOrigin.claimed_source_name != AuthenticatedOrigin.verified_id`, the runtime flags spoofing and strips root fact privileges.
- **Privilege Enforcement**: Sources with `max_claim_privilege = ATTESTATION_ONLY` (such as neural cognitive steps or third-party web text) are strictly prevented from gaining `ROOT_FACT` admission.

### 3.2 Candidate Multimap & Novelty Representation
- `IngressOntology` implements an alias multimap (`alias -> set[entity_id]`), ensuring ambiguous mentions dynamically yield all competing candidate hypotheses rather than singleton overwrites.
- `A4` tracks novel objects as well as novel subjects under `PROVISIONAL_ENTITY` and `PROVISIONAL_RELATION`.

### 3.3 Explicit Lifecycle Operations
- `resolve_deferred_binding(deferred_id, resolved_subject, resolved_object)`: Prunes candidate sets on the original preserved `DeferredBinding` and admits the fact under original `SourceRecord` provenance roots without reparsing raw text.
- `promote_provisional_entity(provisional_id, canonical_id)`: Registers the canonical entity in the domain ontology, closes provisional status, and atomically retargets all provisional relations while preserving original sensor provenance roots.

---

## 4. Stateful 120-World Benchmark & Formal 4-Probe Evaluation

Each benchmark world seeds an initial baseline occurrence ($t_v \in [0.0, 5.0), t_k=1$) to evaluate real transition semantics:
- **`FORWARD_UPDATE`**: Candidate arrives at $t_v=5.0$, superseding baseline at $t_v=5.0$.
- **`RETROACTIVE_BACKFILL`**: Candidate arrives at $t_v \in [1.0, 3.0)$, retroactively updating within the baseline interval.
- **`CONTEMPORANEOUS_DISPUTE`**: Candidate arrives at $t_v=0.0$ with conflicting object value, creating active bitemporal contradiction under single cardinality.

### The Four Formal Downstream Probes:
1. **$Q_1$ (Bitemporal State Probe)**: Evaluates whether active facts in `b_engine.get_active_facts(t_v, 2)` match exact ground truth (including cautious isolation under contemporaneous dispute).
2. **$Q_2$ (Structured Premise Challenge via $\mathcal{S}_t$)**: Evaluates whether `b_engine.why_t(query_triple, t_v, 2)` returns valid, minimal antichain support without unadmitted premises.
3. **$Q_3$ (Action Governance via $\text{Auth}(\mathcal{S}_L)$)**: Verifies that downstream action authority is granted ($\text{Auth} = 1.0$) if and only if valid entitlement holds with authentic lineage (`ROOT_NET_1`).
4. **$Q_4$ (Causal Invalidation via $\text{WHAT\_IF}$)**: Evaluates `b_engine.what_if_t(query_triple, RETRACT(cand_fact))` to confirm that counterfactually retracting candidate observations cleanly restores baseline state.

---

## 5. Verification & Preflight Integrity

- **Automated Tests**: 193 total tests passed in 24.64s (`pytest -v`).
- **Reproducibility Suite**: `scripts/verify_repo.py` verified 100% clean with zero worktree drift.
- **Ledger & Atlas Sync**: `data/claim_ledger.json` and `docs/atlas/data/claims.json` updated with `GENE-C16`.
