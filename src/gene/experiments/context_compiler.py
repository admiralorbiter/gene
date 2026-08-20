"""Epistemic Context Compiler (v3).

Compiles an EpistemicState into a CompiledContext with complete pass-level provenance,
state vs typed equivalence hashing, full-pass provenance conservation, and backend-neutral evidence tagging.
"""

from __future__ import annotations

import hashlib
from typing import Any
from pydantic import BaseModel, Field
from gene.experiments.epistemic_ir import (
    EpistemicState,
    PremiseNode,
    PrivilegeLevel,
    ProvenanceStatus,
    QueryContract,
    RuleSpec,
)


class CompiledContext(BaseModel):
    """Result of context compilation carrying full provenance and audit metadata."""
    prompt: str
    state_hash: str
    equiv_hash: str
    source_occurrence_ids: list[str]
    emitted_occurrence_ids: list[str]
    included_semantic_claim_ids: list[str]
    represented_root_ids: list[str]
    surviving_support_environment_ids: list[str]
    evidence_tag_to_claim_map: dict[str, str] = Field(default_factory=dict)
    merged_occurrence_groups: dict[str, list[str]] = Field(default_factory=dict)
    dropped_occurrence_ids: list[str] = Field(default_factory=list)
    drop_or_merge_reasons: dict[str, str] = Field(default_factory=dict)
    compiler_passes: list[str]
    privilege_level: PrivilegeLevel
    equivalence_class_id: str

    def verify_provenance_conservation(self) -> bool:
        """Verify the conservation invariant across ALL input occurrences:
        source = emitted (+) merged_non_primaries (+) dropped.
        """
        emitted_set = set(self.emitted_occurrence_ids)
        merged_non_primaries = set()
        for primary, group in self.merged_occurrence_groups.items():
            for occ in group:
                if occ != primary:
                    merged_non_primaries.add(occ)
        dropped_set = set(self.dropped_occurrence_ids)

        all_accounted = emitted_set | merged_non_primaries | dropped_set
        source_set = set(self.source_occurrence_ids)

        has_no_overlap = len(emitted_set & merged_non_primaries) == 0 and len(emitted_set & dropped_set) == 0 and len(merged_non_primaries & dropped_set) == 0
        covers_all = (all_accounted == source_set)
        return has_no_overlap and covers_all


class EpistemicContextCompiler:
    """Compiles machine-readable EpistemicState into neural prompts with explicit passes."""

    def __init__(self, pipeline: PrivilegeLevel = PrivilegeLevel.RAW_SERIALIZATION):
        self.pipeline = pipeline

    def compile(
        self,
        state: EpistemicState,
        query: QueryContract,
        occurrence_order: list[str] | None = None,
        equivalence_class_id: str = "default",
    ) -> CompiledContext:
        """Execute the compilation pipeline and return a CompiledContext."""
        state_h = state.compute_state_hash()
        equiv_h = state.compute_permutation_equiv_hash()
        
        all_input_occ_ids = sorted(list(state.premises.keys()))
        
        # Pass 1: Validity Filter
        dropped_by_validity = []
        validity_drop_reasons = {}
        active_premises = {}
        for occ_id, p in state.premises.items():
            if not p.is_valid:
                dropped_by_validity.append(occ_id)
                validity_drop_reasons[occ_id] = "dropped_by_validity_filter:is_valid_false"
            elif any(r in state.invalidated_roots for r in p.root_ids):
                dropped_by_validity.append(occ_id)
                inv_roots = [r for r in p.root_ids if r in state.invalidated_roots]
                validity_drop_reasons[occ_id] = f"dropped_by_validity_filter:invalidated_root_{'+'.join(inv_roots)}"
            else:
                active_premises[occ_id] = p

        surviving_envs = state.get_surviving_support_environments()

        if occurrence_order is not None:
            ordered_occ_ids = [occ_id for occ_id in occurrence_order if occ_id in active_premises]
        else:
            ordered_occ_ids = sorted(list(active_premises.keys()))

        if self.pipeline == PrivilegeLevel.RAW_SERIALIZATION:
            ctx = self._compile_raw_serialization(
                state, query, ordered_occ_ids, active_premises, all_input_occ_ids,
                dropped_by_validity, validity_drop_reasons, surviving_envs, state_h, equiv_h, equivalence_class_id
            )
        elif self.pipeline == PrivilegeLevel.TOPOLOGY_AWARE_GROUPING:
            ctx = self._compile_topology_aware(
                state, query, active_premises, all_input_occ_ids,
                dropped_by_validity, validity_drop_reasons, surviving_envs, state_h, equiv_h, equivalence_class_id
            )
        elif self.pipeline == PrivilegeLevel.GENEALOGICAL_NORMALIZATION:
            ctx = self._compile_genealogical_normalization(
                state, query, ordered_occ_ids, active_premises, all_input_occ_ids,
                dropped_by_validity, validity_drop_reasons, surviving_envs, state_h, equiv_h, equivalence_class_id
            )
        elif self.pipeline == PrivilegeLevel.PROOF_CARRYING_CERTIFICATE:
            ctx = self._compile_proof_carrying(
                state, query, active_premises, all_input_occ_ids,
                dropped_by_validity, validity_drop_reasons, surviving_envs, state_h, equiv_h, equivalence_class_id
            )
        else:
            raise ValueError(f"Unknown compiler pipeline: {self.pipeline}")

        if not ctx.verify_provenance_conservation():
            raise ValueError(
                f"Compiler pass violated provenance conservation: "
                f"source={all_input_occ_ids}, emitted={ctx.emitted_occurrence_ids}, "
                f"merged={ctx.merged_occurrence_groups}, dropped={ctx.dropped_occurrence_ids}"
            )

        return ctx

    def _compile_raw_serialization(
        self,
        state: EpistemicState,
        query: QueryContract,
        ordered_occ_ids: list[str],
        active_premises: dict[str, PremiseNode],
        all_input_occ_ids: list[str],
        dropped_by_validity: list[str],
        validity_drop_reasons: dict[str, str],
        surviving_envs: list[Any],
        state_h: str,
        equiv_h: str,
        eq_id: str,
    ) -> CompiledContext:
        passes = ["validity_filter", "raw_sequence_serialization"]
        lines = ["AUTHORIZATION RULES:"]
        for r in state.rules.values():
            lines.append(f"- {r.rendered_text}")

        lines.append("\nRETRIEVED EPISODIC EVIDENCE:")
        included_claims = set()
        represented_roots = set()
        tag_map = {}
        for idx, occ_id in enumerate(ordered_occ_ids):
            p = active_premises[occ_id]
            tag = f"DOC_{idx+1:02d}"
            lines.append(f"- [{tag}]: {p.rendered_text}")
            included_claims.add(p.semantic_claim_id)
            represented_roots.update(p.root_ids)
            tag_map[tag] = p.semantic_claim_id

        lines.append(f"\nQUESTION: {query.query_question}")
        lines.append(f"Return strictly JSON matching this schema: {query.output_schema_json}")

        return CompiledContext(
            prompt="\n".join(lines),
            state_hash=state_h,
            equiv_hash=equiv_h,
            source_occurrence_ids=all_input_occ_ids,
            emitted_occurrence_ids=ordered_occ_ids,
            included_semantic_claim_ids=sorted(list(included_claims)),
            represented_root_ids=sorted(list(represented_roots)),
            surviving_support_environment_ids=[e.path_id for e in surviving_envs],
            evidence_tag_to_claim_map=tag_map,
            merged_occurrence_groups={},
            dropped_occurrence_ids=dropped_by_validity,
            drop_or_merge_reasons=validity_drop_reasons,
            compiler_passes=passes,
            privilege_level=PrivilegeLevel.RAW_SERIALIZATION,
            equivalence_class_id=eq_id,
        )

    def _compile_topology_aware(
        self,
        state: EpistemicState,
        query: QueryContract,
        active_premises: dict[str, PremiseNode],
        all_input_occ_ids: list[str],
        dropped_by_validity: list[str],
        validity_drop_reasons: dict[str, str],
        surviving_envs: list[Any],
        state_h: str,
        equiv_h: str,
        eq_id: str,
    ) -> CompiledContext:
        passes = ["validity_filter", "formal_path_selection", "pathway_clustering", "canonical_ordering"]
        lines = ["AUTHORIZATION RULES:"]
        for r in state.rules.values():
            lines.append(f"- {r.rendered_text}")

        lines.append("\nEPISTEMIC SUPPORT PATHWAYS:")
        included_occs = []
        included_claims = set()
        represented_roots = set()
        dropped_occs = list(dropped_by_validity)
        drop_reasons = dict(validity_drop_reasons)
        tag_map = {}
        doc_counter = 1

        if not surviving_envs:
            lines.append("No complete, valid derivation pathways exist in active memory.")
            for occ_id in sorted(active_premises.keys()):
                p = active_premises[occ_id]
                tag = f"DOC_{doc_counter:02d}"
                lines.append(f"- [{tag}] [Unconnected] {p.rendered_text}")
                included_occs.append(occ_id)
                included_claims.add(p.semantic_claim_id)
                represented_roots.update(p.root_ids)
                tag_map[tag] = p.semantic_claim_id
                doc_counter += 1
        else:
            for idx, env in enumerate(sorted(surviving_envs, key=lambda e: e.path_id)):
                lines.append(f"Pathway {idx+1}:")
                for cid in sorted(env.required_semantic_claim_ids):
                    matching = [p for p in active_premises.values() if p.semantic_claim_id == cid]
                    if matching:
                        primary = matching[0]
                        tag = f"DOC_{doc_counter:02d}"
                        lines.append(f"  * [{tag}]: {primary.rendered_text}")
                        if primary.occurrence_id not in included_occs:
                            included_occs.append(primary.occurrence_id)
                        included_claims.add(primary.semantic_claim_id)
                        represented_roots.update(primary.root_ids)
                        tag_map[tag] = primary.semantic_claim_id
                        doc_counter += 1

            for occ_id in active_premises.keys():
                if occ_id not in included_occs:
                    dropped_occs.append(occ_id)
                    drop_reasons[occ_id] = "not_selected_for_surviving_pathway"

        lines.append(f"\nQUESTION: {query.query_question}")
        lines.append(f"Return strictly JSON matching this schema: {query.output_schema_json}")

        return CompiledContext(
            prompt="\n".join(lines),
            state_hash=state_h,
            equiv_hash=equiv_h,
            source_occurrence_ids=all_input_occ_ids,
            emitted_occurrence_ids=included_occs,
            included_semantic_claim_ids=sorted(list(included_claims)),
            represented_root_ids=sorted(list(represented_roots)),
            surviving_support_environment_ids=[e.path_id for e in surviving_envs],
            evidence_tag_to_claim_map=tag_map,
            merged_occurrence_groups={},
            dropped_occurrence_ids=dropped_occs,
            drop_or_merge_reasons=drop_reasons,
            compiler_passes=passes,
            privilege_level=PrivilegeLevel.TOPOLOGY_AWARE_GROUPING,
            equivalence_class_id=eq_id,
        )

    def _compile_genealogical_normalization(
        self,
        state: EpistemicState,
        query: QueryContract,
        ordered_occ_ids: list[str],
        active_premises: dict[str, PremiseNode],
        all_input_occ_ids: list[str],
        dropped_by_validity: list[str],
        validity_drop_reasons: dict[str, str],
        surviving_envs: list[Any],
        state_h: str,
        equiv_h: str,
        eq_id: str,
    ) -> CompiledContext:
        passes = ["validity_filter", "semantic_lineage_deduplication", "canonical_ordering"]
        lines = ["AUTHORIZATION RULES:"]
        for r in state.rules.values():
            lines.append(f"- {r.rendered_text}")

        lines.append("\nGENEALOGICALLY DEDUPLICATED ROOTS:")
        
        dedup_groups: dict[tuple[tuple[str, ...], str, str], list[PremiseNode]] = {}
        for occ_id in ordered_occ_ids:
            p = active_premises[occ_id]
            if p.provenance_status == ProvenanceStatus.UNKNOWN_UNTRACKED:
                key = (tuple(), p.semantic_claim_id, p.occurrence_id)
            else:
                key = (tuple(sorted(p.root_ids)), p.semantic_claim_id, "")
            dedup_groups.setdefault(key, []).append(p)

        included_occs = []
        included_claims = set()
        represented_roots = set()
        merged_groups = {}
        dropped_occs = list(dropped_by_validity)
        drop_reasons = dict(validity_drop_reasons)
        tag_map = {}
        doc_counter = 1

        for (roots_tuple, claim_id, unique_tag), occ_list in sorted(dedup_groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
            primary = occ_list[0]
            count = len(occ_list)
            root_label = "+".join(roots_tuple) if roots_tuple else "ambient"
            tag = f"DOC_{doc_counter:02d}"
            if count > 1:
                lines.append(f"- [{tag}] Root {root_label} ({count} cited occurrences): {primary.rendered_text}")
                merged_groups[primary.occurrence_id] = [p.occurrence_id for p in occ_list]
                for p in occ_list[1:]:
                    drop_reasons[p.occurrence_id] = f"merged_into_{primary.occurrence_id}_same_lineage_claim"
            else:
                lines.append(f"- [{tag}] Root {root_label}: {primary.rendered_text}")

            included_occs.append(primary.occurrence_id)
            included_claims.add(primary.semantic_claim_id)
            represented_roots.update(primary.root_ids)
            tag_map[tag] = primary.semantic_claim_id
            doc_counter += 1

        return CompiledContext(
            prompt="\n".join(lines + [f"\nQUESTION: {query.query_question}", f"Return strictly JSON matching this schema: {query.output_schema_json}"]),
            state_hash=state_h,
            equiv_hash=equiv_h,
            source_occurrence_ids=all_input_occ_ids,
            emitted_occurrence_ids=included_occs,
            included_semantic_claim_ids=sorted(list(included_claims)),
            represented_root_ids=sorted(list(represented_roots)),
            surviving_support_environment_ids=[e.path_id for e in surviving_envs],
            evidence_tag_to_claim_map=tag_map,
            merged_occurrence_groups=merged_groups,
            dropped_occurrence_ids=dropped_occs,
            drop_or_merge_reasons=drop_reasons,
            compiler_passes=passes,
            privilege_level=PrivilegeLevel.GENEALOGICAL_NORMALIZATION,
            equivalence_class_id=eq_id,
        )

    def _compile_proof_carrying(
        self,
        state: EpistemicState,
        query: QueryContract,
        active_premises: dict[str, PremiseNode],
        all_input_occ_ids: list[str],
        dropped_by_validity: list[str],
        validity_drop_reasons: dict[str, str],
        surviving_envs: list[Any],
        state_h: str,
        equiv_h: str,
        eq_id: str,
    ) -> CompiledContext:
        passes = ["validity_filter", "formal_entitlement_audit", "proof_carrying_certificate_emission"]
        lines = ["EPISTEMIC AUDIT CERTIFICATE:"]
        entitled = state.is_formally_entitled()

        distinct_roots = set()
        for p in active_premises.values():
            distinct_roots.update(p.root_ids)

        lines.append(f"Formal Entitlement Status: {'VALID_DERIVATION_EXISTS' if entitled else 'NO_VALID_DERIVATION'}")
        lines.append(f"Active Support Pathways: {len(surviving_envs)}")
        lines.append(f"Distinct Ancestral Roots Represented: {len(distinct_roots)}")

        lines.append("\nAUTHORIZATION RULES:")
        for r in state.rules.values():
            lines.append(f"- {r.rendered_text}")

        lines.append("\nVERIFIED EVIDENCE BASE:")
        included_occs = []
        included_claims = set()
        tag_map = {}
        for idx, occ_id in enumerate(sorted(active_premises.keys())):
            p = active_premises[occ_id]
            roots_str = "+".join(sorted(p.root_ids)) if p.root_ids else "ambient"
            tag = f"DOC_{idx+1:02d}"
            lines.append(f"- [{tag}] Root={roots_str}: {p.rendered_text}")
            included_occs.append(p.occurrence_id)
            included_claims.add(p.semantic_claim_id)
            tag_map[tag] = p.semantic_claim_id

        lines.append(f"\nQUESTION: {query.query_question}")
        lines.append(f"Return strictly JSON matching this schema: {query.output_schema_json}")

        return CompiledContext(
            prompt="\n".join(lines),
            state_hash=state_h,
            equiv_hash=equiv_h,
            source_occurrence_ids=all_input_occ_ids,
            emitted_occurrence_ids=included_occs,
            included_semantic_claim_ids=sorted(list(included_claims)),
            represented_root_ids=sorted(list(distinct_roots)),
            surviving_support_environment_ids=[e.path_id for e in surviving_envs],
            evidence_tag_to_claim_map=tag_map,
            merged_occurrence_groups={},
            dropped_occurrence_ids=dropped_by_validity,
            drop_or_merge_reasons=validity_drop_reasons,
            compiler_passes=passes,
            privilege_level=PrivilegeLevel.PROOF_CARRYING_CERTIFICATE,
            equivalence_class_id=eq_id,
        )
