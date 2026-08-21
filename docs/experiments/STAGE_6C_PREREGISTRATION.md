# Preregistration: Exploration Round 6 Stage 6C — Neural Semantic Observation Extraction & Upward Error Migration Assay

## 1. Executive Protocol & Purpose

Following the completion of Stage 6A (Bitemporal Supersession Engine) and Stage 6B (Contract-Guided State Adjudication), Stage 6C investigates the **Neural-Formal Ingress Boundary** of the GENE epistemic architecture.

### Research Question
Can a local neural model reliably convert natural language sentences into structured factual observations $\langle \text{subject}, \text{predicate}, \text{object}, t_{v,\text{start}}, t_{v,\text{end}} \rangle$ required by an already-correct formal epistemic runtime, and does modular extraction externalize errors to the input boundary without corrupting downstream durable state?

---

## 2. Experimental Arms ($N=12$ Cases $\times$ 2 Neural Arms $+$ 4 Canaries $=$ 28 Calls)

### Arm N1: End-to-End Direct Neural Transition Emission
- **Interface**: The neural model is supplied with the natural language observation, the current active facts in memory, and the predicate ontology contract.
- **Task**: The model is prompted to directly output the formal state-transition event batch (`ASSERT`, `SUPERSEDES`, `CONTRADICTS`, `RETRACT`) in structured JSON.
- **Hypothesis**: Direct memory mutation will suffer severe transition syntax and bitemporal reasoning failures due to unconstrained state adjudication in autoregressive generation.

### Arm N2: Modular Semantic Observation Extraction (GENE Bridge)
- **Interface**: The neural model is supplied strictly with the natural language observation and the target predicate name/mode.
- **Task**: The model extracts solely the factual proposition tuple $\langle \text{subject}, \text{predicate}, \text{object}, t_{v,\text{start}}, t_{v,\text{end}} \rangle$.
- **Downstream Runtime**: The formal runtime receives the extracted observation, attaches trusted metadata, executes contract-guided adjudication (`adjudicate_observation`), updates the bitemporal occurrence state, and computes minimal antichain support $S_{t_v}(q \mid t_k)$.

### Arm C0: Deterministic Oracle Extraction Ceiling
- **Interface**: The gold structured observation tuple is provided directly to the deterministic GENE runtime ($0$ live model calls).
- **Purpose**: Establishes the mathematical ceiling ($100.0\%$) of downstream state and support derivation.

---

## 3. Trusted Metadata Invariant

To avoid provenance laundering and epistemic hallucinations, the following fields are **strictly injected by the harness runtime** and never extracted or predicted by the neural model:
- Knowledge transaction time $t_k \in \mathbb{N}$;
- Source identifier `source_id`;
- Sensor/origin identifier `origin_id`;
- Upstream lineage roots `lineage_roots`.

---

## 4. Benchmark Composition ($N=12$ Cases)

The benchmark is balanced across 4 Predicate Contracts $\times$ 4 Temporal Update Scenarios:

| Case ID | Predicate Mode | Update Scenario | Target Predicate | Text Assertion |
|:---|:---|:---|:---|:---|
| `C6C_01` | `TIME_VARYING` | Forward Update | `clearance` | Upgrade to level Gamma at cycle 10 |
| `C6C_02` | `TIME_VARYING` | Retroactive Correction | `role` | Auditor assigned as of cycle 2 |
| `C6C_03` | `TIME_VARYING` | Contemporaneous Dispute | `status` | Independent dispute at cycle 0 |
| `C6C_04` | `TIME_VARYING` | Recurrence / Reassertion | `zone` | Return to Sector 7 at cycle 15 |
| `C6C_05` | `ADDITIVE` | Forward Addition | `certified_skill` | Skill Cryptography acquired at cycle 4 |
| `C6C_06` | `ADDITIVE` | Retroactive Addition | `certified_skill` | Backfilled skill NetworkSecurity as of cycle 1 |
| `C6C_07` | `ADDITIVE` | Contemporaneous Addition | `authorized_tool` | QuantumKey equipped at cycle 0 |
| `C6C_08` | `ADDITIVE` | Reassertion / Renewal | `certified_skill` | PythonArchitecture renewed at cycle 12 |
| `C6C_09` | `EPISODIC` | Forward Point Event | `logged_access` | Terminal Vault 4 accessed at cycle 8 |
| `C6C_10` | `EPISODIC` | Retroactive Point Event | `audit_alert` | Threshold breach discovered at cycle 3 |
| `C6C_11` | `INTERVAL_BOUNDED` | Forward Interval | `active_lease` | Lease valid [5.0, 10.0) |
| `C6C_12` | `INTERVAL_BOUNDED` | Contemporaneous Dispute | `active_lease` | Disputed lease interval [0.0, 5.0) |

---

## 5. Metric Definitions & Four-Layer Decomposition

1. **Layer 0 (Semantic Extraction Fidelity)**:
   - Evaluated field-by-field: Subject Accuracy, Predicate Accuracy, Object Accuracy, $t_{v,\text{start}}$ Accuracy, $t_{v,\text{end}}$ Accuracy, and Complete Tuple Match.
2. **Layer A (State Transition Fidelity)**:
   - Exact tuple match on normalized transition event sequences: `(event_type, target_fact_id, secondary_fact_id, t_v_start, t_v_end)`.
3. **Layer B (Premise State Fidelity)**:
   - **Active Occurrence-Set Fidelity**: Set equality on active fact IDs holding at $(t_v, t_k)$.
   - **Semantic Premise-State Fidelity**: Set equality on full factual state tuples holding at $(t_v, t_k)$: $\langle s, p, o, \text{source}, [t_{\text{start}}, t_{\text{end}}) \rangle$.
4. **Layer C (Epistemic Support & Entitlement)**:
   - **Support Fidelity**: Set equality on minimal premise antichain support sets $S_{t_v}(q \mid t_k)$.
   - **Entitlement Accuracy**: Boolean agreement on derivability $\text{Entitled}(q \mid t_v, t_k) \iff |S_{t_v}(q \mid t_k)| > 0$.
5. **Fault Localization & Error Migration**:
   - Classify all entitlement failures into exact origins: `OBSERVATION_EXTRACTION_ERROR`, `TRANSITION_EMISSION_ERROR`, `PREMISE_STATE_ERROR`, or `SUPPORT_DERIVATION_ERROR`.

---

## 6. Pre-Execution Local Manifest Standard

The experiment protocol requires a pre-execution dataset and manifest artifact:
- Dataset: `data/exploration_round6_stage6c_cases.jsonl`
- Manifest: `data/exploration_round6_stage6c_manifest.json` (specifying SHA256, model parameters, and call budget)
- Local Model: `gemma3:12b` (pinned digest: `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`)
