"""Lineage graph builder and artifact export pipeline for GENE runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
import networkx as nx
from gene.persistence.db import Database
from gene.worlds.schema import World


class LineageRecorder:
    """Manages exposure and reported-support edges and builds the full genealogical lineage DAG."""

    @classmethod
    def record_exposure_edges(
        cls,
        db: Database,
        parent_child_pairs: list[tuple[str, str, str, int, int]],
    ) -> None:
        """Log exposure edges (parent_node_id, child_node_id, call_id, retrieval_rank, context_position)."""
        with db.conn:
            for p_id, c_id, call_id, rank, pos in parent_child_pairs:
                db.conn.execute(
                    """
                    INSERT OR REPLACE INTO exposure_edges (
                        parent_node_id, child_node_id, call_id, retrieval_rank, context_position
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (p_id, c_id, call_id, rank, pos),
                )

    @classmethod
    def record_reported_support_edges(
        cls,
        db: Database,
        reported_pairs: list[tuple[str, str, str, str]],
    ) -> None:
        """Log model-reported support edges (parent_node_id, child_node_id, call_id, reported_role)."""
        with db.conn:
            for p_id, c_id, call_id, role in reported_pairs:
                db.conn.execute(
                    """
                    INSERT OR REPLACE INTO reported_support_edges (
                        parent_node_id, child_node_id, call_id, reported_role
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (p_id, c_id, call_id, role),
                )

    @classmethod
    def build_lineage_graph(cls, db: Database, run_id: str) -> nx.MultiDiGraph:
        """Construct a NetworkX multi-directed graph representing exposure, reported, and verified causal lineage."""
        G = nx.MultiDiGraph()

        # 1. Add all memory nodes with claim attributes
        nodes = db.conn.execute(
            """
            SELECT m.node_id, m.generation, m.node_type, m.natural_text, m.reproductive_status,
                   c.subject, c.predicate, c.object, c.truth_status, c.infection_status, c.parse_status
            FROM memory_nodes m
            LEFT JOIN claims c ON m.node_id = c.node_id
            WHERE m.run_id = ?
            """,
            (run_id,),
        ).fetchall()

        for n in nodes:
            G.add_node(
                n["node_id"],
                generation=n["generation"],
                node_type=n["node_type"],
                natural_text=n["natural_text"] or "",
                reproductive_status=n["reproductive_status"] or "active",
                subject=n["subject"] or "",
                predicate=n["predicate"] or "",
                object=n["object"] or "",
                truth_status=n["truth_status"] or "unknown",
                infection_status=n["infection_status"] or "unresolved",
                parse_status=n["parse_status"] or "unknown",
            )

        # 2. Add exposure edges
        exp_edges = db.conn.execute(
            """
            SELECT e.parent_node_id, e.child_node_id, e.call_id, e.retrieval_rank, e.context_position
            FROM exposure_edges e
            JOIN calls c ON e.call_id = c.call_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()

        for e in exp_edges:
            G.add_edge(
                e["parent_node_id"],
                e["child_node_id"],
                key=f"exp_{e['call_id']}_{e['parent_node_id']}",
                edge_type="exposure",
                call_id=e["call_id"],
                retrieval_rank=e["retrieval_rank"],
                context_position=e["context_position"],
            )

        # 3. Add reported-support edges
        rep_edges = db.conn.execute(
            """
            SELECT r.parent_node_id, r.child_node_id, r.call_id, r.reported_role
            FROM reported_support_edges r
            JOIN calls c ON r.call_id = c.call_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()

        for r in rep_edges:
            G.add_edge(
                r["parent_node_id"],
                r["child_node_id"],
                key=f"rep_{r['call_id']}_{r['parent_node_id']}",
                edge_type="reported_support",
                call_id=r["call_id"],
                reported_role=r["reported_role"] or "support",
            )

        # 4. Add causal edges (only confirmed causal shifts, or tag non-causal explicitly)
        causal_tests = db.conn.execute(
            """
            SELECT ct.parent_node_id, ct.child_node_id, ct.causal_test_id,
                   ct.intervention_type, ct.outcome, ct.score
            FROM causal_tests ct
            JOIN calls c ON ct.original_call_id = c.call_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()

        for ct in causal_tests:
            G.add_edge(
                ct["parent_node_id"],
                ct["child_node_id"],
                key=f"causal_{ct['causal_test_id']}",
                edge_type="causal",
                intervention_type=ct["intervention_type"],
                outcome=ct["outcome"],
                score=ct["score"],
                causal_verified=(ct["outcome"] in ("strong", "partial")),
            )

        return G

    @classmethod
    def export_run_artifacts(
        cls,
        db: Database,
        run_id: str,
        world: World,
        output_dir: str | Path,
        metrics: dict[str, Any] | None = None,
        client_type: str = "UnknownClient",
    ) -> Path:
        """Export all 10 required experiment run artifacts to output directory with full manifest config."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # 1. manifest.json (include parsed config and explicit execution backend)
        run_row = db.conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        manifest = dict(run_row) if run_row else {"run_id": run_id}
        manifest["client_type"] = client_type
        manifest["execution_backend"] = "ollama" if "Ollama" in client_type else "reference"
        if "config_json" in manifest and manifest["config_json"]:
            try:
                manifest["config"] = json.loads(manifest["config_json"])
            except Exception:
                pass

        with open(out / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # 2. world.json
        with open(out / "world.json", "w", encoding="utf-8") as f:
            f.write(world.canonical_json())

        # 3. mutation.json
        if world.mutation:
            with open(out / "mutation.json", "w", encoding="utf-8") as f:
                f.write(world.mutation.canonical_json())

        # 4. calls.jsonl
        calls = db.conn.execute("SELECT * FROM calls WHERE run_id = ? ORDER BY created_at ASC", (run_id,)).fetchall()
        with open(out / "calls.jsonl", "w", encoding="utf-8") as f:
            for c in calls:
                f.write(json.dumps(dict(c)) + "\n")

        # 5. memory_nodes.jsonl
        nodes = db.conn.execute("SELECT * FROM memory_nodes WHERE run_id = ? ORDER BY generation ASC, created_at ASC", (run_id,)).fetchall()
        with open(out / "memory_nodes.jsonl", "w", encoding="utf-8") as f:
            for n in nodes:
                f.write(json.dumps(dict(n)) + "\n")

        # 6. claims.csv
        claims = db.conn.execute(
            """
            SELECT c.* FROM claims c
            JOIN memory_nodes m ON c.node_id = m.node_id
            WHERE m.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        if claims:
            keys = claims[0].keys()
            with open(out / "claims.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for cl in claims:
                    writer.writerow(dict(cl))
        else:
            with open(out / "claims.csv", "w", newline="", encoding="utf-8") as f:
                f.write("claim_id,node_id,subject,predicate,object,parse_status,truth_status,infection_status,oracle_evidence_json\n")

        # 7. exposure_edges.csv
        exp_edges = db.conn.execute(
            """
            SELECT e.* FROM exposure_edges e
            JOIN calls c ON e.call_id = c.call_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        if exp_edges:
            keys = exp_edges[0].keys()
            with open(out / "exposure_edges.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for e in exp_edges:
                    writer.writerow(dict(e))
        else:
            with open(out / "exposure_edges.csv", "w", newline="", encoding="utf-8") as f:
                f.write("parent_node_id,child_node_id,call_id,retrieval_rank,context_position\n")

        # 8. reported_support_edges.csv
        rep_edges = db.conn.execute(
            """
            SELECT r.* FROM reported_support_edges r
            JOIN calls c ON r.call_id = c.call_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        if rep_edges:
            keys = rep_edges[0].keys()
            with open(out / "reported_support_edges.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for r in rep_edges:
                    writer.writerow(dict(r))
        else:
            with open(out / "reported_support_edges.csv", "w", newline="", encoding="utf-8") as f:
                f.write("parent_node_id,child_node_id,call_id,reported_role\n")

        # 9. causal_tests.csv
        causal_tests = db.conn.execute(
            """
            SELECT ct.* FROM causal_tests ct
            JOIN calls c ON ct.original_call_id = c.call_id
            WHERE c.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        if causal_tests:
            keys = causal_tests[0].keys()
            with open(out / "causal_tests.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for ct in causal_tests:
                    writer.writerow(dict(ct))
        else:
            with open(out / "causal_tests.csv", "w", newline="", encoding="utf-8") as f:
                f.write("causal_test_id,parent_node_id,child_node_id,original_call_id,intervention_type,intervention_seed,counterfactual_call_id,outcome,score,comparison_json\n")

        # 10. metrics.json
        with open(out / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics or {}, f, indent=2)

        # 11. lineage.graphml
        graph = cls.build_lineage_graph(db, run_id)
        nx.write_graphml(graph, out / "lineage.graphml")

        return out
