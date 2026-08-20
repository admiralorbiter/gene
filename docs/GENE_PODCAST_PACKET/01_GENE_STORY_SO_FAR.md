# GENE — The Story So Far

## 1. The question that started it

GENE grew out of a deceptively simple problem:

> **What happens to bad information after a system remembers it?**

Most work on AI memory begins with a retrieval question:

> Can the agent remember the right thing later?

That is important, but it hides another problem.

A memory can be:

- easy to retrieve,
- written clearly,
- internally consistent,
- reused repeatedly,

and still be **wrong**.

Persistent memory changes the consequences of an error. A one-turn hallucination disappears when the context window disappears. A hallucination written to durable memory becomes a premise available to future reasoning.

The central GENE intuition became:

> **Persistence preserves errors as well as truths.**

And from there:

> **The better a system becomes at remembering, the more important it becomes that it can change its mind.**

---

# 2. Why information theory alone is not enough

Claude Shannon’s communication theory asks about uncertainty and reliable transmission. It famously brackets off semantic truth.

This means a communication system can transmit a false sentence with extraordinary fidelity.

That produces an important ladder:

1. **Communication question:** Did the signal survive?
2. **Biological question:** Did the representation reproduce?
3. **Cognitive question:** Did the representation survive reconstruction?
4. **Epistemic question:** Is the representation true?
5. **Social/system question:** How many descendants did it produce?

GENE lives in the gaps between these questions.

---

# 3. The biological turn

Biology became useful because living systems do not merely store information.

They:

- replicate it;
- mutate it;
- proofread it;
- repair it;
- select among variants;
- suppress some lineages;
- kill some cells;
- forget;
- maintain provenance through ancestry.

That suggested a different language for persistent AI memory.

## Operational GENE vocabulary

**Locus**  
A stable memory slot or identity.

**Allele**  
The particular semantic claim occupying that locus.

**Mutation**  
Change the semantic allele while preserving the locus.

**Knockout**  
Remove the locus from active exposure.

**Expression**  
Expose the memory to a downstream inference.

**Phenotype**  
The downstream claim produced from the information.

**Lineage**  
The graph of descendants produced from an ancestor.

This is an engineered analogy, not a claim that an LLM memory store is literally alive.

---

# 4. Experiment 0 was supposed to be boring

Experiment 0 had a narrow purpose:

> Before studying misinformation propagation, prove that GENE can actually observe informational ancestry.

The first synthetic worlds were deliberately simple. They contained fictional stations, people, supervisors, protocols, and explicit logical rules.

Example:

- Nerin manages Kestrel.
- Nerin reports to Kira.
- If a station manager reports to Kira, the station uses Protocol Green.

Question:

> Which protocol does Kestrel use?

Because the world is synthetic, GENE knows the exact symbolic truth and valid derivation paths.

The first idea was simple:

- expose memories;
- ask the model for an answer;
- ask the model which memory IDs it used;
- remove a claimed parent;
- see whether the answer changes.

It sounded straightforward.

It was not.

---

# 5. The first lesson: plausible metrics can lie

The earliest plumbing run produced numbers that looked respectable:

- structured outputs worked;
- parent precision and recall looked high;
- causal validation produced a plausible percentage.

Then the implementation was inspected.

Several apparent results were artifacts of the measurement system itself:

- the fake client and causal runner used different request representations;
- some rule-derived questions did not guarantee that the rule itself was visible;
- ambiguous synthetic worlds could contain multiple valid answers;
- metric denominators did not always match the intended definition.

The important scientific lesson was not that the code had bugs.

It was:

> **A metric can look scientifically meaningful while quietly inheriting assumptions and errors from the instrument that produced it.**

GENE was already demonstrating its own thesis: provenance matters for measurements too.

This led to an internal idea:

> **Metrics need genealogy.**

A reported number should be traceable to:
- eligible observations;
- numerator;
- denominator;
- classification rule;
- intervention;
- versioned code and prompts.

---

# 6. Exposure is not support, and support is not causation

GENE eventually separated three ancestry graphs.

## Exposure graph

A memory was physically present in the model context.

This is objective.

## Reported-support graph

The model explicitly cited that memory as supporting its answer.

This is a model self-report.

## Causal graph

A controlled counterfactual intervention on the candidate parent altered the relevant downstream behavior.

This is experimentally tested evidence.

These are not equivalent.

A memory can be exposed but irrelevant.

A model can cite a memory that was not necessary.

A legitimate parent can be redundant: removing it may leave an alternative derivation.

And a model may use a memory without reporting it.

This distinction became one of the central conceptual accomplishments of Experiment 0.

---

# 7. The single-consequent surprise

GENE then tested a one-rule inference environment.

The model saw:

- Fact A: station manager relation.
- Fact B: reporting relation.
- Rule: if the manager reports to Kira, use Protocol Green.

Gemma usually gave the correct answer and often cited all three.

But then GENE removed individual premises.

Something strange happened.

Removing the **rule** changed the answer.

Removing Fact A or Fact B often did **not**.

At first this looked like a contradiction:

> Why would the model report a premise as a parent if the answer survives without it?

The answer was hidden in the information ecology.

The rule itself visibly contained the only available conclusion token:

> Protocol Green.

So after a premise was removed, the model could still latch onto the only plausible answer in context.

GENE had accidentally built a benchmark where the conclusion was easier to guess than to derive.

---

# 8. The detection-to-action split

The joint-premise knockout exposed an even stranger behavior.

In one call Gemma effectively said:

- there is not enough evidence;
- confidence is zero;
- the memories do not establish the requested fact;

…and still emitted the specific protocol token.

This split the problem into two stages:

\[
\text{Information Environment}
\rightarrow
\text{Epistemic Estimate}
\rightarrow
\text{Action}
\]

GENE later formalized this with:

**E — Epistemic state accuracy**  
Did the model correctly judge whether the evidence was sufficient?

**K — Policy/contract consistency**  
Did the emitted behavior comply with that judgment?

This closely resembles what later/parallel abstention research calls a **detection-to-abstention gap**.

A model may know — at least at its explicit output level — that a problem is underspecified and still answer anyway.

---

# 9. Schema v2

GENE introduced a stronger response contract.

The model now had to emit:

- `evidence_status = sufficient | insufficient | conflicting`
- an answer
- parent memory IDs

and was explicitly instructed:

> If evidence is insufficient or conflicting, return `UNKNOWN`.

Crucially, later hardening ensured the evaluator did **not** secretly rewrite inconsistent model outputs into `UNKNOWN`.

The raw model behavior had to stand on its own.

GENE then separated:

**A — Answer behavior correctness**  
Did the output match the expected counterfactual outcome?

**E — Epistemic status correctness**  
Did the explicit sufficiency judgment match the formal evidence state?

**K — Contract consistency**  
If the model said evidence was insufficient, did it actually abstain?

---

# 10. Ecology C: competing consequents

The next change was more important.

Instead of one rule:

- Kira → X7

GENE exposed matched competing rules:

- Kira → `PROTO_X7`
- Tal → `PROTO_Q2`
- Mira → `PROTO_M9`

The labels were deliberately opaque.

Now the model could not simply choose the only conclusion token in the prompt.

It had to identify which premise chain matched which rule.

GENE called:

- **Ecology S:** single consequent / one visible rule.
- **Ecology C:** competing consequents / matched alternatives.

This turned “information ecology” into an experimental variable.

---

# 11. Biological interventions became real assays

The project stopped relying on deletion alone.

It introduced:

## Knockout

Remove one informational parent.

## Double knockout / epistasis

Remove multiple parents together.

## Semantic mutation

Change one allele while preserving its memory locus.

Example:

- canonical: Nerin reports to Kira.
- mutated: Nerin reports to Tal.

## Directional mutation

A good causal assay should not merely destroy the answer.

The mutation should steer the answer predictably:

\[
Kira \rightarrow X7
\]

becomes

\[
Tal \rightarrow Q2.
\]

## Unmatched mutation

Change the premise to a supervisor with no matching rule.

Expected result: `UNKNOWN`.

## Rescue

Start from the actually mutated state and restore the clean allele.

Expected lineage:

\[
X7
\xrightarrow{\text{mutation}}
Q2
\xrightarrow{\text{rescue}}
X7.
\]

That is stronger evidence than a simple knockout.

---

# 12. The frozen 2×2 factorial

Experiment 0 ultimately tested two factors:

1. **Information ecology**
   - S: one visible rule.
   - C: competing matched rules.

2. **Response contract**
   - v1: implicit/looser contract.
   - v2: explicit epistemic status and abstention contract.

All four cells used the same six counterbalanced canonical micro-worlds.

## Results

| Cell | Ecology | Schema | Model calls | Intervention pass rate |
|---|---|---:|---:|---:|
| 1 | S | v1 | 66 | 28/60 = **46.7%** |
| 2 | S | v2 | 66 | 52/60 = **86.7%** |
| 3 | C | v1 | 72 | 43/66 = **65.2%** |
| 4 | C | v2 | 72 | 66/66 = **100%** |

Total: **276 live Gemma 3 12B calls** across the hardened factorial.

Important limitation:

> This is calibration on a small synthetic assay using one model. It is not evidence that Gemma is universally 100% causally faithful.

---

# 13. What the factorial suggested

The most useful interpretation was mechanistic.

## Schema v2 mainly improved K

When the model recognized insufficient evidence, the explicit contract made it much more likely to actually abstain.

## Ecology C mainly improved E

Competing alternatives reduced the single-rule conclusion-token attractor and made the model more likely to correctly assess whether the premise chain matched.

The factors were **complementary and jointly sufficient for perfect performance in the tested calibration assay**.

Do not overstate this as a universal statistical interaction.

---

# 14. The deepest Experiment 0 lesson

A model can fail in different ways.

### Control/action failure

The model recognizes that evidence is insufficient but answers anyway.

### Epistemic estimation failure

The model incorrectly decides that weak or mismatched evidence is sufficient and then behaves consistently with that mistaken judgment.

### Semantic inheritance

The model may eventually reason perfectly from information that is itself false.

That third case is the doorway into Experiment 1.

---

# 15. Why Experiment 1 changes the philosophical problem

Imagine canonical reality says:

> Nerin reports to Kira.

But the agent's memory says:

> Nerin reports to Tal.

Now suppose all downstream rules are correct and the model reasons flawlessly.

The local memory implies:

> Tal → Protocol Q2.

The model produces Q2.

From the perspective of the agent's current evidence, Q2 is perfectly justified.

From the perspective of canonical truth, Q2 is false.

So Experiment 1 introduces two oracles:

**Global truth \(T^*\)**  
Is the claim true in canonical reality?

**Local derivability \(D_t\)**  
Is the claim justified by the information actually available to the agent?

The most interesting infection is therefore:

\[
T^*=0,\quad D_t=1.
\]

Globally false.

Locally perfect.

That is not a hallucinating reasoner.

It is a **competent reasoner with a corrupted inheritance**.

---

# 16. Where the project is now

Experiment 0 is frozen.

Experiment 1 is concerned with whether a single false allele can produce descendants across multiple memory generations.

The intended first branching structure is deliberately simple:

\[
G_0 \rightarrow 2 G_1 \rightarrow 4 G_2.
\]

The key future questions are:

- How many direct infected children does an infected parent produce?
- Does the infection remain semantically faithful to its ancestor?
- Does it change phenotype while propagating?
- Does it go extinct?
- Can clean evidence repair the lineage?
- Does retrieval filtering lower exposure?
- Does write gating prevent a generated falsehood from becoming inherited memory?
- What happens when two independent information lineages converge?
- Can a system develop something analogous to an epistemic immune response?

**At the time of this podcast packet, do not invent Experiment 1 outcomes.**
