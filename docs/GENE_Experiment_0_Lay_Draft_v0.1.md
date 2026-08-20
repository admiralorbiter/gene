# Who Is the Parent of an AI's Thought?

*A layman's companion draft to the GENE Experiment 0 paper*

We spend a lot of time worrying about AI making things up.

But I've started to think the stranger problem begins one step earlier than the future I was originally worried about.

Before I could ask what happens when an AI remembers something wrong, I ran into a more basic question:

> **How would I even know which memory caused what it said next?**

That sounds easier than it is.

Suppose I give an AI three notes:

1. Nerin manages a station called Velora.
2. Nerin reports to Kira.
3. If a station's manager reports to Kira, that station uses Protocol X7.

Then I ask:

> What protocol does Velora use?

The AI says X7.

Easy.

Now I ask the AI which notes it used.

It says: all three.

So are those three notes the parents of the answer?

Maybe.

But there is a problem.

AI explanations are not necessarily explanations in the way we want them to be. Researchers have repeatedly found that models can give convincing descriptions of what supposedly drove an answer without those descriptions reliably tracking the actual behavior of the system. A cited source can be plausible without being causally necessary.

So I tried something stronger.

I removed a parent.

And that is where things got weird.

## The family tree that wasn't

The project is called **GENE — Genealogical Epistemic Network Experiments**.

The admittedly overdramatic idea was to give information a family tree.

Instead of a database saying:

> Here are 10 facts.

I wanted it to say:

> This claim came from these two earlier claims and this rule. This one later produced three children. This branch mutated here. This other branch died out. This claim was exposed to the model but did not seem to matter. This source was cited by the model but failed a causal test.

The biological language eventually became useful because it forced me to stop treating all forms of "source" as the same thing.

A **locus** is the stable memory slot.

An **allele** is the particular claim living in that slot.

A **mutation** changes the claim without pretending it is a completely unrelated memory.

A **knockout** removes it.

A **phenotype** is the downstream answer.

Again, an AI memory is not literally DNA.

But the vocabulary made one point hard to ignore:

> If information can be copied, transformed, and reused, we should probably care about its ancestry.

## Three different kinds of parent

GENE eventually ended up with three different family trees.

The first is boring but objective:

### Exposure

Was the memory physically in the prompt?

If yes, it was exposed.

That tells us it *could* have mattered.

It does not tell us that it did.

The second is what the AI says:

### Reported support

Which memories did the model cite as evidence?

Useful.

But still a self-report.

The third is where things become experimental:

### Causal support

Change the alleged parent.

Does the child change in the way the world predicts?

That sounds obvious, but even this gets slippery.

If I delete one fact and the answer stays the same, perhaps the fact did not matter.

Or maybe the prompt left another shortcut.

Or maybe there were two ways to reach the same conclusion.

This project repeatedly turned into an experiment about experiments.

Every time I thought I had a clean measurement, I found a way the measurement itself could lie.

## The protocol token that refused to die

One of the funniest failures came from trying to make the synthetic world simple.

I gave the model one relevant rule.

If the manager reports to Kira, the station uses Protocol Green.

Then I started deleting premises.

Remove the rule?

The answer disappears.

Great.

Remove one of the facts?

Sometimes the model still says:

> Protocol Green.

That initially looked like evidence that the premise was not causal.

But eventually the problem became obvious.

**Protocol Green was the only protocol in the room.**

I had built a test of logical reasoning where the correct answer was also the only plausible completion token.

The model didn't necessarily need to reconstruct the whole logical chain.

The benchmark was leaking the answer through its structure.

So I changed the world.

Now there were three competing rules:

- Kira → X7
- Tal → Q2
- Mira → M9

The labels were deliberately meaningless.

Now if I changed Kira to Tal, a model actually following the information should not merely produce "something else."

It should move specifically:

> X7 → Q2.

And if I changed Kira to somebody with no rule at all?

It should say:

> I don't know.

That turned out to be far more revealing.

## The model that knew it didn't know—and answered anyway

Another early result was stranger.

I removed enough evidence that the answer could no longer be determined.

Gemma's output basically said:

> The evidence is insufficient.

It gave confidence zero.

Its explanation acknowledged that the relevant information was missing.

And then the answer field still contained the protocol.

That led to a distinction I didn't have when I started.

There are at least two ways a system can answer badly.

The first:

> It correctly recognizes that the evidence is insufficient and answers anyway.

The second:

> It incorrectly decides that the evidence is sufficient and then follows that incorrect judgment perfectly.

Those sound similar if all you score is whether the final answer was right.

They are completely different failures.

Recent research on AI abstention has found a related phenomenon: models can detect that a problem is underspecified without reliably translating that detection into refusing to answer.

So GENE started measuring two things separately.

**E:** Did the model correctly judge the evidence?

**K:** Did its behavior follow that judgment?

That little distinction ended up explaining a surprising amount.

## The 2×2 experiment

By this point there were two knobs.

One knob changed the **information environment**.

Either:

- one visible rule and one obvious conclusion;

or:

- multiple matched rules with competing conclusions.

The second knob changed the **response contract**.

Either:

- a loose JSON answer;

or:

- an explicit requirement to first declare whether the evidence was sufficient, insufficient, or conflicting—and to answer `UNKNOWN` if it wasn't sufficient.

That gave four conditions.

The numbers looked like this:

| | Loose answer contract | Explicit evidence/abstention contract |
|---|---:|---:|
| One visible conclusion | **46.7%** | **86.7%** |
| Competing conclusions | **65.2%** | **100.0%** |

That last number needs a giant asterisk.

It does **not** mean Gemma is 100% reliable.

It means Gemma passed every intervention in this small artificial calibration assay: 66 out of 66 tests across six synthetic worlds.

The important part was *why* the cells failed differently.

The explicit contract mostly fixed the:

> "I know I don't know, but I'm answering anyway"

problem.

The competing information environment mostly fixed the:

> "There is only one answer-looking thing in this prompt, so I'm going to convince myself the evidence supports it"

problem.

One changes what the model does with its judgment.

The other changes the judgment itself.

## Why I think that matters

This project started because I was interested in memory.

But Experiment 0 turned into a lesson about **measurement**.

It is tempting to think a model either "used" a memory or it didn't.

That is probably too crude.

A memory can be:

- visible to the model;
- cited by the model;
- logically required by the formal problem;
- behaviorally necessary under one intervention;
- redundant under another;
- capable of steering the answer when mutated.

Those are different facts.

And the environment we build around the model changes which of those facts we can see.

There is a larger research literature here.

Researchers studying explanation faithfulness have shown that an AI's story about why it answered something is not automatically a faithful description of what drove the output. Others have pointed out that simply deleting words or evidence can itself create weird, unnatural inputs. Counterfactual edits can sometimes provide a cleaner test: instead of destroying the evidence, change it in a way that predicts a specific new answer.

That is essentially where GENE ended up.

Don't just kill the parent.

**Mutate it and see where the child goes.**

Then restore it and see whether the child comes back.

## So is this about AI memory yet?

Not quite.

And that is actually why I think Experiment 0 stands on its own.

Before I can make strong claims about bad memories reproducing through long-running AI systems, I need an instrument that can tell me what reproduction even means.

Experiment 0 is the calibration of that instrument.

It gives me:

- a formal family tree;
- a record of what information was exposed;
- the model's own claimed parents;
- counterfactual intervention tests;
- a distinction between bad evidence judgment and bad response control;
- mutations;
- rescue.

The next experiments can now ask the thing I originally wanted to ask:

> What happens when one bad memory gets to have children?

But that is another paper.

For now, I think Experiment 0 leaves me with a simpler point.

> **An AI answer does not have one obvious provenance.**

If we care about systems that remember, revise, and reuse information for months or years, we may need to know more than where a statement was stored.

We may need to know its family.

---

## Sources / further reading

- Atanasova et al. (2023), *Faithfulness Tests for Natural Language Explanations*.
- Madsen, Chandar & Reddy (2024), *Are self-explanations from Large Language Models faithful?*
- Kamahi & Yaghoobzadeh (2024), *Counterfactuals As a Means for Evaluating Faithfulness of Attribution Methods in Autoregressive Language Models*.
- Siegel et al. (2024), *The Probabilities Also Matter*.
- Gu et al. (2026), *Bridging the Detection-to-Abstention Gap in Reasoning Models under Insufficient Information*.
- Wu et al. (2024), *LongMemEval*.
- Ouyang & Hou (2026), *MemLineage*.
- Zhang & Li (2026), *ConsistencyGate*.
