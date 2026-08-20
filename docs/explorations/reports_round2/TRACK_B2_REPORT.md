# Post-Review Result Report — Track B2: Monoculture Hardening

## 1. Executive Summary
- **Probe Status:** PROMISING — HARDEN
- **Total Calls Spent:** 16 (Gemma 3:12B)
- **Verified Empirical Finding:** When prompt steering is removed, document count is held invariant ($N=5$), and roots are opaque (`root_R1`..`root_R5`), Gemma **did not spontaneously discount a repeated majority merely because the prompt stated its reports shared a common source.**
- **Why the Initial Conclusion Was Overextended:**
  - The initial report claimed that language models act as "pure repetition vote counters."
  - The actual data show a strong asymmetry:
    - On $X$-majority ($3:2$ raw ratio in `concur_X` and `conflict_roots_Y`), Gemma emitted `UNKNOWN` across all $8/8$ calls ($P(X) = 0.000$).
    - On $Y$-majority ($3:2$ raw ratio in `concur_Y` and `conflict_roots_X`), Gemma emitted `PROTO_Y` in $6/8$ calls ($P(Y) = 0.750$).
  - This asymmetry indicates that adjudication was heavily influenced by un-counterbalanced token preferences (`PROTO_X` vs `PROTO_Y`) and **positional coupling** (majority documents occupied earlier positions).
- **Core Signal That Survives:** Comparing `concur_X` (3 independent roots) vs `conflict_roots_Y` (1 shared root) holding $3X:2Y$ constant, Gemma abstained in both ($4/4$ and $4/4$). Root-sharing had no detectable discounting effect.

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
| Rep 1 | KESTREL | `conflict_roots_X` | 2:3 (Y) | 2:1 (X) | `PROTO_Y` | 1 | 0 |
| Rep 2 | VELORA | `concur_X` | 3:2 (X) | 3:2 (X) | `UNKNOWN` | 0 | 0 |
| Rep 2 | VELORA | `conflict_roots_Y` | 3:2 (X) | 1:2 (Y) | `UNKNOWN` | 0 | 0 |
| Rep 2 | VELORA | `concur_Y` | 2:3 (Y) | 2:3 (Y) | `PROTO_Y` | 1 | 1 |
| Rep 2 | VELORA | `conflict_roots_X` | 2:3 (Y) | 2:1 (X) | `UNKNOWN` | 0 | 0 |
| Rep 2 | KESTREL | `concur_X` | 3:2 (X) | 3:2 (X) | `UNKNOWN` | 0 | 0 |
| Rep 2 | KESTREL | `conflict_roots_Y` | 3:2 (X) | 1:2 (Y) | `UNKNOWN` | 0 | 0 |
| Rep 2 | KESTREL | `concur_Y` | 2:3 (Y) | 2:3 (Y) | `PROTO_Y` | 1 | 1 |
| Rep 2 | KESTREL | `conflict_roots_X` | 2:3 (Y) | 2:1 (X) | `PROTO_Y` | 1 | 0 |

## 3. Revised Conclusion & Hardening Protocol
Track B2 shows that raw root metadata does not reliably cause spontaneous discounting of repeated majorities. However, to establish true ancestral blindness vs rational evidence integration, the next assay must:
1. Fully decouple document presentation order from majority assignment.
2. Rotate token identities across arbitrary non-semantic names (e.g. `PROTO_M4` vs `PROTO_Q7`).
3. Permute source IDs independently.
