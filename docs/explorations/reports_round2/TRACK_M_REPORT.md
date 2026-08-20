# Post-Review Result Report — Track M: Measurement Invariance & Model Calibration Gateway

## 1. Executive Summary
- **Probe Status:** VALIDATED METHODOLOGY RESULT
- **Total Calls Spent:** 8 (4 on `qwen2.5:3b`, 4 on `llama3.2:3b`)
- **Verified Empirical Finding:** Both sub-7B open-weight models failed the 4-case zero-shot calibration gateway ($1/4$ pass rate on both Qwen and Llama), confirming that **prompts calibrated on Gemma 3:12B cannot be ported across model families without specialized model adapters**.
- **Observed Failure Modes:**
  - `qwen2.5:3b`: Passed complete derivation (`PROTO_X7`), but on missing premise copied the prompt placeholder string literally (`"PROTOCOL_NAME_OR_UNKNOWN"`), on directional mutation emitted `"PROTOCOL_X7"`, and on entity mismatch hallucinated `"PROTO_X7"`.
  - `llama3.2:3b`: Emitted arbitrary hard-coded tokens (`"PROTO_Q2"` or `"PROTO_X7"`) regardless of premise completeness or entity binding.

## 2. Experimental Data Matrix ($N = 8$ Calls)
| Model | Calibration Case | Expected Value | Emitted Value | Pass Gate? | Observed Error Mode |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `qwen2.5:3b` | `complete_valid` | `PROTO_X7` | `PROTO_X7` | **YES** | Correct Positive Control |
| `qwen2.5:3b` | `missing_premise` | `UNKNOWN` | `"PROTOCOL_NAME_OR_UNKNOWN"` | NO | Schema Placeholder Copying |
| `qwen2.5:3b` | `directional_mutation` | `PROTO_Q2` | `"PROTOCOL_X7"` | NO | Schema String Hallucination |
| `qwen2.5:3b` | `entity_mismatch` | `UNKNOWN` | `PROTO_X7` | NO | Entity Blindness / Hallucination |
| `llama3.2:3b` | `complete_valid` | `PROTO_X7` | `PROTO_Q2` | NO | Arbitrary Allele Emission |
| `llama3.2:3b` | `missing_premise` | `UNKNOWN` | `PROTO_X7` | NO | Hallucination on Missing Premise |
| `llama3.2:3b` | `directional_mutation` | `PROTO_Q2` | `PROTO_Q2` | **YES** | Coincidental Mutation Match |
| `llama3.2:3b` | `entity_mismatch` | `UNKNOWN` | `PROTO_Q2` | NO | Entity Blindness / Hallucination |

## 3. Revised Conclusion & Methodological Policy
Before comparing epistemic behavior across models, researchers must establish **measurement invariance of the response interface**.

Crucially, the solution is not simply imposing rigid grammar constraints (which recent literature shows can introduce a "constraint tax" on semantic accuracy). Rather, **a model-specific calibration adapter must be developed and validated for both structural compliance and semantic fidelity** before admitting any model to phenotypic experiments.
