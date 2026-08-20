"""Epistemic Intermediate Representation (EpistemicIR v2).

Separates the machine-readable EpistemicState, QueryContract, and ExperimentOracle,
providing explicit occurrence IDs, semantic claim IDs, recombinant roots, and structured RuleSpecs.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field


class PrivilegeLevel(str, Enum):
    """Privilege level exercised by the compiler pipeline."""
    RAW_SERIALIZATION = "raw_serialization"
    TOPOLOGY_AWARE_GROUPING = "topology_aware_grouping"
    GENEALOGICAL_NORMALIZATION = "genealogical_normalization"
    PROOF_CARRYING_CERTIFICATE = "proof_carrying_certificate"


class PremiseNode(BaseModel):
    """An individual atomic premise or evidence unit in the epistemic state."""
    occurrence_id: str
    semantic_claim_id: str
    predicate: str
    subject: str
    entity: str
    role: str | None = None
    target_value: str | None = None
    root_ids: list[str] = Field(default_factory=list)
    parent_occurrence_ids: list[str] = Field(default_factory=list)
    authority_level: str = "standard"  # "standard", "root_authority", "relay"
    generation: int = 0
    citations: list[str] = Field(default_factory=list)
    is_valid: bool = True
    rendered_text: str = ""


class RuleSpec(BaseModel):
    """A formal deductive rule governing epistemic derivation."""
    rule_id: str
    antecedent_predicates: list[str]
    consequent_predicate: str
    rendered_text: str = ""


class SupportEnvironment(BaseModel):
    """A minimal set of semantic claims that formally and deductively entails the target claim."""
    path_id: str
    rule_id: str
    required_semantic_claim_ids: list[str]
    is_active: bool = True


class QueryContract(BaseModel):
    """Specification of the epistemic query and abstention interface."""
    target_station: str
    target_predicate: str
    query_question: str
    allow_unknown: bool = True
    output_schema_json: str


class ExperimentOracle(BaseModel):
    """Oracle ground truth held separate from compiler context."""
    canonical_truth: str
    is_locally_derivable: bool
    gold_support_paths: list[list[str]]
    expected_protocol: str


class EpistemicState(BaseModel):
    """The central Intermediate Representation (IR) of epistemic structure."""
    premises: dict[str, PremiseNode]  # occurrence_id -> PremiseNode
    rules: dict[str, RuleSpec]        # rule_id -> RuleSpec
    support_environments: list[SupportEnvironment] = Field(default_factory=list)
    invalidated_roots: list[str] = Field(default_factory=list)

    def get_active_premises(self) -> dict[str, PremiseNode]:
        """Return all premises that are valid and not derived from any invalidated root."""
        return {
            occ_id: p for occ_id, p in self.premises.items()
            if p.is_valid and not any(r in self.invalidated_roots for r in p.root_ids)
        }

    def get_active_semantic_claim_ids(self) -> set[str]:
        """Return unique semantic claim IDs currently supported by active occurrences."""
        return {p.semantic_claim_id for p in self.get_active_premises().values()}

    def get_surviving_support_environments(self) -> list[SupportEnvironment]:
        """Return support environments whose required semantic claims are all present in active memory."""
        active_claim_ids = self.get_active_semantic_claim_ids()
        surviving = []
        for env in self.support_environments:
            if env.is_active and all(cid in active_claim_ids for cid in env.required_semantic_claim_ids):
                surviving.append(env)
        return surviving

    def is_formally_entitled(self) -> bool:
        """A state formally entitles the target claim iff at least one support environment survives."""
        return len(self.get_surviving_support_environments()) > 0

    def compute_ir_hash(self) -> str:
        """Compute stable cryptographic hash of active epistemic state."""
        active = self.get_active_premises()
        data = {
            "active_claims": sorted(list(self.get_active_semantic_claim_ids())),
            "invalidated_roots": sorted(self.invalidated_roots),
            "surviving_paths": sorted([e.path_id for e in self.get_surviving_support_environments()]),
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
