# Exploration Round 7 Stage 7A.2 Report: Epistemic Privilege Escalation, Lifecycle Integrity, and Hardened Ingress Architecture

**Document Status**: Canonical Empirical Report (Stage 7A.2 Privilege-Path Closure & Hardening)  
**Author**: Antigravity Research / GENE Core  
**Associated Target Commit**: `round7-stage7a2-security-freeze`  
**Prerequisites**: Exploration Round 7 Wave 0.2 Freeze ([`round7-wave0-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round7-wave0-freeze)), Stage 7A.1 Post-Review ([`round7-stage7a-postreview-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round7-stage7a-postreview-freeze))  
**Primary Artifact**: [`data/exploration_round7_stage7a_benchmark_summary.json`](../../data/exploration_round7_stage7a_benchmark_summary.json) (`SHA-256: 60f82439f9863cd1f680a549c3afc1f5c51a8c8fd7a60c0192b77129086b8194`)  

---

## 1. Executive Summary & Epistemic Privilege Escalation

Exploration Round 7 investigates the boundary condition of durable epistemic storage. In Stage 7A.2, we formalize the **Epistemic Privilege Escalation Principle**:
> Persistent epistemic systems do not merely decide admission once at ingress. Rather, information repeatedly ascends through distinct privilege tiers over its operational lifecycle:
> $$\text{Raw Record} \xrightarrow{\text{admission}} \text{Candidate / Deferred} \xrightarrow{\text{resolution}} \text{Admitted Fact} \xrightarrow{\text{promotion}} \text{Canonical Entity} \xrightarrow{\text{governance}} \text{Actionable Belief}$$
> Every transition increases what the information is authorized to effectuate. Therefore:
> $$\text{Admission Integrity} \not\equiv \text{Resolution Integrity} \not\equiv \text{Promotion Integrity}$$

Stage 7A.2 closes all unverified write and promotion paths, ensuring that every transition requires an independently verifiable, proof-carrying witness.

---

## 2. Core Architectural Discoveries & Hardened Ingress Invariants

### 2.1 The Orthogonality of Referential and Authorization Correctness
$$\text{Referential Correctness} \not\equiv \text{Authorization Correctness}$$

Stage 7A proves that candidate ambiguity preservation and authorization gating address orthogonal failure classes:
1. **Candidate Preservation Alone (`A2`)**: Eliminates candidate ambiguity and novelty collapse ($\text{UPR} = 100.0\%$, $\text{FDAR}_{\text{ambiguity}} = 0.0\%$, $\text{FDAR}_{\text{novel}} = 0.0\%$), but suffers $100.0\%$ False Durable Admission on resolved unauthorized claims ($\text{FDAR}_{\text{authority}\mid\text{resolved}} = 36/36 = 100.0\%$).
2. **Authority Gating Alone (`A3`)**: Eliminates unauthorized root promotions ($\text{FDAR}_{\text{authority}} = 0.0\%$), but prematurely collapses $100.0\%$ of authorized candidate collisions to Top-1 ($\text{FDAR}_{\text{ambiguity}\mid\text{authorized}} = 12/12 = 100.0\%$, $\text{UPR} = 0.0\%$).
3. **Full Proof-Carrying Ingress (`A4`)**: Unifies hypothesis preservation ($\mathcal{B}(x) = \{b_1, \dots, b_k\}$ under `DEFERRED_BINDING`), `PROVISIONAL_ENTITY` tracking, capability-scoped authorization, and standalone certificate verification, achieving $\mathbf{100.0\% \text{ WorldPass}}$, $\mathbf{\text{FDAR} = 0.0\%}$, $\mathbf{\text{SAC} = 100.0\%}$, and $\mathbf{\text{UPR} = 100.0\%}$.

```
+================================================================================================================+
|                       STAGE 7A.2 FACTORIAL INGRESS BENCHMARK (N=120 WORLDS / 480 PROBES)                       |
+=========================+==============+==============+==================+==================+==================+
| Architecture Arm        | WorldPass    | Global FDAR  | Cond. Auth FDAR  | Cond. Ambig FDAR | SAC / UPR        |
+=========================+==============+==============+==================+==================+==================+
| A0: Top-1 Blind Write   | 58.3% (70)   | 71.4% (60/84)| 100.0% (48/48)   | 100.0% (12/12)   | 100% / 0%        |
| A1: Canonicalize Only   | 58.3% (70)   | 71.4% (60/84)| 100.0% (48/48)   | 100.0% (12/12)   | 100% / 0%        |
| A2: Candidate-Aware     | 75.0% (90)   | 42.9% (36/84)| 100.0% (36/36)   | 0.0% (0/12)      | 100% / 100%      |
| A3: Authority-Aware     | 91.7% (110)  | 14.3% (12/84)| 0.0% (0/48)      | 100.0% (12/12)   | 100% / 0%        |
| A4: Full GENE Ingress   | 100.0% (120) | 0.0% (0/84)  | 0.0% (0/48)      | 0.0% (0/12)      | 100% / 100%      |
+=========================+==============+==============+==================+==================+==================+
```

---

## 3. Privilege-Path Closure & Lifecycle Verification Architecture

### 3.1 Principal-Bound Capabilities vs Untrusted Claimed Roles
- `CapabilityPolicyRegistry` is keyed strictly by `AuthenticatedOrigin.verified_id` (or principal role bindings within the kernel).
- Textually `ClaimedOrigin.claimed_role` is treated as untrusted metadata. A sensor claiming `claimed_role="admin"` in its raw text payload is strictly evaluated under its authenticated sensor capability.

### 3.2 Epistemic Independence Decoupling
$$\text{OriginIdentity} \not\equiv \text{DerivationLineage} \not\equiv \text{IndependenceClass}$$
- Authenticated identity does not imply epistemic independence (multiple sensors can be controlled by a single operator).
- `LineageIndependenceRegistry` maps verified origins to defensible independence classes; unmapped origins default to explicit unverified classes (`ROOT_UNVERIFIED_INDEPENDENCE_*`), preventing lineage laundering.

### 3.3 Standalone `CertificateVerifier`
- Removed caller-supplied `trusted_context` from `CertificateVerifier.verify()`.
- The verifier independently derives `TrustedSourceContext` from platform records, preventing adversary-supplied contexts from bypassing admission checks.
- Programmatic combinatorial mutation matrix tests 7 distinct mutation vectors across all observation/certificate fields with 100% fail-closed rejection.

### 3.4 Proof-Carrying Lifecycle Operations
- **`resolve_deferred_binding()`**: Requires a `ResolutionCertificate` and `disambiguating_record`. Verifies that the resolved entity $\in \mathcal{B}_{\text{original}}(x)$ (candidate set containment) and preserves original sensor capture roots.
- **`promote_provisional_entity()`**: Requires a `PromotionCertificate` and `promotion_authority_record`. Verifies that the promoter possesses `CANONICAL_ONTOLOGY_ADMIN`, rejects collisions with existing canonical IDs, rejects promotion of relations originating from `ATTESTATION_ONLY` sources, and retargets provisional relations atomically.
- **Dual Novelty Support**: Correctly handles relations where both subject and object are novel (`NovelA related_to NovelB`), materializing two `ProvisionalEntity` instances and a dual-provisional relation.

---

## 4. Probe-Separation Assay & Downstream Mechanism Independence

To confirm that the four downstream evaluation probes ($Q_1, Q_2, Q_3, Q_4$) represent distinct, non-redundant mechanisms, a dedicated probe-separation assay (`src/gene/benchmarks/ingress_sidecars/probe_separation.py`) was executed:
- **Profile $(1, 1, 1, 1)$**: Standard valid admission and entitlement.
- **Profile $(1, 1, 0, 1)$**: Admitted into bitemporal state ($Q_1=1$), entitled in Horn support ($Q_2=1$), but blocked from downstream action governance ($\text{Auth} = 0.0$, $Q_3=0$) due to unverified lineage roots.
- **Profile $(1, 0, 0, 1)$**: Active in state ($Q_1=1$), but unentitled under specific premise challenge query ($Q_2=0$).
- **Profile $(1, 1, 1, 0)$**: Admitted, entitled, authorized, but fails causal source ablation $do(\text{source}_i = 0)$ where all occurrences from that source are retracted ($Q_4=0$).

This confirms that state maintenance, deductive support, lineage governance, and causal provenance operate as independent, decoupled layers.

---

## 5. Verification & Preflight Integrity

- **Automated Tests**: 197 total tests passed (`pytest -v`).
- **Reproducibility Suite**: `scripts/verify_repo.py` verified 100% clean with zero worktree drift.
- **Ledger & Atlas Sync**: `data/claim_ledger.json` and `docs/atlas/data/claims.json` updated with `GENE-C16` pointing to `round7-stage7a2-security-freeze`.
