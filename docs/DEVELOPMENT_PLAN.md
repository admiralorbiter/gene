# GENE Development Plan

## Objective

Get from an empty repository to trustworthy first results with the fewest moving parts possible.

The plan is intentionally gated. Fast development is welcome, but later features should not outrun the validity of the measurement system.

---

# Phase 0 — Repository and invariants

## Deliverables

- Python package scaffold;
- configuration loader;
- SQLite schema/migrations;
- run manifest format;
- deterministic ID strategy;
- test harness;
- one hand-authored golden world.

## Exit criteria

- project installs cleanly;
- tests run in one command;
- one empty experiment run can create a manifest/database record;
- commit hash and runtime metadata are captured.

---

# Phase 1 — Synthetic world + oracle

## Build

1. canonical entity/fact schemas;
2. tiny rule language;
3. forward-chaining oracle;
4. deterministic procedural world generator;
5. clean/mutated pair generator;
6. natural-language renderer;
7. task generator for D0 and D1 queries.

## Required tests

- seed reproducibility;
- no accidental contradictions;
- expected closure of rules;
- pair differs only at declared mutation;
- every generated task is oracle-answerable;
- minimal/valid support paths can be recovered.

## Human audit

Print 10 generated worlds in human-readable form and inspect them before adding the LLM.

## Exit criteria

You trust the world/oracle even if no LLM exists.

---

# Phase 2 — Ollama adapter

## Build

- model discovery/metadata capture;
- one chat/generate call path;
- structured JSON response schema;
- retry/error handling;
- token/timing metadata capture;
- prompt template versioning and hashing.

## First model

Use one model that is comfortably fast on the available machine. The exact model is less important than keeping it frozen during initial instrumentation work.

Suggested families for later replication:

- Qwen3 small/medium;
- Gemma 3 small/medium;
- one larger cross-family model if hardware permits.

Do not start by comparing many models.

## Exit criteria

A generated D0/D1 task can be answered through Ollama, parsed into the canonical schema, evaluated by the oracle, and exactly logged.

---

# Phase 3 — Memory and lineage instrumentation

## Build

- append-only memory nodes;
- controlled retrieval;
- exposure-edge logger;
- model-reported parent IDs;
- reported-support edge logger;
- run export.

## Retrieval v0

Supply:

```text
known required support
+ controlled distractors
```

No embeddings yet.

## Exit criteria

For a single derived claim you can answer:

- what the model saw;
- what it said supported the answer;
- what normalized claim it created;
- whether the claim is true;
- what node was written to memory.

---

# Phase 4 — Experiment 0 plumbing run

## Tiny run configuration

Suggested starting point:

```text
worlds: 5–10
model: 1
generation depth: 1–2
task depth: D0/D1
distractors: small fixed count
seeds: 1–2 if needed
```

## Outputs

- reported-lineage precision/recall;
- structured-output failure rate;
- truth accuracy;
- several lineage DAG exports;
- manual audit notes.

## Do not optimize results

If parent reporting performs poorly, that is a scientific result about instrumentation—not a reason to quietly change prompts until it looks impressive.

Prompt changes are fine during plumbing, but version them and rerun the golden cases.

---

# Phase 5 — Counterfactual causal runner

## Build

- exact replay from stored call;
- remove-parent intervention;
- replace-with-clean-counterpart intervention;
- output comparison;
- repeated-seed support if necessary;
- causal evidence categories.

## Golden causal tests

Construct tiny worlds where the expected effect of removing a parent is obvious.

Example:

```text
A + B -> C
```

Test:

- original context A+B produces C;
- removing B should make C unsupported;
- an irrelevant distractor D should not materially affect C.

The LLM may not behave perfectly, but the harness must perform the intervention correctly.

## Exit criteria

You can take one reported lineage edge and produce a stored counterfactual record showing what changed under intervention.

---

# Phase 6 — Experiment 0 pilot

## Purpose

Characterize whether lineage can be measured reliably enough to interpret mutation propagation.

Suggested starting matrix:

```text
~30 worlds
3 decoding seeds
D0/D1 + limited D2
fixed model
fixed prompt version
fixed retrieval policy
```

## Decision gate

Before Experiment 1, review:

- lineage precision/recall;
- hidden causal-parent rate;
- stochastic instability;
- parsing failures;
- causal-test indeterminacy;
- cost/runtime per world;
- common failure modes.

Freeze protocol version `exp0-v1` when satisfied.

---

# Phase 7 — Experiment 1 minimal paired run

## Build

- paired clean/mutated run scheduler;
- generation loop;
- infection ancestry tracking;
- de novo versus transmitted error classification;
- initial `R_mem` metrics;
- cumulative descendant metrics.

## Plumbing configuration

Start tiny:

```text
5 paired worlds
generations 0–4
1 model
minimal causal sample
```

Inspect every lineage manually.

## Exit criteria

At least one run can show, with raw artifacts:

```text
mutation seed
  -> exposure
  -> derived false claim
  -> descendant claim
```

or demonstrate extinction/repair with equally clear evidence.

The goal is observability, not finding a dramatic cascade.

---

# Phase 8 — Experiment 1 pilot

Suggested planning target:

```text
~30 paired worlds
3 decoding seeds
generations 0–8
one frozen model/config
```

Primary candidate endpoint:

> cumulative causally infected descendants through generation 8

Secondary:

- `R_mem(t)`;
- amplification ratio;
- transmission probability/exposure;
- repair probability;
- de novo mutation rate;
- lineage survival;
- clean-world task accuracy.

Use pilot results to determine confirmatory sample size and causal-testing budget.

---

# Phase 9 — Feedback checkpoint

Stop feature development and review the experiment.

Bring back:

1. repo commit hash;
2. `RESULTS_TEMPLATE.md` filled in;
3. run manifest(s);
4. aggregate metrics;
5. 3–5 lineage examples;
6. at least one causal counterfactual example;
7. failures and surprises;
8. approximate runtime/compute cost;
9. any protocol deviations.

Do not add biological defenses before this review unless needed to fix a measurement flaw.

---

# Later experiment backlog — intentionally not active

Once Experiment 0/1 are trustworthy:

## Experiment 2 — Reproduction and criticality

Manipulate exposure opportunity, branching, retrieval rate, and mutation frequency. Test whether `R_mem` predicts persistence/extinction and whether critical behavior exists empirically.

## Experiment 3 — Biological defenses

Compare:

- unrestricted memory;
- source anchoring;
- write-time proofreading;
- lineage-gated reproduction;
- senescence;
- apoptosis;
- combinations.

Key question: can a policy suppress erroneous lineage reproduction without suppressing correct knowledge production?

## Experiment 4 — Epistemic monoculture

Compare apparent evidence count with independent root diversity.

## Experiment 5 — Network ecology

Add multiple agents and controlled communication topologies.

## Experiment 6 — Recovery/hysteresis

Correct an established root error and measure how long descendants remain contaminated.

## Experiment 7 — Spontaneous evolution

Seed no error. Measure naturally arising mutations during repeated memory operations.

---

# Suggested first coding session

If starting immediately, build in this order:

```text
1. repo + pyproject + tests
2. canonical Fact / Rule / World schemas
3. one golden world
4. forward-chaining oracle
5. procedural world generator
6. clean/mutated pair assertion
7. task generator
8. Ollama structured-output adapter
9. one fully logged model call
```

Do not build the generation loop until the single-call record is trustworthy.

---

# Commit discipline

Useful milestone tags:

```text
gene-v0-world-oracle
gene-v0-ollama-contract
gene-v0-lineage-logging
gene-exp0-plumbing
gene-exp0-pilot
gene-exp1-plumbing
gene-exp1-pilot
```

Every experimental result should point to an immutable commit/tag and configuration file.

---

# Questions that should be answered by data, not design debate

Do not overthink these before the pilot:

- Is model-reported lineage reliable?
- How stochastic are causal ablations?
- How many causal tests are necessary?
- Which claim types propagate most easily?
- Does reasoning depth matter?
- Is reproduction approximately branching-process-like?
- Does `R_mem > 1` predict long-lived lineages?
- Are repairs common or rare?

GENE exists to make those questions measurable.
