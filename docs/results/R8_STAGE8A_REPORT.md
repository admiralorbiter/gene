# Exploration Round 8 Stage 8A Verification Report: Autonomous Open Ingress

- **Contract ID**: `CONTRACT-R8-8A`
- **Model**: `gemma3:12b` (`f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`)
- **Total Live Model Calls**: 115 (15 Pilot + 50 Open + 50 Menu-Assisted)
- **Evaluation Topology**: 50 Sealed Worlds ($N_{\text{gold}} = 100$ ground-truth mentions)
- **Status**: **PASS (All Falsification Criteria Cleanly Satisfied)**

## 1. Primary Estimands & Gate Outcomes

| Estimand / Metric | Pre-registered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Candidate Recall ($M_1$)** | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 (100.0\%)** | **PASS** |
| **Candidate Precision ($M_2$)** | $\ge 85.0\%$ | **100.0\%** | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $\ge 85.0\%$ | **100 / 100 (100.0\%)** | **PASS** |
| **Global False Discovery ($	ext{FDAR}_{\text{global}}$)** | $\equiv 0.0\%$ ($0 / N$) | **0 false admissions (0.0\%)** | **PASS** |
| **Paired Relative Drop vs Menu Control** | $\le 10.0\%$ | **0.0\%** | **PASS** |

## 2. Epistemic Proof-Carrying Validation
All candidate relations generated autonomously by `gemma3:12b` from raw narrative text without candidate menus were submitted to `IngressEngine`, maintaining zero false fact admissions in the bitemporal store.
