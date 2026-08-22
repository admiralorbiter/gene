# Literature Delta: GENE (2026-08-22)

### 1. Doyle (1979) — *A Truth Maintenance System* & de Kleer (1986) — *An Assumption-based TMS*
- **Relevance**: Formalizes how epistemic hypotheses can be tracked as non-monotonic assumptions and revised or retracted upon contradiction without polluting base knowledge.
- **Connection to GENE**: Directly justifies the architecture of the non-durable hypothesis ledger ($\mathcal{H}$).

### 2. Getoor & Machanavajjhala (2012) — *Entity Resolution: Theory, Practice & Open Challenges*
- **Relevance**: Distinguishes deterministic identity clustering from provisional clustering under uncertainty.
- **Connection to GENE**: Supports the two-stage separation of existence establishment (clustering) from canonical identity registration (linking).

### 3. Fowler (2015) / Kleppmann (2017) — *Designing Data-Intensive Applications: Event Sourcing & Derived Data*
- **Relevance**: Immutable event streams with deterministic projection functions ensure reproducible state and zero-residue retargeting.
- **Connection to GENE**: Document ingress is an immutable event log; SQLite tables are verified materialized projections.
