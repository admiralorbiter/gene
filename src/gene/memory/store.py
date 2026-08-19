"""Append-only memory store for GENE experimental runs."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Literal
from pydantic import BaseModel, Field
from gene.persistence.db import Database


class MemoryNode(BaseModel):
    """An individual persisted unit of information in the memory store."""
    node_id: str
    run_id: str
    world_id: str
    generation: int
    node_type: Literal["source", "derived", "repair", "mutated"]
    natural_text: str
    structured_json: dict[str, Any] | None = None
    reproductive_status: Literal["active", "quarantined", "senescent", "dead"] = "active"
    created_by_call_id: str | None = None
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


class MemoryStore:
    """Interface for append-only memory retrieval and insertion."""

    def __init__(self, db: Database, run_id: str, world_id: str):
        self.db = db
        self.run_id = run_id
        self.world_id = world_id

    def add_node(
        self,
        generation: int,
        node_type: Literal["source", "derived", "repair", "mutated"],
        natural_text: str,
        structured_json: dict[str, Any] | None = None,
        node_id: str | None = None,
        created_by_call_id: str | None = None,
    ) -> MemoryNode:
        """Append a new memory node to the store and database."""
        nid = node_id or f"node_{uuid.uuid4().hex[:12]}"
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        node = MemoryNode(
            node_id=nid,
            run_id=self.run_id,
            world_id=self.world_id,
            generation=generation,
            node_type=node_type,
            natural_text=natural_text,
            structured_json=structured_json,
            created_by_call_id=created_by_call_id,
            created_at=now,
        )

        with self.db.conn:
            self.db.conn.execute(
                """
                INSERT INTO memory_nodes (
                    node_id, run_id, world_id, generation, node_type, natural_text,
                    structured_json, reproductive_status, created_by_call_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node.node_id,
                    node.run_id,
                    node.world_id,
                    node.generation,
                    node.node_type,
                    node.natural_text,
                    json.dumps(node.structured_json) if node.structured_json else None,
                    node.reproductive_status,
                    node.created_by_call_id,
                    node.created_at,
                ),
            )
        return node

    def get_all_active_nodes(self, max_generation: int | None = None) -> list[MemoryNode]:
        """Fetch all active memory nodes available up to specified generation."""
        query = "SELECT * FROM memory_nodes WHERE run_id = ? AND reproductive_status = 'active'"
        params: list[Any] = [self.run_id]
        if max_generation is not None:
            query += " AND generation <= ?"
            params.append(max_generation)
        query += " ORDER BY generation ASC, created_at ASC"

        rows = self.db.conn.execute(query, params).fetchall()
        nodes = []
        for r in rows:
            structured = json.loads(r["structured_json"]) if r["structured_json"] else None
            nodes.append(
                MemoryNode(
                    node_id=r["node_id"],
                    run_id=r["run_id"],
                    world_id=r["world_id"],
                    generation=r["generation"],
                    node_type=r["node_type"],
                    natural_text=r["natural_text"],
                    structured_json=structured,
                    reproductive_status=r["reproductive_status"],
                    created_by_call_id=r["created_by_call_id"],
                    created_at=r["created_at"],
                )
            )
        return nodes
