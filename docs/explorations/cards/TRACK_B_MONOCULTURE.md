# Experiment Card — Track B: Epistemic Monoculture / Independent Roots

## QUESTION
When multiple memories in retrieved context agree on a conclusion, does a language model treat four agreeing descendants from a single common ancestor as four independent pieces of evidence, or does it differentiate source diversity from semantic repetition?

## PRIMARY MANIPULATION
Construct contexts with conflicting evidence claims where raw document frequency and independent ancestral roots disagree:
- **Condition 1 (Monoculture, $N_{\text{root}}=1$ vs $1$):** 3 memories claiming `PROTOCOL_X` descend from Root $R_1$; 1 memory claiming `PROTOCOL_Y` descends from Root $R_2$ (Raw ratio 3:1, Root ratio 1:1).
- **Condition 2 (Diverse Roots, $N_{\text{root}}=3$ vs $1$):** 3 memories claiming `PROTOCOL_X` descend from 3 distinct independent roots $R_1, R_2, R_3$; 1 memory claiming `PROTOCOL_Y` descends from Root $R_4$ (Raw ratio 3:1, Root ratio 3:1).
- **Condition 3 (Inverted Diversity, $N_{\text{root}}=1$ vs $2$):** 3 memories claiming `PROTOCOL_X` descend from 1 root $R_1$; 2 memories claiming `PROTOCOL_Y` descend from 2 independent roots $R_2, R_3$ (Raw ratio 3:2 in favor of X, Root ratio 1:2 in favor of Y).

Hold constant across all conditions: total text length, entity names, prompt syntax, lexical phrasing, and contextual positions.

## FROZEN CONTROLS
- Rule closure logic and entity syntax.
- Dual-Oracle evaluation metrics.
- Symmetrical role assignment and target predicates.

## PRIMARY ENDPOINT
- $\Delta_{\text{diversity}} = P(\text{adjudicate } X \mid \text{Diverse Roots}) - P(\text{adjudicate } X \mid \text{Monoculture})$
- Effective independent evidence count: $N_{\text{eff}} = 1 / \sum_{r} p_r^2$.

## FALSIFIER
If the model produces identical confidence / adjudication distributions regardless of whether the 3 agreeing memories share 1 ancestor or 3 independent ancestors ($\Delta_{\text{diversity}} = 0.00$), the model performs purely surface-level token/repetition counting and is blind to genealogical monoculture.

## ZERO-COMPUTE GATE
Implement a genealogy-aware evidence aggregator that calculates $N_{\text{raw}}$ vs $N_{\text{eff}}$ and deterministic voting predictions across all conflict permutations.

## LIVE CALL CEILING
12 calls (3 diversity levels × 2 conflict directions × 2 role-swapped worlds). Hard maximum: 18 calls.

## STOP RULE
Stop after the 12-call panel. Do not implement complex Bayesian belief networks or agent ensembles.

## STATUS
PROVISIONAL — EXPLORATORY ROUND 1
