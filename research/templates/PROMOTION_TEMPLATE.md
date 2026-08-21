# Promotion Record: [Experiment / Milestone Name]

---

## 1. Provenance & Execution Identifiers

- **Contract Base Commit (Base SHA)**: `[insert base commit hash here]`
- **Candidate Implementation Commit (Candidate SHA)**: `[insert candidate commit hash here]`
- **Repository Freeze Tag**: `[e.g., round8-stage8a-freeze]`
- **Date of Completion**: `YYYY-MM-DD`
- **Primary Research Question Tested**: `[Restate question from contract]`

---

## 2. Implementation & Execution Summary

- **Implementation Overview**: `[Brief summary of components built/hardened]`
- **Experiments Executed**: `[Total calls, arms, factorial structure]`
- **Models Used**: `[Model name and exact digest]`
- **Compute Consumed**: `[Total runtime, call count, hardware/daemon logs]`

---

## 3. Empirical Results & Acceptance Verification

```
+================================+=======================+=======================+================+
| Evaluation Metric / Estimand   | Preregistered Target  | Empirical Result      | Status         |
+================================+=======================+=======================+================+
| [Metric 1]                     | [Target 1]            | [Result 1]            | PASS / FAIL    |
| [Metric 2]                     | [Target 2]            | [Result 2]            | PASS / FAIL    |
+================================+=======================+=======================+================+
```

- **Acceptance Criteria Outcome**: `MET` | `UNMET` | `PARTIALLY_MET`
- **Repository Test Suite Status**: `205 / 205 PASSED` (`python scripts/verify_repo.py`)
- **Independent / Peer Review Status**: `APPROVED` / `PENDING`

---

## 4. Hardening Corrections & Unexpected Findings

- **Corrections Made During Hardening**: `[List any bug fixes, oracle leakage removals, or schema fixes]`
- **Unexpected Findings / Anomalies**: `[Document any surprising behaviors or edge cases]`
- **Epistemic Belief / Interpretation Updates**: `[How did the findings update the theoretical model?]`

---

## 5. Claims & Ledger Updates

- **Claim ID(s) Registered / Updated**: `[e.g., GENE-C18]`
- **Claim Headline**: `[...]`
- **Claim Scope & Limitations**: `[...]`

---

## 6. Unresolved Issues & Known Gaps

- **Unresolved Anomalies / Edge Cases**: `[Document any observed runtime issues, schema discrepancies, or edge case failures]`
- **Methodological / Benchmark Limitations**: `[Identify constraints of the current experimental design or population scope]`
- **Known Gaps for Future Rounds**: `[List open questions that remain out of scope for this milestone but must be addressed eventually]`

---

## 7. Escalation & Governance Review

- **Potential Epistemic Escalation**: `NO` | `YES`
- *(If YES, explain the epistemic decision required by the human researcher)*: `[...]`

---

## 8. Roadmap & Candidate Next Steps

- **Candidate Next Step**: `[Reference next milestone from roadmap or write NOT YET FROZEN]`
