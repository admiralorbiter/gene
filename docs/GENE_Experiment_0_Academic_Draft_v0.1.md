# GENE: From Reported Support to Causal Lineage in Large Language Models

**Draft v0.1 — Experiment 0 paper**  
**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Status:** Working academic draft  
**Author:** [Author name]  
**Date:** August 2026

> **Working title alternatives**
>
> 1. *Who Is the Parent of a Claim? Causal Lineage Calibration in Large Language Models*
> 2. *GENE: A Counterfactual Assay for Information Lineage, Epistemic State, and Abstention in LLMs*
> 3. *Exposure Is Not Ancestry: Measuring Causal Support in Language Model Reasoning*

---

## Abstract

Long-term memory systems for language-model agents increasingly treat retrieved information as reusable evidence for later reasoning. Yet the provenance of a model output is not straightforward: information may be present in context without affecting the output, a model may cite evidence that is not behaviorally necessary, and a valid causal parent may appear non-necessary when alternative cues or redundant derivations remain available. Before studying how erroneous memories propagate across generations, we therefore ask a more basic measurement question: **what does it mean for one piece of information to be a parent of a model claim?**

We introduce **GENE (Genealogical Epistemic Network Experiments)**, a controlled synthetic-world assay that distinguishes three forms of informational ancestry: **formal derivational ancestry**, **model-reported support**, and **counterfactually demonstrated behavioral influence**. GENE uses machine-readable micro-worlds with symbolic ground truth, model-facing memory identifiers, and interventions including knockout, semantic mutation, matched foil controls, and sequential rescue. We further separate two failure mechanisms that ordinary answer accuracy conflates: **epistemic-state estimation**—whether the model correctly judges that available evidence is sufficient—and **policy consistency**—whether its final answer complies with that judgment.

We calibrate the assay on Gemma 3 12B in a hardened \(2 \times 2\) factorial experiment crossing **information ecology** (single-consequent versus matched competing-consequent rules) with **response contract** (implicit versus explicit sufficiency/abstention semantics). Across 276 live model calls in six counterbalanced synthetic worlds, intervention pass rates were 46.7%, 86.7%, 65.2%, and 100.0% across the four cells. The explicit response contract substantially reduced detection-to-action failures, while competing consequents reduced false sufficiency judgments caused by single-conclusion salience. Under the combined condition, all 66 intervention tests passed, including premise and rule knockouts, directional semantic mutations, unmatched mutations, matched foil controls, and sequential rescue.

These results are not evidence of universal causal faithfulness in LLMs; rather, they show that **causal-lineage measurement is itself sensitive to the information environment and output contract used to elicit model behavior**. GENE provides an auditable instrument for separating exposure, self-reported support, epistemic estimation, behavioral necessity, directional counterfactual sensitivity, and repair. We argue that such distinctions are prerequisites for rigorous study of persistent-memory contamination and downstream information propagation.

---

## 1. Introduction

Language-model systems are increasingly being given memory.

The dominant evaluation question has therefore been straightforward: **can the system remember what it needs later?** Long-term memory benchmarks measure information extraction across large histories, temporal reasoning, knowledge updates, premise awareness, and abstention under sustained interaction (Wu et al., 2024; Wu et al., 2026). These capabilities matter because an agent that cannot reliably retrieve prior experience cannot become a useful long-running assistant.

Persistent memory, however, creates a complementary problem.

A retrieved memory can be clear, stable, and easy to reuse while still being wrong. Once an erroneous claim has been written into persistent state, later model calls may no longer need to hallucinate independently: they can reason correctly from a false premise. Recent work on agent memory has therefore begun to study contamination, provenance, write admission, and the downstream authority of persistent state (Ouyang & Hou, 2026; Zhang & Li, 2026). These systems raise an upstream measurement problem that remains deceptively difficult:

> **How do we know which earlier memories actually gave rise to a later claim?**

A naive answer is to ask the model.

Modern language models readily provide explanations, citations, or lists of evidence they claim to have used. But explanation faithfulness is not guaranteed. Madsen et al. (2024), for example, find that the faithfulness of LLM self-explanations varies substantially across tasks, models, and explanation forms. Atanasova et al. (2023) similarly motivate explicit tests of whether natural-language explanations track the factors responsible for a prediction. These findings suggest that a model-reported source should be treated as a **self-report**, not as direct evidence of causal ancestry.

A second naive answer is deletion: remove a candidate parent and see whether the answer changes. This is stronger, but also incomplete. Removing information can create an unnatural context, and a genuine parent may be individually non-necessary when redundant cues or alternate derivations remain. Kamahi and Yaghoobzadeh (2024) argue that deletion and corruption tests can create out-of-distribution inputs for autoregressive models and propose fluent counterfactual edits as a stronger faithfulness test. Siegel et al. (2024) further show that binary answer flips can miss meaningful counterfactual effects visible in the model's output distribution.

GENE begins from the premise that **informational ancestry is not one relation**.

We distinguish at least three:

1. **Exposure ancestry:** Was the memory physically present in the model's context?
2. **Reported ancestry:** Did the model explicitly identify that memory as supporting its answer?
3. **Causal ancestry:** Does a controlled intervention on that memory change downstream model behavior in the direction predicted by the formal world?

This paper reports **Experiment 0**, whose purpose is not to study long-run memory contamination directly. Instead, Experiment 0 calibrates the instrument required to study such contamination later. We construct fictional, machine-readable micro-worlds with exact symbolic ground truth and use them to test whether the model behaves consistently under knockout, semantic mutation, control interventions, and rescue.

The experiment produced an additional distinction. In several early conditions, the model explicitly recognized that evidence was missing yet still emitted a specific answer. This resembles the **detection-to-abstention gap** described by Gu et al. (2026), who show that reasoning models can detect underspecified problems without translating that detection into abstention. We therefore separate:

\[
\text{Information Environment}
\rightarrow
\text{Epistemic Estimation}
\rightarrow
\text{Response Policy}
\rightarrow
\text{Claim}.
\]

Experiment 0 asks whether failures arise because the model incorrectly judges its evidence or because it correctly recognizes insufficiency and nevertheless answers.

Our primary contributions are:

- **A lineage measurement framework** separating formal ancestry, exposure, model-reported support, and counterfactual behavioral influence.
- **A controlled intervention battery** including knockout, matched foil removal, directional semantic mutation, unmatched mutation, and sequential rescue.
- **A two-stage epistemic decomposition** distinguishing evidence-state estimation from policy compliance.
- **A \(2\times2\) calibration study** showing that both information ecology and response contract materially alter the reliability of causal-lineage measurements.
- **An auditable experimental substrate** in which prompts, model outputs, memory identifiers, interventions, and oracle evaluations are persisted for replay.

The central claim is deliberately methodological:

> **A model's apparent causal lineage is partly a property of the assay used to expose it. Before studying how erroneous memories reproduce, the measurement environment itself must be calibrated.**

---

## 2. Related Work

### 2.1 Long-term memory evaluation

Long-term agent-memory research has largely focused on whether a system can preserve and recover useful information across extended histories. LongMemEval evaluates extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention over sustained interactions (Wu et al., 2024). LongMemEval-V2 extends this framing toward environment-specific experience, including workflows, dynamic state, recurring failure modes, and premise awareness (Wu et al., 2026).

GENE addresses a complementary question. Rather than asking whether the correct memory can be recovered, Experiment 0 asks **how downstream claims should be attributed to the information that was exposed to the model**. This attribution problem becomes increasingly important as memory is reused as evidence rather than merely recalled as text.

### 2.2 Persistent memory contamination and lineage

Recent work increasingly treats memory as a security and epistemic boundary. ConsistencyGate frames false-memory accumulation as a write-admission problem: once a hallucinated fact is stored, it can be reused as a premise in later reasoning (Zhang & Li, 2026). MemLineage attaches provenance and derivational lineage to memory entries and uses ancestry as part of downstream policy enforcement (Ouyang & Hou, 2026).

GENE is related but orthogonal in emphasis. These systems primarily propose defenses or governance mechanisms. Experiment 0 instead focuses on **measurement calibration**: when a system claims that memory \(m_i\) supports claim \(c_j\), what observable evidence justifies treating \(m_i\) as an ancestor?

### 2.3 Explanation faithfulness and self-reported support

The distinction between plausible explanations and faithful explanations is well established. Atanasova et al. (2023) propose counterfactual and reconstruction-based tests for natural-language explanation faithfulness. Madsen et al. (2024) apply self-consistency tests to LLM self-explanations and show that faithfulness depends strongly on model, task, and explanation format.

GENE therefore treats model-emitted parent IDs as **reported-support edges**, not ground-truth causal edges. A cited parent may be irrelevant, redundant, or merely plausible. Conversely, a memory may influence an output without appearing in the reported-support set.

### 2.4 Counterfactual evaluation

Faithfulness is often tested by removing or corrupting purportedly important input features. Kamahi and Yaghoobzadeh (2024) note that such perturbations can create out-of-distribution contexts for autoregressive language models and propose fluent counterfactual generation to evaluate attribution methods. Siegel et al. (2024) argue that counterfactual evaluation should consider distributional movement rather than only binary label flips.

GENE's intervention ladder follows a similar motivation. We begin with deletion-style knockouts but add **directional semantic mutation**: rather than asking only whether a prediction disappears, we ask whether changing a premise from one valid value to another steers the model toward the specifically predicted counterfactual outcome. Sequential rescue then tests whether restoring the original premise restores the original output.

### 2.5 Abstention as control

Gu et al. (2026) identify a detection-to-abstention gap in reasoning models: a model may recognize insufficient information yet continue to reason and produce an unsupported answer. They frame abstention as a control decision rather than merely a final-answer style.

Experiment 0 independently exposes a closely related distinction. We separate **epistemic estimation** from **response policy consistency**, allowing us to distinguish cases where the model misjudges the evidence from cases where it judges the evidence correctly and still fails to abstain.

---

## 3. GENE Measurement Framework

### 3.1 Synthetic worlds

GENE uses fictional symbolic micro-worlds to avoid external factual ambiguity and to make exact derivations mechanically enumerable. A world consists of atomic facts, inference rules, and queries.

A simplified example is:

- `manager(VELORA, NERIN)`
- `reports_to(NERIN, KIRA)`
- if a station's manager reports to Kira, the station uses `PROTO_X7`.

The corresponding query is:

> Which security protocol does Velora use?

The world is deliberately artificial. Its role is analogous to a wind tunnel: it sacrifices ecological realism in order to isolate a small number of causal mechanisms.

Each fact and rule has a stable machine-readable identifier. Model-facing prompts contain natural-language renderings plus opaque memory IDs. The symbolic oracle computes deductive closure and valid support paths independently of the language model.

### 3.2 Three lineage graphs

GENE represents informational ancestry at three levels.

#### Exposure graph

An exposure edge \(m_i \rightarrow c_j\) exists if memory \(m_i\) was physically present in the prompt that produced claim \(c_j\).

Exposure is necessary for direct prompt-mediated influence but is not sufficient evidence of causal relevance.

#### Reported-support graph

A reported-support edge exists when the model explicitly names \(m_i\) as a supporting parent of \(c_j\).

These edges are model self-reports. They are useful measurements, but they are not interpreted as hidden chain-of-thought or direct access to internal computation.

#### Causal graph

A causal edge is supported when an intervention on \(m_i\) changes model behavior in a manner predicted by the experimental oracle.

A single knockout is not always sufficient to establish or reject causality because redundant support can make a genuine parent individually non-necessary. We therefore use multiple intervention types.

### 3.3 Intervention battery

The hardened Experiment 0 assay includes:

- **No-op sham:** identical replay to measure stability.
- **Premise knockout:** remove a required fact.
- **Active-rule knockout:** remove the rule used by the formal derivation.
- **Foil-rule knockout:** remove an irrelevant competing rule.
- **Double knockout:** remove both premises simultaneously.
- **Directional semantic mutation:** replace a valid premise value with another value that should redirect the output to a different matched consequent.
- **Unmatched mutation:** replace the premise with a value matching no rule; expected behavior is abstention.
- **Sequential rescue:** mutate the premise, observe the redirected phenotype, restore the original premise from the mutated state, and test whether the original phenotype returns.
- **Distractor knockout:** remove an irrelevant fact.

The distinction between mutation and deletion is central. If:

\[
KIRA \rightarrow PROTO\_X7,
\]

then mutating the supervisor to Tal should produce:

\[
TAL \rightarrow PROTO\_Q2,
\]

not merely "something different." This provides a directional counterfactual test.

### 3.4 Locus and allele

GENE borrows two terms from genetics as operational nomenclature.

A **locus** is a stable memory slot identity. An **allele** is the semantic proposition currently occupying that slot. A semantic mutation changes the allele while preserving the locus.

This terminology is not intended to imply that LLM memory is literally biological. It enforces a useful systems distinction between:

- identity of a memory location;
- semantic content at that location;
- deletion of the location;
- modification of the content.

---

## 4. Two-Stage Epistemic Decomposition

Early experiments revealed that output accuracy alone collapses qualitatively different failure modes.

We therefore define three diagnostics.

### 4.1 Answer behavior \(A\)

For an intervention \(I\), let \(y_I^\*\) be the oracle-predicted output under the counterfactual world and let \(\hat y_I\) be the model output.

\[
A = \mathbb{1}[\hat y_I = y_I^\*].
\]

### 4.2 Epistemic-state accuracy \(E\)

Schema v2 requires the model to emit an explicit evidence status:

- `sufficient`
- `insufficient`
- `conflicting`

Let \(e_I^\*\) be the oracle-derived evidence status for the exposed context and \(\hat e_I\) the model-emitted status.

\[
E = \mathbb{1}[\hat e_I = e_I^\*].
\]

Importantly, \(E\) is not interpreted as direct access to the model's hidden beliefs. It is an observable, model-emitted judgment about answerability.

### 4.3 Policy consistency \(K\)

The response contract specifies that `insufficient` or `conflicting` evidence should produce `UNKNOWN`.

\[
K =
\mathbb{1}
\left[
(\hat e_I \in \{\text{insufficient}, \text{conflicting}\})
\Rightarrow
(\hat y_I = \text{UNKNOWN})
\right].
\]

This yields at least two distinct failure modes.

#### Detection-to-action failure

\[
A=0,\quad E=1,\quad K=0.
\]

The model recognizes that the evidence is insufficient but emits a specific answer anyway.

#### Epistemic-estimation failure

\[
A=0,\quad E=0,\quad K=1.
\]

The model incorrectly judges the evidence to be sufficient and then behaves consistently with that incorrect judgment.

This decomposition became the basis of the factorial experiment.

---

## 5. Experimental Design

### 5.1 Model and execution environment

The frozen Experiment 0 assay used:

- **Model:** `gemma3:12b` served locally through Ollama
- **Temperature:** 0
- **Context window:** 4096
- **Hardware:** NVIDIA RTX 3060 12GB; AMD Ryzen 7 5700G
- **Total live calls:** 276

The model digest, environment, prompts, run configuration, raw responses, token counts, and timing telemetry were captured in the experiment ledger.

### 5.2 Factor 1: information ecology

We compare two prompt ecologies.

#### Ecology S: single consequent

Only one relevant rule/conclusion is visible.

This condition initially appeared attractive because it minimized context. In pilot testing, however, the single rule's conclusion token could become a salient fallback even when one of its antecedents was missing.

#### Ecology C: competing consequents

Three syntactically matched rules are exposed simultaneously:

\[
KIRA \rightarrow PROTO\_X7
\]

\[
TAL \rightarrow PROTO\_Q2
\]

\[
MIRA \rightarrow PROTO\_M9.
\]

The opaque consequent mapping is rotated across worlds, and rule ordering is counterbalanced. This forces the model to discriminate among multiple plausible outcomes rather than selecting the only visible answer token.

### 5.3 Factor 2: response contract

#### Schema v1

A looser JSON contract without an explicit evidence-state/abstention policy.

#### Schema v2

A structured response containing an evidence status plus an explicit rule:

> If evidence is insufficient or conflicting, return `UNKNOWN`.

The evaluator preserves raw model behavior and does not convert contradictory responses into abstention after generation.

### 5.4 Counterbalancing

Six canonical micro-worlds were used in all four factorial cells. These cover all six rule-order permutations and all three supervisor-to-protocol mappings marginally. Interventions are repeated measurements within worlds; the calls should therefore not be treated as independent experimental units.

### 5.5 Factorial cells

The four conditions are:

1. Ecology S + Schema v1
2. Ecology S + Schema v2
3. Ecology C + Schema v1
4. Ecology C + Schema v2

The purpose is mechanistic calibration rather than population-level inference. We report descriptive intervention success and failure patterns and treat the small number of worlds as a limitation.

---

## 6. Results

### 6.1 Overall factorial results

| Cell | Ecology | Schema | Model calls | Intervention tests | Passed | Pass rate |
|---|---|---|---:|---:|---:|---:|
| 1 | Single consequent | v1 | 66 | 60 | 28 | **46.7%** |
| 2 | Single consequent | v2 | 66 | 60 | 52 | **86.7%** |
| 3 | Competing consequents | v1 | 72 | 66 | 43 | **65.2%** |
| 4 | Competing consequents | v2 | 72 | 66 | 66 | **100.0%** |

Across the full hardened factorial, 276 model calls were executed.

The pattern suggests that the two manipulations address different failure surfaces.

### 6.2 Response contract and the detection-to-action gap

In the original single-consequent v1 condition, knockout calls sometimes produced a striking split: the model's response text indicated that relevant evidence was missing, yet the structured answer field still contained the sole visible conclusion.

Schema v2 substantially changed this behavior. When the model emitted an insufficient evidence status, the explicit contract reliably mapped that judgment to abstention in the tested assay.

We interpret this as a reduction in **policy inconsistency \(K\)** rather than a general improvement in logical reasoning.

This interpretation parallels the detection-to-abstention distinction formalized by Gu et al. (2026): recognizing insufficient evidence and acting on that recognition are separable behaviors.

### 6.3 Information ecology and false sufficiency

Schema v2 did not solve all failures in Ecology S.

Under semantic mutations that changed a rule antecedent, the model could still judge the single visible rule as applicable even when the mutated value no longer satisfied its antecedent. In these cases:

\[
A=0,\quad E=0,\quad K=1.
\]

The model was not violating its own evidence judgment; it was making the wrong evidence judgment.

Introducing matched competing consequents changed this behavior. When Kira, Tal, and Mira each mapped to a distinct opaque output, semantic mutations redirected the model to the predicted alternative rule rather than leaving the original conclusion as a default attractor.

This suggests that **information ecology can alter epistemic-state estimation even when the model and task semantics are otherwise unchanged**.

### 6.4 Directional mutation

Directional mutations produced one of the strongest calibration signals.

If the baseline relation supported `PROTO_X7`, changing the relevant premise from Kira to Tal was expected to redirect the answer to the Tal-associated protocol. In the hardened competing-consequent + Schema v2 condition, these redirections were correct across all six worlds.

A second mutation to Mira likewise redirected the outcome to the appropriate alternative.

Directional mutation provides stronger evidence than a generic answer flip because the counterfactual direction is pre-specified by the symbolic world.

### 6.5 Unmatched mutation

A mutation to an unmatched supervisor, Soren, had no valid rule consequent.

The expected result was therefore `UNKNOWN`.

This condition distinguishes **counterfactual steering** from a generic tendency to choose one of the visible protocol tokens. In Cell 4, all unmatched mutations correctly abstained.

### 6.6 Sequential rescue

Rescue was executed compositionally:

\[
S_0(\text{Kira})
\xrightarrow{\text{mutation}}
S_1(\text{Tal})
\xrightarrow{\text{rescue}}
S_2(\text{Kira}).
\]

The expected output trajectory was:

\[
X7 \rightarrow Q2 \rightarrow X7.
\]

Cell 4 restored the original output in all six worlds.

This sequence is useful because it tests reversible state dependence rather than merely comparing two independent prompts.

### 6.7 Cell 4 intervention battery

In the combined competing-consequent + Schema v2 condition:

- baseline: 6/6
- no-op replay: 6/6
- premise A knockout: 6/6
- premise B knockout: 6/6
- active-rule knockout: 6/6
- foil-rule knockout: 6/6
- double knockout: 6/6
- Kira→Tal mutation: 6/6
- Kira→Mira mutation: 6/6
- unmatched mutation: 6/6
- sequential rescue: 6/6
- distractor knockout: 6/6

The intervention total was 66/66.

This is best interpreted as **assay calibration under the tested condition**, not as evidence that the model is universally faithful or logically perfect.

---

## 7. Discussion

### 7.1 Exposure, citation, and causality are different relations

The most important result of Experiment 0 may be conceptual rather than numerical.

A memory can be:

- exposed but irrelevant;
- cited but behaviorally unnecessary;
- causally influential but not individually necessary because another cue remains;
- formally required by the symbolic derivation while the model reaches the same answer through a shortcut.

This means that "what did the model use?" does not have a single observational answer.

Reported-support edges are valuable because they describe the model's explicit attribution. But explanation-faithfulness research gives good reason not to equate them with causal ancestry (Atanasova et al., 2023; Madsen et al., 2024).

Likewise, knockout necessity is informative but does not exhaust causality. A single deletion can fail to change an answer because the prompt contains redundant or conclusion-salient information. Directional mutation and rescue provide complementary tests.

### 7.2 The assay can manufacture or remove apparent causal failures

The factorial experiment demonstrates a methodological hazard.

Under a single-consequent information ecology, the model often failed antecedent-sensitive interventions. Under a matched competing-consequent ecology, the same basic reasoning relation became much easier to diagnose causally.

Therefore a poor knockout score can reflect at least two possibilities:

1. the model is genuinely insensitive to the candidate premise;
2. the assay leaves another shortcut that preserves the output.

This is particularly important for black-box faithfulness research. If a perturbation changes more than the intended causal variable—or leaves a highly salient alternative cue—its result may be misinterpreted.

Kamahi and Yaghoobzadeh's (2024) critique of destructive perturbations motivates the same general lesson: counterfactual evaluation depends on the quality of the intervention.

### 7.3 Epistemic judgment and behavioral control should be evaluated separately

The \(E/K\) distinction is also consequential.

A system can fail because it does not know that its evidence is insufficient.

Or it can fail because it knows that its evidence is insufficient and continues anyway.

These are not equivalent safety problems and likely require different interventions.

Schema v2 primarily improved the second behavior: when insufficiency was explicitly represented, the response contract made abstention reliable in the calibrated condition.

Competing consequents primarily improved the first: the model was less likely to misclassify a mismatched premise as sufficient.

This suggests that abstention systems should not be evaluated only on whether the final output is `UNKNOWN`. A useful evaluation should ask whether:

1. the model's explicit answerability assessment is correct;
2. the response policy follows that assessment.

### 7.4 Information ecology is part of model behavior

The term **information ecology** is useful because the intervention does not change model weights.

Instead, it changes the local structure of alternatives available to the model.

The same rule can behave differently when it is:

- the only visible conclusion;
- one of several matched alternatives.

This does not imply that "more context is better." Rather, structured alternatives can remove shortcuts that are otherwise invisible in a sparse prompt.

For benchmark design, this creates a practical recommendation:

> **When testing whether an LLM respects a rule antecedent, do not make the correct conclusion the only plausible conclusion token in the context.**

Matched alternatives provide a stronger control.

### 7.5 A genealogy requires more than provenance

Traditional provenance asks where a piece of information came from.

GENE extends this toward a stronger notion:

\[
\text{source}
\rightarrow
\text{exposure}
\rightarrow
\text{reported support}
\rightarrow
\text{intervention}
\rightarrow
\text{derived claim}.
\]

A full genealogy is not merely a citation trail. It records how information changes, whether it remains behaviorally active, and whether changes to an ancestor predict changes in descendants.

This distinction becomes especially relevant for persistent memory systems, where a derived claim may later become a premise for additional generations.

---

## 8. Limitations

Experiment 0 is intentionally a calibration study and has substantial limitations.

### 8.1 One primary live model

The hardened factorial was executed on Gemma 3 12B. The results should not be assumed to generalize to other model families, scales, or training regimes. Cross-model replication is a high-priority next step if the goal is a broader claim about LLM behavior.

### 8.2 Small number of worlds

The experiment uses six counterbalanced synthetic worlds. Intervention calls are repeated measurements within worlds and are not statistically independent. The current results are most appropriately interpreted descriptively and mechanistically.

A larger confirmatory study could fully cross rule order and consequent mapping and expand the number of entities/world instantiations.

### 8.3 Synthetic deductive tasks

The micro-worlds are deliberately simple and machine-readable. They isolate causal mechanisms but do not reproduce the ambiguity, retrieval noise, conflicting sources, compression, or domain knowledge present in deployed memory systems.

This is a feature for calibration and a limitation for external validity.

### 8.4 Explicit epistemic status is an output, not direct introspection

The model's `evidence_status` is an observable generated judgment. It should not be interpreted as direct measurement of internal belief, confidence, hidden chain-of-thought, or neural state.

### 8.5 Discrete output evaluation

Experiment 0 primarily evaluates categorical output changes. Distributional counterfactual metrics may detect weaker forms of influence that do not cross the discrete decision boundary (Siegel et al., 2024).

### 8.6 Causal claims are assay-relative

GENE's causal evidence is intervention-based and behaviorally operational. It does not identify internal neural mechanisms. A memory can be behaviorally necessary under one prompt ecology and redundant under another.

---

## 9. Implications for Persistent Memory

Experiment 0 does not yet measure multi-generation propagation. Its role is to make that future experiment interpretable.

If a persistent system stores a derived claim, that claim may later be exposed as a new premise. At that point, the difference between:

- formal ancestry,
- reported support,
- behavioral influence,
- epistemic estimation,
- response-policy consistency

becomes necessary for describing how an error propagated.

Recent memory systems already motivate this concern. ConsistencyGate treats write-time admission as a protection against storing unsupported facts that later become reusable premises (Zhang & Li, 2026), while MemLineage uses provenance and derivational ancestry to constrain the authority of downstream memory (Ouyang & Hou, 2026).

GENE's next-stage question is therefore not merely whether a false answer persists, but whether a specific informational ancestor produces identifiable descendants and whether the failure phenotype changes as the lineage reproduces.

Experiment 0 supplies the measurement vocabulary required to ask that question.

---

## 10. Conclusion

Before asking how misinformation propagates through persistent language-model memory, we need a defensible answer to a simpler question:

> **When does one memory count as a parent of another claim?**

Experiment 0 shows that the answer cannot be reduced to context presence, model citation, or single-feature deletion.

Formal ancestry, reported support, and counterfactual behavioral influence can diverge. Moreover, the apparent causal behavior of the model depends on the structure of the information environment and the response contract used to elicit it.

In our controlled Gemma 3 12B assay, an explicit evidence-status/abstention contract reduced detection-to-action failures, while matched competing consequents reduced false sufficiency judgments caused by single-conclusion salience. Combining both yielded perfect performance across the frozen intervention battery, including deletion, directional mutation, unmatched mutation, controls, and sequential rescue.

The result should not be read as a claim of universal model faithfulness. It is instead a result about **measurement design**:

> **Causal lineage in language models must be experimentally constructed, not assumed from plausible explanations or convenient perturbations.**

GENE provides one framework for constructing that measurement.

---

# References

Atanasova, P., Camburu, O.-M., Lioma, C., Lukasiewicz, T., Simonsen, J. G., & Augenstein, I. (2023). *Faithfulness Tests for Natural Language Explanations*. Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), 283–294. https://doi.org/10.18653/v1/2023.acl-short.25

Gu, R., Li, J., Wang, Y., Yue, Y., Xiao, H., Chen, Y., Wang, Y., Guo, C., Wei, P., Gu, J., & Cao, Y. (2026). *Bridging the Detection-to-Abstention Gap in Reasoning Models under Insufficient Information*. arXiv:2605.28070.

Kamahi, S., & Yaghoobzadeh, Y. (2024). *Counterfactuals As a Means for Evaluating Faithfulness of Attribution Methods in Autoregressive Language Models*. Proceedings of the 7th BlackboxNLP Workshop, 452–468. https://doi.org/10.18653/v1/2024.blackboxnlp-1.28

Madsen, A., Chandar, S., & Reddy, S. (2024). *Are self-explanations from Large Language Models faithful?* Findings of the Association for Computational Linguistics: ACL 2024, 295–337. https://doi.org/10.18653/v1/2024.findings-acl.19

Ouyang, C., & Hou, R. (2026). *MemLineage: Lineage-Guided Enforcement for LLM Agent Memory*. arXiv:2605.14421.

Siegel, N., Camburu, O.-M., Heess, N., & Perez-Ortiz, M. (2024). *The Probabilities Also Matter: A More Faithful Metric for Faithfulness of Free-Text Explanations in Large Language Models*. Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), 530–546. https://doi.org/10.18653/v1/2024.acl-short.49

Wu, D., Wang, H., Yu, W., Zhang, Y., Chang, K.-W., & Yu, D. (2024). *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory*. arXiv:2410.10813.

Wu, D., Ji, Z., Kawatkar, A., Kwan, B., Gu, J.-C., Peng, N., & Chang, K.-W. (2026). *LongMemEval-V2: Evaluating Long-Term Agent Memory Toward Experienced Colleagues*. arXiv:2605.12493.

Zhang, Y., & Li, S. (2026). *ConsistencyGate: Preventing Memory Contamination in LLM Agents via Self-Consistency Admission Control*. arXiv:2607.22962.

---

# Draft notes before submission

These are not part of the manuscript.

## What is already strong enough to keep

- The three-graph lineage distinction.
- The intervention ladder.
- The A/E/K decomposition.
- The hardened 2×2 design.
- The full Cell 4 truth table.
- The cautious interpretation as calibration rather than universal faithfulness.
- The connection to self-explanation faithfulness and detection-to-abstention.

## What I would add before aiming at a main-track full paper

1. **Cross-model replication.**  
   At minimum one additional open model family, ideally two, with the same frozen assay.

2. **More independent worlds.**  
   Six is enough for a methods/calibration paper or workshop/preprint, but weak for broad population claims.

3. **A compact world-level statistical analysis.**  
   Treat worlds as clusters; report paired world-level contrasts rather than treating all intervention calls as independent.

4. **One figure showing the intervention logic.**  
   Baseline Kira→X7, mutation Tal→Q2, unmatched Soren→UNKNOWN, rescue Tal→Kira→X7.

5. **One figure showing the three lineage graphs.**  
   Exposure vs reported support vs causal.

6. **Potential distributional follow-up.**  
   Optional log-probability counterfactual analysis could strengthen the connection to Siegel et al. without changing the paper's main contribution.

## Likely publication posture

- **Ready now:** public preprint / workshop paper / methods paper draft.
- **Probably needs replication:** strong main-track empirical claim about LLMs generally.
- **Does not need to wait for Experiment 1:** Experiment 0 has a complete scientific arc on its own.
