# Experiment Card — Track M: Support-Preserving Monotonicity & Fragility

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** In Exploration Round 3 Track H (VELORA), adding valid non-contradictory evidence to an active premise produced non-monotonic collapse ($\{E\} \implies \text{PROTO\_X7}$, but $\{A,E\} \implies \text{UNKNOWN}$). While $\{E\}$ was an ungrounded shortcut, this exposes that neural reasoning can experience **Success-to-Error Transitions** when epistemically compatible evidence is appended.
- **Monotonic Scaffolding Contract:** If a target claim is formally entitled under minimal support environment $S_1 = \{A,B\}$, adding formally compatible premise augments ($+D, +E$) must not degrade model accuracy or trigger false abstention.

## 2. Experimental Design & Augmentation Chains
Starting from minimal valid support:
- Step 0: Minimal Support Base $\{A,B\} \implies \text{Expected: PROTO\_X7}$
- Step 1: Augment $+D$ (Add sector_lead) $\implies \{A,B,D\} \implies \text{Expected: PROTO\_X7}$
- Step 2: Augment $+E$ (Add reports_to_S2) $\implies \{A,B,D,E\} \implies \text{Expected: PROTO\_X7}$
- Step 3: Augment $+F$ (Add irrelevant neutral distractor) $\implies \{A,B,D,E,F\} \implies \text{Expected: PROTO\_X7}$

## 3. Measurable Endpoints & Analysis
- **Success-to-Error Transition Rate ($R_{\text{S}\to\text{E}}$):** Frequency with which adding compatible evidence turns a correct answer into an incorrect output or abstention.
- **Monotonicity Preservation Score:** Proportion of augmentation chains that remain strictly monotonic.
