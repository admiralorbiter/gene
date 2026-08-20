# Experiment Card — Track A: Recovery & Epistemic Hysteresis

## QUESTION
Can an established false lineage actually be corrected without simply destroying everything descended from the old belief, and what is the cost-selectivity tradeoff between root overwrite, lineage repair, and revalidate-on-use?

## PRIMARY MANIPULATION
Introduce a corrective update event at the root ($G_0$: $\text{TAL} \leadsto \text{KIRA}$) after an infected descendant tree ($G_1, G_2$) has already been generated and persisted. Compare 5 governance policies:
1. `root_overwrite`: Update root to Kira; leave existing Tal descendants active in memory.
2. `latest_root_preference`: Both root nodes remain; retrieval score prioritizes the newest root.
3. `lineage_quarantine`: Invalidate/quarantine the entire Tal family branch.
4. `lineage_repair`: Invalidate Tal descendants and immediately rederive/recompute Kira descendants.
5. `revalidate_on_use`: Stale descendants remain until retrieved; when retrieved, require ancestry re-verification before reproduction.

## FROZEN CONTROLS
- 2-premise first-order Horn clause rules ($G_1$ protocol, $G_2$ route).
- Structured JSON prompt contract with `UNKNOWN` reject option.
- Role-swapped counterbalanced micro-worlds (Velora vs Kestrel).
- Fixed decoding ($T=0.0$, seed=42).

## PRIMARY ENDPOINTS
- $H_g = P(\text{superseded lineage accessible } g \text{ steps after correction})$ (Hysteresis rate)
- $C_{\text{repair}} = P(\text{correct descendant available after correction})$ (Repair coverage)
- $K_{\text{repair}} = \mathbb{E}[\text{nodes recomputed / revalidated per correction}]$ (Computational cost)

## FALSIFIER
If simply overwriting the root causes downstream reasoners to cleanly abandon old descendants without confusion ($H_g = 0$ under root overwrite), hysteresis is trivial in this ecology and complex revalidation is unnecessary.

## ZERO-COMPUTE GATE
Symbolic state machine must deterministically simulate all 5 policies, verify node staleness flags, and calculate exact $H_g, C_{\text{repair}}, K_{\text{repair}}$ under synthetic retrieval queues before any model call.

## LIVE CALL CEILING
16 calls (2 role-swapped worlds × 4 policy states × 2 queries: clean/infected). Hard maximum: 24 calls.

## STOP RULE
Stop immediately after the single 16-call matched panel on `gemma3:12b`. Do not build a general temporal memory engine.

## STATUS
PROVISIONAL — EXPLORATORY ROUND 1
