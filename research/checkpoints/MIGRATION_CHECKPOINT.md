# Research Migration Checkpoint

> **IMPORTANT NOTICE**:
> This is a post-hoc workflow migration checkpoint, not a preregistration or claim that these constraints were frozen before the preceding work.

---

## 1. Metadata & Repository State

- **Repository / Project Name**: GENE (Genealogical Epistemic Network Experiments)
- **Checkpoint Date**: 2026-08-21
- **Current Git Commit / Tag**: `2b0cd7c` ([`round7-stage7b-live-freeze`](https://github.com/admiralorbiter/gene/releases/tag/round7-stage7b-live-freeze))
- **Current Research Stage**: Exploration Round 7 Stage 7B (Live Neural Ingress Interface & Candidate Disambiguation Benchmark)
- **Model Evaluated**: `gemma3:12b` (Ollama digest: `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`)

---

## 2. Completed Milestones & Recent Work

The following experimental and engineering milestones are fully verified and frozen in repository evidence:
1. **Experiment 0**: Lineage Observability & Causal Parent Interventions.
2. **Experiment 1A**: Single Mutation Propagation & Multi-Generational Cascades.
3. **Experiment 1B-A**: Multi-Generation Branching Transmission, Allele Fidelity, and Analytic Extinction Matrix.
4. **Experiment 1B-B**: Endogenous Multi-Hop Retrieval Dynamics ($X_F, X_A, X_{\text{path}}$), Lexical Competition, Surface-Area Scaling, and Causal Retrieval Rescue.
5. **Phase 9 / 9.5**: Persistence Hardening, Retrieval Boundary Shape Map, 48-Call Live Rescue, and 16-Call Matched Path Expression Assay ($P(\text{active}\mid\text{complete})=1, P(\text{active}\mid\text{broken})=0$).
6. **Exploration Round 4**: 4-Channel Epistemic Retrieval Architecture & Gating.
7. **Exploration Round 5 (Stages 5A, 5B, 5C)**: Lineage-Gated Action Governance, Multi-Hop Lineage Attribution, and Real-Time Revocation.
8. **Exploration Round 6 (Stages 6A, 6B, 6B.1, 6C)**: Bitemporal Supersession Algebra, Contract-Guided State Adjudication, and Neural Extraction Error Boundary Externalization.
9. **Exploration Round 7 Stage 7A (7A.0–7A.3 + Errata)**: Proof-Carrying Epistemic Ingress Benchmark (120/120 worlds verified; decoupled admission, resolution, and promotion integrity; fail-closed authorization gating).
10. **Exploration Round 7 Stage 7B (7B.0–7B.2)**: 52-Call Live Neural Ingress Assay on `gemma3:12b`, Stage 7B.1 deterministic zero-oracle replay, and Stage 7B.2 targeted 10-call ambiguity/temporal micro-assay.

---

## 3. Strongest Supported Findings

1. **Constrained Neural Candidate Extraction**:
   - `gemma3:12b` reliably extracts semantic mention spans (100% subject, 100% object, 98.1% predicate schema adherence) and valid-time start coordinates (100%) from unstructured text when provided with a structured JSON schema.
2. **Zero Positional Selection Bias under Literal Lookup**:
   - Permuting candidate entities across menu slots $[0, 1, 2, 3]$ yielded uniform selection accuracy with zero positional distortion ($H_{\text{norm}} = 1.00$).
3. **Downstream Epistemic Safety & Invariance**:
   - When coupled with the proof-carrying `IngressEngine` under `A4FullGENEIngressPolicy` with zero oracle leakage, downstream 4-probe evaluations ($Q_1, Q_2, Q_3, Q_4$) achieved $96.2\%$ fidelity (50/52) with $\text{FDAR}_{\text{global}} = 0.0\%$, $\text{UPR} = 0.0\%$, and zero runtime autoimmunity.
4. **Interface-Mediated Ambiguity Preservation**:
   - Top-1 collapse is an interface artifact: when the JSON schema explicitly supports multi-candidate subsets and `selection_status = "AMBIGUOUS_DEFER"`, `gemma3:12b` defers ambiguous mentions with $100.0\%$ accuracy (3/3) without premature collapse.
5. **Explicit Temporal Boundaries & Expiry Isolation**:
   - On explicitly bounded sentences ("from t=5.0 through t=10.0"), `gemma3:12b` extracted temporal bounds with $100.0\%$ accuracy (5/5), and the bitemporal engine maintained 100% post-expiry state isolation (4/4 expired at $t=11.0$).

---

## 4. Current Claim Limitations & Ceilings

1. **Finite Candidate Menus**: The model was evaluated on candidate selection given an externally supplied candidate set $\mathcal{B}(x)$; it was not evaluated on unconstrained open-world entity induction from raw text.
2. **Predicate Discovery vs. Schema Adherence**: The prompt provided target predicate names; 98.1% predicate accuracy represents schema adherence and span extraction rather than unassisted predicate discovery.
3. **Telemetry Ingress Policy Contract**: Quoted telemetry claims (`ClaimType.QUOTED_TELEMETRY`) are admitted as root facts only when originating from authenticated principals with `ROOT_FACT` privilege (e.g. `HIGH_PRECISION_SENSOR`); third-party or unauthenticated quotes remain strictly `ATTESTATION_ONLY`.
4. **Sample Scale**: 52 primary live calls + 10 targeted micro-assay calls on `gemma3:12b` ($T=0.0$, seed=42).

---

## 5. Established Invariants & Frozen Decisions

- **Synthetic Fictional Worlds**: Worlds precede real-world facts to isolate structural mechanisms from parametric priors.
- **Machine-Readable Ground Truth**: Canonical world truth is immutable and machine-verifiable.
- **Append-Only Memory**: Memory is strictly append-only; updates and supersessions are modeled via bitemporal transaction events.
- **Exposure Lineage**: Recorded directly by the execution harness, never inferred from model self-reports.
- **Reported Support vs Causal Support**: Model self-reports of reasoning are explicitly separated from causal parentage.
- **Zero LLM Write Authority**: Neural models propose candidate extractions and bindings; only the deterministic kernel verifies certificates and executes durable state transitions.
- **Principal-Bound Capabilities**: Capabilities are bound to verified cryptographic identity (`AuthenticatedOrigin.verified_id`), never to unverified self-assertions.
- **Fail-Closed Verification**: Any missing witness, unauthorized predicate, or ambiguity defect results in fail-closed rejection or deferral.

---

## 6. Known Open Questions & Unresolved Topics

1. **Autonomous Candidate Hypothesis Generation**: How should the system generate $\mathcal{B}(x)$ from unstructured text in an open domain without a fixed ontology candidate menu?
2. **Complex Multi-Hop Temporal Reasoning**: Scaling bitemporal supersession and interval overlap resolution across long causal chains under high event density.
3. **Candidate Next Step**: `NOT YET FROZEN`
