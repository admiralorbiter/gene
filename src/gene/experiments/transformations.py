"""Semantic Transformations for Epistemic Invariance & Conformance Testing (v2).

Transforms underlying data structures first, then renders natural language second.
"""

from __future__ import annotations

import copy
import itertools
from typing import Any
from gene.experiments.epistemic_ir import (
    EpistemicState,
    PremiseNode,
    QueryContract,
    RuleSpec,
    SupportEnvironment,
)
from gene.experiments.epistemic_renderer import EpistemicRenderer


class PermutationTransform:
    """Generates orderings of active premise occurrences."""

    @staticmethod
    def generate_all_permutations(state: EpistemicState) -> list[list[str]]:
        active_ids = list(state.get_active_premises().keys())
        return [list(p) for p in itertools.permutations(active_ids)]

    @staticmethod
    def generate_canonical_and_reverse(state: EpistemicState) -> list[list[str]]:
        active_ids = sorted(list(state.get_active_premises().keys()))
        return [active_ids, list(reversed(active_ids))]


class RoleEquivarianceTransform:
    """Transforms roles, entities, and tokens structurally while preserving formal derivation topology."""

    @staticmethod
    def swap_role_slots(
        state: EpistemicState, query: QueryContract, role_a: str, role_b: str
    ) -> tuple[EpistemicState, QueryContract]:
        """Swap two role definitions across PremiseNodes and RuleSpecs structurally, then re-render."""
        new_state = copy.deepcopy(state)
        new_query = copy.deepcopy(query)

        # 1. Swap roles on PremiseNodes
        for p in new_state.premises.values():
            if p.role == role_a:
                p.role = role_b
                p.semantic_claim_id = p.semantic_claim_id.replace(role_a, "__TEMP__")
            elif p.role == role_b:
                p.role = role_a
                p.semantic_claim_id = p.semantic_claim_id.replace(role_b, role_a)

        for p in new_state.premises.values():
            p.semantic_claim_id = p.semantic_claim_id.replace("__TEMP__", role_b)

        # 2. Swap rule antecedent predicates
        for r in new_state.rules.values():
            new_ants = []
            for ant in r.antecedent_predicates:
                if role_a in ant:
                    new_ants.append(ant.replace(role_a, role_b))
                elif role_b in ant:
                    new_ants.append(ant.replace(role_b, role_a))
                else:
                    new_ants.append(ant)
            r.antecedent_predicates = new_ants

        # 3. Swap required claim IDs in support environments
        for env in new_state.support_environments:
            new_reqs = []
            for cid in env.required_semantic_claim_ids:
                if role_a in cid:
                    new_reqs.append(cid.replace(role_a, role_b))
                elif role_b in cid:
                    new_reqs.append(cid.replace(role_b, role_a))
                else:
                    new_reqs.append(cid)
            env.required_semantic_claim_ids = new_reqs

        # 4. Re-render all texts deterministically
        EpistemicRenderer.render_state(new_state)
        return new_state, new_query

    @staticmethod
    def anonymize_roles(
        state: EpistemicState, query: QueryContract, mapping: dict[str, str]
    ) -> tuple[EpistemicState, QueryContract]:
        """Replace natural-language roles with synthetic opaque tokens structurally, then re-render."""
        new_state = copy.deepcopy(state)
        new_query = copy.deepcopy(query)

        for p in new_state.premises.values():
            for orig, opaque in mapping.items():
                if p.role == orig:
                    p.role = opaque
                    p.semantic_claim_id = p.semantic_claim_id.replace(orig, opaque)

        for r in new_state.rules.values():
            new_ants = []
            for ant in r.antecedent_predicates:
                for orig, opaque in mapping.items():
                    ant = ant.replace(orig, opaque)
                new_ants.append(ant)
            r.antecedent_predicates = new_ants
            if "rule_manager_s1" in r.rule_id:
                r.rule_id = "rule_opaque_q7_s1"
            elif "rule_sector_lead_s2" in r.rule_id:
                r.rule_id = "rule_opaque_m2_s2"

        for env in new_state.support_environments:
            new_reqs = []
            for cid in env.required_semantic_claim_ids:
                for orig, opaque in mapping.items():
                    cid = cid.replace(orig, opaque)
                new_reqs.append(cid)
            env.required_semantic_claim_ids = new_reqs

        EpistemicRenderer.render_state(new_state)
        return new_state, new_query

    @staticmethod
    def rotate_station_entity(
        state: EpistemicState, query: QueryContract, from_st: str, to_st: str
    ) -> tuple[EpistemicState, QueryContract]:
        """Rotate station entity across PremiseNodes, QueryContract, and re-render."""
        new_state = copy.deepcopy(state)
        new_query = copy.deepcopy(query)

        new_query.target_station = to_st
        new_query.query_question = new_query.query_question.replace(from_st, to_st)

        for p in new_state.premises.values():
            if p.entity == from_st:
                p.entity = to_st
                p.semantic_claim_id = p.semantic_claim_id.replace(from_st, to_st)

        for env in new_state.support_environments:
            env.required_semantic_claim_ids = [
                cid.replace(from_st, to_st) for cid in env.required_semantic_claim_ids
            ]

        EpistemicRenderer.render_state(new_state)
        return new_state, new_query


class SupportAugmentationTransform:
    """Constructs minimal support baselines and adds valid, non-contradictory premise augments."""

    @staticmethod
    def generate_augmentation_chain(
        state: EpistemicState,
        base_support_path_id: str,
        augment_occurrence_ids: list[str],
    ) -> list[tuple[list[str], str]]:
        """Generates a sequence of occurrence ID subsets [Base] -> [Base + A1] -> [Base + A1 + A2] ...
        
        Returns list of (active_occurrence_ids, stage_description).
        """
        base_env = next((e for e in state.support_environments if e.path_id == base_support_path_id), None)
        if not base_env:
            raise ValueError(f"Base support path {base_support_path_id} not found in EpistemicState")

        # Find occurrences satisfying the base required semantic claims
        base_occs = []
        for cid in base_env.required_semantic_claim_ids:
            matching = [p.occurrence_id for p in state.premises.values() if p.semantic_claim_id == cid]
            if not matching:
                raise ValueError(f"Required semantic claim {cid} has no matching premise occurrence in state")
            base_occs.append(matching[0])

        chain = []
        current_active = list(base_occs)
        chain.append((list(current_active), f"Minimal Support [{base_support_path_id}]"))

        for aug_id in augment_occurrence_ids:
            if aug_id not in current_active and aug_id in state.premises:
                current_active.append(aug_id)
                p = state.premises[aug_id]
                chain.append((list(current_active), f"Augment +{aug_id} ({p.rendered_text})"))

        return chain
