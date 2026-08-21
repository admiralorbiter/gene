"""Ontology and Capability Policy Registries for Epistemic Ingress (Round 7)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class EntityDefinition:
    """Canonical entity specification in the domain ontology."""
    entity_id: str
    canonical_name: str
    entity_type: str  # e.g., "SERVER_NODE", "FACILITY", "OPERATOR"
    aliases: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""


@dataclass(frozen=True)
class CapabilityPolicy:
    """Defines domain authorization rules for a source role or origin class."""
    source_role: str
    authorized_predicates: frozenset[str]
    max_claim_privilege: str = "ROOT_FACT"  # "ROOT_FACT" | "ATTESTATION_ONLY" | "PREFERENCE_ONLY"


class CapabilityPolicyRegistry:
    """Pure registry mapping source identities / roles to authorization policies."""

    def __init__(self, policies: Optional[dict[str, CapabilityPolicy]] = None):
        self._policies = dict(policies or {})

    def register(self, policy: CapabilityPolicy) -> None:
        self._policies[policy.source_role] = policy

    def get_policy(self, source_role: str) -> Optional[CapabilityPolicy]:
        return self._policies.get(source_role)

    def is_authorized(self, source_role: str, predicate: str) -> bool:
        pol = self.get_policy(source_role)
        if not pol:
            return False
        return predicate in pol.authorized_predicates or "*" in pol.authorized_predicates


class IngressOntology:
    """Registry of known entities, surface aliases, and predicate contracts."""

    def __init__(self, entities: Optional[list[EntityDefinition]] = None):
        self._entities: dict[str, EntityDefinition] = {}
        self._alias_to_id: dict[str, str] = {}
        for ent in entities or []:
            self.register_entity(ent)

    def register_entity(self, ent: EntityDefinition) -> None:
        self._entities[ent.entity_id] = ent
        self._alias_to_id[ent.canonical_name.lower()] = ent.entity_id
        for alias in ent.aliases:
            self._alias_to_id[alias.lower()] = ent.entity_id

    def get_entity(self, entity_id: str) -> Optional[EntityDefinition]:
        return self._entities.get(entity_id)

    def resolve_alias(self, alias_str: str) -> Optional[str]:
        """Resolve a surface alias string to its canonical entity ID."""
        cleaned = alias_str.strip().lower()
        return self._alias_to_id.get(cleaned)

    def find_candidates(self, mention_span: str) -> tuple[str, ...]:
        """Find all plausible matching entity IDs for a mention span."""
        span_lower = mention_span.strip().lower()
        exact = self.resolve_alias(span_lower)
        if exact:
            return (exact,)

        # Prefix / substring / partial matching
        candidates = []
        for alias, eid in self._alias_to_id.items():
            if span_lower in alias or alias in span_lower:
                if eid not in candidates:
                    candidates.append(eid)
        return tuple(candidates)

    def contains_entity(self, entity_id: str) -> bool:
        return entity_id in self._entities
