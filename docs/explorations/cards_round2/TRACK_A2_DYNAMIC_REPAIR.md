# Round 2 Experiment Card — Track A2: Dynamic Memory Repair & Lazy Revalidation

## 1. Scientific Objective
- **Core Research Question:** When an upstream root premise changes in active persistent memory ($G_0: \text{TAL} \leadsto \text{KIRA}$), does **lazy support-aware revalidation** achieve equal behavioral accuracy to eager full-subtree repair while dramatically reducing downstream recomputation costs ($K_{\text{recompute}}$)?
- **Key Shift from Round 1:** Rather than testing pre-constructed static prompts, this track executes **active graph mutations inside SQLite**, tracks dirty/stale flags on descendant nodes, and measures **empirically observed** inspection counts, recomputation calls, and token overhead.

## 2. The Three Evaluated Memory-Revision Policies
1. **Policy 1: Root Overwrite ($P_{\text{overwrite}}$)**
   - Update $G_0$ root record only. Stale $G_1, G_2$ nodes remain active in the memory store without modification.
2. **Policy 2: Eager Support-Aware Repair ($P_{\text{eager}}$)**
   - Upon $G_0$ update, immediately traverse downstream DAG, invalidate broken support sets, and recompute all affected descendant claims synchronously.
3. **Policy 3: Lazy Support-Aware Revalidation ($P_{\text{lazy}}$)**
   - Upon $G_0$ update, mark downstream dependencies `dirty`.
   - At query retrieval time:
     - If candidate memory is clean $\to$ return directly.
     - If `dirty` and alternative clean support path in $S(c)$ exists $\to$ clear dirty flag and return (0 recomputation).
     - If `dirty` and all paths broken $\to$ recompute single target node on-demand, cache result, and return.

## 3. Real Measured Metrics (Zero Simulated Assignations)
- $N_{\text{inspected}}$: Number of graph nodes traversed during update/query.
- $N_{\text{invalidated}}$: Number of minimal support sets marked invalid.
- $K_{\text{recompute}}$: Number of live LLM recomputation calls executed.
- $T_{\text{tokens}}$: Total prompt and completion tokens consumed.
- $L_{\text{latency}}$: Wall-clock execution time (ms).
- $C_{\text{coverage}}$: Behavioral accuracy on target downstream queries ($0.0 \dots 1.0$).
- $H_{\text{stale}}$: Rate of stale/obsolete phenotype expression ($0.0 \dots 1.0$).

## 4. Planned Call Budget
- Baseline graph build: 4 calls.
- Policy evaluations: 3 policies × 2 stations × 2 query loci = 12 calls.
- Total: **16 live calls** (max 24 with 1 replication).
- **Falsifier:** If lazy revalidation produces higher stale output rates than eager repair ($H_{\text{lazy}} > 0.0$), or if lazy compute equals eager compute ($K_{\text{lazy}} = K_{\text{eager}}$), lazy belief maintenance is either unsound or computationally unadvantageous.
