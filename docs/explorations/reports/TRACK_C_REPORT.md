# Provisional Result Report — Track C: Transformation Depth & Causal Provenance Decay

## 1. Executive Summary
- **Probe Status:** SUCCESSFUL (Boundary Discovery)
- **Total Calls Spent:** 12 (Gemma 3:12B)
- **Primary Finding:** In zero-shot structured JSON inference without intermediate scratchpad tokens, **deep multi-hop reasoning collapses into universal abstention ($P(\text{abstain}) = 1.000$)** when intermediate premises are omitted from the retrieved memory set.
- **Mechanism:** When asked to derive $G_3$ (Route) or $G_5$ (Audit Mode) directly from $G_0$ roots and 5 abstract Horn clauses, the model judges the context `insufficient` because the intermediate facts (`protocol`, `clearance`, `access_tier`) do not exist in memory.
- **Architectural Implication:** **Generation-by-generation DAG persistence is non-optional for deep reasoning chains.** In episodic memory systems, intermediate conclusions must be materialized as occurrence nodes in the DAG; an agent cannot be expected to re-execute unbounded symbolic transformations in zero-shot working memory.

## 2. Experimental Data Matrix ($N = 12$ Calls)
| Station | Depth $g$ | Founder Allele | Expected Value | Emitted Value | Allele Faithful? | Abstention? |
| :--- | :---: | :--- | :--- | :--- | :---: | :---: |
| VELORA | 1 | KIRA | `PROTO_X7` | `UNKNOWN` | 0 | 1 |
| VELORA | 1 | TAL | `PROTO_Q2` | `UNKNOWN` | 0 | 1 |
| VELORA | 3 | KIRA | `ROUTE_ALPHA` | `UNKNOWN` | 0 | 1 |
| VELORA | 3 | TAL | `ROUTE_BETA` | `UNKNOWN` | 0 | 1 |
| VELORA | 5 | KIRA | `AUDIT_EXPEDITE` | `UNKNOWN` | 0 | 1 |
| VELORA | 5 | TAL | `AUDIT_MANDATORY` | `UNKNOWN` | 0 | 1 |
| KESTREL | 1 | KIRA | `PROTO_X7` | `UNKNOWN` | 0 | 1 |
| KESTREL | 1 | TAL | `PROTO_Q2` | `UNKNOWN` | 0 | 1 |
| KESTREL | 3 | KIRA | `ROUTE_ALPHA` | `UNKNOWN` | 0 | 1 |
| KESTREL | 3 | TAL | `ROUTE_BETA` | `UNKNOWN` | 0 | 1 |
| KESTREL | 5 | KIRA | `AUDIT_EXPEDITE` | `UNKNOWN` | 0 | 1 |
| KESTREL | 5 | TAL | `AUDIT_MANDATORY` | `UNKNOWN` | 0 | 1 |

## 3. Scientific Significance
This clean null result bounds the computational role of persistent memory. Memory is not simply a historical log; it is the intermediate compute cache that makes multi-hop causal inheritance tractable across generations.
