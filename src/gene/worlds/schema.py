"""Canonical domain models and serialization for GENE worlds."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


def compute_fact_id(subject: str, predicate: str, obj: str) -> str:
    """Compute a deterministic, stable fact identifier from canonical triple."""
    canonical_repr = f"{subject.strip().upper()}|{predicate.strip().lower()}|{obj.strip().upper()}"
    digest = hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()[:12]
    return f"fact_{digest}"


class Fact(BaseModel):
    """An atomic canonical proposition in the ground-truth ledger."""
    subject: str
    predicate: str
    object: str
    truth_value: bool = True
    source_type: Literal["generated", "derived", "mutated"] = "generated"
    fact_id: str = Field(default="")
    locus_id: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if not self.fact_id:
            self.fact_id = compute_fact_id(self.subject, self.predicate, self.object)

    @property
    def triple(self) -> tuple[str, str, str]:
        """Return the canonical (subject, predicate, object) tuple."""
        return (self.subject, self.predicate, self.object)

    def canonical_dict(self) -> dict[str, Any]:
        """Return sorted canonical dictionary representation."""
        d = {
            "fact_id": self.fact_id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "truth_value": self.truth_value,
            "source_type": self.source_type,
        }
        if self.locus_id:
            d["locus_id"] = self.locus_id
        return d

    def canonical_json(self) -> str:
        """Deterministic canonical JSON serialization."""
        return json.dumps(self.canonical_dict(), sort_keys=True)


class Rule(BaseModel):
    """A deterministic forward-chaining rule with antecedent clauses and consequent."""
    rule_id: str
    antecedents: list[tuple[str, str, str]]
    consequent: tuple[str, str, str]
    depth: int = 1
    description: str | None = None

    def canonical_dict(self) -> dict[str, Any]:
        """Return sorted canonical dictionary representation."""
        return {
            "rule_id": self.rule_id,
            "antecedents": self.antecedents,
            "consequent": self.consequent,
            "depth": self.depth,
            "description": self.description,
        }

    def canonical_json(self) -> str:
        """Deterministic canonical JSON serialization."""
        return json.dumps(self.canonical_dict(), sort_keys=True)


class Mutation(BaseModel):
    """Specification of a single atomic corruption in a world pair."""
    mutation_id: str
    world_id: str
    true_fact: Fact
    mutated_fact: Fact
    mutation_type: str = "attribute_swap"

    def canonical_dict(self) -> dict[str, Any]:
        """Return sorted canonical dictionary representation."""
        return {
            "mutation_id": self.mutation_id,
            "world_id": self.world_id,
            "true_fact": self.true_fact.canonical_dict(),
            "mutated_fact": self.mutated_fact.canonical_dict(),
            "mutation_type": self.mutation_type,
        }

    def canonical_json(self) -> str:
        """Deterministic canonical JSON serialization."""
        return json.dumps(self.canonical_dict(), sort_keys=True)


class Task(BaseModel):
    """A benchmark query requiring retrieval and reasoning."""
    task_id: str
    world_id: str
    query_type: str  # e.g., "attribute_lookup", "rule_inference"
    target_fact: Fact
    reasoning_depth: int  # 0 for D0 (direct source), 1 for D1 (one rule), 2 for D2
    prompt: str
    expected_answer: str
    valid_support_path_ids: list[list[str]] = Field(default_factory=list)

    def canonical_dict(self) -> dict[str, Any]:
        """Return sorted canonical dictionary representation."""
        return {
            "task_id": self.task_id,
            "world_id": self.world_id,
            "query_type": self.query_type,
            "target_fact": self.target_fact.canonical_dict(),
            "reasoning_depth": self.reasoning_depth,
            "prompt": self.prompt,
            "expected_answer": self.expected_answer,
            "valid_support_path_ids": sorted(self.valid_support_path_ids),
        }

    def canonical_json(self) -> str:
        """Deterministic canonical JSON serialization."""
        return json.dumps(self.canonical_dict(), sort_keys=True)


class World(BaseModel):
    """An immutable, canonical synthetic world specification."""
    world_id: str
    world_seed: int
    world_version: str = "v1"
    entities: dict[str, list[str]] = Field(default_factory=dict)
    facts: list[Fact] = Field(default_factory=list)
    rules: list[Rule] = Field(default_factory=list)
    mutation: Mutation | None = None

    def canonical_dict(self) -> dict[str, Any]:
        """Return sorted canonical dictionary representation for stable hashing."""
        sorted_entities = {k: sorted(v) for k, v in sorted(self.entities.items())}
        sorted_facts = sorted(
            [f.canonical_dict() for f in self.facts],
            key=lambda x: (x["subject"], x["predicate"], x["object"]),
        )
        sorted_rules = sorted(
            [r.canonical_dict() for r in self.rules],
            key=lambda x: x["rule_id"],
        )
        return {
            "world_id": self.world_id,
            "world_seed": self.world_seed,
            "world_version": self.world_version,
            "entities": sorted_entities,
            "facts": sorted_facts,
            "rules": sorted_rules,
            "mutation": self.mutation.canonical_dict() if self.mutation else None,
        }

    def canonical_json(self) -> str:
        """Deterministic JSON string of the canonical world."""
        return json.dumps(self.canonical_dict(), sort_keys=True, indent=2)

    def validation_hash(self) -> str:
        """Compute SHA256 validation hash of canonical world JSON."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
