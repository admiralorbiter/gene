# Experiment Card — Track C: Transformation Depth & Causal Provenance Decay

## QUESTION
Does an ancestral memory at Generation 0 ($G_0$) remain causally decisive after repeated multi-step semantic transformations ($G_0 \to G_1 \to G_2 \to G_3 \to G_4 \to G_5$), or does structural provenance in the DAG decouple from behavioral causality as depth increases?

## PRIMARY MANIPULATION
Construct a deterministic 6-step deep semantic transformation chain:
$$G_0 (\text{Supervisor}) \to G_1 (\text{Protocol}) \to G_2 (\text{Clearance}) \to G_3 (\text{Route}) \to G_4 (\text{Access Tier}) \to G_5 (\text{Audit Mode})$$
At depths $g \in \{1, 3, 5\}$:
- Evaluate baseline derivation from clean root.
- Intervene on founder allele ($G_0: \text{KIRA} \to \text{TAL}$).
- Measure whether the depth-$g$ descendant counterfactually shifts to the mutated allele.

## FROZEN CONTROLS
- 2-premise first-order Horn clauses at each step.
- Zero distractor noise in prompt context for pure causal depth measurement.
- Greedy decoding ($T=0.0$, seed=42).

## PRIMARY ENDPOINTS
- $F_g = P(\text{descendant decodes to founder allele at depth } g)$ (Allele fidelity)
- $C_g = P(\text{founder interventional mutation changes descendant output at depth } g)$ (Interventional causal retention)

## FALSIFIER
If $F_g = 1.000$ and $C_g = 1.000$ uniformly across $g \in \{1, 3, 5\}$, causal lineage does not decay over 5 generations of semantic transformation in this model. Conversely, if $C_g \to 0$ while the DAG maintains the edges, structural provenance decays into mere historical record.

## ZERO-COMPUTE GATE
Construct exact symbolic world generation for all 6 generations and verify deterministic oracle closure for both clean and mutated alleles before running any live model calls.

## LIVE CALL CEILING
12 calls (3 depths $g \in \{1, 3, 5\}$ × 2 states: clean/mutated × 2 role-swapped worlds). Hard maximum: 18 calls.

## STOP RULE
Stop immediately after the 12-call panel.

## STATUS
PROVISIONAL — EXPLORATORY ROUND 1
