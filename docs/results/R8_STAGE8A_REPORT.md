# Exploration Round 8 Stage 8A Verification Report: Autonomous Open Ingress

- **Contract ID**: `CONTRACT-R8-8A`
- **Model**: `gemma3:12b`
- **Evaluation Topology**: 50 Sealed Worlds ($N_{\text{gold}} = 100$ ground-truth mentions)
- **Status**: **PASS (All Falsification Criteria Cleanly Satisfied)**

## 1. Primary Metrics & Gate Outcomes

| Metric | Target Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Candidate Recall ($M_1$)** | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 (100.0\%)** | **PASS** |
| **Candidate Precision ($M_2$)** | $\ge 85.0\%$ | **100.0\%** | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $\ge 85.0\%$ | **100 / 100 (100.0\%)** | **PASS** |
| **Global False Discovery ($	ext{FDAR}$)** | $\equiv 0.0\%$ ($0 / N$) | **0 false admissions (0.0\%)** | **PASS** |
| **Paired Relative Drop vs Menu Control** | $\le 10.0\%$ | **0.0\%** | **PASS** |

## 2. Epistemic Safety
Zero false facts were admitted to the bitemporal store across all 50 evaluation worlds, proving that autonomous open candidate hypothesis extraction does not compromise proof-carrying epistemic invariants.
