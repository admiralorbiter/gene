# GENE Exploration Round 5 — Stage 5B Results Report
### *Action Governance Under Change: What Surviving Support Structure is Minimally Necessary to Modulate Action Authority?*

**Execution Date:** 2026-08-20  
**Evidence Class:** `deterministic_zero_live_llm`  
**Execution Freeze Git Tag:** `round5-stage5b-freeze`  
**Total Evaluated Scenarios:** **368 cases**  
**Case Ledger:** `data/exploration_round5_stage5b_cases.jsonl` (`SHA256: 12701a7ca30437e7ff700751e87e16f6e2891d6787a98aff10d63999bf4a8cc8`)  
**Summary JSON:** `data/exploration_round5_stage5b_summary.json` (`SHA256: 3851b79f5c88d71db15da7ed87100838cee5730395f9531283fad104aa98e446`)  

---

## 1. Executive Summary & Core Research Findings

Stage 5B answered the central governance question: **What information about surviving support is minimally necessary to govern action authority under change?**

Rather than prematurely assuming that scalar cut-set $\kappa(c)$ or the tuple $\rho(c) = (|S|, \kappa)$ is sufficient, Stage 5B evaluated 4 candidate policies against **7 formal axiomatic invariants**:

```
                        AXIOMATIC COMPLIANCE SCORECARD (7 FORMAL INVARIANTS)
                        
┌──────────────────────────────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────┐
│ Governance Policy            │ Ax 1 │ Ax 2 │ Ax 3 │ Ax 4 │ Ax 5 │ Ax 6 │ Ax 7 │ Score │
├──────────────────────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼───────┤
│ P_binary (Binary Entitlement) │ PASS │ PASS │ FAIL │ PASS │ PASS │ FAIL │ PASS │ 5/7   │
│ P_kappa (Scalar Cut-Set)     │ PASS │ PASS │ FAIL │ PASS │ PASS │ FAIL │ PASS │ 5/7   │
│ P_rho (Tuple Resilience)     │ PASS │ PASS │ PASS │ PASS │ PASS │ FAIL │ PASS │ 6/7   │
│ P_geom (Lineage Geometry)    │ PASS │ PASS │ PASS │ PASS │ PASS │ PASS │ PASS │ 7/7   │
└──────────────────────────────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴───────┘
  Ax 1: Monotonicity under Invalidation       Ax 5: Bloat Invariance (E_S > 0)
  Ax 2: Zero on Retraction (Ent* = 0 => 0.0)  Ax 6: Lineage Independence Discounting
  Ax 3: Degradation Sensitivity               Ax 7: Isomorphism Invariance
  Ax 4: No Duplication Inflation
```

### Core Empirical Discoveries:
1. **$\mathcal{P}_{\text{binary}}$ Fails Graceful Degradation:** Permits **100% of degraded beliefs (104/104)** to execute high-risk actions at full authority ($1.000$), completely blind to damaged support.
2. **$\mathcal{P}_{\kappa}$ Fails Shared-Root Degradation:** In shared-root topologies ($(2,1) \to (1,1)$), $\kappa$ stays constant ($1 \to 1$), so scalar cut-set authority fails to throttle actions when alternative support is lost.
3. **$\mathcal{P}_{\rho}$ Resolves Degradation but Fails Lineage:** Captures $(2,1) \to (1,1)$ via path count drop ($|S|: 2 \to 1$), but treats correlated single-root alternative paths identically to independent multi-root paths.
4. **$\mathcal{P}_{\text{geom}}$ Achieves Full Axiomatic Compliance (7/7):** Modulates authority by cut sets ($\kappa$), structural path length weights ($\omega$), and ancestral lineage root diversity ($\delta_{\text{root}}$), achieving **100% axiomatic compliance**.

---

## 2. Degraded-State Action Gating Comparison ($N = 104$ Cases)

Under a standard irreversible action gating threshold ($\tau = 0.5$):

```
                        ACTION GATING ON DAMAGED-BUT-ENTITLED STATES
                        
┌──────────────────────────────┬──────────────────────────────┬────────────────────────┐
│ Governance Policy            │ Actions Permitted (tau >= 0.5│ Mean Degraded Authority│
├──────────────────────────────┼──────────────────────────────┼────────────────────────┤
│ P_binary (Binary Entitlement) │ 104 / 104 (100.0%)           │ 1.000                  │
│ P_kappa (Scalar Cut-Set)     │ 104 / 104 (100.0%)           │ 0.538                  │
│ P_rho (Tuple Resilience)     │ 44 / 104 (42.3%)             │ 0.481                  │
│ P_geom (Lineage Geometry)    │ 94 / 104 (90.4%)             │ 0.579                  │
└──────────────────────────────┴──────────────────────────────┴────────────────────────┘
```

---

## 3. The Seven Formal Axioms & Policy Counterexamples

1. **Axiom 1 (Monotonicity):** $I_1 \subseteq I_2 \implies \text{Auth}(c, I_2) \le \text{Auth}(c, I_1)$. (All 4 policies PASS).
2. **Axiom 2 (Zero on Retraction):** $\text{Ent}^*(c, I) = 0 \implies \text{Auth}(c, I) = 0.0$. (All 4 policies PASS).
3. **Axiom 3 (Degradation Sensitivity):** $\text{Status} = \text{DEGRADED} \implies 0 < \text{Auth} < \text{Auth}_{\text{unchanged}}$.
   - $\mathcal{P}_{\text{binary}}$ FAILS ($\text{Auth} = 1.0$).
   - $\mathcal{P}_{\kappa}$ FAILS on $(2,1) \to (1,1)$ ($\kappa = 1 \to 1 \implies \text{Auth} = 1.0$).
   - $\mathcal{P}_{\rho}$ and $\mathcal{P}_{\text{geom}}$ PASS.
4. **Axiom 4 (No Duplication Inflation):** Duplicate citations cannot manufacture authority. (All 4 policies PASS due to minimal hypergraph normalization).
5. **Axiom 5 (Bloat Invariance):** Explanatory bloat $E_S > 0$ does not change authority. (All 4 policies PASS).
6. **Axiom 6 (Lineage Independence Discounting):** Alternative paths sharing a single root must receive strictly lower authority than multi-root independent paths.
   - $\mathcal{P}_{\text{binary}}, \mathcal{P}_{\kappa}, \mathcal{P}_{\rho}$ all FAIL (blind to root overlap).
   - $\mathcal{P}_{\text{geom}}$ PASSES ($\text{Auth}_{\text{single-root}} = 0.850 < \text{Auth}_{\text{multi-root}} = 1.000$).
7. **Axiom 7 (Isomorphism Invariance):** Graph isomorphism preserves exact authority. (All 4 policies PASS).

---

## 4. Artifact & Provenance Record

- **Case Ledger (JSONL):** `data/exploration_round5_stage5b_cases.jsonl` (`SHA256: 12701a7ca30437e7ff700751e87e16f6e2891d6787a98aff10d63999bf4a8cc8`)
- **Summary Statistics:** `data/exploration_round5_stage5b_summary.json` (`SHA256: 3851b79f5c88d71db15da7ed87100838cee5730395f9531283fad104aa98e446`)
- **Unit & Property Tests:** `tests/explore_round5/test_action_governance.py` (4/4 passing)
- **Zero Live LLM Compute:** Pure deterministic axiomatic characterization.
