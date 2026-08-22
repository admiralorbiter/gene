---
contract_id: CONTRACT-R8-8C-R3
status: DRAFT
base_sha: 1f3b0207345563ce903d00777455e1f8ed0f46f0
resource_class: gpu
long_running: false
exclusive_gpu: true
interruptible: true
proposed_by: antigravity
design_review: APPROVED
reviewed_by: chatgpt-pro
authorized_by: null
---

# Research Contract: CONTRACT-R8-8C-R3 (Two-Stage Epistemic Ingress with Refined Precedence)

## 1. Executive Summary & Moonshot Objective

This contract executes the confirmatory benchmark for **Stage 8C-R3**, validating two-stage hybrid entity resolution and ontology ingress under the **Existence $\neq$ Identity** architectural decoupling, incorporating the single precedence policy clarification exposed by burned development evidence in Stage 8C-R2 (World 55).

### The Scientific Boundary: Refined Precedence Policy

$$\text{Mention } s \longrightarrow \begin{cases} 
\text{Rule 1: Exact Registered Alias} & \text{if } N(s) \in \text{Aliases}(E) \\
\text{Rule 2: Structural First Refusal} & \text{if } \text{Parent}(s) \in \text{Entities} \land \text{SubID}(s) \neq \emptyset \\
\text{Rule 3: Parenthetical Identity} & \text{if } \text{Parenthetical}(s \lor \text{Ctx}) \in \text{Aliases}(E) \\
\text{Rule 4: Novel Standalone Commissioning} & \text{if } \text{Asserted}(s) \land \text{New}(s) \\
\text{Rule 5: Fail-Closed Deferral} & \text{otherwise}
\end{cases}$$

- **Rule 2 Precedence Scope**: Structural first refusal activates *only* when a mention contains a grounded parent entity and a valid discriminating structural sub-identifier (e.g., `Partition 1`, `Blade 2`, `Slice B`).
- **Rule 3 Precedence Scope**: Structural-looking mentions lacking a discriminating sub-identifier (e.g., `"SAN Alpha Mirror Pool (SAN-Beta)"`) defer to registered parenthetical identity evidence (e.g. `(SAN-Beta)`) if present; otherwise they fail closed to `DEFER` without durable registry mutation.

---

## 2. Statistical Acceptance Gates

| Gate ID | Metric & Target | Invariant Boundary |
| :--- | :--- | :--- |
| **Gate 1** | Neural Proposal Quality Telemetry | Logged across all $N=120$ decisions |
| **Gate 2a** | False Canonical Merge Floor $\equiv 0.0\%$ ($0/120$) | Zero false merges into canonical entities |
| **Gate 2b** | False Provisional Existence Floor $\equiv 0.0\%$ | Zero provisional creations on unasserted mentions |
| **Gate 3** | Provisional Fragmentation $\equiv 0$ duplicates | Single provisional entity per novel identity |
| **Gate 4** | Permanent Deferral Invariant $\ge 7/8$ ($87.5\%$) | Unresolvable / adversarial cases deferred |
| **Gate 5** | Disconfirmation & Accumulation Matrix $\equiv 7/7$ ($100.0\%$) | Exact handling of Arm 4B cases |
| **Gate 6** | Useful Resolvable Coverage $\ge 85.0\%$ | Useful admission across $N=97$ resolvable decisions |
| **Gate 7** | Relational DB & Ledger Integrity Audit | SQLite integrity ok, 0 FK errors, full edge ledger |

---

## 3. Execution Environment & Cryptographic Sealing

- **Model**: Gemma 3 12B Instruct (Q4_K_M) via local Ollama endpoint (`http://127.0.0.1:11434/api/generate`).
- **Worlds Generator**: `src/gene/benchmarks/r8_stage8c_r3/worlds.py` with PRNG seed `3141592653` ($N=60$ worlds, $120$ decisions).
- **Sealing Manifest**: [`research/contracts/SEALING_MANIFEST-R8-8C-R3.json`](SEALING_MANIFEST-R8-8C-R3.json).
