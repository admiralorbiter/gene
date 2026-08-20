"""Unit and golden calibration tests for Experiment 1B-C0.

Verifies closed-form algebraic invariants, 7-policy control decomposition,
and 4-state audit ledger for the epistemic immunity policy engine.
"""

import pytest
from gene.immunity.policy_engine import (
    EpistemicPolicyEngine,
    PolicyNode,
    get_analytic_state_weights,
)


def test_analytic_state_weights_normalization():
    """Verify sum of analytic joint probabilities equals 1.0 for all grid points."""
    tprs = [0.5, 0.75, 0.9, 1.0]
    fprs = [0.0, 0.05, 0.10, 0.20, 0.40]

    for tpr in tprs:
        for fpr in fprs:
            w = get_analytic_state_weights(tpr, fpr)
            assert len(w) == 4
            total = sum(w.values())
            assert pytest.approx(total, abs=1e-9) == 1.0


def test_golden_isomorphic_tree_separation_identity():
    """Verify closed-form identity S = TPR - FPR on synthetic isomorphic trees."""
    # Build synthetic isomorphic trees:
    # Clean: H0 -> H1 -> H2
    # Infected: I0 -> I1 -> I2
    clean_nodes = [
        PolicyNode(node_id="H0", locus_id="supervisor", generation=0, is_root=True, family_id="clean_fam"),
        PolicyNode(node_id="H1", locus_id="protocol", generation=1, parent_ids=("H0",), family_id="clean_fam"),
        PolicyNode(node_id="H2", locus_id="terminal", generation=2, parent_ids=("H1",), family_id="clean_fam"),
    ]
    infected_nodes = [
        PolicyNode(node_id="I0", locus_id="supervisor", generation=0, is_root=True, family_id="inf_fam", is_infected_allele=True),
        PolicyNode(node_id="I1", locus_id="protocol", generation=1, parent_ids=("I0",), family_id="inf_fam", is_infected_allele=True),
        PolicyNode(node_id="I2", locus_id="terminal", generation=2, parent_ids=("I1",), family_id="inf_fam", is_infected_allele=True),
    ]
    pool = clean_nodes + infected_nodes

    tprs = [0.5, 0.75, 0.9, 1.0]
    fprs = [0.0, 0.05, 0.10, 0.20, 0.40]

    for tpr in tprs:
        for fpr in fprs:
            weights = get_analytic_state_weights(tpr, fpr)
            c_h = 0.0
            c_i = 0.0

            for (s_h, s_i), p_state in weights.items():
                root_signals = {"H0": bool(s_h), "I0": bool(s_i)}
                res = EpistemicPolicyEngine.apply_policy(
                    "lineage_quarantine",
                    pool,
                    root_signals=root_signals,
                    clean_root_id="H0",
                    infected_root_id="I0",
                    signal_state=(s_h, s_i),
                )
                # Clean path survives iff H2 is retained
                h_survives = 1.0 if "H2" in res.retained_node_ids else 0.0
                # Infected path survives iff I2 is retained
                i_survives = 1.0 if "I2" in res.retained_node_ids else 0.0

                c_h += p_state * h_survives
                c_i += p_state * i_survives

            expected_c_h = 1.0 - fpr
            expected_c_i = 1.0 - tpr
            expected_s = tpr - fpr

            assert pytest.approx(c_h, abs=1e-7) == expected_c_h
            assert pytest.approx(c_i, abs=1e-7) == expected_c_i
            assert pytest.approx(c_h - c_i, abs=1e-7) == expected_s


def test_equi_error_rate_null_separation():
    """Verify that when TPR == FPR, lineage separation S is identically zero."""
    pool = [
        PolicyNode(node_id="H0", locus_id="supervisor", generation=0, is_root=True, family_id="clean_fam"),
        PolicyNode(node_id="H1", locus_id="terminal", generation=1, parent_ids=("H0",), family_id="clean_fam"),
        PolicyNode(node_id="I0", locus_id="supervisor", generation=0, is_root=True, family_id="inf_fam", is_infected_allele=True),
        PolicyNode(node_id="I1", locus_id="terminal", generation=1, parent_ids=("I0",), family_id="inf_fam", is_infected_allele=True),
    ]

    for p in [0.1, 0.25, 0.5, 0.8]:
        weights = get_analytic_state_weights(tpr=p, fpr=p)
        c_h = 0.0
        c_i = 0.0

        for (s_h, s_i), p_state in weights.items():
            res = EpistemicPolicyEngine.apply_policy(
                "lineage_quarantine",
                pool,
                root_signals={"H0": bool(s_h), "I0": bool(s_i)},
                clean_root_id="H0",
                infected_root_id="I0",
                signal_state=(s_h, s_i),
            )
            c_h += p_state * (1.0 if "H1" in res.retained_node_ids else 0.0)
            c_i += p_state * (1.0 if "I1" in res.retained_node_ids else 0.0)

        assert pytest.approx(c_h - c_i, abs=1e-9) == 0.0


def test_provenance_laundering_under_node_only_quarantine():
    """Verify that node-only quarantine fails to contain downstream derived memories."""
    # When downstream task requires G1 node (which was derived from root G0)
    pool = [
        PolicyNode(node_id="H0", locus_id="supervisor", generation=0, is_root=True, family_id="clean_fam"),
        PolicyNode(node_id="H1", locus_id="protocol", generation=1, parent_ids=("H0",), family_id="clean_fam"),
        PolicyNode(node_id="I0", locus_id="supervisor", generation=0, is_root=True, family_id="inf_fam", is_infected_allele=True),
        PolicyNode(node_id="I1", locus_id="protocol", generation=1, parent_ids=("I0",), family_id="inf_fam", is_infected_allele=True),
    ]

    # Even with perfect detector TPR=1.0, FPR=0.0:
    weights = get_analytic_state_weights(tpr=1.0, fpr=0.0)

    # Under node_only:
    node_only_ci = 0.0
    for (s_h, s_i), p_state in weights.items():
        res = EpistemicPolicyEngine.apply_policy(
            "node_only_quarantine",
            pool,
            root_signals={"H0": bool(s_h), "I0": bool(s_i)},
            clean_root_id="H0",
            infected_root_id="I0",
            signal_state=(s_h, s_i),
        )
        # I1 survives under node-only because only I0 was dropped!
        node_only_ci += p_state * (1.0 if "I1" in res.retained_node_ids else 0.0)

    # Provenance laundering: I1 is 100% available despite root flag!
    assert node_only_ci == 1.0

    # Under lineage quarantine:
    lineage_ci = 0.0
    for (s_h, s_i), p_state in weights.items():
        res = EpistemicPolicyEngine.apply_policy(
            "lineage_quarantine",
            pool,
            root_signals={"H0": bool(s_h), "I0": bool(s_i)},
            clean_root_id="H0",
            infected_root_id="I0",
            signal_state=(s_h, s_i),
        )
        lineage_ci += p_state * (1.0 if "I1" in res.retained_node_ids else 0.0)

    # Lineage containment: I1 is 100% contained (0.0 leak)
    assert lineage_ci == 0.0


def test_per_state_matched_thinning_counts():
    """Verify that signal_conditioned_uniform_thinning and random_family drop exactly matching counts per state."""
    pool = [
        PolicyNode(node_id="H0", locus_id="supervisor", generation=0, is_root=True, family_id="clean_fam"),
        PolicyNode(node_id="H1", locus_id="protocol", generation=1, parent_ids=("H0",), family_id="clean_fam"),
        PolicyNode(node_id="I0", locus_id="supervisor", generation=0, is_root=True, family_id="inf_fam", is_infected_allele=True),
        PolicyNode(node_id="I1", locus_id="protocol", generation=1, parent_ids=("I0",), family_id="inf_fam", is_infected_allele=True),
    ]

    for s_h in [0, 1]:
        for s_i in [0, 1]:
            sig = {"H0": bool(s_h), "I0": bool(s_i)}
            lin = EpistemicPolicyEngine.apply_policy("lineage_quarantine", pool, sig, "H0", "I0", (s_h, s_i))
            uni = EpistemicPolicyEngine.apply_policy("signal_conditioned_uniform_thinning", pool, sig, "H0", "I0", (s_h, s_i))
            fam = EpistemicPolicyEngine.apply_policy("random_family_quarantine", pool, sig, "H0", "I0", (s_h, s_i))

            assert uni.quarantined_count == lin.quarantined_count
            assert fam.quarantined_count == lin.quarantined_count
            assert uni.retained_count == lin.retained_count
            assert fam.retained_count == lin.retained_count


def test_generation_matched_thinning_g2_parity():
    """Verify that generation_matched_thinning drops exactly matching G2 counts."""
    pool = [
        PolicyNode(node_id="H0", locus_id="supervisor", generation=0, is_root=True, family_id="clean_fam"),
        PolicyNode(node_id="H1", locus_id="protocol", generation=1, parent_ids=("H0",), family_id="clean_fam"),
        PolicyNode(node_id="H2", locus_id="route", generation=2, parent_ids=("H1",), family_id="clean_fam"),
        PolicyNode(node_id="I0", locus_id="supervisor", generation=0, is_root=True, family_id="inf_fam", is_infected_allele=True),
        PolicyNode(node_id="I1", locus_id="protocol", generation=1, parent_ids=("I0",), family_id="inf_fam", is_infected_allele=True),
        PolicyNode(node_id="I2", locus_id="route", generation=2, parent_ids=("I1",), family_id="inf_fam", is_infected_allele=True),
    ]

    for s_h in [0, 1]:
        for s_i in [0, 1]:
            sig = {"H0": bool(s_h), "I0": bool(s_i)}
            lin = EpistemicPolicyEngine.apply_policy("lineage_quarantine", pool, sig, "H0", "I0", (s_h, s_i))
            g2_lin_count = sum(1 for nid in lin.quarantined_node_ids if nid in ("H2", "I2"))
            
            gen_match = EpistemicPolicyEngine.apply_policy("generation_matched_thinning", pool, sig, "H0", "I0", (s_h, s_i))
            assert gen_match.quarantined_count == g2_lin_count


def test_signal_blind_uniform_thinning_fixed_budget():
    """Verify signal_blind_uniform_thinning drops fixed budget regardless of signal state."""
    pool = [
        PolicyNode(node_id=f"N{i}", locus_id=f"loc{i}", generation=0)
        for i in range(10)
    ]

    for s_h in [0, 1]:
        for s_i in [0, 1]:
            sig = {"N0": bool(s_h), "N1": bool(s_i)}
            res = EpistemicPolicyEngine.apply_policy(
                "signal_blind_uniform_thinning",
                pool,
                sig,
                "N0",
                "N1",
                (s_h, s_i),
                fixed_thinning_budget=3,
            )
            assert res.quarantined_count == 3
            assert res.retained_count == 7


def test_four_state_policy_audit_ledger():
    """Produce explicit, machine-verifiable 4-state audit ledger across all 7 policies."""
    # Setup G0 -> G1 -> G2 trees for H and I
    nodes = [
        PolicyNode(node_id="H0", locus_id="supervisor", generation=0, is_root=True, family_id="H"),
        PolicyNode(node_id="H1", locus_id="protocol", generation=1, parent_ids=("H0",), family_id="H"),
        PolicyNode(node_id="H2", locus_id="route", generation=2, parent_ids=("H1",), family_id="H"),
        PolicyNode(node_id="I0", locus_id="supervisor", generation=0, is_root=True, family_id="I", is_infected_allele=True),
        PolicyNode(node_id="I1", locus_id="protocol", generation=1, parent_ids=("I0",), family_id="I", is_infected_allele=True),
        PolicyNode(node_id="I2", locus_id="route", generation=2, parent_ids=("I1",), family_id="I", is_infected_allele=True),
        PolicyNode(node_id="C0", locus_id="grid", generation=0, family_id="C"),
        PolicyNode(node_id="C1", locus_id="beacon", generation=0, family_id="C"),
    ]

    policies = [
        "baseline",
        "signal_blind_uniform_thinning",
        "signal_conditioned_uniform_thinning",
        "generation_matched_thinning",
        "random_family_quarantine",
        "node_only_quarantine",
        "lineage_quarantine",
        "oracle_upper_bound",
    ]

    audit_ledger = []
    for policy in policies:
        for s_h, s_i in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            sig = {"H0": bool(s_h), "I0": bool(s_i)}
            res = EpistemicPolicyEngine.apply_policy(policy, nodes, sig, "H0", "I0", (s_h, s_i), seed=42)
            
            h_avail = 1.0 if "H2" in res.retained_node_ids and "C0" in res.retained_node_ids else 0.0
            i_avail = 1.0 if "I2" in res.retained_node_ids and "C0" in res.retained_node_ids else 0.0

            audit_ledger.append({
                "policy": policy,
                "state": (s_h, s_i),
                "retained_count": res.retained_count,
                "quarantined_count": res.quarantined_count,
                "quarantined_ids": sorted(list(res.quarantined_node_ids)),
                "h_g2_survives": "H2" in res.retained_node_ids,
                "i_g2_survives": "I2" in res.retained_node_ids,
                "h_avail": h_avail,
                "i_avail": i_avail,
            })

    # Assert basic consistency across all audit entries
    assert len(audit_ledger) == len(policies) * 4
    # Baseline always has 0 quarantined
    assert all(entry["quarantined_count"] == 0 for entry in audit_ledger if entry["policy"] == "baseline")
    # In state (0, 0), lineage quarantine drops 0 nodes
    lin_00 = [e for e in audit_ledger if e["policy"] == "lineage_quarantine" and e["state"] == (0, 0)][0]
    assert lin_00["quarantined_count"] == 0
    # In state (0, 1), lineage quarantine drops I0, I1, I2
    lin_01 = [e for e in audit_ledger if e["policy"] == "lineage_quarantine" and e["state"] == (0, 1)][0]
    assert lin_01["quarantined_ids"] == ["I0", "I1", "I2"]
    assert lin_01["h_avail"] == 1.0
    assert lin_01["i_avail"] == 0.0
