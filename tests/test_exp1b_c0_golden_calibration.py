"""Unit and golden calibration tests for Experiment 1B-C0.

Verifies closed-form algebraic invariants and analytical state weighting
for the epistemic immunity policy engine.
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
    """Verify that uniform_thinning and random_family drop exactly matching counts per state."""
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
            uni = EpistemicPolicyEngine.apply_policy("uniform_thinning", pool, sig, "H0", "I0", (s_h, s_i))
            fam = EpistemicPolicyEngine.apply_policy("random_family_quarantine", pool, sig, "H0", "I0", (s_h, s_i))

            assert uni.quarantined_count == lin.quarantined_count
            assert fam.quarantined_count == lin.quarantined_count
            assert uni.retained_count == lin.retained_count
            assert fam.retained_count == lin.retained_count
