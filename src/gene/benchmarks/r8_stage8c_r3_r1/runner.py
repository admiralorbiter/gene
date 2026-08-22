"""Confirmatory Benchmark Runner for Stage 8C-R3-R1 (CONTRACT-R8-8C-R3-R1).
Executes 60 genuinely fresh sealed worlds (120 sequential decisions) with local Ollama Gemma 3 12B.
Includes:
1. Candidate Ingress Kernel with Refined Precedence (Structural parent + sub-ID, registered parentheticals).
2. Matched Precedence Ablation Resolver (Structural parent without sub-ID immediately defers without Rule 3 fall-through, while preserving valid structural partitions).
3. Decoupled Lifecycle State Machine & DB Ledger Reconciliation.
"""

import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from gene.benchmarks.r8_stage8c_r3_r1.prompts import format_stage8c_r3_r1_prompt
from gene.benchmarks.r8_stage8c_r3_r1.worlds import (
    generate_stage8c_r3_r1_worlds,
    get_stage8c_r3_r1_base_registry,
)

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:12b"

PARTITION_MARKERS = ["partition", "blade", "slice", "tray", "socket", "pool", "rack", "enclosure", "lun", "bay"]
SUB_IDENTIFIER_REGEX = re.compile(r"(?:\b|\s)(?:[0-9]+|[a-d])\b", re.IGNORECASE)


def contains_literal_phrase(text: str, phrase: str) -> bool:
    """Matches literal whole words / phrases respecting non-word boundaries."""
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, re.IGNORECASE) is not None


def normalize_alias(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[\s\-_,.:;/\\|()\[\]{}`'\"~*!?@#$%^&+=]+", "", s)
    return s


def compute_durable_state_hash(
    durable_registry: Dict[str, Any], provenance_edges: List[Dict[str, Any]]
) -> str:
    durable_entities = {k: v for k, v in sorted(durable_registry.items())}
    edges_sorted = sorted(provenance_edges, key=lambda e: (e["doc_id"], e["target_id"]))
    state_repr = json.dumps(
        {"entities": durable_entities, "edges": edges_sorted},
        sort_keys=True,
        ensure_ascii=True,
    )
    return hashlib.sha256(state_repr.encode("utf-8")).hexdigest()


def call_gemma_api(prompt: str) -> Dict[str, Any]:
    """Invokes local Ollama Gemma 3 12B at temperature 0.0 with fail-closed JSON fallback."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0,
            "top_p": 1.0,
            "num_predict": 512,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_API_URL, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            raw_text = res.get("response", "{}")
            try:
                return json.loads(raw_text)
            except Exception:
                match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                return {
                    "candidate_action": "DEFER",
                    "target_entity_id": None,
                    "confidence": 0.0,
                    "rationale": f"JSON parse fallback on text: {raw_text[:100]}",
                }
    except Exception as e:
        return {
            "candidate_action": "DEFER",
            "target_entity_id": None,
            "confidence": 0.0,
            "rationale": f"Ollama connection fallback: {str(e)}",
        }


class EpistemicIngressSessionR3R1:
    def __init__(self, base_registry: Dict[str, Any], world_id: str = "world_default"):
        self.world_id = world_id
        self.durable_registry = {k: dict(v) for k, v in base_registry.items()}
        self.provenance_edges: List[Dict[str, Any]] = []
        self.hypothesis_ledger: Dict[str, Any] = {}
        self.mutation_log: List[Dict[str, Any]] = []

    def get_durable_hash(self) -> str:
        return compute_durable_state_hash(self.durable_registry, self.provenance_edges)

    def extract_parentheticals(self, text: str) -> List[str]:
        return [m.strip() for m in re.findall(r"\(([^)]+)\)", text) if m.strip()]

    def _resolve_open_hypotheses(self, doc_id: str, mention: str, action: str, target_id: str, rule: str):
        """Updates open UNRESOLVED hypothesis in this world session when evidence resolves an identity."""
        hypo = self.hypothesis_ledger.get(self.world_id)
        if hypo and hypo.get("status") == "UNRESOLVED":
            cand = hypo.get("candidate_target")
            if action == "LINK":
                if cand is not None and cand != target_id:
                    hypo["status"] = "RETARGETED"
                elif cand is not None and cand == target_id:
                    hypo["status"] = "CONFIRMED"
                else:
                    hypo["status"] = "RESOLVED_EXISTING"
            elif action == "CREATE_PROVISIONAL":
                hypo["status"] = "RESOLVED_NOVEL"

            hypo["resolved_target"] = target_id
            hypo["resolving_doc_id"] = doc_id
            hypo.setdefault("evidence_history", []).append({
                "resolving_doc_id": doc_id,
                "resolving_mention": mention,
                "rule": rule,
                "action": action,
                "target_id": target_id,
            })

    def _handle_deferral(
        self,
        doc_id: str,
        source_id: str,
        mention: str,
        context: str,
        neural_proposal: Dict[str, Any],
        rule_name: str = "RULE_5_FAIL_CLOSED_DEFER",
    ) -> Dict[str, Any]:
        cand_target = neural_proposal.get("target_entity_id") if neural_proposal else None
        if self.world_id not in self.hypothesis_ledger:
            hypo_entry = {
                "hypothesis_id": f"hypo_{self.world_id}",
                "world_id": self.world_id,
                "originating_doc_id": doc_id,
                "surface_form": mention,
                "candidate_target": cand_target,
                "status": "UNRESOLVED",
                "resolved_target": None,
                "resolving_doc_id": None,
                "evidence_history": [{"doc_id": doc_id, "mention": mention, "context": context[:120], "action": "DEFER", "rule": rule_name}],
            }
            self.hypothesis_ledger[self.world_id] = hypo_entry
        else:
            hypo = self.hypothesis_ledger[self.world_id]
            hypo.setdefault("evidence_history", []).append({
                "doc_id": doc_id,
                "mention": mention,
                "context": context[:120],
                "action": "DEFER",
                "rule": rule_name,
            })
            if hypo.get("candidate_target") is None and cand_target:
                hypo["candidate_target"] = cand_target

        self.mutation_log.append(
            {"doc_id": doc_id, "action": "DEFER", "target": None, "durable": False}
        )
        return {
            "action": "DEFER",
            "target_id": None,
            "durable": False,
            "rule": rule_name,
        }

    def process_mention(
        self,
        doc_id: str,
        source_id: str,
        mention: str,
        context: str,
        neural_proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        norm_mention = normalize_alias(mention)

        # ---------------------------------------------------------------------
        # Rule 1: Exact Registered Alias / Name Match (Whole-field under N(s))
        # ---------------------------------------------------------------------
        for reg_id, reg_data in self.durable_registry.items():
            canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
            aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
            if norm_mention == canon_norm or norm_mention in aliases_norm:
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": reg_id,
                    "action": "LINK",
                    "rule": "RULE_1_EXACT_ALIAS_MATCH",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "LINK", "target": reg_id, "durable": True}
                )
                self._resolve_open_hypotheses(doc_id, mention, "LINK", reg_id, "RULE_1_EXACT_ALIAS_MATCH")
                return {
                    "action": "LINK",
                    "target_id": reg_id,
                    "durable": True,
                    "rule": "RULE_1_EXACT_ALIAS_MATCH",
                }

        # ---------------------------------------------------------------------
        # Rule 2: Structural First Refusal
        # Activates ONLY when mention contains grounded parent entity AND a discriminating sub-identifier
        # ---------------------------------------------------------------------
        grounded_parent_id = None
        for reg_id, reg_data in self.durable_registry.items():
            canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
            aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
            if canon_norm and canon_norm in norm_mention:
                grounded_parent_id = reg_id
                break
            for a_norm in aliases_norm:
                if a_norm and a_norm in norm_mention:
                    grounded_parent_id = reg_id
                    break
            if grounded_parent_id:
                break

        found_marker = None
        for m in PARTITION_MARKERS:
            if m in mention.lower():
                found_marker = m
                break

        sub_id_match = SUB_IDENTIFIER_REGEX.search(mention)

        if grounded_parent_id and found_marker and sub_id_match:
            sub_id = sub_id_match.group(0).strip().lower()
            prov_partition_id = f"prov_{grounded_parent_id}_{found_marker}_{sub_id}"

            if prov_partition_id in self.durable_registry:
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": prov_partition_id,
                    "action": "LINK",
                    "rule": "RULE_2_STRUCTURAL_PARTITION_LINK",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "LINK", "target": prov_partition_id, "durable": True}
                )
                self._resolve_open_hypotheses(doc_id, mention, "LINK", prov_partition_id, "RULE_2_STRUCTURAL_PARTITION_LINK")
                return {
                    "action": "LINK",
                    "target_id": prov_partition_id,
                    "durable": True,
                    "rule": "RULE_2_STRUCTURAL_PARTITION_LINK",
                }
            else:
                self.durable_registry[prov_partition_id] = {
                    "entity_id": prov_partition_id,
                    "canonical_name": mention,
                    "status": "provisional",
                    "parent_entity": grounded_parent_id,
                    "aliases": [mention],
                }
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": prov_partition_id,
                    "action": "CREATE_PROVISIONAL",
                    "rule": "RULE_2_STRUCTURAL_PARTITION_CREATE",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "CREATE_PROVISIONAL", "target": prov_partition_id, "durable": True}
                )
                self._resolve_open_hypotheses(doc_id, mention, "CREATE_PROVISIONAL", prov_partition_id, "RULE_2_STRUCTURAL_PARTITION_CREATE")
                return {
                    "action": "CREATE_PROVISIONAL",
                    "target_id": prov_partition_id,
                    "durable": True,
                    "rule": "RULE_2_STRUCTURAL_PARTITION_CREATE",
                }

        # ---------------------------------------------------------------------
        # Rule 3: Explicit Registered Parenthetical / Identity Evidence
        # (Searches both mention and surrounding context for registered parentheticals)
        # ---------------------------------------------------------------------
        parentheticals = self.extract_parentheticals(mention) + self.extract_parentheticals(context)
        for p in parentheticals:
            p_norm = normalize_alias(p)
            for reg_id, reg_data in self.durable_registry.items():
                canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
                aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
                if p_norm == canon_norm or p_norm in aliases_norm:
                    edge = {
                        "doc_id": doc_id,
                        "source_id": source_id,
                        "mention": mention,
                        "target_id": reg_id,
                        "action": "LINK",
                        "rule": "RULE_3_PARENTHETICAL_IDENTITY_LINK",
                        "timestamp": time.time(),
                    }
                    self.provenance_edges.append(edge)
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "LINK", "target": reg_id, "durable": True}
                    )
                    self._resolve_open_hypotheses(doc_id, mention, "LINK", reg_id, "RULE_3_PARENTHETICAL_IDENTITY_LINK")
                    return {
                        "action": "LINK",
                        "target_id": reg_id,
                        "durable": True,
                        "rule": "RULE_3_PARENTHETICAL_IDENTITY_LINK",
                    }

        # ---------------------------------------------------------------------
        # Rule 4: Novel Standalone System Commissioning Assertion (Deterministic Existence Authority)
        # ---------------------------------------------------------------------
        unasserted_indicators = [
            "proposal", "pending", "rejected", "mock", "hypothetical",
            "generic", "unspecified", "ephemeral", "simulation",
            "inactive in production", "decommissioning", "decommissioned",
        ]
        is_unasserted = any(contains_literal_phrase(context, ind) for ind in unasserted_indicators)

        commissioning_indicators = [
            "commissioning", "deployment", "active in production",
            "initial provisioning", "allocated",
        ]
        is_commissioned = any(contains_literal_phrase(context, ind) for ind in commissioning_indicators)

        if not is_unasserted and is_commissioned:
            prov_id = f"prov_{mention.lower().replace(' ', '_')}"
            if prov_id in self.durable_registry:
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": prov_id,
                    "action": "LINK",
                    "rule": "RULE_4_NOVEL_SYSTEM_LINK",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                self._resolve_open_hypotheses(doc_id, mention, "LINK", prov_id, "RULE_4_NOVEL_SYSTEM_LINK")
                return {
                    "action": "LINK",
                    "target_id": prov_id,
                    "durable": True,
                    "rule": "RULE_4_NOVEL_SYSTEM_LINK",
                }
            else:
                aliases = [mention]
                for p in parentheticals:
                    if p not in aliases:
                        aliases.append(p)
                self.durable_registry[prov_id] = {
                    "entity_id": prov_id,
                    "canonical_name": mention,
                    "status": "provisional",
                    "parent_entity": None,
                    "aliases": aliases,
                }
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": prov_id,
                    "action": "CREATE_PROVISIONAL",
                    "rule": "RULE_4_NOVEL_SYSTEM_CREATE",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "CREATE_PROVISIONAL", "target": prov_id, "durable": True}
                )
                self._resolve_open_hypotheses(doc_id, mention, "CREATE_PROVISIONAL", prov_id, "RULE_4_NOVEL_SYSTEM_CREATE")
                return {
                    "action": "CREATE_PROVISIONAL",
                    "target_id": prov_id,
                    "durable": True,
                    "rule": "RULE_4_NOVEL_SYSTEM_CREATE",
                }

        # ---------------------------------------------------------------------
        # Rule 5: Fail-Closed Ambiguous / Adversarial Deferral (World-Scoped Hypothesis Ledger)
        # ---------------------------------------------------------------------
        return self._handle_deferral(doc_id, source_id, mention, context, neural_proposal, "RULE_5_FAIL_CLOSED_DEFER")


class EpistemicIngressSessionR3Ablation(EpistemicIngressSessionR3R1):
    """Matched Precedence Ablation Resolver:

    Differs from R3-R1 ONLY at Rule 2 when a mention has (parent + marker) but NO sub-identifier:
    - R3-R1: allows fall-through to Rule 3 parentheticals and Rule 4 novel systems.
    - Matched Ablation: immediately defers without Rule 3 fall-through.
    Valid structural partitions with sub-IDs execute identically to R3-R1.
    Isolates the exact causal effect of the sub-identifier precedence rule.
    """

    def process_mention(
        self,
        doc_id: str,
        source_id: str,
        mention: str,
        context: str,
        neural_proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        norm_mention = normalize_alias(mention)

        # Rule 1: Exact Registered Alias (Identical)
        for reg_id, reg_data in self.durable_registry.items():
            canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
            aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
            if norm_mention == canon_norm or norm_mention in aliases_norm:
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": reg_id,
                    "action": "LINK",
                    "rule": "RULE_1_EXACT_ALIAS_MATCH",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "LINK", "target": reg_id, "durable": True}
                )
                self._resolve_open_hypotheses(doc_id, mention, "LINK", reg_id, "RULE_1_EXACT_ALIAS_MATCH")
                return {"action": "LINK", "target_id": reg_id, "durable": True, "rule": "RULE_1_EXACT_ALIAS_MATCH"}

        # Rule 2: Structural First Refusal check
        grounded_parent_id = None
        for reg_id, reg_data in self.durable_registry.items():
            canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
            aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
            if (canon_norm and canon_norm in norm_mention) or any(a_norm and a_norm in norm_mention for a_norm in aliases_norm):
                grounded_parent_id = reg_id
                break

        found_marker = next((m for m in PARTITION_MARKERS if m in mention.lower()), None)
        sub_id_match = SUB_IDENTIFIER_REGEX.search(mention)

        if grounded_parent_id and found_marker:
            if sub_id_match:
                # Valid sub-ID present -> EXACT SAME structural partition handling as R3-R1
                sub_id = sub_id_match.group(0).strip().lower()
                prov_partition_id = f"prov_{grounded_parent_id}_{found_marker}_{sub_id}"

                if prov_partition_id in self.durable_registry:
                    edge = {
                        "doc_id": doc_id,
                        "source_id": source_id,
                        "mention": mention,
                        "target_id": prov_partition_id,
                        "action": "LINK",
                        "rule": "RULE_2_STRUCTURAL_PARTITION_LINK",
                        "timestamp": time.time(),
                    }
                    self.provenance_edges.append(edge)
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "LINK", "target": prov_partition_id, "durable": True}
                    )
                    self._resolve_open_hypotheses(doc_id, mention, "LINK", prov_partition_id, "RULE_2_STRUCTURAL_PARTITION_LINK")
                    return {"action": "LINK", "target_id": prov_partition_id, "durable": True, "rule": "RULE_2_STRUCTURAL_PARTITION_LINK"}
                else:
                    self.durable_registry[prov_partition_id] = {
                        "entity_id": prov_partition_id,
                        "canonical_name": mention,
                        "status": "provisional",
                        "parent_entity": grounded_parent_id,
                        "aliases": [mention],
                    }
                    edge = {
                        "doc_id": doc_id,
                        "source_id": source_id,
                        "mention": mention,
                        "target_id": prov_partition_id,
                        "action": "CREATE_PROVISIONAL",
                        "rule": "RULE_2_STRUCTURAL_PARTITION_CREATE",
                        "timestamp": time.time(),
                    }
                    self.provenance_edges.append(edge)
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "CREATE_PROVISIONAL", "target": prov_partition_id, "durable": True}
                    )
                    self._resolve_open_hypotheses(doc_id, mention, "CREATE_PROVISIONAL", prov_partition_id, "RULE_2_STRUCTURAL_PARTITION_CREATE")
                    return {"action": "CREATE_PROVISIONAL", "target_id": prov_partition_id, "durable": True, "rule": "RULE_2_STRUCTURAL_PARTITION_CREATE"}
            else:
                # Ablated behavior: Missing sub-ID triggers immediate DEFER without falling through to Rule 3 parentheticals
                return self._handle_deferral(doc_id, source_id, mention, context, neural_proposal, "RULE_2_ABLATED_STRUCTURAL_FIRST_REFUSAL")

        # Fall through to standard Rule 3, Rule 4, Rule 5
        return super().process_mention(doc_id, source_id, mention, context, neural_proposal)


def init_database(db_path: Path):
    """Initializes the relational SQLite database with strict foreign key constraints and seeds base registry once."""
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("""
        CREATE TABLE entities (
            entity_id TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL,
            status TEXT NOT NULL,
            parent_entity TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE aliases (
            alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT NOT NULL,
            alias TEXT NOT NULL,
            UNIQUE(entity_id, alias),
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
        )
    """)
    cur.execute("""
        CREATE TABLE provenance_edges (
            edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id TEXT NOT NULL,
            doc_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            mention TEXT NOT NULL,
            target_id TEXT NOT NULL,
            action TEXT NOT NULL,
            rule TEXT NOT NULL,
            timestamp REAL NOT NULL,
            FOREIGN KEY (target_id) REFERENCES entities(entity_id)
        )
    """)
    cur.execute("""
        CREATE TABLE hypothesis_ledger (
            hypothesis_id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL UNIQUE,
            originating_doc_id TEXT NOT NULL,
            surface_form TEXT NOT NULL,
            candidate_target TEXT,
            status TEXT NOT NULL,
            resolved_target TEXT,
            resolving_doc_id TEXT,
            evidence_history_json TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE execution_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id TEXT NOT NULL,
            doc_id TEXT NOT NULL UNIQUE,
            arm TEXT NOT NULL,
            source_id TEXT NOT NULL,
            mention TEXT NOT NULL,
            context TEXT NOT NULL,
            neural_proposal_json TEXT NOT NULL,
            hybrid_decision_json TEXT NOT NULL,
            durable_hash TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    """)

    # Seed base registry once
    base_registry = get_stage8c_r3_r1_base_registry()
    for eid, edata in base_registry.items():
        cur.execute(
            "INSERT INTO entities (entity_id, canonical_name, status, parent_entity) VALUES (?, ?, ?, ?)",
            (eid, edata["canonical_name"], edata["status"], edata.get("parent_entity")),
        )
        for a in edata.get("aliases", []):
            cur.execute("INSERT OR IGNORE INTO aliases (entity_id, alias) VALUES (?, ?)", (eid, a))

    conn.commit()
    conn.close()


def run_stage8c_r3_r1_benchmark(
    worlds: List[Dict[str, Any]],
    gold_manifest: Dict[str, Any],
    db_path: Path,
    evidence_path: Path,
) -> Dict[str, Any]:
    """Executes the 60 genuinely fresh worlds (120 decisions) across all 4 benchmark arms."""
    print("================================================================================")
    print("RUNNING STAGE 8C-R3-R1 CONFIRMATORY BENCHMARK (CONTRACT-R8-8C-R3-R1)")
    print(f"Model: {MODEL_NAME} via Ollama ({OLLAMA_API_URL})")
    print("================================================================================\n")

    base_registry = get_stage8c_r3_r1_base_registry()
    init_database(db_path)

    if evidence_path.exists():
        evidence_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    total_decisions = 0
    start_time = time.time()

    for w_idx, world in enumerate(worlds, start=1):
        wid = world["world_id"]
        arm = world["arm"]
        session = EpistemicIngressSessionR3R1(base_registry, world_id=wid)

        print(f"[{w_idx:02d}/60] Executing World: {wid} ({arm})...")

        for doc in world["docs"]:
            doc_id = doc["doc_id"]
            src_id = doc["source_id"]
            mention = doc["mention"]
            ctx = doc["context"]

            prompt = format_stage8c_r3_r1_prompt(
                doc_id=doc_id,
                source_id=src_id,
                mention=mention,
                context=ctx,
                durable_registry=session.durable_registry,
            )

            # Query Gemma 3 12B
            neural_proposal = call_gemma_api(prompt)

            # Process mention through hybrid ingress kernel
            decision = session.process_mention(
                doc_id=doc_id,
                source_id=src_id,
                mention=mention,
                context=ctx,
                neural_proposal=neural_proposal,
            )

            durable_hash = session.get_durable_hash()
            total_decisions += 1

            # Log to SQLite execution_records
            cur.execute(
                """INSERT INTO execution_records
                   (world_id, doc_id, arm, source_id, mention, context, neural_proposal_json, hybrid_decision_json, durable_hash, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    wid,
                    doc_id,
                    arm,
                    src_id,
                    mention,
                    ctx,
                    json.dumps(neural_proposal),
                    json.dumps(decision),
                    durable_hash,
                    time.time(),
                ),
            )

            # Log to evidence JSONL
            record = {
                "world_id": wid,
                "arm": arm,
                "doc_id": doc_id,
                "source_id": src_id,
                "mention": mention,
                "context": ctx,
                "neural_proposal": neural_proposal,
                "hybrid_decision": decision,
                "durable_hash": durable_hash,
                "timestamp": time.time(),
            }
            with open(evidence_path, "a", encoding="utf-8") as f_jsonl:
                f_jsonl.write(json.dumps(record) + "\n")

        # Persist newly created session entities
        for eid, edata in session.durable_registry.items():
            cur.execute(
                "INSERT OR REPLACE INTO entities (entity_id, canonical_name, status, parent_entity) VALUES (?, ?, ?, ?)",
                (eid, edata["canonical_name"], edata["status"], edata.get("parent_entity")),
            )
            for a in edata.get("aliases", []):
                cur.execute("INSERT OR IGNORE INTO aliases (entity_id, alias) VALUES (?, ?)", (eid, a))

        # Persist session provenance edges
        for edge in session.provenance_edges:
            cur.execute(
                """INSERT INTO provenance_edges
                   (world_id, doc_id, source_id, mention, target_id, action, rule, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    wid,
                    edge["doc_id"],
                    edge["source_id"],
                    edge["mention"],
                    edge["target_id"],
                    edge["action"],
                    edge.get("rule", "UNKNOWN"),
                    edge.get("timestamp", time.time()),
                ),
            )

        # Persist world hypothesis ledger (at most 1 per world)
        for world_k, hyp in session.hypothesis_ledger.items():
            cur.execute(
                """INSERT OR REPLACE INTO hypothesis_ledger
                   (hypothesis_id, world_id, originating_doc_id, surface_form, candidate_target, status, resolved_target, resolving_doc_id, evidence_history_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    hyp["hypothesis_id"],
                    hyp["world_id"],
                    hyp["originating_doc_id"],
                    hyp["surface_form"],
                    hyp.get("candidate_target"),
                    hyp["status"],
                    hyp.get("resolved_target"),
                    hyp.get("resolving_doc_id"),
                    json.dumps(hyp.get("evidence_history", [])),
                ),
            )

        conn.commit()

    conn.close()
    elapsed = time.time() - start_time
    print(f"\n================================================================================")
    print(f"STAGE 8C-R3-R1 BENCHMARK COMPLETED: {total_decisions} decisions in {elapsed:.2f}s")
    print(f"Evidence JSONL:  {evidence_path.resolve()}")
    print(f"SQLite Registry: {db_path.resolve()}")
    print(f"================================================================================\n")
    return {"total_decisions": total_decisions, "elapsed_seconds": elapsed}


if __name__ == "__main__":
    worlds, gold_manifest = generate_stage8c_r3_r1_worlds(seed=2718281828)
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "r8_stage8c_r3_r1_registry.sqlite"
    evidence_path = data_dir / "r8_stage8c_r3_r1_candidate_evidence.jsonl"
    run_stage8c_r3_r1_benchmark(worlds, gold_manifest, db_path, evidence_path)
