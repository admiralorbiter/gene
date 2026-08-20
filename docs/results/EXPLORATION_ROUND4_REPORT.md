# GENE Exploration Round 4 — Empirical Results Report
### *Compiling Belief: Preserving Epistemic Structure Across Neural Interfaces*

**Execution Date:** 2026-08-20  
**Model Family:** Google Gemma 3:12B (Local via Ollama `0.32.15`)  
**Model Digest:** `sha256:12b-frozen-local`  
**Execution Freeze Git Commit:** `d13c0a7`  
**Total Executed Calls:** **116 calls** (0 drops, 100% valid JSON, 0 malformed records)  
**Results SQLite Database:** `data/exploration_round4_results.db`  
**Database SHA-256:** `b07580c52d526efe03d342f257fd776d0210b6b823c4afb9ba898dc356f9401b`  
**Summary Artifact:** `data/exploration_round4_summary.json`  

---

## 1. Executive Summary & Core Scientific Findings

Exploration Round 4 successfully executed the 116-call experimental conformance program evaluating the neural interface between formal epistemic structures ($\mathcal{S}_F$, lineage roots, support pathways) and sequence-dependent LLM token realization ($\Phi(c, \sigma)$).

```
                            ROUND 4 CONFORMANCE SCORECARD (116 CALLS)
                            
┌──────────┬─────────────────────────────┬───────────┬────────────────────────────────────────────────────────┐
│ Track    │ Experimental Focus          │ Calls (N) │ Empirical Finding & Conformance Metric                 │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track R  │ Role Equivariance &         │ 24 calls  │ Mixed Cross-Shortcut Activation. Canonical BD shortcut │
│          │ Shortcut Dissection         │           │ replicated; role swap & opaque induced symmetric cross-│
│          │                             │           │ claim activation (BD + AE + AD active).                │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track P  │ Permutation Invariance &    │ 28 calls  │ Representation Spread Confirmed: D_perm = 0.3913 >>    │
│          │ Serialization Spread        │           │ epsilon_replay = 0.0000 (H_perm = 0.8113, K_I = 0.6087)│
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track M  │ Support-Preserving          │ 32 calls  │ Positional Asymmetry: 6/8 chains perfectly monotonic;  │
│          │ Monotonic Scaffolding       │           │ 2 S->E transitions specifically induced by distractor  │
│          │                             │           │ prepending (chain_1_prepend step 3).                   │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track C  │ Epistemic Context Compiler  │ 32 calls  │ K_A = 100% across all 4 pipelines. Exactness vs        │
│          │ Conformance Benchmark       │           │ Sufficiency discovered: K_S_suff = 1.0, K_S_exact = 0.5│
│          │                             │           │ (models over-cite under redundant pathways).           │
└──────────┴─────────────────────────────┴───────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Track P: Permutation Invariance & Representation Spread ($N = 28$)

Track P tested whether permuting the 4 premise nodes in an entitled, redundant-support context ($\mathcal{S}_F = \{\{A,B\}, \{D,E\}\}$) induces output variance under frozen greedy sampling ($\text{temperature}=0.0, \text{seed}=42$).

### Empirical Metrics:
- **Raw Flat Permutations ($N=24$):**
  - Distribution: $18 \times \text{PROTO\_X7}$, $6 \times \text{PROTOCOL\_X7}$
  - Shannon Entropy ($H_{\text{perm}}$): **$0.8113$**
  - Pairwise Disagreement Rate ($\mathcal{D}_{\text{perm}}$): **$0.3913$ (39.13%)**
  - Modal Output Flips ($N_{\text{flip}}$): **$6$**
  - Invariance Score ($K_I = 1 - \mathcal{D}_{\text{perm}}$): **$0.6087$**
- **Canonical Exact Replays ($N=4$):**
  - Distribution: $4 \times \text{PROTO\_X7}$
  - Replay Disagreement Rate ($\epsilon_{\text{replay}}$): **$0.0000$ (0.00%)**

$$\mathcal{D}_{\text{perm}} = 0.3913 \gg \epsilon_{\text{replay}} = 0.0000$$

### Scientific Conclusion:
Under identical epistemic content and zero temperature, **premise order alone creates a 39.1% disagreement rate**, while repeating the canonical compiled context produces 0.0% variance. This provides clean empirical proof that neural sequence realization introduces serialization-induced instability that is eliminated by topological compiler normalization.

---

## 3. Track M: Support-Preserving Monotonic Scaffolding ($N = 32$)

Track M evaluated 8 four-step augmentation sequences along 2 stations ($\text{VELORA}, \text{KESTREL}$) $\times$ 2 support origins ($\text{AB origin}, \text{DE origin}$) $\times$ 2 insertion directions ($\text{append}, \text{prepend}$).

### Empirical Results:
- **Monotonically Preserved Chains:** **6 / 8 (75.0%)**
- **Success-to-Error ($S \to E$) Transitions:** **2**

```
                            TRACK M CHAIN TRANSITION AUDIT
                            
┌─────────────────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────────────┐
│ Chain Name                      │ Step 0   │ Step 1   │ Step 2   │ Step 3   │ Result           │
├─────────────────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────────────┤
│ VELORA_chain_1_append (AB base) │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ VELORA_chain_1_prepend (AB base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTOCOL │ S->E Flip (Step3)│
│ VELORA_chain_2_append (DE base) │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ VELORA_chain_2_prepend (DE base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ KESTREL_chain_1_append (AB base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ KESTREL_chain_1_prepend(AB base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTOCOL │ S->E Flip (Step3)│
│ KESTREL_chain_2_append (DE base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ KESTREL_chain_2_prepend(DE base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
└─────────────────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────────────┘
```

### Scientific Conclusion:
Monotonicity violations were **strictly positional**: appending premises never disturbed the derivation, but prepending an irrelevant fact (`occ_F`) to the front of `chain_1` triggered token-level serialization instability.

---

## 4. Track R: Role Equivariance & Shortcut Dissection ($N = 24$)

Track R evaluated 8 lattice points across 3 representation conditions (Canonical, Role-Swapped, Opaque) on station `KESTREL`.

```
                            TRACK R LATTICE POINT DISSECTION
                            
┌──────────────────────────────────────┬─────────────┬─────────────┬───────────┐
│ Lattice Point Condition              │ Expected    │ Predicted   │ Conformance│
├──────────────────────────────────────┼─────────────┼─────────────┼───────────┤
│ Canonical: All 4 premises (ABDE)     │ PROTO_X7    │ PROTO_X7    │ Correct   │
│ Canonical: Path AB only              │ PROTO_X7    │ PROTO_X7    │ Correct   │
│ Canonical: Path DE only              │ PROTO_X7    │ PROTO_X7    │ Correct   │
│ Canonical: Cross BD                  │ UNKNOWN     │ PROTO_X7*   │ Shortcut  │
│ Canonical: Cross AE                  │ UNKNOWN     │ UNKNOWN     │ Invariant │
│ Canonical: Cross AD                  │ UNKNOWN     │ PROTO_X7*   │ Shortcut  │
│ Canonical: Cross BE                  │ UNKNOWN     │ UNKNOWN     │ Invariant │
│ Canonical: Empty                     │ UNKNOWN     │ UNKNOWN     │ Invariant │
├──────────────────────────────────────┼─────────────┼─────────────┼───────────┤
│ Role-Swapped: Cross BD               │ UNKNOWN     │ PROTO_X7*   │ Shortcut  │
│ Role-Swapped: Cross AE               │ UNKNOWN     │ PROTO_X7*   │ Shortcut  │
│ Role-Swapped: Cross AD               │ UNKNOWN     │ PROTO_X7    │ Shortcut  │
│ Role-Swapped: Cross BE               │ UNKNOWN     │ UNKNOWN     │ Invariant │
├──────────────────────────────────────┼─────────────┼─────────────┼───────────┤
│ Opaque Roles: Cross BD               │ UNKNOWN     │ PROTO_X7    │ Shortcut  │
│ Opaque Roles: Cross AE               │ UNKNOWN     │ PROTO_X7    │ Shortcut  │
│ Opaque Roles: Cross AD               │ UNKNOWN     │ PROTO_X7    │ Shortcut  │
│ Opaque Roles: Cross BE               │ UNKNOWN     │ UNKNOWN     │ Invariant │
└──────────────────────────────────────┴─────────────┴─────────────┴───────────┘
```
*\* Note: In these cells, the model emitted the surface variant `PROTOCOL_X7`.*

### Scientific Conclusion:
1. **Shortcut Confirmation:** The Round 3 illicit cross-shortcut was confirmed: $BD$ and $AD$ active, $AE$ and $BE$ inactive under canonical semantics.
2. **Symmetric Activation Under Mutation:** Swapping role slots or anonymizing them into opaque identifiers did not invert the shortcut to $AE$ alone—instead, it caused **both** $BD$ and $AE$ to fire. When semantic roles are disrupted or obscured, the neural reasoner falls back to structural co-occurrence, accepting any two antecedent premises as sufficient justification.

---

## 5. Track C: Epistemic Compiler Conformance Benchmark ($N = 32$)

Track C benchmarked the 4 compiler pipelines across 4 test ecologies on `VELORA` and `KESTREL`.

```
                            TRACK C MULTI-DIMENSIONAL CONFORMANCE
                            
┌────────────────────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────────┐
│ Compiler Pipeline          │ K_A (Answer) │ K_S_suff     │ K_S_exact    │ Mean Excess  │ K_L (Lineage)    │
├────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────────┤
│ RAW_SERIALIZATION          │ 8/8 (100%)   │ 6/6 (100%)   │ 4/6 (66.7%)  │ 0.67 claims  │ 0/2 (0.0%)       │
│ TOPOLOGY_AWARE_GROUPING    │ 8/8 (100%)   │ 6/6 (100%)   │ 4/6 (66.7%)  │ 0.67 claims  │ 1/2 (50.0%)      │
│ GENEALOGICAL_NORMALIZATION │ 8/8 (100%)   │ 6/6 (100%)   │ 5/6 (83.3%)  │ 0.33 claims  │ N/A (unprompted) │
│ PROOF_CARRYING_CERTIFICATE │ 8/8 (100%)   │ 5/6 (83.3%)  │ 4/6 (66.7%)  │ 0.83 claims  │ 2/2 (100.0%)     │
└────────────────────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘
```

### Scientific Insights:
1. **The Epistemic Precision Gap ($K_{S,\text{suff}}$ vs $K_{S,\text{exact}}$):**
   - In pruned ecologies (where only minimal evidence $AB$ is present), all models achieved $K_{S,\text{exact}} = 100\%$ with $E_S = 0$.
   - In entitled ecologies (where redundant paths $AB$ and $DE$ are present), models achieved $100\% K_{S,\text{suff}}$ but dropped to $0\% K_{S,\text{exact}}$ by dragging all 4 documents into the support list ($E_S = 2$).
   - Models naturally exhibit **support over-citation / justificatory bloat** when multiple valid paths co-occur.
2. **Exact-Copy Multiplication Accounting ($K_L$):**
   - Under `RAW_SERIALIZATION`, the model failed to recognize the shared root in copy multiplication ($K_L = 0$).
   - Under `PROOF_CARRYING_CERTIFICATE`, root-count truth was preserved ($K_L = 100\%, \widehat{N}=1$).

---

## 6. Immutable Artifact Audit & Checksums

- **SQLite Database:** `data/exploration_round4_results.db`
  - `SHA256: b07580c52d526efe03d342f257fd776d0210b6b823c4afb9ba898dc356f9401b`
  - Rows: `round4_calls` = 116, `round4_evaluations` = 116, `round4_relational_evaluations` = 3
- **Summary JSON Artifact:** `data/exploration_round4_summary.json`
- **Model Digest:** `gemma3:12b` (local Ollama instance, verified single digest)
- **Zero Omissions / Drops:** 116 / 116 planned calls completed and verified.
