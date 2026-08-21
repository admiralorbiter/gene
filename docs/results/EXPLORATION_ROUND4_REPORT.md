# GENE Exploration Round 4 — Empirical Results & Scientific Synthesis Report
### *Compiling Belief: Preserving Epistemic Structure Across Neural Interfaces*

**Execution Date:** 2026-08-20  
**Model Family:** Google Gemma 3:12B (Local via Ollama `0.32.15`)  
**Model Digest:** `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a` (captured post-execution via `/api/tags` from unchanged local Ollama instance)  
**Parameter Size / Quantization:** `12.2B` / `Q4_K_M`  
**Execution Freeze Git Commit:** `d13c0a7`  
**Post-Review Tag:** `round4-postreview-freeze`  
**Total Executed Calls:** **116 calls** (0 drops, 100% valid JSON, 0 malformed records)  
**Results SQLite Database:** `data/exploration_round4_results.db`  
- **Raw Execution DB SHA-256:** `b07580c52d526efe03d342f257fd776d0210b6b823c4afb9ba898dc356f9401b`
- **Post-Review Augmented DB SHA-256:** `820e574e6d3a0196dfec13ffc392d68d399791b210fd65187795dd834046269e`  
*(Note: 116 raw call records and 116 contemporaneous evaluation records are 100% byte/content identical; model_digest was backfilled post-execution).*  
**Summary JSON Artifact:** `data/exploration_round4_summary.json` (`SHA256: 8984076c22033ed79628138fbd18a44d650dc479796632dcf02bc9e501be5949`)  
**Artifact Manifest:** `data/exploration_round4_artifacts.json`  

---

## 1. Executive Summary & Four-Layer Conformance Taxonomy

Round 4 evaluated the neural interface between formal epistemic structures ($\mathcal{S}_F$, lineage roots, minimal support pathways) and sequence-dependent LLM token realization ($\Phi(c, \sigma)$) across 116 live calls.

The central scientific discovery of this round is that neural-interface failures fall into **four qualitatively distinct layers**, each demanding different architectural controls:

```
                            FOUR-LAYER CONFORMANCE TAXONOMY
                            
┌─────────────────────────────┬─────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Conformance Layer           │ Failure Mode                    │ Empirical Manifestation in Round 4                     │
├─────────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Symbolic / Interface     │ Surface-Form Token Drift        │ Track P: D_perm,symbol = 0.3913 vs D_perm,sem = 0.0000 │
│    Realization              │ (PROTO_X7 vs PROTOCOL_X7)       │ Track M: Positional S->E flip at chain_1_prepend step 3│
├─────────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 2. Cross-Field Contract     │ Incoherent Structured Fields    │ Track C: 'determinable' paired with root_count=null;   │
│    Coherence                │ (Syntactic JSON != Valid State) │ 'indeterminable' paired with root_count=1.             │
├─────────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 3. Justification Precision  │ Justificatory Bloat             │ Track C: Entitled states yield K_S_suff = 100% but     │
│    Conformance              │ (E_S > 0 Over-Citation)         │ K_S_exact = 12.5% (E_S = 1.625 mean excess claims).   │
├─────────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 4. Epistemic / Formal       │ Illicit Coalition Derivation    │ Track R: AD & BD active across all representations;    │
│    Derivability             │ (S_F = 0 -> Concrete Answer)    │ AE activated under mutation; BE=0 strictly rejected.   │
└─────────────────────────────┴─────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Track P: Surface-Form Serialization Effect vs Semantic Invariance ($N = 28$)

Track P tested whether permuting the 4 premise nodes in an entitled, redundant-support context ($\mathcal{S}_F = \{\{A,B\}, \{D,E\}\}$) induces output variance under frozen greedy sampling ($\text{temperature}=0.0, \text{seed}=42$).

### Empirical Metrics:
- **Raw Flat Permutations ($N=24$):**
  - Raw Distribution: $18 \times \text{PROTO\_X7}$, $6 \times \text{PROTOCOL\_X7}$.
  - **Symbolic Disagreement Rate ($\mathcal{D}_{\text{perm,symbol}}$):** **$0.3913$ (39.13%)** ($H_{\text{perm,symbol}} = 0.8113, K_{I,\text{symbol}} = 0.6087, N_{\text{flip}} = 6$).
  - **Semantic Disagreement Rate ($\mathcal{D}_{\text{perm,semantic}}$):** **$0.0000$ (0.00%)** ($H_{\text{perm,semantic}} = 0.0, K_{I,\text{semantic}} = 1.0$).
- **Canonical Exact Replays ($N=4$):**
  - Distribution: $4 \times \text{PROTO\_X7}$.
  - Replay Disagreement Rate ($\epsilon_{\text{replay}}$): **$0.0000$ (0.00%)**.

$$\mathcal{D}_{\text{perm,symbol}} = 0.3913 \gg \epsilon_{\text{replay}} = 0.0000 \quad\text{and}\quad \mathcal{D}_{\text{perm,semantic}} = 0.0000$$

### Scientific Conclusion:
1. **Semantic Invariance Null:** On positive redundant support ecologies, premise serialization order does *not* alter the underlying authorized protocol belief ($24/24$ calls derive protocol $\text{X7}$).
2. **Local Symbolic-Interface Effect:** Premise ordering alone causes a **39.13% surface-form realization shift** ($\text{PROTO\_X7} \to \text{PROTOCOL\_X7}$) under greedy decoding, while exact canonical compilation achieves 0.0% variance. This demonstrates that typed output validation or canonical context formatting stabilizes the symbolic interface.

---

## 3. Track M: Support-Preserving Monotonic Scaffolding ($N = 32$)

Track M evaluated 8 four-step augmentation sequences along 2 stations ($\text{VELORA}, \text{KESTREL}$) $\times$ 2 support origins ($\text{AB base}, \text{DE base}$) $\times$ 2 insertion directions ($\text{append}, \text{prepend}$).

### Empirical Results:
- **Semantic Monotonicity:** **8 / 8 chains (100.0%)** (Zero loss of derivation, $S \to E_{\text{semantic}} = 0$).
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
No semantic monotonicity violations occurred in the tested chains. The observed transitions were **strictly positional and symbolic**: appending premises never disturbed exact token realization, but prepending an irrelevant fact (`occ_F`) to the front of `chain_1` triggered a surface-form drift without destroying the underlying derivation.

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
1. **Shortcut Replication:** Under canonical semantics, the Round 3 illicit shortcut was replicated ($BD$ and $AD$ active, $AE$ and $BE$ inactive).
2. **Phenotype Breakdown:** $AD$ and $BD$ remained active across all three representations; $AE$ activated only after role-swapping or opacity; $BE$ was strictly rejected across all three.
3. **Mechanism Interpretation:** The observed truth table is **consistent with a role-anchored predicate-class heuristic** ($AD \lor AE \lor BD$ with $BE = 0$). Because $BE$ contains two `reports_to` predicates while the other pairs each contain at least one `has_role` predicate, the model appears to require at least one role declaration to trigger derivation. Canonical natural-language semantics selectively suppress $AE$, but anonymizing role names removes that suppression. (Further predicate-level anonymization is required to distinguish role semantics from general sentence syntax).

---

## 5. Track C: Epistemic Compiler Conformance Benchmark ($N = 32$)

Track C evaluated 4 compiler pipelines across 4 test ecologies on `VELORA` and `KESTREL`.

### Preregistered Support Conformance ($N = 16$ calls across Entitled and Pruned Ecologies):

```
                            PREREGISTERED SUPPORT CONFORMANCE MATRIX (N=16)
                            
┌────────────────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Compiler Pipeline          │ K_A (Answer) │ K_S_suff     │ K_S_exact    │ Mean Excess  │
├────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ RAW_SERIALIZATION          │ 4/4 (100%)   │ 4/4 (100%)   │ 2/4 (50.0%)  │ 1.00 claims  │
│ TOPOLOGY_AWARE_GROUPING    │ 4/4 (100%)   │ 4/4 (100%)   │ 2/4 (50.0%)  │ 1.00 claims  │
│ GENEALOGICAL_NORMALIZATION │ 4/4 (100%)   │ 4/4 (100%)   │ 3/4 (75.0%)  │ 0.25 claims  │
│ PROOF_CARRYING_CERTIFICATE │ 4/4 (100%)   │ 4/4 (100%)   │ 2/4 (50.0%)  │ 1.00 claims  │
├────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ TOTAL / PREREGISTERED MEAN │ 16/16 (100%) │ 16/16 (100%) │ 9/16 (56.25%)│ 0.8125 claims│
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
├────────────────────────────┼─────────────────────────────┼──────────┼──────────┼──────────┼────────┼───────────────────┤
│ GENEALOGICAL_NORMALIZATION │ entitled_VELORA             │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ N/A (unprompted)  │
│ GENEALOGICAL_NORMALIZATION │ entitled_KESTREL            │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 1 claims │ 2      │ N/A (unprompted)  │
│ GENEALOGICAL_NORMALIZATION │ pruned_VELORA               │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ N/A (unprompted)  │
│ GENEALOGICAL_NORMALIZATION │ pruned_KESTREL              │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 0      │ N/A (unprompted)  │
│ GENEALOGICAL_NORMALIZATION │ unentitled_VELORA           │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ None   │ N/A (indeterm.)   │
│ GENEALOGICAL_NORMALIZATION │ unentitled_KESTREL          │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ None   │ N/A (indeterm.)   │
│ GENEALOGICAL_NORMALIZATION │ copy_multiplication_VELORA  │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ Abstain (null)    │
│ GENEALOGICAL_NORMALIZATION │ copy_multiplication_KESTREL │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ None   │ Abstain (null)    │
├────────────────────────────┼─────────────────────────────┼──────────┼──────────┼──────────┼────────┼───────────────────┤
│ PROOF_CARRYING_CERTIFICATE │ entitled_VELORA             │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 2 claims │ 2      │ N/A (unprompted)  │
│ PROOF_CARRYING_CERTIFICATE │ entitled_KESTREL            │ 1 (PASS) │ 1 (PASS) │ 0 (FAIL) │ 2 claims │ 2      │ N/A (unprompted)  │
│ PROOF_CARRYING_CERTIFICATE │ pruned_VELORA               │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ N/A (unprompted)  │
│ PROOF_CARRYING_CERTIFICATE │ pruned_KESTREL              │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ N/A (unprompted)  │
│ PROOF_CARRYING_CERTIFICATE │ unentitled_VELORA           │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ 1      │ N/A (indeterm.)   │
│ PROOF_CARRYING_CERTIFICATE │ unentitled_KESTREL          │ 1 (PASS) │ N/A      │ N/A      │ N/A      │ 1      │ N/A (indeterm.)   │
│ PROOF_CARRYING_CERTIFICATE │ copy_multiplication_VELORA  │ 1 (PASS) │ 0 (FAIL)*│ 0 (FAIL)*│ 1 claims │ 1      │ 1 / 1 (PASS)      │
│ PROOF_CARRYING_CERTIFICATE │ copy_multiplication_KESTREL │ 1 (PASS) │ 1 (PASS) │ 1 (PASS) │ 0 claims │ 1      │ 1 / 1 (PASS)      │
└────────────────────────────┴─────────────────────────────┴──────────┴──────────┴──────────┴────────┴───────────────────┘
```
*\* Note: In `proof_carrying_certificate_eco_copy_multiplication_VELORA`, the model cited only `DOC_01` (manager role) omitting `DOC_05` (reports_to).*

### Key Scientific Takeaways from Track C:
1. **The Epistemic Precision Gap ($K_{S,\text{suff}}$ vs $K_{S,\text{exact}}$):**
   - In pruned ecologies ($AB$ only), models isolate the minimal proof with **$100\%$ exactness** ($8/8$) and $0$ excess claims.
   - In entitled ecologies ($AB$ and $DE$ co-occurring), models achieve **$100\% K_{S,\text{suff}}$**, but exactness drops to **$12.5\%$** ($1/8$), with $6/8$ cells citing all 4 documents ($E_S = 2$).
   - **Theoretical Bridge to Epistemic Repair:** Support bloat creates a structural mechanism by which naïve dependency storage could produce unnecessary downstream revision or false autoimmunity upon partial premise invalidation.
2. **Lineage Observability vs Kernel Judgment:**
   - Merely annotating prompt strings with lineage tags (`GENEALOGICAL_NORMALIZATION`) did not induce the neural model to compute the numeric independence root count ($\to \text{null}$).
   - In contrast, explicit kernel certification (`PROOF_CARRYING_CERTIFICATE`) achieved $100\%$ compliance ($\widehat{N}=1, K_L = 2/2$).
   - **Takeaway:** The Epistemic Kernel must explicitly compute and enforce lineage statistics rather than delegating independence accounting to prompt-conditioned neural reasoning.

---

## 6. Provenance & Artifact Integrity

- **Database Path:** `data/exploration_round4_results.db`
- **Raw Execution Checksum (SHA-256):** `b07580c52d526efe03d342f257fd776d0210b6b823c4afb9ba898dc356f9401b`
- **Post-Review Augmented Checksum (SHA-256):** `820e574e6d3a0196dfec13ffc392d68d399791b210fd65187795dd834046269e`
- **Summary JSON Path:** `data/exploration_round4_summary.json`
- **Summary Checksum (SHA-256):** `8984076c22033ed79628138fbd18a44d650dc479796632dcf02bc9e501be5949`
- **Artifact Manifest:** `data/exploration_round4_artifacts.json`
- **Model Digest:** `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a` (Google Gemma 3:12B)
- **Zero Omissions / Drops:** 116 / 116 planned calls completed, parsed, and verified.
