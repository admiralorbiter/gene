# Experiment Card — Track G2: Clean Non-Destructive Lineage Immunity

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** A support-aware governance kernel successfully preserves claims with surviving alternative support paths ($AB + DE \to C$ after $A \leadsto 0$), while correctly inactivating claims whose apparent paths share a single corrupted root ($AX + AY \to C$ after $A \leadsto 0$).
- **Confound Elimination from Round 2:**
  1. **Zero Auxiliary Schema Leaks:** Output schema contains only target claim and status:
     `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}`.
     No `surviving_paths_count` or numeric counts in prompt schemas.
  2. **Un-Manipulated Positive Baseline Control:** Includes an explicit un-revoked baseline condition where both $S_1$ and $S_2$ are valid.
  3. **Strict Machine-Diff Audit:** Prompts differ strictly in the presence/absence of revocation clauses.

## 2. Experimental Design Matrix (3 Arms $\times$ 2 Geometries)
```
┌─────────────────────────┬──────────────────────────┬─────────────────────────┬─────────────────────────┐
│ Geometry                │ Arm 1: Unrevoked Baseline│ Arm 2: Revoke Path 1 (A)│ Arm 3: Revoke Shared (A)│
├─────────────────────────┼──────────────────────────┼─────────────────────────┼─────────────────────────┤
│ G2-Indep (AB + DE -> C) │ Valid (Both AB & DE)     │ Valid (Surviving DE)    │ N/A (Independent roots) │
│ G2-Shared (AX + AY -> C)│ Valid (Both AX & AY)     │ N/A (Shared root)       │ Inactivated (0 survive) │
└─────────────────────────┴──────────────────────────┴─────────────────────────┴─────────────────────────┘
```

## 3. Governance Policy Comparison
1. **Naïve Lineage Policy:** Flag any claim descending from $A$ as contaminated $\implies C \to \text{DEAD}$ in both geometries (severe epistemic autoimmunity on $AB+DE$).
2. **Support-Aware Policy:** Invalidate support set $\{A,B\}$; preserve $C$ if alternative set $\{D,E\}$ remains valid $\implies C \to \text{ALIVE}$ on $AB+DE$, $C \to \text{DEAD}$ on $AX+AY$.

## 4. Measurable Endpoints
- **Epistemic Autoimmunity Avoidance:** $P(C \text{ active}\mid AB+DE, A=0) = 1.0$ under support-aware kernel vs $0.0$ under naïve lineage.
- **Containment Fidelity:** $P(C \text{ active}\mid AX+AY, A=0) = 0.0$.
- **Positive Control Derivability:** $P(C \text{ active}\mid \text{baseline}) = 1.0$.

## 5. Live Call Allocation
- 2 Stations $\times$ 3 Arms $\times$ 3 Repetitions = 18 calls on Gemma 3:12B.
- Budget ceiling: **18 calls**.
