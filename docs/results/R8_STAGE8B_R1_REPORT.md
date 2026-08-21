# Exploration Round 8 Stage 8B-R1 Confirmatory Verification Report

- **Contract ID**: `CONTRACT-R8-8B-R1`
- **Model**: `gemma3:12b` (`f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`)
- **Total Live Invocations**: 145 (15 Pilot + 100 Multi-Doc Confirmatory Evaluation + 30 Near-Collision Controls)
- **Multi-Document Streams**: 50 Fresh Sealed Worlds $\times$ 2 Documents = 100 Document Packets
  - Cell 1 (Literal x In-Order): 10 Worlds (20 Documents)
  - Cell 2 (Alias x In-Order): 15 Worlds (30 Documents, 30 Gold Alias Mentions)
  - Cell 3 (Literal x Out-of-Order): 10 Worlds (20 Documents, Occurrence-Splitting Supersession)
  - Cell 4 (Alias x Out-of-Order): 15 Worlds (30 Documents, 30 Gold Alias Mentions, Occurrence-Splitting Supersession)
- **Status**: **PASS (All Confirmatory Criteria Satisfied)**

## 1. Confirmatory Estimands & Factorial Gate Outcomes

| Estimand / Metric | Exact Denominator | Pre-registered Floor | Observed Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Coreference Recall ($M_{1\text{coref}}$)** | $N = 60$ alias mentions (Cells 2 & 4) | $\ge 85.0\%$ ($51 / 60$) | **60 / 60 mentions (100.0\%)** | **PASS** |
| **Candidate Precision ($M_2$)** | Total proposed candidates | $\ge 85.0\%$ | **100.0\%** against canonical targets | **PASS** |
| **False Merge Rate** | $N = 30$ distractor trials | $\equiv 0.0\%$ ($0 / 30$) | **0 false merges (0.0\%)** | **PASS** |
| **False Split Rate** | $N = 60$ coreference mentions | $\le 5.0\%$ | **0 false splits (0.0\%)** | **PASS** |
| **Temporal Correctness (Out-of-Order)** | $N = 100$ 4-point queries (Cells 3 & 4) | $\ge 90.0\%$ ($90 / 100$) | **100 / 100 (100.0\%)** | **PASS** |
| **Useful Admission Coverage ($M_3$)** | $N = 200$ total gold mentions | $\ge 80.0\%$ ($160 / 200$) | **200 / 200 (100.0\%)** | **PASS** |
| **Global False Discovery ($	ext{FDAR}_{\text{global}}$)** | Total durable admissions | $\equiv 0.0\%$ ($0 / N$) | **0 false durable admissions (0.0\%)** | **PASS** |
| **Downstream Probes Q1..Q4** | $N = 4 \times N_{\text{admitted}}$ (400 queries) | $\equiv 100.0\%$ | **400 / 400 (100.0\% passed)** | **PASS** |
