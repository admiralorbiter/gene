# Experiment Card — Track M: Support-Preserving Monotonicity & Fragility

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** In Exploration Round 3 Track H (VELORA), appending evidence produced non-monotonic collapse ($\{E\} \implies \text{PROTO\_X7}$, but adding $A \implies \{A,E\} \implies \text{UNKNOWN}$). While $\{E\}$ was an illicit shortcut, this reveals that neural inference can experience **Success-to-Error Transitions ($S \to E$)** when epistemically compatible evidence is appended.
- **Formal Support-Preserving Augmentation:** Unlike generic prompt lengthening, GENE defines a precise semantic contract: If target claim $c$ is formally entitled under minimal support environment $S_1 = \{A,B\}$, sequentially adding valid, non-contradictory premise augments ($+D, +E, +F_{\text{distractor}}$) **must preserve formal entitlement** ($S_F(c) \ne \emptyset$).
- **Positional & Path Counterbalancing:**
  - To prevent presentation-order effects (from Round 3 B3) from confounding the additive information effect, we test both insertion orders (append at end vs prepend at start).
  - We mirror the augmentation chains symmetrically from both minimal proof paths ($S_1 = \{A,B\}$ and $S_2 = \{D,E\}$).

## 2. Experimental Chains & Counterbalanced Panels

### Chain 1 (Originating at Path AB):
- Step 0: Minimal Base $\{A,B\} \implies \text{Expected: PROTO\_X7}$
- Step 1: Augment $+D$ (Add sector_lead) $\implies \{A,B,D\} \implies \text{Expected: PROTO\_X7}$
- Step 2: Augment $+E$ (Add reports_to_S2) $\implies \{A,B,D,E\} \implies \text{Expected: PROTO\_X7}$
- Step 3: Augment $+F$ (Add neutral fact) $\implies \{A,B,D,E,F\} \implies \text{Expected: PROTO\_X7}$

### Chain 2 (Originating at Path DE):
- Step 0: Minimal Base $\{D,E\} \implies \text{Expected: PROTO\_X7}$
- Step 1: Augment $+A$ (Add manager) $\implies \{D,E,A\} \implies \text{Expected: PROTO\_X7}$
- Step 2: Augment $+B$ (Add reports_to_S1) $\implies \{D,E,A,B\} \implies \text{Expected: PROTO\_X7}$
- Step 3: Augment $+F$ (Add neutral fact) $\implies \{D,E,A,B,F\} \implies \text{Expected: PROTO\_X7}$

Tested across 2 Insertion Positions (Append vs Prepend) $\times$ 2 Stations (`VELORA`, `KESTREL`) = **32 calls**.

## 3. Measurable Endpoints & Analysis
- **Success-to-Error Transition Rate ($R_{S \to E}$):** Frequency of transitions where a correct answer at step $k$ flips to incorrect or `UNKNOWN` at step $k+1$ despite the addition being formally compatible.
- **Monotonic Scaffolding Score ($K_{\text{mono}}$):** Proportion of augmentation chains that remain 100% monotonically correct throughout all 4 steps.
