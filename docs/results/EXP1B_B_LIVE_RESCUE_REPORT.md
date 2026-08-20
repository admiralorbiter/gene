# Experiment 1B-B Live Mechanism Verification Report

**Experiment ID:** EXP-1B-B-LIVE-RESCUE-01  
**Timestamp:** 2026-08-20  
**Model Family:** `gemma3:12b` (Local Ollama, SHA256: `f4031aab637d...`)  
**Repository Commit:** `22579027` (HEAD)  
**Database File:** `gene_exp1b_live_boundary_rescue_20260820_133706.db`  
**Total Live Calls:** 48 (24 calls at $k=4$, 24 calls at $k=6$)  

---

## 1. Executive Summary

In Experiment 1B-B, we investigated whether the memory retrieval layer functions as a causal gatekeeper for multi-generational transmission in synthetic epistemic networks. 

By evaluating matched clean and infected worlds across preflight-mapped retrieval boundaries, we demonstrate:
1. **Retrieval-Mediated Boundary Collapse ($k=4, N_{\text{hard}}=4$)**: When lexical clutter competition prevents complete multi-hop proof assembly ($X_{\text{path}, G1} = 0.0\%$), `gemma3:12b` consistently abstains across both generations ($N_{\text{written}} = 0$). Empirical $\hat{W}$ is unestimable, and the lineage is extinguished.
2. **Retrieval-Mediated Boundary Rescue ($k=6, N_{\text{hard}}=4$)**: Expanding the retrieval budget without altering the underlying world restores complete G1 proof assembly ($X_{\text{path}, G1} = 100.0\%$), rescuing the lineage from extinction into active multi-generational replication with 100% semantic allele fidelity.
3. **Expression Asymmetry Discovery**: Under complete G1 path recovery ($X_{\text{path}, G1} = 100\%$), clean G1 claims expressed at 50% (2/4) while infected G1 claims expressed at 100% (4/4), identifying a specific G1 derivation sensitivity to context composition and slot labeling.

---

## 2. Experimental Design & Parameters

```
Target Boundary Worlds:
  - World 0: Seed 7000, Station VELORA, Clean Allele KIRA, Mutated Allele TAL
  - World 1: Seed 7005, Station KESTREL, Clean Allele KIRA, Mutated Allele TAL

Evaluated Arms:
  - Clean Arm (H): Canonical ground truth
  - Infected Arm (I): Single point mutation at founder locus (reports_to: KIRA -> TAL)

Retrieval Budget Grid:
  - Collapse Condition: top_k = 4, N_hard = 4, N_easy = 4 (Candidate pool = 12 nodes)
  - Rescue Condition:   top_k = 6, N_hard = 4, N_easy = 4 (Candidate pool = 12 nodes)

Call Budget Calculation:
  2 worlds x 2 arms x (2 G1 tasks + 4 G2 tasks) = 24 calls per condition
  Total = 48 live LLM calls
```

---

## 3. Quantitative Results Ledger

### 3.1 Aggregate Condition Summary

| Condition | Arm | $X_{F, G1}$ | $X_{A, G1}$ | $X_{\text{path}, G1}$ | G1 Written (Active) | G1 Semantic Fidelity | G2 Parent Recall | G2 Written (Active) | G2 Semantic Fidelity | Inactive Abstentions |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$k=4$** | Clean | 50.0% (2/4) | 50.0% (2/4) | **0.0% (0/4)** | 0 / 4 (0%) | N/A | 0.0% (0/8) | 0 / 8 (0%) | N/A | **12 / 12 (100%)** |
| **$k=4$** | Infected | 50.0% (2/4) | 50.0% (2/4) | **0.0% (0/4)** | 0 / 4 (0%) | N/A | 0.0% (0/8) | 0 / 8 (0%) | N/A | **12 / 12 (100%)** |
| **$k=6$** | Clean | 100.0% (4/4) | 100.0% (4/4) | **100.0% (4/4)** | 2 / 4 (50%) | 100% Healthy | 50.0% (4/8) | 4 / 8 (50%) | 100% Healthy | 6 / 12 (50%) |
| **$k=6$** | Infected | 100.0% (4/4) | 100.0% (4/4) | **100.0% (4/4)** | **4 / 4 (100%)** | **100% Semantic** | 75.0% (6/8) | **6 / 8 (75%)** | **100% Semantic** | 2 / 12 (17%) |

---

### 3.2 Key Scientific Findings

1. **Sharp Boundary Collapse**:
   At $k=4$, the multi-hop proof path was incomplete in every instance ($X_{\text{path}, G1} = 0.0\%$). Gemma adhered strictly to epistemic contract rules, outputting `UNKNOWN` for all 24 queries. Because no concrete claims were written ($N_{\text{written}} = 0$), empirical reproduction $\hat{W}$ is unestimable, proving that retrieval failure alone halts transmission without requiring model-level safety filters.

2. **Causal Retrieval Rescue**:
   At $k=6$, the retriever recovered both required premises ($X_{\text{path}, G1} = 100.0\%$). Under the infected arm, all 4 G1 tasks derived the mutated alleles (`CLEARANCE_SIGMA`, `CLEARANCE_OMEGA`, `PROTO_Q2`, `PROTO_X7`) with 100% fidelity. In G2, when exposed to G1 parents in top-6 context, 100% of exposed tasks (6/6) successfully replicated the downstream lineage (`ROUTE_ORBITAL_SLIP`, `TIER_STANDARD`, `ROUTE_HYPERLANE`, `TIER_PRIORITY`, `AUDIT_WEEKLY`, `ACCESS_UNRESTRICTED`).

3. **G1 Clean Expression Asymmetry**:
   While $X_{\text{path}, G1} = 100\%$ across both arms at $k=6$, Clean G1 produced 2 abstentions on `security_clearance` tasks, while Infected G1 produced active derivations for all tasks. Detailed prompt inspection revealed that Clean G1 contexts included dynamic memory IDs from prior tasks and differing distractor slot compositions, highlighting the need for the matched path sufficiency test (Exp 1B-B1c).

---

## 4. Instrumentation & Persistence Audit

- **Foreign Key Integrity**: All 48 evaluations point directly to valid `node_id` foreign keys in `memory_nodes`.
- **Occurrence Accounting**: All 48 calls generated persistent memory records:
  - 16 active nodes ($\text{is\_active}=1, \text{reproductive\_status}=\text{"active"}$)
  - 32 inactive nodes ($\text{is\_active}=0, \text{reproductive\_status}=\text{"inactive"}$)
- **Run Lifecycle**: All 8 runs were marked `status="completed"` with UTC completion timestamps.
