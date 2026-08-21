---
contract_id: CONTRACT-R8-8C
status: DRAFT
proposed_by: antigravity
design_review: null
reviewed_by: chatgpt-pro
authorized_by: null
base_sha: add7574737a88f43570d645a1a8e0dcae4b099d8
execution_base_sha: null
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
---

# Research Contract Proposal: CONTRACT-R8-8C (Incubation / Draft)

## Title
Exploration Round 8 Stage 8C: Autonomous Open-World Ontology Induction & Epistemic Registry Extension

## 1. Context & Research Question
In Stage 8B-R1, registry-assisted neural extraction was proven to feed a deterministic bitemporal system that safely integrates repeated entity mentions and out-of-order contradictory telemetry ($100\%$ precision, $\text{FDAR} \equiv 0.0\%$). However, Stage 8B relied on a static, pre-registered canonical entity registry.

Stage 8C isolates the next critical scaffolding removal: **autonomous open-world ontology extension**. The system must safely classify unmapped entity mentions without pre-supplied alias dictionaries, determining whether a novel mention should be linked to an existing canonical entity, admitted as a new provisional entity, kept strictly distinct from near-collisions, or deferred due to ambiguity.

```
Stage 8B (Static Pre-Registered Ontology):
Document Stream -> LLM Extract + Canonical Registry Lookup -> Bitemporal Engine -> Epistemic Truth

Stage 8C (Autonomous Open-World Induction):
Document Stream -> LLM Epistemic Reasoner [LINK | CREATE_PROVISIONAL | KEEP_DISTINCT | DEFER] -> Proof-Carrying Ingress -> Dynamic Registry Evolution
```

### Core Research Question
Can an autonomous neural reasoner safely induct novel entity identities, link unmapped aliases to known canonical entities, preserve separation among near-collision entities, and defer under insufficient evidence, while maintaining zero false durable merges ($\text{FDAR}_{\text{merge}} \equiv 0.0\%$)?

---

## 2. Empirical Scouting Findings (Stage 8C Scout Baseline)
Prior to drafting, a 20-case exploratory scout was conducted on `gemma3:12b` across four core classes (5 cases each):
1. **Genuinely Novel Entities**: $5/5$ ($100.0\%$) correct `CREATE_PROVISIONAL` admissions (e.g. `Aurora Node 1`, `Helios Ingress Unit`).
2. **Unmapped Aliases of Known Entities**: $5/5$ ($100.0\%$) correct `LINK_TO_EXISTING` resolutions (e.g. `CC-1 Prime`, `Array PA-2 Main`).
3. **Near-Collision Boundaries**: $3/5$ ($60.0\%$) correct separation. **Key Failure Modes Discovered**:
   - Sub-unit/suffix ambiguity: `Compute Cluster 1-B` was mistakenly linked to `Compute Cluster 1` (treating suffix as variant rather than distinct unit).
   - Cardinality confusion: `Compute Cluster 10` was proposed as provisional rather than partitioned as distinct from `Compute Cluster 1`.
4. **Ambiguous / Insufficient Evidence**: $4/5$ ($80.0\%$) correct `DEFER` actions. Bare single-word tokens (e.g. `Array`) occasionally triggered over-eager creation instead of safe deferral.

---

## 3. Epistemic Decision Taxonomy & Ingress Policy

For every unmapped entity mention $M$ encountered in the document stream:
1. **`LINK_TO_EXISTING`**: High-confidence linguistic/operational alias mapping to an established canonical record $E \in \mathcal{R}_{\text{known}}$.
2. **`CREATE_PROVISIONAL`**: High-confidence detection of an unambiguous, previously unseen hardware entity. Emits a new provisional identity $E_{\text{prov}}$.
3. **`KEEP_DISTINCT`**: Explicit rejection of near-collision candidate matches (e.g. `Cluster 1-A` vs `Cluster 1-B`).
4. **`DEFER`**: Insufficient contextual grounding or bare generic terminology (`The Node`, `System`). Emits zero durable ontology mutations.

### Epistemic Safety Invariant
- **Proof-Carrying Ingress Rule**: No unmapped mention may mutate the durable registry without a structured evidence proof and confidence calibration.
- **Fail-Closed Principle**: When evidence is ambiguous, the system must defer rather than hypothesize.

---

## 4. Proposed Factorial Evaluation Matrix (Confirmatory Target)

The confirmatory experiment will evaluate $N=60$ sealed evaluation worlds ($N=120$ documents) balanced across a $2 \times 2$ factorial grid:

| Factorial Cell | Registry State | Mention Relationship | Expected Epistemic Decision | Target Metric Floor |
| :--- | :--- | :--- | :--- | :--- |
| **Cell 1: Novel Discovery** | Known $\mathcal{R}_0$ | Unseen Hardware Units ($N=30$) | `CREATE_PROVISIONAL` | Recall $\ge 85.0\%$ |
| **Cell 2: Unmapped Aliases** | Known $\mathcal{R}_0$ | Multi-Doc Variant Names ($N=30$) | `LINK_TO_EXISTING` | Precision $\ge 90.0\%$ |
| **Cell 3: Adversarial Collisions** | Known $\mathcal{R}_0$ | Syntactic Near-Collisions ($N=30$) | `KEEP_DISTINCT` | False Merges $\equiv 0.0\%$ |
| **Cell 4: Epistemic Deferral** | Known $\mathcal{R}_0$ | Ambiguous Bare Mentions ($N=30$) | `DEFER` | False Admissions $\equiv 0.0\%$ |

---

## 5. Epistemic Scope Ceilings
- **Claim Ceiling**: Explores autonomous open-world entity identity induction and dynamic registry extension in controlled multi-document technical corpora.
- **Exclusions**: Does NOT claim unconstrained real-world web entity resolution, cross-ontology schema alignment, or open-vocabulary relation induction (predicate schemas remain fixed).
