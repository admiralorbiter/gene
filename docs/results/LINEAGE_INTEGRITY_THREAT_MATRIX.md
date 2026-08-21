# Exploration Round 6 Lineage Integrity Threat Model & Attack Report (v1)

**Assay Name**: Lineage Integrity & Adversarial Manipulation Analysis v1  
**Target Milestone**: Exploration Round 6  
**Summary Artifact**: [`../../data/exploration_round6_lineage_threat_matrix_summary.json`](../../data/exploration_round6_lineage_threat_matrix_summary.json)

---

## Executive Summary

GENE's action governance theorems establish that an agent's authority to act on a belief $c$ is proportional to its ancestral root cut-set resilience $\kappa_L(\mathcal{S}_L(c))$. If derivational lineage is treated as an unauthenticated, mutable metadata dictionary, an adversary can directly manipulate action gates via **Root Splitting** or **Root Merging**.

This assay formally implements and deterministically measures these two attack modalities, demonstrating how unauthenticated lineage allows adversaries to either illegally force actions (`BLOCK` $\to$ `PERMIT`) or cause denial of service (`PERMIT` $\to$ `BLOCK`).

```
+========================================================================================================================+
|                                    LINEAGE ATTACK MATRIX v1 RESULTS                                                    |
+================================+=========================+===========================+=================================+
| Attack Modality                | Honest Metric           | Attacked Metric           | Governance Gate Impact          |
+================================+=========================+===========================+=================================+
| 1. Root Splitting (Sybil)      | kappa_L = 1 (BLOCK)     | kappa_L = 3 (PERMIT)      | FORCED ACTION PERMISSION        |
| 2. Root Merging (Suppression)  | kappa_L = 3 (PERMIT)    | kappa_L = 1 (BLOCK)       | FALSE ACTION DENIAL (DoS)       |
+================================+=========================+===========================+=================================+
```

---

## Detailed Attack Experimental Results

### Attack: `Root Splitting (Sybil Roots Inflation)`
- **Adversarial Mechanism**: Adversary splits single root R_1 into {R_1a, R_1b, R_1c}
- **Honest Hypergraph $\mathcal{S}_L$**: `[['R_1']]` ($\kappa_L = 1$, Policy Decision: **BLOCK**)
- **Attacked Hypergraph $\mathcal{S}_L$**: `[['R_1a'], ['R_1c'], ['R_1b']]` ($\kappa_L = 3$, Policy Decision: **PERMIT**)
- **Policy Breach Demonstrated**: **YES (Gate Inverted)**
- **Defense Requirement**: **Write-time digital origin binding: Origin certificates signed by private source keys prevent sybil root synthesis.**

### Attack: `Root Merging (Denial of Service Suppression)`
- **Adversarial Mechanism**: Adversary or summarizer collapses {R_1, R_2, R_3} into {R_COMMON}
- **Honest Hypergraph $\mathcal{S}_L$**: `[['R_2'], ['R_1'], ['R_3']]` ($\kappa_L = 3$, Policy Decision: **PERMIT**)
- **Attacked Hypergraph $\mathcal{S}_L$**: `[['R_COMMON']]` ($\kappa_L = 1$, Policy Decision: **BLOCK**)
- **Policy Breach Demonstrated**: **YES (Gate Inverted)**
- **Defense Requirement**: **Immutable root preservation across summarization and transformations.**


---

## Invariant Defense Requirements

1. **Write-Time Cryptographic Origin Binding**: Lineage roots $\mathcal{L}(p)$ must be signed with private source keys $\text{Sign}_{K}(f)$ at acquisition time. Agents cannot synthesize or relabel root IDs post-hoc.
2. **Conjunctive Tool Envelope Propagation**: Any intermediary transformation tool must compute $\mathcal{L}(\text{out}) = \mathcal{L}(\text{tool}) \cup \bigcup_i \mathcal{L}(\text{in}_i)$.
