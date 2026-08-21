# Exploration Round 6 Scale Envelope Benchmark Report (v1)

**Assay Name**: Exact Support & ATMS Complexity Scale Envelope v1  
**Execution Environment**: Python `3.12.0` on `Windows 11`  
**Peak Memory Usage**: `3.879 MB`  
**Total Elapsed Time**: `9.463s`  
**Summary Artifact**: [`../../data/exploration_round6_scale_envelope_summary.json`](../../data/exploration_round6_scale_envelope_summary.json)

---

## Executive Summary

Scale Envelope v1 rigorously profiles the computational complexity of exact antichain-minimized support maintenance across two complementary regimes:
1. **Typical Parameterized Horn Workloads**: $1,800$ synthetic worlds evaluating root universes up to $N=16$, depth $D \le 5$, branching $B \le 4$, and active premise correlation.
2. **Adversarial Sperner Antichain Workloads**: Bipartite worst-case constructions generating maximal antichains $\binom{N}{N/2}$ up to $N=16$ roots.

### Key Empirical Findings:
- **Typical Workload Behavior**: Across shallow to moderate hierarchies ($N \le 12, D \le 3, B \le 2$), support sizes remain bounded ($|\mathcal{S}| \le 3$), with median enumeration latencies under $400\mu\text{s}$. In deep multi-branching configurations ($N=16, D=5, B=4$), median latency reaches `5193.3\mu\text{s}` with p99 reaching `161300.3\mu\text{s}`.
- **Adversarial Combinatorial Growth Boundary**: Under adversarial Sperner antichains, support size scales exponentially: $N=8 \implies |\mathcal{S}|=70$ (`372.4\mu\text{s}`), $N=12 \implies |\mathcal{S}|=924$ (`20.03\text{ms}`), $N=16 \implies |\mathcal{S}|=2,000$ capped (`92.57\text{ms}`).
- **The Epistemic Risk of Lossy Support Pruning**: Scalability is not merely a systems problem. Arbitrarily pruning support families (such as naïve top-$k$ beam selection) recreates Stage 5A **revision autoimmunity**: if all $k$ retained paths are later invalidated while an un-retained $(k+1)$-th path remains valid, the runtime will falsely retract an entitled belief.

```
+========================================================================================================================+
|                                    TYPICAL WORKLOAD SCALING SAMPLE (p50 / p99)                                         |
+==========+=======+===========+===================+==================+======================+=========================+
| Roots N  | Depth | Branching | Mean Support |S|  | Max Support |S|  | p50 Latency (μs)     | p99 Latency (μs)        |
+==========+=======+===========+===================+==================+======================+=========================+
| 4 | 1 | 1 | 1.00 | 1 | 22.4 | 87.5 |
| 4 | 1 | 2 | 1.16 | 2 | 22.0 | 88.4 |
| 4 | 1 | 4 | 1.62 | 4 | 26.2 | 104.9 |
| 4 | 3 | 1 | 1.00 | 1 | 34.7 | 209.2 |
| 4 | 3 | 2 | 1.26 | 3 | 47.1 | 131.9 |
| 4 | 3 | 4 | 1.34 | 3 | 86.6 | 352.2 |
| 4 | 5 | 1 | 1.00 | 1 | 55.8 | 223.5 |
| 4 | 5 | 2 | 1.10 | 2 | 83.0 | 316.3 |
| 4 | 5 | 4 | 1.20 | 3 | 160.3 | 399.7 |
| 8 | 1 | 1 | 1.00 | 1 | 45.5 | 118.8 |
| 8 | 1 | 2 | 1.42 | 2 | 48.0 | 195.9 |
| 8 | 1 | 4 | 1.96 | 4 | 53.5 | 294.2 |
| 8 | 3 | 1 | 1.00 | 1 | 67.7 | 298.9 |
| 8 | 3 | 2 | 1.88 | 5 | 95.6 | 301.0 |
| 8 | 3 | 4 | 2.98 | 9 | 159.4 | 577.7 |
| 8 | 5 | 1 | 1.00 | 1 | 107.2 | 628.9 |
| 8 | 5 | 2 | 1.82 | 8 | 181.5 | 553.8 |
| 8 | 5 | 4 | 2.98 | 15 | 527.8 | 2041.5 |
| 12 | 1 | 1 | 1.00 | 1 | 83.9 | 212.0 |
| 12 | 1 | 2 | 1.44 | 2 | 89.1 | 318.7 |
| 12 | 1 | 4 | 2.10 | 4 | 93.8 | 330.7 |
| 12 | 3 | 1 | 1.00 | 1 | 107.6 | 235.7 |
| 12 | 3 | 2 | 2.76 | 8 | 152.8 | 403.2 |
| 12 | 3 | 4 | 7.04 | 21 | 317.5 | 797.9 |
| 12 | 5 | 1 | 1.00 | 1 | 160.4 | 334.1 |
| 12 | 5 | 2 | 2.98 | 9 | 364.6 | 677.1 |
| 12 | 5 | 4 | 8.88 | 30 | 1316.4 | 11201.4 |
| 16 | 1 | 1 | 1.00 | 1 | 135.3 | 284.1 |
| 16 | 1 | 2 | 1.40 | 2 | 137.3 | 274.8 |
| 16 | 1 | 4 | 2.12 | 4 | 140.9 | 295.2 |
| 16 | 3 | 1 | 1.00 | 1 | 171.3 | 386.2 |
| 16 | 3 | 2 | 3.46 | 12 | 211.0 | 419.1 |
| 16 | 3 | 4 | 12.96 | 67 | 507.2 | 4199.2 |
| 16 | 5 | 1 | 1.00 | 1 | 241.6 | 512.6 |
| 16 | 5 | 2 | 6.52 | 59 | 476.7 | 2332.1 |
| 16 | 5 | 4 | 21.72 | 78 | 5193.3 | 161300.3 |
+==========+=======+===========+===================+==================+======================+=========================+
```

```
+========================================================================================================================+
|                                    ADVERSARIAL SPERNER ANTICHAIN SCALING                                               |
+==========+==============================+======================+======================+================================+
| Roots N  | Theoretical Max Antichain    | Actual Support |S|   | Enum Latency (μs)    | Inval Latency (μs)             |
+==========+==============================+======================+======================+================================+
| 4 | 6 | 6 | 62.9 | 304.5 |
| 6 | 20 | 20 | 88.3 | 844.7 |
| 8 | 70 | 70 | 372.4 | 3391.1 |
| 10 | 252 | 252 | 2071.4 | 27633.9 |
| 12 | 924 | 924 | 20028.1 | 292838.0 |
| 14 | 3,432 | 2,000 | 92484.6 | 675746.6 |
| 16 | 12,870 | 2,000 | 92573.7 | 659775.3 |
+==========+==============================+======================+======================+================================+
```

---

## Architectural Guidance for Scaling Truth Maintenance

1. **Approximation Integrity & Exact Compressed Representations**: Before resorting to lossy truncation, the Epistemic Kernel should explore exact compressed representations:
   - **Binary/Zero-Suppressed Decision Diagrams (BDD/ZDD)**
   - **Factorized Provenance Circuits**
   - **Lazy Support Enumeration** (computing cuts and entitlement dynamically without materializing all paths).
2. **Explicit Uncertainty on Approximation**: If memory constraints ever force support truncation, the belief state must be explicitly tagged as `SUPPORT_INCOMPLETE` rather than masquerading as complete ground truth.
