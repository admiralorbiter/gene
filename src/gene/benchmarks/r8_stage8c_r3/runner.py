"""Confirmatory Benchmark Runner for Stage 8C-R3 (CONTRACT-R8-8C-R3).
Implements the refined precedence rule:
- Rule 1: Exact Registered Alias / Name Match.
- Rule 2: Structural First Refusal (Requires grounded parent AND discriminating sub-identifier).
- Rule 3: Explicit Registered Parenthetical Identity Evidence in Mention/Context.
- Rule 4: Novel Standalone System Commissioning Assertion.
- Rule 5: Non-Resolvable Fail-Closed Deferral.
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

from gene.benchmarks.r8_stage8c_r3.prompts import (
    STAGE8C_R3_SYSTEM_PROMPT,
    format_stage8c_r3_prompt,
)
from gene.benchmarks.r8_stage8c_r3.worlds import (
    generate_stage8c_r3_worlds,
    get_stage8c_r3_base_registry,
)

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:12b"

PARTITION_MARKERS = ["partition", "blade", "slice", "tray", "socket", "pool", "rack", "enclosure", "lun"]
SUB_IDENTIFIER_REGEX = re.compile(r"(?:\b|\s)(?:[0-9]+|[a-d])\b", re.IGNORECASE)


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


class EpistemicIngressSessionR3:
    def __init__(self, base_registry: Dict[str, Any]):
        self.durable_registry = {k: dict(v) for k, v in base_registry.items()}
        self.provenance_edges: List[Dict[str, Any]] = []
        self.hypothesis_ledger: Dict[str, Any] = {}
        self.mutation_log: List[Dict[str, Any]] = []

    def get_durable_hash(self) -> str:
        return compute_durable_state_hash(self.durable_registry, self.provenance_edges)

    def extract_parentheticals(self, text: str) -> List[str]:
        return [m.strip() for m in re.findall(r"\(([^)]+)\)", text) if m.strip()]

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
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "LINK", "target": reg_id, "durable": True}
                )
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

            # Check if this exact structural partition is already registered
            if prov_partition_id in self.durable_registry:
                edge = {
                    "doc_id": doc_id,
                    "source_id": source_id,
                    "mention": mention,
                    "target_id": prov_partition_id,
                    "action": "LINK",
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "LINK", "target": prov_partition_id, "durable": True}
                )
                return {
                    "action": "LINK",
                    "target_id": prov_partition_id,
                    "durable": True,
                    "rule": "RULE_2_STRUCTURAL_PARTITION_LINK",
                }
            else:
                # Create provisional partition
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
                }
                self.provenance_edges.append(edge)
                self.mutation_log.append(
                    {"doc_id": doc_id, "action": "CREATE_PROVISIONAL", "target": prov_partition_id, "durable": True}
                )
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
                    }
                    self.provenance_edges.append(edge)
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "LINK", "target": reg_id, "durable": True}
                    )
                    return {
                        "action": "LINK",
                        "target_id": reg_id,
                        "durable": True,
                        "rule": "RULE_3_PARENTHETICAL_IDENTITY_LINK",
                    }

        # ---------------------------------------------------------------------
        # Rule 4: Novel Standalone System Commissioning Assertion
        # ---------------------------------------------------------------------
        unasserted_indicators = ["proposal", "pending", "rejected", "mock", "hypothetical", "generic", "unspecified", "ephemeral", "simulation"]
        ctx_lower = context.lower()
        is_unasserted = any(ind in ctx_lower for ind in unasserted_indicators)

        commissioning_indicators = ["commissioning", "deployment", "active in production", "initial provisioning", "allocated"]
        is_commissioned = any(ind in ctx_lower for ind in commissioning_indicators)

        if not is_unasserted and is_commissioned:
            cand_action = neural_proposal.get("candidate_action")
            if cand_action in ("CREATE_PROVISIONAL", "LINK_EXISTING"):
                prov_id = f"prov_{mention.lower().replace(' ', '_')}"
                if prov_id in self.durable_registry:
                    edge = {
                        "doc_id": doc_id,
                        "source_id": source_id,
                        "mention": mention,
                        "target_id": prov_id,
                        "action": "LINK",
                    }
                    self.provenance_edges.append(edge)
                    return {
                        "action": "LINK",
                        "target_id": prov_id,
                        "durable": True,
                        "rule": "RULE_4_NOVEL_SYSTEM_LINK",
                    }
                else:
                    # Register provisional system
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
                    }
                    self.provenance_edges.append(edge)
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "CREATE_PROVISIONAL", "target": prov_id, "durable": True}
                    )
                    return {
                        "action": "CREATE_PROVISIONAL",
                        "target_id": prov_id,
                        "durable": True,
                        "rule": "RULE_4_NOVEL_SYSTEM_CREATE",
                    }

        # ---------------------------------------------------------------------
        # Rule 5: Fail-Closed Ambiguous / Adversarial Deferral
        # ---------------------------------------------------------------------
        hypo_entry = {
            "surface_form": mention,
            "candidate_target": neural_proposal.get("target_entity_id"),
            "status": "deferred",
            "context_excerpt": context[:120],
        }
        self.hypothesis_ledger[doc_id] = hypo_entry
        self.mutation_log.append(
            {"doc_id": doc_id, "action": "DEFER", "target": None, "durable": False}
        )
        return {
            "action": "DEFER",
            "target_id": None,
            "durable": False,
            "rule": "RULE_5_FAIL_CLOSED_DEFER",
        }
