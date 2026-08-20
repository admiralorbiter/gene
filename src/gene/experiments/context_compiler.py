"""Epistemic Context Compiler (v2).

Compiles machine-readable EpistemicState and QueryContract into a CompiledContext.
Supports four distinct compilation pipelines with explicit privilege auditing:
1. RAW_SERIALIZATION ('raw_flat'): Unstructured sequence of active premises + rules.
2. TOPOLOGY_AWARE_GROUPING ('canonical_support_blocks'): Organizes premises by formal proof path.
3. GENEALOGICAL_NORMALIZATION ('lineage_deduplicated'): Semantic-lineage deduplication by (root_id, semantic_claim_id).
4. PROOF_CARRYING_CERTIFICATE ('support_certificate'): Prepend explicit kernel derivation certificate.
"""

from __future__ import annotations

import hashlib
from typing import Any
from pydantic import BaseModel, Field
from gene.experiments.epistemic_ir import (
    EpistemicState,
    PremiseNode,
    PrivilegeLevel,
    QueryContract,
    RuleSpec,
)


class CompiledContext(BaseModel):
    """Result of context compilation, carrying full provenance and audit metadata."""
    prompt: str
    source_ir_hash: str
    included_occurrence_ids: list[str]
    included_semantic_claim_ids: list[str]
    represented_root_ids: list[str]
    surviving_support_environment_ids: list[str]
    compiler_passes: list[str]
    privilege_level: PrivilegeLevel
    equivalence_class_id: str


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
        ir_hash = state.compute_ir_hash()
        active_premises = state.get_active_premises()
        surviving_envs = state.get_surviving_support_environments()

        # Determine ordering of occurrences
        if occurrence_order is not None:
            ordered_occ_ids = [occ_id for occ_id in occurrence_order if occ_id in active_premises]
        else:
            ordered_occ_ids = sorted(list(active_premises.keys()))

        if self.pipeline == PrivilegeLevel.RAW_SERIALIZATION:
            return self._compile_raw_serialization(state, query, ordered_occ_ids, active_premises, surviving_envs, ir_hash, equivalence_class_id)
        elif self.pipeline == PrivilegeLevel.TOPOLOGY_AWARE_GROUPING:
            return self._compile_topology_aware(state, query, active_premises, surviving_envs, ir_hash, equivalence_class_id)
        elif self.pipeline == PrivilegeLevel.GENEALOGICAL_NORMALIZATION:
            return self._compile_genealogical_normalization(state, query, ordered_occ_ids, active_premises, surviving_envs, ir_hash, equivalence_class_id)
        elif self.pipeline == PrivilegeLevel.PROOF_CARRYING_CERTIFICATE:
            return self._compile_proof_carrying(state, query, active_premises, surviving_envs, ir_hash, equivalence_class_id)
        else:
            raise ValueError(f"Unknown compiler pipeline: {self.pipeline}")

    def _compile_raw_serialization(
        self,
        state: EpistemicState,
        query: QueryContract,
        ordered_occ_ids: list[str],
        active_premises: dict[str, PremiseNode],
        surviving_envs: list[Any],
        ir_hash: str,
        eq_id: str,
    ) -> CompiledContext:
        passes = ["validity_filter", "raw_sequence_serialization"]
        lines = ["AUTHORIZATION RULES:"]
        for r in state.rules.values():
            lines.append(f"- {r.rendered_text}")

        lines.append("\nRETRIEVED EPISODIC EVIDENCE:")
        included_claims = set()
        represented_roots = set()
        for idx, occ_id in enumerate(ordered_occ_ids):
            p = active_premises[occ_id]
            lines.append(f"- DOC_{idx+1:02d}: {p.rendered_text}")
            included_claims.add(p.semantic_claim_id)
            represented_roots.update(p.root_ids)

        lines.append(f"\nQUESTION: {query.query_question}")
        lines.append(f"Return strictly JSON matching this schema: {query.output_schema_json}")

        return CompiledContext(
            prompt="\n".join(lines),
            source_ir_hash=ir_hash,
            included_occurrence_ids=ordered_occ_ids,
            included_semantic_claim_ids=sorted(list(included_claims)),
            represented_root_ids=sorted(list(represented_roots)),
            surviving_support_environment_ids=[e.path_id for e in surviving_envs],
            compiler_passes=passes,
            privilege_level=PrivilegeLevel.RAW_SERIALIZATION,
            equivalence_class_id=eq_id,
        )

    def _compile_topology_aware(
        self,
        state: EpistemicState,
        query: QueryContract,
        active_premises: dict[str, PremiseNode],
        surviving_envs: list[Any],
        ir_hash: str,
        eq_id: str,
    ) -> CompiledContext:
        passes = ["validity_filter", "support_pathway_clustering", "canonical_ordering"]
        lines = ["AUTHORIZATION RULES:"]
        for r in state.rules.values():
            lines.append(f"- {r.rendered_text}")

        lines.append("\nEPISTEMIC SUPPORT PATHWAYS:")
        included_occs = []
        included_claims = set()
        represented_roots = set()

        if not surviving_envs:
            lines.append("No complete, valid derivation pathways exist in active memory.")
            # Include isolated active premises
            for occ_id in sorted(active_premises.keys()):
                p = active_premises[occ_id]
                lines.append(f"- [Unconnected] {p.rendered_text}")
                included_occs.append(occ_id)
                included_claims.add(p.semantic_claim_id)
                represented_roots.update(p.root_ids)
        else:
            for idx, env in enumerate(sorted(surviving_envs, key=lambda e: e.path_id)):
                lines.append(f"Pathway {idx+1} ({env.path_id}):")
                for cid in sorted(env.required_semantic_claim_ids):
                    matching = [p for p in active_premises.values() if p.semantic_claim_id == cid]
                    if matching:
                        primary = matching[0]
                        lines.append(f"  * {primary.rendered_text}")
                        included_occs.append(primary.occurrence_id)
                        included_claims.add(primary.semantic_claim_id)
                        represented_roots.update(primary.root_ids)

        lines.append(f"\nQUESTION: {query.query_question}")
        lines.append(f"Return strictly JSON matching this schema: {query.output_schema_json}")

        return CompiledContext(
            prompt="\n".join(lines),
            source_ir_hash=ir_hash,
            included_occurrence_ids=included_occs,
            included_semantic_claim_ids=sorted(list(included_claims)),
            represented_root_ids=sorted(list(represented_roots)),
            surviving_support_environment_ids=[e.path_id for e in surviving_envs],
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
        surviving_envs: list[Any],
        ir_hash: str,
        eq_id: str,
    ) -> CompiledContext:
        """Semantic-lineage deduplication: groups by (tuple(root_ids), semantic_claim_id)."""
        passes = ["validity_filter", "semantic_lineage_deduplication", "canonical_ordering"]
        lines = ["AUTHORIZATION RULES:"]
        for r in state.rules.values():
            lines.append(f"- {r.rendered_text}")

        lines.append("\nGENEALOGICALLY DEDUPLICATED ROOTS:")
        
        # Group by (tuple(root_ids), semantic_claim_id)
        dedup_groups: dict[tuple[tuple[str, ...], str], list[PremiseNode]] = {}
        for occ_id in ordered_occ_ids:
            p = active_premises[occ_id]
            key = (tuple(sorted(p.root_ids)), p.semantic_claim_id)
            dedup_groups.setdefault(key, []).append(p)

        included_occs = []
        included_claims = set()
        represented_roots = set()

        for (roots_tuple, claim_id), occ_list in sorted(dedup_groups.items(), key=lambda x: (x[0][0], x[0][1])):
            primary = occ_list[0]
            count = len(occ_list)
            root_label = "+".join(roots_tuple) if roots_tuple else "ambient"
            if count > 1:
                lines.append(f"- Root {root_label} ({count} cited occurrences): {primary.rendered_text}")
            else:
                lines.append(f"- Root {root_label}: {primary.rendered_text}")

            included_occs.append(primary.occurrence_id)
            included_claims.add(primary.semantic_claim_id)
            represented_roots.update(primary.root_ids)

        lines.append(f"\nQUESTION: {query.query_question}")
        lines.append(f"Return strictly JSON matching this schema: {query.output_schema_json}")

        return CompiledContext(
            prompt="\n".join(lines),
            source_ir_hash=ir_hash,
            included_occurrence_ids=included_occs,
            included_semantic_claim_ids=sorted(list(included_claims)),
            represented_root_ids=sorted(list(represented_roots)),
            surviving_support_environment_ids=[e.path_id for e in surviving_envs],
            compiler_passes=passes,
            privilege_level=PrivilegeLevel.GENEALOGICAL_NORMALIZATION,
            equivalence_class_id=eq_id,
        )

    def _compile_proof_carrying(
        self,
        state: EpistemicState,
        query: QueryContract,
        active_premises: dict[str, PremiseNode],
        surviving_envs: list[Any],
        ir_hash: str,
        eq_id: str,
    ) -> CompiledContext:
        passes = ["validity_filter", "formal_entitlement_audit", "proof_carrying_certificate_emission"]
        lines = ["EPISTEMIC AUDIT CERTIFICATE:"]
        entitled = state.is_formally_entitled()

        # Clearly distinguish support environments count from independent ancestral roots count
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
        for occ_id in sorted(active_premises.keys()):
            p = active_premises[occ_id]
            roots_str = "+".join(sorted(p.root_ids)) if p.root_ids else "ambient"
            lines.append(f"- [{p.occurrence_id}] Root={roots_str}: {p.rendered_text}")
            included_occs.append(p.occurrence_id)
            included_claims.add(p.semantic_claim_id)

        lines.append(f"\nQUESTION: {query.query_question}")
        lines.append(f"Return strictly JSON matching this schema: {query.output_schema_json}")

        return CompiledContext(
            prompt="\n".join(lines),
            source_ir_hash=ir_hash,
            included_occurrence_ids=included_occs,
            included_semantic_claim_ids=sorted(list(included_claims)),
            represented_root_ids=sorted(list(distinct_roots)),
            surviving_support_environment_ids=[e.path_id for e in surviving_envs],
            compiler_passes=passes,
            privilege_level=PrivilegeLevel.PROOF_CARRYING_CERTIFICATE,
            equivalence_class_id=eq_id,
        )
