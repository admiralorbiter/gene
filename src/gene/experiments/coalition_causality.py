"""Track H: Coalition Causality & Overdetermination Engine.

Implements intervention lattices over parent subsets, evaluates minimal causally sufficient
support environments S_C(c), and contrasts single-parent vs coalition knockouts against formal support S_F(c).
"""

from __future__ import annotations

import itertools
from typing import Any
from pydantic import BaseModel, Field


class CoalitionInterventionResult(BaseModel):
    """Result of an intervention on a subset of parent premises."""
    geometry: str
    target_claim: str
    all_parents: list[str]
    knocked_out_parents: list[str]
    active_parents: list[str]
    formal_support_survives: bool
    expected_claim: str
    surviving_formal_paths: list[list[str]] = Field(default_factory=list)


class CoalitionCausalityEngine:
    """Evaluates formal support closure across the power set of parent interventions."""

    def __init__(self):
        # Formal minimal support sets for canonical recombinant geometry
        self.geometries = {
            "redundant_independent": {
                "paths": [["A", "B"], ["D", "E"]],
                "parents": ["A", "B", "D", "E"],
                "target": "PROTO_X7",
            },
        }

    def evaluate_intervention(
        self, geometry: str, knocked_out: set[str]
    ) -> CoalitionInterventionResult:
        if geometry not in self.geometries:
            raise ValueError(f"Unknown geometry: {geometry}")

        geom_data = self.geometries[geometry]
        all_parents = geom_data["parents"]
        target = geom_data["target"]
        paths = geom_data["paths"]

        active_parents = [p for p in all_parents if p not in knocked_out]
        surviving_paths = []

        for p in paths:
            if all(node in active_parents for node in p):
                surviving_paths.append(p)

        formal_survives = len(surviving_paths) > 0
        expected = target if formal_survives else "UNKNOWN"

        return CoalitionInterventionResult(
            geometry=geometry,
            target_claim=target,
            all_parents=all_parents,
            knocked_out_parents=sorted(list(knocked_out)),
            active_parents=active_parents,
            formal_support_survives=formal_survives,
            expected_claim=expected,
            surviving_formal_paths=surviving_paths,
        )

    def extract_minimal_causal_coalitions(
        self, geometry: str, behavioral_results: dict[tuple[str, ...], str]
    ) -> list[set[str]]:
        """Extract minimal parent sets whose simultaneous presence sustains the target claim.
        
        behavioral_results maps knocked_out_tuple -> emitted_claim.
        """
        geom_data = self.geometries[geometry]
        target = geom_data["target"]
        all_parents = set(geom_data["parents"])

        sufficient_active_sets = []
        for knocked_out_tuple, emitted in behavioral_results.items():
            if emitted == target:
                active = all_parents - set(knocked_out_tuple)
                sufficient_active_sets.append(active)

        # Minimize to irredundant sets
        minimal_coalitions: list[set[str]] = []
        for s in sorted(sufficient_active_sets, key=len):
            if not any(existing.issubset(s) for existing in minimal_coalitions):
                minimal_coalitions.append(s)

        return minimal_coalitions
