"""Galton-Watson Branching Process Simulator and Analytical Engine for Experiment 1B-A2.

Models multi-generational stochastic family-tree dynamics under offspring distribution:
    K ~ Binomial(b, p)
where:
    b = branching factor per parent (default: 2)
    p = retrieval contact probability
    tau = epistemic transmissibility (assumed 1.0)
    W = write admission rate (assumed 1.0)

Key Theoretical Quantities:
    Mean offspring: mu = b * p
    PGF: G(s) = ((1 - p) + p * s)^b
    Finite-generation extinction: q_g = G(q_{g-1}), q_0 = 0
    Ultimate extinction: q_inf = 1.0 if p <= 0.5 else ((1 - p) / p)^b
    Surviving mean: E[Z_g | Z_g > 0] = mu^g / (1 - q_g)
    Jackpot fraction: P(Z_g = b^g) = (p^b)^((b^g - 1)/(b - 1))
"""

from __future__ import annotations

import math
import random
from typing import Any, Literal
from pydantic import BaseModel, Field


class BranchingGenerationSummary(BaseModel):
    """Metrics for a specific generation g in the branching process."""
    generation: int
    theoretical_extinction_q: float
    empirical_extinction_q: float
    theoretical_mean_population: float
    empirical_mean_population: float
    empirical_surviving_mean_population: float
    theoretical_jackpot_fraction: float
    empirical_jackpot_fraction: float
    population_histogram: dict[int, int] = Field(default_factory=dict)


class BranchingDoseSummary(BaseModel):
    """Complete summary of branching simulation and analytical solutions across generations at dose p."""
    exposure_p: float
    branching_factor_b: int
    mean_offspring_mu: float
    regime: Literal["subcritical", "critical", "supercritical"]
    ultimate_extinction_q_inf: float
    generations: list[BranchingGenerationSummary]


class GaltonWatsonSimulator:
    """Analytical engine and Monte Carlo simulator for Galton-Watson branching processes."""

    def __init__(self, branching_factor_b: int = 2):
        self.b = branching_factor_b

    def pgf(self, s: float, p: float) -> float:
        """Evaluate probability generating function G(s) = ((1-p) + p*s)^b."""
        return ((1.0 - p) + p * s) ** self.b

    def analytical_extinction_curve(self, p: float, max_gen: int = 4) -> list[float]:
        """Compute exact finite-generation extinction probabilities [q_1, ..., q_max_gen]."""
        curve: list[float] = []
        q = 0.0
        for _ in range(max_gen):
            q = self.pgf(q, p)
            curve.append(q)
        return curve

    def ultimate_extinction_prob(self, p: float) -> float:
        """Compute asymptotic ultimate extinction probability q_inf."""
        mu = self.b * p
        if mu <= 1.0:
            return 1.0
        if self.b == 2:
            return ((1.0 - p) / p) ** 2
        # Numerical fixed-point iteration for arbitrary b
        s = 0.0
        for _ in range(1000):
            s_next = self.pgf(s, p)
            if abs(s_next - s) < 1e-9:
                return s_next
            s = s_next
        return s

    def theoretical_jackpot_fraction(self, p: float, generation: int) -> float:
        """Compute theoretical fraction of trees reaching maximal capacity b^g (all branches surviving)."""
        if generation == 0:
            return 1.0
        if self.b == 1:
            total_parents = generation
        else:
            total_parents = (self.b ** generation - 1) // (self.b - 1)
        return (p ** self.b) ** total_parents

    def simulate_dose(
        self,
        p: float,
        max_gen: int = 4,
        num_trials: int = 10000,
        seed: int = 42,
    ) -> BranchingDoseSummary:
        """Run Monte Carlo simulation of family-tree trajectories and compare with analytical truth."""
        rng = random.Random(seed)
        mu = self.b * p
        if abs(mu - 1.0) < 1e-5:
            regime: Literal["subcritical", "critical", "supercritical"] = "critical"
        elif mu < 1.0:
            regime = "subcritical"
        else:
            regime = "supercritical"

        q_inf = self.ultimate_extinction_prob(p)
        analytical_qs = self.analytical_extinction_curve(p, max_gen=max_gen)

        # Track population per trial per generation: trajectories[trial_idx] = [Z_0, Z_1, ..., Z_max_gen]
        trajectories: list[list[int]] = []

        for _ in range(num_trials):
            traj = [1]  # Z_0 = 1
            z = 1
            for g in range(1, max_gen + 1):
                if z == 0:
                    traj.append(0)
                else:
                    # Each of z parents produces Binomial(b, p) offspring
                    offspring = sum(
                        1 for _ in range(z * self.b) if rng.random() < p
                    )
                    z = offspring
                    traj.append(z)
            trajectories.append(traj)

        gen_summaries: list[BranchingGenerationSummary] = []

        for g in range(1, max_gen + 1):
            populations = [traj[g] for traj in trajectories]
            num_extinct = sum(1 for z in populations if z == 0)
            emp_q = num_extinct / num_trials

            emp_mean = sum(populations) / num_trials
            theo_mean = mu ** g

            surviving = [z for z in populations if z > 0]
            emp_surviving_mean = (sum(surviving) / len(surviving)) if surviving else 0.0

            max_possible_pop = self.b ** g
            num_jackpots = sum(1 for z in populations if z == max_possible_pop)
            emp_jackpot = num_jackpots / num_trials
            theo_jackpot = self.theoretical_jackpot_fraction(p, g)

            # Histogram
            hist: dict[int, int] = {}
            for z in populations:
                hist[z] = hist.get(z, 0) + 1

            gen_summaries.append(
                BranchingGenerationSummary(
                    generation=g,
                    theoretical_extinction_q=analytical_qs[g - 1],
                    empirical_extinction_q=emp_q,
                    theoretical_mean_population=theo_mean,
                    empirical_mean_population=emp_mean,
                    empirical_surviving_mean_population=emp_surviving_mean,
                    theoretical_jackpot_fraction=theo_jackpot,
                    empirical_jackpot_fraction=emp_jackpot,
                    population_histogram=dict(sorted(hist.items())),
                )
            )

        return BranchingDoseSummary(
            exposure_p=p,
            branching_factor_b=self.b,
            mean_offspring_mu=mu,
            regime=regime,
            ultimate_extinction_q_inf=q_inf,
            generations=gen_summaries,
        )

