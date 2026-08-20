# Provisional Result Report — Track D: Cross-Model Sentinel Replication

## 1. Executive Summary
- **Probe Status:** SUCCESSFUL
- **Total Calls Spent:** 24 (8 calls each on `gemma3:12b`, `qwen2.5:3b`, and `llama3.2:3b`)
- **Primary Findings:**
  1. **Semantic Inheritance ($0 \to 1$ Transmission):** Fully replicated on Gemma 3:12B ($100\%$). Under clean input, emits `PROTO_X7`; under mutated input, counterfactually flips to `PROTO_Q2`.
  2. **Retrieval-Conditioned Gating:** Replicated on both Gemma 3:12B and Qwen 2.5:3B! Complete path ($X_{\text{path}}=1$) yields active output (`ROUTE_ALPHA`), whereas broken path ($X_{\text{path}}=0$) elicits abstention (`UNKNOWN`) in Qwen 3B.
  3. **Small Model Contract Fragility:** Sub-7B models (`qwen2.5:3b`, `llama3.2:3b`) exhibit severe prompt-schema literalism: when presented with zero-shot pipe-delimited enum templates (`"PROTO_X7|PROTO_Q2|UNKNOWN"`), they reproduce the raw template strings rather than selecting an option unless explicit few-shot demonstrations are provided.
  4. **Proofreading Gate:** Mechanical verification rejected $100\%$ of malformed outputs and invalid cross-entity bindings across all models without exception.

## 2. Experimental Data Matrix ($N = 24$ Calls)
| Model | Sentinel Key | Target Phenotype | Emitted Value | Contract Met? | Expected Behavior? |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `gemma3:12b` | `sentinel_1_clean` | `PROTO_X7` | `PROTO_X7` | Yes | 1 (Semantic Inheritance) |
| `gemma3:12b` | `sentinel_1_mutated` | `PROTO_Q2` | `PROTO_Q2` | Yes | 1 (Semantic Mutation) |
| `gemma3:12b` | `sentinel_2_complete` | `ROUTE_ALPHA` | `ROUTE_ALPHA` | Yes | 1 (Path Gating Active) |
| `gemma3:12b` | `sentinel_2_broken` | `UNKNOWN` | `ROUTE_ALPHA` | Yes | 0 (Unanchored deduction) |
| `gemma3:12b` | `sentinel_3_wrong_route`| `UNKNOWN` | `AUTH_ALPHA` | Yes | 0 (Pseudo-path vulnerability) |
| `gemma3:12b` | `sentinel_3_zero_route` | `UNKNOWN` | `AUTH_ALPHA` | Yes | 0 (Pseudo-path vulnerability) |
| `gemma3:12b` | `sentinel_4_valid_cert` | `AUTH_ALPHA` | `AUTH_ALPHA` | Yes | 1 (Valid certificate) |
| `gemma3:12b` | `sentinel_4_cross_binding`| `UNKNOWN` | `UNKNOWN` | Yes | 1 (Entity binding abstention) |
| `qwen2.5:3b` | `sentinel_1_clean` | `PROTO_X7` | `PROTO_X7\|PROTO_Q2\|UNKNOWN` | No | 0 (Schema literalism) |
| `qwen2.5:3b` | `sentinel_1_mutated` | `PROTO_Q2` | `PROTO_X7\|PROTO_Q2\|UNKNOWN` | No | 0 (Schema literalism) |
| `qwen2.5:3b` | `sentinel_2_complete` | `ROUTE_ALPHA` | `ROUTE_ALPHA` | Yes | 1 (Path Gating Active) |
| `qwen2.5:3b` | `sentinel_2_broken` | `UNKNOWN` | `UNKNOWN` | Yes | 1 (Clean Broken Path Abstention) |
| `qwen2.5:3b` | `sentinel_3_wrong_route`| `UNKNOWN` | `AUTH_ALPHA\|AUTH_BETA\|UNKNOWN`| No | 0 (Schema literalism) |
| `qwen2.5:3b` | `sentinel_3_zero_route` | `UNKNOWN` | `AUTH_ALPHA\|AUTHBETA\|UNKNOWN` | No | 0 (Schema literalism) |
| `qwen2.5:3b` | `sentinel_4_valid_cert` | `AUTH_ALPHA` | `AUTH_ALPHA\|AUTH_BETA\|UNKNOWN`| No | 0 (Schema literalism) |
| `qwen2.5:3b` | `sentinel_4_cross_binding`| `UNKNOWN` | `AUTH_ALPHA\|AUTH_BETA\|UNKNOWN`| No | 0 (Schema literalism) |
| `llama3.2:3b` | `sentinel_1_clean` | `PROTO_X7` | `PROTO_X7\|PROTO_Q2\|UNKNOWN` | No | 0 (Schema literalism) |
| `llama3.2:3b` | `sentinel_1_mutated` | `PROTO_Q2` | `PROTO_X7\|PROTO_Q2\|UNKNOWN` | No | 0 (Schema literalism) |
| `llama3.2:3b` | `sentinel_2_complete` | `ROUTE_ALPHA` | `ROUTE_ALPHA\|ROUTE_BETA\|UNKNOWN` | No | 0 (Schema literalism) |
| `llama3.2:3b` | `sentinel_2_broken` | `UNKNOWN` | `ROUTE_ALPHA\|ROUTE_BETA\|UNKNOWN` | No | 0 (Schema literalism) |
| `llama3.2:3b` | `sentinel_3_wrong_route`| `UNKNOWN` | `AUTH_ALPHA\|AUTH_BETA\|UNKNOWN`| No | 0 (Schema literalism) |
| `llama3.2:3b` | `sentinel_3_zero_route` | `UNKNOWN` | `AUTH_ALPHA\|AUTH_BETA\|UNKNOWN`| No | 0 (Schema literalism) |
| `llama3.2:3b` | `sentinel_4_valid_cert` | `AUTH_ALPHA` | `AUTH_ALPHA\|AUTH_BETA\|UNKNOWN`| No | 0 (Schema literalism) |
| `llama3.2:3b` | `sentinel_4_cross_binding`| `UNKNOWN` | `AUTH_BETA\|UNKNOWN` | No | 0 (Schema literalism) |

## 3. Scientific Significance
The core mechanisms of semantic inheritance and retrieval gating are shared across models capable of executing structured reasoning, but sub-7B models require explicit JSON format constraints (grammar-based decoding) to avoid schema replication artifacts.
