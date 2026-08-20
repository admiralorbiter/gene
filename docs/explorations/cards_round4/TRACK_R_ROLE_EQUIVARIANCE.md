# Experiment Card — Track R: Role Equivariance & Semantic Shortcut Dissection

## 1. Core Hypothesis & Scientific Rationale
- **Core Hypothesis:** In Exploration Round 3 Track H (KESTREL), the model sustained `PROTO_X7` on formally invalid cross-premise combinations ($\{B,D\}$ and $\{A,D\}$), with premise $D$ (`sector_lead`) appearing in 3 of 4 minimal coalitions. This observation **suggests a candidate explanation**: that `sector_lead` functions as a privileged natural-language authority cue allowing premature inference.
- **The Discriminating Contrast:**
  - In the canonical baseline ($A = \text{manager}, B = \text{reports\_to\_S1}, D = \text{sector\_lead}, E = \text{reports\_to\_S2}$):
    - Shortcut observed: $\{B,D\} \to \text{PROTO\_X7}$ (Rule 1 reporting + Rule 2 authority role `sector_lead`).
    - Non-shortcut baseline: $\{A,E\} \to \text{UNKNOWN}$ (Rule 1 authority role `manager` + Rule 2 reporting).
  - We apply a **topology-preserving semantic intervention** swapping roles $A \leftrightarrow D$ ($A = \text{sector\_lead}, D = \text{manager}$) and dynamically re-rendering the formal rules via typed `RuleAntecedent`s:
    1. **Semantic-Role Follow:** If the shortcut is driven by the semantic authority of `sector_lead`, the shortcut must **invert**: $\{A,E\}$ becomes behaviorally sufficient ($\to \text{PROTO\_X7}$), while $\{B,D\}$ collapses to $\text{UNKNOWN}$.
    2. **Graph-Slot / Position Follow:** If the shortcut is driven by graph topology or position $D$, $\{B,D\}$ remains behaviorally sufficient even though $D$ is now `manager`.
    3. **Formal Equivalence / Alpha-Renaming ($\rho_{\text{opaque}}$):** Replacing roles with opaque synthetic tokens (`ROLE_Q7`, `ROLE_M2`) tests whether shortcuts vanish entirely when natural-language role semantics are stripped.

## 2. Experimental Intervention Matrix (KESTREL Ecology)
We evaluate 3 representation conditions $\times$ 8 key lattice points = **24 calls**:
1. **Condition 1 (Canonical Natural Roles):** $A=\text{manager}, D=\text{sector\_lead}$.
2. **Condition 2 (Role-Swapped Semantic Intervention):** $A=\text{sector\_lead}, D=\text{manager}$.
3. **Condition 3 (Opaque Synthetic Roles):** $A=\text{ROLE\_Q7}, D=\text{ROLE\_M2}$.

### Probed Lattice Points per Condition (8 points):
- Baseline: $\{A,B,D,E\} \implies \text{PROTO\_X7}$
- Formal Path 1: $\{A,B\} \implies \text{PROTO\_X7}$
- Formal Path 2: $\{D,E\} \implies \text{PROTO\_X7}$
- Cross-Pair 1: $\{B,D\}$
- Cross-Pair 2: $\{A,E\}$
- Cross-Pair 3: $\{A,D\}$
- Cross-Pair 4: $\{B,E\}$
- Zero Premises: $\emptyset \implies \text{UNKNOWN}$

## 3. Measurable Endpoints & Analysis
- **Role Inversion Ratio ($\mathcal{R}_{\text{role}}$):** Proportion of shortcut transitions that switch from $\{B,D\}$ to $\{A,E\}$ upon swapping $A \leftrightarrow D$.
- **Opaque Shortcut Suppression Rate:** Rate at which illicit cross-pairs ($\{A,D\}, \{B,D\}$) return to valid $\text{UNKNOWN}$ under opaque synthetic tokens.
- **Role Equivariance Conformance ($K_{\text{role}}$):** Whether formal paths ($\{A,B\}, \{D,E\}$) retain 100% entitlement regardless of role renaming.
