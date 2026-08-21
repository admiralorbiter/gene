---
checkpoint_id: CHECKPOINT-R8-8B
contract_id: CONTRACT-R8-8B-R1
promotion_id: PROMOTION-CONTRACT-R8-8B-R1
timestamp: "2026-08-21 23:46:00Z"
base_sha: add7574737a88f43570d645a1a8e0dcae4b099d8
status: PROMOTED
authorized_by: human
---

# Checkpoint Record: CHECKPOINT-R8-8B (Multi-Document Stream Coreference & Occurrence Splitting)

## 1. Verified Scientific State
- **Contract Promoted**: `CONTRACT-R8-8B-R1`
- **Promotion Artifact**: [`research/promotions/PROMOTION-CONTRACT-R8-8B-R1.md`](../promotions/PROMOTION-CONTRACT-R8-8B-R1.md)
- **Verified Code Baseline**: `add7574737a88f43570d645a1a8e0dcae4b099d8`
- **Empirical Confirmation**:
  - In multi-document asynchronous telemetry streams, `gemma3:12b` successfully resolves coreferent entity mentions and hardware aliases against a pre-registered canonical entity registry ($60/60$ alias mentions resolved across Cells 2 and 4, $100\%$ precision on $200$ candidate mention slots).
  - Out-of-order contradictory telemetry is cleanly integrated via deterministic bitemporal occurrence splitting ($100/100$ 4-point bitemporal timeline queries satisfied with unique active state).
  - Zero false merges ($0/30$) across adversarial near-collision distractor controls; zero false splits ($0/60$); zero false durable admissions ($\text{FDAR} \equiv 0.0\%$).

## 2. Epistemic Architecture & Scope Ceilings
- **Established Architecture**: Neural model extracts uncertain raw entity spans and temporal intervals $\to$ hypothesis binding against canonical registry $\to$ proof-carrying admission policy $\to$ deterministic bitemporal supersession algebra $\to$ durable epistemic state.
- **Unresolved / Next Frontier**: Autonomous open-world ontology induction without pre-registered alias mappings, or higher-order multi-hop lineage reasoning under epistemic uncertainty.
