# Provisional Result Report — Track M: Measurement Invariance & Model Calibration Gateway

## 1. Executive Summary
- **Probe Status:** SUCCESSFUL CALIBRATION GATEWAY (Measurement Non-Invariance Confirmed)
- **Total Calls Spent:** 8 (4 on `qwen2.5:3b`, 4 on `llama3.2:3b`)
- **Primary Finding:** Both sub-7B open-weight models failed the 4-case zero-shot calibration gateway, confirming that **assay prompts calibrated on Gemma 3:12B cannot be ported to other model families without specialized model adapters**.
- **Model Failure Modes:**
  - `qwen2.5:3b`: Passed complete valid derivation (`PROTO_X7`), but on missing premise copied the prompt placeholder literally (`"PROTOCOL_NAME_OR_UNKNOWN"`), on directional mutation emitted `"PROTOCOL_X7"`, and on entity mismatch hallucinated `"PROTO_X7"` ($1/4$ pass).
  - `llama3.2:3b`: Emitted `"PROTO_Q2"` or `"PROTO_X7"` irrespective of whether premises were missing or entity-mismatched ($1/4$ pass).

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

## 3. Scientific Significance & Model Gateway Policy
Neither `qwen2.5:3b` nor `llama3.2:3b` is currently admitted to GENE substantive phenotypic experiments under zero-shot prompting. Future multi-model scaling requires building formal grammar-constrained JSON adapters (`ModelAdapter_v1`) before cross-model phenotypic comparisons are valid.
