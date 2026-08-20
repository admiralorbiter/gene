# Exploration Round 3 Results Report: When One Belief Has Many Reasons

## 1. Executive Summary & Post-Review Portfolio Scorecard

Exploration Round 3 evaluated the operational relationships between **formal justification ($S_F$)**, **behaviorally sufficient exposure environments ($S_C$)**, and **governance lineage ($G_{\text{lineage}}$)** across 96 live Gemma 3:12B calls under zero core engine modifications.

```
                               ROUND 3 POST-REVIEW PORTFOLIO SCORECARD
                               
┌──────────┬─────────────────────────────┬───────────┬───────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Track    │ Experimental Focus          │ Calls (N) │ Post-Review Classification        │ Key Empirical Observation                              │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track H  │ Coalition Causality         │ 32 calls  │ PROMISING DISCOVERY —             │ Full 16-pt lattice exposes shortcut coalitions         │
│          │ (Overdetermination Lattice) │           │ ROLE REPLICATION REQUIRED         │ (S_C != S_F) with context-dependent non-monotonicity.   │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track G2 │ Non-Destructive Immunity    │ 20 calls  │ VALIDATED SYNTHETIC MECHANISM     │ 20/20 behavioral compatibility: support-aware filter   │
│          │ (Clean Governance Policies) │           │                                   │ retains unaffected paths & collapses shared roots.     │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track B3 │ Monoculture Multiverse      │ 24 calls  │ CLEAN NULL SIGNAL —               │ Delta_root = +0.000; conflict abstention governed      │
│          │ (Factorial Multiverse)      │           │ NO ROOT-TOKEN EFFECT              │ 100% by document ordering (Delta_order = +1.000).      │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track S  │ Support Acquisition         │  0 calls  │ VALIDATED FORMAL PROTOTYPE        │ Formally verified OR-of-AND trace compiler prototype.  │
├──────────┼─────────────────────────────┼───────────┼───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Track L  │ Independence Laundering     │ 20 calls  │ PROMISING MIXED PHENOTYPE —       │ Provenance loss triggers 50/50 bifurcation between     │
│          │ (Epistemic Observability)   │           │ BIFURCATION & RESISTANCE          │ false 4-source certainty and epistemic resistance.     │
└──────────┴─────────────────────────────┴───────────┴───────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Track-by-Track Empirical Post-Mortem

### Track H: Coalition Causality & Overdetermination ($N=32$)
- **Formal Target:** Recombinant support $S_F(C) = \{\{A,B\}, \{D,E\}\}$ where $A=\text{manager}, B=\text{reports\_to}(S1), D=\text{sector\_lead}, E=\text{reports\_to}(S2)$.
- **Empirical Findings Across Dual Station Ecologies:**

```
                            COMPLETE 16-POINT LATTICE OBSERVATIONS
                            
┌────────────────────┬────────────────────┬──────────────────────┬──────────────────────┬─────────────────┐
│ Active Premise Set │ Knocked Out Set    │ VELORA Emitted       │ KESTREL Emitted      │ Formal Expected │
├────────────────────┼────────────────────┼──────────────────────┼──────────────────────┼─────────────────┤
│ Ø (0 premises)     │ {A, B, D, E}       │ UNKNOWN              │ UNKNOWN              │ UNKNOWN         │
│ {A}                │ {B, D, E}          │ UNKNOWN              │ UNKNOWN              │ UNKNOWN         │
│ {B}                │ {A, D, E}          │ UNKNOWN              │ UNKNOWN              │ UNKNOWN         │
│ {D}                │ {A, B, E}          │ UNKNOWN              │ UNKNOWN              │ UNKNOWN         │
│ {E}                │ {A, B, D}          │ PROTO_X7 (Shortcut!) │ UNKNOWN              │ UNKNOWN         │
│ {A, B}             │ {D, E}             │ PROTO_X7             │ PROTO_X7             │ PROTO_X7        │
│ {A, D}             │ {B, E}             │ PROTO_X7 (Shortcut!) │ PROTO_X7 (Shortcut!) │ UNKNOWN         │
│ {A, E}             │ {B, D}             │ UNKNOWN              │ UNKNOWN              │ UNKNOWN         │
│ {B, D}             │ {A, E}             │ PROTO_X7 (Shortcut!) │ PROTO_X7 (Shortcut!) │ UNKNOWN         │
│ {B, E}             │ {A, D}             │ UNKNOWN              │ UNKNOWN              │ UNKNOWN         │
│ {D, E}             │ {A, B}             │ PROTO_X7             │ PROTO_X7             │ PROTO_X7        │
│ {A, B, D}          │ {E}                │ PROTO_X7             │ PROTO_X7             │ PROTO_X7        │
│ {A, B, E}          │ {D}                │ PROTO_X7             │ PROTO_X7             │ PROTO_X7        │
│ {A, D, E}          │ {B}                │ PROTO_X7             │ PROTO_X7             │ PROTO_X7        │
│ {B, D, E}          │ {A}                │ PROTO_X7             │ PROTO_X7             │ PROTO_X7        │
│ {A, B, D, E}       │ Ø                  │ PROTO_X7             │ PROTO_X7             │ PROTO_X7        │
└────────────────────┴────────────────────┴──────────────────────┴──────────────────────┴─────────────────┘
```

- **Recovered Minimal Behavioral Support ($S_C$):**
  - $\text{VELORA}: S_C = \{\{E\}, \{B,D\}, \{A,D\}, \{A,B\}\}$
  - $\text{KESTREL}: S_C = \{\{D,E\}, \{B,D\}, \{A,D\}, \{A,B\}\}$
- **Key Discoveries:**
  1. **Single-Parent Blindspot (Overdetermination):** All 4 single knockouts ($\{A\}, \{B\}, \{D\}, \{E\}$) left output invariant at `PROTO_X7` in both stations ($P(\text{Target}) = 1.0$). A standard single-parent but-for causal test concludes that none of the premises are causally necessary.
  2. **Divergence of $S_C$ from $S_F$:** The model behaviorally sustains the claim on illegitimate cross-premise combinations ($\{A,D\}$ and $\{B,D\}$) that do not satisfy either formal rule.
  3. **Role Asymmetry ($D = \text{sector\_lead}$):** $D$ appears in 3/4 minimal coalitions in KESTREL. The sector lead role functions as an asymmetric authority cue allowing premature inference.
  4. **Context-Dependent Non-Monotonicity:** In VELORA, $\{E\} \implies \text{PROTO\_X7}$, but adding $A$ or $B$ suppresses the output to `UNKNOWN` (2 non-monotonic regressions). In KESTREL, the landscape is strictly monotonic.

---

### Track G2: Non-Destructive Support Immunity ($N=20$)
- **Two Distinct Components:**
  1. **Deterministic Retained Support Property:** `apply_governance_retrieval()` mathematically preserves unaffected support paths during ancestor revocation while inactivating claims whose paths all share the retracted root.
  2. **Downstream Behavioral Compatibility:** Gemma 3:12B correctly produced the intended output across all 20 policy contexts (**20/20 = 100.0%**):
     - `baseline_independent`: 4/4 (100%) $\implies$ `PROTO_X7`
     - `baseline_shared`: 4/4 (100%) $\implies$ `PROTO_X7`
     - `naive_lineage_quarantine`: 4/4 (100%) $\implies$ `UNKNOWN` (Autoimmunity)
     - `support_aware_independent_preservation`: 4/4 (100%) $\implies$ `PROTO_X7` (Preservation)
     - `support_aware_shared_collapse`: 4/4 (100%) $\implies$ `UNKNOWN` (Safe Collapse)

---

### Track B3: Monoculture Measurement Multiverse ($N=24$)
- **Factorial Decomposition Across 16 Primary Cells:**

```
                               16-CELL FACTORIAL DECOMPOSITION
                               
┌──────────────────┬─────────────────────────────┬───────────────────────────┬──────────────┬───────────────────┐
│ Factor           │ Level 0 (P(Majority))       │ Level 1 (P(Majority))     │ Delta (Maj)  │ Delta (UNKNOWN)   │
├──────────────────┼─────────────────────────────┼───────────────────────────┼──────────────┼───────────────────┤
│ Root Structure   │ Independent: 2/8 (25.0%)    │ Monoculture: 2/8 (25.0%)  │ +0.000       │ +0.000            │
│ Token Mapping    │ M4 Majority: 2/8 (25.0%)    │ Q7 Majority: 2/8 (25.0%)  │ +0.000       │ +0.000            │
│ Document Order   │ Forward: 0/8 (0.0%)         │ Interleaved: 4/8 (50.0%)  │ -0.500       │ +1.000 (100%->0%) │
│ Station Entity   │ VELORA: 2/8 (25.0%)         │ KESTREL: 2/8 (25.0%)      │ +0.000       │ +0.000            │
└──────────────────┴─────────────────────────────┴───────────────────────────┴──────────────┴───────────────────┘
```

- **Replay & Seed Stability:**
  - Exact CallSpec Replay Instability: $\epsilon_{\text{replay}} = 0/4 \quad (0.0\%)$
  - Seed Perturbation Sensitivity: $\epsilon_{\text{seed}} = 0/4 \quad (0.0\%)$
- **Key Takeaway:** Raw root tokens (`root_R1`) produced **zero marginal effect** ($\Delta_{\text{root}} = +0.000$). Instead, document order completely governed conflict behavior: forward clustering of majority documents triggered 100% UNKNOWN abstention, whereas interleaving eliminated abstention (50% majority / 50% minority).

---

### Track L: Independence Laundering & Epistemic Observability ($N=20$)
- **Stage-by-Stage Phenotype Breakdown:**

```
                               STAGE-BY-STAGE OBSERVABILITY BREAKDOWN
                               
┌──────────────────────────────┬────────────┬─────────────────────────────┬────────────────────────┬──────────────────────┐
│ Reproduction Stage           │ True Roots │ Determinable Rate (P(Det))  │ Cond. Mean Sources (N̂) │ Observed Phenotype   │
├──────────────────────────────┼────────────┼─────────────────────────────┼────────────────────────┼──────────────────────┤
│ G0 (True 1-Root Observation) │ 1          │ 4/4 (100.0%)                │ 1.00                   │ Ground Truth Baseline│
│ G1 (4 Cited Paraphrases)     │ 1          │ 0/4 (0.0%)                  │ N/A (4/4 Indeterm.)    │ Strict Abstention    │
│ G2 (Partial Laundering)      │ 1          │ 3/4 (75.0%)                 │ 2.33                   │ Emerging Inflation   │
│ G3 (Fully Laundered Consensus│ 1          │ 2/4 (50.0%)                 │ 4.00                   │ 50/50 Bifurcation    │
│ G_ctrl (True 4-Root Control) │ 4          │ 3/4 (75.0%)                 │ 4.00                   │ True Consensus CTL   │
└──────────────────────────────┴────────────┴─────────────────────────────┴────────────────────────┴──────────────────────┘
```

- **Epistemic Bifurcation at $G_3$:**
  - In `VELORA`: Both runs declared independence **determinable** with $\widehat{N} = 4$ (**False Multi-Source Certainty**).
  - In `KESTREL`: Both runs declared independence **indeterminable** with $\widehat{N} = \text{null}$ (**Epistemic Resistance**).
  - Rather than a uniform inflation curve, provenance loss creates an epistemic fork between manufactured certainty and conservative resistance.

---

## 3. Epistemic Hierarchy Synthesis

Round 3 demonstrates that formal support, behavioral sufficiency, and historical lineage are **operationally distinct objects** that can diverge in multi-agent memory systems:
1. **$S_F(C)$ (Formal Support):** Hypergraph of deductively sufficient root assumption sets.
2. **$S_C(C)$ (Behavioral Exposure Environments):** Minimal sets of visible premises that empirically sustain model output under intervention.
3. **$G_{\text{lineage}}$ (Ancestral History):** Directed acyclic graph of physical generation events and citation edges.

When claims are multiply justified, single-parent lineage interventions cannot detect causal dependency, and neural models may rely on illicit shortcuts outside $S_F(C)$. Support-aware governance resolves this tension by tracking proof paths deterministically rather than relying on neural introspection.
