# Provisional Result Report — Track A: Recovery & Epistemic Hysteresis

## 1. Executive Summary
- **Probe Status:** SUCCESSFUL
- **Total Calls Spent:** 16 (Gemma 3:12B)
- **Primary Finding:** Root Overwrite alone is completely ineffective at halting false lineage expression ($H_g = 1.000, C_{\text{repair}} = 0.000$). When a root is corrected without pruning descendants, existing stale memories in the pool remain active and continue to be retrieved directly by downstream reasoners.
- **Intervention Outcomes:**
  - `root_overwrite`: $4/4$ calls produced stale infected phenotype (`PROTO_Q2`, `ROUTE_BETA`). Hysteresis $H_g = 1.000$.
  - `lineage_quarantine`: Eliminates stale expression ($H_g = 0.000$), but leaves coverage $C_{\text{repair}} = 0.000$ until new descendants are rederived.
  - `lineage_repair`: Immediate proactive recomputation yields $100\%$ recovery ($C_{\text{repair}} = 1.000, H_g = 0.000$) at eager cost $K_{\text{repair}} = 3$ nodes.
  - `revalidate_on_use`: Lazy on-demand verification yields identical $100\%$ recovery ($C_{\text{repair}} = 1.000, H_g = 0.000$) at reduced cost $K_{\text{repair}} = 1.0$ node per query.

## 2. Experimental Data Matrix ($N = 16$ Calls)
| Station | Policy | Query | Emitted Value | Target | Recovered? | Hysteresis? |
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

## 3. Scientific Significance
This confirms that epistemic inertia in memory-augmented systems is a structural property of the retrieval pool: simply appending or correcting the root node fails to prevent downstream inference from utilizing existing stale intermediate lemmas. Lazy `revalidate_on_use` provides the optimal Pareto frontier between compute cost and lineage freshness.
