"""SQLite database schema, migrations, and append-only persistence layer for GENE."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any
from gene.worlds.schema import Fact, Mutation, Rule, World


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS worlds (
    world_id TEXT PRIMARY KEY,
    world_seed INTEGER NOT NULL,
    world_version TEXT NOT NULL,
    canonical_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    validation_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS world_facts (
    fact_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    truth_value INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    canonical_json TEXT NOT NULL,
    FOREIGN KEY(world_id) REFERENCES worlds(world_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rules (
    rule_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    rule_json TEXT NOT NULL,
    rule_depth INTEGER NOT NULL,
    FOREIGN KEY(world_id) REFERENCES worlds(world_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mutations (
    mutation_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    true_fact_id TEXT NOT NULL,
    mutated_subject TEXT NOT NULL,
    mutated_predicate TEXT NOT NULL,
    mutated_object TEXT NOT NULL,
    mutation_type TEXT NOT NULL,
    FOREIGN KEY(world_id) REFERENCES worlds(world_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    experiment_version TEXT NOT NULL,
    condition TEXT NOT NULL,
    world_id TEXT NOT NULL,
    model_name TEXT,
    model_digest TEXT,
    ollama_version TEXT,
    seed INTEGER,
    num_ctx INTEGER,
    temperature REAL,
    prompt_version TEXT,
    prompt_hash TEXT,
    retrieval_policy TEXT,
    memory_policy TEXT,
    git_commit TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY(world_id) REFERENCES worlds(world_id)
);

CREATE TABLE IF NOT EXISTS calls (
    call_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    generation INTEGER NOT NULL,
    task_id TEXT,
    request_json TEXT NOT NULL,
    response_text TEXT,
    response_json TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    latency_ms REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS memory_nodes (
    node_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    world_id TEXT NOT NULL,
    generation INTEGER NOT NULL,
    node_type TEXT NOT NULL,
    natural_text TEXT NOT NULL,
    structured_json TEXT,
    reproductive_status TEXT DEFAULT 'active',
    created_by_call_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(run_id),
    FOREIGN KEY(world_id) REFERENCES worlds(world_id),
    FOREIGN KEY(created_by_call_id) REFERENCES calls(call_id)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    parse_status TEXT NOT NULL,
    truth_status TEXT NOT NULL,
    infection_status TEXT NOT NULL,
    oracle_evidence_json TEXT,
    FOREIGN KEY(node_id) REFERENCES memory_nodes(node_id)
);

CREATE TABLE IF NOT EXISTS exposure_edges (
    parent_node_id TEXT NOT NULL,
    child_node_id TEXT NOT NULL,
    call_id TEXT NOT NULL,
    retrieval_rank INTEGER,
    context_position INTEGER,
    PRIMARY KEY(parent_node_id, child_node_id, call_id),
    FOREIGN KEY(parent_node_id) REFERENCES memory_nodes(node_id),
    FOREIGN KEY(child_node_id) REFERENCES memory_nodes(node_id),
    FOREIGN KEY(call_id) REFERENCES calls(call_id)
);

CREATE TABLE IF NOT EXISTS reported_support_edges (
    parent_node_id TEXT NOT NULL,
    child_node_id TEXT NOT NULL,
    call_id TEXT NOT NULL,
    reported_role TEXT,
    PRIMARY KEY(parent_node_id, child_node_id, call_id),
    FOREIGN KEY(child_node_id) REFERENCES memory_nodes(node_id),
    FOREIGN KEY(call_id) REFERENCES calls(call_id)
);

CREATE TABLE IF NOT EXISTS causal_tests (
    causal_test_id TEXT PRIMARY KEY,
    parent_node_id TEXT NOT NULL,
    child_node_id TEXT NOT NULL,
    original_call_id TEXT NOT NULL,
    intervention_type TEXT NOT NULL,
    intervention_seed INTEGER,
    counterfactual_call_id TEXT,
    outcome TEXT NOT NULL,
    score REAL,
    comparison_json TEXT,
    FOREIGN KEY(child_node_id) REFERENCES memory_nodes(node_id),
    FOREIGN KEY(original_call_id) REFERENCES calls(call_id),
    FOREIGN KEY(counterfactual_call_id) REFERENCES calls(call_id)
);

CREATE TABLE IF NOT EXISTS evaluations (
    evaluation_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    scope_type TEXT NOT NULL,
    scope_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    metric_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);
"""


class Database:
    """Database interface for GENE experimental records."""

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.init_schema()

    def init_schema(self) -> None:
        """Initialize all schema tables."""
        with self.conn:
            self.conn.executescript(SCHEMA_SQL)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()

    def save_world(self, world: World) -> None:
        """Save a canonical world, its facts, rules, and optional mutation record."""
        now = datetime.now(timezone.utc).isoformat()
        with self.conn:
            # 1. Insert world record
            self.conn.execute(
                """
                INSERT OR REPLACE INTO worlds (
                    world_id, world_seed, world_version, canonical_json, created_at, validation_hash
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    world.world_id,
                    world.world_seed,
                    world.world_version,
                    world.canonical_json(),
                    now,
                    world.validation_hash(),
                ),
            )

            # 2. Insert source facts
            for fact in world.facts:
                self.conn.execute(
                    """
                    INSERT OR REPLACE INTO world_facts (
                        fact_id, world_id, subject, predicate, object, truth_value, source_type, canonical_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        fact.fact_id,
                        world.world_id,
                        fact.subject,
                        fact.predicate,
                        fact.object,
                        1 if fact.truth_value else 0,
                        fact.source_type,
                        fact.canonical_json(),
                    ),
                )

            # 3. Insert rules
            for rule in world.rules:
                self.conn.execute(
                    """
                    INSERT OR REPLACE INTO rules (
                        rule_id, world_id, rule_json, rule_depth
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        rule.rule_id,
                        world.world_id,
                        rule.canonical_json(),
                        rule.depth,
                    ),
                )

            # 4. Insert mutation if present
            if world.mutation:
                m = world.mutation
                self.conn.execute(
                    """
                    INSERT OR REPLACE INTO mutations (
                        mutation_id, world_id, true_fact_id, mutated_subject, mutated_predicate, mutated_object, mutation_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        m.mutation_id,
                        world.world_id,
                        m.true_fact.fact_id,
                        m.mutated_fact.subject,
                        m.mutated_fact.predicate,
                        m.mutated_fact.object,
                        m.mutation_type,
                    ),
                )

    def load_world(self, world_id: str) -> World | None:
        """Load and reconstruct a canonical World by its world_id."""
        row = self.conn.execute(
            "SELECT canonical_json FROM worlds WHERE world_id = ?", (world_id,)
        ).fetchone()
        if not row:
            return None
        data = json.loads(row["canonical_json"])
        return World.model_validate(data)
