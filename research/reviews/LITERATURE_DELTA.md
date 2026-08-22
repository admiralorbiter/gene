# Literature Delta: GENE (2026-08-22)

## 1. Chen et al. (2022) / EDIN — *Entity Discovery and Indexing in Knowledge Bases* & "Learn to Not Link"

- **Connection class**: DIRECT
- **What it actually established**: Explicitly separates two distinct NIL / out-of-KB failure modes:
  1. Mentions where a real, novel entity exists in the source text but is absent from the knowledge base (requiring entity discovery and provisional clustering).
  2. Mentions that are non-entities, noisy spans, or unresolvable ambiguities (requiring unlinkable rejection).
- **Why it became relevant**: Maps directly onto the core Stage 8C-R2 architectural distinction:
  $$\text{Distinct entity exists but unindexed (Arm 1 provisional creation)} \ne \text{Insufficient evidence of entity (Arm 4A deferral)}$$
- **Hypothesis it suggests for us**: Grounding provisional entity creation on explicit textual existence indicators (e.g. deployment notices) prevents NIL unreachability without inflating false canonical linking.
- **What our evidence does NOT yet establish**: Whether this distinction generalizes to open-domain web corpus extraction without controlled hardware registry schemas.

---

## 2. Doyle (1979) — *A Truth Maintenance System* & de Kleer (1986) — *An Assumption-based TMS*

- **Connection class**: MECHANISTIC NEIGHBOR
- **What it actually established**: Tracks dependencies of non-monotonic assertions as hypotheses that can be revised, updated, or retracted upon receiving contradictory evidence without mutating base axioms.
- **Why it became relevant**: Provides theoretical foundation for the non-durable hypothesis ledger ($\mathcal{H}$), where multi-token composite candidates remain non-durable until Document 2 corroboration.
- **Hypothesis it suggests for us**: Treating ungrounded composite mentions as assumption-based hypotheses guarantees zero premature canonical corruption.
- **What our evidence does NOT yet establish**: Multi-document hypothesis chaining beyond two-document sequences.

---

## 3. Fowler (2015) / Kleppmann (2017) — *Event Sourcing & CQRS (Designing Data-Intensive Applications)*

- **Connection class**: ANALOGY (Architectural Analogy)
- **What it actually established**: Separates an append-only event log (source of truth) from derived materialized views that are deterministically projected via replay.
- **Why it became relevant**: In GENE, the document ingress stream is an immutable event log; the SQLite registry and hypothesis tables are verified derived projections.
- **Hypothesis it suggests for us**: State reconciliation across retargeting and disconfirmations is guaranteed bug-free if modeled as deterministic event log replay.
- **What our evidence does NOT yet establish**: Does not prove optimal indexing strategies for multi-gigabyte document streams.
