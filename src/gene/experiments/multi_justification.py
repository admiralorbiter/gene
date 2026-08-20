"""Track G: Multi-Justification & Epistemic Recombination Engine.

Implements minimal support set algebra S(c), ancestor invalidation, non-destructive
survival evaluation, and epistemic cut set calculations kappa(c).
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class MinimalSupportEngine:
    """Deterministic belief maintenance engine over minimal support sets S(c)."""

    def __init__(self) -> None:
        # claim_id -> set of frozenset of premise strings
        self._support_sets: dict[str, set[frozenset[str]]] = {}
        # set of invalidated / discredited ancestor premises
        self._invalidated_ancestors: set[str] = set()

    def add_support_set(self, claim: str, premises: set[str] | list[str]) -> None:
        """Register a minimal sufficient conjunctive premise set for claim."""
        if not premises:
            raise ValueError("Support set cannot be empty.")
        if claim not in self._support_sets:
            self._support_sets[claim] = set()
        self._support_sets[claim].add(frozenset(premises))

    def support_sets(self, claim: str) -> set[frozenset[str]]:
        """Return all registered minimal support sets for claim."""
        return self._support_sets.get(claim, set())

    def active_support_sets(self, claim: str) -> set[frozenset[str]]:
        """Return support sets for claim that contain NO invalidated ancestors."""
        all_sets = self.support_sets(claim)
        active = set()
        for s in all_sets:
            if not (s & self._invalidated_ancestors):
                active.add(s)
        return active

    def invalidate_ancestor(self, ancestor: str) -> set[str]:
        """Discredit an ancestor premise and return set of claims whose active support changed."""
        self._invalidated_ancestors.add(ancestor)
        affected_claims = set()
        for claim, s_sets in self._support_sets.items():
            for s in s_sets:
                if ancestor in s:
                    affected_claims.add(claim)
                    break
        return affected_claims

    def restore_ancestor(self, ancestor: str) -> None:
        """Restore validity of an ancestor premise."""
        self._invalidated_ancestors.discard(ancestor)

    def claim_survives(self, claim: str) -> bool:
        """Check if claim possesses at least one valid, un-invalidated support set."""
        return len(self.active_support_sets(claim)) > 0

    def minimal_cut_sets(self, claim: str) -> set[frozenset[str]]:
        """Compute minimal hitting sets of ancestors whose invalidation destroys all support sets."""
        active_sets = self.active_support_sets(claim)
        if not active_sets:
            return {frozenset()}

        # Find all distinct ancestors across active support sets
        all_ancestors = sorted(list(set().union(*active_sets)))
        min_cuts: list[set[str]] = []

        # Enumerate hitting sets by increasing size
        import itertools
        for r in range(1, len(all_ancestors) + 1):
            found_at_this_size = False
            for combo in itertools.combinations(all_ancestors, r):
                combo_set = set(combo)
                # Check if combo hits every active support set
                if all(bool(s & combo_set) for s in active_sets):
                    # Check irredundancy (no strict subset is already a valid cut)
                    if not any(prior.issubset(combo_set) for prior in min_cuts):
                        min_cuts.append(combo_set)
                        found_at_this_size = True
            if found_at_this_size:
                # We found minimal cuts of size r
                pass

        return {frozenset(c) for c in min_cuts}

    def epistemic_resilience(self, claim: str) -> int:
        """Compute kappa(c): size of the smallest ancestral cut that eliminates all valid support."""
        cuts = self.minimal_cut_sets(claim)
        if not cuts or frozenset() in cuts:
            return 0
        return min(len(c) for c in cuts)
