# Experiment Card — Track L: Independence Laundering & Epistemic Observability

## 1. Core Hypothesis & Epistemic Observability
- **Core Hypothesis:** As an ancestral observation reproduces through successive downstream generations (paraphrasing, partial citing, metadata stripping), downstream models may either exhibit **epistemic overconfidence** (perceiving 4 separate documents as 4 independent primary sources: $\widehat{N}_{\text{model}} \leadsto 4$) or **epistemic resistance** (correctly recognizing that provenance is missing and independence is indeterminable).
- **Reject-Option & Non-Forced Schema:** Rather than forcing an integer output, the interface allows the model to state whether independence is determinable:
  `{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "independence_status": "determinable|indeterminable", "estimated_independent_sources": "INTEGER_OR_NULL", "evidence_status": "sufficient|insufficient"}`.

## 2. Experimental Transformation Cascade & 4-Root Positive Control
We evaluate 5 discrete conditions:
1. **$G_0$ True Root:** 1 doc authored by `root_R1` ($N_{\text{true}} = 1$, expected: determinable, $N=1$).
2. **$G_1$ Cited Paraphrases:** 4 docs all explicitly citing `root_R1` ($N_{\text{true}} = 1$, expected: determinable, $N=1$).
3. **$G_2$ Partial Laundering:** 4 docs (2 cite `root_R1`, 2 reference ambient archive).
4. **$G_3$ Laundered Consensus:** 4 docs with provenance completely stripped ($N_{\text{true}} = 1$, measured outcome: determinable vs indeterminable).
5. **$G_{\text{ctrl}}$ True 4-Root Control:** 4 docs from 4 explicitly independent roots `root_R1`..`root_R4` ($N_{\text{true}} = 4$, expected: determinable, $N=4$).

## 3. Measurable Endpoints & Analysis
- **Determinability Rate ($P(\text{determinable})$):** Probability that the model classifies independence as determinable across reproduction stages.
- **Conditional Perceived Independence ($\widehat{N}_{\text{model}}\mid \text{determinable}$):** Perceived root count when declared determinable.
- **4-Root Control Sanity:** Verification that the model accurately reports 4 sources under $G_{\text{ctrl}}$.

## 4. Live Call Allocation
- 5 Stages $\times$ 2 Stations $\times$ 2 Target Protocols = **20 calls** on Gemma 3:12B.
- Budget ceiling: **20 calls**.
