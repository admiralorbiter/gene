"""Track B3: Monoculture Factorial Multiverse Engine.

Generates the full 16-cell factorial design over root structure, token assignment,
document position ordering, and station context, with pure lexical root isolation.
"""

from __future__ import annotations

import difflib
from typing import Any
from pydantic import BaseModel, Field


class MultiverseCell(BaseModel):
    cell_id: str
    root_structure: str  # 'independent' vs 'monoculture'
    token_mapping: str   # 'M4_majority' vs 'Q7_majority'
    doc_order: str       # 'forward' vs 'interleaved'
    station: str         # 'VELORA' vs 'KESTREL'
    majority_protocol: str
    minority_protocol: str
    prompt: str
    raw_docs: list[str]


class MultiverseGenerator:
    """Constructs balanced factorial cells with pure lexical root token isolation."""

    def __init__(self):
        self.stations = ["VELORA", "KESTREL"]
        self.root_structures = ["independent", "monoculture"]
        self.token_mappings = ["M4_majority", "Q7_majority"]
        self.doc_orders = ["forward", "interleaved"]

    def build_prompt(
        self,
        station: str,
        root_structure: str,
        token_mapping: str,
        doc_order: str,
    ) -> MultiverseCell:
        if token_mapping == "M4_majority":
            maj_proto = "PROTO_M4"
            min_proto = "PROTO_Q7"
        else:
            maj_proto = "PROTO_Q7"
            min_proto = "PROTO_M4"

        # Pure template: identical sentence structure, only root tokens vary
        if root_structure == "independent":
            # 3 distinct roots for majority; 2 distinct roots for minority
            d1 = f"Source root_R1 states station {station} requires protocol {maj_proto}."
            d2 = f"Source root_R2 states station {station} requires protocol {maj_proto}."
            d3 = f"Source root_R3 states station {station} requires protocol {maj_proto}."
            d4 = f"Source root_R4 states station {station} requires protocol {min_proto}."
            d5 = f"Source root_R5 states station {station} requires protocol {min_proto}."
        else:  # monoculture
            # 1 shared root (root_R1 repeated 3 times) for majority; 2 distinct roots for minority
            d1 = f"Source root_R1 states station {station} requires protocol {maj_proto}."
            d2 = f"Source root_R1 states station {station} requires protocol {maj_proto}."
            d3 = f"Source root_R1 states station {station} requires protocol {maj_proto}."
            d4 = f"Source root_R4 states station {station} requires protocol {min_proto}."
            d5 = f"Source root_R5 states station {station} requires protocol {min_proto}."

        if doc_order == "forward":
            ordered_docs = [d1, d2, d3, d4, d5]
        else:  # interleaved: [min, maj, min, maj, maj]
            ordered_docs = [d4, d1, d5, d2, d3]

        doc_lines = [f"- DOC_{i+1:02d}: {doc}" for i, doc in enumerate(ordered_docs)]

        prompt = (
            "RETRIEVED EVIDENCE:\n"
            + "\n".join(doc_lines)
            + f"\n\nQUESTION: Based on the retrieved evidence, which security protocol is best supported for station {station}?\n"
            "Return strictly JSON matching this schema:\n"
            '{"station": "STATION_NAME", "adjudicated_protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
        )

        cell_id = f"cell_{station.lower()}_{root_structure}_{token_mapping}_{doc_order}"

        return MultiverseCell(
            cell_id=cell_id,
            root_structure=root_structure,
            token_mapping=token_mapping,
            doc_order=doc_order,
            station=station,
            majority_protocol=maj_proto,
            minority_protocol=min_proto,
            prompt=prompt,
            raw_docs=ordered_docs,
        )

    def generate_all_16_cells(self) -> list[MultiverseCell]:
        cells = []
        for st in self.stations:
            for rs in self.root_structures:
                for tm in self.token_mappings:
                    for do in self.doc_orders:
                        cells.append(self.build_prompt(st, rs, tm, do))
        return cells

    @staticmethod
    def compute_machine_diff(prompt_a: str, prompt_b: str) -> list[str]:
        """Produce unified line-by-line diff between two prompts."""
        diff = difflib.unified_diff(
            prompt_a.splitlines(keepends=True),
            prompt_b.splitlines(keepends=True),
            fromfile="treatment",
            tofile="control",
        )
        return list(diff)
