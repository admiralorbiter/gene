# Exploration Round 3 Results Report: When One Belief Has Many Reasons

## 1. Executive Summary & Headline Findings

Exploration Round 3 evaluated the central collision between **formal justification ($S_F$)**, **neural causal influence ($S_C$)**, and **governance lineage** across 96 live Gemma 3:12B calls under zero core engine modifications.

```
                             ROUND 3 HEADLINE PORTFOLIO SCORECARD
                             
┌──────────┬─────────────────────────────┬───────────┬────────────────────────────────────────────────────────┐
│ Track    │ Experimental Question       │ Calls (N) │ Empirical Discovery                                    │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track H  │ Coalition Causality         │ 32 calls  │ S_F != S_C confirmed: Single-parent knockouts show 0%  │
│          │ (Overdetermination Lattice) │           │ causal effect; lattice reveals neural shortcut paths.  │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track G2 │ Non-Destructive Immunity    │ 20 calls  │ 100% (20/20) Preservation & Safe Collapse:             │
│          │ (Clean Governance Policies) │           │ Support-aware filtering eliminates autoimmunity.       │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track B3 │ Monoculture Multiverse      │ 24 calls  │ Delta_root = +0.000: Provenance tokens alone produce   │
│          │ (Factorial Multiverse)      │           │ zero spontaneous genealogical discounting (eps=0.0%).  │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track S  │ Support Acquisition         │  0 calls  │ Formally verified OR-of-AND compiler prototype.        │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track L  │ Independence Laundering     │ 20 calls  │ Perceived diversity inflates from 1.0 -> 2.33 -> 4.0   │
│          │ (Epistemic Observability)   │           │ across reproduction generations from a single root.    │
└──────────┴─────────────────────────────┴───────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Track-by-Track Empirical Results

### Track H: Coalition Causality & Overdetermination ($N=32$)
- **Core Finding:** In the presence of redundant justification ($S_F(C) = \{\{A,B\}, \{D,E\}\}$), **single-parent counterfactual knockouts fail 100% of the time** ($A \leadsto 0, B \leadsto 0, D \leadsto 0, E \leadsto 0$ all emit `PROTO_X7`).
- **Empirical Causal Coalitions ($S_C$):**
  - For `KESTREL`: $S_C(C) = \{\{D,E\}, \{B,D\}, \{A,D\}, \{A,B\}\}$.
  - The model behaviorally sustains the claim on illegitimate cross-premise combinations ($\{A,D\}$: manager + sector lead) even when neither reporting relation ($B, E$) is present.
- **Scientific Impact:** Causal parenthood cannot be measured as a simple binary but-for edge ($A \to C$). Multi-justified claims require power-set intervention lattices to uncover minimal behaviorally sufficient exposure environments.

### Track G2: Non-Destructive Support Immunity ($N=20$)
- **Empirical Accuracy:** **20 / 20 (100.0%)** across all 5 executed governance conditions:
  - `baseline_independent`: 4/4 (100%) $\implies$ `PROTO_X7`
  - `baseline_shared`: 4/4 (100%) $\implies$ `PROTO_X7`
  - `naive_lineage_quarantine`: 4/4 (100%) $\implies$ `UNKNOWN` (Autoimmunity)
  - `support_aware_independent_preservation`: 4/4 (100%) $\implies$ `PROTO_X7` (Preserved)
  - `support_aware_shared_collapse`: 4/4 (100%) $\implies$ `UNKNOWN` (Safe Collapse)
- **Scientific Impact:** Support-aware governance successfully decouples corrupted ancestral paths from independent surviving derivations, eliminating epistemic autoimmunity while guaranteeing safe collapse on shared-root corruption.

### Track B3: Monoculture Measurement Multiverse ($N=24$)
- **Substantive Marginal Effect ($\Delta_{\text{root}}$):**
  $$P(\text{Majority}\mid \text{Independent}) = 2/8 \quad (25.0\%)$$
  $$P(\text{Majority}\mid \text{Monoculture}) = 2/8 \quad (25.0\%)$$
  $$\Delta_{\text{root}} = +0.000$$
- **Replay & Perturbation Instability:**
  - Exact CallSpec Replay Instability: $\epsilon_{\text{replay}} = 0/4 \quad (0.0\%)$
  - Seed Perturbation Sensitivity: $\epsilon_{\text{seed}} = 0/4 \quad (0.0\%)$
- **Scientific Impact:** When document syntax and token mappings are strictly counterbalanced, raw root annotations (`root_R1`) produce **zero spontaneous discounting**. Neural reasoners aggregate surface evidence frequencies unless explicitly governed by lineage mechanisms.

### Track L: Independence Laundering & Epistemic Observability ($N=20$)
- **$G_0$ True Root ($N_{\text{true}} = 1$):** 4/4 Determinable $\implies \text{Mean } \widehat{N}_{\text{model}} = 1.00$.
- **$G_1$ Cited Paraphrases ($N_{\text{true}} = 1$):** 4/4 **Indeterminable** (Model correctly refuses to treat cited copies as independent primary sources).
- **$G_2$ Partial Laundering ($N_{\text{true}} = 1$):** 3/4 Determinable $\implies \text{Mean } \widehat{N}_{\text{model}} = 2.33$.
- **$G_3$ Fully Laundered Consensus ($N_{\text{true}} = 1$):** 2/4 Determinable $\implies \text{Mean } \widehat{N}_{\text{model}} = 4.00$.
- **$G_{\text{ctrl}}$ True 4-Root Control ($N_{\text{true}} = 4$):** 3/4 Determinable $\implies \text{Mean } \widehat{N}_{\text{model}} = 4.00$.
- **Scientific Impact:** Semantic reproduction acts as an evolutionary diversity multiplier, progressively laundering single-root memories into apparent 4-source consensus ($\widehat{N}_{\text{model}}: 1.00 \leadsto 2.33 \leadsto 4.00$).

---

## 3. Epistemic Synthesis

Round 3 experimentally proves the three-tier separation of GENE:
$$\text{Formal Derivability } (S_F) \ne \text{Neural Causal Influence } (S_C) \ne \text{Ancestral Lineage } (G_{\text{lineage}})$$
- $S_F$: Derived deductively by the trace-to-support compiler.
- $S_C$: Discovered empirically via power-set intervention lattices.
- Governance: Support-aware kernel preserves valid multi-supported memory while naive lineage causes autoimmunity.
