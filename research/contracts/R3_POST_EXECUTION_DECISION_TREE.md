# Stage 8C-R3 Post-Execution Interpretation & Decision Tree

> **Classification**: `PRE-EXECUTION PREREGISTRATION`  
> **Target Contract**: `CONTRACT-R8-8C-R3`  
> **Status**: Frozen Predeclaration (Specified Prior to Clean Benchmark Execution)  
> **Objective**: Eliminate post-hoc rationalization by establishing the deterministic interpretation matrix for all possible Stage 8C-R3 empirical outcomes.

---

## 1. Deterministic Decision Tree

```mermaid
graph TD
    START["Stage 8C-R3 Execution Completed"] --> CHECK_SAFETY{"Safety Gates Check:<br/>- Gate 2a == 0 false canonical<br/>- Gate 2b == 0 false prov unasserted<br/>- Gate 3 == 0 prov duplicates"}
    
    CHECK_SAFETY -->|ANY FAIL| FAIL_SAFETY["DISPOSITION: REJECTED<br/>- Core epistemic safety broken<br/>- Critical fail-closed boundary breached"]
    
    CHECK_SAFETY -->|ALL PASS| CHECK_COV{"Gate 6 Coverage Check:<br/>Resolvable Coverage >= 85.0%<br/>(N=97 resolvable denominator)"}
    
    CHECK_COV -->|FAIL (< 85%)| FAIL_COV["DISPOSITION: REVISED_CONTRACT_REQUIRED<br/>- Safe but over-conservative admission failure<br/>- Characterize refusal: Rule 2 regex vs Rule 3 parenthetical"]
    
    CHECK_COV -->|PASS (>= 85%)| CHECK_LIFE{"Gate 5 & Gate 7 Lifecycle Check:<br/>- Gate 5: Exact 7/7 Arm 4B transitions<br/>- Gate 7: Strict 8 Unresolved + 7 Resolved == 15 Total"}
    
    CHECK_LIFE -->|FAIL (< 7/7)| DIAG_LIFE["DISPOSITION: REVISED_CONTRACT_REQUIRED / FIX<br/>- Dissect Telemetry vs Kernel:<br/>  (A) Neural Proposal Defect (Gemma failed candidate)<br/>  (B) Kernel State Machine Defect (Transition logic error)"]
    
    CHECK_LIFE -->|PASS (7/7 & 15/15)| PROMOTE["DISPOSITION: PROMOTION (CANDIDATE -> PROMOTED)<br/>- Ingress Kernel formally canonized<br/>- Stage 8 concluded; proceed to Stage 9 Horizon"]
```

---

## 2. Quantitative Comparative Replay Attribution ($R3$ vs $R2$)

The verification suite automatically runs the frozen Stage 8C-R2 deterministic resolver against the identical documents and proposals. The empirical delta $\Delta = \text{Coverage}_{R3} - \text{Coverage}_{R2}$ will be interpreted as follows:

| Replay Delta ($\Delta$) | Empirical Interpretation | Epistemic Significance |
| :--- | :--- | :--- |
| **$\Delta \le 0.0\%$** | Precedence policy refinement added no useful admission capacity. | Reversion to simpler R2 policy recommended; sub-ID grammar unnecessary. |
| **$0.0\% < \Delta < 15.0\%$** | Marginal improvement on edge cases. | Modest policy benefit; assess grammar complexity tradeoff. |
| **$\Delta \ge 15.0\%$** | Substantial recovery of resolvable hardware mentions previously blocked by universal first refusal. | Validates the architectural necessity of discriminating sub-identifiers and explicit parenthetical evidence. |

---

## 3. Epistemic Protocol Commitment

1. If any safety gate fails, no post-hoc excuse of "prompt nuance" or "ambiguous phrasing" will be accepted; the contract must fail closed.
2. If Gate 5 fails, the root cause must be separated into **neural calibration variance** vs **deterministic kernel logic** with raw JSON telemetry evidence.
3. Upon promotion, all synthetic naming grammar benchmarking ($R4, R5 \dots$) is permanently closed, and GENE transitions to Stage 9.
