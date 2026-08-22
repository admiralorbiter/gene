"""Confirmatory Benchmark Runner for Stage 8C-R3 (CONTRACT-R8-8C-R3).
Implements the refined precedence rule with deterministic existence authority and full hypothesis lifecycle tracking:
- Rule 1: Exact Registered Alias / Name Match.
- Rule 2: Structural First Refusal (Requires grounded parent AND discriminating sub-identifier).
- Rule 3: Explicit Registered Parenthetical Identity Evidence in Mention/Context.
- Rule 4: Novel Standalone System Commissioning Assertion (Deterministic Existence Authority).
- Rule 5: Non-Resolvable Fail-Closed Deferral (Hypothesis Ledger Creation).
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

PARTITION_MARKERS = ["partition", "blade", "slice", "tray", "socket", "pool", "rack", "enclosure", "lun", "bay"]
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

    def _resolve_open_hypotheses(self, doc_id: str, mention: str, action: str, target_id: str, rule: str):
        """Updates open UNRESOLVED hypotheses in this session when evidence resolves an identity."""
        for hid, hypo in self.hypothesis_ledger.items():
            if hypo.get("status") == "UNRESOLVED":
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
                hypo.setdefault("evidence_history", []).append({
                    "resolving_doc_id": doc_id,
                    "resolving_mention": mention,
                    "rule": rule,
                    "action": action,
                    "target_id": target_id,
                })

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
        unasserted_indicators = ["proposal", "pending", "rejected", "mock", "hypothetical", "generic", "unspecified", "ephemeral", "simulation"]
        ctx_lower = context.lower()
        is_unasserted = any(ind in ctx_lower for ind in unasserted_indicators)

        commissioning_indicators = ["commissioning", "deployment", "active in production", "initial provisioning", "allocated"]
        is_commissioned = any(ind in ctx_lower for ind in commissioning_indicators)

        if not is_unasserted and is_commissioned:
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
        # Rule 5: Fail-Closed Ambiguous / Adversarial Deferral
        # ---------------------------------------------------------------------
        hypo_entry = {
            "hypothesis_id": f"hypo_{doc_id}",
            "doc_id": doc_id,
            "surface_form": mention,
            "candidate_target": neural_proposal.get("target_entity_id"),
            "status": "UNRESOLVED",
            "resolved_target": None,
            "context_excerpt": context[:120],
            "evidence_history": [{"doc_id": doc_id, "mention": mention, "context": context[:120]}],
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
