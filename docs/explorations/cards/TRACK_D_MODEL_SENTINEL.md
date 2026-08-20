# Experiment Card — Track D: Cross-Model Sentinel Replication

## QUESTION
Are GENE's core phenomena (100% semantic inheritance $\tau=1.0$, retrieval-conditioned gating, unsupported pseudo-path formation, and mechanical proofreading rejection) fundamental properties of persistent reasoning or idiosyncratic behaviors of Gemma 3:12B?

## PRIMARY MANIPULATION
Evaluate a frozen 4-pair sentinel battery across 3 distinct open-weight model architectures (`gemma3:12b`, `qwen2.5:7b`, and `llama3.2:3b`):
- **Sentinel 1 (Semantic Inheritance):** Clean vs Mutated Complete Path $\implies$ Predicts $(0, 1, 1, 1, 1)$ Semantic Infection.
- **Sentinel 2 (Retrieval Gate):** Complete Path vs Broken Path ($X_{\text{path}} = 1$ vs $0$) $\implies$ Predicts Active vs `UNKNOWN`.
- **Sentinel 3 (Pseudo-Path Vulnerability):** Explicit Wrong Route vs Zero Route in context $\implies$ Tests single-premise conclusion jumping.
- **Sentinel 4 (Proofreading Defense):** Mechanical first-order certificate validator evaluated on candidate outputs from all models.

## FROZEN CONTROLS
- Strictly identical frozen prompts, zero per-model prompt tweaking.
- Identical JSON schema, greedy decoding ($T=0.0$, seed=42).
- Identical mechanical proofreader code.

## PRIMARY ENDPOINTS
Per model:
- Semantic Inheritance: Replicated / Not Replicated
- Retrieval Gate: Replicated / Not Replicated
- Pseudo-Path Vulnerability: Replicated / Model-Specific
- Proofreader Rejection: Replicated / Not Replicated

## FALSIFIER
If other model families fail to execute clean 2-premise deductions from context (contract failure / hallucination at baseline), the task design requires model-specific prompt engineering. If other models cleanly abstain on zero-route contexts ($P(\text{pseudo-path}) = 0$), the pseudo-path vulnerability is Gemma-specific.

## ZERO-COMPUTE GATE
Mock runner testing that all 4 sentinel prompts parse identically across the test harness.

## LIVE CALL CEILING
24 calls (3 models × 8 calls per sentinel battery). Hard maximum: 32 calls.

## STOP RULE
Stop after 8 calls per model. Do not perform large-scale sweeps.

## STATUS
PROVISIONAL — EXPLORATORY ROUND 1
