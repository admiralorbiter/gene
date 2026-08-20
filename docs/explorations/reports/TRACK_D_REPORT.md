# Post-Review Result Report — Track D: Cross-Model Sentinel Replication

## 1. Executive Summary
- **Probe Status:** PROMISING METHODOLOGY RESULT (Contract Portability Failure)
- **Total Calls Spent:** 24 (8 calls each across `gemma3:12b`, `qwen2.5:3b`, and `llama3.2:3b`)
- **Key Methodological Finding:** **Assay calibration does not transfer across model families.** GENE's zero-shot JSON response contract, calibrated on Gemma 3:12B, completely failed when ported to smaller open-weight models (`qwen2.5:3b`, `llama3.2:3b`).
- **Detailed Model Behaviors:**
  - **Gemma 3:12B:** Passed semantic inheritance (clean $\to$ `PROTO_X7`, mutated $\to$ `PROTO_Q2`) and entity-binding abstention on Sentinel 4.2 (`UNKNOWN`). Failed retrieval gating on Sentinel 2.2 (`ROUTE_ALPHA` on broken path without proofreader).
  - **Qwen 2.5:3B:** Successfully executed 2-hop retrieval gating on Sentinel 2 (`ROUTE_ALPHA` on complete path, `UNKNOWN` on broken path). However, on Sentinels 1, 3, and 4, it exhibited severe schema literalism, emitting the pipe-delimited enum template literally (e.g. `"PROTO_X7|PROTO_Q2|UNKNOWN"`).
  - **Llama 3.2:3B:** Emitted literal enum template strings across all 8 calls, failing JSON value extraction.
- **Audit Corrections:**
  - The initial claim of "cross-model mechanism replication" is incorrect: cross-model semantic inheritance was not successfully tested due to schema failures on Qwen and Llama.
  - `evaluate_epistemic_proofreading` was imported but was never invoked in the live execution loop.
  - No few-shot demonstrations were evaluated in this batch.

## 2. Experimental Data Matrix ($N = 24$ Calls)
| Model | Sentinel Key | Target Phenotype | Emitted String | Contract Status | Evaluation |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `gemma3:12b` | `sentinel_1_clean` | `PROTO_X7` | `PROTO_X7` | Clean | Semantic Inheritance (Clean) |
| `gemma3:12b` | `sentinel_1_mutated` | `PROTO_Q2` | `PROTO_Q2` | Clean | Semantic Inheritance (Mutated) |
| `gemma3:12b` | `sentinel_2_complete` | `ROUTE_ALPHA` | `ROUTE_ALPHA` | Clean | Complete Path Active |
| `gemma3:12b` | `sentinel_2_broken` | `UNKNOWN` | `ROUTE_ALPHA` | Clean | Broken Path Active (Failed Gating) |
| `gemma3:12b` | `sentinel_3_wrong_route`| `UNKNOWN` | `AUTH_ALPHA` | Clean | Pseudo-path Jump |
| `gemma3:12b` | `sentinel_3_zero_route` | `UNKNOWN` | `AUTH_ALPHA` | Clean | Pseudo-path Jump |
| `gemma3:12b` | `sentinel_4_valid_cert` | `AUTH_ALPHA` | `AUTH_ALPHA` | Clean | Valid Certificate Active |
| `gemma3:12b` | `sentinel_4_cross_binding`| `UNKNOWN` | `UNKNOWN` | Clean | Clean Abstention on Entity Mismatch |
| `qwen2.5:3b` | `sentinel_1_clean` | `PROTO_X7` | `"PROTO_X7\|PROTO_Q2\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `qwen2.5:3b` | `sentinel_1_mutated` | `PROTO_Q2` | `"PROTO_X7\|PROTO_Q2\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `qwen2.5:3b` | `sentinel_2_complete` | `ROUTE_ALPHA` | `ROUTE_ALPHA` | Clean | Complete Path Active |
| `qwen2.5:3b` | `sentinel_2_broken` | `UNKNOWN` | `UNKNOWN` | Clean | Clean Broken Path Abstention |
| `qwen2.5:3b` | `sentinel_3_wrong_route`| `UNKNOWN` | `"AUTH_ALPHA\|AUTH_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `qwen2.5:3b` | `sentinel_3_zero_route` | `UNKNOWN` | `"AUTH_ALPHA\|AUTHBETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `qwen2.5:3b` | `sentinel_4_valid_cert` | `AUTH_ALPHA` | `"AUTH_ALPHA\|AUTH_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `qwen2.5:3b` | `sentinel_4_cross_binding`| `UNKNOWN` | `"AUTH_ALPHA\|AUTH_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `llama3.2:3b` | `sentinel_1_clean` | `PROTO_X7` | `"PROTO_X7\|PROTO_Q2\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `llama3.2:3b` | `sentinel_1_mutated` | `PROTO_Q2` | `"PROTO_X7\|PROTO_Q2\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `llama3.2:3b` | `sentinel_2_complete` | `ROUTE_ALPHA` | `"ROUTE_ALPHA\|ROUTE_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `llama3.2:3b` | `sentinel_2_broken` | `UNKNOWN` | `"ROUTE_ALPHA\|ROUTE_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `llama3.2:3b` | `sentinel_3_wrong_route`| `UNKNOWN` | `"AUTH_ALPHA\|AUTH_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `llama3.2:3b` | `sentinel_3_zero_route` | `UNKNOWN` | `"AUTH_ALPHA\|AUTH_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `llama3.2:3b` | `sentinel_4_valid_cert` | `AUTH_ALPHA` | `"AUTH_ALPHA\|AUTH_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |
| `llama3.2:3b` | `sentinel_4_cross_binding`| `UNKNOWN` | `"AUTH_BETA\|UNKNOWN"` | Schema Literalism | Untested (Contract Failure) |

## 3. Revised Conclusion & Process Lesson
This track yielded an essential research insight: **changing the model changes the measuring instrument**. Cross-model replication cannot begin by porting prompts designed for Gemma 3:12B. A formal model-specific calibration stage (validating contract adherence, JSON enum syntax, or grammar constraints) must precede any cross-family phenotypic comparison.
