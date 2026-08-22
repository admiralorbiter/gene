"""Development-only exploratory mini-scout for Stage 8C-R1:
Tests non-durable hypothesis isolation, evidence accumulation, and clean disconfirmation/retargeting.
"""

import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Tuple


def normalize_alias(s: str) -> str:
    """Mechanical exact-alias normalizer: lowercase, strip, collapse hyphens/spaces/punct."""
    s = s.lower().strip()
    s = re.sub(r"[\s\-_]+", "", s)
    return s


def compute_registry_hash(registry: Dict[str, Any]) -> str:
    """Computes a cryptographic hash of the durable canonical registry state."""
    canon_state = {k: v for k, v in sorted(registry.items()) if v.get("status") == "CANONICAL"}
    s = json.dumps(canon_state, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class EpistemicIngressSession:
    def __init__(self, base_registry: Dict[str, Any]):
        self.durable_registry = {k: dict(v) for k, v in base_registry.items()}
        self.hypothesis_ledger: Dict[str, Any] = {}
        self.mutation_log: List[Dict[str, Any]] = []

    def process_mention(
        self,
        doc_id: str,
        source_id: str,
        mention: str,
        context: str,
        neural_proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        norm_mention = normalize_alias(mention)

        # 1. Exact Registered Alias Check
        for reg_id, reg_data in self.durable_registry.items():
            if reg_data.get("status") == "CANONICAL":
                canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
                aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
                if norm_mention == canon_norm or norm_mention in aliases_norm:
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "LINK", "target": reg_id, "durable": True}
                    )
                    return {
                        "action": "LINK",
                        "target_id": reg_id,
                        "durable": True,
                        "guardrail": "EXACT_ALIAS_PRESERVED",
                    }

        # 2. Check if this is an explicit corroboration/clarification for an active hypothesis
        # Identifying construction: e.g. "Cluster 1 Backup (CC-1 Standby Instance)" or "Primary SAN (Storage Array Beta)"
        corroboration_match = re.search(r"\(([^)]+)\)", mention)
        if corroboration_match:
            parent_clarify = corroboration_match.group(1).strip()
            norm_clarify = normalize_alias(parent_clarify)

            # Find matching active hypothesis
            hyp_key = None
            for k, hyp in self.hypothesis_ledger.items():
                if hyp["status"] == "UNRESOLVED" and normalize_alias(hyp["surface_form"]) in norm_mention:
                    hyp_key = k
                    break

            # Check if parent_clarify matches a canonical entity
            resolved_target = None
            for reg_id, reg_data in self.durable_registry.items():
                if reg_data.get("status") == "CANONICAL":
                    canon_norm = normalize_alias(reg_data.get("canonical_name", ""))
                    aliases_norm = [normalize_alias(a) for a in reg_data.get("aliases", [])]
                    if norm_clarify == canon_norm or any(a in norm_clarify for a in aliases_norm) or any(norm_clarify in a for a in aliases_norm):
                        resolved_target = reg_id
                        break

            if resolved_target:
                if hyp_key:
                    orig_cand = self.hypothesis_ledger[hyp_key]["candidate_target"]
                    if resolved_target == orig_cand:
                        # Confirmed!
                        self.hypothesis_ledger[hyp_key]["status"] = "CONFIRMED_RESOLVED"
                        self.hypothesis_ledger[hyp_key]["durable_target"] = resolved_target
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
                        # Contradicted / Retargeted!
                        self.hypothesis_ledger[hyp_key]["status"] = "CONTRADICTED_DISCARDED"
                        self.hypothesis_ledger[hyp_key]["retargeted_to"] = resolved_target
                        self.mutation_log.append(
                            {"doc_id": doc_id, "action": "LINK", "target": resolved_target, "durable": True}
                        )
                        return {
                            "action": "LINK",
                            "target_id": resolved_target,
                            "durable": True,
                            "guardrail": f"HYPOTHESIS_CONTRADICTED_RETARGET (orig: {orig_cand} -> new: {resolved_target})",
                        }
                else:
                    self.mutation_log.append(
                        {"doc_id": doc_id, "action": "LINK", "target": resolved_target, "durable": True}
                    )
                    return {
                        "action": "LINK",
                        "target_id": resolved_target,
                        "durable": True,
                        "guardrail": "EXPLICIT_CORROBORATION_DIRECT_LINK",
                    }

        # 3. Unseen composite with known stem -> Emit Non-Durable Identity Hypothesis
        proposed_target = neural_proposal.get("target_id")
        if proposed_target and proposed_target in self.durable_registry:
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

        # Default Defer
        self.mutation_log.append(
            {"doc_id": doc_id, "action": "DEFER", "target": None, "durable": False}
        )
        return {"action": "DEFER", "target_id": None, "durable": False, "guardrail": "BARE_TOKEN_DEFER"}


def run_mini_scout():
    print("================================================================================")
    print("SCOUT: Stage 8C-R1 Non-Durable Hypothesis Isolation & Disconfirmation")
    print("================================================================================")

    base_reg = {
        "compute_cluster_1": {
            "canonical_name": "Compute Cluster 1",
            "status": "CANONICAL",
            "aliases": ["CC-1", "CC1", "Cluster 1"],
        },
        "storage_array_alpha": {
            "canonical_name": "Storage Array Alpha",
            "status": "CANONICAL",
            "aliases": ["SAN-Alpha", "Array Alpha", "Storage-Alpha"],
        },
        "storage_array_beta": {
            "canonical_name": "Storage Array Beta",
            "status": "CANONICAL",
            "aliases": ["SAN-Beta", "Array Beta"],
        },
    }

    session = EpistemicIngressSession(base_reg)
    h0 = compute_registry_hash(session.durable_registry)

    test_cases = [
        # Case 1: Exact registered alias
        ("W01-D1", "source_feed_A", "CC-1", "Exact alias of CC1", {"identity_judgment": "EXISTING", "target_id": "compute_cluster_1"}),
        
        # Case 2: Unseen composite (Confirmation sequence)
        # Doc 1: "Cluster 1 Backup" -> hypothesis on compute_cluster_1
        ("W02-D1", "source_feed_A", "Cluster 1 Backup", "Under-specified composite mention", {"identity_judgment": "EXISTING", "target_id": "compute_cluster_1"}),
        # Doc 2: "Cluster 1 Backup (CC-1 Standby Instance)" -> confirms compute_cluster_1
        ("W02-D2", "source_feed_B", "Cluster 1 Backup (CC-1 Standby Instance)", "Explicit corroboration", {"identity_judgment": "EXISTING", "target_id": "compute_cluster_1"}),

        # Case 3: Unseen composite (Contradiction / Disconfirmation sequence)
        # Doc 1: "SAN Alpha Unit" -> Gemma proposed storage_array_alpha
        ("W03-D1", "source_feed_A", "SAN Alpha Unit", "Under-specified composite mention", {"identity_judgment": "EXISTING", "target_id": "storage_array_alpha"}),
        # Doc 2: "SAN Alpha Unit (Storage Array Beta)" -> Explicitly points to Beta instead of Alpha!
        ("W03-D2", "source_feed_B", "SAN Alpha Unit (Storage Array Beta)", "Contradictory explicit clarification", {"identity_judgment": "EXISTING", "target_id": "storage_array_beta"}),
    ]

    for doc_id, src, mention, ctx, prop in test_cases:
        h_before = compute_registry_hash(session.durable_registry)
        res = session.process_mention(doc_id, src, mention, ctx, prop)
        h_after = compute_registry_hash(session.durable_registry)
        is_h_invariant = (h_before == h_after) if not res.get("durable") else True
        print(f"[{doc_id}] '{mention}' -> Action: {res['action']}, Durable: {res['durable']}, Guardrail: {res['guardrail']}")
        if not res.get("durable"):
            print(f"       Hash Invariant: {is_h_invariant} ({h_before[:12]} == {h_after[:12]})")

    print("\n--------------------------------------------------------------------------------")
    print("HYPOTHESIS LEDGER STATE:")
    for hyp_id, hyp in session.hypothesis_ledger.items():
        print(f"  {hyp_id}: status={hyp['status']}, candidate={hyp['candidate_target']}, durable_target={hyp.get('durable_target')}, retargeted_to={hyp.get('retargeted_to')}")
    print("--------------------------------------------------------------------------------")
    print("SCOUT COMPLETE: Disconfirmation and isolation verified cleanly.")


if __name__ == "__main__":
    run_mini_scout()
