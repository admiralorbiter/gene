---
contract_id: CONTRACT-R8-8C-R3-R1
status: DRAFT
base_sha: 92400bf22a24316e5c1522489a1a003c365fe848
created_at: "2026-08-22 10:55:00Z"
proposed_by: antigravity
design_review: CHANGES_REQUESTED
reviewed_by: chatgpt-pro
authorized_by: null
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: false
---

# Research Contract: CONTRACT-R8-8C-R3-R1 (Definitive Stage 8 Closure & Epistemic Ingress Decoupling)

**Lifecycle Status**: `DRAFT` (Scientific Review: CHANGES_REQUESTED; Awaiting Re-Review & Human Strategic Authorization)

---

## 1. Executive Summary & Epistemic Motivation

Stage 8C-R3 observed candidate evidence showing 97/97 resolvable coverage and a 39-recovery/0-regression historical replay, but ended `REVISED_CONTRACT_REQUIRED` because Gate 5 did not meet its preregistered lifecycle criterion.

Specifically, R3 revealed a crucial architectural insight:
$$\textbf{Neural Proposal Conservatism} \neq \textbf{Lifecycle State Machine Correctness}$$

When the neural prompt commanded *"Never guess or merge distinct entities without strong evidence"*, Gemma 3 12B safely proposed `candidate_action: "DEFER"` with `target_entity_id: null` on all ungrounded ambiguous mentions. This caused Gate 5 to observe $3/7$ exact matches rather than $7/7$ because the live neural proposer refused to speculate on ungrounded candidate targets.

**CONTRACT-R8-8C-R3-R1** delivers the surgical closure of Stage 8:
1. **Decouples Live Lifecycle Testing from Neural Speculation**: Live Gate 5 validates that the hypothesis ledger transition matches the *actual* candidate proposal (`cand is None` $\to$ `RESOLVED_EXISTING`, `cand == target` $\to$ `CONFIRMED`, `cand != target` $\to$ `RETARGETED`, novel creation $\to$ `RESOLVED_NOVEL`).
2. **Deterministic CPU Branch-Coverage Assay (Gate 5b)**: A standalone unit test that injects synthetic candidates to prove all four terminal transitions execute with 100% mathematical soundness.
3. **Dual Paired Comparators**:
   - **Total Historical Gain**: $R3 - \text{Frozen } R2$.
   - **Isolated Precedence Attribution**: $R3 - R3_{\text{ablation}}$ (a matched resolver where structural mentions lacking sub-IDs immediately defer without Rule 3 fall-through, while valid structural partitions with sub-IDs execute identically to R3-R1).
4. **Fresh Sealed Worlds & Machine-Verifiable Freshness Audit**: 60 genuinely lexically fresh synthetic worlds ($120$ decisions) generated with PRNG seed `2718281828`, with an automated freshness assertion verifying zero lexical overlap with R3 across Arms 1, 3, 4A, and 4B.

---

## 2. Statistical Acceptance Gates ($N=120$ Decisions, $N=97$ Resolvable)

| Gate ID | Target Metric | Preregistered Boundary | Evaluation Method |
| :--- | :--- | :--- | :--- |
| **Gate 1** | Neural Proposal Telemetry Logging | Logged across all $N=120$ decisions | `len(records) == 120` and all have `neural_proposal` |
| **Gate 2a** | False Canonical Merge Floor | $\equiv 0.0\%$ ($0/120$ false merges) | Zero links to canonical entities outside gold expected target |
| **Gate 2b** | False Provisional Floor on Unasserted | $\equiv 0.0\%$ ($0/16$ unasserted mentions) | Zero `CREATE_PROVISIONAL` actions in Arm 4A |
| **Gate 3** | Provisional Entity Fragmentation | $\equiv 0$ duplicate provisional creations | Zero duplicate provisional entities created within any single world |
| **Gate 4** | Permanent Deferral Invariant (Arm 4A) | $\ge 7/8$ ($87.5\%$) fully deferred worlds | At least 7 of 8 Arm 4A worlds have both Doc 1 and Doc 2 deferring |
| **Gate 5** | Live Lifecycle State Machine (Arm 4B) | $\equiv 7/7$ sound transitions | Status matches actual candidate proposal, resolves to Doc 2, 2 evidence items |
| **Gate 5b** | Deterministic CPU Branch Coverage | $\equiv \text{PASS}$ across all 5 branches | Synthetic injection proves `RETARGETED`, `CONFIRMED`, `RESOLVED_EXISTING`, `RESOLVED_NOVEL`, `UNRESOLVED` |
| **Gate 6** | Useful Resolvable Coverage ($N=97$ Resolvable) | $\ge 85.0\%$ across $N=97$ resolvable events | Useful admissions / 97 resolvable events |
| **Gate 7** | Relational DB & Ledger Reconciliation | Strict 8 UNRESOLVED + 7 Resolved == 15 Total | Integrity OK, 0 FK violations, 120 execution records, 15 hypothesis rows |
| **Audit** | Freshness Audit vs Frozen R3 | $\equiv \text{PASS}$ ($\text{Overlap} \equiv \emptyset$) | Machine-verifiable disjointness across Arms 1, 3, 4A, and 4B |

---

## 3. Scientific Claim Ceiling

### Certified Finding Authorized Upon Promotion
> In a controlled synthetic streaming hardware benchmark ($N=60$ fresh worlds, $120$ decisions), hybrid neural-symbolic ingress with refined precedence achieves $\ge 85.0\%$ useful admission coverage on resolvable events with $0.0\%$ false canonical and provisional commitments, while the deterministic hypothesis ledger maintains 100% sound evidence accumulation across all lifecycle transitions.

### Explicit Exclusions
This contract does **NOT** authorize claims of unstructured open-world entity resolution, unsupervised ontology discovery, or autonomous claim-level truth maintenance (which begins in Stage 9).
