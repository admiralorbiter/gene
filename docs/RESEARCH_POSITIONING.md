# GENE Research Positioning Notes

**Status:** working literature map, not a novelty claim.

**Last checked:** 2026-08-19

GENE sits near several rapidly developing research areas. Much of the closest work is from 2026 and is still preprint-stage, so this document should be refreshed before any publication or public novelty statement.

---

# 1. Long-term memory benchmarks

## LoCoMo

Maharana et al. introduced LoCoMo to evaluate very long-term conversational memory across long multi-session conversations, including question answering, event summarization, and related memory tasks.

- Paper: https://arxiv.org/abs/2402.17753

## LongMemEval

Wu et al. evaluate long-term interactive memory across information extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention.

- Paper: https://arxiv.org/abs/2410.10813

## LongMemEval-V2

The 2026 follow-up expands toward whether agents acquire useful environment-specific experience, including static state, dynamic state, workflows, gotchas, and premise awareness.

- Paper: https://arxiv.org/abs/2605.12493

### Relevance to GENE

These benchmarks establish strong conventions for evaluating memory quality, but GENE is not primarily a recall benchmark. Its initial target is the **ancestry and causal propagation of generated memory claims** under exact synthetic ground truth.

---

# 2. State and memory contamination

## State Contamination in Memory-Augmented LLM Agents

This 2026 work studies how contaminated persistent state can influence later agent behavior and uses counterfactual methodology to separate contamination effects from baseline behavior.

- Paper: https://arxiv.org/abs/2605.16746

### Relevance to GENE

GENE should borrow paired/counterfactual experimental logic, but move the unit of analysis from downstream behavioral effect toward **individual information descendants and lineage edges**.

## ConsistencyGate

ConsistencyGate treats hallucinated facts written into memory as memory contamination and introduces a write-time self-consistency admission gate. It evaluates controlled corruptions across real-conversation benchmarks and a structured synthetic corpus.

- Paper: https://arxiv.org/abs/2607.22962

### Relevance to GENE

Write-time admission is a natural later intervention. It should not be part of the first baseline because GENE first needs to observe unconstrained lineage dynamics.

---

# 3. Cross-temporal propagation

## Memory Contagion

Liu (2026) studies cross-temporal propagation of evaluator bias through agent memory and reports bias-type-dependent behavior rather than a single universal propagation pattern.

- Paper: https://arxiv.org/abs/2606.23195

### Relevance to GENE

This supports varying mutation/error classes later. The first experiment should deliberately remain simpler: one atomic factual mutation with exact oracle truth.

---

# 4. Provenance and derivation lineage

## MemLineage

MemLineage attaches provenance and derivation lineage to agent memory and represents derivation using a weighted DAG for security enforcement.

- Paper: https://arxiv.org/abs/2605.14421

## MAP-Graph

MAP-Graph represents agents, sources, memories, claims, and actions in a provenance-aware execution graph and uses ancestry/trust operationally in shared-memory workflows.

- Paper: https://arxiv.org/abs/2608.10509

## Memory Provenance Laundering / PPMF

This work studies how memory consolidation can preserve an action trigger while obscuring low-trust provenance, and proposes provenance-preserving memory controls.

- Paper: https://arxiv.org/abs/2607.29167

### Relevance to GENE

GENE should not claim that lineage-aware memory is itself novel. Its working distinction is methodological:

> **Exposure lineage, model-reported support, and experimentally tested causal ancestry are separate objects.**

The experiment asks whether a bad claim creates descendants and whether individual transmission edges can be perturbed and validated.

---

# 5. Memory governance as selection

## Governed Collaborative Memory as Artificial Selection

A 2026 viewpoint explicitly frames shared memory governance as a selection regime determining which memory variants persist, remain private, are rejected, or are superseded.

- Paper: https://arxiv.org/abs/2605.04264

### Relevance to GENE

This is close to GENE's biological motivation and means we should avoid claiming that “memory as selection” is new. GENE's stronger possible contribution is **experimentalizing reproduction, mutation, repair, and extinction at the claim-lineage level**.

---

# 6. Epistemic reproduction number

## Computational Epistemics of Biological Discovery, Part III

A June 2026 preprint uses the term **Epistemic Reproduction Number** \(R_E\) and describes a threshold in which circulating false positives generate more than one descendant in autonomous scientific networks.

- Landing page/preprint record: https://figshare.com/articles/preprint/Computational_Epistemics_of_Biological_Discovery_Part_III_Collective_Computational_Epistemics_and_Multi-Agent_Networks/32666031

### Relevance to GENE

Do not claim to invent an “epistemic reproduction number.”

For internal experiments, use working notation such as \(R_{mem}\) for the **empirically observed number of causally infected memory children per reproductively active infected memory node**.

A potential contribution would be testing whether a reproduction statistic measured from actual LLM memory lineages predicts persistence/extinction, rather than assuming the dynamics theoretically.

---

# 7. Working GENE research gap

The current defensible positioning is:

> Existing work studies long-term recall, memory contamination, bias contagion, provenance, lineage-aware security, and memory governance. GENE builds a controlled synthetic testbed where the complete ground truth is known and the ancestry of an erroneous claim can be recorded at exposure time, reported by the model, and selectively tested using counterfactual parent interventions.

Potentially distinctive components, to be validated rather than advertised as novel:

1. **Claim genealogy as the primary object of evaluation**, rather than final task accuracy alone.
2. **Three-layer lineage:** exposure, reported support, causal evidence.
3. **Direct classification of transmitted mutation vs de novo mutation vs repair.**
4. **Empirical reproduction statistics derived from observed descendants.**
5. **Later controlled tests of biological governance mechanisms** such as senescence, reproduction gating, repair, and lineage extinction.
6. **Epistemic monoculture experiments** that separate apparent evidence count from independent ancestry.

---

# 8. Novelty language to avoid for now

Avoid:

- “first epistemic reproduction number”;
- “first lineage-aware LLM memory”;
- “first biological model of AI memory”;
- “no one has studied memory contagion”;
- “information propagation in agents is unexplored.”

Safer language:

- “GENE tests whether...”
- “We operationalize...”
- “We empirically measure...”
- “We distinguish...”
- “We evaluate a biological analogy as an experimental intervention rather than assuming equivalence.”

---

# 9. Literature questions for the next research pass

Before a paper-quality experiment, search specifically for:

- causal attribution of individual persistent-memory entries;
- information diffusion/branching-process models in LLM memory;
- rumor cascade metrics adapted to agent-generated knowledge;
- synthetic knowledge-graph corruption benchmarks with generational write-back;
- influence functions / causal tracing across external memory rather than model weights;
- epistemic diversity/source independence metrics;
- biological senescence/apoptosis analogies in knowledge management or distributed systems;
- error-threshold/quasispecies analogies in machine-generated information systems.

The purpose of that pass should be to sharpen claims, not to delay Experiment 0.
