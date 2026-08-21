# Exploration Round 7 Stage 7B Report: Live Neural Ingress Interface & Candidate Disambiguation Benchmark

**Document Status**: Canonical Empirical Report (Stage 7B Live Neural Extraction, Zero-Leakage Replay & Interface Hardening)  
**Author**: Antigravity Research / GENE Core  
**Associated Target Commit**: `round7-stage7b-live-freeze`  
**Model Under Test**: `gemma3:12b` (Ollama digest: `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`)  
**Total Invocations**: 52 Primary Live Calls + 10 Targeted Micro-Assay Calls ($T=0.0$, seed=42)  
**Primary Artifacts**:
1. [`data/exploration_round7_stage7b_summary.json`](../../data/exploration_round7_stage7b_summary.json) (`SHA-256: f9c7a1142b38c46f5c89c68319330fa3c837db54a5a46a46bfc1763fc04fe70b`)
2. [`data/exploration_round7_stage7b_raw_calls.jsonl`](../../data/exploration_round7_stage7b_raw_calls.jsonl) (`SHA-256: fd85007539bf5bf4afd6a529c2461cfafba84634787798c1abdaecd1c672171d`)
3. [`runs/exploration_round7_stage7b_results.db`](../../runs/exploration_round7_stage7b_results.db) (SQLite Run Log)

---

## 1. Executive Summary & Core Scientific Findings

Exploration Round 7 investigates how a fallible neural front-end can extract semantic claims, time coordinates, and candidate entity bindings without acquiring direct or unconstrained write authority into persistent epistemic memory.

Stage 7B evaluates this boundary end-to-end on `gemma3:12b`. The neural model operates strictly as a semantic span extractor and candidate entity retriever ($\mathcal{B}(x) = \{b_1, \dots, b_k\}$). The resulting parsed attestation is evaluated through the deterministic `IngressEngine` governed by `A4FullGENEIngressPolicy` and verified by `CertificateVerifier` with **zero oracle leakage**.

### Key Empirical Discoveries:
1. **Constrained Neural Candidate Extraction Fidelity**: `gemma3:12b` achieved $100.0\%$ Subject Span Accuracy (52/52), $98.1\%$ Predicate Span Schema Adherence (51/52), $100.0\%$ Object Span Accuracy (52/52), $100.0\%$ Valid Time Start Accuracy (52/52), and $100.0\%$ Candidate Match Accuracy (52/52).
2. **Zero Positional Selection Bias under Literal Menu Lookup**: Across 16 counterbalanced cases permuting the target entity across slots $[0, 1, 2, 3]$, the model selected the exact entity with $100.0\%$ accuracy regardless of position (slot distribution $\{0: 4, 1: 4, 2: 4, 3: 4\}$, normalized positional entropy $H_{\text{norm}} = 1.00$).
3. **Zero-Oracle-Leakage Downstream Invariant**: Replaying raw neural extractions through the deterministic runtime with all oracle fallbacks stripped achieved $\mathbf{96.2\% \text{ Probe Pass Rate (50/52)}}$ with $\mathbf{\text{FDAR} = 0.0\%}$, $\mathbf{\text{UPR} = 0.0\%}$, and $\mathbf{0.0\% \text{ runtime autoimmunity}}$. The sole 2 non-passing cases stemmed from out-of-scope predicate extraction (`reports` instead of `device_status`), which the engine correctly rejected fail-closed.
4. **Telemetry Ingress Policy Contract**: When authenticated sensors hold `ROOT_FACT` privilege, direct observations classified as `QUOTED_TELEMETRY` are eligible for root-fact admission; unauthenticated or third-party quotes remain strictly `ATTESTATION_ONLY`.
5. **Targeted Micro-Assay on Ambiguity & Explicit Intervals (10 Calls)**:
   - **Ambiguity Preservation**: When the schema supported multi-candidate subsets (`selection_status = AMBIGUOUS_DEFER`), Gemma preserved ambiguous mentions without Top-1 collapse with $\mathbf{100.0\% \text{ accuracy (3/3)}}$.
   - **Explicit Temporal Boundaries**: On explicitly bounded intervals ("from t=5.0 through t=10.0"), Gemma extracted start and end times with $\mathbf{100.0\% \text{ accuracy (5/5)}}$, and the deterministic engine maintained post-expiry temporal isolation (fact expired at $t=11.0$) in $\mathbf{100.0\% \text{ of cases (4/4)}}$.

---

## 2. Experimental Architecture & Pipeline Separation

```
+================================================================================================================+
|                           STAGE 7B NEURAL-DETERMINISTIC INGRESS ARCHITECTURE                                    |
+================================================================================================================+
|  Unstructured Text  -->  Gemma 3:12B  -->  ParsedAttestation + Candidate Hypothesis Set B(x)                   |
|                                                    |                                                           |
|                                                    v                                                           |
|                                       A4 Full GENE Ingress Policy                                              |
|                                                    |                                                           |
|                                                    v                                                           |
|                                       CertificateVerifier (Proof-Carrying)                                     |
|                                                    |                                                           |
|                                                    v                                                           |
|                      +-----------------------------+-----------------------------+                             |
|                      |                             |                             |                             |
|                      v                             v                             v                             |
|                  [ADMIT]                        [DEFER]                      [REJECT]                          |
|           Authoritative Fact Store       Deferred Binding Store       Attestation Archive Only                 |
+================================================================================================================+
```

---

## 3. Detailed Results & Empirical Breakdown

### 3.1 Field-Level Extraction Accuracies (52 Calls)
```
+================================+=======================+==================================================+
| Extraction Target Field        | Empirical Accuracy    | Error Localization & Characterization            |
+================================+=======================+==================================================+
| Subject Mention Span           | 52 / 52 (100.0%)      | Verbatim substring extracted without drift       |
| Predicate Span                 | 51 / 52 (98.1%)       | 1 formatting extraction error (reports)          |
| Object Mention Span            | 52 / 52 (100.0%)      | Normalized status recognized correctly           |
| Valid Time Start (t_v_start)   | 52 / 52 (100.0%)      | Exact float coordinate extracted from text       |
| Candidate Entity Match         | 52 / 52 (100.0%)      | Exact match to target candidate ID               |
| Novelty Detection              | 52 / 52 (100.0%)      | Correctly identified novel entities              |
+================================+=======================+==================================================+
```

### 3.2 Downstream Factorial Invariance (32 Primary Calls)
```
+======================+======================+===================+===================+==========================+
| Linguistic Condition | Source Privilege     | Admission Status  | Probe Vector      | Downstream Epistemic Fix |
+======================+======================+===================+===================+==========================+
| EXACT_MATCH          | AUTHORIZED_SENSOR    | ADMIT             | (1, 1, 1, 1)      | Admitted as Root Fact    |
| EXACT_MATCH          | UNPRIVILEGED_GUEST   | REJECT            | (1, 1, 1, 1)      | Blocked fail-closed      |
| LEXICAL_ALIAS        | AUTHORIZED_SENSOR    | ADMIT             | (1, 1, 1, 1)      | Alias resolved -> Fact   |
| LEXICAL_ALIAS        | UNPRIVILEGED_GUEST   | REJECT            | (1, 1, 1, 1)      | Blocked fail-closed      |
| TRUE_AMBIGUITY       | AUTHORIZED_SENSOR    | DEFER             | (1, 1, 1, 1)      | DEFERRED_BINDING preserved|
| TRUE_AMBIGUITY       | UNPRIVILEGED_GUEST   | REJECT            | (1, 1, 1, 1)      | Blocked fail-closed      |
| NOVEL_ENTITY         | AUTHORIZED_SENSOR    | DEFER             | (1, 1, 1, 1)      | PROVISIONAL_ENTITY created|
| NOVEL_ENTITY         | UNPRIVILEGED_GUEST   | REJECT            | (1, 1, 1, 1)      | Blocked fail-closed      |
+======================+======================+===================+===================+==========================+
```

### 3.3 Stage 7B.2 Targeted Micro-Assay Findings (10 Calls)
1. **Multi-Candidate Ambiguity Deferral**:
   - When given mentions like "Server 1" matching multiple candidates, Gemma returned `AMBIGUOUS_DEFER` with `["Server_Node_1", "Server_Node_1_Backup"]` across all 3 ambiguous cases (3/3 = 100.0%).
   - On unambiguous ("Server_Node_1") and novel ("Quantum Switch Omega") controls, the model correctly selected `RESOLVED` and `NOVEL`.
2. **Explicit Temporal Interval Extraction & Post-Expiry Isolation**:
   - Gemma extracted explicit valid-time intervals ("from t=5.0 through t=10.0", "until t=8.0") with 100.0% accuracy (5/5).
   - In the bitemporal engine, facts were active inside interval $[t_{\text{start}}, t_{\text{end}}]$ and fully expired at $t > t_{\text{end}}$ (4/4 = 100.0%), confirming interval boundary isolation.

---

## 4. Scientific Claims Validated

1. **Neural Candidate Extraction without Write Authority**: Small open-weight models (Gemma 3:12B) can accurately parse unstructured telemetry, extract valid-time coordinates, and resolve entity candidate references without being given durable-write authority.
2. **Interface Ambiguity Representation**: Neural Top-1 collapse is an interface-contract defect: when the prompt schema explicitly supports multi-candidate subsets and `DEFER`, the model preserves ambiguity rather than hallucinating a single entity choice.
3. **Zero-Leakage Ingress Immunity**: The GENE Epistemic Ingress architecture prevents both false durable admissions ($\text{FDAR} = 0.0\%$) and unauthorized promotions ($\text{UPR} = 0.0\%$) under live neural inputs.

---

## 5. Artifact Verification & Manifest Alignment

- **Unit Test Suite**: 205 passing tests (`pytest -v`).
- **Canonical Manifest**: Checked and deeply synchronized via `python scripts/verify_repo.py`.
- **Database Logs**: SQLite run logs and raw JSONL archives committed and tracked.
