"""Deterministic Lineage Integrity & Attack Matrix Assay (v1).

Executes concrete deterministic root-splitting and root-merging attacks on
support hypergraphs, measuring actual quantitative distortion on S_L, kappa_L,
and action governance decisions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    BitemporalRule,
    EventType,
    TemporalEvent,
    compute_antichain,
    compute_cut_set_size,
)


def run_root_splitting_attack_assay() -> dict[str, Any]:
    """Attack 1: Root Splitting (Sybil Roots).

    An adversarial agent splits a single untrusted root R_1 into three fake roots
    {R_1a, R_1b, R_1c} to artificially inflate cut-set resilience kappa_L from 1 to 3,
    illegally bypassing a governance policy requiring kappa_L >= 2.
    """
    engine_honest = BitemporalEngine()
    engine_attacked = BitemporalEngine()

    # Honest scenario: 3 premises derived from the same single root R_1
    f1 = BitemporalFact("f1", "Target", "param", "V1", roots=frozenset(["R_1"]))
    f2 = BitemporalFact("f2", "Target", "param", "V2", roots=frozenset(["R_1"]))
    f3 = BitemporalFact("f3", "Target", "param", "V3", roots=frozenset(["R_1"]))
    for f in [f1, f2, f3]:
        engine_honest.register_fact(f)
        engine_honest.record_event(TemporalEvent(f"ev_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    # Attacked scenario: Adversary re-labels roots as 3 distinct roots
    f1_att = BitemporalFact("f1", "Target", "param", "V1", roots=frozenset(["R_1a"]))
    f2_att = BitemporalFact("f2", "Target", "param", "V2", roots=frozenset(["R_1b"]))
    f3_att = BitemporalFact("f3", "Target", "param", "V3", roots=frozenset(["R_1c"]))
    for f in [f1_att, f2_att, f3_att]:
        engine_attacked.register_fact(f)
        engine_attacked.record_event(TemporalEvent(f"ev_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    # Rules: each fact independently entitles Goal
    goal = ("Target", "action", "EXECUTE")
    for fid in ["f1", "f2", "f3"]:
        param = "V1" if fid == "f1" else "V2" if fid == "f2" else "V3"
        r = BitemporalRule(f"r_{fid}", goal, (("Target", "param", param),))
        engine_honest.register_rule(r)
        engine_attacked.register_rule(r)

    # Evaluate honest
    honest_l = engine_honest.compute_temporal_lineage(goal, t_v=0.0, t_k=0)
    honest_kappa = compute_cut_set_size(honest_l)
    honest_gate = "PERMIT" if honest_kappa >= 2 else "BLOCK"

    # Evaluate attacked
    attack_l = engine_attacked.compute_temporal_lineage(goal, t_v=0.0, t_k=0)
    attack_kappa = compute_cut_set_size(attack_l)
    attack_gate = "PERMIT" if attack_kappa >= 2 else "BLOCK"

    return {
        "attack_name": "Root Splitting (Sybil Roots Inflation)",
        "mechanism": "Adversary splits single root R_1 into {R_1a, R_1b, R_1c}",
        "honest_S_L": [sorted(list(s)) for s in honest_l],
        "honest_kappa_L": honest_kappa,
        "honest_policy_decision": honest_gate,
        "attacked_S_L": [sorted(list(s)) for s in attack_l],
        "attacked_kappa_L": attack_kappa,
        "attacked_policy_decision": attack_gate,
        "policy_breach_detected": honest_gate == "BLOCK" and attack_gate == "PERMIT",
        "cryptographic_defense": "Write-time digital origin binding: Origin certificates signed by private source keys prevent sybil root synthesis.",
    }


def run_root_merging_attack_assay() -> dict[str, Any]:
    """Attack 2: Root Merging (Corroboration Suppression / Denial of Service).

    An adversary (or uncalibrated summarizer) merges 3 genuinely independent roots
    {R_1, R_2, R_3} into a single root {R_common}, destroying true cut-set resilience
    (kappa_L: 3 -> 1) and falsely blocking legitimate high-resilience actions.
    """
    engine_honest = BitemporalEngine()
    engine_attacked = BitemporalEngine()

    f1 = BitemporalFact("f1", "Target", "param", "V1", roots=frozenset(["R_1"]))
    f2 = BitemporalFact("f2", "Target", "param", "V2", roots=frozenset(["R_2"]))
    f3 = BitemporalFact("f3", "Target", "param", "V3", roots=frozenset(["R_3"]))
    for f in [f1, f2, f3]:
        engine_honest.register_fact(f)
        engine_honest.record_event(TemporalEvent(f"ev_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    f1_m = BitemporalFact("f1", "Target", "param", "V1", roots=frozenset(["R_COMMON"]))
    f2_m = BitemporalFact("f2", "Target", "param", "V2", roots=frozenset(["R_COMMON"]))
    f3_m = BitemporalFact("f3", "Target", "param", "V3", roots=frozenset(["R_COMMON"]))
    for f in [f1_m, f2_m, f3_m]:
        engine_attacked.register_fact(f)
        engine_attacked.record_event(TemporalEvent(f"ev_{f.fact_id}", EventType.ASSERT, t_knowledge=0, t_valid_start=0.0, target_fact_id=f.fact_id))

    goal = ("Target", "action", "EXECUTE")
    for fid in ["f1", "f2", "f3"]:
        param = "V1" if fid == "f1" else "V2" if fid == "f2" else "V3"
        r = BitemporalRule(f"r_{fid}", goal, (("Target", "param", param),))
        engine_honest.register_rule(r)
        engine_attacked.register_rule(r)

    honest_l = engine_honest.compute_temporal_lineage(goal, t_v=0.0, t_k=0)
    honest_kappa = compute_cut_set_size(honest_l)
    honest_gate = "PERMIT" if honest_kappa >= 2 else "BLOCK"

    attack_l = engine_attacked.compute_temporal_lineage(goal, t_v=0.0, t_k=0)
    attack_kappa = compute_cut_set_size(attack_l)
    attack_gate = "PERMIT" if attack_kappa >= 2 else "BLOCK"

    return {
        "attack_name": "Root Merging (Denial of Service Suppression)",
        "mechanism": "Adversary or summarizer collapses {R_1, R_2, R_3} into {R_COMMON}",
        "honest_S_L": [sorted(list(s)) for s in honest_l],
        "honest_kappa_L": honest_kappa,
        "honest_policy_decision": honest_gate,
        "attacked_S_L": [sorted(list(s)) for s in attack_l],
        "attacked_kappa_L": attack_kappa,
        "attacked_policy_decision": attack_gate,
        "policy_breach_detected": honest_gate == "PERMIT" and attack_gate == "BLOCK",
        "defense": "Immutable root preservation across summarization and transformations.",
    }


def run_lineage_attack_matrix_v1() -> dict[str, Any]:
    """Execute the full lineage attack assay."""
    print("=" * 70)
    print("      GENE LINEAGE INTEGRITY ATTACK ASSAY v1                       ")
    print("=" * 70)

    attacks = [
        run_root_splitting_attack_assay(),
        run_root_merging_attack_assay(),
    ]

    summary = {
        "assay_name": "Lineage Integrity Threat Model & Attack Matrix v1",
        "attacks_evaluated": attacks,
    }

    out_json = Path(r"C:\Users\admir\Github\gene\data\exploration_round6_lineage_threat_matrix_summary.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved Lineage Attack Matrix v1 summary to {out_json}")

    return summary


def write_lineage_threat_model_v1_report(summary: dict[str, Any]) -> None:
    """Generate formal Markdown report for Lineage Threat Model v1."""
    report_path = Path(r"C:\Users\admir\Github\gene\docs\results\LINEAGE_INTEGRITY_THREAT_MATRIX.md")

    sections = []
    for a in summary["attacks_evaluated"]:
        sections.append(f"""### Attack: `{a['attack_name']}`
- **Adversarial Mechanism**: {a['mechanism']}
- **Honest Hypergraph $\\mathcal{{S}}_L$**: `{a['honest_S_L']}` ($\\kappa_L = {a['honest_kappa_L']}$, Policy Decision: **{a['honest_policy_decision']}**)
- **Attacked Hypergraph $\\mathcal{{S}}_L$**: `{a['attacked_S_L']}` ($\\kappa_L = {a['attacked_kappa_L']}$, Policy Decision: **{a['attacked_policy_decision']}**)
- **Policy Breach Demonstrated**: **{'YES (Gate Inverted)' if a['policy_breach_detected'] else 'NO'}**
- **Defense Requirement**: **{a.get('cryptographic_defense', a.get('defense'))}**
""")

    body = "\n".join(sections)

    md = f"""# Exploration Round 6 Lineage Integrity Threat Model & Attack Report (v1)

**Assay Name**: Lineage Integrity & Adversarial Manipulation Analysis v1  
**Target Milestone**: Exploration Round 6  
**Summary Artifact**: [`../../data/exploration_round6_lineage_threat_matrix_summary.json`](../../data/exploration_round6_lineage_threat_matrix_summary.json)

---

## Executive Summary

GENE's action governance theorems establish that an agent's authority to act on a belief $c$ is proportional to its ancestral root cut-set resilience $\\kappa_L(\\mathcal{{S}}_L(c))$. If derivational lineage is treated as an unauthenticated, mutable metadata dictionary, an adversary can directly manipulate action gates via **Root Splitting** or **Root Merging**.

This assay formally implements and deterministically measures these two attack modalities, demonstrating how unauthenticated lineage allows adversaries to either illegally force actions (`BLOCK` $\\to$ `PERMIT`) or cause denial of service (`PERMIT` $\\to$ `BLOCK`).

```
+========================================================================================================================+
|                                    LINEAGE ATTACK MATRIX v1 RESULTS                                                    |
+================================+=========================+===========================+=================================+
| Attack Modality                | Honest Metric           | Attacked Metric           | Governance Gate Impact          |
+================================+=========================+===========================+=================================+
| 1. Root Splitting (Sybil)      | kappa_L = 1 (BLOCK)     | kappa_L = 3 (PERMIT)      | FORCED ACTION PERMISSION        |
| 2. Root Merging (Suppression)  | kappa_L = 3 (PERMIT)    | kappa_L = 1 (BLOCK)       | FALSE ACTION DENIAL (DoS)       |
+================================+=========================+===========================+=================================+
```

---

## Detailed Attack Experimental Results

{body}

---

## Invariant Defense Requirements

1. **Write-Time Cryptographic Origin Binding**: Lineage roots $\\mathcal{{L}}(p)$ must be signed with private source keys $\\text{{Sign}}_{{K}}(f)$ at acquisition time. Agents cannot synthesize or relabel root IDs post-hoc.
2. **Conjunctive Tool Envelope Propagation**: Any intermediary transformation tool must compute $\\mathcal{{L}}(\\text{{out}}) = \\mathcal{{L}}(\\text{{tool}}) \\cup \\bigcup_i \\mathcal{{L}}(\\text{{in}}_i)$.
"""
    report_path.write_text(md.strip() + "\n", encoding="utf-8")
    print(f"Wrote Lineage Threat Model v1 report to {report_path}")


if __name__ == "__main__":
    summary = run_lineage_attack_matrix_v1()
    write_lineage_threat_model_v1_report(summary)
