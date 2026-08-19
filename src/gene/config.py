"""Configuration models and loading utilities for GENE experiments."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal
from pydantic import BaseModel, Field
import yaml


class WorldGenConfig(BaseModel):
    """Configuration for synthetic world generation."""
    num_stations: int = 4
    num_people: int = 8
    num_sectors: int = 3
    num_protocols: int = 3
    num_teams: int = 3
    facts_per_world: int = 20
    rules_per_world: int = 4
    seed: int = 42


class RetrievalConfig(BaseModel):
    """Configuration for memory retrieval."""
    policy: Literal["controlled", "oracle_support_plus_distractors"] = "controlled"
    num_distractors: int = 3
    policy_version: str = "v1"


class ModelConfig(BaseModel):
    """Configuration for LLM inference (Ollama)."""
    model_config = {"protected_namespaces": ()}

    model_name: str = "gemma3:12b"
    temperature: float = 0.0
    num_ctx: int = 4096
    top_p: float | None = None
    seed: int | None = 42


class CausalConfig(BaseModel):
    """Configuration for counterfactual causal testing."""
    sample_rate: float = 1.0  # fraction of reported edges to test
    seeds_to_test: list[int] = Field(default_factory=lambda: [42])
    intervention_types: list[Literal["remove", "replace_clean"]] = Field(
        default_factory=lambda: ["remove", "replace_clean"]
    )


class ExperimentConfig(BaseModel):
    """Top-level configuration for an experiment run."""
    experiment_name: str = "exp0_lineage"
    experiment_version: str = "exp0-v1"
    condition: Literal["clean", "mutated"] = "clean"
    world_seed: int = 42
    decoding_seed: int = 42
    generations: int = 2
    prompt_version: str = "v1"
    world: WorldGenConfig = Field(default_factory=WorldGenConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    causal: CausalConfig = Field(default_factory=CausalConfig)

    def config_hash(self) -> str:
        """Compute deterministic SHA256 hash of this configuration."""
        serialized = self.model_dump_json(indent=None)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def from_yaml(cls, path: str | Path) -> ExperimentConfig:
        """Load experiment configuration from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    def to_yaml(self, path: str | Path) -> None:
        """Save experiment configuration to YAML file."""
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(mode="json"), f, sort_keys=False)
