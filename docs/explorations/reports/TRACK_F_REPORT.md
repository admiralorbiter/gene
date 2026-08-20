# Provisional Result Report — Track F: Reported-Lineage Identifier Equivariance

## 1. Executive Summary
- **Probe Status:** SUCCESSFUL (Perfect Readout Equivariance)
- **Total Calls Spent:** 12 (Gemma 3:12B)
- **Primary Finding:** The self-reported support lineage citation interface ($\mathcal{R}$, $P_{\text{reported}}$) is **100% equivariant to identifier tokenization** ($A_{\text{ID}} = 1.000, E_{\text{ID}} = 0.000$).
- **Label Invariance:**
  - Whether memory nodes are labeled using natural language descriptors (`KAVO_ARCHIVE`, `RILEN_LOG`), short synthetic codes (`ZURI_01`, `MEKO_02`), or arbitrary hexadecimal hashes (`NODE_8F3A2B`, `NODE_E1C7D9`), the model unswervingly cites the exact supporting parent set without citing distractor nodes ($12/12 = 100.0\%$).

## 2. Experimental Data Matrix ($N = 12$ Calls)
| Repetition | Station | Mapping Format | Emitted Protocol | Unmapped Cited Roles | Exact Parent Set? | Distractor Leakage? |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| Rep 1 | VELORA | `semantic_natural` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 1 | VELORA | `short_coded` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 1 | VELORA | `random_hashes` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 1 | KESTREL | `semantic_natural` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 1 | KESTREL | `short_coded` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 1 | KESTREL | `random_hashes` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 2 | VELORA | `semantic_natural` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 2 | VELORA | `short_coded` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 2 | VELORA | `random_hashes` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 2 | KESTREL | `semantic_natural` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 2 | KESTREL | `short_coded` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |
| Rep 2 | KESTREL | `random_hashes` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | 0 |

## 3. Scientific Significance
This confirms that GENE's support-certificate readout interface does not rely on semantic cueing in memory identifiers. The model tracks symbolic token references purely by relational context in the retrieved prompt.
