"""Ontology, Capability Policy, and Lineage Independence Registries for Epistemic Ingress (Round 7)."""

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
    """Defines domain authorization rules for a verified principal or principal role."""
    principal_id_or_role: str
    authorized_predicates: frozenset[str]
    max_claim_privilege: ClaimPrivilege = ClaimPrivilege.ROOT_FACT
    reliability_class: str = "HIGH_PRECISION_SENSOR"
    is_ontology_admin: bool = False
    can_disambiguate: bool = True


class CapabilityPolicyRegistry:
    """Pure registry mapping authenticated principal identities / roles to authorization policies.
    
    SECURITY INVARIANT:
    Keyed by AuthenticatedOrigin.verified_id (or principal role mapping in registry).
    Never keyed by untrusted textually ClaimedOrigin.claimed_role.
    """

    def __init__(
        self,
        policies: Optional[dict[str, CapabilityPolicy]] = None,
        principal_role_bindings: Optional[dict[str, str]] = None,
    ):
        self._policies = dict(policies or {})
        self._principal_role_bindings = dict(principal_role_bindings or {})

    def register(self, policy: CapabilityPolicy) -> None:
        self._policies[policy.principal_id_or_role] = policy

    def bind_principal_role(self, verified_id: str, role_name: str) -> None:
        self._principal_role_bindings[verified_id] = role_name

    def get_policy(self, verified_id: str) -> Optional[CapabilityPolicy]:
        # 1. Direct principal policy match
        if verified_id in self._policies:
            return self._policies[verified_id]
        # 2. Bound principal role match
        role = self._principal_role_bindings.get(verified_id)
        if role and role in self._policies:
            return self._policies[role]
        return None

    def is_authorized(self, verified_id: str, predicate: str) -> bool:
        pol = self.get_policy(verified_id)
        if not pol:
            return False
        return predicate in pol.authorized_predicates or "*" in pol.authorized_predicates

    def is_ontology_admin(self, verified_id: str) -> bool:
        pol = self.get_policy(verified_id)
        return pol.is_ontology_admin if pol else False

    def can_disambiguate(self, verified_id: str, predicate: str) -> bool:
        pol = self.get_policy(verified_id)
        if not pol:
            return False
        if not pol.can_disambiguate:
            return False
        return predicate in pol.authorized_predicates or "*" in pol.authorized_predicates


class LineageIndependenceRegistry:
    """Pure registry mapping authenticated origins to defensible independence classes.
    
    SECURITY INVARIANT:
    OriginIdentity != DerivationLineage != IndependenceClass.
    Verified identity alone does NOT establish epistemic independence.
    Unmapped origins default to explicit unverified classes.
    """

    def __init__(self, mappings: Optional[dict[str, str]] = None):
        self._mappings = dict(mappings or {})

    def register_independence_class(self, verified_id: str, independence_class: str) -> None:
        self._mappings[verified_id] = independence_class

    def get_independence_class(self, verified_id: str) -> str:
        return self._mappings.get(verified_id, f"ROOT_UNKNOWN_INDEPENDENCE_{verified_id}")


def derive_trusted_source_context(
    source_record: SourceRecord,
    capability_registry: CapabilityPolicyRegistry,
    independence_registry: Optional[LineageIndependenceRegistry] = None,
) -> TrustedSourceContext:
    """Derive authentic TrustedSourceContext from platform record and principal capability policy.
    
    Enforces origin verification and prevents spoofed claimed origins or claimed roles.
    STRICT SECURITY INVARIANT:
    If independence_registry is missing or unmapped, strictly defaults to ROOT_UNKNOWN_INDEPENDENCE.
    Never reconstructs independence from verified identity.
    """
    claimed = source_record.claimed_origin
    auth = source_record.authenticated_origin

    # 1. Cross-check: Claimed name must match authenticated identity
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
            independence_class=f"ROOT_UNKNOWN_INDEPENDENCE_{auth.verified_id}",
            is_spoofed_origin=False,
        )

    # 2. Lookup capability policy strictly by AuthenticatedOrigin.verified_id (NEVER claimed_role)
    policy = capability_registry.get_policy(auth.verified_id)
    if not policy:
        return TrustedSourceContext(
            authenticity="PLATFORM_LOCAL" if "LOCAL" in auth.auth_method else "CRYPTOGRAPHIC_VERIFIED",
            authorization_scope=frozenset(),
            max_claim_privilege=ClaimPrivilege.ATTESTATION_ONLY,
            reliability_class="UNREGISTERED_PRINCIPAL",
            independence_class=f"ROOT_UNKNOWN_INDEPENDENCE_{auth.verified_id}",
            is_spoofed_origin=False,
        )

    # 3. Derive independence class from explicit registry (STRICT FAIL-CLOSED)
    ind_class = independence_registry.get_independence_class(auth.verified_id) if independence_registry else f"ROOT_UNKNOWN_INDEPENDENCE_{auth.verified_id}"

    auth_type = "PLATFORM_LOCAL" if "LOCAL" in auth.auth_method else "CRYPTOGRAPHIC_VERIFIED"
    return TrustedSourceContext(
        authenticity=auth_type,
        authorization_scope=policy.authorized_predicates,
        max_claim_privilege=policy.max_claim_privilege,
        reliability_class=policy.reliability_class,
        independence_class=ind_class,
        is_spoofed_origin=False,
    )


class IngressOntology:
    """Registry of known entities, surface aliases, and candidate generation multimap."""

    def __init__(self, entities: Optional[list[EntityDefinition]] = None):
        self._entities: dict[str, EntityDefinition] = {}
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
        cleaned = alias_str.strip().lower()
        return tuple(sorted(self._alias_to_ids.get(cleaned, set())))

    def find_candidates(self, mention_span: str) -> tuple[str, ...]:
        span_lower = mention_span.strip().lower()
        exact = self.resolve_alias_candidates(span_lower)
        if exact:
            return exact

        candidates: set[str] = set()
        for alias, eids in self._alias_to_ids.items():
            if span_lower in alias or alias in span_lower:
                candidates.update(eids)
        return tuple(sorted(candidates))

    def contains_entity(self, entity_id: str) -> bool:
        return entity_id in self._entities
