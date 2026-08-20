"""Semantic Transformations for Epistemic Invariance & Conformance Testing.

Provides exact generators for:
1. Permutations (pi in Pi) -> Permutation Invariance
2. Role & Entity Equivariance (rho in P) -> Role/Entity Equivariance
3. Support-Preserving Augmentations (tau in T) -> Semantic Monotonicity
"""

from __future__ import annotations

import copy
import itertools
from typing import Any
from gene.experiments.epistemic_ir import EpistemicIR, PremiseNode, SupportEnvironment


class PermutationTransform:
    """Generates orderings of active premises."""

    @staticmethod
    def generate_all_permutations(ir: EpistemicIR) -> list[list[str]]:
        active_ids = list(ir.get_active_premises().keys())
        return [list(p) for p in itertools.permutations(active_ids)]

    @staticmethod
    def generate_canonical_and_reverse(ir: EpistemicIR) -> list[list[str]]:
        active_ids = sorted(list(ir.get_active_premises().keys()))
        return [active_ids, list(reversed(active_ids))]


class RoleEquivarianceTransform:
    """Transforms roles, entities, and tokens while strictly preserving underlying support topology."""

    @staticmethod
    def swap_role_slots(ir: EpistemicIR, role_a: str, role_b: str) -> EpistemicIR:
        """Swap two role definitions across all premise nodes."""
        new_ir = copy.deepcopy(ir)
        text_a = role_a.replace("_", " ")
        text_b = role_b.replace("_", " ")

        for pid, p in new_ir.premises.items():
            if p.role == role_a:
                p.role = role_b
                p.text = p.text.replace(role_a, "__TEMP_SWAP__").replace(text_a, "__TEMP_SWAP_TEXT__")
            elif p.role == role_b:
                p.role = role_a
                p.text = p.text.replace(role_b, role_a).replace(text_b, text_a)
        
        for pid, p in new_ir.premises.items():
            p.text = p.text.replace("__TEMP_SWAP__", role_b).replace("__TEMP_SWAP_TEXT__", text_b)
        return new_ir

    @staticmethod
    def anonymize_roles(ir: EpistemicIR, mapping: dict[str, str]) -> EpistemicIR:
        """Replace descriptive semantic roles (e.g. 'manager', 'sector_lead') with synthetic opaque tokens."""
        new_ir = copy.deepcopy(ir)
        for pid, p in new_ir.premises.items():
            for orig, opaque in mapping.items():
                orig_text = orig.replace("_", " ")
                if p.role == orig:
                    p.role = opaque
                p.text = p.text.replace(orig, opaque).replace(orig_text, opaque)
        return new_ir

    @staticmethod
    def rotate_station_entity(ir: EpistemicIR, from_st: str, to_st: str) -> EpistemicIR:
        """Rotate target and premise station entities."""
        new_ir = copy.deepcopy(ir)
        new_ir.target_station = to_st
        new_ir.query_question = new_ir.query_question.replace(from_st, to_st)
        for pid, p in new_ir.premises.items():
            if p.subject == from_st:
                p.subject = to_st
            p.text = p.text.replace(from_st, to_st)
        return new_ir


class SupportAugmentationTransform:
    """Constructs minimal support baselines and adds valid, non-contradictory premise augments."""

    @staticmethod
    def generate_augmentation_chain(
        ir: EpistemicIR,
        base_support_path_id: str,
        augment_premise_ids: list[str],
    ) -> list[tuple[list[str], str]]:
        """Generates a sequence of premise subsets [Base] -> [Base + A1] -> [Base + A1 + A2] ...
        
        Returns list of (active_premise_ids, stage_description).
        """
        base_env = next((e for e in ir.support_environments if e.path_id == base_support_path_id), None)
        if not base_env:
            raise ValueError(f"Base support path {base_support_path_id} not found in IR")

        chain = []
        current_active = list(base_env.required_premise_ids)
        chain.append((list(current_active), f"Minimal Support [{base_support_path_id}]"))

        for aug_id in augment_premise_ids:
            if aug_id not in current_active and aug_id in ir.premises:
                current_active.append(aug_id)
                chain.append((list(current_active), f"Augment +{aug_id} ({ir.premises[aug_id].text})"))

        return chain
