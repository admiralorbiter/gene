"""Confirmatory Benchmark Worlds for Stage 8C-R3 (CONTRACT-R8-8C-R3).
Generates 60 fresh synthetic worlds (120 sequential decisions) with PRNG seed 3141592653.
"""

import random
from typing import Any, Dict, List, Tuple


def get_stage8c_r3_base_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "compute_cluster_alpha": {
            "entity_id": "compute_cluster_alpha",
            "canonical_name": "Compute Cluster Alpha",
            "status": "canonical",
            "aliases": ["Cluster-Alpha", "CCA", "Alpha Compute Pool"],
            "parent_entity": None,
        },
        "compute_cluster_beta": {
            "entity_id": "compute_cluster_beta",
            "canonical_name": "Compute Cluster Beta",
            "status": "canonical",
            "aliases": ["Cluster-Beta", "CCB", "Beta Compute Pool"],
            "parent_entity": None,
        },
        "storage_array_alpha": {
            "entity_id": "storage_array_alpha",
            "canonical_name": "Storage Array Alpha",
            "status": "canonical",
            "aliases": ["SAN-Alpha", "SAA", "Primary Storage Pool"],
            "parent_entity": None,
        },
        "storage_array_beta": {
            "entity_id": "storage_array_beta",
            "canonical_name": "Storage Array Beta",
            "status": "canonical",
            "aliases": ["SAN-Beta", "SAB", "Secondary Storage Pool"],
            "parent_entity": None,
        },
        "gateway_router_alpha": {
            "entity_id": "gateway_router_alpha",
            "canonical_name": "Gateway Router Alpha",
            "status": "canonical",
            "aliases": ["Router-Alpha", "GRA", "Edge Gateway Alpha"],
            "parent_entity": None,
        },
        "gateway_router_beta": {
            "entity_id": "gateway_router_beta",
            "canonical_name": "Gateway Router Beta",
            "status": "canonical",
            "aliases": ["Router-Beta", "GRB", "Edge Gateway Beta"],
            "parent_entity": None,
        },
    }


def generate_stage8c_r3_worlds(seed: int = 3141592653) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rng = random.Random(seed)
    worlds = []
    gold_manifest = {}

    systems = [
        ("Vector Core Alpha", "VCA", "accelerator"),
        ("Neural Engine Beta", "NEB", "accelerator"),
        ("Quantum Buffer Gamma", "QBG", "memory"),
        ("Optical Fabric Delta", "OFD", "interconnect"),
        ("Tensor Pipeline Epsilon", "TPE", "pipeline"),
        ("Telemetry Sensor Zeta", "TSZ", "telemetry"),
        ("Hypervisor Node Eta", "HNE", "compute"),
        ("Cache Array Theta", "CAT", "storage"),
        ("Inference Engine Iota", "IEI", "compute"),
        ("Switch Fabric Kappa", "SFK", "network"),
        ("Load Balancer Lambda", "LBL", "network"),
        ("Security Module Mu", "SMM", "security"),
        ("Crypto Accelerator Nu", "CAN", "security"),
        ("Flash Pool Xi", "FPX", "storage"),
        ("Database Node Omicron", "DNO", "database"),
    ]

    canonical_entities = list(get_stage8c_r3_base_registry().keys())

    # --- Arm 1: Novel Systems (15 worlds, 30 decisions) ---
    for i, (name, acronym, stype) in enumerate(systems):
        wid = f"world_r3_arm1_{i+1:02d}"
        doc1_id = f"{wid}_doc_1"
        doc2_id = f"{wid}_doc_2"
        prov_id = f"prov_{name.lower().replace(' ', '_')}"

        doc1 = {
            "doc_id": doc1_id,
            "source_id": "deployment_manifest",
            "mention": name,
            "context": f"Initial commissioning and deployment notice: Standalone system {name} ({acronym}) is now active in production.",
            "arm": "ARM1_NOVEL",
        }
        gold_manifest[doc1_id] = {
            "world_id": wid,
            "arm": "ARM1_NOVEL",
            "action": "CREATE_PROVISIONAL",
            "expected_target": prov_id,
            "resolvable": True,
        }

        doc2 = {
            "doc_id": doc2_id,
            "source_id": "telemetry_daemon",
            "mention": acronym,
            "context": f"Performance monitoring update: Secondary interface telemetry active on {acronym} ({name}).",
            "arm": "ARM1_NOVEL",
        }
        gold_manifest[doc2_id] = {
            "world_id": wid,
            "arm": "ARM1_NOVEL",
            "action": "LINK",
            "expected_target": prov_id,
            "resolvable": True,
        }

        worlds.append({"world_id": wid, "arm": "ARM1_NOVEL", "docs": [doc1, doc2]})

    # --- Arm 2: Known Registered Aliases (15 worlds, 30 decisions) ---
    base_reg = get_stage8c_r3_base_registry()
    for i in range(15):
        wid = f"world_r3_arm2_{i+1:02d}"
        doc1_id = f"{wid}_doc_1"
        doc2_id = f"{wid}_doc_2"

        target_eid = canonical_entities[i % len(canonical_entities)]
        edata = base_reg[target_eid]
        cname = edata["canonical_name"]
        aliases = edata["aliases"]
        alias1 = aliases[0]
        alias2 = aliases[1] if len(aliases) > 1 else cname

        doc1 = {
            "doc_id": doc1_id,
            "source_id": "audit_log",
            "mention": alias1,
            "context": f"Routine audit telemetry captured on {alias1} during morning health check.",
            "arm": "ARM2_KNOWN_ALIAS",
        }
        gold_manifest[doc1_id] = {
            "world_id": wid,
            "arm": "ARM2_KNOWN_ALIAS",
            "action": "LINK",
            "expected_target": target_eid,
            "resolvable": True,
        }

        doc2 = {
            "doc_id": doc2_id,
            "source_id": "network_monitor",
            "mention": alias2,
            "context": f"Packet distribution confirmed normal on {alias2} across all ingress ports.",
            "arm": "ARM2_KNOWN_ALIAS",
        }
        gold_manifest[doc2_id] = {
            "world_id": wid,
            "arm": "ARM2_KNOWN_ALIAS",
            "action": "LINK",
            "expected_target": target_eid,
            "resolvable": True,
        }

        worlds.append({"world_id": wid, "arm": "ARM2_KNOWN_ALIAS", "docs": [doc1, doc2]})

    # --- Arm 3: Structural Partitions with Discriminative Sub-IDs (15 worlds, 30 decisions) ---
    partition_markers = ["Partition", "Blade", "Slice", "Tray", "Socket"]
    for i in range(15):
        wid = f"world_r3_arm3_{i+1:02d}"
        doc1_id = f"{wid}_doc_1"
        doc2_id = f"{wid}_doc_2"

        target_eid = canonical_entities[i % len(canonical_entities)]
        cname = base_reg[target_eid]["canonical_name"]
        marker = partition_markers[i % len(partition_markers)]
        sub_num = (i % 4) + 1

        mention1 = f"{cname} {marker} {sub_num}"
        prov_partition_id = f"prov_{target_eid}_{marker.lower()}_{sub_num}"

        doc1 = {
            "doc_id": doc1_id,
            "source_id": "hardware_manifest",
            "mention": mention1,
            "context": f"Hardware allocation logged for {mention1} under parent unit {cname}.",
            "arm": "ARM3_PARTITION",
        }
        gold_manifest[doc1_id] = {
            "world_id": wid,
            "arm": "ARM3_PARTITION",
            "action": "CREATE_PROVISIONAL",
            "expected_target": prov_partition_id,
            "resolvable": True,
        }

        mention2 = f"{marker} {sub_num} on {cname}"
        doc2 = {
            "doc_id": doc2_id,
            "source_id": "power_telemetry",
            "mention": mention2,
            "context": f"Voltage draw within acceptable envelope on {mention2} (sub-unit of {cname}).",
            "arm": "ARM3_PARTITION",
        }
        gold_manifest[doc2_id] = {
            "world_id": wid,
            "arm": "ARM3_PARTITION",
            "action": "LINK",
            "expected_target": prov_partition_id,
            "resolvable": True,
        }

        worlds.append({"world_id": wid, "arm": "ARM3_PARTITION", "docs": [doc1, doc2]})

    # --- Arm 4A: Permanent Non-Resolvable Ambiguity & Deferrals (8 worlds, 16 decisions) ---
    adversarial_cases = [
        ("Speculative Cluster Omega", "Architecture discussion: Proposal for Speculative Cluster Omega pending funding approval."),
        ("Rejected Cache Pool X", "Decommission notice: Proposed Rejected Cache Pool X was rejected during design review and will not be built."),
        ("Generic Storage", "System notice: Backups transferred to generic storage volume without unique identifier."),
        ("Unspecified Gateway", "Network event: Interface error on unspecified gateway device."),
        ("Mock Accelerator Alpha", "Test harness: Synthetic test driver initialized with mock accelerator alpha for unit test suite."),
        ("Hypothetical Server Node", "Simulation run: Modeling performance impact on hypothetical server node under 10x load."),
        ("Ambiguous Cluster", "Alert: Ambiguous cluster status reported across overlapping zones."),
        ("Virtual Slice", "Log entry: Ephemeral container spun up on virtual slice without hardware backing."),
    ]
    for i, (mention_text, ctx) in enumerate(adversarial_cases):
        wid = f"world_r3_arm4a_{i+1:02d}"
        doc1_id = f"{wid}_doc_1"
        doc2_id = f"{wid}_doc_2"

        doc1 = {
            "doc_id": doc1_id,
            "source_id": "informational_bulletin",
            "mention": mention_text,
            "context": ctx,
            "arm": "ARM4A_PERMANENT_DEFERRAL",
        }
        gold_manifest[doc1_id] = {
            "world_id": wid,
            "arm": "ARM4A_PERMANENT_DEFERRAL",
            "action": "DEFER",
            "expected_target": None,
            "resolvable": False,
        }

        doc2 = {
            "doc_id": doc2_id,
            "source_id": "informational_bulletin_followup",
            "mention": mention_text,
            "context": f"Follow-up clarification: {mention_text} remains unconfirmed and non-operational.",
            "arm": "ARM4A_PERMANENT_DEFERRAL",
        }
        gold_manifest[doc2_id] = {
            "world_id": wid,
            "arm": "ARM4A_PERMANENT_DEFERRAL",
            "action": "DEFER",
            "expected_target": None,
            "resolvable": False,
        }

        worlds.append({"world_id": wid, "arm": "ARM4A_PERMANENT_DEFERRAL", "docs": [doc1, doc2]})

    # --- Arm 4B: Refined Precedence & Accumulation Matrix (7 worlds, 14 decisions) ---
    # World 54 (1): Structural keyword without discriminating sub-ID + Explicit Registered Parenthetical
    # e.g. "SAN Alpha Mirror Pool (SAN-Beta)" -> Refined Rule: no discriminating sub-ID, but has registered parenthetical (SAN-Beta) -> LINK storage_array_beta
    w54_doc1 = {
        "doc_id": "world_r3_arm4b_01_doc_1",
        "source_id": "storage_migration_log",
        "mention": "SAN Alpha Mirror Pool (SAN-Beta)",
        "context": "Replication target configured on SAN Alpha Mirror Pool (SAN-Beta) for disaster recovery.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3_arm4b_01_doc_1"] = {
        "world_id": "world_r3_arm4b_01",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "LINK",
        "expected_target": "storage_array_beta",
        "resolvable": True,
    }
    w54_doc2 = {
        "doc_id": "world_r3_arm4b_01_doc_2",
        "source_id": "storage_audit",
        "mention": "SAN-Beta",
        "context": "SAN-Beta confirms receipt of mirrored volume blocks.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3_arm4b_01_doc_2"] = {
        "world_id": "world_r3_arm4b_01",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "LINK",
        "expected_target": "storage_array_beta",
        "resolvable": True,
    }
    worlds.append({"world_id": "world_r3_arm4b_01", "arm": "ARM4B_DISCONFIRMATION", "docs": [w54_doc1, w54_doc2]})

    # World 55 (2): Structural keyword without discriminating sub-ID and NO registered parenthetical -> DEFER
    w55_doc1 = {
        "doc_id": "world_r3_arm4b_02_doc_1",
        "source_id": "storage_note",
        "mention": "Storage Array Alpha Mirror Pool",
        "context": "Discussion regarding potential Storage Array Alpha Mirror Pool creation.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3_arm4b_02_doc_1"] = {
        "world_id": "world_r3_arm4b_02",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    w55_doc2 = {
        "doc_id": "world_r3_arm4b_02_doc_2",
        "source_id": "storage_note_2",
        "mention": "Storage Array Alpha Mirror Pool",
        "context": "Mirror pool proposal remains unapproved.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3_arm4b_02_doc_2"] = {
        "world_id": "world_r3_arm4b_02",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    worlds.append({"world_id": "world_r3_arm4b_02", "arm": "ARM4B_DISCONFIRMATION", "docs": [w55_doc1, w55_doc2]})

    # Worlds 56-60 (3-7): Accumulation & Multi-Source Disconfirmation
    arm4b_accum_cases = [
        ("Edge Gateway Alpha Hot-Spare", "Gateway Router Alpha", "gateway_router_alpha", "Hardware replacement: Edge Gateway Alpha Hot-Spare (Router-Alpha) provisioned."),
        ("Compute Cluster Beta Overflow Node", "Compute Cluster Beta", "compute_cluster_beta", "Burst capacity routed to Compute Cluster Beta Overflow Node (CCB)."),
        ("Primary Storage Pool Backup Mirror", "Storage Array Alpha", "storage_array_alpha", "Snapshot scheduled on Primary Storage Pool Backup Mirror (SAN-Alpha)."),
        ("Edge Gateway Beta Ingress Route", "Gateway Router Beta", "gateway_router_beta", "Route metric updated on Edge Gateway Beta Ingress Route (Router-Beta)."),
        ("Compute Cluster Alpha Auxiliary Blade", "Compute Cluster Alpha", "compute_cluster_alpha", "Maintenance cycle on Compute Cluster Alpha Auxiliary Blade (Cluster-Alpha)."),
    ]
    for i, (mention_text, parent_name, target_eid, ctx) in enumerate(arm4b_accum_cases):
        wid = f"world_r3_arm4b_{i+3:02d}"
        doc1_id = f"{wid}_doc_1"
        doc2_id = f"{wid}_doc_2"

        doc1 = {
            "doc_id": doc1_id,
            "source_id": "infrastructure_ledger",
            "mention": mention_text,
            "context": ctx,
            "arm": "ARM4B_DISCONFIRMATION",
        }
        gold_manifest[doc1_id] = {
            "world_id": wid,
            "arm": "ARM4B_DISCONFIRMATION",
            "action": "LINK",
            "expected_target": target_eid,
            "resolvable": True,
        }

        doc2 = {
            "doc_id": doc2_id,
            "source_id": "health_telemetry",
            "mention": base_reg[target_eid]["aliases"][0],
            "context": f"Status OK confirmed on {base_reg[target_eid]['aliases'][0]}.",
            "arm": "ARM4B_DISCONFIRMATION",
        }
        gold_manifest[doc2_id] = {
            "world_id": wid,
            "arm": "ARM4B_DISCONFIRMATION",
            "action": "LINK",
            "expected_target": target_eid,
            "resolvable": True,
        }

        worlds.append({"world_id": wid, "arm": "ARM4B_DISCONFIRMATION", "docs": [doc1, doc2]})

    assert len(worlds) == 60, f"Expected 60 worlds, got {len(worlds)}"
    assert len(gold_manifest) == 120, f"Expected 120 decisions in gold manifest, got {len(gold_manifest)}"

    return worlds, gold_manifest
