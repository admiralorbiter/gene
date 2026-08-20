# Exploration Round 3 — Stage-1 Registered-Report & Machine-Diff Audit

## 1. Executive Summary & Review Mandate
This document executes the mandatory pre-execution **Stage-1 Registered-Report Audit** for **Exploration Round 3: *When One Belief Has Many Reasons*** across all five tracks.

Zero live LLM compute is authorized until all 7 mechanical checklist items are audited:

```
                           STAGE-1 MECHANICAL AUDIT MATRIX
                           
┌──────────┬─────────────────────────────┬─────────────────┬──────────────────────────────────────────┐
│ Track    │ Focus Area                  │ Stage-1 Verdict │ 7-Item Mechanical Audit Status           │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track H  │ Coalition Causality         │ PASS            │ Schema placeholders; lattice validated;  │
│          │ (Overdetermination Lattice) │                 │ contemporaneous evaluation logging wired.│
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track G2 │ Non-Destructive Immunity    │ PASS            │ Zero numeric count leaks; un-revoked CTL │
│          │ (Clean 3-Arm Design)        │                 │ baseline included; diff purity verified. │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track B3 │ Monoculture Multiverse      │ PASS            │ Full 16-cell factorial matrix; machine   │
│          │ (Factorialized Controls)    │                 │ diff isolates only source phrase tokens. │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track S  │ Support Acquisition         │ PASS            │ Backward-slicing compiler verified;      │
│          │ (Trace-to-Support Compiler) │                 │ zero prompt answer leaks.                │
├──────────┼─────────────────────────────┼─────────────────┼──────────────────────────────────────────┤
│ Track L  │ Independence Laundering     │ PASS            │ Progressive G0->G3 cascade; generic      │
│          │ (Diversity Inflation)       │                 │ "INTEGER" schema placeholder.            │
└──────────┴─────────────────────────────┴─────────────────┴──────────────────────────────────────────┘
```

---

## 2. Seven-Item Mechanical Checklist Verification

### 1. Schema Field Audit (Generic Placeholders Only)
- **Track H:** `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}` $\implies$ **PASS.**
- **Track G2:** `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}` $\implies$ **PASS.** (Auxiliary `surviving_paths_count` field eliminated).
- **Track B3:** `{"station": "STATION_NAME", "adjudicated_protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}` $\implies$ **PASS.**
- **Track S:** `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}` $\implies$ **PASS.**
- **Track L:** `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "estimated_independent_sources": "INTEGER", "evidence_status": "sufficient|insufficient"}` $\implies$ **PASS.**

### 2. Positive Control Baseline
- **Track H:** Baseline arm with 0 knockouts evaluated on $AB \to C$ and $AB + DE \to C$ ($P(\text{Target}) = 1.0$).
- **Track G2:** `unrevoked_baseline` arm included with both $S_1$ and $S_2$ active ($P(\text{Target}) = 1.0$).
- **Track S:** `single_path` and `recombinant_path` positive derivations included.
- **Track L:** $G_0$ True Root and $G_1$ Cited Paraphrase baselines included.
- **Status:** **PASS.**

### 3. Position Permutation & Positional Decoupling
- **Track B3:** Factorially permutes document presentation order ([1,2,3,4,5] forward vs [4,1,5,2,3] interleaved) across all root conditions.
- **Status:** **PASS.**

### 4. Cost Verification & Active Execution
- Every runner executes actual live API calls through `ExplorationHarness.execute_call()`.
- Zero direct-write string insertions bypassing the client.
- **Status:** **PASS.**

### 5. Contemporaneous Evaluation Enforcement ($N_{\text{evaluations}} = N_{\text{calls}}$)
- Every runner invokes `harness.record_evaluation()` immediately inside the execution loop.
- **Status:** **PASS.**

### 6. Causal-Role Equivariance
- **Track B3:** Role-swaps token assignments (`M4_majority` vs `Q7_majority`) and station entities (`VELORA` vs `KESTREL`).
- **Track L:** Evaluates across distinct target protocols (`PROTO_ALPHA` vs `PROTO_OMEGA`).
- **Status:** **PASS.**

### 7. Contrast Reconstruction via Automated Machine Diff
Machine diff between Track B3 Independent vs Monoculture prompts confirms that **only the source attribution clauses change**:
```diff
--- treatment (independent)
+++ control (monoculture)
@@ -1,7 +1,7 @@
 RETRIEVED EVIDENCE:
 - DOC_01: Source root_R1 states station VELORA requires protocol PROTO_M4.
-- DOC_02: Source root_R2 states station VELORA requires protocol PROTO_M4.
-- DOC_03: Source root_R3 states station VELORA requires protocol PROTO_M4.
+- DOC_02: Citing source root_R1, field log notes station VELORA requires protocol PROTO_M4.
+- DOC_03: Archive relay quoting source root_R1 confirms station VELORA requires protocol PROTO_M4.
 - DOC_04: Source root_R4 states station VELORA requires protocol PROTO_Q7.
 - DOC_05: Source root_R5 states station VELORA requires protocol PROTO_Q7.
```
- **Status:** **PASS.**

---

## 3. Total Proposed Live Compute Allocation
- **Track H (Coalition Causality):** 18 calls
- **Track G2 (Non-Destructive Immunity):** 18 calls
- **Track B3 (Monoculture Multiverse):** 24 calls
- **Track S (Support Acquisition):** 8 calls
- **Track L (Independence Laundering):** 16 calls
- **Total Portfolio Allocation:** **84 live calls** ($\le 84$ ceiling).

---

## 4. Gating Verdict
All five Round-3 designs satisfy the 7-item registered-report checklist:
$$\text{Audit Passed} \implies \text{Live Compute Approved for Exploration Round 3.}$$
