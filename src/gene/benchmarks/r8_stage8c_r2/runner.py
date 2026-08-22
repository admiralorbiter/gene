"""Confirmatory Benchmark Runner for Stage 8C-R2 (CONTRACT-R8-8C-R2).
Executes 60 fresh sealed worlds (120 sequential decisions) with Ollama Gemma 3 12B.
Enforces:
1. Existence vs Identity Decoupling (Principle A)
2. Grounded Structural Partition Grammar with sub-identifier regex (Principle B)
3. Nullable Hypothesis Candidates & World-Local Uniqueness (Principle C)
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

from gene.benchmarks.r8_stage8c_r2.prompts import format_stage8c_r2_prompt
from gene.benchmarks.r8_stage8c_r2.worlds import (
    generate_stage8c_r2_worlds,
    get_stage8c_r2_base_registry,
)

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:12b"

PARTITION_MARKERS = [
    "partition",
    "shelf",
    "pool",
    "blade",
    "bay",
    "node",
    "unit",
    "subunit",
    "sub-unit",
    "sub unit",
    "core",
    "switch",
    "enclosure",
    "slice",
    "sub-rack",
    "sub rack",
    "tray",
    "socket",
    "pci-e",
    "lun",
    "volume pool",
    "rack",
]

AFFIRMATIVE_EXISTENCE_PHRASES = [
    "initial deployment of",
    "newly installed",
    "standalone system",
    "provisioning notice",
    "commissioned in",
    "hardware deployment",
    "new physical device",
]

EXISTENCE_BLOCKER_PHRASES = [
    "proposed",
    "planned",
    "if deployed",
    "deployment cancelled",
    "virtual replica",
    "testing stub",
    "concept",
    "future",
    "simulation",
]

SUB_IDENTIFIER_REGEX = re.compile(r"(?i)\b(?:[a-z]*\d[a-z0-9_-]*|\d+[a-z0-9_-]*)\b")


def normalize_alias(s: str) -> str:
    """Literal mechanical exact-alias normalizer: lowercase, strip, collapse all punctuation/whitespace/hyphens."""
    s = s.strip().lower()
    s = re.sub(r"[\s\-_,.:;/\\|()\[\]{}`'\"~*!?@#$%^&+=]+", "", s)
    return s


def compute_durable_state_hash(
    durable_registry: Dict[str, Any], provenance_edges: List[Dict[str, Any]]
) -> str:
    """Computes a cryptographic SHA-256 digest covering ALL durable epistemic state:
    - Canonical entities & aliases
    - Provisional entities & aliases
    - Provenance edges & durable links
    Excludes ONLY the ephemeral non-durable hypothesis ledger.
    """
    durable_entities = {k: v for k, v in sorted(durable_registry.items())}
    sorted_edges = sorted(
        provenance_edges,
        key=lambda e: (
            e.get("doc_id", ""),
            e.get("source_id", ""),
            e.get("target_id", ""),
        ),
    )
    payload = {
        "entities": durable_entities,
        "edges": sorted_edges,
    }
    s = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def call_gemma_api(prompt: str) -> Dict[str, Any]:
    """Invokes local Ollama Gemma 3 12B at temperature 0.0."""
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
                "identity_judgment": "AMBIGUOUS",
                "registry_mutation": "DEFER",
                "target_id": None,
                "confidence": 0.0,
                "rationale": f"JSON parse fallback on text: {raw_text[:100]}",
            }


class EpistemicIngressSession:
    def __init__(self, base_registry: Dict[str, Any]):
        self.durable_registry = {k: dict(v) for k, v in base_registry.items()}
        self.provenance_edges: List[Dict[str, Any]] = []
        self.hypothesis_ledger: Dict[str, Any] = {}
        self.mutation_log: List[Dict[str, Any]] = []
        self.provisional_counter: int = 1

    def get_durable_hash(self) -> str:
        return compute_durable_state_hash(self.durable_registry, self.provenance_edges)

    def validate_normalizer_collision_invariant(self) -> bool:
        """Asserts that N(alias) maps 1-to-1 to exactly one entity across all registered names/aliases."""
        alias_map = {}
        for eid, edata in self.durable_registry.items():
            names = [edata.get("canonical_name", "")] + edata.get("aliases", [])
            for n in names:
                norm = normalize_alias(n)
                if norm:
                    if norm in alias_map and alias_map[norm] != eid:
                        return False
                    alias_map[norm] = eid
        return True

    def process_mention(
        self,
        doc_id: str,
        source_id: str,
        mention: str,
        context: str,
        neural_proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        norm_mention = normalize_alias(mention)

        # Pre-execution check: 1-to-1 alias map
        alias_map = {}
        for eid, edata in self.durable_registry.items():
            names = [edata.get("canonical_name", "")] + edata.get("aliases", [])
            for n in names:
                norm = normalize_alias(n)
                if norm:
                    alias_map[norm] = eid

        ctx_lower = context.lower()

        # ---------------------------------------------------------------------
        # Precedence Rule 1: Exact Whole-Mention Registered Identity Match
        # ---------------------------------------------------------------------
        if norm_mention in alias_map:
            matched_id = alias_map[norm_mention]
            edge = {
                "doc_id": doc_id,
                "source_id": source_id,
                "mention": mention,
                "target_id": matched_id,
                "action": "LINK",
                "timestamp": time.time(),
            }
            self.provenance_edges.append(edge)
            decision = {
                "doc_id": doc_id,
                "action": "LINK",
                "target_id": matched_id,
                "durable": True,
                "must_not_link": [],
                "rationale": f"Deterministic Rule 1 (Exact registered alias match -> {matched_id})",
            }
            self.mutation_log.append(decision)
            return decision

        # ---------------------------------------------------------------------
        # Precedence Rule 2: Structural-Form Detection & Partition Parse
        # ---------------------------------------------------------------------
        # Check if mention begins with recognized registered parent stem + structural marker
        matched_parent_id = None
        for eid, edata in self.durable_registry.items():
            parent_names = [edata.get("canonical_name", "")] + edata.get("aliases", [])
            for p_name in parent_names:
                p_norm = normalize_alias(p_name)
                if norm_mention.startswith(p_norm) and norm_mention != p_norm:
                    remainder = mention[len(p_name):].strip()
                    rem_lower = remainder.lower()
                    for marker in PARTITION_MARKERS:
                        if marker in rem_lower:
                            matched_parent_id = eid
                            break
                if matched_parent_id:
                    break
            if matched_parent_id:
                break

        if matched_parent_id:
            # Structural First Refusal: Generic canonical linking strictly prohibited
            # Check for distinct discriminating sub-identifier matching regex (requires at least one digit)
            has_sub_id = bool(SUB_IDENTIFIER_REGEX.search(mention))
            if has_sub_id:
                # Valid grounded structural partition
                prov_id = f"prov_{mention.lower().replace(' ', '_').replace('-', '_')}"
                self.durable_registry[prov_id] = {
                    "canonical_name": mention,
                    "status": "PROVISIONAL",
                    "aliases": [mention],
                    "parent_entity": matched_parent_id,
                }
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": prov_id,
                    "action": "CREATE_PROVISIONAL",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                decision = {
                    "doc_id": doc_id,
                    "action": "CREATE_PROVISIONAL",
                    "target_id": prov_id,
                    "durable": True,
                    "must_not_link": [matched_parent_id],
                    "rationale": f"Deterministic Rule 2 (Grounded structural partition under {matched_parent_id} -> {prov_id})",
                }
                self.mutation_log.append(decision)
                return decision
            else:
                # Missing discriminating sub-identifier (e.g. "Tensor Pod Three Sub-Unit")
                # Transitions directly to UNRESOLVED hypothesis without provisional creation
                if mention not in self.hypothesis_ledger:
                    self.hypothesis_ledger[mention] = {
                        "surface_form": mention,
                        "candidate_target": None,
                        "status": "UNRESOLVED",
                        "evidence": [],
                    }
                self.hypothesis_ledger[mention]["evidence"].append({
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "context": context,
                })
                decision = {
                    "doc_id": doc_id,
                    "action": "DEFER",
                    "target_id": None,
                    "durable": False,
                    "must_not_link": [],
                    "rationale": f"Deterministic Rule 2 (Ungrounded structural partition lacking discriminating sub-ID -> Defer)",
                }
                self.mutation_log.append(decision)
                return decision

        # ---------------------------------------------------------------------
        # Precedence Rule 3: Explicit Parenthetical Corroboration (Non-Structural)
        # ---------------------------------------------------------------------
        paren_match = re.match(r"^(.+?)\s*\((.+?)\)$", mention.strip())
        if paren_match:
            surface_stem = paren_match.group(1).strip()
            inner_ident = paren_match.group(2).strip()
            norm_inner = normalize_alias(inner_ident)

            # Case 3A: Inner identifier matches registered entity
            if norm_inner in alias_map:
                matched_id = alias_map[norm_inner]
                # If an unresolved hypothesis exists for surface_stem, mark resolved
                if surface_stem in self.hypothesis_ledger:
                    self.hypothesis_ledger[surface_stem]["status"] = "RESOLVED"
                    self.hypothesis_ledger[surface_stem]["resolved_target"] = matched_id

                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": matched_id,
                    "action": "LINK",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                decision = {
                    "doc_id": doc_id,
                    "action": "LINK",
                    "target_id": matched_id,
                    "durable": True,
                    "must_not_link": [],
                    "rationale": f"Deterministic Rule 3 (Parenthetical corroboration -> {matched_id})",
                }
                self.mutation_log.append(decision)
                return decision

            # Case 3B: Inner identifier matches existing hypothesis surface form
            norm_surface = normalize_alias(surface_stem)
            if norm_surface in alias_map:
                matched_id = alias_map[norm_surface]
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": matched_id,
                    "action": "LINK",
                    "timestamp": time.time(),
                }
                self.provenance_edges.append(edge)
                decision = {
                    "doc_id": doc_id,
                    "action": "LINK",
                    "target_id": matched_id,
                    "durable": True,
                    "must_not_link": [],
                    "rationale": f"Deterministic Rule 3 (Surface stem match with parenthetical -> {matched_id})",
                }
                self.mutation_log.append(decision)
                return decision

        # ---------------------------------------------------------------------
        # Precedence Rule 4: Standalone Existence Parse (Principle A Decoupling)
        # ---------------------------------------------------------------------
        has_affirmative = any(phrase in ctx_lower for phrase in AFFIRMATIVE_EXISTENCE_PHRASES)
        has_blocker = any(blocker in ctx_lower for blocker in EXISTENCE_BLOCKER_PHRASES)

        if has_affirmative and not has_blocker:
            prov_id = f"prov_{mention.lower().replace(' ', '_')}"
            self.durable_registry[prov_id] = {
                "canonical_name": mention,
                "status": "PROVISIONAL",
                "aliases": [mention],
            }
            edge = {
                "doc_id": doc_id,
                "source_id": source_id,
                "mention": mention,
                "target_id": prov_id,
                "action": "CREATE_PROVISIONAL",
                "timestamp": time.time(),
            }
            self.provenance_edges.append(edge)
            decision = {
                "doc_id": doc_id,
                "action": "CREATE_PROVISIONAL",
                "target_id": prov_id,
                "durable": True,
                "must_not_link": [],
                "rationale": f"Deterministic Rule 4 (Standalone existence established -> {prov_id})",
            }
            self.mutation_log.append(decision)
            return decision

        # ---------------------------------------------------------------------
        # Precedence Rule 5: Unresolved Hypothesis Ledger & Deferral
        # ---------------------------------------------------------------------
        cand_target = neural_proposal.get("target_id")
        # World-local uniqueness: update existing record if surface_form already present
        if mention not in self.hypothesis_ledger:
            self.hypothesis_ledger[mention] = {
                "surface_form": mention,
                "candidate_target": cand_target,
                "status": "UNRESOLVED",
                "evidence": [],
            }
        else:
            if cand_target and not self.hypothesis_ledger[mention].get("candidate_target"):
                self.hypothesis_ledger[mention]["candidate_target"] = cand_target

        self.hypothesis_ledger[mention]["evidence"].append({
            "doc_id": doc_id,
            "source_id": source_id,
            "context": context,
        })

        decision = {
            "doc_id": doc_id,
            "action": "DEFER",
            "target_id": None,
            "durable": False,
            "must_not_link": [],
            "rationale": f"Deterministic Rule 5 (Unresolved hypothesis ledger -> Defer)",
        }
        self.mutation_log.append(decision)
        return decision


def init_database(db_path: Path):
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
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
            timestamp REAL NOT NULL,
            FOREIGN KEY (target_id) REFERENCES entities(entity_id)
        )
    """)
    cur.execute("""
        CREATE TABLE hypothesis_ledger (
            hypothesis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id TEXT NOT NULL,
            surface_form TEXT NOT NULL,
            candidate_target TEXT,
            status TEXT NOT NULL,
            evidence_json TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE execution_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id TEXT NOT NULL,
            doc_id TEXT NOT NULL,
            neural_proposal_json TEXT NOT NULL,
            hybrid_decision_json TEXT NOT NULL,
            durable_hash TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def run_stage8c_r2_benchmark():
    print("================================================================================")
    print("RUNNING STAGE 8C-R2 CONFIRMATORY BENCHMARK (CONTRACT-R8-8C-R2)")
    print("Model: Gemma 3 12B Instruct (Q4_K_M) via Ollama")
    print("================================================================================\n")

    base_registry = get_stage8c_r2_base_registry()
    worlds, gold_manifest = generate_stage8c_r2_worlds()

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    gold_manifest_path = data_dir / "r8_stage8c_r2_gold_manifest.json"
    gold_manifest_path.write_text(json.dumps(gold_manifest, indent=2), encoding="utf-8")

    db_path = data_dir / "r8_stage8c_r2_registry.sqlite"
    init_database(db_path)

    jsonl_path = data_dir / "r8_stage8c_r2_candidate_evidence.jsonl"
    if jsonl_path.exists():
        jsonl_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    total_decisions = 0
    start_time = time.time()

    for w_idx, world in enumerate(worlds, start=1):
        wid = world["world_id"]
        arm = world["arm"]
        session = EpistemicIngressSession(base_registry)

        # Pre-seed base registry in DB
        for eid, edata in session.durable_registry.items():
            cur.execute(
                "INSERT OR IGNORE INTO entities (entity_id, canonical_name, status, parent_entity) VALUES (?, ?, ?, ?)",
                (eid, edata["canonical_name"], edata["status"], edata.get("parent_entity")),
            )
            for a in edata.get("aliases", []):
                cur.execute("INSERT INTO aliases (entity_id, alias) VALUES (?, ?)", (eid, a))

        print(f"[{w_idx:02d}/60] Executing World: {wid} ({arm})...")

        for doc in world["documents"]:
            doc_id = doc["doc_id"]
            src_id = doc["source_id"]
            mention = doc["mention"]
            ctx = doc["context"]

            # 1. Format prompt with current durable registry
            reg_view = {
                k: {
                    "name": v["canonical_name"],
                    "status": v["status"],
                    "aliases": v.get("aliases", []),
                }
                for k, v in session.durable_registry.items()
            }
            prompt = format_stage8c_r2_prompt(
                registry_json=json.dumps(reg_view, indent=2),
                doc_id=doc_id,
                source_id=src_id,
                mention_text=mention,
                narrative_context=ctx,
            )

            # 2. Query Gemma 3 12B
            neural_proposal = call_gemma_api(prompt)

            # 3. Hybrid Resolver Decision
            decision = session.process_mention(
                doc_id=doc_id,
                source_id=src_id,
                mention=mention,
                context=ctx,
                neural_proposal=neural_proposal,
            )

            durable_hash = session.get_durable_hash()
            total_decisions += 1

            # Log to SQLite
            cur.execute(
                """INSERT INTO execution_records
                   (world_id, doc_id, neural_proposal_json, hybrid_decision_json, durable_hash, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    wid,
                    doc_id,
                    json.dumps(neural_proposal),
                    json.dumps(decision),
                    durable_hash,
                    time.time(),
                ),
            )

            # Log to JSONL
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
            with open(jsonl_path, "a", encoding="utf-8") as f_jsonl:
                f_jsonl.write(json.dumps(record) + "\n")

        # Persist session entities and edges
        for eid, edata in session.durable_registry.items():
            cur.execute(
                "INSERT OR REPLACE INTO entities (entity_id, canonical_name, status, parent_entity) VALUES (?, ?, ?, ?)",
                (eid, edata["canonical_name"], edata["status"], edata.get("parent_entity")),
            )
        for edge in session.provenance_edges:
            cur.execute(
                """INSERT INTO provenance_edges
                   (world_id, doc_id, source_id, mention, target_id, action, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    wid,
                    edge["doc_id"],
                    edge["source_id"],
                    edge["mention"],
                    edge["target_id"],
                    edge["action"],
                    edge["timestamp"],
                ),
            )
        for s_form, hyp in session.hypothesis_ledger.items():
            cur.execute(
                """INSERT INTO hypothesis_ledger
                   (world_id, surface_form, candidate_target, status, evidence_json)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    wid,
                    s_form,
                    hyp["candidate_target"],
                    hyp["status"],
                    json.dumps(hyp["evidence"]),
                ),
            )
        conn.commit()

    conn.close()
    elapsed = time.time() - start_time
    print(f"\n================================================================================")
    print(f"BENCHMARK RUN COMPLETED: {total_decisions} decisions executed in {elapsed:.2f}s")
    print(f"Candidate Evidence: {jsonl_path.resolve()}")
    print(f"SQLite Registry:    {db_path.resolve()}")
    print(f"================================================================================\n")


if __name__ == "__main__":
    run_stage8c_r2_benchmark()
