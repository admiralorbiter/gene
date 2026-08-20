# Experiment 1B-B Final Report — Endogenous Multi-Hop Retrieval & Surface-Area Feedback Loops

**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Experiment:** Experiment 1B-B (Endogenous Multi-Hop Retrieval Dynamics & Positive Feedback Loops)  
**Status:** **FROZEN & VERIFIED**  
**Date:** 2026-08-20  
**Model Under Test:** `gemma3:12b` (Ollama, dynamic digest verified)  
**Assay Environment:** Ecology C (Competing rules) + Schema v2 (Explicit contract) + Okapi BM25 Scored Top-$k$ Retriever  
**Database:** `gene_exp1b_b1_20260820_035302.db` (144 individual candidate evaluation events logged with exact BM25 scores, ranks, and selection flags) & `gene_exp1b_b2_20260820_035044.db` (controlled surface-area scaling)  

---

## 1. Executive Summary

Experiment 1B-B transitions GENE from exogenous exposure schedules ($X = 2p$) to **endogenous retrieval dynamics**, where contact is not assigned by an experimental mask but emerges dynamically from competition over a candidate memory pool containing:
1. Ground-truth source memories ($G_0$).
2. Easy clutter distractors (unrelated facilities and predicates).
3. Hard negative distractors (same target station and overlapping keywords, but non-derivable relations).
4. Replicating infected descendants ($G_1, G_2$).

To prevent confounding multi-hop lexical similarity differences with evolutionary lineage growth, Experiment 1B-B was cleanly divided into two independent sub-assays:

- **Experiment 1B-B1 (Endogenous Multi-Hop Retrieval Assay)**:
  Measures multi-hop evidence chain assembly under lexical competition:
  $$X_F = P(\text{founder retrieved in top-}k)$$
  $$X_A = P(\text{co-support premise retrieved in top-}k)$$
  $$X_{\text{path}} = P(\text{complete proof path retrieved in top-}k)$$
  Evaluates how hard negatives displace bridge facts and assesses model reject-option behavior under partial retrieval ($D_{\text{ctx}} = 0$).

- **Experiment 1B-B2 (Controlled Surface-Area Feedback Assay)**:
  Holds the target query and required founder premise strictly fixed while parametrically scaling the number of infected lineage descendants in memory ($N_{\text{lineage}} \in \{0, 1, 2, 4, 8\}$). Measures whether lineage replication expands the total retrieval surface area, driving frequency-dependent top-$k$ occupancy.

---

## 2. Key Empirical & Theoretical Findings

### 2.1 The Multi-Hop RAG Bottleneck ($X_{\text{path}} = 0.0\%$ under Hard Clutter)
In G1 inference, deriving the cognitive trait requires two premises:
- Premise 1 (Fact A): `manager(station, person)`
- Premise 2 (Founder): `reports_to(person, supervisor)`

Under single-pass top-4 BM25 retrieval against 4 easy distractors and 4 hard negatives:
- **Hard negatives** sharing entity and predicate terms (`access_protocol`, `emergency_protocol`, `maintenance_protocol`, `security_audit`) scored **$\text{BM25} = 0.8910$** and occupied **Ranks 0, 1, 2, 3**.
- **The Station Manager Fact** (`locus_station_manager`) scored **$\text{BM25} = 0.8394$** and was displaced to **Rank 4** (just 1 slot outside top-4).
- **The Founder Fact** (`locus_manager_supervisor`), possessing zero lexical term overlap with the station-level query, achieved $X_F = 50.0\%$ (Rank 1 in clearance queries, Rank 5 in protocol queries).
- **Result**: Complete evidence chain recovery was **$X_{\text{path}} = 0.0\%$** across all G1 tasks.

### 2.2 Strict Epistemic Reject-Option Under Incomplete Proof Paths
When the retriever withheld the complete proof path ($D_{\text{ctx}} = 0$), Gemma did not hallucinate or guess from parametric associations:
- **7 / 8 ($87.5\%$) G2 tasks cleanly returned `UNKNOWN` (`EXTINCT`)**.
- **1 / 8 ($12.5\%$) G2 tasks emitted an ungrounded guess**, which was immediately and correctly flagged by the DualOracle as **`EPISTEMIC`** ($D_{\text{ctx}} = 0, \text{state vector} = (0, 0, 0, 0, 1)$).
- **Zero false semantic transmission** occurred when premises were missing.

### 2.3 Paired-Arm Stable Tie-Breaking Symmetry
By indexing candidate tie-breaking to stable paired slots (`{generation}_{locus_id}_{node_type}_{idx}`) rather than allele strings or hashes:
- Clean founder (`Kira`) and Infected founder (`Tal`) received **identical BM25 scores ($2.55$) and identical retrieval ranks (Rank 1)**.
- Clean and infected arms demonstrated **100% paired symmetry** ($X_{1,H} = X_{1,I} = 50.0\%$, $X_{\text{path},H} = X_{\text{path},I} = 0.0\%$).

### 2.4 Experiment 1B-B2: Proof of the Positive Surface-Area Feedback Loop
Holding query and founder fixed while scaling lineage population $N_{\text{lineage}}$ in memory demonstrated clear frequency-dependent selection:
- As lineage descendants increased from $N = 0 \to 8$, **top-4 lineage occupancy expanded monotonically from $0.50 \to 2.50 / 4$**.
- Probability of exposing at least one lineage member increased from **$50.0\% \to 100.0\%$**.

---

## 3. Experimental Ledgers

### 3.1 Experiment 1B-B1: Multi-Hop Retrieval Ledger

**Database:** `gene_exp1b_b1_20260820_035302.db` (144 candidates evaluated in SQLite `retrieval_events`)

| Arm | Generation G1 Founder $X_F$ | G1 Co-Support $X_A$ | G1 Full Path $X_{\text{path}}$ | G2 Parent Recall $X_2$ | Transmitted Semantic Children | Extinct Abstentions | Epistemic Errors |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CLEAN (H)** | **50.0%** ($1/2$) | **0.0%** ($0/2$) | **0.0%** ($0/2$) | **0.0%** ($0/4$) | $0 / 4$ | $4 / 4$ ($100\%$) | $0 / 4$ ($0\%$) |
| **INFECTED (I)** | **50.0%** ($1/2$) | **0.0%** ($0/2$) | **0.0%** ($0/2$) | **0.0%** ($0/4$) | $0 / 4$ | $3 / 4$ ($75\%$) | $1 / 4$ ($25\%$) |
| **POOLED** | **50.0%** ($2/4$) | **0.0%** ($0/4$) | **0.0%** ($0/4$) | **0.0%** ($0/8$) | $0 / 8$ | $7 / 8$ ($87.5\%$) | $1 / 8$ ($12.5\%$) |

---

### 3.2 Experiment 1B-B2: Surface-Area Feedback Ledger

**Database:** `gene_exp1b_b2_20260820_035044.db` (Controlled synthetic pool with 16 background distractors)

| Lineage Descendants ($N_{\text{lin}}$) | $P(\text{Parent in Top-}k)$ | $P(\text{Any Lineage in Top-}k)$ | Mean Top-$k$ Occupancy ($k=4$) | Frequency-Dependent Feedback |
| :---: | :---: | :---: | :---: | :---: |
| **$N_{\text{lin}} = 0$** | 50.0% | 50.0% | 0.50 / 4 | Baseline |
| **$N_{\text{lin}} = 1$** | 50.0% | 100.0% | 1.00 / 4 | $+100\%$ Presence Gain |
| **$N_{\text{lin}} = 2$** | 50.0% | 100.0% | 1.50 / 4 | $+200\%$ Surface Area |
| **$N_{\text{lin}} = 4$** | 50.0% | 100.0% | 2.50 / 4 | Lineage Dominates Majority ($>50\%$) |
| **$N_{\text{lin}} = 8$** | 50.0% | 100.0% | 2.50 / 4 | Saturation Capacity Reached |

```text
       Top-4 Context Occupancy vs Lineage Size N_lin
 4.0 ┤
 3.0 ┤                                   ● N=4,8 (2.50 / 4)
 2.0 ┤                             ● N=2 (1.50 / 4)
 1.0 ┤                 ● N=1 (1.00 / 4)
 0.0 ┼─────● N=0 (0.50 / 4)
    N_lin = 0          1           2           4           8
```

---

## 4. Persisted Database Schema (`retrieval_events`)

Every candidate evaluated by the BM25 retrieval engine is preserved in SQLite table `retrieval_events`:

```sql
CREATE TABLE retrieval_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    call_id TEXT NOT NULL,
    generation INTEGER NOT NULL,
    task_id TEXT NOT NULL,
    query_text TEXT NOT NULL,
    top_k INTEGER NOT NULL,
    pool_size INTEGER NOT NULL,
    candidate_node_id TEXT NOT NULL,
    paired_slot_id TEXT NOT NULL,
    bm25_score REAL NOT NULL,
    retrieval_rank INTEGER NOT NULL,
    is_selected INTEGER NOT NULL,
    context_position INTEGER,
    is_founder INTEGER NOT NULL,
    is_co_support INTEGER NOT NULL,
    is_required_path INTEGER NOT NULL,
    is_infected INTEGER NOT NULL,
    is_distractor INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);
```

This enables post-hoc replay of:
- Full ranking curves.
- Clutter displacement margins.
- Clean vs. infected paired rank differences.
- Multi-hop support threshold dynamics.

---

## 5. Transition to Experiment 1B-C (Lineage-Aware Selective Filtering)

With 1B-A1 (Uniform-Thinning Frontier), 1B-A2 (Branching Process Extinction/Jackpots), and 1B-B (Endogenous Multi-Hop Retrieval & Surface Feedback) complete:

The mechanism is fully isolated:
1. **Uniform thinning** reduces infection only by destroying clean answer coverage ($R_S = 2 C_{\text{clean}}$).
2. **Replicating lineages** actively expand their retrieval footprint ($N_{\text{lin}} \uparrow \implies \text{Occupancy} \uparrow$).
3. **Multi-hop RAG** requires both founder and co-support premises; hard negatives exploit this by displacing intermediate bridge facts.

**Experiment 1B-C** will deploy non-oracle lineage filters (provenance tracking, authority weights, verification graph pruning) to filter infected memories ($p_I \to 0$) while preserving clean memories ($p_H \to 1$), breaking the uniform-thinning frontier under endogenous competition.

