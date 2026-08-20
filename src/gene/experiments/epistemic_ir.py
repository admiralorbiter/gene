"""Epistemic Intermediate Representation (EpistemicIR v2.3).

Provides:
1. Complete exact state hashing (H_state) including parentage and citations.
2. Typed equivalence class hashing (H_perm, H_rep, H_alpha).
3. First-class provenance status (known_single, recombinant, unknown_untracked, asserted_unverified).
4. First-order variable unification & minimality in validate_ir_consistency().
5. Truthful subselected state validation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field


class PrivilegeLevel(str, Enum):
    """Privilege level exercised by the compiler pipeline."""
    RAW_SERIALIZATION = "raw_serialization"
    TOPOLOGY_AWARE_GROUPING = "topology_aware_grouping"
    GENEALOGICAL_NORMALIZATION = "genealogical_normalization"
    PROOF_CARRYING_CERTIFICATE = "proof_carrying_certificate"


class ProvenanceStatus(str, Enum):
    """Status of ancestral provenance for a premise."""
    KNOWN_SINGLE_ROOT = "known_single_root"
    KNOWN_RECOMBINANT_ROOTS = "known_recombinant_roots"
    UNKNOWN_UNTRACKED = "unknown_untracked"
    ASSERTED_UNVERIFIED = "asserted_unverified"


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
    provenance_status: ProvenanceStatus = ProvenanceStatus.KNOWN_SINGLE_ROOT
    authority_level: str = "standard"  # "standard", "root_authority", "relay"
    generation: int = 0
    citations: list[str] = Field(default_factory=list)
    is_valid: bool = True
    rendered_text: str = ""


class RuleAntecedent(BaseModel):
    """A typed structural antecedent atom in a deductive rule with variable bindings."""
    predicate: str
    subject_var: str = "P"
    entity_var: str = "S"
    subject_role: str | None = None
    target_value: str | None = None


class RuleSpec(BaseModel):
    """A formal deductive rule governing epistemic derivation."""
    rule_id: str
    antecedents: list[RuleAntecedent] = Field(default_factory=list)
    consequent_predicate: str = "station_operates_protocol"
    consequent_entity_var: str = "S"
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
        """Compute exact cryptographic hash of full state (H_state), including parentage and citations."""
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
                "parent_occurrence_ids": sorted(p.parent_occurrence_ids),
                "citations": sorted(p.citations),
                "provenance_status": p.provenance_status.value,
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

    def compute_permutation_equiv_hash(self) -> str:
        """H_perm: Invariant under premise reordering."""
        data = {
            "active_claims": sorted(list(self.get_active_semantic_claim_ids())),
            "invalidated_roots": sorted(self.invalidated_roots),
            "surviving_paths": sorted([e.path_id for e in self.get_surviving_support_environments()]),
            "rules": sorted([r.rule_id for r in self.rules.values()]),
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

    def compute_reproduction_equiv_hash(self) -> str:
        """H_rep: Invariant under copy multiplication (same roots, same semantic claims)."""
        active = self.get_active_premises()
        lineage_claim_pairs = sorted(list(set(
            (tuple(sorted(p.root_ids)), p.semantic_claim_id) for p in active.values()
        )))
        data = {
            "lineage_claim_pairs": [(list(r), c) for r, c in lineage_claim_pairs],
            "surviving_paths": sorted([e.path_id for e in self.get_surviving_support_environments()]),
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

    def compute_alpha_equiv_hash(self) -> str:
        """H_alpha: Invariant under formal alpha-renaming of roles (derived topologically from sorted rules)."""
        # Order roles topologically by their appearance in sorted rules
        ordered_roles = []
        for r_id, r in sorted(self.rules.items()):
            for ant in r.antecedents:
                if ant.subject_role and ant.subject_role not in ordered_roles:
                    ordered_roles.append(ant.subject_role)

        role_map = {r: f"ROLE_SLOT_{idx+1}" for idx, r in enumerate(ordered_roles)}

        abstract_claims = []
        for p in self.get_active_premises().values():
            abstract_claim = p.semantic_claim_id
            for r, slot in role_map.items():
                abstract_claim = abstract_claim.replace(r, slot)
            abstract_claims.append(abstract_claim)

        data = {
            "abstract_claims": sorted(list(set(abstract_claims))),
            "surviving_paths_count": len(self.get_surviving_support_environments()),
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


def validate_ir_consistency(
    state: EpistemicState,
    query: QueryContract | None = None,
    allow_partial_substate: bool = False,
) -> list[str]:
    """Validate internal proof-rule consistency, variable/entity unification, and minimality."""
    errors = []

    # 1. Premise validation
    for occ_id, p in state.premises.items():
        if not p.occurrence_id:
            errors.append(f"Premise {occ_id} has empty occurrence_id")
        if not p.semantic_claim_id:
            errors.append(f"Premise {occ_id} has empty semantic_claim_id")
        if p.provenance_status != ProvenanceStatus.UNKNOWN_UNTRACKED and not p.root_ids:
            errors.append(f"Premise {occ_id} has status {p.provenance_status} but empty root_ids list")

    # 2. Rule validation
    for r_id, r in state.rules.items():
        if not r.antecedents:
            errors.append(f"Rule {r_id} has empty antecedents list")
        if not r.consequent_predicate:
            errors.append(f"Rule {r_id} has empty consequent_predicate")

    # 3. Support Environment Proof-Rule Correspondence & First-Order Variable Unification
    active_claim_ids = state.get_active_semantic_claim_ids()

    for env in state.support_environments:
        if env.rule_id not in state.rules:
            errors.append(f"SupportEnvironment {env.path_id} references unregistered rule {env.rule_id}")
            continue

        rule = state.rules[env.rule_id]
        req_cids = env.required_semantic_claim_ids

        # If partial substate, skip full proof check for inactive environments whose claims aren't present
        if allow_partial_substate and not all(cid in active_claim_ids for cid in req_cids):
            continue

        # Minimality Check: Number of required premises must strictly equal number of antecedents
        if len(req_cids) != len(rule.antecedents):
            errors.append(f"SupportEnvironment {env.path_id} violates minimality: {len(req_cids)} claims required for {len(rule.antecedents)} antecedents")

        # Check required claims exist in state
        env_premises = []
        for cid in req_cids:
            matching = [p for p in state.premises.values() if p.semantic_claim_id == cid]
            if not matching:
                errors.append(f"SupportEnvironment {env.path_id} requires semantic claim {cid} not present in state")
            else:
                env_premises.append(matching[0])

        if len(env_premises) == len(req_cids) == len(rule.antecedents):
            # First-Order Variable Unification across antecedents
            var_bindings: dict[str, str] = {}
            matched_antecedents = set()

            for p in env_premises:
                # Find matching antecedent
                found_match = False
                for idx, ant in enumerate(rule.antecedents):
                    if idx in matched_antecedents:
                        continue
                    if p.predicate != ant.predicate:
                        continue
                    if ant.predicate == "has_role" and p.role != ant.subject_role:
                        continue
                    if ant.predicate == "reports_to" and p.target_value != ant.target_value:
                        continue

                    # Unify subject variable (e.g. P)
                    if ant.subject_var in var_bindings:
                        if var_bindings[ant.subject_var] != p.subject:
                            errors.append(f"SupportEnvironment {env.path_id} variable unification error: {ant.subject_var} bound to both '{var_bindings[ant.subject_var]}' and '{p.subject}'")
                    else:
                        var_bindings[ant.subject_var] = p.subject

                    # Unify entity variable (e.g. S)
                    if ant.entity_var in var_bindings:
                        if var_bindings[ant.entity_var] != p.entity:
                            errors.append(f"SupportEnvironment {env.path_id} variable unification error: {ant.entity_var} bound to both '{var_bindings[ant.entity_var]}' and '{p.entity}'")
                    else:
                        var_bindings[ant.entity_var] = p.entity

                    matched_antecedents.add(idx)
                    found_match = True
                    break

                if not found_match:
                    errors.append(f"Premise {p.occurrence_id} in {env.path_id} does not match any available antecedent of Rule {rule.rule_id}")

            # Check all antecedents matched
            if len(matched_antecedents) != len(rule.antecedents):
                errors.append(f"SupportEnvironment {env.path_id} failed to satisfy all antecedents of Rule {rule.rule_id}")

            # Query target alignment check
            if query is not None and rule.consequent_entity_var in var_bindings:
                bound_entity = var_bindings[rule.consequent_entity_var]
                if bound_entity != query.target_station:
                    errors.append(f"SupportEnvironment {env.path_id} bound entity '{bound_entity}' does not match query target station '{query.target_station}'")

    # 4. Query alignment validation
    if query is not None:
        for r in state.rules.values():
            if query.target_predicate not in r.consequent_predicate:
                errors.append(f"Rule {r.rule_id} consequent {r.consequent_predicate} does not align with query target {query.target_predicate}")

    return errors
