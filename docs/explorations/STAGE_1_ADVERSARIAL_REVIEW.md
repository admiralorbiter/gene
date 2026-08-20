# Exploration Round 2 — Stage-1 Adversarial Red Team Review

## 1. Executive Summary & Review Mandate
This document serves as the mandatory pre-execution **Stage-1 Registered-Report Design Audit** for Exploration Round 2. 

Every track is evaluated prior to spending live LLM compute to answer the critical adversarial question:
> *"How could this experiment get the predicted answer without the hypothesized scientific mechanism being true?"*

```
                              STAGE-1 RED TEAM AUDIT VERDICT MATRIX
                              
┌──────────┬──────────────────────┬───────────────────────┬──────────────────────────────────────────┐
│ Track    │ Focus Area           │ Stage-1 Verdict       │ Audit Findings & Pre-Flight Checks       │
├──────────┼──────────────────────┼───────────────────────┼──────────────────────────────────────────┤
│ Track G  │ Multi-Justification  │ PASS                  │ Schema uses generic placeholders; zero   │
│          │                      │                       │ leak; 4/4 deterministic geometries pass. │
├──────────┼──────────────────────┼───────────────────────┼──────────────────────────────────────────┤
│ Track B2 │ Monoculture Hardened │ PASS WITH CAVEAT      │ Doc count strictly N=5; opaque root IDs; │
│          │                      │                       │ neutral prompt; X/Y counterbalanced.     │
├──────────┼──────────────────────┼───────────────────────┼──────────────────────────────────────────┤
│ Track A2 │ Dynamic Memory       │ PASS                  │ Real SQLite updates; active dirty flags; │
│          │                      │                       │ measured latency/tokens; zero pre-bake.  │
├──────────┼──────────────────────┼───────────────────────┼──────────────────────────────────────────┤
│ Track M  │ Model Calibration    │ PASS                  │ 4 functional cases; generic placeholder; │
│          │                      │                       │ fail-closed lexical leak protection.     │
└──────────┴──────────────────────┴───────────────────────┴──────────────────────────────────────────┘
```

---

## 2. Track-by-Track Adversarial Analysis

### Track G: Multi-Justification & Epistemic Recombination
- **Target Leak Audit:** PASS. The schema template specifies:
  `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient", "surviving_paths_count": 0}`.
  Neither `PROTO_X7` nor specific authority IDs are leaked.
- **Baseline Validity:** PASS. `MinimalSupportEngine` passes deterministic tests for single-path, independent redundant support, shared-root collapse, and recombinant survival (`pytest tests/explore_round2/test_track_g.py` $\implies 4/4$).
- **Counterfactual Control:** PASS. Condition A provides $S_1 \text{ (revoked)} + S_2 \text{ (valid)}$; Condition B provides $S_1 \text{ (revoked)} + S_1 \text{ (revoked)}$. The only difference is whether the second path shares the revoked root or is independent.
- **Verdict:** **PASS.** Eligible for live execution (12 calls).

### Track B2: Monoculture Hardening
- **Round 1 Confound Removal Check:**
  - *Document Count:* PASS. Exactly 5 documents in all 4 conditions (`DOC_01` to `DOC_05`).
  - *Authority Status Cues:* PASS. Uses opaque non-semantic identifiers (`root_R1`, `root_R2`, `root_R3`). The word "independent" was caught and removed during preflight testing.
  - *Prompt Steering:* PASS. Prompt asks: *"Based on the retrieved evidence, which security protocol is best supported for station {station}?"* Zero steering regarding source counting or independence.
  - *Directional Counterbalancing:* PASS. Evaluates $3:2$ raw advantage for $X$ alongside $3:2$ raw advantage for $Y$.
- **Caveat:** The model must parse parenthetical citation references (e.g. *"Citing source root_R1..."*) in few-shot natural text. If the model ignores citation clauses entirely, it will default to raw frequency.
- **Verdict:** **PASS WITH CAVEAT.** Eligible for live execution (16 calls).

### Track A2: Dynamic Memory Repair & Lazy Revalidation
- **Real vs Simulated Cost Check:** PASS. The engine executes active SQL `UPDATE` queries against an in-situ SQLite database. Dirty flags are tracked on rows. Latency and node inspection counts are measured directly.
- **Prompt Pre-Baking Check:** PASS. Prompts are assembled dynamically by querying the current state of `episodic_memories` table after the policy execution step.
- **Verdict:** **PASS.** Eligible for live execution (12 calls).

### Track M: Model Calibration Gateway
- **Contract Portability Check:** PASS. Evaluates generic placeholder JSON formatting to resolve the schema-literalism failure discovered in Round 1.
- **Pre-Execution Leak Prevention:** PASS. Verified that `audit_prompt_for_lexical_leakage` fails-closed before any call is made if target protocols appear in the schema.
- **Verdict:** **PASS.** Eligible for calibration battery (8 calls per model family).

---

## 3. Total Proposed Live Compute Allocation
- **Track G:** 12 calls (Gemma 3:12B)
- **Track B2:** 16 calls (Gemma 3:12B)
- **Track A2:** 12 calls (Gemma 3:12B)
- **Track M:** 16 calls (8 calls on Qwen 2.5:3B, 8 calls on Llama 3.2:3B)
- **Total Portfolio Allocation:** **56 live calls** ($\le 90$ ceiling).

---

## 4. Gating Verdict
All four Round-2 experiment designs satisfy the Stage-1 Registered-Report quality gates:
$$\text{Baseline Valid} \land \text{Counterfactual Valid} \land \text{No Answer Leak} \land \text{Role Symmetry} \land \text{Contract Calibrated}$$
**Live compute is approved for Exploration Round 2.**
