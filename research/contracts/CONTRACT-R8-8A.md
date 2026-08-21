---
contract_id: CONTRACT-R8-8A
status: FROZEN
base_sha: 21e63efe537def204ce0a0013a0e9f7d974e5217
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
proposed_by: antigravity
design_review: APPROVED
reviewed_by: chatgpt-pro
authorized_by: human
creation_date: "2026-08-21"
target_completion_date: "2026-08-23"
---

# Research Contract: CONTRACT-R8-8A — Autonomous Open-World Candidate Generation

> **FROZEN RESEARCH CONTRACT — AUTHORIZED FOR EXECUTION**:
> This contract is frozen and authorized by the Human Research Director following scientific review by `chatgpt-pro`. It formalizes Exploration Round 8 Stage 8A, testing autonomous candidate hypothesis extraction $\hat{\mathcal{B}}(x)$ from unstructured text without externally supplied finite menus, evaluated across a sealed 50-world benchmark with paired baseline controls and end-to-end useful admission coverage.

---

## 1. Metadata & Lifecycle Status

- **Contract ID**: `CONTRACT-R8-8A`
- **Contract Status**: `FROZEN`
- **Base Git Commit (`base_sha`)**: `21e63efe537def204ce0a0013a0e9f7d974e5217`
- **Target Experiment / Phase**: Exploration Round 8 Stage 8A (Autonomous Open Ingress)
- **Protocol Version**: `v0.1`
- **Governance**:
  - **Proposed By**: `antigravity`
  - **Design Review**: `APPROVED` (Reviewed by `chatgpt-pro`)
  - **Authorized By**: `human` (Human Director Strategic Authorization)

---

## 2. Research Question & Scientific Rationale

- **Primary Research Question**:
  Can `gemma3:12b` autonomously induce an open candidate hypothesis set $\hat{\mathcal{B}}(x)$ directly from raw synthetic narrative text without an externally supplied candidate menu, achieving $\ge 90.0\%$ target entity recall, $\ge 85.0\%$ relevant candidate precision, and $\ge 85.0\%$ end-to-end useful admission coverage without admitting a single false fact ($\text{FDAR}_{\text{global}} = 0 / N$)?

- **Why This Follows from Existing Evidence**:
  In Round 7 Stage 7B (commit `2b0cd7c`), `gemma3:12b` demonstrated $98.1\%$ schema compliance and $96.2\%$ downstream 4-probe fidelity when selecting from a supplied candidate menu $[0, 1, 2, 3]$. However, Section 4 of `MIGRATION_CHECKPOINT.md` noted that candidate generation remained an unresolved dependency. Stage 8A removes this menu scaffolding.

- **Hypotheses**:
  - **$H_1$ (Primary Hypothesis)**: Structured JSON span extraction prompts enable `gemma3:12b` to generate open candidate mentions $\hat{\mathcal{B}}(x)$ that recover ground-truth target entities with $\ge 90.0\%$ recall and $\ge 85.0\%$ precision, feeding valid certificates into `IngressEngine` to achieve $\ge 85.0\%$ end-to-end useful admission coverage.
  - **$H_0$ (Null Hypothesis)**: Open candidate generation without menu scaffolding collapses into severe hallucination drift or entity omissions, yielding useful admission coverage $< 70.0\%$.
  - **$H_{\text{alt}}$ (Salience Bias)**: Open generation is distorted by entity frequency or syntactic position, dropping low-salience entities while preserving high-salience ones.

---

## 3. Evaluation Sealing & Experimental Design

- **Development vs Sealed Evaluation Split**:
  - **Development / Pilot Set**: 15 synthetic narrative worlds used exclusively for prompt engineering, JSON schema formatting, and threshold tuning.
  - **Sealed Final Evaluation Set**: 50 fixed synthetic narrative worlds. This set remains strictly sealed until all prompts, schemas, and hyperparameters are frozen. Final-world performance may never be used for iterative tuning.

- **Stratified Evaluation Topology (50 Final Worlds)**:
  - Worlds contain multi-clause epistemic events with explicit machine-readable gold target sets $\mathcal{G}(w)$.
  - Total ground-truth target mentions across 50 worlds: $N_{\text{gold}} = 100$ mentions (2 target events per world).
  - Balanced across syntactic position (subject vs object mentions) and entity salience (high-frequency vs single-mention entities).

- **Paired Experimental Conditions (Evaluated on Same 50 Worlds)**:
  1. **Open Candidate Generation (Primary Arm)**: LLM induces candidate set $\hat{\mathcal{B}}(x)$ from raw text $\to$ `IngressEngine` validation.
  2. **Paired Menu-Assisted Control**: LLM provided with Stage 7B-style finite candidate menus $[0, 1, 2, 3]$ on the exact same 50 worlds.

---

## 4. Estimands & Operational Formulas

- **Candidate Recall ($M_1$)**:
  $$\text{Recall} = \frac{|\{e \in \mathcal{G}_{\text{gold}} \mid e \in \hat{\mathcal{B}}(x)\}|}{|\mathcal{G}_{\text{gold}}|}$$
  (Target: $\ge 90.0\%$ over $N_{\text{gold}} = 100$ ground-truth mentions).

- **Candidate Precision ($M_2$)**:
  $$\text{Precision} = \frac{|\{e \in \hat{\mathcal{B}}(x) \mid e \in \mathcal{G}_{\text{gold}}\}|}{|\hat{\mathcal{B}}(x)|}$$
  (Target: $\ge 85.0\%$ against preregistered gold relevant-candidate set).

- **End-to-End Useful Admission Coverage ($M_3$)**:
  $$\text{Coverage} = \frac{|\{e \in \mathcal{G}_{\text{gold}} \mid e \text{ proposed, validated, admitted, and passes } Q_1..Q_4\}|}{|\mathcal{G}_{\text{gold}}|}$$
  (Target: $\ge 85.0\%$).

- **Observed False Discovery Admission Rate ($\text{FDAR}_{\text{global}}$)**:
  $$\text{FDAR}_{\text{global}} = \frac{N_{\text{false\_admissions}}}{N_{\text{total\_admissions}}} \equiv 0 / N$$
  (Strict zero tolerance: Any single false fact admission fails the benchmark).

---

## 5. Acceptance & Falsification Criteria

- **Success Criteria**:
  1. Target Candidate Recall ($M_1$) $\ge 90.0\%$ ($90 / 100$ gold mentions).
  2. Candidate Precision ($M_2$) $\ge 85.0\%$.
  3. End-to-End Useful Admission Coverage ($M_3$) $\ge 85.0\%$ ($85 / 100$ gold records).
  4. $\text{FDAR}_{\text{global}} \equiv 0.0\%$ (Zero observed false admissions).
  5. Paired drop in useful coverage relative to menu-assisted control is $\le 10.0\%$.
  6. Clean pass on `python scripts/verify_repo.py`.

- **Falsification / Failure Criteria**:
  1. Useful admission coverage drops below $75.0\%$.
  2. Any hallucinated fact admitted to durable memory ($\text{FDAR} > 0$).
  3. Severe salience disparity ($> 25\%$ recall gap between high-salience and low-salience entities).

---

## 6. Claim Ceiling & Epistemic Boundaries

- **Authorized Claim (If all criteria pass)**:
  Autonomous candidate hypothesis extraction and entity grounding directly from raw narrative text without external candidate menus, achieving high useful admission coverage and preserving proof-carrying epistemic safety.
- **Explicit Exclusions / Prohibited Overclaims**:
  1. Does NOT claim open-world entity resolution across massive web corpora.
  2. Does NOT claim autonomous predicate ontology discovery (predicate schema remains predefined).

---

## 7. Required Run Artifacts & Verification

- SQLite Database: `runs/r8_stage8a_candidate_generation.db`
- Raw Call Archive: `data/r8_stage8a_raw_calls.jsonl`
- Canonical Summary JSON: `data/r8_stage8a_summary.json`
- Formal Report: `docs/results/R8_STAGE8A_REPORT.md`
- Verification: Clean pass on `python scripts/verify_repo.py`

---

## 8. Compute Budget

- **Resource Class**: `gpu`
- **Estimated Invocations**: 15 pilot calls + 50 open test calls + 50 menu control calls = 115 live calls to `gemma3:12b`.
- **Estimated Execution Time**: ~12 minutes on local GPU
- **Long-Running Process**: `false`
- **Exclusive GPU**: `true`
- **Interruptible**: `true`

---

## 9. Human Strategic Authorization Checklist

- [x] Scientific Design Review: `APPROVED` by `chatgpt-pro`.
- [x] Machine-readable gold denominators ($N_{\text{gold}} = 100$) and relevant precision defined.
- [x] Development set (15 worlds) separated from sealed evaluation set (50 worlds).
- [x] Paired world-for-world menu-assisted control specified on identical evaluation set.
- [x] End-to-end useful admission coverage ($M_3 \ge 85\%$) replaces conditional-only admission.
- [x] Zero-tolerance observed $\text{FDAR} = 0 / N$ enforced.
- [ ] **Human Director Strategic Authorization**: Awaiting strategic decision to freeze (`status: FROZEN`, `authorized_by: human`).
