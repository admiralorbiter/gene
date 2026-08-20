# GENE Technical Architecture

## 1. Design goal

The architecture should make experimental state **observable, immutable where necessary, reproducible, and easy to perturb**.

Prefer a boring Python harness over a complex agent framework. The experiment is the product.

Initial stack:

- Python 3.12+
- Ollama local API
- Pydantic/dataclasses for schemas
- SQLite for append-only experimental records
- NetworkX optional for lineage analysis/visualization
- pandas/Polars optional for analysis exports
- pytest + property-based tests for world/oracle invariants

A vector database is intentionally excluded from v0.

---

# 2. System layers

```text
Synthetic World Generator
        ↓
Immutable Ground-Truth Oracle
        ↓
Natural-Language Renderer
        ↓
Experiment Scheduler
        ↓
Memory Retrieval ────────┐
        ↓                 │
Ollama Model Call         │
        ↓                 │
Structured Claim Parser   │
        ↓                 │
Oracle Evaluation         │
        ↓                 │
Memory Writer ────────────┘
        ↓
Lineage Recorder
        ↓
Counterfactual Causal Runner
        ↓
Metrics + Export
```

---

# 3. Two stores, never one

GENE needs a hard distinction between truth and model memory.

## 3.1 Ground-truth ledger

Immutable after world generation.

Contains:

- entities;
- canonical facts;
- derivation rules;
- valid task answers;
- mutation specification;
- clean/mutated render mappings.

The model never edits this ledger.

## 3.2 Experimental memory store

Mutable only through append operations.

Contains what the experimental system has been shown or has generated.

Incorrect claims are preserved exactly rather than overwritten so lineage can be reconstructed later.

---

# 4. Suggested data model

SQLite is sufficient initially. Use foreign keys and migrations from day one.

## worlds

```text
world_id TEXT PK
world_seed INTEGER
world_version TEXT
canonical_json TEXT
created_at TEXT
validation_hash TEXT
```

## world_facts

```text
fact_id TEXT PK
world_id TEXT FK
subject TEXT
predicate TEXT
object TEXT
truth_value INTEGER
source_type TEXT       # generated | derived
canonical_json TEXT
```

## rules

```text
rule_id TEXT PK
world_id TEXT FK
rule_json TEXT
rule_depth INTEGER
```

## mutations

```text
mutation_id TEXT PK
world_id TEXT FK
true_fact_id TEXT FK
mutated_subject TEXT
mutated_predicate TEXT
mutated_object TEXT
mutation_type TEXT
```

## runs

```text
run_id TEXT PK
experiment_name TEXT
experiment_version TEXT
condition TEXT          # clean | mutated | later intervention names
world_id TEXT FK
model_name TEXT
model_digest TEXT
ollama_version TEXT
seed INTEGER
num_ctx INTEGER
temperature REAL
prompt_version TEXT
prompt_hash TEXT
retrieval_policy TEXT
memory_policy TEXT
git_commit TEXT
started_at TEXT
completed_at TEXT
status TEXT
```

## calls

```text
call_id TEXT PK
run_id TEXT FK
generation INTEGER
task_id TEXT
request_json TEXT
response_text TEXT
response_json TEXT
prompt_tokens INTEGER
completion_tokens INTEGER
latency_ms REAL
created_at TEXT
```

## memory_nodes

```text
node_id TEXT PK
run_id TEXT FK
world_id TEXT FK
generation INTEGER
node_type TEXT          # source | derived | repair | etc.
natural_text TEXT
structured_json TEXT
reproductive_status TEXT DEFAULT 'active'
created_by_call_id TEXT FK
created_at TEXT
```

## claims

```text
claim_id TEXT PK
node_id TEXT FK
subject TEXT
predicate TEXT
object TEXT
parse_status TEXT
truth_status TEXT        # true | false | unsupported | contradiction | unknown
infection_status TEXT    # clean | infected | repaired | de_novo | unresolved
oracle_evidence_json TEXT
```

## exposure_edges

```text
parent_node_id TEXT FK
child_node_id TEXT FK
call_id TEXT FK
retrieval_rank INTEGER
context_position INTEGER
PRIMARY KEY(parent_node_id, child_node_id, call_id)
```

## reported_support_edges

```text
parent_node_id TEXT FK
child_node_id TEXT FK
call_id TEXT FK
reported_role TEXT
PRIMARY KEY(parent_node_id, child_node_id, call_id)
```

## causal_tests

```text
causal_test_id TEXT PK
parent_node_id TEXT FK
child_node_id TEXT FK
original_call_id TEXT FK
intervention_type TEXT   # remove | replace_clean | replace_other
intervention_seed INTEGER
counterfactual_call_id TEXT FK
outcome TEXT             # strong | partial | none | indeterminate
score REAL
comparison_json TEXT
```

## evaluations

```text
evaluation_id TEXT PK
run_id TEXT FK
scope_type TEXT          # claim | node | generation | run
scope_id TEXT
metric_name TEXT
metric_value REAL
metric_json TEXT
created_at TEXT
```

---

# 5. World object

A world should serialize to one canonical JSON object so it can be recreated exactly.

Example shape:

```json
{
  "world_id": "world_0042",
  "world_seed": 42,
  "entities": {
    "people": ["NERIN", "TAL", "SOREN"],
    "stations": ["VELORA"],
    "sectors": ["SECTOR_K"],
    "protocols": ["GREEN", "AMBER"]
  },
  "facts": [
    ["VELORA", "manager", "NERIN"],
    ["NERIN", "reports_to", "TAL"]
  ],
  "rules": [
    {
      "if": [
        ["?station", "manager", "?person"],
        ["?person", "reports_to", "TAL"]
      ],
      "then": ["?station", "uses_protocol", "GREEN"]
    }
  ],
  "mutation": {
    "replace": ["VELORA", "manager", "NERIN"],
    "with": ["VELORA", "manager", "SOREN"]
  }
}
```

Natural-language renderings should be generated separately so canonical truth does not depend on phrasing.

---

# 6. Model contract

Use structured output from the beginning.

Conceptual response schema:

```json
{
  "answer": {
    "subject": "VELORA",
    "predicate": "uses_protocol",
    "object": "GREEN"
  },
  "parent_memory_ids": ["mem_001", "mem_007"],
  "confidence": 0.86,
  "explanation": "..."
}
```

`explanation` is optional observational data. Do not use free-form reasoning as the truth source for lineage.

The harness itself supplies exposure IDs, so the model cannot hide which memories were actually presented.

---

# 7. Retrieval policy v0

Avoid embeddings initially.

Experiment 0 requires known support sets, so use controlled retrieval:

```text
required support memories
+ N deterministic distractor memories
```

Record:

- full candidate set;
- selected set;
- order;
- ranks;
- support/distractor labels known only to the harness.

Later experiments can introduce lexical, BM25, embedding, or learned retrieval as explicit treatments.

---

# 8. Oracle evaluation

The oracle should answer at least four questions mechanically:

1. Is the normalized claim true in the canonical world?
2. Is it false/contradictory?
3. Is it derivable from canonical facts/rules?
4. What minimal valid support sets exist for the target claim?

For v0, keep the rule language limited enough that forward chaining can enumerate the closure and derivation paths exactly.

Store all valid derivation paths where tractable; this prevents falsely labeling an alternative valid parent as unsupported.

---

# 9. Infection evaluation

Truth status and infection status are separate.

A false claim is not automatically infected.

Proposed v0 logic:

```text
if claim is false and causal ancestry reaches mutation seed:
    infected
elif claim is false and no causal ancestry reaches mutation seed:
    de_novo
elif claim is true and causal ancestry reaches an infected parent:
    repaired
elif claim is true:
    clean
else:
    unresolved
```

Because causal edges are sampled rather than always exhaustive, `unresolved` is necessary.

---

# 10. Causal runner

The causal runner should be able to replay a call from stored metadata.

Conceptual API:

```python
result = causal_runner.replay(
    original_call_id="call_123",
    intervention={
        "type": "replace_clean",
        "target_memory_id": "mem_17"
    },
    seed=7,
)
```

It should:

- reconstruct the exact prompt template;
- preserve non-target context order;
- preserve model/runtime settings;
- substitute/remove the target memory;
- log the new call independently;
- compare normalized outputs;
- never overwrite the original run.

---

# 11. Determinism and reproducibility

Full LLM determinism may not always be achievable across hardware/runtime versions. GENE should therefore distinguish:

- **world determinism** — must be exact;
- **prompt determinism** — must be exact given stored config;
- **retrieval determinism** — must be exact for v0;
- **model-call determinism** — characterize empirically.

Hash at minimum:

- canonical world JSON;
- rendered memory content;
- prompt template;
- complete call request;
- model digest.

---

# 12. File outputs per run

Even with SQLite, create an easily inspectable run artifact:

```text
runs/<run_id>/
├── manifest.json
├── world.json
├── mutation.json
├── calls.jsonl
├── memory_nodes.jsonl
├── exposure_edges.csv
├── reported_support_edges.csv
├── causal_tests.csv
├── claims.csv
├── metrics.json
└── lineage.graphml
```

This makes debugging and external analysis easier than requiring direct database access.

---

# 13. Minimum visualization

Do not build a UI.

Generate static analysis artifacts later:

- lineage DAG;
- node label = normalized claim;
- generation on x-axis;
- truth/infection state encoded in attributes;
- edge type = exposure/reported/causal;
- a small generation-level reproduction table.

GraphML should be considered the canonical graph export; PNG/SVG can be generated for inspection.

---

# 14. Testing requirements

## Unit tests

- canonical fact parsing;
- rule evaluation;
- world serialization;
- mutation pairing;
- claim normalization;
- truth classification;
- database append behavior;
- metric calculations.

## Property/invariant tests

- same `world_seed` => same canonical world;
- clean and mutated pair differ only at declared mutation representation;
- world generator never emits contradictory facts unless configured;
- every task has at least one oracle-valid answer;
- every declared known-chain task has expected support path;
- no memory node changes after persistence;
- replay preserves all non-intervened request components.

## Golden tests

Keep several tiny hand-authored worlds with expected derivation closures and lineage answers. These should remain stable even if the procedural generator changes.

---

# 15. Architectural rule for later biological experiments

Later policies should be implemented as replaceable **memory-governance layers**, not baked into the base store.

Future interface might resemble:

```python
class ReproductionPolicy:
    def can_retrieve(node, context) -> bool: ...
    def can_write(claim, evidence) -> bool: ...
    def requires_revalidation(node, context) -> bool: ...
    def post_generation_update(node, outcomes) -> None: ...
```

Potential policies:

- unrestricted baseline;
- source anchoring;
- write proofreading;
- lineage-gated reproduction;
- senescence;
- apoptosis;
- germline/somatic promotion.

Do not implement these until baseline lineage behavior is validated.

---

# 16. Methodological Principles & Backlog

### 16.1 Frozen Methodological Principles

1. **Causal-Role Equivariance**:
   Whenever treatment and control identities can be reversed (e.g. Station A = Healthy, Station B = Infected), always evaluate both forward ($A \to B$) and swapped ($B \to A$) configurations. Any true causal effect must follow the causal role rather than the lexical or token identity.
2. **Representation is Not Lineage Identity**:
   Causal descent is established interventionally and derivationally through the ancestry graph, not by lexical similarity, embedding cosine distance, or coordinate persistence. Lineage identity is a causal relation, not a similarity relation.
3. **Readout Validation Principle**:
   Failure of a reporting interface is not evidence that the underlying information state is absent unless the readout channel itself has been independently validated. An interface failure must never be conflated with an information-state failure.

### 16.2 Inactive Methodology Backlog (Do Not Build Yet)

1. **Reported-Lineage Identifier Equivariance Diagnostic**:
   Hold semantic evidence constant, remap model-facing parent labels/order (e.g. `mem_17 -> KAVO`, `mem_22 -> RILEN` vs `mem_17 -> ZURI`, `mem_22 -> TELO`), unmap responses, and quantify $E_{\text{ID}} = 1 - \text{agreement}$ across arbitrary labelings.
2. **Transformation-Depth Assay**:
   Measure how many semantic transformations a lineage can undergo before ancestral decoding or causal attribution becomes unreliable ($F_g = \prod_{i=1}^g f_i$).
3. **Interventional vs Structural Parenthood Under Complex Transformations**:
   Define parenthood interventionally rather than logging-structurally when summaries or multi-hop tools merge disparate parent nodes.

---

# 17. Two-Layer Epistemic Architecture & Replay Stability

### 17.1 Replay Stability Principle
> **Fixed prompt + temperature 0 + fixed seed cannot be assumed deterministic without empirical verification on that execution stack.**
In local Ollama / GPU execution runtimes, backend numerical non-determinism, thread scheduling, and kernel execution can produce observable response branching under bit-for-bit identical input strings. Repeated invocations must be reported as empirical sample frequencies across observed execution counts, not assumed as deterministic identities or stable parameter distributions.

### 17.2 Two-Layer Epistemic Defense Architecture
Epistemic reliability in multi-agent and reasoning ecologies requires two structurally distinct defense layers:

1. **Layer 1 — Memory Governance (Lineage Intervention)**:
   - **Function**: Controls reproductive access to information lineages based on ancestry tracking and external risk signals.
   - **Mechanism**: Prunes derivation edges or quarantines transitive descendant families when an ancestor is discredited.
   - **Failure Mode**: Provenance laundering (if node-only filtering is used) or epistemic autoimmunity (if false alarms prune healthy lineages).
2. **Layer 2 — Inference Integrity (Epistemic Proofreading)**:
   - **Function**: Prevents downstream reasoning engines from manufacturing unsupported pseudo-paths from surviving, unquarantined evidence.
   - **Mechanism**: Verifies that cited memory nodes structurally and semantically unify with the antecedent clauses of the triggered deductive rules before admitting outputs to memory.
   - **Failure Mode**: Pseudo-path formation, cross-entity variable binding failure, and unsupported concrete assertions.

### 17.3 Decoupled Phenotypic Ontology
Reproductive outcome must be decoupled from epistemic state:
- **Reproductive Status**:
  - `active`: Concrete claim emitted with sufficient evidence status (eligible for memory storage and reproduction).
  - `inactive`: Abstention / UNKNOWN emitted or insufficient evidence status (quarantined from reproductive storage).
- **Epistemic State Vector $(T^*, D_{\text{ctx}}, A, E, K)$**:
  - `healthy`: $(1, 1, 1, 1, 1)$ — Globally true in $W^*$, locally warranted by context $D_{\text{ctx}}=1$.
  - `semantic`: $(0, 1, 1, 1, 1)$ — Globally false in $W^*$, but locally derivable from mutated context $D_{\text{ctx}}=1$.
  - `epistemic`: $(1, 0, 0, 0, 1)$ — Locally underivable ($D_{\text{ctx}}=0$), but happens to match canonical ground truth ($T^*=1$).
  - `de_novo_error`: $(0, 0, 0, 0, 1)$ — Locally underivable ($D_{\text{ctx}}=0$) and globally false ($T^*=0$).
  - `clean_abstention`: $(1, 0, 1, 1, 1)$ — Locally underivable ($D_{\text{ctx}}=0$), model correctly abstains with UNKNOWN and claims insufficient evidence.
  - `contract_failure`: $(1, 0, 1, 0, 0)$ or $(0, 0, 1, 0, 0)$ — Model abstains with UNKNOWN but claims sufficient evidence or violates schema contract.


