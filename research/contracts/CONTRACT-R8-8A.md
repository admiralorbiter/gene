---
contract_id: CONTRACT-R8-8A
status: DRAFT
base_sha: 21e63efe537def204ce0a0013a0e9f7d974e5217
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
proposed_by: antigravity
design_review: PENDING
reviewed_by: null
authorized_by: null
creation_date: "2026-08-21"
target_completion_date: "2026-08-23"
---

# Research Contract (Draft Proposal): CONTRACT-R8-8A — Autonomous Open-World Candidate Generation

> **DRAFT PROPOSAL — PENDING SCIENTIFIC DESIGN REVIEW**:
> This contract proposes the first milestone of Exploration Round 8 (Stage 8A), addressing the open question identified in `MIGRATION_CHECKPOINT.md`: transitioning from finite candidate menus $\mathcal{B}(x)$ to autonomous open candidate hypothesis generation from raw unstructured text.

---

## 1. Metadata & Lifecycle Status

- **Contract ID**: `CONTRACT-R8-8A`
- **Contract Status**: `DRAFT`
- **Base Git Commit (`base_sha`)**: `21e63efe537def204ce0a0013a0e9f7d974e5217`
- **Target Experiment / Phase**: Exploration Round 8 Stage 8A (Open-World Ingress)
- **Protocol Version**: `v0.1`
- **Governance**:
  - **Proposed By**: `antigravity`
  - **Design Review**: `PENDING` (Awaiting Review by `chatgpt-pro`)
  - **Authorized By**: `null` (Pending Human Director Authorization)

---

## 2. Research Question & Scientific Rationale

- **Primary Research Question**:
  Can an instruction-tuned LLM (`gemma3:12b`) autonomously extract an unconstrained candidate hypothesis set $\hat{\mathcal{B}}(x)$ directly from raw synthetic narrative text without an externally supplied finite candidate menu, while maintaining $\ge 90.0\%$ target entity recall and $\text{FDAR}_{\text{global}} = 0.0\%$ downstream false-discovery admission in the bitemporal epistemic store?

- **Why This Follows from Existing Evidence**:
  In Round 7 Stage 7B (commit `2b0cd7c`), `gemma3:12b` demonstrated $98.1\%$ schema compliance and $96.2\%$ downstream 4-probe fidelity when choosing from a supplied candidate menu $[0, 1, 2, 3]$. However, Section 4 of `MIGRATION_CHECKPOINT.md` explicitly noted that the system relied on an external oracle for the candidate set $\mathcal{B}(x)$. Stage 8A removes this scaffolding by requiring the model to generate the candidate set itself.

- **Hypotheses**:
  - **$H_1$ (Primary Hypothesis)**: Structured JSON span extraction prompts enable `gemma3:12b` to generate candidate entity mentions $\hat{\mathcal{B}}(x)$ with $\ge 90.0\%$ target recall and $\ge 85.0\%$ precision, feeding valid certificates into the proof-carrying `IngressEngine`.
  - **$H_0$ (Null Hypothesis)**: Open candidate generation without menu scaffolding causes severe hallucination or entity drop ($\text{Recall} < 75.0\%$ or $\text{Precision} < 70.0\%$), causing downstream admission failure.
  - **$H_{\text{alt}}$ (Alternative Mechanism)**: The model selectively extracts high-frequency synthetic names while dropping low-salience entities, failing entity-frequency invariance.

---

## 3. Frozen Experimental Design & Methodology

- **Experimental Unit**: 50 Synthetic Narrative Worlds spanning multi-clause epistemic events.
- **Model Under Test**: `gemma3:12b` (Ollama digest: `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`).
- **Inference Configuration**: Temperature ($T=0.0$), Seed (`42`), Context Window ($8192$), Top-p ($1.0$).
- **Experimental Conditions**:
  1. **Open-World Candidate Generation (Primary Condition)**: Raw sentence $\to$ LLM proposes $\hat{\mathcal{B}}(x) \to$ `IngressEngine` validation.
  2. **Menu-Assisted Baseline Control**: Standard Stage 7B finite candidate menu $[0, 1, 2, 3]$ serving as upper-bound comparison.
  3. **Entity Permutation Invariance Control**: Permuted entity names and surface spellings across identical narrative templates.

---

## 4. Estimands & Primary Metrics

- **Primary Estimands**:
  1. **Candidate Mention Recall ($M_1$)**: Fraction of ground-truth target entities present in the generated candidate hypothesis set $\hat{\mathcal{B}}(x)$ (Target $\ge 90.0\%$).
  2. **Candidate Precision ($M_2$)**: Fraction of proposed candidates that correspond to valid semantic spans in the text (Target $\ge 85.0\%$).
  3. **Downstream Ingress Admission Fidelity ($M_3$)**: Fraction of admitted records passing 4-probe downstream invariants ($Q_1 \dots Q_4$) (Target $\ge 90.0\%$).
  4. **Global False Discovery Admission Rate ($\text{FDAR}_{\text{global}}$)**: Fraction of ungrounded or hallucinated assertions admitted to the durable store (Target $\equiv 0.0\%$).

- **Statistical Protocol**:
  - Exact binomial confidence intervals for Recall, Precision, and Admission Fidelity across 50 trials.
  - Zero-tolerance verification: Any single false fact admission ($\text{FDAR} > 0$) immediately fails the contract.

---

## 5. Acceptance & Falsification Criteria

- **Success Criteria**:
  1. Candidate Mention Recall $\ge 90.0\%$ (at least 45/50 target entities recovered).
  2. Candidate Precision $\ge 85.0\%$.
  3. Downstream Ingress Admission Fidelity $\ge 90.0\%$.
  4. $\text{FDAR}_{\text{global}} \equiv 0.0\%$ (Strict Zero Tolerance).
  5. Clean pass on `python scripts/verify_repo.py`.

- **Falsification / Failure Criteria**:
  1. Recall drops below $80.0\%$.
  2. Any hallucinated fact admitted to durable memory ($\text{FDAR} > 0$).

---

## 6. Claim Ceiling & Epistemic Boundaries

- **Maximum Authorized Claim**:
  Autonomous candidate hypothesis extraction from raw single-document synthetic narratives without external candidate menus, maintaining proof-carrying downstream safety.
- **Explicit Exclusions / Prohibited Overclaims**:
  1. Does NOT claim open-world entity resolution across massive web corpora.
  2. Does NOT claim autonomous predicate ontology discovery (predicate set remains defined by schema).

---

## 7. Required Run Artifacts & Verification

- SQLite Database: `runs/r8_stage8a_candidate_generation.db`
- Raw Call Archive: `data/r8_stage8a_raw_calls.jsonl`
- Canonical Summary JSON: `data/r8_stage8a_summary.json`
- Formal Report: `docs/results/R8_STAGE8A_REPORT.md`
- Claim Ledger Entry: `data/claim_ledger.json`
- Verification Script: Clean pass on `python scripts/verify_repo.py`

---

## 8. Compute & Resource Budget

- **Resource Class**: `gpu`
- **Estimated Invocations**: 50 live model calls to `gemma3:12b`
- **Estimated Execution Time**: ~6 minutes on local GPU
- **Long-Running Process**: `false`
- **Exclusive GPU**: `true`
- **Interruptible**: `true`

---

## 9. Governance & Review Tracking

- [x] Initial Draft Created by Antigravity (`proposed_by: antigravity`).
- [ ] Scientific Design Review by `chatgpt-pro` (`design_review: PENDING`).
- [ ] Human Director Strategic Authorization (`authorized_by: null`).
