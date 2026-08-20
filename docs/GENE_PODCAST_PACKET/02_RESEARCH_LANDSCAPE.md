# Research Landscape — What GENE Connects To

This document is organized as a set of research threads rather than a linear literature review. The podcast should use these papers to deepen the story, not read them as a bibliography.

---

# Thread 1 — From “can it remember?” to “what happens when memory is wrong?”

## LoCoMo — very long-term conversational memory

**Maharana et al. (2024), “Evaluating Very Long-Term Conversational Memory of LLM Agents.”**  
arXiv:2402.17753

LoCoMo created long multi-session conversations and evaluated question answering, summarization, and multimodal dialogue memory.

### Why it matters

This represents the first broad framing:

> Can an agent retain and retrieve information over very long interactions?

GENE asks a different downstream question:

> If the stored information is wrong, how does that error influence future reasoning?

---

## LongMemEval

**Wu et al. (2024), “LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory.”**  
arXiv:2410.10813

LongMemEval evaluates extraction, multi-session reasoning, temporal reasoning, updates, and abstention.

### Podcast connection

Long-memory research initially treats memory mostly as a capability.

GENE treats memory as a **stateful causal substrate**.

The problem shifts from “did we recall the fact?” to:

- Who wrote the fact?
- What did it descend from?
- What future claims inherited it?
- Can it be corrected without losing useful memory?

---

## LongMemEval-V2

**Wu et al. (2026), “LongMemEval-V2: Evaluating Long-Term Agent Memory Toward Experienced Colleagues.”**  
arXiv:2605.12493

The newer benchmark focuses on whether agents internalize environment-specific experience: workflows, dynamic state, gotchas, and premise awareness.

### Why it matters

As memory becomes procedural and institutional — “how this environment works” — contamination becomes more consequential.

A wrong memory is no longer just a wrong fact.

It can become a wrong **workflow**.

---

# Thread 2 — Memory contamination as a persistent-state problem

## State Contamination

**Yian Wang, Agam Goyal, Yuen Chen, Hari Sundaram (2026), “State Contamination in Memory-Augmented LLM Agents.”**  
arXiv:2605.16746

The paper studies persistent agent state including summaries, transcripts, retrieved context, and memory buffers.

A particularly relevant concept is **memory laundering**:

- harmful/toxic context gets compressed;
- the summary may look benign to detectors;
- downstream behavior still shifts compared with matched neutral baselines.

The authors introduce a “sub-threshold propagation gap” to capture influence that survives even when the stored summary looks safe.

### Connection to GENE

GENE independently converged on a similar concern:

> **The surface form of a memory may look safe or ordinary while its ancestry still matters.**

This is why GENE separates content from lineage.

---

## ConsistencyGate

**Yan Zhang & Shibo Li (2026), “ConsistencyGate: Preventing Memory Contamination in LLM Agents via Self-Consistency Admission Control.”**  
arXiv:2607.22962

ConsistencyGate focuses on **write-time admission**.

Before a candidate memory is committed, the system evaluates whether it is sufficiently supported.

### Connection to GENE

This maps cleanly onto the future decomposition:

\[
\text{Exposure} \times \text{Transmission} \times \text{Write Admission}.
\]

A generated error cannot reproduce through persistent memory if it never becomes an active memory node.

Podcast question:

> Is the safest time to fight misinformation **before it enters memory**, after it is retrieved, or after it has already produced descendants?

---

## MemGuard

**Ha et al. (2026), “MemGuard: Preventing Memory Contamination in Long-Term Memory-Augmented Large Language Models.”**  
arXiv:2605.28009

MemGuard argues that different memory functions — stable facts, episodes, behavioral rules — should not be treated as interchangeable evidence.

### Connection

GENE’s “information ecology” result points in a compatible direction.

What surrounds a claim and what kind of evidence it is allowed to interact with changes downstream behavior.

---

# Thread 3 — Lineage and provenance

## MemLineage

**Ciyan Ouyang & Rui Hou (2026), “MemLineage: Lineage-Guided Enforcement for LLM Agent Memory.”**  
arXiv:2605.14421

MemLineage attaches provenance and a derivation DAG to memory entries and uses ancestry when deciding whether a memory may justify sensitive actions.

### Connection

This is one of the closest architectural neighbors to GENE.

But the emphasis differs:

- MemLineage: use lineage as an enforcement/security mechanism.
- GENE: use lineage as an **experimental object** and measure mutation, reproduction, repair, and phenotype.

---

## Memory Provenance Laundering

**Xu et al. (2026), “Memory Provenance Laundering in LLM Agents: A Non-Amplification Firewall for Persistent Memory.”**  
arXiv:2607.29167

This work studies how low-authority external observations can be rewritten into apparent user history or workflow memory, preserving action triggers while losing their original authority.

### Podcast connection

This is the “citation laundering” version of memory contamination.

A claim can survive while its **source status disappears**.

GENE's stronger idea is to track not just the source but the entire descendant family tree.

---

# Thread 4 — Cross-temporal contagion

## Memory Contagion

**Zewen Liu (2026), “Memory Contagion: Cross-Temporal Propagation of Evaluator Bias via Agent Memory.”**  
arXiv:2606.23195

The paper shows evaluator bias can pass through stored memory into later agents, even with oracle-quality consolidation.

Importantly, different bias types behaved differently.

### Connection

This is a warning against treating “misinformation transmissibility” as one universal constant.

The fitness of bad information may depend on:

- what kind of information it is;
- how it is compressed;
- what model reads it;
- the surrounding information ecology.

---

## Misinformation Propagation in Benign Multi-Agent Systems

**Becker, Wahle, Ruas & Gipp (2026).**  
arXiv:2606.16710

The authors inject misinformation into benign single-agent and multi-agent systems.

They find propagation depends on group composition and decision protocol; multi-agent interaction can sometimes reduce degradation, especially when most agents remain unexposed.

### Connection

This suggests a later GENE phase:

> After understanding one memory lineage inside one agent, place infected lineages into different network topologies.

But this should come *after* single-lineage dynamics are understood.

---

# Thread 5 — Memory governance as selection

## Governing Evolving Memory in LLM Agents

**Lam, Li, Zhang & Zhao (2026).**  
arXiv:2603.11768

This work frames dynamic memory as a governance problem involving semantic drift, consistency verification, temporal decay, access control, and consolidation.

### Connection

One of GENE's speculative biological ideas is that healthy memory systems need more than permanent storage:

- promotion;
- decay;
- quarantine;
- supersession;
- revision;
- active forgetting.

---

## Governed Collaborative Memory as Artificial Selection

**Cuadros et al. (2026).**  
arXiv:2605.04264

This viewpoint explicitly describes memory governance as a selection regime determining which variants persist into shared institutional memory.

### Connection

This is strikingly close to the evolutionary metaphor.

GENE can make the metaphor experimentally measurable:

> Which variants actually produce descendants, and what selection regime changes their reproductive success?

---

# Thread 6 — Self-explanation is not ancestry

## Are self-explanations from LLMs faithful?

**Madsen, Chandar & Reddy (ACL 2024).**

The authors test whether model self-explanations correspond to behavior under intervention and conclude faithfulness varies by model, task, and explanation type.

### Connection

GENE's parent IDs are therefore treated as:

> reported support, not causal truth.

This is why the project maintains separate reported-support and causal graphs.

---

## Counterfactuals for evaluating faithfulness

**Mueller & Chen (BlackboxNLP 2024).**

The paper argues that simple token removal can create out-of-distribution inputs for autoregressive language models and proposes fluent counterfactuals as a stronger evaluation approach.

### Connection

GENE independently encountered this.

Single-parent deletion was not enough.

Directional semantic mutation became much more informative:

\[
Kira \rightarrow Tal
\]

should not merely make the answer “different.”

It should steer it to the *specific* Tal consequence.

---

## The probabilities also matter

**Siegel, Camburu, Heess & Perez-Ortiz (ACL 2024).**

The authors argue that an output can retain the same discrete prediction while its probability distribution shifts substantially under intervention.

### Future GENE implication

A memory may influence a descendant without flipping the final answer.

Future assays could therefore measure:

- categorical output shift;
- confidence/log-probability shift;
- lineage influence below the decision threshold.

---

# Thread 7 — Abstention is a control problem

## Bridging the Detection-to-Abstention Gap

**Gu et al. (2026).**  
arXiv:2605.28070

This paper studies reasoning models that recognize insufficient information but continue to reason and answer anyway.

They frame abstention as a control decision rather than merely a final-answer style.

### Connection to GENE

GENE's early Schema-v1 behavior showed an almost uncanny version of the same problem:

- model output signaled missing evidence;
- answer field still contained the salient conclusion token.

GENE eventually separated:

\[
E = \text{did the model assess sufficiency correctly?}
\]

from

\[
K = \text{did behavior obey that assessment?}
\]

---

# Thread 8 — Shannon: fidelity is not truth

## Claude Shannon, 1948

**“A Mathematical Theory of Communication.”**

Shannon established the mathematics of information transmission under noise.

One of the most important conceptual warnings for the podcast:

> Shannon information is not a truth metric.

A false sentence can travel down a channel with perfect fidelity.

### GENE connection

This gives two independent axes:

- **semantic/global truth**
- **transmission fidelity**

A lineage can preserve an error perfectly.

---

# Thread 9 — Hamming: reliable systems need error-correcting structure

## Richard Hamming, 1950

**“Error Detecting and Error Correcting Codes.”**

Hamming was motivated by large-scale computation in which many operations must occur without a single error spoiling the final result.

He showed that adding structured redundancy makes detection and correction possible.

### GENE connection

GENE’s Ecology C unexpectedly echoes this logic.

Competing alternatives gave the model more structure with which to determine which premise chain actually matched.

The lesson is not “more context is always better.”

It is:

> **The right redundant structure can make errors detectable.**

---

# Thread 10 — DNA replication: copying fidelity requires machinery

## Kunkel & Loeb, 1981

**“Fidelity of mammalian DNA polymerases.”**

Their measurements showed isolated polymerases could be much less accurate than the overall fidelity observed in living systems, implying additional mechanisms contribute to maintaining genetic information.

### Podcast connection

Reliable inheritance is not produced by one magic copier.

It is a stack:

- selection;
- proofreading;
- repair;
- redundancy;
- removal of damaged components.

Persistent AI memory may eventually need an analogous stack.

---

# Thread 11 — Luria–Delbrück: the jackpot lineage

## Luria & Delbrück, 1943

**“Mutations of Bacteria from Virus Sensitivity to Virus Resistance.”**

This classic experiment used the distribution of resistant bacteria across cultures to show that mutations could arise before exposure to the selecting virus.

A famous later historical account describes Luria getting the key statistical intuition after thinking about a slot-machine jackpot.

### Why this is perfect for GENE

If a mutation happens late:

> it has few descendants.

If it happens early:

> one mutation can generate a huge family.

That is exactly why “how many false answers exist?” is less informative than:

> **Where in the family tree did the error begin?**

---

# Thread 12 — Eigen’s error threshold

## Manfred Eigen, 1971

Eigen's early quasispecies work explored how copying fidelity, mutation, and selection interact in populations of replicating macromolecules.

One famous implication of this family of models is an **error threshold**:

> past some mutation regime, a lineage may no longer preserve the information that defined its ancestral sequence.

### GENE connection

Future GENE experiments could separate:

- high reproduction + high fidelity;
- high reproduction + low fidelity;
- low reproduction + high fidelity;
- extinction.

This is more informative than one scalar “spread” metric.

---

# Thread 13 — Prions: inheritance without genetic sequence

## Stanley Prusiner, 1982

**“Novel Proteinaceous Infectious Particles Cause Scrapie.”**

Prusiner proposed the term **prion** for an infectious agent whose crucial component was protein rather than a conventional nucleic-acid genome.

### Why this belongs in the podcast

Prions are a startling reminder that an infectious informational pattern need not be transmitted through an obvious symbolic “code.”

A protein conformation can template further conformational change.

### GENE connection

This is a useful analogy for **structural contagion**:

- a memory may change downstream behavior without copying its exact wording;
- summaries can preserve framing while losing visibly toxic content;
- lineage can matter even when descendants no longer resemble the ancestor lexically.

This is an analogy, not a mechanistic equivalence.

---

# Thread 14 — Human memory is reconstructive

## Loftus & Palmer, 1974

Participants watched automobile accidents.

Changing the wording of later questions — famously using verbs such as “smashed” versus milder verbs — changed speed estimates and later memory reports.

## Loftus, Miller & Burns, 1978

Misleading post-event information reduced memory accuracy and could become integrated into the remembered event.

### GENE connection

Human memory also does not behave like immutable file storage.

Later information can enter the representation used to reconstruct an earlier event.

---

# Thread 15 — Retrieval can reopen memory

## Nader, Schafe & LeDoux, Nature 2000

The researchers showed that reactivated fear memories in rats could return to a labile state and require protein synthesis again for reconsolidation.

### GENE connection

Retrieval is not necessarily passive access.

In both biological and engineered systems, the moment information is used may be exactly when it becomes vulnerable to change.

This inspires a future rule:

> **Revalidate knowledge when it reproduces.**

---

# Thread 16 — False memory from semantic structure

## Roediger & McDermott, 1995

Participants studied lists of related words but frequently recalled or recognized a strongly associated word that had never been presented.

### GENE connection

A representation can be generated by the **structure of the surrounding information** even when it was never explicitly stored.

That is remarkably similar to GENE's early single-consequent protocol-token attractor.

---

# Thread 17 — Forgetting can be active

## Shuai et al., Cell 2010

Manipulating Rac activity in Drosophila changed the rate of forgetting.

## Berry et al., Neuron 2012

Specific dopamine signaling was implicated in both learning and regulated forgetting.

### Connection

Persistent systems often treat forgetting as failure.

Biology suggests forgetting can also be a **control function**.

For long-memory agents, the hard question may not be:

> How do we prevent forgetting?

but:

> **What deserves to remain reproductively active?**

---

# Thread 18 — Evolutionary epistemology

## Donald T. Campbell, 1960

**“Blind variation and selective retention in creative thought as in other knowledge processes.”**

Campbell applied an evolutionary structure — variation and selection — to knowledge and creativity.

### GENE connection

This offers a philosophical bridge:

> Knowledge systems are not healthy merely because they preserve information.

They need mechanisms that generate variants, evaluate them, reject some, and retain others.

That makes **selection policy** part of epistemology.
