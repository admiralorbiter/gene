# GENE Results Feedback Packet

Use this after a plumbing or pilot run. The goal is to make it easy to review both scientific validity and implementation problems without needing the entire repository in the first pass.

---

# 1. Run identity

```text
Experiment:
Protocol version:
Git commit/tag:
Date:
Machine/GPU:
Ollama version:
Model:
Model digest:
Quantization:
num_ctx:
Temperature:
Other decoding parameters:
Prompt version/hash:
Retrieval policy:
Memory policy:
```

---

# 2. Run size

```text
Worlds:
Clean/mutated pairs:
Decoding seeds per world:
Generations:
Task depths:
Total model calls:
Total causal reruns:
Wall-clock runtime:
Approximate tokens:
Failures/retries:
```

---

# 3. What changed since the protocol

List every material deviation, even if it seemed minor.

Examples:

- changed prompt wording;
- changed model;
- changed number of distractors;
- changed causal criterion;
- skipped failed runs;
- repaired parser during the run;
- changed generation schedule.

```text
Deviations:
```

---

# 4. Experiment 0 metrics

Fill what applies.

| Metric | Value | Notes |
|---|---:|---|
| Structured-output success | | |
| Claim parse success | | |
| Task truth accuracy | | |
| Reported-lineage precision | | |
| Reported-lineage recall | | |
| Tested reported edges with strong/partial causal support | | |
| Hidden causal parent rate | | |
| Causal tests indeterminate | | |

---

# 5. Experiment 1 metrics

| Metric | Value | Notes |
|---|---:|---|
| Primary: cumulative causally infected descendants through G8 | | |
| Mean/median amplification ratio | | |
| `R_mem(1)` | | |
| `R_mem(2)` | | |
| `R_mem(...)` | | |
| Transmission probability per infected exposure | | |
| Repair probability | | |
| De novo mutation rate | | |
| Extinction by G8 | | |
| Clean-world task accuracy | | |
| Mutated-world task accuracy | | |

Where possible, report paired differences and world-level confidence intervals rather than only pooled totals.

---

# 6. Generation table

Example structure:

| Generation | Active infected nodes | New infected children | Repairs | De novo errors | `R_mem` |
|---:|---:|---:|---:|---:|---:|
| 0 | | | | | |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |

---

# 7. Most informative lineage examples

Choose 3–5, not merely the most dramatic.

## Lineage A — successful transmission

```text
World ID:
Mutation seed:
Path:
Why classified as infected:
Causal test:
Unexpected behavior:
Artifact paths/IDs:
```

## Lineage B — extinction or repair

```text
World ID:
Mutation seed:
Path:
Repair/extinction event:
Causal evidence:
Artifact paths/IDs:
```

## Lineage C — de novo mutation / measurement failure

```text
World ID:
What happened:
Why it matters:
Artifact paths/IDs:
```

---

# 8. One full causal counterfactual

Provide the smallest example that makes the intervention understandable.

```text
Original child-producing call ID:
Candidate parent ID:
Original parent content:
Intervention type:
Counterfactual replacement/removal:
Original descendant:
Counterfactual descendant:
Seeds repeated:
Classification: strong / partial / none / indeterminate
Reason:
```

Attach or include the relevant raw prompt/context and response if manageable.

---

# 9. Failures and weirdness

This section is scientifically important.

Track things such as:

- model cited distractors;
- model produced correct claim from infected ancestry;
- model produced false claim in clean world;
- parent ID hallucinations;
- output-schema violations;
- counterfactual runs unstable across seeds;
- mutation spread without obvious semantic copying;
- retrieval never exposed the mutation;
- two independent paths made causal attribution ambiguous;
- oracle/parser disagreement;
- context ordering effects.

```text
Observations:
```

---

# 10. Distribution, not just averages

Include if available:

- histogram/table of infected descendant count per world;
- number of worlds with zero descendants;
- maximum observed cascade;
- median and quartiles;
- clean vs mutated paired differences;
- survival/extinction by generation.

A few large cascades may matter more than the mean.

---

# 11. Runtime and feasibility

```text
Average base call latency:
Average causal rerun latency:
Calls per paired world:
Approximate tokens per paired world:
Disk usage per run:
Main computational bottleneck:
```

This determines whether later experiments should increase worlds, generations, models, or causal sampling.

---

# 12. Your interpretation before external feedback

Keep this short and separate observation from explanation.

```text
What I think happened:
What surprised me:
What I do NOT trust yet:
What I would change next:
```

---

# 13. Decision requested

When returning results for review, choose one:

```text
[ ] Instrumentation is broken; help diagnose it.
[ ] Experiment 0 needs another iteration.
[ ] Lineage appears trustworthy enough for Experiment 1.
[ ] Experiment 1 plumbing works; help design the pilot.
[ ] Pilot is complete; help analyze results and freeze confirmatory design.
[ ] Unexpected phenomenon appeared; help design a targeted experiment.
```
