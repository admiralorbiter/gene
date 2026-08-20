# Experiment 0 Final Report — Lineage Observability & Causal Calibration

**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Experiment:** Experiment 0 (Lineage Observability & Causal Assay Calibration)  
**Status:** **FROZEN & VERIFIED**  
**Freeze Tag:** `gene-exp0-freeze-v1`  
**Date:** 2026-08-20  
**Model Under Test:** `gemma3:12b` (Ollama, dynamic SHA256 captured)  
**Hardware Environment:** NVIDIA GeForce RTX 3060 (12GB VRAM), AMD Ryzen 7 5700G, Windows 11, Python 3.12.0  

---

## 1. Executive Summary

Experiment 0 establishes the experimental instrumentation required to measure, trace, and causally verify memory lineage in language models. Before introducing infected or mutated memory lineages (Experiment 1), the research instrument must prove that it can distinguish:
1. **Machine-Readable Formal Ancestry** (Oracle forward-chaining derivation graphs);
2. **Model Self-Reported Support** (Citations emitted by the model);
3. **Counterfactual Behavioral Necessity** ($C_{\\text{nec}}$, whether knocking out a premise removes the claim);
4. **Epistemic State Accuracy** ($E$, whether the model correctly assesses evidential sufficiency);
5. **Response Policy Consistency** ($K$, whether model behavior complies with its epistemic assessment);
6. **Directional Mutational Sensitivity** (Whether altering a premise steers the model to the predictable counterfactual consequent);
7. **Sequential Compositional Rescue** (Whether restoring an ancestor in state lineage $S_0 \\xrightarrow{\\text{mut}} S_1 \\xrightarrow{\\text{rescue}} S_2$ recovers the baseline phenotype).

Through a hardened $2 \\times 2$ factorial assay spanning **264 total model calls across 6 counterbalanced micro-worlds**, we discovered that model failure occurs along two distinct mechanistic transitions:
$$\\text{Information Environment} \\xrightarrow{\\text{Epistemic Estimation } (E)} \\text{Epistemic State} \\xrightarrow{\\text{Policy Compliance } (K)} \\text{Emitted Claim } (A)$$

- **The Response Contract (Schema v2)** fixes the **detection-to-action gap** ($K$).
- **The Information Ecology (Ecology C: Competing Consequents)** fixes the **antecedent binding failure / false sufficiency estimation** ($E$).
- **Synergy (Cell 4: Ecology C + Schema v2)** achieves **100.0% causal and epistemic calibration (66/66 interventions passed)**.

With this calibration complete, Experiment 0 is frozen.

---

## 2. Theoretical Framework: Two-Stage Epistemic Decomposition

Earlier naive evaluations conflated output correctness with causal lineage. By decomposing model evaluation into three orthogonal diagnostic metrics, we isolate the exact failure phenotypes:

### 2.1 The Diagnostic Metrics ($A, E, K$)
1. **$A$ (Answer Correctness / Behavioral Output)**:
   $$\\text{Is } \\text{normalized\\_object} == \\text{expected\\_counterfactual\\_object}?$$
   Evaluates whether the model's emitted token matches the ground-truth counterfactual state derived by the machine-readable Oracle.
2. **$E$ (Epistemic State Accuracy)**:
   $$\\text{Is } \\text{raw\\_evidence\\_status} == \\text{expected\\_evidence\\_status}?$$
   Evaluates whether the model's internal assessment of evidence (`sufficient` vs `insufficient` / `conflicting`) matches the formal deductibility of the premise set.
3. **$K$ (Contract / Policy Consistency)**:
   $$\\text{Does } (\\text{raw\\_evidence\\_status} \\in \\{\\text{insufficient}, \\text{conflicting}\\}) \\implies (\\text{normalized\\_object} == \\text{"UNKNOWN"})?$$
   Evaluates whether the model's generation complies with its own epistemic judgment.

### 2.2 Mechanism of Action
- **Control / Action Failure ($A=0, E=1, K=0$)**: The model correctly recognizes that evidence is missing (`confidence: 0.0` or `evidence_status: insufficient`), but emits a specific answer token anyway due to token completion pressure. (Prominent in Schema v1).
- **Epistemic State Estimation Failure ($A=0, E=0, K=1$)**: The model erroneously judges that incomplete or mutated evidence is sufficient (`evidence_status: sufficient`) due to single-consequent rule salience, and then behaves consistently with that false judgment by emitting the rule's conclusion token. (Prominent in Ecology S).

---

## 3. Biological Informational Nomenclature

To prevent ambiguity between memory slot identity and semantic content, GENE formalizes a strict biological mapping:

| Biological Term | Informational Definition in GENE | Implementation in Engine |
| :--- | :--- | :--- |
| **Locus** | Persistent memory slot identity in the agent's context. Invariant under mutation and replacement. | `locus_id` (`mem_locus_station_manager`, `mem_locus_manager_supervisor`). |
| **Allele** | Specific semantic proposition (fact/rule triple) currently occupying a locus. | `Fact.fact_id` (deterministic SHA256 digest of `(subject, predicate, object)`). |
| **Mutation** | Modifying the semantic allele at a locus while preserving locus identity. | `InterventionSpec(mutated_facts=[Fact(..., locus_id=base.locus_id)])`. |
| **Deletion / Knockout** | Removing a locus entirely from the active retrieval context. | `target_node_ids=[locus_id]`, excluded from prompt rendering. |
| **Expression** | Exposure of a memory locus in the retrieved context prompt. | `exposure_edges` logged in database. |
| **Phenotype** | The downstream generated claim emitted by the model. | `memory_nodes(node_type="derived")`. |
| **Fitness / Replication**| The transmission and citation of a memory node into descendant generations. | $R_0$ (Reproductive number in Experiment 1). |

---

## 4. Hardened $2 \\times 2$ Factorial Results

The complete $2 \\times 2$ factorial assay was executed on the exact same 6 counterbalanced canonical micro-worlds across all 6 rule-order permutations ($p \\in \\{0..5\\}$) and all 3 supervisor-to-protocol rotations ($r \\in \\{0..2\\}$ marginally).

### Factorial Matrix Summary

| Cell | Information Ecology | Output Response Schema | Total Calls | Intervention Tests | Interventions Passed | Pass Rate ($A$) | Primary Failure Phenotype |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | **Ecology S** (Single Rule) | **Schema v1** (Implicit) | 66 | 60 | **28 / 60** | **46.7%** | **Detection-to-Action Split ($K=0$)**: Emits conclusion token on deletion/mutation despite recognizing missing evidence. |
| **2** | **Ecology S** (Single Rule) | **Schema v2** (Explicit) | 66 | 60 | **52 / 60** | **86.7%** | **Antecedent Binding Failure ($E=0, K=1$)**: Single rule conclusion acts as an attractor; model falsely judges $E=\\text{sufficient}$. |
| **3** | **Ecology C** (Competing Rules)| **Schema v1** (Implicit) | 72 | 66 | **43 / 66** | **65.2%** | **Directional Sensitivity without Abstention**: Directional mutations pass (100%), but unmatched mutations ($\\to$ Soren) fail to abstain (0%). |
| **4** | **Ecology C** (Competing Rules)| **Schema v2** (Explicit) | 72 | 66 | **66 / 66** | **100.0%** | **Flawless Calibration ($A=1, E=1, K=1$)**: 100% directional steering, 100% knockout abstention, 100% unmatched abstention, 100% rescue. |

```
                 SCHEMA v1 (Implicit)       SCHEMA v2 (Explicit Contract)
               +--------------------------+-------------------------------+
  ECOLOGY S    |         CELL 1           |            CELL 2             |
  (Single Rule)|     Pass Rate: 46.7%     |       Pass Rate: 86.7%        |
               | (Detection-Action Split) |  (Antecedent Binding Failure) |
               +--------------------------+-------------------------------+
  ECOLOGY C    |         CELL 3           |            CELL 4             |
  (Competing   |     Pass Rate: 65.2%     |       Pass Rate: 100.0%       |
   Rules)      | (No Abstention Contract) |   (Full Causal Calibration)   |
               +--------------------------+-------------------------------+
```

---

## 5. Detailed Breakdown of Cell 4 (The Frozen Benchmark)

**Database:** `gene_d1_c_v2_20260820_001206.db` (Ollama `gemma3:12b`)

Across all 6 counterbalanced micro-worlds (72 model calls, 66 intervention tests):

| Assay Battery Category | Target / Counterfactual State | Expected Behavior | Observed Pass Rate | Diagnostics |
| :--- | :--- | :--- | :---: | :---: |
| **Clean Baseline ($S_0$)** | Clean micro-world state | Emits Target Protocol ($X7, Q2, M9$) | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **No-op Sham Control** | Identical context replay | Emits Target Protocol ($S_0$ stability) | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Knockout Premise A** | Delete `manager(station, person)` | Abstain to `UNKNOWN` ($C_{\\text{nec}}=100\%$) | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Knockout Premise B** | Delete `reports_to(person, sup)` | Abstain to `UNKNOWN` ($C_{\\text{nec}}=100\%$) | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Knockout Active Rule**| Delete active deduction rule | Abstain to `UNKNOWN` ($C_{\\text{nec}}=100\%$) | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Knockout Foil Rule**  | Delete inactive competing rule | Invariant: Emits Target Protocol ($H_D=0\%$) | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Epistasis Double KO** | Delete Premise A + Premise B | Abstain to `UNKNOWN` | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Directional Mutation 1**| Mutate B: $\\text{Kira} \\to \\text{Tal}$ | Steer to Tal's Protocol ($Q2, X7, M9$) | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Directional Mutation 2**| Mutate B: $\\text{Kira} \\to \\text{Mira}$| Steer to Mira's Protocol ($M9, Q2, X7$)| **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Unmatched Mutation**   | Mutate B: $\\text{Kira} \\to \\text{Soren}$| Abstain to `UNKNOWN` (No rule match) | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Sequential Rescue**    | Restore $S_1 (\\text{Tal}) \\to S_2 (\\text{Kira})$ | Recover $S_0$ Target Protocol | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **Distractor Fact KO**   | Delete non-rule station fact | Invariant: Emits Target Protocol | **6 / 6 (100.0%)** | $A=1, E=1, K=1$ |
| **OVERALL CELL 4 SCORE**  | **Complete 11-Intervention Assay** | **All Invariants Confirmed** | **66 / 66 (100.0%)** | **FLAWLESS** |

---

## 6. Telemetry & Computational Performance

- **Average Call Latency:** 4.82 seconds (warm GPU context).
- **Prompt Evaluation Duration:** $550\\text{ ms} - 1,100\\text{ ms}$.
- **Token Generation Duration:** $1.8\\text{ s} - 4.5\\text{ s}$.
- **Prompt Token Count:** ~240–280 tokens per call.
- **Completion Token Count:** ~35–65 tokens per call.
- **Total Experiment 0 Calls Executed:** 264 calls across 4 databases, completed in ~22 minutes without a single API drop or malformed JSON error.

---

## 7. Artifact & Database Inventory

All experimental artifacts and databases are preserved in the repository:

1. `gene_d1_c_v2_20260820_001206.db`: Cell 4 (Ecology C / Schema v2) — 72 calls, 66 tests (100.0% pass).
2. `gene_d1_s_v2_20260820_002016.db`: Cell 2 (Ecology S / Schema v2) — 66 calls, 60 tests (86.7% pass).
3. `gene_d1_s_v1_20260820_003640.db`: Cell 1 (Ecology S / Schema v1) — 66 calls, 60 tests (46.7% pass).
4. `gene_d1_c_v1_20260820_004223.db`: Cell 3 (Ecology C / Schema v1) — 72 calls, 66 tests (65.2% pass).
5. `tests/test_interventions_and_competing.py`: 9 comprehensive deterministic unit/property tests.
6. `tests/`: 52 / 52 automated tests passing in test suite.

---

## 8. Transition to Experiment 1: The Three Infection Phenotypes

With Experiment 0 frozen, Experiment 1 will introduce a single mutated source memory (the "bad gene") into generation $G_0$ and track its transmission across multi-generation propagation networks ($G_0 \\to G_1 \\to G_2 \\dots$).

Using the $A/E/K$ diagnostic engine established in Experiment 0, we can now distinguish **three distinct infection phenotypes** in downstream descendants:

1. **Semantic Infection ($A=0, E=1, K=1$)**:
   The descendant inherits the mutated premise and validly derives an incorrect downstream claim.
   $$\\text{Transmission Rate: } R_{\\text{semantic}}$$
2. **Epistemic Infection ($A=0, E=0, K=1$)**:
   The descendant falsely estimates that corrupted/insufficient evidence is sufficient and forces an unsupported conclusion.
   $$\\text{Transmission Rate: } R_{\\text{epistemic}}$$
3. **Control / Policy Infection ($A=0, E=1, K=0$)**:
   The descendant recognizes that evidence is corrupted/insufficient, but fails its response policy and emits a hallucinated claim anyway.
   $$\\text{Transmission Rate: } R_{\\text{control}}$$

This completes Experiment 0. The instrument is frozen and ready for Experiment 1.
