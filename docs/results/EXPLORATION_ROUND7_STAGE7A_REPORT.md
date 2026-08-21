# Exploration Round 7 Stage 7A Report: Epistemic Privilege Escalation, Lifecycle Security, and Formal Ingress Architecture

**Document Status**: Canonical Empirical Report (Stage 7A Ingress Architecture & Security Validation)  
**Author**: Antigravity Research / GENE Core  
**Associated Target Commit**: `round7-stage7a3-final-closure`  
**Prerequisites**: Exploration Round 7 Wave 0.2 Freeze ([`round7-wave0-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round7-wave0-freeze))  
**Primary Artifacts**:
1. [`data/exploration_round7_stage7a_benchmark_summary.json`](../../data/exploration_round7_stage7a_benchmark_summary.json) (`SHA-256: 93dd421f900f29c9fbec3dc95a601bcd446afb2c2074139d0ffdaec13b529236`)
2. [`data/exploration_round7_stage7a_security_summary.json`](../../data/exploration_round7_stage7a_security_summary.json) (`SHA-256: 18081edff907bfc8725f00c818de4b90a589b444d59896f8d3da574ad77c1c43`)

---

## 1. Executive Summary & Epistemic Privilege Escalation

Exploration Round 7 investigates the fundamental boundary condition of durable epistemic storage: **what earns the right to enter epistemic memory in the first place?**

Stage 7A establishes the **Epistemic Privilege Escalation Principle**:
> Persistent epistemic systems do not merely decide admission once at ingress. Rather, information repeatedly ascends through distinct privilege tiers over its operational lifecycle:
> $$\text{Raw Record} \xrightarrow{\text{admission}} \text{Candidate / Deferred} \xrightarrow{\text{resolution}} \text{Admitted Fact} \xrightarrow{\text{promotion}} \text{Canonical Entity} \xrightarrow{\text{governance}} \text{Actionable Belief}$$
> Every transition increases what the information is authorized to effectuate. Therefore:
> $$\text{Admission Integrity} \not\equiv \text{Resolution Integrity} \not\equiv \text{Promotion Integrity}$$

---

## 2. Core Architectural Discoveries & Ingress Benchmark Results

### 2.1 The Orthogonality of Referential and Authorization Correctness
$$\text{Referential Correctness} \perp \text{Authorization Correctness}$$

Stage 7A proves that referential ambiguity preservation and authorization gating address orthogonal failure classes:
1. **Candidate Preservation Alone (`A2`)**: Eliminates candidate ambiguity and novelty collapse ($\text{UPR} = 100.0\%$, $\text{FDAR}_{\text{ambiguity}} = 0.0\%$, $\text{FDAR}_{\text{novel}} = 0.0\%$), but suffers $100.0\%$ False Durable Admission on resolved unauthorized claims ($\text{FDAR}_{\text{authority}\mid\text{resolved}} = 36/36 = 100.0\%$).
2. **Authority Gating Alone (`A3`)**: Eliminates unauthorized root promotions ($\text{FDAR}_{\text{authority}} = 0.0\%$), but prematurely collapses $100.0\%$ of authorized candidate collisions to Top-1 ($\text{FDAR}_{\text{ambiguity}\mid\text{authorized}} = 12/12 = 100.0\%$, $\text{UPR} = 0.0\%$).
3. **Full Proof-Carrying Ingress (`A4`)**: Unifies hypothesis preservation ($\mathcal{B}(x) = \{b_1, \dots, b_k\}$ under `DEFERRED_BINDING`), `PROVISIONAL_ENTITY` tracking, capability-scoped authorization, and standalone certificate verification, achieving $\mathbf{100.0\% \text{ WorldPass}}$, $\mathbf{\text{FDAR} = 0.0\%}$, $\mathbf{\text{SAC} = 100.0\%}$, and $\mathbf{\text{UPR} = 100.0\%}$.

```
+================================================================================================================+
|                       STAGE 7A FACTORIAL INGRESS BENCHMARK (N=120 WORLDS / 480 PROBES)                         |
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

## 3. Privilege-Lifecycle Security Architecture & Invariants

### 3.1 Principal-Bound Capabilities vs Untrusted Claimed Roles
`CapabilityPolicyRegistry` is keyed strictly by `AuthenticatedOrigin.verified_id` (or verified principal role bindings within the platform kernel). Textually `ClaimedOrigin.claimed_role` is treated as untrusted metadata. Disambiguation privilege is fail-closed (`can_disambiguate: bool = False` by default).

### 3.2 Strict Fail-Closed Epistemic Independence
$$\text{OriginIdentity} \not\equiv \text{DerivationLineage} \not\equiv \text{IndependenceClass}$$
- Authenticated identity does not establish epistemic independence.
- `derive_trusted_source_context()` derives independence strictly from `LineageIndependenceRegistry`.
- If unmapped or if the registry is absent, independence class strictly defaults to `ROOT_UNKNOWN_INDEPENDENCE_*` (never reconstructed from identity), eliminating lineage laundering.

### 3.3 Standalone `CertificateVerifier` & Full-Proof Verification
- The verifier re-derives `TrustedSourceContext` internally; external callers cannot inject forged trusted contexts.
- **`verify_resolution()`**: Cross-checks all `ResolutionCertificate` fields, verifies candidate set containment ($\text{chosen} \in \mathcal{B}_{\text{original}}(x)$), checks predicate-level disambiguation authority (`can_disambiguate`), and verifies that certificate lineage roots match the original source record.
- **`verify_promotion()`**: Cross-checks all `PromotionCertificate` fields, enforces `is_ontology_admin=True`, verifies absence of canonical entity ID collisions in the ontology, and rejects promotion of relations originating from `ATTESTATION_ONLY` sources.

### 3.4 Dual-Novel Status Laundering Prevention
When promoting provisional entity $A$ in relation $(A, \text{pred}, B)$ where $B$ remains provisional:
- The relation is retargeted to $(\text{canonical}_A, \text{pred}, B)$ and **kept provisional**.
- Zero authoritative `BitemporalFact` instances are emitted.
- The relation migrates to an authoritative `BitemporalFact` **only when all endpoints become canonical**.

---

## 4. Downstream Mechanism Decoupling & Probe Separation Assay

To confirm that the four downstream evaluation probes ($Q_1, Q_2, Q_3, Q_4$) represent distinct, non-redundant mechanisms, an 8-world assay ([`src/gene/benchmarks/ingress_sidecars/probe_separation.py`](../../src/gene/benchmarks/ingress_sidecars/probe_separation.py)) separates raw epistemic state vectors $(A, E, G, C)$ from behavioral probe correctness $(Q_1, Q_2, Q_3, Q_4)$:

- **`W1_FULL_PASS`**: Raw $(1, 1, 1, 1)$, Correctness $(1, 1, 1, 1)$ — Standard valid admission, supported, authorized, robust.
- **`W2_ACTION_GOVERNANCE_BLOCKED`**: Raw $(1, 1, 0, 1)$, Correctness $(1, 1, 1, 1)$ — Active in state ($A=1$), entitled in Horn support ($E=1$), but action governance blocked ($G=0$) due to unverified lineage roots (`ROOT_UNKNOWN_INDEPENDENCE`). Correctness vector is $(1, 1, 1, 1)$ because blocking unverified roots is the normative policy.
- **`W3_PREMISE_CHALLENGE_FAILED`**: Raw $(1, 0, 0, 1)$, Correctness $(1, 1, 1, 1)$ — Active in state ($A=1$), but queried challenge triple is unentitled ($E=0, G=0$).
- **`W4_CAUSAL_SOURCE_ABLATION_VULNERABLE`**: Raw $(1, 1, 1, 0)$, Correctness $(1, 1, 1, 1)$ — Admitted, supported, authorized, but under exact causal source ablation $do(\text{source}=0)$ via `what_if_source_t("sensor_trusted_a")`, all supporting occurrences are retracted, losing entitlement ($C=0$).
- **`W5_MULTISOURCE_REDUNDANT_RESCUE`**: Raw $(1, 1, 1, 1)$, Correctness $(1, 1, 1, 1)$ — Multi-source redundant derivation: ablating source A leaves independent source B support intact ($C=1$).
- **`W6_DISPUTE_ISOLATION`**: Raw $(0, 0, 0, 0)$, Correctness $(1, 1, 1, 1)$ — Single cardinality contemporaneous dispute triggers cautious isolation.
- **`W7_UNAUTHENTICATED_REJECT`**: Raw $(0, 0, 0, 0)$, Correctness $(1, 1, 1, 1)$ — Unauthenticated assertion rejected fail-closed.
- **`W8_OUT_OF_SCOPE_REJECT`**: Raw $(0, 0, 0, 0)$, Correctness $(1, 1, 1, 1)$ — Out-of-scope assertion rejected.

---

## 5. Programmatic Multi-Family Adversarial Mutation Suite

Adversarial mutation suites test fail-closed rejection across all lifecycle certificate fields:
- **`AdmissionCertificate` (7 vectors)**: Mutated predicate, $t_k$ spoofing, out-of-hypothesis subject, out-of-hypothesis object, forged roots, empty witness, valid interval mismatch.
- **`ResolutionCertificate` (4 vectors)**: Out-of-candidate subject, mismatched record ID, forged lineage roots, empty resolution witness.
- **`PromotionCertificate` (3 vectors)**: Canonical ID collision, mismatched authority record ID, empty authority witness.
- **Result**: $\mathbf{14/14 \text{ attack vectors (100.0\%) fail closed}}$ with descriptive error witnesses.

---

## 6. Preflight Verification & Canonical Audit

- **Automated Tests**: 203 passing tests (`pytest -v`).
- **Reproducibility Suite**: `scripts/verify_repo.py` verified 100% clean with zero worktree drift.
- **Ledger & Atlas Sync**: `data/claim_ledger.json` and `docs/atlas/data/claims.json` bind both `exploration_round7_stage7a_benchmark_summary.json` and `exploration_round7_stage7a_security_summary.json` under `GENE-C16`.
