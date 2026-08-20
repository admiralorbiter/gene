# GENE Experimental Protocol

> [!NOTE]
> **STATUS: HISTORICAL FROZEN FOUNDATIONAL PROTOCOL**  
> This protocol documents the early architecture through Experiment 0 / 1A. All subsequent research phases (Phase 8 through Phase 10.5) have been completed and frozen into canonical reports and schemas.  
> See [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md), [`docs/DEVELOPMENT_PLAN.md`](../docs/DEVELOPMENT_PLAN.md), and [`docs/results/`](../docs/results/) for current execution status.

---

# 1. Research objective

GENE studies the **genealogy of information inside persistent LLM memory systems**.

The foundational question is not merely whether an LLM outputs a false answer. It is:

> When an erroneous stored claim is exposed to later inference and memory-writing processes, how does it reproduce, mutate, repair, persist, or become extinct?

The first experiments test whether those processes can be observed reliably enough to support later causal and biological analogies.

---

# 2. Operational definitions

These definitions should remain stable across the first pilot.

## 2.1 Source fact

An atomic proposition generated directly by the synthetic-world generator and stored in the immutable ground-truth ledger.

Example:

```text
manager(VELORA, NERIN)
```

## 2.2 Rule

A machine-readable implication that permits deterministic derivation from source or derived facts.

Example:

```text
reports_to(X, TAL) AND manager(STATION, X)
    -> protocol(STATION, GREEN)
```

## 2.3 Claim

An atomic proposition extracted from an LLM output and normalized into the experiment ontology.

A claim may be true, false, unsupported, contradictory, or unparseable relative to the oracle.

## 2.4 Memory node

A persisted information artifact available for future retrieval. A node may contain one or more normalized claims plus the original natural-language representation.

## 2.5 Generation

A discrete reproduction step. Generation 0 contains the initial source memories. Generation `t+1` contains memories produced by tasks that consume memories available at or before generation `t`, according to the experiment policy.

## 2.6 Exposure edge

A directed edge `A -> B` exists when memory node A was actually included in the model context used to produce node B.

This edge is objective and should be logged by the harness.

## 2.7 Reported-support edge

A directed edge `A -> B` exists when the model explicitly identifies A as supporting B.

This is a model report, not causal evidence.

## 2.8 Causal edge

A directed edge `A -> B` is supported when a controlled counterfactual intervention on A changes the relevant truth/infection status or semantic content of B while holding the remainder of the generation procedure fixed as closely as possible.

Causal edges should carry an evidence strength and intervention record rather than a binary philosophical claim of perfect causation.

## 2.9 Mutation seed

The single intentionally corrupted atomic fact introduced into the mutated member of a clean/mutated world pair.

## 2.10 Infected claim

For Experiment 1, a claim is infected when its falsity is causally downstream of the mutation seed.

This is stricter than simply being false.

A false claim with no causal ancestry from the seed is classified as a **de novo mutation**.

## 2.11 Repair

A claim with infected ancestry that returns to the oracle-consistent state.

## 2.12 Reproductive activity

A node is reproductively active when experiment policy permits it to be retrieved as input to tasks that can create persistent descendants.

---

# 3. Why synthetic worlds come first

GENE should initially avoid real-world facts because real-world truth introduces unnecessary ambiguity:

- source disagreement;
- temporal change;
- incomplete knowledge;
- entity ambiguity;
- evaluator-model dependence;
- hidden pretrained knowledge.

Synthetic worlds allow exact ground truth, exact valid derivations, exact corruption injection, and automated evaluation.

The worlds should still be expressed in natural language so the LLM performs realistic extraction and reasoning.

---

# 4. Synthetic world design

## 4.1 World components

Each world contains:

- unique fictional entities;
- typed binary or unary relations;
- source facts;
- deterministic derivation rules;
- natural-language renderings;
- a canonical graph/triple representation;
- generated tasks requiring retrieval and inference.

Avoid names strongly associated with real people, companies, places, or franchises.

## 4.2 Initial relation vocabulary

Start small:

```text
manager(station, person)
reports_to(person, person)
located_in(station, sector)
opened_in(station, year)
uses_protocol(station, protocol)
member_of(person, team)
team_lead(team, person)
```

Do not expand the ontology until Experiment 0 is stable.

## 4.3 Reasoning-depth tiers

Create three difficulty tiers:

- **D0:** direct source fact;
- **D1:** one-rule inference;
- **D2:** two-rule inference.

Experiment 0 should demonstrate reliable lineage at D0 and D1 before D2 is heavily used.

## 4.4 World constraints

A generated world should pass an oracle validator before use:

- no contradictory canonical facts unless intentionally configured;
- all entities typed;
- no ambiguous valid answer for benchmarked tasks;
- no unintended alternative derivation for tasks intended to have one known chain;
- clean and mutated worlds identical except for the intended mutation.

---

# 5. Experiment 0 — Lineage observability

## 5.1 Question

Can GENE correctly observe the ancestry of derived information?

## 5.2 Hypotheses

**H0.1:** Structured parent reporting will identify a substantial fraction of known supporting memories, but will not be sufficiently reliable to treat self-reported lineage as causal ground truth.

**H0.2:** Exposure logging plus counterfactual ablation will distinguish merely present context from influential ancestry.

## 5.3 Procedure

For each synthetic world:

1. Generate validated source facts and rules.
2. Render source facts into natural-language memory nodes.
3. Generate tasks with known derivation depth and valid supporting ancestors.
4. Retrieve the required memory set plus controlled distractors.
5. Ask the model to return structured output containing:
   - normalized answer claim;
   - confidence if requested;
   - `parent_memory_ids`;
   - short rationale, stored only as an observable artifact and not used as ground truth.
6. Record all exposure edges automatically.
7. Compare reported parents with the oracle-valid support set.
8. Select reported and unreported candidate parents for counterfactual reruns.
9. Remove or replace one candidate parent while holding other inputs/configuration fixed.
10. Measure whether the descendant claim changes.

## 5.4 Primary Experiment 0 metrics

### Reported-lineage precision

Of reported parent edges, what fraction are oracle-valid supports?

### Reported-lineage recall

Of oracle-required supports, what fraction are reported?

### Causal validation rate

Of tested reported-parent edges, what fraction survive the predefined causal-ablation criterion?

### Hidden causal parent rate

Of tested exposed-but-unreported memories, what fraction measurably influence the descendant?

## 5.5 Gate to Experiment 1

Proceed when:

- exposure logging is exact by construction;
- oracle evaluation is passing unit/property tests;
- structured output failure is low enough not to dominate runs;
- parent-report metrics are characterized;
- causal reruns are reproducible enough to interpret;
- at least several complete lineage DAGs have been manually audited.

No arbitrary precision threshold is frozen before the plumbing pilot. The goal is characterization first.

---

# 6. Experiment 1 — Single mutation

## 6.1 Question

What descendants are produced by one corrupted stored fact?

## 6.2 Design

Each experimental unit is a **paired synthetic world**:

```text
World_i_clean
World_i_mutated
```

The pair has identical:

- world seed;
- entities;
- true ontology;
- tasks;
- distractors;
- prompt templates;
- generation schedule;
- model configuration.

The mutated world differs in exactly one presented source fact.

Example:

```text
TRUE:    manager(VELORA, NERIN)
MUTATED: manager(VELORA, SOREN)
```

The immutable oracle still contains the true canonical world.

## 6.3 Mutation selection

The seed mutation should initially be:

- atomic;
- plausible within the fictional world;
- syntactically normal;
- capable of affecting at least one downstream derivation;
- not contradicted by another immediately visible source fact.

Later experiments can vary mutation type.

## 6.4 Generational procedure

Initial target: generations 0–8.

At each generation:

1. sample or select downstream tasks according to a frozen schedule;
2. retrieve eligible memories;
3. log all exposures;
4. ask the model for answer + structured parent IDs;
5. normalize output claims;
6. oracle-evaluate truth state;
7. write configured outputs back to memory;
8. record lineage edges;
9. perform causal checks on a prespecified sample of candidate transmission edges.

## 6.5 Primary endpoint

> **Cumulative causally infected descendants through generation 8.**

The metric counts distinct descendant claims whose erroneous state is supported as causally downstream of the seeded mutation.

The exact causal-testing budget should be frozen after the plumbing pilot, because exhaustive ablation may be too expensive.

## 6.6 Secondary endpoints

### Memory reproduction number

Working notation:

\[
R_{mem}(t) = \frac{1}{|I_t|}\sum_{i\in I_t} K_i
\]

where:

- `I_t` = reproductively active infected claims at generation `t`;
- `K_i` = number of directly infected causal children produced by infected claim `i`.

Do not overclaim an epidemiological or biological phase transition from a small pilot. Initially treat this as an empirical descriptive statistic.

### Cumulative amplification ratio

Total infected descendants generated per seeded mutation.

### Transmission probability per exposure

Probability that exposure to an infected memory produces an infected child under the relevant task conditions.

### Repair probability

Probability that infected ancestry yields a true/oracle-consistent descendant.

### De novo mutation rate

Rate of false claims without infected causal ancestry.

### Lineage survival

Number of generations until no reproductively active infected descendants remain.

### Task accuracy

Needed to ensure an intervention does not simply prevent error spread by destroying useful reasoning.

---

# 7. Four-state classification

Every evaluated atomic claim should fall into a useful conceptual matrix:

| | Clean ancestry | Infected ancestry |
|---|---|---|
| **True** | faithful knowledge | repaired lineage |
| **False** | de novo mutation | transmitted mutation |

Unsupported/unparseable outputs should be tracked separately rather than forced into the matrix.

---

# 8. Causal counterfactual protocol

This is one of the highest-risk methodological components and should be explicit.

For a candidate parent A and child B:

1. preserve the original call metadata;
2. rerun the child-producing prompt with A removed **or**, where removal changes task solvability, replaced by its clean paired-world counterpart;
3. keep model, model digest, prompt template, decoding settings, context ordering policy, and all other memories fixed;
4. compare normalized descendant claims;
5. repeat across predefined seeds when stochastic decoding is used;
6. store the complete intervention record.

Possible evidence categories:

- **strong causal support:** infection disappears/reverses consistently under intervention;
- **partial causal support:** infection probability or content changes materially but not deterministically;
- **no detected effect:** descendant remains materially unchanged;
- **indeterminate:** output instability prevents interpretation.

Do not collapse these into a binary edge until the intervention rule is empirically validated.

---

# 9. Initial run matrix

## Plumbing run

Purpose: find bugs, not estimate effects.

Suggested:

- 5–10 worlds;
- 1 model;
- 1 decoding configuration;
- 1–2 seeds if stochastic;
- D0/D1 tasks only;
- short generation depth.

## Pilot run

Purpose: characterize variance and freeze confirmatory design.

Suggested starting target:

- ~30 paired worlds;
- 3 decoding seeds;
- generations 0–8;
- D0/D1 plus limited D2;
- one small/medium open model.

These are planning numbers, not a preregistered power calculation. Use pilot variance/effect distributions to design later confirmatory runs.

## Cross-model replication

Only after the protocol is frozen:

- one additional model family;
- then one larger-capacity model if compute permits.

Do not vary model, retrieval policy, ontology complexity, and intervention simultaneously.

---

# 10. Model/runtime metadata

Record at minimum:

```text
run_id
experiment_version
git_commit
ollama_version
model_name
model_digest
quantization
parameter_size
num_ctx
temperature
top_p (if set)
seed
world_seed
prompt_template_version
prompt_hash
retrieval_policy_version
memory_policy_version
oracle_version
started_at
completed_at
```

Per call also preserve:

```text
raw_request
raw_response
structured_response
input_memory_ids
output_memory_ids
eval_result
prompt_tokens
completion_tokens
latency
```

---

# 11. Statistical rules

- Treat **world** as the primary experimental unit.
- Preserve pairing between clean and mutated worlds.
- Do not treat every descendant as an independent replicate.
- Prefer world-level bootstrap confidence intervals for early reporting.
- For later modeling, consider hierarchical models with world/run effects.
- Count outcomes may be overdispersed; negative-binomial models may be more appropriate than ordinary least squares.
- Transmission events can be modeled with binomial/logistic approaches.
- Extinction/persistence can be analyzed as time-to-event data.
- Freeze one primary endpoint before confirmatory scaling.

---

# 12. Threats to validity to track from day one

## Pretraining leakage

Even fictional names can accidentally resemble known entities. Use generated names and validate uniqueness where practical.

## Prompt-position effects

Context order may alter influence. Randomize or systematically control order and log it.

## Stochastic instability

A causal rerun may change simply because generation is stochastic. Use deterministic decoding where scientifically acceptable or replicate interventions across seeds.

## Evaluator leakage

Do not use the same LLM as the sole truth oracle. Canonical truth must be machine-generated and mechanically evaluated wherever possible.

## Parsing failure

Natural-language claims may not normalize cleanly. Track parsing failure as an outcome and keep raw output.

## Alternative derivations

A descendant may remain infected even after a candidate parent is removed because another infected ancestor independently supports it. World/task generation must identify valid alternative paths.

## Retrieval confounding

Failure to propagate can occur because a memory was never retrieved rather than because the model rejected it. Exposure and adoption must remain separate measurements.

## Memory volume confounding

Later generations may have larger candidate stores. Control retrieval opportunity and record candidate-set size.

---

# 13. Explicit non-goals for Experiment 0/1

Do not yet claim to demonstrate:

- a universal misinformation threshold;
- biological equivalence;
- human-memory dynamics;
- real-world misinformation behavior;
- optimal memory governance;
- multi-agent emergent behavior;
- general safety effectiveness.

The first result is narrower: **a validated method for observing and perturbing information lineages in controlled LLM memory experiments.**
