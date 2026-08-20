# Experiment Card — Track G2: Clean Non-Destructive Support Immunity

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** Support-aware governance filtering preserves valid multiply-supported knowledge while naive ancestry quarantine causes unnecessary epistemic loss (autoimmunity). Furthermore, the support-aware kernel correctly inactivates a claim when all supporting paths share a retracted root (safe collapse).
- **Executed Governance Engine:** The deterministic `apply_governance_retrieval()` engine evaluates the DAG, applies policy rules (Naive Lineage vs Support-Aware Kernel), and constructs the retrieved evidence set.
- **Zero Auxiliary Schema Leaks:** Output schema contains only target claim and status:
  `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}`.

## 2. Experimental Policy Conditions (5 Arms $\times$ 2 Stations $\times$ 2 Reps = 20 Calls)
1. **`baseline_independent`:** Both paths unrevoked $\to$ Full context $\to$ Formal: `PROTO_X7`.
2. **`baseline_shared`:** Shared root unrevoked $\to$ Full context $\to$ Formal: `PROTO_X7`.
3. **`naive_lineage_quarantine`:** $S_1$ revoked under naive lineage $\to$ Entire claim family quarantined $\to$ Formal: `UNKNOWN` (Autoimmunity).
4. **`support_aware_independent_preservation`:** $S_1$ revoked under support-aware kernel $\to$ Path 1 pruned, Path 2 preserved and retrieved $\to$ Formal: `PROTO_X7` (Preservation).
5. **`support_aware_shared_collapse`:** $S_1$ revoked under support-aware kernel on shared root $\to$ Both paths broken $\to$ Formal: `UNKNOWN` (Safe Collapse).

## 3. Measurable Endpoints
- **Epistemic Autoimmunity Avoidance:** $P(C = \text{PROTO\_X7}\mid \text{support-aware}) = 1.0$ vs $0.0$ under naïve lineage.
- **Safe Collapse Rate:** $P(C = \text{UNKNOWN}\mid \text{support\_aware\_shared\_collapse}) = 1.0$.
- **Shared-Root Baseline Sanity:** $P(C = \text{PROTO\_X7}\mid \text{baseline\_shared}) = 1.0$.

## 4. Live Call Allocation
- 5 Conditions $\times$ 2 Stations $\times$ 2 Repetitions = **20 calls** on Gemma 3:12B.
- Budget ceiling: **20 calls**.
