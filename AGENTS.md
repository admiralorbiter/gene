# AGENTS.md — GENE Development Contract

## Project

GENE = **Genealogical Epistemic Network Experiments**.

This repository is a research instrument. Correct measurement, replayability, and auditability take priority over feature count or framework sophistication.

Read before coding:

1. `README.md`
2. `docs/EXPERIMENTAL_PROTOCOL.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DEVELOPMENT_PLAN.md`
5. `docs/results/` (All completed experiment reports)

---

# Current Objective & Roadmap Status

### Completed & Validated Milestones:
- **Experiment 0**: Lineage Observability & Causal Parent Interventions.
- **Experiment 1A**: Single Mutation Propagation & Multi-Generational Cascades.
- **Experiment 1B-A**: Multi-Generation Branching Transmission, Allele Fidelity, and Analytic Extinction Matrix.
- **Experiment 1B-B**: Endogenous Multi-Hop Retrieval Dynamics ($X_F, X_A, X_{\text{path}}$), Lexical Competition, Surface-Area Scaling, and Causal Retrieval Rescue.
- **Phase 9 / 9.5**: Persistence Hardening, Retrieval Boundary Shape Map, 48-Call Live Rescue, and 16-Call Matched Path Expression Assay ($P(\text{active}\mid\text{complete})=1, P(\text{active}\mid\text{broken})=0$).

### Current Milestone: Phase 10 — Experiment 1B-C Delayed Adjudication & Lineage Immunity Sandbox
1. **Epistemic Risk-Signal Principle**: Lineage is a mechanism for *propagating* trust or distrust, not an intrinsic truth detector (topologies are isomorphic). The policy receives ancestry metadata and an external binary risk signal ($S \in \{0, 1\}$); it never receives canonical $T^*$.
2. **Experiment 1B-C0 (Policy Calibration Engine)**: Exact analytic verification of 6 policies (`baseline`, `uniform_thinning`, `random_family_quarantine`, `node_only_quarantine`, `lineage_quarantine`, `oracle_upper_bound`) across 4 discrete root-signal states $(S_H, S_I)$ weighted by $\text{TPR} \times \text{FPR}$.
3. **Experiment 1B-C1 (Delayed-Adjudication Retrieval Sandbox, $G_2 \to G_3$)**: Measure post-adjudication path availability ($C_H = X_{\text{path},H}^{\text{post}}, C_I = X_{\text{path},I}^{\text{post}}$), containment ($1 - C_I$), and epistemic autoimmunity ($1 - C_H$) across 6 paired worlds under BM25 retrieval with zero live LLM compute.
4. **Pareto Frontier Mapping**: Identify non-trivial detector quality regions where lineage quarantine outperforms node-only and topology-matched controls without excessive healthy-path loss.

---

# Core Research Principle

> **Cheap deterministic measurement $\to$ tiny live mechanism test $\to$ review $\to$ only then scale.**

Never spend live model compute on an intervention or baseline until its behavior and boundary conditions have been mapped and proven deterministically.

---

# Frozen Design Constraints

Do not change these without recording a decision and explaining why:

- Synthetic fictional worlds come before real-world facts.
- Canonical ground truth is machine-readable and immutable.
- Experimental memory is append-only.
- All model outputs (including `UNKNOWN` abstentions) generate persistent occurrence nodes.
- Exposure lineage is recorded by the harness, not inferred by the model.
- Reported-support lineage is explicitly separate from causal lineage.
- Model self-reports are never treated as causal ground truth.
- Clean/mutated pairs must differ only at the declared mutation.
- World is the experimental unit.
- Raw prompts/responses and run metadata are preserved in SQLite.
- Every reported result must resolve to a Git commit/tag + configuration + model digest.

---

# Inactive Roadmap Backlog (Do Not Build Yet)

Unless explicitly approved after a gating milestone, do **not** build:

- web UI / dashboard services (Flask/FastAPI);
- vector databases / dense embedding retrieval (keep BM25 until lexical boundaries are fully mapped);
- multi-agent open communication ecologies;
- real-world search / fact checking;
- complex senescence / apoptosis / biological memory pruning;
- autonomous experiment generation;
- multi-model provider scaling across dozens of model families;
- elaborate plugin / orchestration frameworks.

---

# Experiment Discipline

During plumbing/debugging, prompt and schema changes are allowed. Every material change must increment a prompt/protocol/config version.

Once an experiment pilot is declared frozen:

- do not modify prompts mid-run;
- do not silently drop failed worlds;
- do not tune causal criteria or thresholds after seeing aggregate results;
- do not rewrite the oracle to make model outputs count as correct;
- do not pool descendants across worlds as if they were independent.

A negative or null result is a valid scientific result.

---

# Coding Preferences

Prefer explicit, testable code over framework magic:

- Python 3.12+
- type hints on public interfaces;
- Pydantic or dataclasses for persisted schemas;
- SQLite with migrations and foreign key integrity;
- pytest;
- deterministic UUID/hash-derived IDs;
- pure functions for world generation/oracle logic;
- dependency injection for model client/retrieval policy;
- zero hidden global state.

Keep LLM calls behind one narrow adapter so tests can run instantly with deterministic fakes.

---

# Required Run Artifacts

Every completed run should be understandable without opening the source code:

- SQLite database (`runs`, `calls`, `memory_nodes`, `dual_oracle_evaluations`, `retrieval_events`, `retrieval_sweep_results`, `causal_tests`)
- `manifest.json`
- `world.json`
- `mutation.json` (when applicable)
- summary report markdown in `docs/results/`

Never overwrite a prior completed run database or directory.

