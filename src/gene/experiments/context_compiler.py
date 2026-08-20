"""Epistemic Context Compiler.

Compiles an EpistemicIR state into a serialized prompt for a neural model.
Supports four distinct compilation backends:
1. 'raw_flat': Unstructured sequence of active premises.
2. 'canonical_support_blocks': Structured grouping of premises into formal derivation paths.
3. 'lineage_deduplicated': Pre-inference genealogical resolution of multi-copy root redundancies.
4. 'support_certificate': Explicit derivation block certifying active valid proofs before query.
"""

from __future__ import annotations

from typing import Literal
from gene.experiments.epistemic_ir import EpistemicIR, PremiseNode


class EpistemicContextCompiler:
    """Compiles machine-readable EpistemicIR into neural prompts."""

    def __init__(self, backend: Literal["raw_flat", "canonical_support_blocks", "lineage_deduplicated", "support_certificate"] = "raw_flat"):
        self.backend = backend

    def compile(
        self,
        ir: EpistemicIR,
        premise_order: list[str] | None = None,
    ) -> str:
        """Compile the EpistemicIR into a complete prompt string."""
        active_premises = ir.get_active_premises()

        # Determine ordering
        if premise_order is not None:
            ordered_pids = [pid for pid in premise_order if pid in active_premises]
        else:
            ordered_pids = sorted(list(active_premises.keys()))

        if self.backend == "raw_flat":
            return self._compile_raw_flat(ir, ordered_pids, active_premises)
        elif self.backend == "canonical_support_blocks":
            return self._compile_canonical_support_blocks(ir, active_premises)
        elif self.backend == "lineage_deduplicated":
            return self._compile_lineage_deduplicated(ir, active_premises)
        elif self.backend == "support_certificate":
            return self._compile_support_certificate(ir, active_premises)
        else:
            raise ValueError(f"Unknown compiler backend: {self.backend}")

    def _compile_raw_flat(
        self, ir: EpistemicIR, ordered_pids: list[str], active_premises: dict[str, PremiseNode]
    ) -> str:
        lines = ["RETRIEVED EPISODIC EVIDENCE:"]
        for idx, pid in enumerate(ordered_pids):
            p = active_premises[pid]
            lines.append(f"- DOC_{idx+1:02d}: {p.text}")
        lines.append(f"\nQUESTION: {ir.query_question}")
        lines.append('Return strictly JSON matching this schema: {"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}')
        return "\n".join(lines)

    def _compile_canonical_support_blocks(
        self, ir: EpistemicIR, active_premises: dict[str, PremiseNode]
    ) -> str:
        lines = ["EPISTEMIC SUPPORT PATHWAYS:"]
        surviving_paths = ir.get_surviving_support_environments()

        if not surviving_paths:
            lines.append("No complete, valid derivation pathways exist in active memory.")
        else:
            for idx, path in enumerate(surviving_paths):
                lines.append(f"Pathway {idx+1} ({path.path_id}):")
                for pid in path.required_premise_ids:
                    p = active_premises[pid]
                    lines.append(f"  * {p.text}")

        lines.append(f"\nQUESTION: {ir.query_question}")
        lines.append('Return strictly JSON matching this schema: {"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}')
        return "\n".join(lines)

    def _compile_lineage_deduplicated(
        self, ir: EpistemicIR, active_premises: dict[str, PremiseNode]
    ) -> str:
        lines = ["GENEALOGICALLY DEDUPLICATED ROOTS:"]
        # Group active premises by root_id
        by_root: dict[str, list[PremiseNode]] = {}
        for p in active_premises.values():
            by_root.setdefault(p.root_id, []).append(p)

        for root_id, doc_list in by_root.items():
            primary = doc_list[0]
            count = len(doc_list)
            if count > 1:
                lines.append(f"- Root {root_id} ({count} cited/paraphrased occurrences): {primary.text}")
            else:
                lines.append(f"- Root {root_id}: {primary.text}")

        lines.append(f"\nQUESTION: {ir.query_question}")
        lines.append('Return strictly JSON matching this schema: {"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}')
        return "\n".join(lines)

    def _compile_support_certificate(
        self, ir: EpistemicIR, active_premises: dict[str, PremiseNode]
    ) -> str:
        lines = ["EPISTEMIC AUDIT CERTIFICATE:"]
        surviving_paths = ir.get_surviving_support_environments()
        entitled = ir.is_formally_entitled()

        lines.append(f"Formal Entitlement Status: {'VALID_DERIVATION_EXISTS' if entitled else 'NO_VALID_DERIVATION'}")
        lines.append(f"Active Independent Support Environments: {len(surviving_paths)}")
        
        lines.append("\nVERIFIED EVIDENCE BASE:")
        for idx, (pid, p) in enumerate(active_premises.items()):
            lines.append(f"- [{pid}] Root={p.root_id}: {p.text}")

        lines.append(f"\nQUESTION: {ir.query_question}")
        lines.append('Return strictly JSON matching this schema: {"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}')
        return "\n".join(lines)
