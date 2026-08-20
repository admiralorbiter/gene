# Post-Review Result Report — Track A: Recovery & Epistemic Hysteresis

## 1. Executive Summary
- **Probe Status:** PROMISING — HARDEN
- **Total Calls Spent:** 16 (Gemma 3:12B)
- **Verified Empirical Finding (Stale-Descendant Hysteresis):** Root Overwrite alone is completely ineffective at halting false lineage expression when stale descendants remain active in the retrieved context ($H_g = 1.000$). When a root is updated ($G_0: \text{TAL} \leadsto \text{KIRA}$) but the stale intermediate lemma (`PROTO_Q2`) is simultaneously presented in retrieved memory, the model continues to cite the stale descendant and emit the obsolete phenotype across all 4 station × query cases ($4/4 = 100\%$).
- **Assay Limitations & Unmeasured Claims:**
  - The live runner evaluated 4 prompt configurations rather than an active memory-management engine: the runner prepared the repaired/revalidated contexts beforehand and passed them to the model.
  - The relative computational costs ($K_{\text{repair}} = 3$ eager vs $K_{\text{lazy}} = 1$ lazy) were assigned by the deterministic simulation model, not empirically measured via token counts, compute time, or cache eviction profiles.
  - `latest_root_preference` was simulated deterministically but omitted from the live 16-call allocation.
- **Key Emergent Observation (Read-Time Rederivation):** Under `lineage_quarantine` (where the stale $G_1$ protocol was removed from memory, leaving only the fresh $G_0$ Kira root and the Horn rules), Gemma successfully rederived the canonical protocol (`PROTO_X7`) and route (`ROUTE_ALPHA`) in all 4 calls. Deleting stale descendants does not destroy behavioral coverage when surviving upstream ancestry is sufficient for the reasoner to regenerate the conclusion at read time.

## 2. Experimental Data Matrix ($N = 16$ Calls)
| Station | Policy Condition | Query | Emitted Value | Target | Recovered? | Stale Hysteresis? |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| VELORA | root_overwrite | Protocol | `PROTO_Q2` | `PROTO_X7` | 0 | 1 |
| VELORA | root_overwrite | Route | `ROUTE_BETA` | `ROUTE_ALPHA` | 0 | 1 |
| VELORA | lineage_repair | Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| VELORA | lineage_repair | Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |
| VELORA | lineage_quarantine | Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| VELORA | lineage_quarantine | Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |
| VELORA | revalidate_on_use | Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| VELORA | revalidate_on_use | Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |
| KESTREL | root_overwrite | Protocol | `PROTO_Q2` | `PROTO_X7` | 0 | 1 |
| KESTREL | root_overwrite | Route | `ROUTE_BETA` | `ROUTE_ALPHA` | 0 | 1 |
| KESTREL | lineage_repair | Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| KESTREL | lineage_repair | Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |
| KESTREL | lineage_quarantine | Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| KESTREL | lineage_quarantine | Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |
| KESTREL | revalidate_on_use | Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| KESTREL | revalidate_on_use | Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |

## 3. Revised Conclusion & Next Steps
Root correction alone does not neutralize directly retrievable stale descendants in tested contexts. Removing or replacing stale descendants restored clean behavior. The relative compute advantage of lazy revalidation versus eager repair remains an unmeasured theoretical proposition that requires active execution harness measurement in Phase 11.
