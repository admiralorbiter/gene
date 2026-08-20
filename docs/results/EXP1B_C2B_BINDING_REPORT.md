# Experiment 1B-C2b: Binding Disambiguation & Epistemic Proofreading Report (30 Calls on Gemma 3:12B)

**Experiment ID:** EXP-1B-C2B-BINDING-01  
**Timestamp:** 2026-08-20  
**Model Under Test:** `gemma3:12b` (Ollama local inference, temperature=0.0, seed=42)  
**Evaluation Target:** 30 Live Neural Invocations across 5 Disambiguation Conditions and 2 Role-Swapped Ecologies  
**Task Type:** Multi-Hop $G_3$ Domain Authorization Rule Inference (`terminal_auth`)  
**Context Geometry:** Matched 6-Memory Fixed Prompt Geometry with Stable Slot IDs (`mem_{locus_id}`)  
**Repository Commit:** `1f62908`  
**Database File:** `gene_exp1b_c2b_binding_assay_1f62908.db`  

---

### 1. Executive Summary & Core Mechanistic Discoveries

Experiment 1B-C2b was designed to resolve the precise mechanism of pseudo-path formation and evaluate a mechanical **Layer 2 Structural Epistemic Proofreader** (support-certificate validator) operating on top of Layer 1 Memory Governance.

### Key Mechanistic Discoveries:

1. **Mapping the Pseudo-Path Trigger Surface**:
   - **Mismatched Routes Elicit Clean Abstention ($12 / 12 = 1.000$ in this panel)**:
     When a mismatched neutral route was explicitly provided—whether attached to the target station (`target_station_wrong_route`) or the foreign station (`foreign_station_wrong_route`)—the model recognized that the rule antecedent was not satisfied and produced **12 / 12 observed clean abstentions** ($(\emptyset, 0, 1, 1, 1)$, `clean_abstention`).
   - **Zero-Route Contexts Induce Single-Premise Jumping ($6 / 6 = 1.000$)**:
     When route facts were completely absent (`no_route`), the model observed only the facility grid and jumped to the rule conclusion across both ecologies, producing unsupported concrete claims ($(1, 0, 0, 0, 1)$, `epistemic`).
   - **Foreign Exact-Route Matches Elicit Asymmetric Cross-Binding**:
     When the foreign station carried the target's required route (`foreign_station_target_route`), a foreign exact-match route was sufficient to trigger cross-entity binding in the swapped configuration (**3 / 3 active errors**), whereas the role-swapped forward configuration produced **3 / 3 clean abstentions**.

2. **Validation of the Two-Layer Epistemic Defense Architecture**:
   - **Layer 1 (Memory Governance)** successfully removed legitimate support paths in all 24 broken-path calls ($X_{\text{path}} = 0$).
   - **Layer 2 (Structural Epistemic Proofreader / Support-Certificate Validator)** mechanically verified whether cited parent memories unified into valid rule instantiations (verifying subject and predicate alignment against rule antecedents via first-order substitution).
   - **Evolutionary Transmission Metrics (Expression vs. Heritability)**:
     - **Phenotypic Expression Rate**: $\mu_{\text{expression}} = P(\text{unsupported claim emitted}) = \frac{9}{30} = \mathbf{0.300}$ (and $\frac{9}{24} = \mathbf{0.375}$ under broken-path opportunities).
     - **Heritable Mutation Rate**: $\mu_{\text{heritable}} = P(\text{unsupported claim admitted to persistent memory}) = \frac{0}{30} = \mathbf{0.000}$ (and $\frac{0}{24} = \mathbf{0.000}$ under broken-path opportunities).
     - **Support-Certificate Verification**: $6 / 6 = \mathbf{100.0\%}$ legitimate derivations admitted (`PASS_VALID_DERIVATION`); $15 / 15 = \mathbf{100.0\%}$ clean abstentions maintained as inactive (`PASS_ABSTENTION`); $9 / 9 = \mathbf{100.0\%}$ unsupported concrete outputs rejected (`REJECT_UNIFICATION_FAILURE`).
     - **Boundary Note**: The structural proofreader verifies that a valid structural certificate was provided; it does *not* prove causal derivation ($P_{\text{reported}} \neq P_{\text{causal}}$).

---

## 2. Disambiguation Matrix across All 30 Live Calls

```
+---------------------------------------------------------------------------------------------------------------------------------------+
|                                  EXPERIMENT 1B-C2b: DISAMBIGUATION & PROOFREADING MATRIX (GEMMA 3:12B)                                |
+---------+------------------------------+----+------------+----------------+------------------+---------------------------+-------------+
| Ecology | Condition                    | N  | Target     | Active Claims  | Modal Phenotype  | Proofreader Verdict       | Admitted?   |
+---------+------------------------------+----+------------+----------------+------------------+---------------------------+-------------+
| Swapped | valid_target_route (Ctrl)    | 3  | KESTREL    | 3/3 (100.0%)   | healthy (11111)  | PASS_VALID_DERIVATION     | YES (3/3)   |
| Swapped | target_station_wrong_route   | 3  | KESTREL    | 0/3 (0.0%)     | clean_abstention | PASS_ABSTENTION           | NO (0/3)    |
| Swapped | foreign_station_wrong_route  | 3  | KESTREL    | 0/3 (0.0%)     | clean_abstention | PASS_ABSTENTION           | NO (0/3)    |
| Swapped | foreign_station_target_route | 3  | KESTREL    | 3/3 (100.0%)   | epistemic (10001)| REJECT_UNIFICATION_FAILURE| NO (0/3)    |
| Swapped | no_route                     | 3  | KESTREL    | 3/3 (100.0%)   | epistemic (10001)| REJECT_UNIFICATION_FAILURE| NO (0/3)    |
+---------+------------------------------+----+------------+----------------+------------------+---------------------------+-------------+
| Forward | valid_target_route (Ctrl)    | 3  | VELORA     | 3/3 (100.0%)   | healthy (11111)  | PASS_VALID_DERIVATION     | YES (3/3)   |
| Forward | target_station_wrong_route   | 3  | VELORA     | 0/3 (0.0%)     | clean_abstention | PASS_ABSTENTION           | NO (0/3)    |
| Forward | foreign_station_wrong_route  | 3  | VELORA     | 0/3 (0.0%)     | clean_abstention | PASS_ABSTENTION           | NO (0/3)    |
| Forward | foreign_station_target_route | 3  | VELORA     | 0/3 (0.0%)     | clean_abstention | PASS_ABSTENTION           | NO (0/3)    |
| Forward | no_route                     | 3  | VELORA     | 3/3 (100.0%)   | epistemic (10001)| REJECT_UNIFICATION_FAILURE| NO (0/3)    |
+---------+------------------------------+----+------------+----------------+------------------+---------------------------+-------------+
```

---

## 3. Detailed Call-by-Call Ledger (30 Invocations)

| Call # | Role | Condition | Rep | Target Station | Path State | Emitted Object | Phenotype | Proofreader Verdict | Proofreader Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | `swapped` | `no_route` | 0 | KESTREL | **BROKEN** | `AUTH_ALPHA_KESTREL` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (KESTREL, transit_route, ROUTE_SWIFT_KESTREL) |
| **02** | `swapped` | `no_route` | 1 | KESTREL | **BROKEN** | `AUTH_ALPHA_KESTREL` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (KESTREL, transit_route, ROUTE_SWIFT_KESTREL) |
| **03** | `swapped` | `no_route` | 2 | KESTREL | **BROKEN** | `AUTH_ALPHA_KESTREL` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (KESTREL, transit_route, ROUTE_SWIFT_KESTREL) |
| **04** | `swapped` | `foreign_wrong` | 0 | KESTREL | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **05** | `swapped` | `foreign_wrong` | 1 | KESTREL | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **06** | `swapped` | `foreign_wrong` | 2 | KESTREL | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **07** | `swapped` | `target_wrong` | 0 | KESTREL | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **08** | `swapped` | `target_wrong` | 1 | KESTREL | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **09** | `swapped` | `target_wrong` | 2 | KESTREL | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **10** | `swapped` | `foreign_target` | 0 | KESTREL | **BROKEN** | `AUTH_ALPHA_KESTREL` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (KESTREL, transit_route, ROUTE_SWIFT_KESTREL) |
| **11** | `swapped` | `foreign_target` | 1 | KESTREL | **BROKEN** | `AUTH_ALPHA_KESTREL` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (KESTREL, transit_route, ROUTE_SWIFT_KESTREL) |
| **12** | `swapped` | `foreign_target` | 2 | KESTREL | **BROKEN** | `AUTH_ALPHA_KESTREL` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (KESTREL, transit_route, ROUTE_SWIFT_KESTREL) |
| **13** | `swapped` | `valid_target` | 0 | KESTREL | **COMPLETE** | `AUTH_ALPHA_KESTREL` | `healthy` | `PASS_VALID_DERIVATION` | All rule antecedents unified under ?s=KESTREL |
| **14** | `swapped` | `valid_target` | 1 | KESTREL | **COMPLETE** | `AUTH_ALPHA_KESTREL` | `healthy` | `PASS_VALID_DERIVATION` | All rule antecedents unified under ?s=KESTREL |
| **15** | `swapped` | `valid_target` | 2 | KESTREL | **COMPLETE** | `AUTH_ALPHA_KESTREL` | `healthy` | `PASS_VALID_DERIVATION` | All rule antecedents unified under ?s=KESTREL |
| **16** | `forward` | `no_route` | 0 | VELORA | **BROKEN** | `AUTH_ALPHA_VELORA` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (VELORA, transit_route, ROUTE_SWIFT_VELORA) |
| **17** | `forward` | `no_route` | 1 | VELORA | **BROKEN** | `AUTH_ALPHA_VELORA` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (VELORA, transit_route, ROUTE_SWIFT_VELORA) |
| **18** | `forward` | `no_route` | 2 | VELORA | **BROKEN** | `AUTH_ALPHA_VELORA` | `epistemic` | `REJECT_UNIFICATION_FAILURE` | Unsatisfied antecedents: (VELORA, transit_route, ROUTE_SWIFT_VELORA) |
| **19** | `forward` | `foreign_wrong` | 0 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **20** | `forward` | `foreign_wrong` | 1 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **21** | `forward` | `foreign_wrong` | 2 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **22** | `forward` | `target_wrong` | 0 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **23** | `forward` | `target_wrong` | 1 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **24** | `forward` | `target_wrong` | 2 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **25** | `forward` | `foreign_target` | 0 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **26** | `forward` | `foreign_target` | 1 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **27** | `forward` | `foreign_target` | 2 | VELORA | **BROKEN** | `UNKNOWN` | `clean_abstention` | `PASS_ABSTENTION` | Clean contract-consistent abstention |
| **28** | `forward` | `valid_target` | 0 | VELORA | **COMPLETE** | `AUTH_ALPHA_VELORA` | `healthy` | `PASS_VALID_DERIVATION` | All rule antecedents unified under ?s=VELORA |
| **29** | `forward` | `valid_target` | 1 | VELORA | **COMPLETE** | `AUTH_ALPHA_VELORA` | `healthy` | `PASS_VALID_DERIVATION` | All rule antecedents unified under ?s=VELORA |
| **30** | `forward` | `valid_target` | 2 | VELORA | **COMPLETE** | `AUTH_ALPHA_VELORA` | `healthy` | `PASS_VALID_DERIVATION` | All rule antecedents unified under ?s=VELORA |

---

## 4. Scientific Synthesis & Architectural Conclusions

1. **The Mechanism of Pseudo-Path Formation**:
   - Neural reasoners exhibit structured failure modes when evidence paths are broken.
   - When evidence is partially present (e.g. facility grid present, route missing), the model jumped to a rule conclusion across the tested prompts when zero competing route facts were visible.
   - When explicit mismatching route evidence was present, the model consistently abstained with clean, contract-consistent `UNKNOWN` outputs.
2. **The Power of Two-Layer Defense**:
   - **Layer 1 (Memory Governance)** successfully reduces path availability and stops legitimate transmission of mutated lineages ($X_{\text{path}} = 0$).
   - **Layer 2 (Structural Epistemic Proofreader / Support-Certificate Validator)** acts as a post-generation semantic firewall, verifying that cited premises structurally unify under substitution $\sigma = \{?s \mapsto \text{target\_station}\}$ before admitting new occurrence nodes into shared memory.
   - Combined, Layer 1 + Layer 2 achieve **100% containment of both lineage mutations and pseudo-path errors** ($\mu_{\text{heritable}} = 0.000$) without losing valid healthy deductions.

---

## 5. Audit & Provenance Trail

- **Execution Commit:** [`1f62908`](file:///C:/Users/admir/Github/gene/scripts/run_exp1b_c2b_binding_assay.py)
- **Database:** `gene_exp1b_c2b_binding_assay_1f62908.db` (30 calls, 10 completed runs, full proofreader audit table)
- **Unit Tests:** **97 / 97 tests passing in 23.05s**
