"""Epistemic Intermediate Representation (EpistemicIR).

Defines the central, machine-readable data structures for formal support environments,
ancestral lineage roots, validity states, and query contracts independent of prompt serialization.
"""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class PremiseNode(BaseModel):
    """An individual atomic premise or evidence unit in the epistemic state."""
    premise_id: str
    text: str
    predicate: str | None = None
    subject: str | None = None
    role: str | None = None
    target_value: str | None = None
    root_id: str
    is_valid: bool = True
    authority_level: str = "standard"  # e.g. "standard", "root_authority", "relay"
    generation: int = 0
    citations: list[str] = Field(default_factory=list)


class SupportEnvironment(BaseModel):
    """A minimal set of premises that formally and deductively entails the claim."""
    path_id: str
    required_premise_ids: list[str]
    rule_description: str | None = None
    is_active: bool = True


class EpistemicIR(BaseModel):
    """The central Intermediate Representation (IR) produced by the Epistemic Kernel."""
    target_station: str
    target_claim: str
    expected_protocol: str
    premises: dict[str, PremiseNode]
    support_environments: list[SupportEnvironment] = Field(default_factory=list)
    invalidated_roots: list[str] = Field(default_factory=list)
    query_question: str

    def get_active_premises(self) -> dict[str, PremiseNode]:
        """Return all premises that are valid and not derived from an invalidated root."""
        return {
            pid: p for pid, p in self.premises.items()
            if p.is_valid and p.root_id not in self.invalidated_roots
        }

    def get_surviving_support_environments(self) -> list[SupportEnvironment]:
        """Return support environments whose required premises are all active."""
        active_ids = set(self.get_active_premises().keys())
        surviving = []
        for env in self.support_environments:
            if env.is_active and all(pid in active_ids for pid in env.required_premise_ids):
                surviving.append(env)
        return surviving

    def is_formally_entitled(self) -> bool:
        """A claim is formally entitled iff at least one support environment survives."""
        return len(self.get_surviving_support_environments()) > 0
