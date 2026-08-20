# Post-Review Result Report — Track B: Epistemic Monoculture / Independent Roots

## 1. Executive Summary
- **Probe Status:** PROMISING — HARDEN
- **Total Calls Spent:** 12 (Gemma 3:12B)
- **Observed Phenomenon:** The model exhibited a striking behavioral shift across evidence conditions:
  - 3 reports from 1 common named authority vs 1 report from 1 authority $\to$ `PROTO_X` ($4/4$ calls, following raw frequency).
  - 3 reports from 3 independent authorities vs 1 report from 1 authority $\to$ `PROTO_X` ($4/4$ calls).
  - 3 reports from 1 common authority vs 2 reports from 2 independent authorities $\to$ `PROTO_Y` ($4/4$ calls, flipping to the minority count).
- **Critical Confounds Identified in Post-Review:**
  1. **Direct Prompt Steering:** The prompt explicitly instructed the model: *"Evaluate the reliability, independent sources, and potential corroboration of the evidence."* The test does not establish whether the model spontaneously discounts shared ancestry without explicit prompting.
  2. **Rich Semantic Authority Cues:** Roots were described with high-status professional titles (`Station Director Kira`, `Chief Engineer Nerin`, `Fleet Commander Jax`, `Security Chief Tal`, `Grid Auditor Vael`) rather than opaque provenance identifiers.
  3. **Document Count Asymmetry:** `inverted_diversity` presented 5 retrieved reports in context while `monoculture` and `diverse_roots` presented 4 reports, breaking the planned document-count invariance.
  4. **Unidirectional Target Assignment:** `PROTO_X` was always the repetition-favored allele and `PROTO_Y` was always the diversity-favored allele; counterbalanced X/Y directional flips were planned but not executed.

## 2. Experimental Data Matrix ($N = 12$ Calls)
| Repetition | Station | Condition | Raw Ratio | Root Ratio | Adjudicated Protocol | Follows Surface? | Follows Diversity? |
| :---: | :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| Rep 1 | VELORA | `monoculture` | 3:1 (X) | 1:1 | `PROTO_X` | 1 | 0 |
| Rep 1 | VELORA | `diverse_roots` | 3:1 (X) | 3:1 (X) | `PROTO_X` | 1 | 1 |
| Rep 1 | VELORA | `inverted_diversity` | 3:2 (X) | 1:2 (Y) | `PROTO_Y` | 0 | 1 |
| Rep 1 | KESTREL | `monoculture` | 3:1 (X) | 1:1 | `PROTO_X` | 1 | 0 |
| Rep 1 | KESTREL | `diverse_roots` | 3:1 (X) | 3:1 (X) | `PROTO_X` | 1 | 1 |
| Rep 1 | KESTREL | `inverted_diversity` | 3:2 (X) | 1:2 (Y) | `PROTO_Y` | 0 | 1 |
| Rep 2 | VELORA | `monoculture` | 3:1 (X) | 1:1 | `PROTO_X` | 1 | 0 |
| Rep 2 | VELORA | `diverse_roots` | 3:1 (X) | 3:1 (X) | `PROTO_X` | 1 | 1 |
| Rep 2 | VELORA | `inverted_diversity` | 3:2 (X) | 1:2 (Y) | `PROTO_Y` | 0 | 1 |
| Rep 2 | KESTREL | `monoculture` | 3:1 (X) | 1:1 | `PROTO_X` | 1 | 0 |
| Rep 2 | KESTREL | `diverse_roots` | 3:1 (X) | 3:1 (X) | `PROTO_X` | 1 | 1 |
| Rep 2 | KESTREL | `inverted_diversity` | 3:2 (X) | 1:2 (Y) | `PROTO_Y` | 0 | 1 |

## 3. Revised Conclusion & Hardening Roadmap
Track B provides a highly compelling behavioral seed: when explicitly instructed, Gemma prioritizes two distinct authorities over three repetitions of one authority. However, this is not yet evidence of spontaneous genealogical discounting. 

A rigorous hardening assay must test:
- Opaque, non-semantic root identifiers (e.g. `source_id_01` vs `source_id_02`).
- Strictly matched document counts across all conditions ($N=4$ or $N=5$).
- Counterbalanced X/Y predicate assignments.
- Unprompted adjudication (neutral prompt with zero instructions directing the model to weight independence).
- Must remain separate from Track A / Recovery to avoid conflating distinct causal questions.
