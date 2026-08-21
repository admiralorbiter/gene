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
6. `research/checkpoints/MIGRATION_CHECKPOINT.md`
7. `research/ACTIVE_CONTRACT.md`

---

# Operational Research Workflow & Active Contract Discovery

All research experiments, contracts, promotions, and checkpoints are organized under `research/`:

- `research/ACTIVE_CONTRACT.md`: **The single machine-discoverable pointer to currently authorized work.** Agents MUST inspect this file before executing experimental runs. Its operational state vocabulary is:
  `IDLE | READY | RUNNING | AUDITING | ESCALATED`
  When `status: IDLE`, no autonomous experimental execution may begin.
- `research/checkpoints/`: Milestones and migration snapshots (e.g., `MIGRATION_CHECKPOINT.md`).
- `research/contracts/`: Active and archived research contracts named `CONTRACT-<ID>.md`. Contracts use an immutable lifecycle:
  `DRAFT | FROZEN | SUPERSEDED`
  Historical frozen contracts remain frozen and immutable after execution.
- `research/promotions/`: Completed promotion records named `PROMOTION-<ID>.md` with status:
  `CANDIDATE | PROMOTED | REJECTED | REVISED_CONTRACT_REQUIRED | ESCALATED`
- `research/templates/`: Reusable templates for contracts (`CONTRACT_TEMPLATE.md`) and promotions (`PROMOTION_TEMPLATE.md`).

### Machine-Readable Contract Frontmatter:
Every contract in `research/contracts/` must begin with YAML frontmatter specifying execution requirements and resource classes:

```yaml
---
contract_id: CONTRACT-<ID>
status: DRAFT | FROZEN | SUPERSEDED
base_sha: <commit-hash>
resource_class: cpu | gpu | hybrid
long_running: false | true
exclusive_gpu: false | true
interruptible: true | false
---
```

---

# Autonomous Repair vs. Epistemic Escalation Boundaries

### Agents May Autonomously Repair:
- Implementation bugs and logic defects
- Test failures and flakiness
- Missing edge cases and parameter boundary guards
- Artifact tracking and `.gitignore` exceptions
- Documentation, ledger, and result synchronization
- Reproducibility failures and deterministic replay discrepancies
- Property/invariant-test failures
- Malformed identifiers, schemas, or manifests
- Violations of already-frozen implementation requirements

### Agents Must Escalate:
- Hypothesis changes or reformulations
- Metric or estimand changes
- Benchmark-design, case-population, or prompt-distribution changes
- Questionable or tautological oracle definitions
- Causal or scientific interpretation changes
- Unexpected results that materially alter the proposed mechanism
- Claim-ceiling or scope-limitation changes
- Retraction or replacement of a prior conclusion
- Roadmap changes or premature progression to unapproved milestones
- Any repair that would cause an experiment to answer a materially different question

> **Core Research Invariant**:
> **Agents optimize implementation against the frozen research contract. They do not optimize the research contract until the implementation passes.**
> If satisfying a contract requires changing the contract, agents MUST STOP and escalate:
> `ESCALATE — HUMAN EPISTEMIC DECISION REQUIRED`

---

# Repository Test & Verification Commands

Use these exact commands to verify repository state and integrity:

```powershell
# 1. Full Local Verification & Integrity Preflight Suite (Pytest + Docs + Manifest + Claims + Git Cleanliness)
python scripts/verify_repo.py

# 2. Pytest Unit & Integration Test Suite
pytest -v

# 3. Canonical Results Manifest Check
python scripts/generate_results_manifest.py --check

# 4. Documentation & Asset Links Integrity Check
python scripts/check_doc_links.py
```

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
