---
contract_id: CONTRACT-[ID]
status: DRAFT | FROZEN | SUPERSEDED
base_sha: [insert_base_commit_hash_here]
resource_class: cpu | gpu | live_llm
long_running: false | true
exclusive_gpu: false | true
interruptible: true | false
---

# Research Contract: [Experiment / Milestone Name]

> **CRITICAL REPRODUCIBILITY WARNING**:
> An experiment MUST NOT be represented as preregistered or frozen unless this contract file was committed in git under `status: FROZEN` prior to executing any live model invocations or evaluating primary experimental metrics.

---

## 1. Metadata & Lifecycle Status

- **Contract ID**: `CONTRACT-[ID]`
- **Contract Status**: `DRAFT` | `FROZEN` | `SUPERSEDED`
- **Base Git Commit (Base SHA)**: `[insert base commit hash here]`
- **Target Experiment / Phase**: `[e.g., Exploration Round 8 Stage 8A]`
- **Date Created / Frozen**: `YYYY-MM-DD`
- **Protocol Version**: `vX.Y.Z`

---

## 2. Research Question & Scientific Rationale

- **Primary Research Question**: `[Clear, unambiguous question to be tested]`
- **Why This Follows from Existing Evidence**: `[Cite prior milestone findings and exact mechanisms]`
- **Hypothesis / Competing Hypotheses**:
  - $H_1$ (Primary Hypothesis): `[...]`
  - $H_0$ (Null / Baseline Hypothesis): `[...]`
  - $H_{\text{alt}}$ (Competing Explanations): `[...]`

---

## 3. Frozen Experimental Design & Methodology

- **Experimental Unit**: `[e.g., World, Call, Query]`
- **Experimental Population / Case Factorial**:
  - Sample Size ($N$): `[...]`
  - Factorial Dimensions: `[...]`
  - Control Arms & Counterbalancing: `[...]`
- **Model(s) Under Test**: `[e.g., gemma3:12b, exact Ollama digest]`
- **Inference Configuration**: Temperature ($T=0.0$), Seed (`42`), Top-p, Context Window.

---

## 4. Estimands, Primary Metrics & Oracle Reference

- **Primary Estimands & Formulas**:
  - Metric 1: `[...]`
  - Metric 2: `[...]`
- **Oracle / Reference Definition**: `[Machine-readable ground truth definition]`
- **Acceptance Criteria (Preregistered Gate to Pass)**:
  - Criterion 1: `[...]`
  - Criterion 2: `[...]`
- **Falsification / Failure Criteria**: `[...]`
- **Preregistered Claim Ceiling**: `[Maximum scope of claim supported by this benchmark design]`

---

## 5. Implementation Boundaries & Escalation Rules

### Permitted Autonomous Implementation Changes:
- Bug fixes in harness, parsers, or deterministic state tracking
- Test suite additions and parameter boundary hardening
- Logging, serialization, and SQLite schema migrations
- Artifact synchronization and manifest updates

### Prohibited Autonomous Changes (MUST ESCALATE):
- Modifying prompts, candidate sets, or case generation after freezing
- Tuning thresholds, metrics, or oracle rules post-hoc to improve scores
- Changing the experimental population or dropping failed cases
- Raising the claim ceiling or altering the causal interpretation
- Proceeding to unapproved follow-up experiments

> **Escalation Trigger**:
> If satisfying this contract requires modifying the contract itself or redefining the oracle/metric, the agent MUST STOP immediately and flag:
> `ESCALATE — HUMAN EPISTEMIC DECISION REQUIRED`

---

## 6. Required Run Artifacts & Verification

- SQLite Database: `runs/[experiment_name]_results.db`
- Raw Call Archive: `data/[experiment_name]_raw_calls.jsonl`
- Canonical Summary JSON: `data/[experiment_name]_summary.json`
- Formal Report: `docs/results/[EXPERIMENT_NAME]_REPORT.md`
- Claim Ledger Entry: `data/claim_ledger.json` & `docs/atlas/data/claims.json`
- Verification: Clean pass on `python scripts/verify_repo.py`

---

## 7. Compute & Resource Budget

- **Estimated LLM Invocations**: `[e.g., 52 calls]`
- **Estimated Execution Time**: `[e.g., 5 minutes]`
- **Long-Running Process Handling**: `[e.g., daemon Ollama process]`

---

## 8. Completion Definition

This contract is declared complete ONLY when all of the following conditions are simultaneously satisfied:
1. All preregistered experimental cases, factorial permutations, and control arms have executed to completion without runtime exceptions or missing outputs.
2. All primary estimands, field-level accuracies, and downstream invariant probes are computed mechanically from recorded execution artifacts.
3. All required artifacts (`runs/*.db`, `data/*.jsonl`, `data/*_summary.json`, `docs/results/*_REPORT.md`) are generated, SHA-256 hashed, and actively tracked in git.
4. The canonical claim ledger (`data/claim_ledger.json`), Atlas claims (`docs/atlas/data/claims.json`), and results manifest (`data/canonical_results_manifest.json`) are updated and deeply synchronized.
5. The full local verification suite passes cleanly (`python scripts/verify_repo.py` returns exit code 0).
6. A completed Promotion Record (`PROMOTION_TEMPLATE.md` instance) is filled out and reviewed.
7. The final repository state is committed, tagged, and pushed with a clean working tree (zero uncommitted changes or untracked drift).
