# Post-Review Result Report — Track F: Reported-Lineage Identifier Equivariance

## 1. Executive Summary
- **Probe Status:** CONFOUNDED — ANSWER LEAK
- **Total Calls Spent:** 12 (Gemma 3:12B)
- **Critical Confound Identified (Answer Leakage):** The prompt generation function `build_track_f_prompt` constructed the target JSON schema template as follows:
  ```python
  target_schema = '{"station": "' + station + '", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient", "cited_memory_ids": ["' + mapping['parent_mgr'] + '", "' + mapping['parent_sup'] + '"]}'
  ```
  The prompt literally provided the exact two target memory IDs directly inside the schema example.
- **Confound Impact:** The assay cannot distinguish whether Gemma:
  1. Actively tracked symbolic parent lineage across different identifier tokenizations; or
  2. Simply copied the literal string values embedded in the prompt schema.
- **Action:** The reported-lineage identifier equivariance invariant is **not** established and remains open.

## 2. Experimental Data Matrix ($N = 12$ Calls)
| Repetition | Station | Mapping Format | Emitted Protocol | Unmapped Cited Roles | Exact Parent Set? | Result Interpretation |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| Rep 1 | VELORA | `semantic_natural` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 1 | VELORA | `short_coded` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 1 | VELORA | `random_hashes` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 1 | KESTREL | `semantic_natural` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 1 | KESTREL | `short_coded` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 1 | KESTREL | `random_hashes` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 2 | VELORA | `semantic_natural` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 2 | VELORA | `short_coded` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 2 | VELORA | `random_hashes` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 2 | KESTREL | `semantic_natural` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 2 | KESTREL | `short_coded` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |
| Rep 2 | KESTREL | `random_hashes` | `PROTO_X7` | `['parent_mgr', 'parent_sup']` | 1 | Confounded by schema leak |

## 3. Revised Conclusion & Proper Hardening Protocol
This probe is a classic prompt-engineering artifact that illustrates the necessity of rigorous adversarial review.

The un-confounded protocol requires:
1. Target schema with generic placeholders only: `"cited_memory_ids": ["id_a", "id_b"]` (or empty list schema).
2. Randomizing the sequential presentation order of memories in the retrieved context.
3. Permuting and rotating which opaque identifier is bound to which semantic fact.
4. Unmapping emitted IDs strictly post-inference.
