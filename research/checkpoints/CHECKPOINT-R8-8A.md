---
checkpoint_id: CHECKPOINT-R8-8A
contract_id: CONTRACT-R8-8A
status: PROMOTED
promoted_sha: c7c9ef641393adf6687f9ce05eda0b8776e2e32d
created_at: "2026-08-21 22:16:00Z"
---

# Research Checkpoint: Stage 8A Autonomous Open Ingress (Promoted)

## 1. Verified Scientific State
- **Hypothesis Confirmed**: Removing explicit candidate menus does not degrade relation candidate generation or downstream safe bitemporal admission for `gemma3:12b` on synthetic single-document telemetry.
- **Empirical Baseline**:
  - 115 live model invocations, 0 fallbacks
  - Recall ($M_1$): $100\%$ ($100/100$)
  - Precision ($M_2$): $100\%$
  - Useful Admission Coverage ($M_3$): $100\%$ ($100/100$)
  - Global False Discovery ($\text{FDAR}$): $0\%$
  - Downstream Probes Q1..Q4: $100\%$ passed
- **Next Frontier**: Stage 8B — Multi-Document Entity Resolution and Cross-Document Temporal Fusion under Ambiguity.
