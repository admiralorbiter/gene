# Stage 8C-R3 Post-Execution Interpretation & Decision Tree

> **Classification**: `PRE-EXECUTION PREREGISTRATION`  
> **Target Contract**: `CONTRACT-R8-8C-R3`  
> **Status**: Frozen Predeclaration (Specified Prior to Clean Benchmark Execution)  
> **Objective**: Eliminate post-hoc rationalization by establishing the deterministic interpretation matrix and paired discordance criteria for all possible Stage 8C-R3 empirical outcomes.

---

## 1. Deterministic Decision Tree & Governance Boundary

```mermaid
graph TD
    START["Stage 8C-R3 Execution Completed"] --> CHECK_SAFETY{"Safety Gates Check:<br/>- Gate 2a == 0 false canonical<br/>- Gate 2b == 0 false prov unasserted<br/>- Gate 3 == 0 prov duplicates"}
    
    CHECK_SAFETY -->|ANY FAIL| FAIL_SAFETY["DISPOSITION: REJECTED<br/>- Core epistemic safety broken<br/>- Critical fail-closed boundary breached"]
    
    CHECK_SAFETY -->|ALL PASS| CHECK_COV{"Gate 6 Coverage Check:<br/>Resolvable Coverage >= 85.0%<br/>(N=97 resolvable denominator)"}
    
    CHECK_COV -->|FAIL (< 85%)| FAIL_COV["DISPOSITION: REVISED_CONTRACT_REQUIRED<br/>- Safe but over-conservative admission failure<br/>- Characterize refusal: Rule 2 regex vs Rule 3 parenthetical"]
    
    CHECK_COV -->|PASS (>= 85%)| CHECK_LIFE{"Gate 5 & Gate 7 Lifecycle Check:<br/>- Gate 5: Exact 7/7 Arm 4B transitions<br/>- Gate 7: Strict 8 Unresolved + 7 Resolved == 15 Total"}
    
    CHECK_LIFE -->|FAIL (< 7/7)| DIAG_LIFE["DISPOSITION: REVISED_CONTRACT_REQUIRED / FIX<br/>- Dissect Telemetry vs Kernel:<br/>  (A) Neural Proposal Defect (Gemma failed candidate)<br/>  (B) Kernel State Machine Defect (Transition logic error)"]
    
    CHECK_LIFE -->|PASS (7/7 & 15/15)| CANDIDATE["DISPOSITION: PROMOTION_CANDIDATE<br/>(SEAL CANDIDATE ARTIFACT)"]
    
    CANDIDATE --> REVIEW["Scientific Promotion Review Desk (ChatGPT Pro)"]
    REVIEW -->|APPROVED| AUTH["Human Strategic Promotion Authorization"]
    AUTH -->|AUTHORIZED| PROMOTED["FINAL STATUS: PROMOTED<br/>- Ingress Kernel formally canonized<br/>- Stage 8 concluded; proceed to Stage 9 Horizon"]
```

---

## 2. Quantitative Comparative Replay Attribution ($R3$ vs $R2$)

The verification suite automatically runs the frozen Stage 8C-R2 deterministic resolver against the identical documents and proposals.

### A. Paired Discordance Matrix ($2 \times 2$)
To evaluate the true nature of policy changes rather than relying solely on net aggregate coverage delta ($\Delta$), the verifier computes the exact paired discordance:

$$\begin{array}{c|c|c}
& \text{R3 Correct} & \text{R3 Incorrect} \\
\hline
\text{R2 Correct} & n_{11} \text{ (Concordant Correct)} & n_{10} \text{ (R2 Right, R3 Wrong / Regressions)} \\
\hline
\text{R2 Incorrect} & n_{01} \text{ (R2 Wrong, R3 Right / Recovered)} & n_{00} \text{ (Concordant Incorrect)}
\end{array}$$

$$\Delta = \text{Coverage}_{R3} - \text{Coverage}_{R2} = \frac{n_{01} - n_{10}}{N_{\text{resolvable}}} \times 100\%$$

### B. Pre-Registered Attribution Tiers

| Observed Metric Profile | Empirical Interpretation | Epistemic Significance |
| :--- | :--- | :--- |
| **$n_{01} > 0$ and $n_{10} == 0$** | Pure Pareto improvement. Refined precedence cleanly recovers previously blocked cases without regressions. | Strong evidence that discriminating sub-identifiers and parenthetical evidence improve this benchmark. |
| **$n_{01} > n_{10} > 0$ ($\Delta > 0$)** | Net positive coverage gain with isolated regressions. | Analyze $n_{10}$ failure cases; determine whether regressions stem from grammar edge cases or prompt ambiguity. |
| **$\Delta \le 0.0\%$ ($n_{01} \le n_{10}$)** | Net coverage flat or negative. | Precedence policy refinement failed to improve net admission; inspect discordance breakdown across benchmark arms before considering policy reversion. |

---

## 3. Epistemic Protocol Commitment

1. **No Autonomous Auto-Promotion**: A passing run transitions the project to `PROMOTION_CANDIDATE`. Formal promotion requires Review Desk approval and explicit Human Strategic Authorization.
2. **Deterministic Safety Enforcement**: If any safety gate fails, no post-hoc excuse will be accepted; the contract must fail closed.
3. **Horizon Closure**: Upon promotion, all synthetic naming grammar benchmarking ($R4, R5 \dots$) is permanently closed, and GENE transitions to Stage 9.
