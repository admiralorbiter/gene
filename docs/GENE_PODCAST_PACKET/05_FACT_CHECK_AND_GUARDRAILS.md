# Fact Check, Claim Boundaries, and Podcast Guardrails

This is the file the skeptical host should keep open.

---

# Claims GENE can make

## Experiment 0

GENE built a deterministic synthetic-world assay with explicit ground truth and intervention logic.

It separated:

- exposure lineage;
- model-reported support;
- counterfactual behavioral dependence.

It implemented:

- knockout;
- double knockout;
- semantic mutation;
- unmatched mutation;
- sequential rescue.

It ran a hardened 2×2 factorial on Gemma 3 12B using six counterbalanced canonical micro-worlds.

The four cells produced:

- Single-rule + schema v1: **28/60 intervention passes = 46.7%**.
- Single-rule + schema v2: **52/60 = 86.7%**.
- Competing-rule + schema v1: **43/66 = 65.2%**.
- Competing-rule + schema v2: **66/66 = 100%**.

Across the four cells, the hardened factorial used **276 model calls**.

The six worlds covered all six rule-order permutations and all three protocol rotations **marginally**, not the complete 18-combination Cartesian product.

Worlds are the intended experimental unit; interventions are repeated measurements clustered within worlds.

---

# What 100% means

Correct:

> “Gemma passed all 66 interventions in the tested Ecology-C + Schema-v2 calibration cell.”

Incorrect:

> “Gemma is 100% causally faithful.”

Incorrect:

> “The experiment proves competing information always improves LLM reasoning.”

Incorrect:

> “GENE solved hallucinations.”

---

# What A/E/K mean

**A**  
Whether the emitted answer behavior matched the experiment's expected outcome.

**E**  
Whether the model's *explicitly emitted* evidence-status judgment matched formal evidence sufficiency.

**K**  
Whether the model's output behavior complied with that explicit judgment.

Important:

> E is not a direct measurement of hidden neural belief or internal chain-of-thought.

It is an experimentally useful model-emitted epistemic judgment.

---

# What lineage means

**Exposure lineage** is objective context inclusion.

**Reported lineage** is what the model says supported it.

**Causal lineage** is evidence from controlled interventions.

A model-reported parent is not automatically a causal parent.

A parent that fails a single knockout test is not automatically irrelevant: redundancy can make a real ancestor individually non-necessary.

---

# What biology means

GENE uses biological language operationally:

- locus;
- allele;
- mutation;
- phenotype;
- reproduction;
- rescue.

Do not claim:

> LLM memories are literally genes.

Do say:

> The biological vocabulary forces precise distinctions between identity, content, reproduction, mutation, and extinction.

---

# What the research literature establishes

## State Contamination

Shows persistent memory/state can carry downstream harmful influence and that compressed memory can preserve effects not obvious from surface safety signals.

It does **not** prove all summaries are contaminated.

## ConsistencyGate

Shows write-time admission control can reduce contamination in the authors' benchmarks.

It does **not** establish that self-consistency gating is universally optimal.

## Memory Contagion

Shows cross-temporal propagation of evaluator bias in the tested setup and that propagation can differ by bias type.

It argues against assuming one universal contamination dynamic.

## MemLineage

Shows lineage/provenance can be used for enforcement in a memory-security architecture.

It is not the same experimental goal as GENE.

## Misinformation Propagation in Multi-Agent Systems

Shows system robustness depends on composition and decision protocol.

Do not conclude “multi-agent systems are safer” in general.

---

# Shannon guardrail

Shannon information theory measures communication quantities such as entropy and channel capacity.

Do not say:

> Shannon tells us whether information is true.

A central podcast point is the opposite:

> Truth and transmission fidelity are separate.

---

# Human-memory guardrail

Loftus-style experiments show that post-event information can alter later reports and memory performance.

They do not mean every human memory is false.

Reconsolidation research shows reactivated memories can become labile under particular experimental conditions.

Do not simplify this to:

> “Every time you remember something, you rewrite it completely.”

Active-forgetting research in flies demonstrates regulated forgetting mechanisms.

Do not assume the same molecular mechanism explains human autobiographical forgetting.

---

# Prion guardrail

Prions are real infectious proteinaceous agents associated with transmissible spongiform encephalopathies.

Use prions as an analogy for **pattern propagation without exact symbolic copying**.

Do not imply LLM semantic propagation and prion molecular templating share a biological mechanism.

---

# Experiment 1 guardrail

At the time this packet was prepared, Experiment 1 is the forward-looking branching experiment.

Do not invent:

- reproduction numbers;
- infection counts;
- mutual information values;
- extinction rates;
- successful or failed propagation.

If updated Experiment 1 results are uploaded later, prefer those.

---

# Novelty guardrail

Do not call GENE:

- the first system to study AI memory contamination;
- the first lineage-aware memory system;
- the inventor of epistemic reproduction numbers;
- the first biology-inspired memory architecture.

Adjacent work already exists in all of these broad areas.

A safer possible positioning is:

> GENE is exploring an experimentally controlled, claim-level genealogy of information in persistent LLM memory, with separate measurements for exposure, reported support, causal intervention, mutation, repair, and future reproduction.

---

# Good skeptical questions for the hosts

- Could the synthetic world make the task too easy?
- Does this replicate in other model families?
- Is `evidence_status` merely prompt compliance?
- Are opaque tokens actually reducing pretrained priors, or just creating another artificial setting?
- What happens when retrieval is stochastic?
- What happens when two infected branches converge?
- What happens when summaries alter the wording but preserve the causal frame?
- What if a false lineage becomes independently corroborated?
- How do we distinguish repair from simple loss of the lineage?
- Can aggressive “immune” defenses suppress useful novelty?
