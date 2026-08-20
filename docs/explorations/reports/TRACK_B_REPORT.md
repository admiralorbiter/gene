# Provisional Result Report — Track B: Epistemic Monoculture / Independent Roots

## 1. Executive Summary
- **Probe Status:** SUCCESSFUL
- **Total Calls Spent:** 12 (Gemma 3:12B)
- **Primary Finding:** Neural reasoners exhibit nuanced sensitivity to ancestral source diversity. When raw frequency favors a claim but roots are tied ($3:1$ raw vs $1:1$ roots), the model falls back to raw frequency repetition ($P(\text{adjudicate } X) = 1.000$). However, when an alternative claim has **multiple distinct named independent authorities** ($3:2$ raw in favor of X vs $1:2$ roots in favor of Y), the model counterfactually flips its adjudication to the diverse root claim ($P(\text{adjudicate } Y) = 1.000$).
- **Key Metric:**
  - $\Delta_{\text{diversity}} = P(\text{adjudicate } Y \mid N_{\text{roots}}=2) - P(\text{adjudicate } Y \mid N_{\text{roots}}=1) = 1.000 - 0.000 = +1.000$.

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

## 3. Scientific Significance
Language models can recognize independent ancestral lineages when explicit authority tokens differ, overcoming raw repetition advantages. However, when an echo chamber of multiple citations refers back to a single authority vs another single authority, models default to repetition heuristic counting ($N_{\text{raw}}$) rather than epistemic tie-breaking ($N_{\text{eff}}$).
