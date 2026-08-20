# Meta-Scientific & Architectural Lessons From Exploration Round 1

## 1. The Core Paradox: Frozen Substrates vs Mutable Wrappers

In Exploration Round 1, we established a strict governance boundary:
> *"No experiment may alter the frozen core engine to make its result work."*

This rule successfully protected the base codebase: commit `9353005` remained untouched, zero lines of `src/gene/` core logic were modified, and the 100-test baseline suite continued passing with 100% fidelity.

However, the post-execution batch review revealed a deeper methodological phenomenon:
$$\text{Immutable Core} \ne \text{Unconfounded Assay}$$

When exploratory branch agents were granted freedom to construct ad-hoc runner scripts, the measuring confounds simply **migrated outward into the experimental wrapper layer**:

1. **Answer Leaks in Output Schemas (Track F):** The wrapper placed the ground-truth answer IDs directly inside the schema formatting example, making it impossible to separate genuine relational reasoning from trivial template string copying.
2. **Hard-Coded Evaluator Constants (Track E):** The wrapper embedded theoretical policy constants directly inside return dictionaries, turning an intended empirical replay into a tautological self-test.
3. **Model-Contract Fragility (Track D):** The wrapper assumed prompt syntax calibrated on Gemma 3:12B would seamlessly transfer to 3B models, discovering that sub-7B models interpret schema enum strings literally.
4. **Baseline Contract Breakage (Track C):** The wrapper modified task prompt syntax to an extent that caused the model to fail at depth $G_1$ (where all premises were present), falsely mimicking a depth-decay phenomenon.
5. **Prompt Steering & Confounded Geometry (Track B):** The wrapper introduced explicit instructions (*"Evaluate independent sources"*) and asymmetric document counts (5 vs 4), muddying a genuine source-diversity finding.
6. **Pre-Computed States vs Active Policies (Track A):** The wrapper constructed pre-cooked prompt states rather than executing dynamic runtime revalidation.

---

## 2. The Recursive Epistemic Lesson

There is a striking recursion between GENE's scientific domain and its software engineering process:

| GENE Domain Principle | Exploration Round 1 Process Parallel |
| :--- | :--- |
| **Exposure vs Local Reasoning:** A reasoner exposed to corrupted ancestors may reproduce corrupted descendants without intentional deceit. | A well-intentioned agent running on a trusted substrate can write a flawed wrapper that generates corrupted scientific conclusions. |
| **Lineage Laundering:** Corrupted facts appear legitimate once detached from ancestral provenance. | Flawed empirical results appear rigorous once wrapped in clean tables, preflight assertions, and passing unit tests. |
| **Representation as Relation:** Conflating the surface representation of a belief with its underlying causal support. | Conflating the surface execution of a script with genuine empirical measurement of the underlying phenomenon. |

---

## 3. The New Exploration Rule: The Unified Exploration Harness

For all future exploratory batches (Round 2+), we establish the following development law:

> **Parallelize the experiment; do not parallelize the measuring instrument.**

Exploratory branches are encouraged to propose new worlds, topologies, prompts, and hypotheses. However, **no exploratory script may write its own ad-hoc persistence schema, bypass model digest resolution, or omit CallSpec logging.**

Every live call in future exploratory batches must pass through a single, shared `ExplorationHarness` (`src/gene/experiments/exploration_harness.py`) that automatically enforces:
- Strict `CallSpec` hashing and persistence.
- Automatic Ollama model SHA-256 digest discovery and logging.
- Standardized SQLite table schema (`exploration_runs`, `exploration_calls`, `exploration_evaluations`).
- Machine-checked `DualOracle` evaluation logging.
- Automatic detection of prompt schema answer leakage (e.g. asserting that schema templates contain no ground-truth IDs or answers).
