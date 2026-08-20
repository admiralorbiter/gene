# Experiment 1B-B Final Report — Endogenous Multi-Hop Retrieval & Lineage Surface-Area Dynamics

**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Experiment:** Experiment 1B-B (Endogenous Multi-Hop Retrieval Dynamics & Lineage Surface-Area Scaling)  
**Status:** **PILOT VALIDATED — INSTRUMENT GREEN-LIT**  
**Date:** 2026-08-20  
**Model Under Test:** `gemma3:12b` (Ollama, dynamic digest captured)  
**Assay Environment:** Ecology C (Competing rules) + Schema v2 (Explicit contract) + Okapi BM25 Scored Top-$k$ Retriever  
**Databases:**
- `gene_exp1b_b1_20260820_041254.db` (Live $k=6$ rescue replication: 12 calls, 12 evaluations, 158 candidate retrieval events, 27 memory nodes)
- `gene_exp1b_b1_20260820_035302.db` (Live $k=4$ baseline pilot: 12 calls, 144 candidate retrieval events)
- `gene_exp1b_b2_20260820_040910.db` (Controlled surface-area scaling: 4 worlds, 5 parametric sweep points in `surface_feedback_sweeps`)

---

## 1. Executive Summary

Experiment 1B-B transitions GENE from exogenous exposure schedules ($X = 2p$) to **endogenous retrieval dynamics**, where contact is not assigned by an experimental mask but emerges dynamically from competition over a candidate memory pool containing:
1. Ground-truth source memories ($G_0$).
2. Easy clutter distractors (unrelated facilities and predicates).
3. Hard negative distractors (same target station and natural overlapping vocabulary, but non-derivable relations with zero target answer leakage).
4. Replicating lineage descendants ($G_1, G_2$).

To prevent confounding multi-hop lexical similarity differences with evolutionary lineage growth, Experiment 1B-B is divided into two focused sub-assays:

- **Experiment 1B-B1 (Endogenous Multi-Hop Retrieval & Causal Rescue Assay)**:
  Measures multi-hop evidence chain assembly under lexical competition:
  $$X_F = P(\text{founder retrieved in top-}k)$$
  $$X_A = P(\text{co-support premise retrieved in top-}k)$$
  $$X_{\text{path}} = P(\text{complete proof path retrieved in top-}k)$$
  Evaluates how same-entity hard negatives displace bridge facts, validates model reject-option behavior under partial retrieval ($D_{\text{ctx}} = 0$), and experimentally demonstrates **causal retrieval rescue** by expanding the retrieval budget from $k=4 \to k=6$.

- **Experiment 1B-B2 (Controlled Lineage Surface-Area Scaling Assay)**:
  Holds the target query and required founder premise strictly fixed while parametrically scaling lineage descendants in memory ($N_{\text{lineage}} \in \{0, 1, 2, 4, 8\}$). Demonstrates that lineage multiplicity monotonically expands top-$k$ context visibility.

---

## 2. Key Empirical Findings

### 2.1 The Multi-Hop Evidence Chain Assembly ($X_F$ vs. $X_A$ vs. $X_{\text{path}}$)
In G1 inference, deriving the cognitive trait requires two premises:
- Premise 1 (Fact A): `manager(station, person)`
- Premise 2 (Founder): `reports_to(person, supervisor)`

The retriever's contact rate $X$ decomposes into three distinct events:
1. **Lineage Contact ($X_F$)**:
   - In clearance queries (`"Which security clearance tier is assigned to Velora?"`), query tokens match the founder memory (`"Nerin directly reports to Tal/Kira"`), achieving $\text{BM25} = 2.55$ (Rank 1) $\implies X_F = 100\%$.
   - In protocol queries (`"Which security protocol does Velora operate under?"`), the founder shares zero tokens with the query, achieving $\text{BM25} = 0.00$ (Rank 5) $\implies X_F = 0\%$.
   - Mean founder contact across G1 tasks: $X_F = 50.0\%$.
2. **Co-Support Coverage ($X_A$)**:
   - Under $k=4$ with 4 hard negatives, the station manager fact (`locus_station_manager`) scored $\text{BM25} = 0.8394$ and was pushed to **Rank 4** (just 1 slot outside top-4 context).
3. **Complete-Path Recovery ($X_{\text{path}}$)**:
   - Because single-pass query-only top-4 retrieval prunes the complementary bridge premise, complete evidence assembly under crowded hard negatives collapses to **$X_{\text{path}} = 0.0\%$**.

### 2.2 Model Behavior Under Retrieval Failure: Reject-Option vs. Epistemic Error
When the retriever withheld the complete proof path ($D_{\text{ctx}} = 0$):
- **7 / 8 ($87.5\%$) tasks cleanly returned `UNKNOWN` (`EXTINCT`)**.
- **1 / 8 ($12.5\%$) tasks emitted an unsupported concrete output**, which was cleanly classified by the DualOracle as an **`EPISTEMIC` error** ($D_{\text{ctx}} = 0$, state vector $(0, 0, 0, 0, 1)$).
- **Zero semantic transmission** occurred without the complete proof path.

### 2.3 Hard-Negative Clutter Dose-Response (Ablation Sweep)
Holding $k=4$ fixed while parametrically varying hard negative clutter ($N_{\text{hard}} \in \{0, 2, 4, 8\}$) reveals the monotonic collapse of multi-hop recovery:
- $N_{\text{hard}} = 0 \implies X_F = 100.0\%, X_A = 100.0\%, \mathbf{X_{\text{path}} = 100.0\%}$
- $N_{\text{hard}} = 2 \implies X_F = 100.0\%, X_A = 87.5\%, \mathbf{X_{\text{path}} = 87.5\%}$
- $N_{\text{hard}} = 4 \implies X_F = 50.0\%, X_A = 87.5\%, \mathbf{X_{\text{path}} = 37.5\%}$
- $N_{\text{hard}} = 8 \implies X_F = 50.0\%, X_A = 50.0\%, \mathbf{X_{\text{path}} = 0.0\%}$

```text
       Complete-Path Recall X_path vs Hard Negative Clutter
 100% ┤ ● N=0 (100%)
  80% ┤     ● N=2 (87.5%)
  60% ┤
  40% ┤         ● N=4 (37.5%)
  20% ┤
   0% ┼────────────────────────● N=8 (0.0%)
     N_hard = 0    2       4       8
```

### 2.4 Experimental Causal Rescue ($k=4 \to k=6$)
Expanding the retrieval budget restores the pruned bridge facts:
- $k=4 \implies X_{\text{path}} = 37.5\%$
- $k=5 \implies X_{\text{path}} = 50.0\%$
- $k=6 \implies \mathbf{X_{\text{path}} = 100.0\%}$

**Live Model Verification on `gemma3:12b`**:
- **Under $k=4$ (Path Absent)**: Model abstains on both arms $\to$ Clean: `UNKNOWN`, Infected: `UNKNOWN`.
- **Under $k=6$ (Path Restored)**: Complete deduction occurs $\to$
  - Clean Arm: `transit_route` $\to$ `ROUTE_HYPERLANE` (**HEALTHY**), `resource_tier` $\to$ `TIER_PRIORITY` (**HEALTHY**).
  - Infected Arm: `transit_route` $\to$ `ROUTE_ORBITAL_SLIP` (**SEMANTIC**), `resource_tier` $\to$ `TIER_STANDARD` (**SEMANTIC**), `access_level` $\to$ `ACCESS_ESCORT_ONLY` (**SEMANTIC**).

This directly demonstrates causal retrieval rescue: **restoring the multi-hop proof path restores phenotypic transmission**.

---

## 3. Experiment 1B-B2: Lineage Surface-Area Scaling

**Database:** `gene_exp1b_b2_20260820_040910.db` (Persisted in `surface_feedback_sweeps`)

| Lineage Multiplicity ($N_{\text{lin}}$) | $P(\text{Founder in Top-}k)$ | $P(\text{Any Lineage in Top-}k)$ | Mean Top-$k$ Occupancy ($k=4$) | Mechanism Interpretation |
| :---: | :---: | :---: | :---: | :---: |
| **$N_{\text{lin}} = 0$** | 50.0% | 50.0% | 0.50 / 4 | Single Founder Baseline |
| **$N_{\text{lin}} = 1$** | 50.0% | 100.0% | 1.50 / 4 | $+100\%$ Lineage Presence |
| **$N_{\text{lin}} = 2$** | 37.5% | 100.0% | 2.25 / 4 | Lineage Occupies Over $50\%$ of Context |
| **$N_{\text{lin}} = 4$** | 50.0% | 100.0% | 2.25 / 4 | Retrieval Visibility Saturation |
| **$N_{\text{lin}} = 8$** | 50.0% | 100.0% | 2.25 / 4 | Context Capacity Bound Reached |

*Note on Terminology*: This assay demonstrates **retrieval surface-area scaling** (lineage multiplicity expands retrieval visibility), which serves as a necessary mechanism for closed-loop reproductive feedback.

---

## 4. Auditable Database Schema & Reconstructability

All experimental runs are completely reconstructable from SQLite alone:

1. **`runs`**: Git commit, dynamic model digest, prompt hash, config hash, environment info.
2. **`calls`**: Exact JSON request payload, raw response text, parsed JSON, token counts, and latency telemetry.
3. **`memory_nodes`**: Full structured JSON representation and natural language renderings for every source, clutter, and derived memory.
4. **`dual_oracle_evaluations`**: Canonical vs. context truth status, 5-element state vectors, phenotype classification, ancestral allele fidelity.
5. **`retrieval_events`**: Complete candidate ledger recording every evaluated candidate's BM25 score, rank, paired slot ID, and top-$k$ selection flag.
6. **`surface_feedback_sweeps`**: Complete parametric lineage scaling sweep results.

---

## 5. Synthesis & Transition to Experiment 1B-C

The experimental sequence now establishes:
1. **Factorization Structure ($R_S = X \times \tau_S \times W$)**: Transmission is a product of contact, epistemic derivability, and memory admission.
2. **Internal Structure of Contact ($X = (X_F, X_A, X_{\text{path}})$)**: In multi-hop architectures, contacting an infected memory is distinct from assembling a reproductively complete proof path.
3. **The Uniform-Thinning Frontier ($R_S = 2 C_{\text{clean}}$)**: Indiscriminate retrieval thinning cannot suppress infection without proportionally destroying clean answer coverage.
4. **Surface-Area Multiplicity**: Growing lineages expand their prompt footprint independently of ground truth.

**Experiment 1B-C (Lineage-Aware Selective Immunity)** will deploy non-oracle lineage filters (provenance chain verification, authority weighting, epistemic graph pruning) to suppress infected retrieval ($p_I \to 0$) while preserving clean memory recall ($p_H \to 1$), breaking the uniform-thinning frontier under endogenous competition.


