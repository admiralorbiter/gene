# AGENTS.md — GENE Development Contract

## Project

GENE = **Genealogical Epistemic Network Experiments**.

This repository is a research instrument. Correct measurement, replayability, and auditability take priority over feature count or framework sophistication.

Read before coding:

1. `README.md`
2. `docs/EXPERIMENTAL_PROTOCOL.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DEVELOPMENT_PLAN.md`

---

# Current objective

Implement only the infrastructure required to run **Experiment 0 (Lineage Observability)** and prepare the minimal paired path for **Experiment 1 (Single Mutation)**.

The first useful result is not a polished application. It is a trustworthy experimental trace showing:

```text
world -> source memories -> exposures -> model claim -> reported parents
      -> oracle evaluation -> counterfactual parent intervention -> comparison
```

---

# Frozen design constraints

Do not change these without recording a decision and explaining why.

- Synthetic fictional worlds come before real-world facts.
- Canonical ground truth is machine-readable and immutable.
- Experimental memory is append-only.
- Exposure lineage is recorded by the harness, not inferred by the model.
- Reported-support lineage is explicitly separate from causal lineage.
- Model self-reports are never treated as causal ground truth.
- Clean/mutated pairs must differ only at the declared mutation.
- World is the experimental unit.
- Experiment 0 precedes biological memory interventions.
- Raw prompts/responses and run metadata are preserved.
- Every reported result must resolve to a Git commit/tag + configuration + model digest.

---

# Do not build yet

Unless required to fix an identified measurement problem, do **not** add:

- web UI;
- Flask/FastAPI service;
- vector database;
- embedding retrieval;
- multi-agent orchestration;
- real-world search/fact checking;
- senescence;
- apoptosis;
- source-anchoring intervention;
- germline/somatic memory;
- autonomous experiment generation;
- multiple model providers;
- elaborate plugin architecture.

Keep future-policy interfaces simple enough that these can be added later.

---

# Implementation order

Work in this sequence.

## Milestone A — deterministic world/oracle

Implement:

- `Fact`, `Rule`, `World`, `Task`, `Mutation` schemas;
- one tiny hand-authored golden world;
- forward-chaining oracle;
- valid support-path enumeration;
- procedural world generator;
- deterministic natural-language renderer;
- clean/mutated pairing;
- D0/D1 task generation;
- unit + invariant/property tests.

### Stop and inspect when

The system can generate 10 worlds without an LLM and prove:

- same seed => same canonical world;
- all tasks have one valid benchmark answer under configured constraints;
- all declared support paths are recoverable;
- clean/mutated canonical pairs differ only as intended.

Do not continue if the oracle is uncertain.

## Milestone B — one fully auditable Ollama call

Implement:

- Ollama adapter;
- structured response schema;
- model metadata/digest capture;
- prompt/config hashing;
- raw request/response persistence;
- token/timing metadata where available;
- claim normalization + oracle evaluation.

### Stop and inspect when

One D0/D1 task can be replayed from stored artifacts and its output can be mechanically classified.

## Milestone C — lineage logging

Implement:

- append-only memory nodes;
- controlled support + distractor retrieval;
- exposure edges;
- reported parent IDs;
- reported-support edges;
- GraphML/CSV/JSONL export.

### Stop and inspect when

For any derived node we can answer exactly:

1. what memories were available;
2. which were actually exposed;
3. which parents the model reported;
4. what claim was written;
5. whether the claim is oracle-consistent.

## Milestone D — causal replay

Implement:

- replay from stored call metadata;
- parent removal;
- clean-counterpart replacement;
- counterfactual run persistence;
- normalized output comparison;
- strong/partial/none/indeterminate causal evidence labels.

### Stop and return evidence when

At least 3 manually inspectable cases exist:

- expected relevant parent changes result;
- irrelevant distractor does not materially change result;
- one ambiguous/stochastic case if present.

Do not hide indeterminate cases.

---

# Experiment discipline

During plumbing/debugging, prompt and schema changes are allowed. Every material change must increment a prompt/protocol/config version.

Once an experiment pilot is declared frozen:

- do not modify prompts mid-run;
- do not silently drop failed worlds;
- do not tune causal criteria after seeing aggregate results;
- do not rewrite the oracle to make model outputs count as correct;
- do not pool descendants as if they were independent worlds.

A negative or null result is a valid result.

---

# Coding preferences

Prefer explicit, testable code over framework magic.

Suggested conventions:

- Python 3.12+
- type hints on public interfaces;
- Pydantic or dataclasses for persisted schemas;
- SQLite with migrations;
- pytest;
- deterministic UUID/hash-derived IDs where useful;
- pure functions for world generation/oracle logic;
- dependency injection for model client/retrieval policy where it improves testing;
- no hidden global state.

Keep LLM calls behind one narrow adapter so tests can use deterministic fakes.

---

# Required tests before experimental runs

At minimum:

```text
world seed reproducibility
world serialization round-trip
rule closure correctness
support-path correctness
mutation-pair invariant
natural-language render stability
claim normalization cases
truth classification cases
append-only persistence
exposure logging exactness
reported-parent validation
replay preserves non-intervened inputs
metric calculation golden cases
```

Add small golden fixtures before adding complex procedural cases.

---

# Required run artifacts

Every completed run should be understandable without opening the source code.

Produce:

```text
manifest.json
world.json
mutation.json (when applicable)
calls.jsonl
memory_nodes.jsonl
claims.csv
exposure_edges.csv
reported_support_edges.csv
causal_tests.csv
metrics.json
lineage.graphml
```

Never overwrite a prior completed run directory.

---

# First feedback checkpoint

When Experiment 0 plumbing is runnable, stop broad development and prepare:

- 5–10 world run;
- aggregate lineage metrics;
- 3–5 example DAGs;
- raw artifacts for one good and one bad/ambiguous lineage report;
- at least one parent counterfactual;
- runtime/compute notes;
- failures and surprises;
- `docs/RESULTS_TEMPLATE.md` filled as far as possible.

The next design decision should be driven by those observations.

---

# Rule for unexpected discoveries

If an unexpected phenomenon appears, preserve it before fixing anything:

1. save the run;
2. add a minimal reproducer if possible;
3. record the commit/config/model digest;
4. describe the behavior without interpreting it prematurely;
5. only then change code or prompts.

Unexpected failures may be more valuable than expected success in GENE.
