# Post-Review Result Report — Track A2: Dynamic Memory Repair & Lazy Revalidation

## 1. Executive Summary
- **Probe Status:** PROMISING MECHANISM — HARDEN
- **Total Calls Spent:** 12 (Gemma 3:12B)
- **Verified Empirical Finding (Stale-Descendant Survival):** When a root premise changes in active SQLite storage ($G_0: \text{TAL} \leadsto \text{KIRA}$), leaving stale descendants active causes the reasoner to continue emitting the obsolete phenotype in $4/4$ tested queries ($H_{\text{stale}} = 1.000$).
- **Verified Read-Time Rederivation:** When dirty descendant records are excluded at retrieval time and the fresh root is supplied, Gemma rederives the clean answer in $4/4$ queries ($C_{\text{clean}} = 1.000, H_{\text{stale}} = 0.000$).
- **Audit Corrections & Implementation Limits:**
  1. **Eager Repair Was Not Executed via LLM:** In `update_eager_repair()`, the script wrote the expected strings (`PROTO_X7`, `ROUTE_ALPHA`) directly to SQLite without invoking `client.chat()`. The earlier report's claim of "Immediate LLM Calls: 2" was factually incorrect.
  2. **Lazy Revalidation Was Read-Time Filtering, Not Memory Repair:** The lazy policy marked records dirty and excluded them from query prompts. It did not evaluate minimal support sets, rewrite dirty rows in the database, clear dirty flags, or measure amortized costs over repeated queries.
  3. **Overclaims Struck:** Claims of "unassailable experimental proof", "Pareto dominance", and "zero total cost" are removed.

## 2. Experimental Data Matrix ($N = 12$ Calls)
| Station | Policy Condition | Query Locus | Emitted Value | Target | Recovered? | Stale? |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| VELORA | `root_overwrite` | Protocol | `PROTO_Q2` | `PROTO_X7` | 0 | 1 |
| VELORA | `root_overwrite` | Route | `ROUTE_BETA` | `ROUTE_ALPHA` | 0 | 1 |
| VELORA | `eager_repair` (direct write)| Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| VELORA | `eager_repair` (direct write)| Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |
| VELORA | `lazy_revalidation` (filter)| Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| VELORA | `lazy_revalidation` (filter)| Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |
| KESTREL | `root_overwrite` | Protocol | `PROTO_Q2` | `PROTO_X7` | 0 | 1 |
| KESTREL | `root_overwrite` | Route | `ROUTE_BETA` | `ROUTE_ALPHA` | 0 | 1 |
| KESTREL | `eager_repair` (direct write)| Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| KESTREL | `eager_repair` (direct write)| Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |
| KESTREL | `lazy_revalidation` (filter)| Protocol | `PROTO_X7` | `PROTO_X7` | 1 | 0 |
| KESTREL | `lazy_revalidation` (filter)| Route | `ROUTE_ALPHA` | `ROUTE_ALPHA` | 1 | 0 |

## 3. Revised Conclusion & Hardening Roadmap
Stale descendants survive root correction and continue driving downstream inference. Filtering dirty records and supplying fresh root context allows read-time behavioral rederivation. 

However, genuine support-aware dynamic repair (evaluating whether a dirty node still possesses alternative valid support sets in $S(c)$, recomputing only when all paths fail, and persisting refreshed state) remains to be implemented and measured.
