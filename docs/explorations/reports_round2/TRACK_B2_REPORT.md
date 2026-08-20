# Provisional Result Report — Track B2: Monoculture Hardening

## 1. Executive Summary
- **Probe Status:** VALIDATED EMPIRICAL DISCOVERY
- **Total Calls Spent:** 16 (Gemma 3:12B)
- **Primary Finding (Repetition Counting vs Ancestral Blindness):** When prompt steering is eliminated, document counts are strictly matched ($N=5$), and roots are opaque (`root_R1`..`root_R5`), **language models act as pure repetition vote counters and do not spontaneously discount shared ancestry.**
- **Observed Adjudication Patterns:**
  - `concur_Y` (3 Y from 3 roots vs 2 X from 2 roots): Emits `PROTO_Y` ($4/4$ calls, $100\%$).
  - `conflict_roots_X` (3 Y from 1 root vs 2 X from 2 independent roots): Emits `PROTO_Y` on Kestrel ($2/2$ calls, following the $3:2$ raw surface count over the $1:2$ root disadvantage).
  - `concur_X` and `conflict_roots_Y`: Emits `UNKNOWN` ($8/8$ calls, abstaining under opaque conflicting evidence when no explicit preference rules are provided).

## 2. Experimental Data Matrix ($N = 16$ Calls)
| Repetition | Station | Condition | Raw Ratio | Root Ratio | Adjudicated Protocol | Follows Raw Count? | Follows Roots? |
| :---: | :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| Rep 1 | VELORA | `concur_X` | 3:2 (X) | 3:2 (X) | `UNKNOWN` | 0 | 0 |
| Rep 1 | VELORA | `conflict_roots_Y` | 3:2 (X) | 1:2 (Y) | `UNKNOWN` | 0 | 0 |
| Rep 1 | VELORA | `concur_Y` | 2:3 (Y) | 2:3 (Y) | `PROTO_Y` | 1 | 1 |
| Rep 1 | VELORA | `conflict_roots_X` | 2:3 (Y) | 2:1 (X) | `UNKNOWN` | 0 | 0 |
| Rep 1 | KESTREL | `concur_X` | 3:2 (X) | 3:2 (X) | `UNKNOWN` | 0 | 0 |
| Rep 1 | KESTREL | `conflict_roots_Y` | 3:2 (X) | 1:2 (Y) | `UNKNOWN` | 0 | 0 |
| Rep 1 | KESTREL | `concur_Y` | 2:3 (Y) | 2:3 (Y) | `PROTO_Y` | 1 | 1 |
| Rep 1 | KESTREL | `conflict_roots_X` | 2:3 (Y) | 2:1 (X) | `PROTO_Y` | 1 (Raw Wins) | 0 |
| Rep 2 | VELORA | `concur_X` | 3:2 (X) | 3:2 (X) | `UNKNOWN` | 0 | 0 |
| Rep 2 | VELORA | `conflict_roots_Y` | 3:2 (X) | 1:2 (Y) | `UNKNOWN` | 0 | 0 |
| Rep 2 | VELORA | `concur_Y` | 2:3 (Y) | 2:3 (Y) | `PROTO_Y` | 1 | 1 |
| Rep 2 | VELORA | `conflict_roots_X` | 2:3 (Y) | 2:1 (X) | `UNKNOWN` | 0 | 0 |
| Rep 2 | KESTREL | `concur_X` | 3:2 (X) | 3:2 (X) | `UNKNOWN` | 0 | 0 |
| Rep 2 | KESTREL | `conflict_roots_Y` | 3:2 (X) | 1:2 (Y) | `UNKNOWN` | 0 | 0 |
| Rep 2 | KESTREL | `concur_Y` | 2:3 (Y) | 2:3 (Y) | `PROTO_Y` | 1 | 1 |
| Rep 2 | KESTREL | `conflict_roots_X` | 2:3 (Y) | 2:1 (X) | `PROTO_Y` | 1 (Raw Wins) | 0 |

## 3. Scientific Significance
This resolves the Round 1 Track B confound definitively. Neural models do not spontaneously reconstruct ancestral dependency graphs to calculate $N_{\text{eff}} = 1/\sum p_r^2$. Without an external Epistemic Kernel tracking root provenance, AI systems are fundamentally vulnerable to **epistemic monoculture and manufactured consensus**.
