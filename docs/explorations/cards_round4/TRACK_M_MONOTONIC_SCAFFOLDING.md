# Experiment Card — Track M: Support-Preserving Monotonicity & Fragility

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** In Exploration Round 3 Track H (VELORA), appending evidence produced non-monotonic collapse ($\{E\} \implies \text{PROTO\_X7}$, but adding $A \implies \{A,E\} \implies \text{UNKNOWN}$). While $\{E\}$ was an illicit shortcut, this reveals that neural inference can experience **Success-to-Error Transitions ($S \to E$)** when epistemically compatible evidence is appended.
- **Formal Support-Preserving Augmentation:** Unlike generic prompt lengthening, GENE defines a precise semantic contract: If target claim $c$ is formally entitled under minimal support environment $S_1 = \{A,B\}$, sequentially adding valid, non-contradictory premise augments ($+D, +E, +F_{\text{distractor}}$) **must preserve formal entitlement** ($S_F(c) \ne \emptyset$).
- **Neutral Distractor Specification:** Premise $F$ is formally defined in `EpistemicState` as a typed neutral fact (`predicate: "neutral_fact"`, `subject: "Corin"`, `entity: "VELORA"`, `root_ids: ["R3"]`), rendered as *"Archive record logs Corin on duty at VELORA."*

## 2. Experimental Chains & Exact Token Sequences

### Chain 1 (Originating at Path AB):
1. **Append Direction:**
   - Step 0 ($N=2$): $[A, B]$
   - Step 1 ($N=3$): $[A, B, D]$
   - Step 2 ($N=4$): $[A, B, D, E]$
   - Step 3 ($N=5$): $[A, B, D, E, F]$
2. **Prepend Direction:**
   - Step 0 ($N=2$): $[A, B]$
   - Step 1 ($N=3$): $[D, A, B]$
   - Step 2 ($N=4$): $[E, D, A, B]$
   - Step 3 ($N=5$): $[F, E, D, A, B]$

### Chain 2 (Originating at Path DE):
1. **Append Direction:**
   - Step 0 ($N=2$): $[D, E]$
   - Step 1 ($N=3$): $[D, E, A]$
   - Step 2 ($N=4$): $[D, E, A, B]$
   - Step 3 ($N=5$): $[D, E, A, B, F]$
2. **Prepend Direction:**
   - Step 0 ($N=2$): $[D, E]$
   - Step 1 ($N=3$): $[A, D, E]$
   - Step 2 ($N=4$): $[B, A, D, E]$
   - Step 3 ($N=5$): $[F, B, A, D, E]$

Tested across 2 Chains $\times$ 2 Insertion Directions $\times$ 4 Steps $\times$ 2 Stations (`VELORA`, `KESTREL`) = **32 calls**.

## 3. Measurable Endpoints & Analysis
- **Success-to-Error Transition Rate ($R_{S \to E}$):** Frequency of transitions where a correct answer at step $k$ flips to incorrect or `UNKNOWN` at step $k+1$ despite the addition being formally compatible.
- **Monotonic Scaffolding Score ($K_{\text{mono}}$):** Proportion of augmentation chains that remain 100% monotonically correct throughout all 4 steps.
