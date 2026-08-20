# Source Library

This is a curated source list for the podcast model. Sources are grouped by purpose. Primary research and official paper pages are favored.

---

# A. GENE project sources

## Experiment 0 final report
Repository file:
`docs/EXPERIMENT_0_FINAL_REPORT.md`

## Experiment 0 walkthrough
Repository file:
`docs/results/EXPERIMENT_0_WALKTHROUGH.md`

## Experiment 1 protocol
Repository file:
`docs/EXPERIMENT_1_PROTOCOL.md`

## Research positioning
Repository file:
`docs/RESEARCH_POSITIONING.md`

---

# B. Modern LLM memory and contamination

## State Contamination in Memory-Augmented LLM Agents
Yian Wang, Agam Goyal, Yuen Chen, Hari Sundaram. 2026.  
https://arxiv.org/abs/2605.16746

Key use:
- persistent state as a causal safety channel;
- memory laundering;
- sub-threshold downstream influence;
- intervention placement matters.

## ConsistencyGate: Preventing Memory Contamination in LLM Agents via Self-Consistency Admission Control
Yan Zhang, Shibo Li. 2026.  
https://arxiv.org/abs/2607.22962

Key use:
- write-time admission;
- one false fact can become a persistent premise;
- memory protection can act before storage.

## Memory Contagion: Cross-Temporal Propagation of Evaluator Bias via Agent Memory
Zewen Liu. 2026.  
https://arxiv.org/abs/2606.23195

Key use:
- bias can propagate through memory;
- contagion occurs even under oracle consolidation;
- different bias types propagate differently.

## MemLineage: Lineage-Guided Enforcement for LLM Agent Memory
Ciyan Ouyang, Rui Hou. 2026.  
https://arxiv.org/abs/2605.14421

Key use:
- derivation DAG;
- provenance;
- lineage-based action control.

## Memory Provenance Laundering in LLM Agents: A Non-Amplification Firewall for Persistent Memory
Jinghan Xu et al. 2026.  
https://arxiv.org/abs/2607.29167

Key use:
- low-trust origins can be rewritten into apparently authoritative persistent memory;
- provenance authority can amplify unless deliberately preserved.

## MemGuard: Preventing Memory Contamination in Long-Term Memory-Augmented Large Language Models
Hyeonjeong Ha et al. 2026.  
https://arxiv.org/abs/2605.28009

Key use:
- heterogeneous memory types;
- functional boundaries between facts, episodes, and rules.

## Governing Evolving Memory in LLM Agents
Chingkwun Lam, Jiaxin Li, Lingfei Zhang, Kuo Zhao. 2026.  
https://arxiv.org/abs/2603.11768

Key use:
- memory governance;
- semantic drift;
- temporal decay;
- access control.

## Governed Collaborative Memory as Artificial Selection in LLM-Based Multi-Agent Systems
Diego F. Cuadros et al. 2026.  
https://arxiv.org/abs/2605.04264

Key use:
- memory governance as a selection regime;
- variants persist, remain local, or are rejected.

## Misinformation Propagation in Benign Multi-Agent Systems
Jonas Becker, Jan Philip Wahle, Terry Ruas, Bela Gipp. 2026.  
https://arxiv.org/abs/2606.16710

Key use:
- misinformation can persist in multi-agent debate;
- robustness depends on group composition and aggregation protocol.

---

# C. Long-term memory benchmarks

## Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo)
Adyasha Maharana et al. 2024.  
https://arxiv.org/abs/2402.17753

## LongMemEval
Di Wu et al. 2024.  
https://arxiv.org/abs/2410.10813

## LongMemEval-V2
Di Wu et al. 2026.  
https://arxiv.org/abs/2605.12493

Use these to establish:
- the field has invested heavily in memory capacity, retrieval, temporal reasoning, and updates;
- GENE's question begins after recall succeeds.

---

# D. Explanation faithfulness and counterfactual intervention

## Are self-explanations from Large Language Models faithful?
Andreas Madsen, Sarath Chandar, Siva Reddy. ACL Findings 2024.  
https://aclanthology.org/2024.findings-acl.19/

## Counterfactuals As a Means for Evaluating Faithfulness of Attribution Methods in Autoregressive Language Models
Aaron Mueller, Hanjie Chen. BlackboxNLP 2024.  
https://aclanthology.org/2024.blackboxnlp-1.28/

## The Probabilities Also Matter: A More Faithful Metric for Faithfulness of Free-Text Explanations in Large Language Models
Noah Siegel, Oana-Maria Camburu, Nicolas Heess, Maria Perez-Ortiz. ACL 2024.  
https://aclanthology.org/2024.acl-short.49/

## Analyzing Semantic Faithfulness of Language Models via Input Intervention on Question Answering
Akshay Chaturvedi et al. Computational Linguistics 2024.  
https://aclanthology.org/2024.cl-1.5/

Use these for:
- self-report ≠ causal explanation;
- deletion can be misleading;
- counterfactual semantic edits can be stronger;
- binary answer flips may miss sub-threshold influence.

---

# E. Abstention and epistemic control

## Bridging the Detection-to-Abstention Gap in Reasoning Models under Insufficient Information
Renjie Gu et al. 2026.  
https://arxiv.org/abs/2605.28070

Use for:
- models can recognize insufficient information yet continue to answer;
- abstention as a control decision.

---

# F. Information theory and error correction

## Claude E. Shannon — A Mathematical Theory of Communication
Bell System Technical Journal, 1948.

Part I DOI:  
https://doi.org/10.1002/j.1538-7305.1948.tb01338.x

Part II DOI:  
https://doi.org/10.1002/j.1538-7305.1948.tb00917.x

Key use:
- mathematical transmission fidelity;
- semantics deliberately outside the engineering problem.

## Richard W. Hamming — Error Detecting and Error Correcting Codes
Bell System Technical Journal, 1950.  
https://doi.org/10.1002/j.1538-7305.1950.tb00463.x

Key use:
- structured redundancy;
- reliable computation over many operations.

---

# G. Genetics, mutation, and informational reproduction

## Luria & Delbrück — Mutations of Bacteria from Virus Sensitivity to Virus Resistance
Genetics, 1943.  
https://doi.org/10.1093/genetics/28.6.491

Historical jackpot retrospective:
https://pmc.ncbi.nlm.nih.gov/articles/PMC4788220/

Key use:
- early mutations produce large descendant jackpots;
- infer invisible lineage history from population distribution.

## Matthew Meselson & Franklin Stahl — The Replication of DNA in Escherichia coli
PNAS, 1958.  
https://doi.org/10.1073/pnas.44.7.671

Key use:
- inheritance and generational copying;
- elegant physical tracing of ancestry.

## Thomas Kunkel & Lawrence Loeb — Fidelity of mammalian DNA polymerases
Science, 1981.  
https://doi.org/10.1126/science.6454965

Key use:
- isolated copying mechanisms are not the whole fidelity story;
- larger biological systems add correction mechanisms.

## Manfred Eigen — Selforganization of matter and the evolution of biological macromolecules
Naturwissenschaften, 1971.  
https://doi.org/10.1007/BF00623322

Key use:
- mutation-selection dynamics;
- error-threshold / quasispecies conceptual bridge.

## Stanley Prusiner — Novel Proteinaceous Infectious Particles Cause Scrapie
Science, 1982.  
https://doi.org/10.1126/science.6801762

Key use:
- prions;
- structural pattern propagation;
- infection need not look like ordinary genetic copying.

---

# H. Human memory, contamination, and reconsolidation

## Loftus & Palmer — Reconstruction of automobile destruction: An example of the interaction between language and memory
Journal of Verbal Learning and Verbal Behavior, 1974.  
https://doi.org/10.1016/S0022-5371(74)80011-3

Key use:
- wording affects later remembered reports.

## Loftus, Miller & Burns — Semantic integration of verbal information into a visual memory
Journal of Experimental Psychology: Human Learning and Memory, 1978.  
https://pubmed.ncbi.nlm.nih.gov/621467/

Key use:
- misleading post-event information can be integrated into later memory.

## Roediger & McDermott — Creating False Memories: Remembering Words Not Presented in Lists
Journal of Experimental Psychology: Learning, Memory, and Cognition, 1995.  
https://doi.org/10.1037/0278-7393.21.4.803

Key use:
- information structure can generate a remembered item that was never presented.

## Johnson, Hashtroudi & Lindsay — Source Monitoring
Psychological Bulletin, 1993.  
https://doi.org/10.1037/0033-2909.114.1.3

Key use:
- remembering content and remembering its source are different cognitive problems.

## Nader, Schafe & LeDoux — Fear memories require protein synthesis in the amygdala for reconsolidation after retrieval
Nature, 2000.  
https://doi.org/10.1038/35021052

Key use:
- reactivated memories can become labile and require reconsolidation.

## Shuai et al. — Forgetting Is Regulated through Rac Activity in Drosophila
Cell, 2010.  
https://doi.org/10.1016/j.cell.2009.12.044

## Berry et al. — Dopamine Is Required for Learning and Forgetting in Drosophila
Neuron, 2012.  
https://doi.org/10.1016/j.neuron.2012.04.007

Key use:
- forgetting can be actively regulated rather than treated solely as passive decay.

---

# I. Epidemiology, branching, and evolutionary epistemology

## Diekmann, Heesterbeek & Roberts — The construction of next-generation matrices for compartmental epidemic models
Journal of the Royal Society Interface, 2010.  
https://doi.org/10.1098/rsif.2009.0386

Key use:
- reproduction numbers in structured populations;
- next-generation matrices;
- multiple infectious phenotypes/types.

## Watson & Galton — On the Probability of the Extinction of Families
Journal of the Anthropological Institute, 1875.

Historical use only:
- early branching-process problem framed around surname/family extinction.
- Be aware of Galton's eugenic history; do not romanticize him.

## Donald T. Campbell — Blind variation and selective retention in creative thought as in other knowledge processes
Psychological Review, 1960.  
https://doi.org/10.1037/h0040373

Key use:
- evolutionary epistemology;
- variation + selection as a model of knowledge processes.

---

# J. Philosophy and conceptual references

These are interpretive lenses, not empirical sources.

## Karl Popper
*Conjectures and Refutations* (1963)

Use:
- knowledge growth through criticism and error elimination.

## Thomas Kuhn
*The Structure of Scientific Revolutions* (1962)

Use:
- conceptual environments shape what evidence is noticed and how anomalies are interpreted.

## Gregory Bateson
*Steps to an Ecology of Mind* (1972)

Use:
- “difference that makes a difference” as a conversational bridge to counterfactual causality.

## Richard Dawkins
*The Selfish Gene* (1976)

Use cautiously:
- memes as cultural replicators;
- useful analogy;
- GENE attempts a much more operational notion of informational lineage.

---

# Recommended “must use” subset for a 45-minute episode

If the podcast cannot use everything, prioritize:

1. GENE Experiment 0 Final Report
2. Shannon 1948
3. Hamming 1950
4. Luria–Delbrück 1943
5. Prusiner 1982
6. Loftus & Palmer 1974
7. Nader et al. 2000
8. State Contamination 2026
9. ConsistencyGate 2026
10. Memory Contagion 2026
11. MemLineage 2026
12. Detection-to-Abstention Gap 2026
13. Madsen et al. 2024 on self-explanation faithfulness
14. Mueller & Chen 2024 on counterfactual faithfulness
