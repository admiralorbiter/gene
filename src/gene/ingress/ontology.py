"""Ontology and Capability Policy Registries for Epistemic Ingress (Round 7)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Set

from gene.ingress.models import (
    AuthenticatedOrigin,
    ClaimPrivilege,
    SourceRecord,
    TrustedSourceContext,
)


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
    max_claim_privilege: ClaimPrivilege = ClaimPrivilege.ROOT_FACT
    reliability_class: str = "HIGH_PRECISION_SENSOR"
    default_independence_prefix: str = "ROOT"


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


def derive_trusted_source_context(
    source_record: SourceRecord,
    capability_registry: CapabilityPolicyRegistry,
) -> TrustedSourceContext:
    """Derive authentic TrustedSourceContext from platform record and capability policy.
    
    Enforces origin verification and prevents spoofed claimed origins.
    """
    claimed = source_record.claimed_origin
    auth = source_record.authenticated_origin

    # Cross-check: If claimed source does not match authenticated identity, flag spoofing
    is_spoofed = (auth.is_authenticated and claimed.claimed_source_name != auth.verified_id)
    if is_spoofed:
        return TrustedSourceContext(
            authenticity="UNVERIFIED",
            authorization_scope=frozenset(),
            max_claim_privilege=ClaimPrivilege.ATTESTATION_ONLY,
            reliability_class="SPOOFED_UNTRUSTED",
            independence_class=f"SPOOFED_{auth.verified_id}",
            is_spoofed_origin=True,
        )

    if not auth.is_authenticated or auth.auth_method == "ANONYMOUS":
        return TrustedSourceContext(
            authenticity="UNVERIFIED",
            authorization_scope=frozenset(["user_feedback", "feedback_only"]),
            max_claim_privilege=ClaimPrivilege.ATTESTATION_ONLY,
            reliability_class="UNTRUSTED_ANONYMOUS",
            independence_class=f"ROOT_ANONYMOUS_{auth.verified_id}",
            is_spoofed_origin=False,
        )

    # Lookup capability policy for authenticated role
    policy = capability_registry.get_policy(claimed.claimed_role)
    if not policy:
        return TrustedSourceContext(
            authenticity="PLATFORM_LOCAL" if "LOCAL" in auth.auth_method else "CRYPTOGRAPHIC_VERIFIED",
            authorization_scope=frozenset(),
            max_claim_privilege=ClaimPrivilege.ATTESTATION_ONLY,
            reliability_class="UNREGISTERED_ROLE",
            independence_class=f"ROOT_{auth.verified_id}",
            is_spoofed_origin=False,
        )

    auth_type = "PLATFORM_LOCAL" if "LOCAL" in auth.auth_method else "CRYPTOGRAPHIC_VERIFIED"
    return TrustedSourceContext(
        authenticity=auth_type,
        authorization_scope=policy.authorized_predicates,
        max_claim_privilege=policy.max_claim_privilege,
        reliability_class=policy.reliability_class,
        independence_class=f"{policy.default_independence_prefix}_{auth.verified_id}",
        is_spoofed_origin=False,
    )


class IngressOntology:
    """Registry of known entities, surface aliases, and candidate generation multimap."""

    def __init__(self, entities: Optional[list[EntityDefinition]] = None):
        self._entities: dict[str, EntityDefinition] = {}
        # Multimap: alias string -> set of entity IDs (preserves ambiguity!)
        self._alias_to_ids: dict[str, set[str]] = defaultdict(set)
        for ent in entities or []:
            self.register_entity(ent)

    def register_entity(self, ent: EntityDefinition) -> None:
        self._entities[ent.entity_id] = ent
        self._alias_to_ids[ent.canonical_name.lower()].add(ent.entity_id)
        for alias in ent.aliases:
            self._alias_to_ids[alias.lower()].add(ent.entity_id)

    def get_entity(self, entity_id: str) -> Optional[EntityDefinition]:
        return self._entities.get(entity_id)

    def resolve_alias_candidates(self, alias_str: str) -> tuple[str, ...]:
        """Resolve a surface alias string to all associated entity IDs."""
        cleaned = alias_str.strip().lower()
        return tuple(sorted(self._alias_to_ids.get(cleaned, set())))

    def find_candidates(self, mention_span: str) -> tuple[str, ...]:
        """Find all candidate entity IDs for a mention span (exact or substring)."""
        span_lower = mention_span.strip().lower()
        exact = self.resolve_alias_candidates(span_lower)
        if exact:
            return exact

        # Substring / partial matching
        candidates: set[str] = set()
        for alias, eids in self._alias_to_ids.items():
            if span_lower in alias or alias in span_lower:
                candidates.update(eids)
        return tuple(sorted(candidates))

    def contains_entity(self, entity_id: str) -> bool:
        return entity_id in self._entities
