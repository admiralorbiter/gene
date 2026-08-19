# GENE

**Genealogical Epistemic Network Experiments**

GENE is an experimental testbed for studying how information changes, reproduces, persists, repairs, and dies inside persistent LLM memory systems.

The initial research question is deliberately narrow:

> When a single erroneous claim enters an otherwise controlled memory system, what descendants does it produce, and can we causally trace that lineage?

GENE begins with local/open models through Ollama and synthetic worlds with exact machine-readable ground truth. The goal is not to build a production memory framework. The goal is to build instrumentation reliable enough that later experiments about misinformation propagation, epistemic reproduction, error thresholds, senescence, repair, monoculture, and multi-agent networks can be interpreted confidently.

## Core idea

Most LLM memory evaluations ask whether an agent remembers correctly or whether contaminated state changes later behavior. GENE treats persistent information as a lineage.

A stored claim may be:

- retrieved by later generations,
- cited as support,
- transformed into a descendant claim,
- repaired,
- mutated,
- propagated into additional descendants,
- or retired from reproduction.

GENE records these events so we can distinguish three kinds of ancestry:

1. **Exposure lineage** — which memory nodes were actually placed in the model context.
2. **Reported-support lineage** — which memory nodes the model says support a new claim.
3. **Causal lineage** — which parent nodes demonstrably change the descendant when removed or counterfactually replaced.

The first development milestone is to prove that this instrumentation works before testing more ambitious biological interventions.

## Initial research program

### Experiment 0 — Lineage observability

Can GENE correctly observe information ancestry?

Use synthetic worlds with mechanically known derivation chains. Models create derived claims while returning structured parent IDs. Compare reported lineage with known valid support and causal ablation tests.

### Experiment 1 — Single mutation

What happens when exactly one fact is corrupted?

Create paired clean and mutated versions of the same world. Hold model, prompts, world structure, generation schedule, and decoding settings constant. Track whether the mutation:

- disappears,
- remains isolated,
- is repaired,
- changes form,
- or generates descendants.

The planned primary endpoint for the first serious pilot is:

> **Cumulative causally infected descendants through generation 8.**

## Project principles

- **Ground truth before realism.** Begin with fictional, procedurally generated worlds whose truth is exactly known.
- **Lineage before intervention.** Do not test senescence, apoptosis, source anchoring, or multi-agent topologies until lineage measurement is trustworthy.
- **Causality over self-report.** Model-provided citations are useful observations, not proof of influence.
- **Append-only raw evidence.** Preserve source facts, prompts, model outputs, and evaluation results exactly as generated.
- **Paired experiments by default.** Clean and mutated worlds should differ only in the intended treatment.
- **World is the experimental unit.** Descendants from a shared world are correlated and must not be treated as independent samples.
- **Freeze before scaling.** Pilot for bugs and variance; freeze the protocol before confirmatory runs.
- **Reproducibility is part of the result.** Record model digest, Ollama version, quantization, prompt hash, context size, seed, world seed, and policy version.

## Suggested repository layout

```text
GENE/
├── README.md
├── pyproject.toml
├── src/
│   └── gene/
│       ├── config.py
│       ├── ollama_client.py
│       ├── worlds/
│       │   ├── generator.py
│       │   ├── schema.py
│       │   └── oracle.py
│       ├── memory/
│       │   ├── store.py
│       │   ├── retrieval.py
│       │   └── lineage.py
│       ├── experiments/
│       │   ├── exp0_lineage.py
│       │   └── exp1_single_mutation.py
│       ├── evaluation/
│       │   ├── claims.py
│       │   ├── causality.py
│       │   └── metrics.py
│       └── persistence/
│           └── db.py
├── tests/
├── configs/
│   ├── exp0.yaml
│   └── exp1.yaml
├── data/
│   └── .gitkeep
├── runs/
│   └── .gitkeep
└── docs/
    ├── EXPERIMENTAL_PROTOCOL.md
    ├── ARCHITECTURE.md
    ├── DEVELOPMENT_PLAN.md
    └── RESULTS_TEMPLATE.md
```

## First runnable definition of done

GENE v0 is ready for feedback when it can:

1. deterministically create a synthetic world from a `world_seed`;
2. export canonical ground-truth triples and derivation rules;
3. generate a clean/mutated paired world differing in exactly one atomic fact;
4. query one Ollama model with structured JSON output;
5. persist every call, retrieved memory node, created claim, and lineage edge;
6. mechanically classify a generated atomic claim as true, false, unsupported, or unparseable;
7. rerun a selected generation with one parent removed/replaced;
8. produce a lineage DAG and a small run summary;
9. reproduce the same world and configuration from stored metadata.

At that point, run a tiny plumbing test and return the results before adding biological defenses.

## What GENE is not yet

Do **not** initially build:

- a general-purpose agent framework;
- embeddings/vector databases unless exact retrieval becomes a limitation;
- a web UI;
- multi-agent societies;
- real-world fact checking;
- senescence/apoptosis policies;
- automatic research-paper generation;
- a complex ontology;
- dozens of model backends.

Those are later experiments, not prerequisites for Experiment 0.

## Working terminology

See `docs/EXPERIMENTAL_PROTOCOL.md` for frozen operational definitions and metrics.

## Immediate next step

Implement only the path needed for **Experiment 0** and a minimal **Experiment 1** paired run. When the first runs exist, use `docs/RESULTS_TEMPLATE.md` to package results for review.
