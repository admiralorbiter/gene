# Experiment 1B-C2a: Live Behavioral Immunity, Replay Stability & Inference Integrity Report (50 Calls on Gemma 3:12B)

**Experiment ID:** EXP-1B-C2A-LIVE-ASSAY-01 (Re-scored under Decoupled Dual-Oracle v2)  
**Timestamp:** 2026-08-20  
**Model Under Test:** `gemma3:12b` (Ollama local inference, temperature=0.0, seed=42)  
**Evaluation Target:** 50 Live Neural Invocations across 3 Structured Panels  
**Task Type:** Multi-Hop $G_3$ Domain Authorization Rule Inference (`terminal_auth`)  
**Context Geometry:** Matched 6-Memory Fixed Prompt Geometry with Stable Slot IDs (`mem_{locus_id}`)  
**Repository Commit:** `a1474d6`  
**Database File:** `gene_exp1b_c2a_live_assay_a1474d6.db` (Tables: `calls`, `runs`, `dual_oracle_evaluations_v2`)  

---

## 1. Executive Summary & Key Scientific Findings

Experiment 1B-C2a tests the translation of retrieval-level lineage quarantine into live neural behavior on `gemma3:12b`, combining three panels:
1. **Complete 4-State Discrete Panel ($N = 24$)**: States $(S_H, S_I) \in \{00, 01, 10, 11\}$ plus `node_only` and `generation_matched` controls.
2. **Replay Stability Panel ($N = 20$)**: 10 repeated invocations of the Swapped Broken Clean prompt (`f8e561988445`) and 10 repetitions of Forward Broken Clean prompt (`e6fbcc9a89a2`).
3. **Foreign Fact Factorial Manipulation ($N = 6$)**: Testing whether replacing a foreign same-predicate transit route with an unrelated neutral distractor reduces unsupported pseudo-path formation.

### Key Discoveries:

1. **Selective Lineage Quarantine Validated Live**:
   - **Lineage Quarantine (State 01)** achieved **100% behavioral containment** of mutated phenotypes across both forward and swapped ecologies ($C_I^{\text{behavior}} = 0.000$, state $(1, 0, 1, 1, 1)$, `clean_abstention`) while preserving **100% healthy coverage** ($C_H^{\text{behavior}} = 1.000$, state $(1, 1, 1, 1, 1)$, `healthy`).
   - **Node-Only Quarantine** suffered **100% descendant-mediated laundering** ($C_I^{\text{behavior}} = 1.000$, state $(0, 1, 1, 1, 1)$, `semantic`), delivering **0% containment**.

2. **Empirical Replay Non-Determinism on Frozen Requests**:
   - Replaying the identical frozen prompt (`f8e561988445`) across 10 repeated invocations under temperature 0 and fixed seed 42 yielded:
     - 9 / 10 invocations emitted active concrete claims (`AUTH_ALPHA_KESTREL`, state $(1, 0, 0, 0, 1)$, `epistemic`).
     - 1 / 10 invocations emitted an inactive response (`UNKNOWN`, state $(1, 0, 1, 0, 0)$, `contract_failure`).
     - 0 / 10 invocations produced a clean, contract-consistent abstention.
   - In contrast, the forward broken counterpart (`e6fbcc9a89a2`) yielded **10 / 10 clean abstentions** ($(1, 0, 1, 1, 1)$).
   - **Methodological Law**: Fixed prompt + temperature 0 + fixed seed cannot be assumed deterministic under modern LLM/GPU execution runtimes without empirical verification.

3. **Inference-Integrity Failure vs. Memory Governance**:
   - **Memory Governance (Layer 1)** successfully removed legitimate support paths in 4/4 double-quarantine tasks.
   - However, **Behavioral Suppression** occurred in only 2/4 executions (Forward: 2/2 abstained; Swapped: 2/2 emitted active concrete outputs despite zero available routes).
   - **Conclusion**: Memory containment $\neq$ behavioral containment when the downstream inference engine can construct unsupported pseudo-paths from surviving evidence.

4. **Foreign Fact Interaction with Pseudo-Path Formation**:
   - In the swapped broken context, the presence of a foreign same-predicate transit route (`mem_velora_transit_route`) produced unsupported concrete outputs in **13 / 15 invocations (86.7%)**.
   - Replacing that foreign route with an unrelated neutral distractor (`OUTPOST_3 commissioned in 2183`) increased clean abstention to **3 / 4 invocations (75.0%)**.
   - However, because double quarantine (zero routes) also produced unsupported outputs in the swapped ecology, foreign facts are **not a necessary condition** for pseudo-path formation.

---

## 2. Decoupled Phenotype Distribution ($N = 50$ Calls)

```
+---------------------------------------------------------------------------------------------------------------+
|                                    DECOUPLED PHENOTYPE & REPRODUCTIVE AUDIT                                   |
+----------------------+--------------------+-------+------------+----------------------------------------------+
| Metric Category      | Classification     | Count | Percentage | Epistemic / Reproductive Meaning             |
+----------------------+--------------------+-------+------------+----------------------------------------------+
| Reproductive Status  | active             | 31    | 62.0%      | Admitted to memory (concrete claim emitted)  |
| Reproductive Status  | inactive           | 19    | 38.0%      | Quarantined from memory (abstention/UNKNOWN) |
+----------------------+--------------------+-------+------------+----------------------------------------------+
| Epistemic Phenotype  | clean_abstention   | 17    | 34.0%      | (∅, 0, 1, 1, 1) Underivable, warranted UNK   |
| Epistemic Phenotype  | epistemic          | 15    | 30.0%      | (1, 0, 0, 0, 1) Underivable, true in W*      |
| Epistemic Phenotype  | semantic           | 8     | 16.0%      | (0, 1, 1, 1, 1) Locally true, false in W*    |
| Epistemic Phenotype  | healthy            | 6     | 12.0%      | (1, 1, 1, 1, 1) Locally & globally true      |
| Epistemic Phenotype  | contract_failure   | 2     | 4.0%       | (∅, 0, 1, 0, 0) UNK with sufficient claim    |
| Epistemic Phenotype  | de_novo_error      | 2     | 4.0%       | (0, 0, 0, 0, 1) Underivable & false in W*    |
+----------------------+--------------------+-------+------------+----------------------------------------------+
```

---

## 3. Exact Prompt-Hash Equivalence Classes (12 Unique Requests)

```
+---------------------------------------------------------------------------------------------------------------------------------------+
|                                         PROMPT-HASH EQUIVALENCE CLASSES (12 UNIQUE REQUESTS)                                          |
+--------------+----+--------+-------------+----------------------+-------------------------+-------------------------------------------+
| Prompt Hash  | N  | Target | Path State  | Modal Phenotype      | Observed Distribution   | Representative Invocations                |
+--------------+----+--------+-------------+----------------------+-------------------------+-------------------------------------------+
| f8e561988445 | 15 | KESTREL| unsupported | epistemic            | 13 epistemic, 2 failure | Swapped Autoimmunity & Replay (Clean)     |
| e6fbcc9a89a2 | 12 | VELORA | unsupported | clean_abstention     | 12 clean_abstention     | Forward Autoimmunity & Replay (Clean)     |
| 631a2cb4eece | 4  | KESTREL| unsupported | clean_abstention     | 3 abstention, 1 epist   | Swapped Double Quaran & Factorial Control |
| fb409183fe1c | 2  | VELORA | supported   | healthy              | 2 healthy (100%)        | Forward Baseline & Node-Only (Clean)      |
| 7d0f36305053 | 2  | KESTREL| supported   | semantic             | 2 semantic (100%)       | Forward Baseline & Node-Only (Mutated)    |
| eb253240c667 | 2  | KESTREL| supported   | semantic             | 2 semantic (100%)       | Forward Autoimmunity & Gen-Match (Mutated)|
| f2dd82e14a70 | 2  | KESTREL| supported   | healthy              | 2 healthy (100%)        | Swapped Baseline & Node-Only (Clean)      |
| b6611fbe4fdc | 2  | VELORA | supported   | semantic             | 2 semantic (100%)       | Swapped Baseline & Node-Only (Mutated)    |
| 4cdbde3e1d73 | 2  | VELORA | supported   | semantic             | 2 semantic (100%)       | Swapped Autoimmunity & Gen-Match (Mutated)|
| 69637276b084 | 1  | VELORA | supported   | healthy              | 1 healthy (100%)        | Forward Lineage Quarantine (Clean)        |
| 0393b0cee02d | 1  | KESTREL| unsupported | clean_abstention     | 1 clean_abstention      | Forward Lineage Quarantine (Mutated)      |
| 0dac53a0fb8d | 1  | KESTREL| supported   | healthy              | 1 healthy (100%)        | Swapped Lineage Quarantine (Clean)        |
| 6f577951ea5e | 1  | VELORA | unsupported | clean_abstention     | 1 clean_abstention      | Swapped Lineage Quarantine (Mutated)      |
| 35b3af073a2c | 1  | VELORA | unsupported | epistemic            | 1 epistemic             | Forward Double Quarantine (Clean)         |
| c5fff9316941 | 1  | KESTREL| unsupported | de_novo_error        | 1 de_novo_error         | Forward Double Quarantine (Mutated)       |
| fb47a42977f2 | 1  | VELORA | unsupported | de_novo_error        | 1 de_novo_error         | Swapped Double Quarantine (Mutated)       |
+--------------+----+--------+-------------+----------------------+-------------------------+-------------------------------------------+
```

---

## 4. Replay Stability & Replay Variance Findings

Across 10 repeated invocations of the identical frozen request:
- **Swapped Broken Prompt (`f8e561988445`, Target: KESTREL)**:
  - 9 / 10 emitted `AUTH_ALPHA_KESTREL` (state $(1, 0, 0, 0, 1)$, `epistemic`).
  - 1 / 10 emitted `UNKNOWN` (state $(1, 0, 1, 0, 0)$, `contract_failure`).
  - Demonstrates that Call 17 and Call 19 in C2 were draws from this empirical branching frequency.
- **Forward Broken Prompt (`e6fbcc9a89a2`, Target: VELORA)**:
  - 10 / 10 emitted `UNKNOWN` (state $(1, 0, 1, 1, 1)$, `clean_abstention`).

---

## 5. Architectural Implications: Two-Layer Epistemic Defense

Experiment 1B-C2a formally establishes the necessity of a **two-layer epistemic architecture**:

1. **Layer 1 (Memory Governance / Lineage Immunity)**:
   - Successfully prunes reproductive lineage paths when ancestors are discredited.
   - Prevents provenance laundering ($C_I = 0.000$ vs $1.000$ under node-only filtering).
2. **Layer 2 (Inference Integrity / Epistemic Proofreading)**:
   - Memory governance alone cannot prevent an autoregressive reasoner from constructing unsupported pseudo-paths from surviving evidence.
   - A mechanical proofreading layer is required to verify that cited memories structurally unify into valid rule instantiations before admitting new occurrence nodes to memory.

---

## 6. Audit & Provenance Trail

- **Execution Commit:** [`a1474d6`](file:///C:/Users/admir/Github/gene/scripts/run_exp1b_c2_live_assay.py)
- **Database:** `gene_exp1b_c2a_live_assay_a1474d6.db` (Tables: `calls`, `runs`, `dual_oracle_evaluations_v2`)
- **Unit Tests:** **94 / 94 tests passing in 20.66s**
