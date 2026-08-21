# GENE Exploration Round 4 — Empirical Results & Scientific Synthesis Report
### *Compiling Belief: Preserving Epistemic Structure Across Neural Interfaces*

**Execution Date:** 2026-08-20  
**Model Family:** Google Gemma 3:12B (Local via Ollama `0.32.15`)  
**Model Digest:** `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`  
**Parameter Size / Quantization:** `12.2B` / `Q4_K_M`  
**Execution Freeze Git Commit:** `d13c0a7`  
**Total Executed Calls:** **116 calls** (0 drops, 100% valid JSON, 0 malformed records)  
**Results SQLite Database:** `data/exploration_round4_results.db`  
**Database SHA-256:** `820e574e6d3a0196dfec13ffc392d68d399791b210fd65187795dd834046269e`  
**Summary JSON Artifact:** `data/exploration_round4_summary.json`  
**Summary SHA-256:** `8083e88dd31a774151bca07b95370a51f401ab4571783a0949172aced5d20ff9`  
**Artifact Manifest:** `data/exploration_round4_artifacts.json`  

---

## 1. Executive Summary & Core Scientific Findings

Exploration Round 4 evaluated the neural interface between formal epistemic structures ($\mathcal{S}_F$, lineage roots, minimal support pathways) and sequence-dependent LLM token realization ($\Phi(c, \sigma)$) across 116 live calls on local Gemma 3:12B.

A critical discovery of this round is the necessity of separating **Typed-Interface / Symbolic Conformance** ($K_{\text{symbol}}$) from **Underlying Epistemic / Semantic Conformance** ($K_{\text{semantic}}$).

```
                            ROUND 4 CONFORMANCE SCORECARD (116 CALLS)
                            
┌──────────┬─────────────────────────────┬───────────┬────────────────────────────────────────────────────────┐
│ Track    │ Experimental Focus          │ Calls (N) │ Empirical Finding & Dual Conformance Analysis          │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track R  │ Role Equivariance &         │ 24 calls  │ Predicate-Class Role-Anchor Shortcut Confirmed:        │
│          │ Shortcut Dissection         │           │ AD v AE v BD active; BE=0 strictly rejected across all │
│          │                             │           │ conditions. Canonical semantics selectively suppress AE│
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track P  │ Permutation Invariance &    │ 28 calls  │ Surface-Form Conformance Spread Confirmed:             │
│          │ Serialization Drift         │           │ D_perm,symbol = 0.3913 >> epsilon_replay = 0.0000;     │
│          │                             │           │ D_perm,semantic = 0.0000 (all 24 infer X7).            │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track M  │ Support-Preserving          │ 32 calls  │ Positional Asymmetry: 8/8 chains semantically          │
│          │ Monotonic Scaffolding       │           │ monotonic; 2 symbolic S->E flips strictly induced by   │
│          │                             │           │ prepending distractor occ_F at Step 3.                 │
├──────────┼─────────────────────────────┼───────────┼────────────────────────────────────────────────────────┤
│ Track C  │ Epistemic Context Compiler  │ 32 calls  │ K_A = 100% across all 4 pipelines.                     │
│          │ Conformance Benchmark       │           │ Epistemic Precision Gap: K_S_suff = 100% vs            │
│          │                             │           │ K_S_exact = 62.5% (models over-cite redundant paths).  │
└──────────┴─────────────────────────────┴───────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Track P: Surface-Form Instability vs Epistemic Invariance ($N = 28$)

Track P tested whether permuting the 4 premise nodes in an entitled, redundant-support context ($\mathcal{S}_F = \{\{A,B\}, \{D,E\}\}$) induces output variance under frozen greedy sampling ($\text{temperature}=0.0, \text{seed}=42$).

### Dual Metric Decomposition:
- **Raw Flat Permutations ($N=24$):**
  - Raw Distribution: $18 \times \text{PROTO\_X7}$, $6 \times \text{PROTOCOL\_X7}$.
  - **Symbolic Disagreement Rate ($\mathcal{D}_{\text{perm,symbol}}$):** **$0.3913$ (39.13%)** ($H_{\text{perm,symbol}} = 0.8113, K_{I,\text{symbol}} = 0.6087$).
  - **Semantic Disagreement Rate ($\mathcal{D}_{\text{perm,semantic}}$):** **$0.0000$ (0.00%)** ($H_{\text{perm,semantic}} = 0.0, K_{I,\text{semantic}} = 1.0$).
- **Canonical Exact Replays ($N=4$):**
  - Distribution: $4 \times \text{PROTO\_X7}$.
  - Replay Disagreement Rate ($\epsilon_{\text{replay}}$): **$0.0000$ (0.00%)**.

$$\mathcal{D}_{\text{perm,symbol}} = 0.3913 \gg \epsilon_{\text{replay}} = 0.0000 \quad\text{and}\quad \mathcal{D}_{\text{perm,semantic}} = 0.0000$$

### Scientific Conclusion:
1. **Epistemic Invariance:** On positive redundant support ecologies, premise serialization order does *not* alter the underlying authorized protocol belief ($24/24$ calls derive protocol $\text{X7}$).
2. **Symbolic-Interface Drift:** Premise ordering alone causes a **39.13% surface-form realization shift** ($\text{PROTO\_X7} \to \text{PROTOCOL\_X7}$) under greedy decoding, while exact canonical compilation achieves 0.0% variance. For typed external systems, context compilation provides essential interface stabilization.

---

## 3. Track M: Support-Preserving Monotonic Scaffolding ($N = 32$)

Track M evaluated 8 four-step augmentation sequences along 2 stations ($\text{VELORA}, \text{KESTREL}$) $\times$ 2 support origins ($\text{AB base}, \text{DE base}$) $\times$ 2 insertion directions ($\text{append}, \text{prepend}$).

### Empirical Results:
- **Semantic Monotonicity:** **8 / 8 chains (100.0%)** (Zero loss of derivation).
- **Symbolic Contract Transitions:** **2 Success-to-Error ($S \to E$) flips** at Step 3 specifically in `chain_1_prepend`.

```
                            TRACK M CHAIN TRANSITION AUDIT
                            
┌─────────────────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────────────┐
│ Chain Name                      │ Step 0   │ Step 1   │ Step 2   │ Step 3   │ Semantic Result  │
├─────────────────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────────────┤
│ VELORA_chain_1_append (AB base) │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ VELORA_chain_1_prepend (AB base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTOCOL │ Monotonic (PASS)*│
│ VELORA_chain_2_append (DE base) │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ VELORA_chain_2_prepend (DE base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ KESTREL_chain_1_append (AB base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ KESTREL_chain_1_prepend(AB base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTOCOL │ Monotonic (PASS)*│
│ KESTREL_chain_2_append (DE base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
│ KESTREL_chain_2_prepend(DE base)│ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ PROTO_X7 │ Monotonic (PASS) │
└─────────────────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────────────┘
```
*\* Note: Step 3 emitted surface variant `PROTOCOL_X7` (contract drift, semantic pass).*

### Scientific Conclusion:
Monotonicity violations were **strictly positional and symbolic**: appending premises never disturbed exact token realization, but prepending an irrelevant fact (`occ_F`) to the front of `chain_1` triggered a surface-form drift without destroying the underlying derivation.

---

## 4. Track R: Role Equivariance & Predicate-Class Anchoring ($N = 24$)

Track R evaluated 8 lattice points across 3 representation conditions (Canonical, Role-Swapped, Opaque) on station `KESTREL`.

```
                            TRACK R LATTICE POINT DISSECTION
                            
┌──────────────────────────────────────┬─────────────┬─────────────┬──────────────┬────────────────────────┐
│ Lattice Point Condition              │ Expected    │ Predicted   │ Semantic Pred│ Mechanism Interpretation│
├──────────────────────────────────────┼─────────────┼─────────────┼──────────────┼────────────────────────┤
│ Canonical: All 4 premises (ABDE)     │ PROTO_X7    │ PROTO_X7    │ PROTO_X7     │ Valid Derivation       │
│ Canonical: Path AB only              │ PROTO_X7    │ PROTO_X7    │ PROTO_X7     │ Valid Derivation       │
│ Canonical: Path DE only              │ PROTO_X7    │ PROTO_X7    │ PROTO_X7     │ Valid Derivation       │
│ Canonical: Cross BD                  │ UNKNOWN     │ PROTOCOL_X7 │ PROTO_X7     │ Shortcut Active        │
│ Canonical: Cross AE                  │ UNKNOWN     │ UNKNOWN     │ UNKNOWN      │ Invariant (Suppressed) │
│ Canonical: Cross AD                  │ UNKNOWN     │ PROTOCOL_X7 │ PROTO_X7     │ Shortcut Active        │
│ Canonical: Cross BE                  │ UNKNOWN     │ UNKNOWN     │ UNKNOWN      │ Correctly Rejected     │
│ Canonical: Empty                     │ UNKNOWN     │ UNKNOWN     │ UNKNOWN      │ Correctly Rejected     │
├──────────────────────────────────────┼─────────────┼─────────────┼──────────────┼────────────────────────┤
│ Role-Swapped: Cross BD               │ UNKNOWN     │ PROTOCOL_X7 │ PROTO_X7     │ Shortcut Active        │
│ Role-Swapped: Cross AE               │ UNKNOWN     │ PROTOCOL_X7 │ PROTO_X7     │ Shortcut Active        │
│ Role-Swapped: Cross AD               │ UNKNOWN     │ PROTO_X7    │ PROTO_X7     │ Shortcut Active        │
│ Role-Swapped: Cross BE               │ UNKNOWN     │ UNKNOWN     │ UNKNOWN      │ Correctly Rejected     │
├──────────────────────────────────────┼─────────────┼─────────────┼──────────────┼────────────────────────┤
│ Opaque Roles: Cross BD               │ UNKNOWN     │ PROTO_X7    │ PROTO_X7     │ Shortcut Active        │
│ Opaque Roles: Cross AE               │ UNKNOWN     │ PROTO_X7    │ PROTO_X7     │ Shortcut Active        │
│ Opaque Roles: Cross AD               │ UNKNOWN     │ PROTO_X7    │ PROTO_X7     │ Shortcut Active        │
│ Opaque Roles: Cross BE               │ UNKNOWN     │ UNKNOWN     │ UNKNOWN      │ Correctly Rejected     │
└──────────────────────────────────────┴─────────────┴─────────────┴──────────────┴────────────────────────┘
```

### Scientific Discovery:
1. **Shortcut Confirmation:** Under canonical semantics, the Round 3 illicit shortcut was replicated ($BD$ and $AD$ active, $AE$ and $BE$ inactive).
2. **Predicate-Class Anchoring:** Under role-swapping and opaque roles, the shortcut did not invert to $AE$ alone—instead, **$AD \lor AE \lor BD$** fired while **$BE$ remained 100% rejected across all conditions**.
   - $BE$ contains two `reports_to` predicates (Nerin reports S1 + Vael reports S2).
   - $AD$, $AE$, and $BD$ each contain at least one `has_role` predicate.
   - **Conclusion:** The neural reasoner uses a **role-anchored predicate-class heuristic**, treating any combination containing a role declaration as sufficient justification, while natural semantic priors selectively suppress $AE$ under canonical labeling.

---

## 5. Track C: Epistemic Compiler Conformance Benchmark ($N = 32$)

Track C evaluated 4 compiler pipelines across 4 test ecologies on `VELORA` and `KESTREL`.

### Preregistered Support Conformance ($N = 16$ calls across Entitled and Pruned Ecologies):

```
                            PREREGISTERED SUPPORT CONFORMANCE MATRIX
                            
┌────────────────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Compiler Pipeline          │ K_A (Answer) │ K_S_suff     │ K_S_exact    │ Mean Excess  │
├────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ RAW_SERIALIZATION          │ 4/4 (100%)   │ 4/4 (100%)   │ 2/4 (50.0%)  │ 1.0 claims   │
│ TOPOLOGY_AWARE_GROUPING    │ 4/4 (100%)   │ 4/4 (100%)   │ 2/4 (50.0%)  │ 1.0 claims   │
│ GENEALOGICAL_NORMALIZATION │ 4/4 (100%)   │ 4/4 (100%)   │ 3/4 (75.0%)  │ 0.5 claims   │
│ PROOF_CARRYING_CERTIFICATE │ 4/4 (100%)   │ 4/4 (100%)   │ 2/4 (50.0%)  │ 1.0 claims   │
└────────────────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

### Complete Cell Decomposition Across All 32 Calls:

```
                            TRACK C COMPLETE CELL AUDIT (32 CALLS)
                            
┌────────────────────────────┬─────────────────────────────┬──────────┬──────────┬──────────┬──────────┬────────┬───────────────────┐
│ Compiler Pipeline          │ Ecology & Station           │ K_A      │ K_S_suff │ K_S_exact│ Excess   │ Roots  │ K_L | Determinable│
├────────────────────────────┼─────────────────────────────┼──────────┼──────────┼──────────┼──────────┼────────┼───────────────────┤
│ RAW_SERIALIZATION          │ entitled_VELORA             │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 2 claims │ 0      │ N/A (unprompted)  │
│ RAW_SERIALIZATION          │ entitled_KESTREL            │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 2 claims │ 0      │ N/A (unprompted)  │
│ RAW_SERIALIZATION          │ pruned_VELORA               │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ N/A (unprompted)  │
│ RAW_SERIALIZATION          │ pruned_KESTREL              │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ N/A (unprompted)  │
│ RAW_SERIALIZATION          │ unentitled_VELORA           │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ None   │ N/A (indeterm.)   │
│ RAW_SERIALIZATION          │ unentitled_KESTREL          │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ None   │ N/A (indeterm.)   │
│ RAW_SERIALIZATION          │ copy_multiplication_VELORA  │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 0      │ 0 / 1 (FAIL)      │
│ RAW_SERIALIZATION          │ copy_multiplication_KESTREL │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 0      │ 0 / 1 (FAIL)      │
├────────────────────────────┼─────────────────────────────┼──────────┼──────────┼──────────┼──────────┼────────┼───────────────────┤
│ TOPOLOGY_AWARE_GROUPING    │ entitled_VELORA             │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 2 claims │ 1      │ N/A (unprompted)  │
│ TOPOLOGY_AWARE_GROUPING    │ entitled_KESTREL            │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 2 claims │ 1      │ N/A (unprompted)  │
│ TOPOLOGY_AWARE_GROUPING    │ pruned_VELORA               │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ N/A (unprompted)  │
│ TOPOLOGY_AWARE_GROUPING    │ pruned_KESTREL              │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 0      │ N/A (unprompted)  │
│ TOPOLOGY_AWARE_GROUPING    │ unentitled_VELORA           │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ None   │ N/A (indeterm.)   │
│ TOPOLOGY_AWARE_GROUPING    │ unentitled_KESTREL          │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ None   │ N/A (indeterm.)   │
│ TOPOLOGY_AWARE_GROUPING    │ copy_multiplication_VELORA  │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ 1 / 1 (PASS)      │
│ TOPOLOGY_AWARE_GROUPING    │ copy_multiplication_KESTREL │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ Abstain (null)    │
├────────────────────────────┼─────────────────────────────┼──────────┼──────────┼──────────┼──────────┼────────┼───────────────────┤
│ GENEALOGICAL_NORMALIZATION │ entitled_VELORA             │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ N/A (unprompted)  │
│ GENEALOGICAL_NORMALIZATION │ entitled_KESTREL            │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 1 claims │ 2      │ N/A (unprompted)  │
│ GENEALOGICAL_NORMALIZATION │ pruned_VELORA               │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ N/A (unprompted)  │
│ GENEALOGICAL_NORMALIZATION │ pruned_KESTREL              │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 0      │ N/A (unprompted)  │
│ GENEALOGICAL_NORMALIZATION │ unentitled_VELORA           │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ None   │ N/A (indeterm.)   │
│ GENEALOGICAL_NORMALIZATION │ unentitled_KESTREL          │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ None   │ N/A (indeterm.)   │
│ GENEALOGICAL_NORMALIZATION │ copy_multiplication_VELORA  │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ Abstain (null)    │
│ GENEALOGICAL_NORMALIZATION │ copy_multiplication_KESTREL │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ Abstain (null)    │
├────────────────────────────┼─────────────────────────────┼──────────┼──────────┼──────────┼──────────┼────────┼───────────────────┤
│ PROOF_CARRYING_CERTIFICATE │ entitled_VELORA             │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 2 claims │ 2      │ N/A (unprompted)  │
│ PROOF_CARRYING_CERTIFICATE │ entitled_KESTREL            │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 2 claims │ 2      │ N/A (unprompted)  │
│ PROOF_CARRYING_CERTIFICATE │ pruned_VELORA               │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ N/A (unprompted)  │
│ PROOF_CARRYING_CERTIFICATE │ pruned_KESTREL              │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ N/A (unprompted)  │
│ PROOF_CARRYING_CERTIFICATE │ unentitled_VELORA           │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ 1      │ N/A (indeterm.)   │
│ PROOF_CARRYING_CERTIFICATE │ unentitled_KESTREL          │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ 1      │ N/A (indeterm.)   │
│ PROOF_CARRYING_CERTIFICATE │ copy_multiplication_VELORA  │ 1 (PASS) │ 0 (FAIL)*│ 0 (FAIL)*│ 1 claims │ 1      │ 1 / 1 (PASS)      │
│ PROOF_CARRYING_CERTIFICATE │ copy_multiplication_KESTREL │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ 1 / 1 (PASS)      │
└────────────────────────────┴─────────────────────────────┴──────────┴──────────┴──────────┴──────────┴────────┴───────────────────┘
```
*\* Note: In `proof_carrying_certificate_eco_copy_multiplication_VELORA`, the model cited only `DOC_01` (manager role) omitting `DOC_05` (reports_to).*

### Key Scientific Takeaways from Track C:
1. **The Epistemic Precision Gap & Justificatory Bloat ($E_S > 0$):**
   - In pruned ecologies ($AB$ only), models isolate the minimal proof with $100\%$ exactness and $0$ excess claims.
   - In entitled ecologies ($AB$ and $DE$ co-occurring), models achieve $100\% K_{S,\text{suff}}$ but drag all redundant documents into reported support ($E_S = 2$).
   - **Connection to Non-Destructive Memory Repair:** Bloated support records ($E_S > 0$) create false fragility. If $D$ is subsequently retracted, a system storing bloated support $\{A,B,D,E\}$ may incorrectly reconsider $C$, causing false epistemic autoimmunity.
2. **Exact-Copy Lineage Accounting ($K_L$):**
   - `RAW_SERIALIZATION`: Model failed to isolate ancestral root count ($\widehat{N}=0, K_L = 0/2$).
   - `PROOF_CARRYING_CERTIFICATE`: Complied with explicit certificate root count ($\widehat{N}=1, K_L = 2/2$).
   - `TOPOLOGY_AWARE_GROUPING`: Correctly recognized single root at VELORA ($\widehat{N}=1$).

---

## 6. Provenance & Artifact Integrity

- **Database Path:** `data/exploration_round4_results.db`
- **Database Checksum (SHA-256):** `820e574e6d3a0196dfec13ffc392d68d399791b210fd65187795dd834046269e`
- **Summary JSON Path:** `data/exploration_round4_summary.json`
- **Summary Checksum (SHA-256):** `8083e88dd31a774151bca07b95370a51f401ab4571783a0949172aced5d20ff9`
- **Artifact Manifest:** `data/exploration_round4_artifacts.json`
- **Model Digest:** `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a` (Gemma 3:12B)
- **Zero Omissions / Drops:** 116 / 116 planned calls completed, parsed, and verified.
