# Experiment 1 Protocol — Single Mutation Propagation & Epidemiological Dynamics

**Project:** GENE (Genealogical Epistemic Network Experiments)  
**Experiment:** Experiment 1 (Single Mutation Dynamics)  
**Status:** DRAFT / READY FOR IMPLEMENTATION  
**Baseline Instrument Freeze:** `gene-exp0-freeze-v1`  
**Prerequisites:** Experiment 0 Lineage Observability & Causal Assay Passed ($C_{\\text{nec}}=100\\%, H_D=0\\%$)  

---

## 1. Research Question

When a single mutated source fact (an epistemic pathogen / "bad gene") is introduced into an agent's memory substrate, how does it replicate, propagate, and mutate across multiple generations of derived reasoning?

Specifically:
1. **What is the basic reproduction number ($R_0$) of a mutated memory?**
2. **Which infection phenotype dominates downstream memory generation?**
   - Semantic infection ($R_{\\text{semantic}}$): Valid inference from corrupted premises.
   - Epistemic infection ($R_{\\text{epistemic}}$): Erroneous sufficiency estimation under corrupted context.
   - Control infection ($R_{\\text{control}}$): Failure to abstain despite detecting corruption.
3. **Does competing information ecology or exposure filtering attenuate epistemic transmission?**

---

## 2. Experimental Design & Architecture

### 2.1 Paired Clean vs Mutated Micro-Worlds
For each procedural seed:
- **Clean World ($W_{\\text{clean}}$)**: Canonical ground truth.
- **Mutated World ($W_{\\text{mut}}$)**: Exactly one source fact allele is mutated at a specific locus (e.g. `Locus B: Kira -> Tal`).

### 2.2 Multi-Generation Propagation Graph ($G_0 \\to G_1 \\to G_2$)
- **Generation $G_0$**: Ground truth source memories and operational policy rules.
- **Generation $G_1$**: Primary inference tasks executed against $G_0$ memories. Derived claims are written to the append-only memory ledger as $G_1$ nodes.
- **Generation $G_2$**: Secondary multi-hop inference tasks executed against mixed $G_0 + G_1$ memories. Derived claims written as $G_2$ nodes.
- **Generation $G_3$**: Tertiary integration tasks executed against $G_0 + G_1 + G_2$.

---

## 3. Epidemiological & Evolutionary Metrics

### 3.1 Basic Reproduction Number ($R_0$)
The average number of secondary infected derived memory nodes directly citing the mutated ancestor node $M^*$:
$$R_0 = \\frac{1}{|M^*|} \\sum_{n \\in \\text{Descendants}(M^*)} \\mathbb{I}(M^* \\in \\text{CausalAncestors}(n))$$

### 3.2 Infection Phenotype Stratification
Every derived node in generation $G_k$ is classified via the $A/E/K$ diagnostic battery:

1. **Uninfected / Healthy**:
   - $A=1, E=1, K=1$: Derives true claim from uncorrupted branch.
2. **Semantic Carrier ($R_{\\text{semantic}}$)**:
   - $A=0, E=1, K=1$: Emits mutated consequent because it faithfully used the mutated premise.
3. **Epistemic Carrier ($R_{\\text{epistemic}}$)**:
   - $A=0, E=0, K=1$: Emits corrupted claim because context corruption distorted its sufficiency estimate.
4. **Control Carrier ($R_{\\text{control}}$)**:
   - $A=0, E=1, K=0$: Emits corrupted claim despite flagging insufficiency.

---

## 4. Experimental Conditions & Assay Plan

1. **Condition 1 (Baseline Transmission)**: Single mutation in Ecology C with standard exposure retriever.
2. **Condition 2 (Ecology Attenuation)**: Comparing transmission dynamics in Ecology S vs Ecology C.
3. **Condition 3 (Exposure Filtering Intervention)**: Evaluating whether lineage-aware retrieval filtering halts descendant infection.

---

## 5. Required Run Artifacts

```text
runs/
  ├── manifest.json
  ├── world_clean.json
  ├── world_mutated.json
  ├── mutation_locus.json
  ├── lineage_propagation.graphml
  ├── memory_nodes.jsonl
  ├── calls.jsonl
  ├── transmission_matrix.csv
  └── metrics_exp1.json
```
