"""Confirmatory Benchmark Runner for Stage 8C-R1 (CONTRACT-R8-8C-R1).
Executes 60 fresh sealed worlds (120 sequential decisions) with Ollama Gemma 3 12B.
Enforces literal mechanical exact-alias normalization, collision invariants, observable hypothesis isolation,
whole-field corroboration, symmetric novelty assertions, and multi-source evidence disconfirmation.
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

from gene.benchmarks.r8_stage8c_r1.prompts import format_stage8c_r1_prompt
from gene.benchmarks.r8_stage8c_r1.worlds import (
    generate_stage8c_r1_worlds,
    get_stage8c_r1_base_registry,
)

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:12b"

PARTITION_KEYWORDS = [
    "partition",
    "blade",
    "enclosure",
    "slice",
    "sub-rack",
    "sub-unit",
    "sub unit",
    "tray",
    "shelf",
    "socket",
    "pci-e",
    "lun",
    "volume pool",
    "rack",
]


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
                    if norm in alias_map and alias_map[norm] != eid:
                        # Collision detected -> fail closed to ambiguous defer
                        self.mutation_log.append(
                            {"doc_id": doc_id, "action": "AMBIGUOUS_DEFER", "durable": False}
                        )
                        return {
                            "action": "DEFER",
                            "target_id": None,
                            "durable": False,
                            "guardrail": "NORMALIZER_COLLISION_AMBIGUOUS_DEFER",
                        }
                    alias_map[norm] = eid

        # 1. Exact Registered Alias Match (Whole-field match under N(s))
        for reg_id, reg_data in self.durable_registry.items():
            canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
            aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
            if norm_mention == canon_norm or norm_mention in aliases_norm:
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "target_id": reg_id,
                    "type": "EXACT_ALIAS_LINK",
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "LINK", "target": reg_id, "durable": True}
                )
                return {
                    "action": "LINK",
                    "target_id": reg_id,
                    "durable": True,
                    "guardrail": "EXACT_ALIAS_PRESERVED",
                }

        # 1b. Neural Provisional Link: if neural model proposes linking to an existing provisional entity in this world
        proposed_target = neural_proposal.get("target_id")
        if (
            proposed_target
            and proposed_target in self.durable_registry
            and self.durable_registry[proposed_target].get("status") == "PROVISIONAL"
            and neural_proposal.get("registry_mutation") == "LINK"
        ):
            edge = {
                "doc_id": doc_id,
                "source_id": source_id,
                "target_id": proposed_target,
                "type": "PROVISIONAL_ENTITY_REUSE_LINK",
            }
            self.provenance_edges.append(edge)
            self.durable_registry[proposed_target]["aliases"].append(mention)
            self.mutation_log.append(
                {"doc_id": doc_id, "action": "LINK", "target": proposed_target, "durable": True}
            )
            return {
                "action": "LINK",
                "target_id": proposed_target,
                "durable": True,
                "guardrail": "PROVISIONAL_ENTITY_REUSE_LINK",
            }

        # 1c. Context Parenthetical Match for Provisional Entities
        ctx_match = re.search(r"\(([^)]+)\)", context)
        if ctx_match:
            norm_ctx_field = normalize_alias(ctx_match.group(1))
            for prov_id, prov_data in self.durable_registry.items():
                if prov_data.get("status") == "PROVISIONAL":
                    prov_canon = normalize_alias(prov_data.get("canonical_name", ""))
                    if norm_ctx_field == prov_canon:
                        edge = {
                            "doc_id": doc_id,
                            "source_id": source_id,
                            "target_id": prov_id,
                            "type": "PROVISIONAL_ENTITY_CONTEXT_LINK",
                        }
                        self.provenance_edges.append(edge)
                        self.durable_registry[prov_id]["aliases"].append(mention)
                        self.mutation_log.append(
                            {"doc_id": doc_id, "action": "LINK", "target": prov_id, "durable": True}
                        )
                        return {
                            "action": "LINK",
                            "target_id": prov_id,
                            "durable": True,
                            "guardrail": "PROVISIONAL_ENTITY_CONTEXT_LINK",
                        }

        # 2. Partition Syntax Blocking & Tracking
        is_partition = any(kw in mention.lower() for kw in PARTITION_KEYWORDS)
        if is_partition:
            # Check if partition already exists in provisional entities
            for prov_id, prov_data in self.durable_registry.items():
                if prov_data.get("status") == "PROVISIONAL":
                    prov_canon = normalize_alias(prov_data.get("canonical_name", ""))
                    prov_aliases = [normalize_alias(a) for a in prov_data.get("aliases", [])]
                    if norm_mention == prov_canon or norm_mention in prov_aliases:
                        edge = {
                            "doc_id": doc_id,
                            "source_id": source_id,
                            "target_id": prov_id,
                            "type": "PROVISIONAL_PARTITION_LINK",
                        }
                        self.provenance_edges.append(edge)
                        self.mutation_log.append(
                            {"doc_id": doc_id, "action": "LINK", "target": prov_id, "durable": True}
                        )
                        return {
                            "action": "LINK",
                            "target_id": prov_id,
                            "durable": True,
                            "guardrail": "PROVISIONAL_PARTITION_REUSE_LINK",
                        }

            # Create new provisional partition entity
            prov_id = f"prov_partition_{self.provisional_counter}"
            self.provisional_counter += 1
            self.durable_registry[prov_id] = {
                "canonical_name": mention,
                "status": "PROVISIONAL",
                "aliases": [mention],
            }
            edge = {
                "doc_id": doc_id,
                "source_id": source_id,
                "target_id": prov_id,
                "type": "NEW_PROVISIONAL_PARTITION_CREATE",
            }
            self.provenance_edges.append(edge)
            self.mutation_log.append(
                {"doc_id": doc_id, "action": "CREATE_PROVISIONAL", "target": prov_id, "durable": True}
            )
            return {
                "action": "CREATE_PROVISIONAL",
                "target_id": prov_id,
                "durable": True,
                "guardrail": "PARTITION_SYNTAX_PROVISIONAL_CREATED",
            }

        # 3. Explicit Whole-Field Identifying Corroboration: "Surface Form (Explicit Identifier)"
        corroboration_match = re.search(r"\(([^)]+)\)", mention)
        if not corroboration_match and len(self.hypothesis_ledger) > 0:
            corroboration_match = re.search(r"\(([^)]+)\)", context)

        if corroboration_match and (len(self.hypothesis_ledger) > 0 or "(" in mention):
            extracted_field = corroboration_match.group(1).strip()
            norm_extracted = normalize_alias(extracted_field)
            surface_prefix = mention.split("(")[0].strip()
            norm_prefix = normalize_alias(surface_prefix)

            # Match parent surface form against active hypothesis
            hyp_key = None
            for k, hyp in self.hypothesis_ledger.items():
                if hyp["status"] == "UNRESOLVED" and normalize_alias(hyp["surface_form"]) == norm_prefix:
                    hyp_key = k
                    break

            # Whole-field match against durable registered entities (canonical or provisional)
            resolved_target = None
            for reg_id, reg_data in self.durable_registry.items():
                canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
                aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
                if norm_extracted == canon_norm or norm_extracted in aliases_norm or norm_mention == canon_norm or norm_mention in aliases_norm:
                    resolved_target = reg_id
                    break

            if resolved_target:
                if hyp_key:
                    orig_cand = self.hypothesis_ledger[hyp_key]["candidate_target"]
                    if resolved_target == orig_cand:
                        # Case A: Confirmation
                        self.hypothesis_ledger[hyp_key]["status"] = "CONFIRMED_RESOLVED"
                        self.hypothesis_ledger[hyp_key]["durable_target"] = resolved_target
                        edge = {
                            "doc_id": doc_id,
                            "source_id": source_id,
                            "target_id": resolved_target,
                            "type": "CONFIRMED_HYPOTHESIS_LINK",
                        }
                        self.provenance_edges.append(edge)
                        self.mutation_log.append(
                            {"doc_id": doc_id, "action": "LINK", "target": resolved_target, "durable": True}
                        )
                        return {
                            "action": "LINK",
                            "target_id": resolved_target,
                            "durable": True,
                            "guardrail": f"HYPOTHESIS_CONFIRMED_RESOLVE (from {hyp_key})",
                        }
                    else:
                        # Case B: Contradiction -> Retarget to Existing Canonical
                        self.hypothesis_ledger[hyp_key]["status"] = "CONTRADICTED_DISCARDED"
                        self.hypothesis_ledger[hyp_key]["retargeted_to"] = resolved_target
                        edge = {
                            "doc_id": doc_id,
                            "source_id": source_id,
                            "target_id": resolved_target,
                            "type": "RETARGETED_HYPOTHESIS_LINK",
                        }
                        self.provenance_edges.append(edge)
                        self.mutation_log.append(
                            {"doc_id": doc_id, "action": "LINK", "target": resolved_target, "durable": True}
                        )
                        return {
                            "action": "LINK",
                            "target_id": resolved_target,
                            "durable": True,
                            "guardrail": f"HYPOTHESIS_CONTRADICTED_RETARGET_EXISTING (orig: {orig_cand} -> new: {resolved_target})",
                        }
                else:
                    edge = {
                        "doc_id": doc_id,
                        "source_id": source_id,
                        "target_id": resolved_target,
                        "type": "DIRECT_CORROBORATION_LINK",
                    }
                    self.provenance_edges.append(edge)
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "LINK", "target": resolved_target, "durable": True}
                    )
                    return {
                        "action": "LINK",
                        "target_id": resolved_target,
                        "durable": True,
                        "guardrail": "EXPLICIT_CORROBORATION_DIRECT_LINK",
                    }
            else:
                # Case C: Contradiction -> Symmetric Novelty Assertion Check
                # Requires: unmatched identifier + explicit document novelty text + neural NOVEL
                is_explicit_novelty_text = any(
                    nw in context.lower()
                    for nw in [
                        "newly installed",
                        "newly designated",
                        "new unit",
                        "standalone system",
                        "new hardware",
                    ]
                )
                neural_is_novel = neural_proposal.get("identity_judgment") == "NOVEL" or neural_proposal.get("registry_mutation") == "CREATE_PROVISIONAL"

                if is_explicit_novelty_text and neural_is_novel and norm_extracted:
                    prov_id = f"prov_{norm_extracted[:15]}"
                    self.provisional_counter += 1
                    self.durable_registry[prov_id] = {
                        "canonical_name": extracted_field,
                        "status": "PROVISIONAL",
                        "aliases": [surface_prefix],
                    }
                    if hyp_key:
                        orig_cand = self.hypothesis_ledger[hyp_key]["candidate_target"]
                        self.hypothesis_ledger[hyp_key]["status"] = "CONTRADICTED_DISCARDED"
                        self.hypothesis_ledger[hyp_key]["retargeted_to"] = prov_id
                    edge = {
                        "doc_id": doc_id,
                        "source_id": source_id,
                        "target_id": prov_id,
                        "type": "RETARGETED_NOVEL_PROVISIONAL_LINK",
                    }
                    self.provenance_edges.append(edge)
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "CREATE_PROVISIONAL", "target": prov_id, "durable": True}
                    )
                    return {
                        "action": "CREATE_PROVISIONAL",
                        "target_id": prov_id,
                        "durable": True,
                        "guardrail": f"HYPOTHESIS_CONTRADICTED_RETARGET_NOVEL (target: {prov_id})",
                    }
                else:
                    # Unmatched parenthetical without explicit novelty assertion -> fail closed
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "DEFER", "durable": False}
                    )
                    return {
                        "action": "DEFER",
                        "target_id": None,
                        "durable": False,
                        "guardrail": "UNMATCHED_PARENTHETICAL_LACKS_NOVELTY_ASSERTION_DEFER",
                    }

        # 4. Repeated Unseen Composite without identifying evidence (Evidence Did Not Arrive)
        for k, hyp in self.hypothesis_ledger.items():
            if hyp["status"] == "UNRESOLVED" and normalize_alias(hyp["surface_form"]) == norm_mention:
                hyp["evidence_sources"].append(source_id)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "DEFER_REPEATED_NO_EVIDENCE", "hyp_id": k, "durable": False}
                )
                return {
                    "action": "DEFER",
                    "hypothesis_id": k,
                    "durable": False,
                    "guardrail": "REPEATED_UNRESOLVED_COMPOSITE_NO_EVIDENCE",
                }

        # 5. Unseen composite with known stem -> Emit Initial Non-Durable Identity Hypothesis
        proposed_target = neural_proposal.get("target_id")
        has_known_stem = any(
            normalize_alias(edata.get("canonical_name", "")) in norm_mention
            or any(normalize_alias(a) in norm_mention for a in edata.get("aliases", []))
            for edata in self.durable_registry.values()
        )
        if proposed_target and proposed_target in self.durable_registry and has_known_stem:
            hyp_id = f"hyp_{doc_id}_{norm_mention[:10]}"
            self.hypothesis_ledger[hyp_id] = {
                "hypothesis_id": hyp_id,
                "surface_form": mention,
                "candidate_target": proposed_target,
                "status": "UNRESOLVED",
                "evidence_sources": [source_id],
                "durable_mutation": None,
            }
            self.mutation_log.append(
                {"doc_id": doc_id, "action": "DEFER_HYPOTHESIS", "hyp_id": hyp_id, "durable": False}
            )
            return {
                "action": "DEFER",
                "hypothesis_id": hyp_id,
                "candidate_target": proposed_target,
                "durable": False,
                "guardrail": "NON_DURABLE_HYPOTHESIS_EMITTED",
            }

        # 6. Novel Standalone Entities (Arm 1)
        # Check if mention matches an existing provisional entity created earlier in this world
        for prov_id, prov_data in self.durable_registry.items():
            if prov_data.get("status") == "PROVISIONAL":
                prov_canon = normalize_alias(prov_data.get("canonical_name", ""))
                prov_aliases = [normalize_alias(a) for a in prov_data.get("aliases", [])]
                if norm_mention == prov_canon or norm_mention in prov_aliases:
                    edge = {
                        "doc_id": doc_id,
                        "source_id": source_id,
                        "target_id": prov_id,
                        "type": "PROVISIONAL_ENTITY_REUSE_LINK",
                    }
                    self.provenance_edges.append(edge)
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "LINK", "target": prov_id, "durable": True}
                    )
                    return {
                        "action": "LINK",
                        "target_id": prov_id,
                        "durable": True,
                        "guardrail": "PROVISIONAL_ENTITY_REUSE_LINK",
                    }

        # Check for bare generic tokens
        bare_tokens = [
            "thesystem", "theunit", "thenode", "thecluster", "thearray",
            "primaryhost", "backupnode", "hostunit", "primaryunit"
        ]
        if norm_mention in bare_tokens:
            self.mutation_log.append(
                {"doc_id": doc_id, "action": "DEFER", "target": None, "durable": False}
            )
            return {"action": "DEFER", "target_id": None, "durable": False, "guardrail": "BARE_TOKEN_DEFER"}

        # If neural proposal is NOVEL (Arm 1 Doc 1)
        if neural_proposal.get("identity_judgment") == "NOVEL" or neural_proposal.get("registry_mutation") == "CREATE_PROVISIONAL":
            prov_id = f"prov_{norm_mention[:15]}"
            self.durable_registry[prov_id] = {
                "canonical_name": mention,
                "status": "PROVISIONAL",
                "aliases": [mention],
            }
            edge = {
                "doc_id": doc_id,
                "source_id": source_id,
                "target_id": prov_id,
                "type": "NEW_PROVISIONAL_ENTITY_CREATE",
            }
            self.provenance_edges.append(edge)
            self.mutation_log.append(
                {"doc_id": doc_id, "action": "CREATE_PROVISIONAL", "target": prov_id, "durable": True}
            )
            return {
                "action": "CREATE_PROVISIONAL",
                "target_id": prov_id,
                "durable": True,
                "guardrail": "NOVEL_STANDALONE_PROVISIONAL_CREATED",
            }

        # Default Defer
        self.mutation_log.append(
            {"doc_id": doc_id, "action": "DEFER", "target": None, "durable": False}
        )
        return {"action": "DEFER", "target_id": None, "durable": False, "guardrail": "BARE_TOKEN_DEFER"}


def build_sqlite_archive(
    db_path: Path,
    durable_registry: Dict[str, Any],
    provenance_edges: List[Dict[str, Any]],
    hypothesis_ledger: Dict[str, Any],
    mutation_log: List[Dict[str, Any]],
):
    """Builds a verified SQLite archive recording durable state and hypothesis records."""
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE entities (
            entity_id TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE aliases (
            alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT NOT NULL,
            alias_text TEXT NOT NULL,
            normalized_alias TEXT NOT NULL,
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE provenance_edges (
            edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            edge_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_id) REFERENCES entities(entity_id)
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE hypothesis_records (
            hypothesis_id TEXT PRIMARY KEY,
            surface_form TEXT NOT NULL,
            candidate_target TEXT NOT NULL,
            status TEXT NOT NULL,
            evidence_sources TEXT NOT NULL,
            durable_target TEXT,
            retargeted_to TEXT
        )
    """
    )

    for eid, edata in durable_registry.items():
        cur.execute(
            "INSERT INTO entities (entity_id, canonical_name, status) VALUES (?, ?, ?)",
            (eid, edata.get("canonical_name", ""), edata.get("status", "PROVISIONAL")),
        )
        for a in edata.get("aliases", []):
            cur.execute(
                "INSERT INTO aliases (entity_id, alias_text, normalized_alias) VALUES (?, ?, ?)",
                (eid, a, normalize_alias(a)),
            )

    for edge in provenance_edges:
        cur.execute(
            "INSERT INTO provenance_edges (doc_id, source_id, target_id, edge_type) VALUES (?, ?, ?, ?)",
            (
                edge.get("doc_id", ""),
                edge.get("source_id", ""),
                edge.get("target_id", ""),
                edge.get("type", ""),
            ),
        )

    for hid, hdata in hypothesis_ledger.items():
        cur.execute(
            """
            INSERT INTO hypothesis_records 
            (hypothesis_id, surface_form, candidate_target, status, evidence_sources, durable_target, retargeted_to)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hid,
                hdata.get("surface_form", ""),
                hdata.get("candidate_target", ""),
                hdata.get("status", ""),
                json.dumps(hdata.get("evidence_sources", [])),
                hdata.get("durable_target"),
                hdata.get("retargeted_to"),
            ),
        )

    conn.commit()
    conn.close()


def run_stage8c_r1_benchmark():
    print("================================================================================")
    print("STARTING STAGE 8C-R1 CONFIRMATORY BENCHMARK: 60 Worlds (120 Decisions)")
    print(f"Model: {MODEL_NAME} | Endpoint: {OLLAMA_API_URL}")
    print("================================================================================")

    worlds, gold_manifest = generate_stage8c_r1_worlds()
    base_reg = get_stage8c_r1_base_registry()

    all_durable_registries = {}
    all_provenance_edges = []
    all_hypothesis_records = {}
    all_mutation_logs = []

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = data_dir / "r8_stage8c_r1_candidate_evidence.jsonl"
    summary_path = data_dir / "r8_stage8c_r1_summary.json"
    sqlite_path = data_dir / "r8_stage8c_r1_registry.sqlite"
    manifest_path = data_dir / "r8_stage8c_r1_evidence_manifest.json"

    raw_records = []
    start_time = time.time()

    for w_idx, world in enumerate(worlds, start=1):
        wid = world["world_id"]
        arm = world["arm"]
        print(f"\n--- World {w_idx:02d}/60: {wid} [{arm}] ---", flush=True)

        session = EpistemicIngressSession(base_reg)

        for doc in world["documents"]:
            doc_id = doc["doc_id"]
            source_id = doc["source_id"]
            mention = doc["mention"]
            context = doc["context"]

            h_before = session.get_durable_hash()

            reg_json_str = json.dumps(session.durable_registry, indent=2)
            prompt = format_stage8c_r1_prompt(
                reg_json_str, doc_id, source_id, mention, context
            )

            call_start = time.time()
            neural_proposal = call_gemma_api(prompt)
            call_latency = time.time() - call_start

            ingress_result = session.process_mention(
                doc_id, source_id, mention, context, neural_proposal
            )

            h_after = session.get_durable_hash()
            hash_invariant = (h_before == h_after) if not ingress_result.get("durable") else True

            gold = gold_manifest.get(doc_id, {})
            expected_action = gold.get("action")
            expected_target = gold.get("expected_target")

            is_action_correct = ingress_result["action"] == expected_action
            is_target_correct = (
                ingress_result.get("target_id") == expected_target
                if expected_target
                else (ingress_result.get("target_id") is None if expected_action == "DEFER" else True)
            )
            is_hybrid_correct = is_action_correct and is_target_correct

            # Neural proposal accuracy check
            neural_action = neural_proposal.get("registry_mutation")
            neural_target = neural_proposal.get("target_id")
            is_neural_correct = (neural_action == expected_action) and (
                neural_target == expected_target if expected_target else True
            )

            record = {
                "world_id": wid,
                "arm": arm,
                "doc_id": doc_id,
                "source_id": source_id,
                "mention": mention,
                "context": context,
                "prompt": prompt,
                "neural_proposal": neural_proposal,
                "ingress_result": ingress_result,
                "gold": gold,
                "latency_sec": call_latency,
                "durable_hash_before": h_before,
                "durable_hash_after": h_after,
                "hash_invariant": hash_invariant,
                "is_neural_correct": is_neural_correct,
                "is_hybrid_correct": is_hybrid_correct,
            }
            raw_records.append(record)

            print(
                f"  [{doc_id}] '{mention}' -> Neural: {neural_proposal.get('registry_mutation')}:{neural_proposal.get('target_id')} | "
                f"Hybrid: {ingress_result['action']}:{ingress_result.get('target_id')} (Durable: {ingress_result['durable']}) "
                f"[{ingress_result['guardrail']}]",
                flush=True,
            )
        for eid, edata in session.durable_registry.items():
            if eid not in all_durable_registries:
                all_durable_registries[eid] = edata
        all_provenance_edges.extend(session.provenance_edges)
        all_hypothesis_records.update(session.hypothesis_ledger)
        all_mutation_logs.extend(session.mutation_log)

    elapsed_total = time.time() - start_time

    # Persist JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in raw_records:
            f.write(json.dumps(r) + "\n")

    # Build SQLite
    build_sqlite_archive(
        sqlite_path,
        all_durable_registries,
        all_provenance_edges,
        all_hypothesis_records,
        all_mutation_logs,
    )

    # Compute Summary Statistics
    total_calls = len(raw_records)
    neural_correct_count = sum(1 for r in raw_records if r["is_neural_correct"])
    hybrid_correct_count = sum(1 for r in raw_records if r["is_hybrid_correct"])

    # Arm-by-Arm Neural Accuracy
    arm_stats = {}
    for r in raw_records:
        arm = r["arm"]
        if arm not in arm_stats:
            arm_stats[arm] = {"total": 0, "neural_correct": 0, "hybrid_correct": 0}
        arm_stats[arm]["total"] += 1
        if r["is_neural_correct"]:
            arm_stats[arm]["neural_correct"] += 1
        if r["is_hybrid_correct"]:
            arm_stats[arm]["hybrid_correct"] += 1

    summary = {
        "contract_id": "CONTRACT-R8-8C-R1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL_NAME,
        "total_calls": total_calls,
        "elapsed_sec": elapsed_total,
        "neural_accuracy": neural_correct_count / total_calls,
        "hybrid_accuracy": hybrid_correct_count / total_calls,
        "arm_breakdown": arm_stats,
        "hypothesis_ledger_count": len(session.hypothesis_ledger),
        "durable_entity_count": len(session.durable_registry),
        "provenance_edge_count": len(session.provenance_edges),
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Build Evidence Manifest
    manifest = {
        "candidate_id": "CANDIDATE-R8-8C-R1",
        "contract_id": "CONTRACT-R8-8C-R1",
        "model_digest": MODEL_NAME,
        "jsonl_sha256": hashlib.sha256(open(jsonl_path, "rb").read()).hexdigest(),
        "summary_sha256": hashlib.sha256(open(summary_path, "rb").read()).hexdigest(),
        "sqlite_sha256": hashlib.sha256(open(sqlite_path, "rb").read()).hexdigest(),
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n================================================================================")
    print("STAGE 8C-R1 EXECUTION COMPLETED")
    print(f"Total Calls: {total_calls} | Elapsed: {elapsed_total:.2f}s")
    print(f"Overall Neural Proposal Accuracy: {summary['neural_accuracy']*100:.1f}%")
    print(f"Overall Hybrid Ingress Accuracy:   {summary['hybrid_accuracy']*100:.1f}%")
    print("Arm Breakdown:")
    for arm, stats in arm_stats.items():
        print(f"  {arm:<28}: Neural {stats['neural_correct']}/{stats['total']} ({stats['neural_correct']/stats['total']*100:.1f}%) | Hybrid {stats['hybrid_correct']}/{stats['total']} ({stats['hybrid_correct']/stats['total']*100:.1f}%)")
    print("Artifacts Persisted:")
    print(f"  Evidence JSONL:   {jsonl_path}")
    print(f"  Summary JSON:     {summary_path}")
    print(f"  SQLite Archive:   {sqlite_path}")
    print(f"  Manifest:         {manifest_path}")
    print("================================================================================")


if __name__ == "__main__":
    run_stage8c_r1_benchmark()
