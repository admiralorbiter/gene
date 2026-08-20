"""Epistemic Intermediate Representation (EpistemicIR v2.1).

Separates the machine-readable EpistemicState, QueryContract, and ExperimentOracle.
Provides typed RuleSpecs, occurrence and semantic claim identities, recombinant roots,
exact state hashing (H_state), semantic equivalence hashing (H_equiv), and an IR self-consistency validator.
"""

from __future__ import annotations

import copy
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


class RuleAntecedent(BaseModel):
    """A typed structural antecedent atom in a deductive rule."""
    predicate: str
    subject_role: str | None = None
    target_value: str | None = None


class RuleSpec(BaseModel):
    """A formal deductive rule governing epistemic derivation."""
    rule_id: str
    antecedents: list[RuleAntecedent] = Field(default_factory=list)
    consequent_predicate: str
    consequent_protocol: str = "PROTO_X7"
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

    def compute_state_hash(self) -> str:
        """Compute exact cryptographic hash of full state (H_state), including occurrences and ancestry."""
        premise_data = {}
        for occ_id, p in sorted(self.premises.items()):
            premise_data[occ_id] = {
                "semantic_claim_id": p.semantic_claim_id,
                "predicate": p.predicate,
                "subject": p.subject,
                "entity": p.entity,
                "role": p.role,
                "target_value": p.target_value,
                "root_ids": sorted(p.root_ids),
                "is_valid": p.is_valid,
                "authority_level": p.authority_level,
                "generation": p.generation,
            }
        rule_data = {}
        for r_id, r in sorted(self.rules.items()):
            rule_data[r_id] = {
                "antecedents": [a.model_dump() for a in r.antecedents],
                "consequent_predicate": r.consequent_predicate,
                "consequent_protocol": r.consequent_protocol,
            }
        state_repr = {
            "premises": premise_data,
            "rules": rule_data,
            "support_environments": [e.model_dump() for e in sorted(self.support_environments, key=lambda e: e.path_id)],
            "invalidated_roots": sorted(self.invalidated_roots),
        }
        return hashlib.sha256(json.dumps(state_repr, sort_keys=True).encode("utf-8")).hexdigest()

    def compute_equiv_hash(self) -> str:
        """Compute cryptographic hash of semantic equivalence class (H_equiv)."""
        data = {
            "active_claims": sorted(list(self.get_active_semantic_claim_ids())),
            "invalidated_roots": sorted(self.invalidated_roots),
            "surviving_paths": sorted([e.path_id for e in self.get_surviving_support_environments()]),
            "rules": sorted([r.rule_id for r in self.rules.values()]),
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

    def subselect_occurrences(self, occurrence_ids: list[str]) -> EpistemicState:
        """Create a truthful subselected EpistemicState containing strictly the chosen occurrences."""
        sub = copy.deepcopy(self)
        sub.premises = {
            occ_id: p for occ_id, p in sub.premises.items()
            if occ_id in occurrence_ids
        }
        return sub


def validate_ir_consistency(state: EpistemicState, query: QueryContract | None = None) -> list[str]:
    """Validate internal consistency across PremiseNodes, RuleSpecs, SupportEnvironments, and QueryContract."""
    errors = []

    # 1. Premise validation
    for occ_id, p in state.premises.items():
        if not p.occurrence_id:
            errors.append(f"Premise {occ_id} has empty occurrence_id")
        if not p.semantic_claim_id:
            errors.append(f"Premise {occ_id} has empty semantic_claim_id")
        if not p.root_ids:
            errors.append(f"Premise {occ_id} has empty root_ids list")

    # 2. Rule validation
    for r_id, r in state.rules.items():
        if not r.antecedents:
            errors.append(f"Rule {r_id} has empty antecedents list")
        if not r.consequent_predicate:
            errors.append(f"Rule {r_id} has empty consequent_predicate")

    # 3. Support environment validation
    for env in state.support_environments:
        if env.rule_id not in state.rules:
            errors.append(f"SupportEnvironment {env.path_id} references unregistered rule {env.rule_id}")
        for cid in env.required_semantic_claim_ids:
            matching = [p for p in state.premises.values() if p.semantic_claim_id == cid]
            if not matching:
                errors.append(f"SupportEnvironment {env.path_id} requires semantic claim {cid} not present in state.premises")

    # 4. Query alignment validation
    if query is not None:
        for r in state.rules.values():
            if query.target_predicate not in r.consequent_predicate:
                errors.append(f"Rule {r.rule_id} consequent {r.consequent_predicate} does not align with query target {query.target_predicate}")

    return errors
