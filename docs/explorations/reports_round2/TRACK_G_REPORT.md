# Post-Review Result Report — Track G: Multi-Justification & Epistemic Recombination

## 1. Executive Summary
- **Probe Status:**
  - **G-Formal Engine:** VALIDATED FORMAL PROTOTYPE
  - **G-Live Neural Assay:** CONFOUNDED — SUPPORT-COUNT LEAK + NO NEURAL BASELINE
- **Total Calls Spent:** 12 (Gemma 3:12B)
- **What Was Verified (Deterministic Support Algebra):** `MinimalSupportEngine` in `src/gene/experiments/multi_justification.py` correctly implements minimal support sets $S(c)$, ancestor invalidation, and hitting-set cut resilience $\kappa(c)$ across all 4 canonical geometries ($AB \to C$, $AB + DE \to C$, $AX + AY \to C$, $AI + BH \to C$).
- **Why the Live Neural Assay Is Confounded:**
  1. **Auxiliary Schema Answer Leakage:** The prompt schema template contained `"surviving_paths_count": 0` in both conditions. For `independent_survival`, the expected value was $1$. The prompt literally instructed the model that 0 surviving paths existed.
  2. **Missing Positive Baseline Control:** No un-revoked baseline control (where both $S_1$ and $S_2$ are valid) was evaluated to prove that Gemma can derive `PROTO_X7` under this specific Horn-clause prompt structure.
  3. **Uninterpretable Abstention:** Because of the schema count error and missing baseline, Gemma's universal `UNKNOWN` emissions ($12/12$ calls) cannot be scientifically attributed to a "conservative revocation bias."

## 2. Experimental Data Matrix ($N = 12$ Calls)
| Station | Condition | Target Protocol | Expected Surviving Paths | Schema Template Value | Emitted Protocol | Result Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| VELORA | `independent_survival` | `PROTO_X7` | 1 | **0 (Error)** | `UNKNOWN` | Confounded by schema value |
| VELORA | `shared_collapse` | `UNKNOWN` | 0 | 0 | `UNKNOWN` | Confounded by schema value |
| KESTREL | `independent_survival` | `PROTO_X7` | 1 | **0 (Error)** | `UNKNOWN` | Confounded by schema value |
| KESTREL | `shared_collapse` | `UNKNOWN` | 0 | 0 | `UNKNOWN` | Confounded by schema value |
| VELORA | `independent_survival` | `PROTO_X7` | 1 | **0 (Error)** | `UNKNOWN` | Confounded by schema value |
| VELORA | `shared_collapse` | `UNKNOWN` | 0 | 0 | `UNKNOWN` | Confounded by schema value |
| KESTREL | `independent_survival` | `PROTO_X7` | 1 | **0 (Error)** | `UNKNOWN` | Confounded by schema value |
| KESTREL | `shared_collapse` | `UNKNOWN` | 0 | 0 | `UNKNOWN` | Confounded by schema value |
| VELORA | `independent_survival` | `PROTO_X7` | 1 | **0 (Error)** | `UNKNOWN` | Confounded by schema value |
| VELORA | `shared_collapse` | `UNKNOWN` | 0 | 0 | `UNKNOWN` | Confounded by schema value |
| KESTREL | `independent_survival` | `PROTO_X7` | 1 | **0 (Error)** | `UNKNOWN` | Confounded by schema value |
| KESTREL | `shared_collapse` | `UNKNOWN` | 0 | 0 | `UNKNOWN` | Confounded by schema value |

## 3. Revised Conclusion & Hardening Protocol
The deterministic minimal support algebra is sound and valuable. 

The live neural experiment remains to be executed under a clean protocol:
1. Remove all auxiliary numeric fields from prompt schemas (or use generic placeholders like `"surviving_paths_count": "INTEGER"`).
2. Include an explicit positive control arm with clean, un-revoked multi-path support.
3. Evaluate whether Gemma can utilize surviving alternative derivations when one path is retracted.
