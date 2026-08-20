"""Deterministic Invariant and Statistical Convergence Tests for Experiment 1B-A2 Branching Simulator."""

import math
import pytest
from gene.simulation.branching import GaltonWatsonSimulator


def test_analytical_extinction_probabilities_exact_values():
    """Verify that analytical PGF recursions match exact closed-form algebraic solutions."""
    sim = GaltonWatsonSimulator(branching_factor_b=2)

    # 1. Critical boundary p = 0.50
    # G(s) = (0.5 + 0.5s)^2
    # q_1 = G(0) = 0.25
    # q_2 = G(0.25) = (0.5 + 0.125)^2 = 0.625^2 = 0.390625
    # q_3 = G(0.390625) = (0.5 + 0.1953125)^2 = 0.6953125^2 = 0.48345947265625
    qs_p50 = sim.analytical_extinction_curve(p=0.50, max_gen=3)
    assert abs(qs_p50[0] - 0.25) < 1e-9
    assert abs(qs_p50[1] - 0.390625) < 1e-9
    assert abs(qs_p50[2] - 0.48345947265625) < 1e-9
    assert sim.ultimate_extinction_prob(0.50) == 1.0

    # 2. Supercritical near replacement p = 0.60
    # G(s) = (0.4 + 0.6s)^2
    # q_1 = 0.4^2 = 0.16
    # q_2 = (0.4 + 0.6 * 0.16)^2 = 0.496^2 = 0.246016
    # q_inf = (0.4 / 0.6)^2 = (2/3)^2 = 4/9 ~ 0.444444...
    qs_p60 = sim.analytical_extinction_curve(p=0.60, max_gen=2)
    assert abs(qs_p60[0] - 0.16) < 1e-9
    assert abs(qs_p60[1] - 0.246016) < 1e-9
    assert abs(sim.ultimate_extinction_prob(0.60) - (4.0 / 9.0)) < 1e-9

    # 3. Supercritical p = 0.75
    # q_inf = (0.25 / 0.75)^2 = (1/3)^2 = 1/9 ~ 0.111111...
    assert abs(sim.ultimate_extinction_prob(0.75) - (1.0 / 9.0)) < 1e-9

    # 4. Deterministic p = 1.00
    assert sim.ultimate_extinction_prob(1.00) == 0.0


def test_monte_carlo_convergence_within_three_sigma():
    """Verify that Monte Carlo empirical extinction probabilities converge to analytical truth within 3-sigma."""
    sim = GaltonWatsonSimulator(branching_factor_b=2)
    num_trials = 25000
    p = 0.60
    summary = sim.simulate_dose(p=p, max_gen=4, num_trials=num_trials, seed=1337)

    assert summary.regime == "supercritical"
    assert abs(summary.mean_offspring_mu - 1.20) < 1e-9
    assert abs(summary.ultimate_extinction_q_inf - (4.0 / 9.0)) < 1e-9

    for gen_sum in summary.generations:
        q_theo = gen_sum.theoretical_extinction_q
        q_emp = gen_sum.empirical_extinction_q

        # 3-sigma confidence interval for Binomial(N, q_theo)
        sigma = math.sqrt((q_theo * (1.0 - q_theo)) / num_trials)
        assert abs(q_emp - q_theo) <= 3.0 * sigma, f"Gen {gen_sum.generation}: empirical {q_emp} deviates from theoretical {q_theo} by >3 sigma"

        # Mean population convergence
        mu_theo = gen_sum.theoretical_mean_population
        mu_emp = gen_sum.empirical_mean_population
        # Check relative mean error is small (< 5%)
        assert abs(mu_emp - mu_theo) / mu_theo < 0.05, f"Gen {gen_sum.generation}: empirical mean {mu_emp} deviates from theoretical {mu_theo}"


def test_critical_boundary_martingale_and_extinction_properties():
    """Verify that at p = 0.50, mean population is conserved (E[Z_g] == 1.0) while extinction steadily climbs toward 1.0."""
    sim = GaltonWatsonSimulator(branching_factor_b=2)
    num_trials = 20000
    summary = sim.simulate_dose(p=0.50, max_gen=4, num_trials=num_trials, seed=42)

    assert summary.regime == "critical"
    assert summary.ultimate_extinction_q_inf == 1.0

    prev_q = 0.0
    for gen_sum in summary.generations:
        # Extinction strictly increases with generation
        assert gen_sum.empirical_extinction_q > prev_q
        prev_q = gen_sum.empirical_extinction_q

        # Martingale property: E[Z_g] = 1.0 for all g
        assert abs(gen_sum.theoretical_mean_population - 1.0) < 1e-9
        assert abs(gen_sum.empirical_mean_population - 1.0) < 0.05

        # Surviving mean conditional on non-extinction MUST grow: E[Z_g | Z_g > 0] = 1 / (1 - q_g)
        expected_surviving_mean = 1.0 / (1.0 - gen_sum.theoretical_extinction_q)
        assert abs(gen_sum.empirical_surviving_mean_population - expected_surviving_mean) < 0.15


def test_jackpot_scaling_at_high_exposure():
    """Verify that theoretical and empirical jackpot probabilities match across generations."""
    sim = GaltonWatsonSimulator(branching_factor_b=2)
    p = 0.75
    num_trials = 20000
    summary = sim.simulate_dose(p=p, max_gen=3, num_trials=num_trials, seed=999)

    # At G1: jackpot pop = 2. P(both survive) = p^2 = 0.75^2 = 0.5625
    g1 = summary.generations[0]
    assert abs(g1.theoretical_jackpot_fraction - 0.5625) < 1e-9
    assert abs(g1.empirical_jackpot_fraction - 0.5625) < 0.015

    # At G2: jackpot pop = 4. P(all 4 survive) = (p^2)^1 * (p^2)^2 = (0.5625)^3 = 0.177978515625
    g2 = summary.generations[1]
    assert abs(g2.theoretical_jackpot_fraction - 0.177978515625) < 1e-9
    assert abs(g2.empirical_jackpot_fraction - 0.177978515625) < 0.015

