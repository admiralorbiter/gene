# Source Library — Podcast V2

This library is intentionally biased toward sources **not used as major narrative anchors in Podcast V1**.

The podcast generator should use these to support stories, not to read citations aloud.

---

# A. Manuscript genealogy / stemmatics

## Written cultures as complex transmission systems

**Use for:** manuscript family trees, shared errors, lost ancestors, textual extinction, transmission as branching history.

- https://pmc.ncbi.nlm.nih.gov/articles/PMC13339094/

Useful conceptual points:

- surviving manuscripts are “witnesses” to a transmission history;
- common errors/innovations can help infer genealogy;
- reconstructed stemmata contain surviving and hypothetical ancestors;
- textual traditions can lose branches and preserve others.

## Oxford Handbook — Recension / stemmatics

**Use for:** shared errors and the limitation introduced by contamination across multiple exemplars.

- https://academic.oup.com/edited-volume/62564/chapter-abstract/560047309

Key point:

> A clean tree works best when transmission is vertical; horizontal contamination can make the genealogy network-like.

## Open Stemmata

**Use for:** explaining that textual family trees are a real scholarly object, not an analogy invented for the podcast.

- https://eadh2021.culintec.de/CAMPS_Jean_Baptiste__em_Open_Stemmata__em___A_Digital_Collec.html

---

# B. Copied citations / inherited bibliographic errors

## Simkin & Roychowdhury

**Use for:** citation typos as lineage markers; apparent source count vs independent verification.

- https://arxiv.org/abs/cond-mat/0305150

## U.S. Office of Research Integrity summary

**Use for:** readable secondary summary of the shared-miscitation argument.

- https://ori.hhs.gov/how-many-cited-papers-are-not-read-citing-authors

Guardrail:

Do not present the study's estimate of how often papers are actually read as universally established. Use only the robust storytelling point that **identical bibliographic errors can propagate through copying**.

---

# C. Kinetic proofreading

## Hopfield, 1974

**Use for:** extra verification step before commitment; reliability can require time/energy spent on rejection.

- https://pmc.ncbi.nlm.nih.gov/articles/PMC434344/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/4530290/

Podcast connection:

```text
initial recognition
    ↓
extra verification
    ↓
commit
```

Do not call the GENE validator a literal implementation of kinetic proofreading.

---

# D. Immunological tolerance / autoimmunity framing

## Burnet Nobel lecture

**Use for:** self/non-self recognition, tolerance as part of effective immunity.

- https://www.nobelprize.org/uploads/2018/06/burnet-lecture.pdf

## Nobel scientific background on immune tolerance

**Use for:** historical story of Burnet/Medawar and acquired tolerance; clonal-selection/negative-selection context.

- https://www.nobelprize.org/uploads/2025/10/advanced-medicineprize2025-1.pdf

Podcast connection:

> Better defense is not maximal aggression; specificity creates both protection and autoimmunity risk.

---

# E. Continued influence / correction

## Ecker et al., Nature Reviews Psychology (2022)

**Use for:** misinformation continuing to influence reasoning after correction; barriers to knowledge revision; correction/prebunking nuance.

- https://www.nature.com/articles/s44159-021-00006-y

## Reminders and corrections, Scientific Reports

**Use for:** the more nuanced point that reactivating old misinformation during correction can sometimes support integrative updating rather than simply backfire.

- https://www.nature.com/articles/s41598-022-25649-6

Podcast connection:

> Explicit conflict may sometimes be easier to update than an invisible gap — a conceptual rhyme with GENE's mismatch-vs-missing-evidence result, not the same mechanism.

---

# F. Current LLM persistent-memory security / governance

Use the repository's `docs/RESEARCH_POSITIONING.md` as the primary maintained link map because this literature is moving quickly.

Important families of work:

- LongMemEval / LongMemEval-V2
- LoCoMo
- State Contamination
- ConsistencyGate
- Memory Contagion
- MemLineage
- MAP-Graph
- Memory Provenance Laundering / PPMF
- Governed Collaborative Memory as Artificial Selection
- Hidden in Memory: Sleeper Memory Poisoning
- Remembering More, Risking More
- Securing LLM-Agent Long-Term Memory Against Poisoning
- MemGuard

Podcast use:

> The field increasingly agrees that persistent memory is a security and epistemic boundary. GENE's narrower contribution is to make claim-level reproduction and lineage experimentally traceable under exact synthetic ground truth.

Do not claim GENE invented provenance-aware memory, write gating, or memory contamination research.

---

# G. Internal GENE sources for the sequel

Use the frozen/current reports rather than intermediate narrative summaries.

Core documents:

- `docs/EXPERIMENT_0_FINAL_REPORT.md`
- `docs/results/EXPERIMENT_1A_REPORT.md`
- `docs/results/EXPERIMENT_1B_REPORT.md`
- `docs/results/EXPERIMENT_1B_B_REPORT.md`
- `docs/results/EXP1B_B1C_MATCHED_EXPRESSION_REPORT.md`
- `docs/results/EXP1B_C1B_SHARED_ECOLOGY_REPORT.md`
- `docs/results/EXP1B_C2A_LIVE_ASSAY_REPORT.md`
- `docs/results/EXP1B_C2B_BINDING_REPORT.md`
- `docs/ARCHITECTURE.md`
- `docs/DEVELOPMENT_PLAN.md`

If a canonical machine-readable results manifest exists by podcast-generation time, prefer it for headline denominators/numbers.

---

# H. Old podcast packet — callback only

The original packet is at:

- `docs/GENE_PODCAST_PACKET/`

It is useful for knowing what the listener may already have heard.

Do not reuse its outside-story sections as the main explanatory material in V2.

The GENE Experiment 0 recap can overlap, but compress it aggressively.

---

# I. Source hierarchy for factual claims

Prefer:

1. original paper / official report;
2. peer-reviewed review article;
3. official historical institution source;
4. reputable secondary summary only for storytelling context.

For GENE claims, prefer:

1. frozen DB/results manifest;
2. experiment report tied to immutable execution commit;
3. architecture/development summary;
4. podcast packet only as narrative guidance.

---

# J. Final generation check

Before generating audio, verify:

- all headline GENE denominators against the latest frozen report/results manifest;
- any newly published 2026 memory papers that materially change research positioning;
- the old audio/transcript if available, specifically for accidental repeated stories or jokes.
