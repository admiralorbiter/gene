# Experiment Card — Track R: Role Equivariance & Semantic Shortcut Dissection

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** In Exploration Round 3 Track H, the model sustained `PROTO_X7` on formally invalid cross-premise combinations ($\{A,D\}$ and $\{B,D\}$), with premise $D$ (`sector_lead`) appearing in 3 of 4 minimal coalitions. This suggests that `sector_lead` functions as a privileged lexical/semantic authority anchor rather than an ungrounded formal variable.
- **The Tripartite Dissection:** By applying three semantics-preserving transformations to the same formal support topology $S_F = \{\{A,B\}, \{D,E\}\}$, we determine what drives the shortcut:
  1. **Role Slot Inversion ($\rho_{\text{swap}}$):** Swap $A \leftrightarrow D$ (`A = sector_lead`, `D = manager`). If shortcut shifts from $\{A,D\}$ to $\{D,A\}$, the shortcut follows the semantic role.
  2. **Role Anonymization ($\rho_{\text{opaque}}$):** Replace natural-language roles with synthetic opaque tokens (`ROLE_Q7`, `ROLE_M2`). If shortcuts vanish, lexical priors drive the shortcut.
  3. **Station Entity Rotation ($\rho_{\text{station}}$):** Swap station entity `VELORA` $\leftrightarrow$ `KESTREL` to test context-conditioned permissiveness.

## 2. Experimental Arms & Intervention Grid
For each representation condition:
- Baseline ($AB+DE \to \text{PROTO\_X7}$)
- Formal Single Knockouts ($A=0, B=0, D=0, E=0$)
- Shortcut Probes ($\{A,D\}, \{B,D\}, \{A,E\}, \{B,E\}$)
- Full Knockout ($\emptyset \to \text{UNKNOWN}$)

## 3. Measurable Endpoints & Success Criteria
- **Role Follow Rate:** Percentage of shortcut expressions that align with the `sector_lead` role vs the slot $D$.
- **Lexical Prior Suppression:** Reduction in invalid shortcutting under opaque synthetic role tokens.
- **Station Divergence Ratio:** Ratio of shortcut acceptance in `VELORA` vs `KESTREL`.
