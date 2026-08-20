# Round 2 Experiment Card — Track M: Measurement Invariance & Model Calibration Gateway

## 1. Scientific Objective
- **Core Objective:** Establish a standardized, lightweight calibration gate to determine the minimal response contract under which open-weight models (`qwen2.5:3b`, `llama3.2:3b`) demonstrate the same experimental construct as `gemma3:12b`.
- **Target Phenomenon:** Measurement invariance across heterogeneous model families. Models must demonstrate contract comprehension before being admitted to phenotypic experiments.

## 2. The 4-Test Miniature Calibration Battery
Each model family is evaluated against 4 deterministic functional cases:
1. **Case 1: Complete Valid Derivation (Positive Control)**
   - Complete support path present in context $\to$ must emit expected target value (e.g. `PROTO_X7`).
2. **Case 2: Missing Premise Abstention (Negative Control)**
   - Required intermediate premise missing $\to$ must emit `UNKNOWN` with `evidence_status: "insufficient"`.
3. **Case 3: Directional Mutation Sensitivity (Intervention Control)**
   - Founder premise mutated $\to$ must emit mutated target value (e.g. `PROTO_Q2`).
4. **Case 4: Entity Mismatch / Cross-Binding Abstention (Binding Control)**
   - Premises refer to disjoint entity IDs $\to$ must abstain (`UNKNOWN`).

## 3. Multiverse Contract Variations Evaluated
To eliminate the schema-literalism failure discovered in Round 1 Track D, we test four response contract variants:
- **Variant 1: Raw Pipe-Delimited Enum (Round 1 Baseline):** `{"protocol": "PROTO_X7|PROTO_Q2|UNKNOWN"}`
- **Variant 2: Generic Placeholder Schema:** `{"protocol": "PROTOCOL_NAME_OR_UNKNOWN"}`
- **Variant 3: JSON Schema with Type/Enum Definition:** Structured Pydantic/Ollama `format: { "type": "object", ... }`
- **Variant 4: 1-Shot Structural Demonstration:** A neutral synthetic example showing valid JSON extraction.

## 4. Planned Call Budget
- 2 models (`qwen2.5:3b`, `llama3.2:3b`) × 4 test cases × 2 contract variants = **16 live calls** (max 24).
- **Admission Criterion:** A model adapter is declared **CALIBRATED** if and only if it achieves 4/4 on the calibration battery without schema literalism or hallucinated outputs.
