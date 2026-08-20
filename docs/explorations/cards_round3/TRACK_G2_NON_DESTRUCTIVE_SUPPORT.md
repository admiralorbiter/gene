# Experiment Card — Track G2: Clean Non-Destructive Support Immunity

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** Support-aware governance filtering preserves valid multiply-supported knowledge while naive ancestry quarantine causes unnecessary epistemic loss (autoimmunity).
- **Confound Elimination & Systems Framing:**
  1. **Real Governance Policy Contexts:** The deterministic support engine constructs the retrieved prompt context dictated by the active policy (Naive Lineage vs Support-Aware Kernel).
  2. **Shared-Root Unrevoked Baseline:** Includes an explicit baseline control for shared-root syntax before revocation.
  3. **Zero Auxiliary Schema Leaks:** Output schema contains only target claim and status:
     `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}`.

## 2. Experimental Policy Conditions (4 Arms $\times$ 2 Stations $\times$ 2 Reps = 16 Calls)
1. **`baseline_independent`:** Both paths unrevoked $\to$ Full context $\to$ Target: `PROTO_X7`.
2. **`baseline_shared`:** Shared root unrevoked $\to$ Full context $\to$ Target: `PROTO_X7`.
3. **`naive_lineage_quarantine`:** $S_1$ revoked under naive lineage $\to$ Entire claim family quarantined $\to$ Target: `UNKNOWN`.
4. **`support_aware_independent_preservation`:** $S_1$ revoked under support-aware kernel $\to$ Path 1 pruned, Path 2 preserved and retrieved $\to$ Target: `PROTO_X7`.

## 3. Measurable Endpoints
- **Epistemic Autoimmunity Avoidance:** $P(C = \text{PROTO\_X7}\mid \text{support-aware}) = 1.0$ vs $0.0$ under naïve lineage.
- **Shared-Root Baseline Sanity:** $P(C = \text{PROTO\_X7}\mid \text{baseline\_shared}) = 1.0$.

## 4. Live Call Allocation
- 4 Conditions $\times$ 2 Stations $\times$ 2 Repetitions = **16 calls** on Gemma 3:12B.
- Budget ceiling: **16 calls**.
