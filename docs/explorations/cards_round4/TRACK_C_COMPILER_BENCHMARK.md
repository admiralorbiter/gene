# Experiment Card — Track C: Epistemic Context Compiler Conformance Benchmark

## 1. Core Hypothesis & Systems Mission
- **Core Systems Hypothesis:** An Epistemic Context Compiler translating explicit Intermediate Representations (`EpistemicIR`) into structured neural contexts can significantly reduce serialization sensitivity, eliminate presentation-order fragility, and prevent ancestry laundering without modifying the underlying frozen LLM weights.
- **The Conformance Objective:** The compiler is evaluated not on arbitrary prompt optimization ("which prompt gets higher accuracy?"), but on **conformance invariance** ("does the compiled prompt preserve the machine-readable semantics of the epistemic state?").

## 2. Compiler Backends Evaluated
1. **`raw_flat`**: Naive list concatenation of active retrieved memories.
2. **`canonical_support_blocks`**: Groups premises by formal derivation pathways ($S_F$).
3. **`lineage_deduplicated`**: Resolves multi-copy descendant documents ($N_{\text{vis}}=4, N_{\text{root}}=1$) into a single consolidated ancestral root before serialization.
4. **`support_certificate`**: Generates a verified derivation audit certificate prepended to the evidence base.

## 3. Conformance Benchmark Metrics
- **Worst-Case Accuracy Across Permutations:** Minimum accuracy achieved over all test orderings.
- **Serialization Disagreement Rate:** Pairwise inconsistency between semantically equivalent prompt serializations.
- **Unsupported Concrete Output Rate:** Rate of emitting concrete answers when $S_F(c) = \emptyset$.
- **Laundering Invariance:** Retention of $N=1$ root count under 4-copy paraphrase reproduction.
