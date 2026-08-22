"""Confirmatory Benchmark Worlds for Stage 8C-R3 (CONTRACT-R8-8C-R3-R1).
Generates 60 lexically fresh synthetic worlds (120 sequential decisions) with PRNG seed 2718281828.
No reused surface forms from Stage 8C-R2.
"""

import random
from typing import Any, Dict, List, Tuple


def get_stage8c_r3_r1_base_registry() -> Dict[str, Dict[str, Any]]:
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


def generate_stage8c_r3_r1_worlds(seed: int = 2718281828) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rng = random.Random(seed)
    worlds = []
    gold_manifest = {}

    # Fresh novel systems (lexically independent from R2)
    fresh_systems = [
        ("Photonic Interconnect Zeta", "PIZ", "interconnect"),
        ("Graph Accelerator Epsilon", "GAE", "accelerator"),
        ("Neuromorphic Mesh Theta", "NMT", "compute"),
        ("Direct Memory Fabric Iota", "DMFI", "memory"),
        ("Sparse Matrix Unit Kappa", "SMUK", "accelerator"),
        ("Telemetry Aggregator Lambda", "TAL", "telemetry"),
        ("Quantum Cryo Node Mu", "QCNM", "quantum"),
        ("Optoelectronic Switch Nu", "OESN", "network"),
        ("Coherent Cache Pool Xi", "CCPX", "memory"),
        ("Neural Ingress Gateway Omicron", "NIGO", "gateway"),
        ("Elastic Shard Node Pi", "ESNP", "database"),
        ("Vector Reduction Pipeline Rho", "VRPR", "pipeline"),
        ("Atomic State Sequencer Sigma", "ASSS", "sequencer"),
        ("Fast Transit Bus Tau", "FTBT", "interconnect"),
        ("Secure Enclave Host Upsilon", "SEHU", "security"),
    ]

    canonical_entities = list(get_stage8c_r3_r1_base_registry().keys())

    # --- Arm 1: Fresh Novel Systems (15 worlds, 30 decisions, 30 resolvable) ---
    for i, (name, acronym, stype) in enumerate(fresh_systems):
        wid = f"world_r3r1_arm1_{i+1:02d}"
        doc1_id = f"{wid}_doc_1"
        doc2_id = f"{wid}_doc_2"
        prov_id = f"prov_{name.lower().replace(' ', '_')}"

        doc1 = {
            "doc_id": doc1_id,
            "source_id": "commissioning_daemon",
            "mention": name,
            "context": f"Initial commissioning and deployment log: Standalone system {name} ({acronym}) is now active in production.",
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
            "source_id": "telemetry_stream",
            "mention": acronym,
            "context": f"Secondary telemetry signal captured on {acronym} ({name}).",
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

    # --- Arm 2: Known Registered Aliases (15 worlds, 30 decisions, 30 resolvable) ---
    base_reg = get_stage8c_r3_r1_base_registry()
    for i in range(15):
        wid = f"world_r3r1_arm2_{i+1:02d}"
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
            "source_id": "infrastructure_monitor",
            "mention": alias1,
            "context": f"Heartbeat verification logged for {alias1} during routine sweep.",
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
            "source_id": "traffic_analyzer",
            "mention": alias2,
            "context": f"Throughput threshold satisfied on {alias2} under standard operational load.",
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

    # --- Arm 3: Structural Partitions with Discriminating Sub-IDs (15 worlds, 30 decisions, 30 resolvable) ---
    partition_markers = ["Partition", "Blade", "Slice", "Tray", "Socket"]
    sub_identifiers = ["1", "2", "3", "4", "A", "B", "C", "D"]
    for i in range(15):
        wid = f"world_r3r1_arm3_{i+1:02d}"
        doc1_id = f"{wid}_doc_1"
        doc2_id = f"{wid}_doc_2"

        target_eid = canonical_entities[i % len(canonical_entities)]
        cname = base_reg[target_eid]["canonical_name"]
        marker = partition_markers[i % len(partition_markers)]
        sub_id = sub_identifiers[i % len(sub_identifiers)]

        mention1 = f"{cname} {marker} {sub_id}"
        prov_partition_id = f"prov_{target_eid}_{marker.lower()}_{sub_id.lower()}"

        doc1 = {
            "doc_id": doc1_id,
            "source_id": "hardware_allocator",
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

        mention2 = f"{marker} {sub_id} on {cname}"
        doc2 = {
            "doc_id": doc2_id,
            "source_id": "power_monitor",
            "mention": mention2,
            "context": f"Thermal profile nominal on {mention2} (sub-component of {cname}).",
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

    # --- Arm 4A: Permanent Non-Resolvable Deferrals (8 worlds, 16 decisions, 0 resolvable) ---
    fresh_adversarial_cases = [
        ("Speculative Cluster Omega", "Architectural memo: Proposal for Speculative Cluster Omega pending executive funding."),
        ("Decommissioned Cache Matrix", "Retirement log: Proposed Decommissioned Cache Matrix was rejected during architectural review."),
        ("Generic Storage Fabric", "System event: Data migrated to generic storage fabric without unique asset identifier."),
        ("Unspecified Gateway Interface", "Routing alert: Latency spike observed on unspecified gateway interface."),
        ("Mock Accelerator Unit", "Test harness: Unit test initialized with mock accelerator unit."),
        ("Simulated Host Node", "Benchmarking report: Workload stress-tested on simulated host node in sandbox."),
        ("Ambiguous Switching Fabric", "Network telemetry: Transient fault reported across ambiguous switching fabric."),
        ("Virtual Execution Slice", "Ephemeral container spun up on virtual execution slice without physical backing."),
    ]
    for i, (mention_text, ctx) in enumerate(fresh_adversarial_cases):
        wid = f"world_r3r1_arm4a_{i+1:02d}"
        doc1_id = f"{wid}_doc_1"
        doc2_id = f"{wid}_doc_2"

        doc1 = {
            "doc_id": doc1_id,
            "source_id": "bulletin",
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
            "source_id": "bulletin_followup",
            "mention": mention_text,
            "context": f"Clarification update: {mention_text} is not commissioned for production traffic.",
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

    # --- Arm 4B: Evidence Accumulation & Precedence Matrix (7 worlds, 14 decisions, 7 resolvable) ---
    # Case 1: Precedence conflict lifecycle test
    # Doc 1: "Edge Gateway Alpha Reserve Bay" (no sub-ID, no parenthetical) -> DEFER (hypothesis created)
    # Doc 2: "Edge Gateway Alpha Reserve Bay (Router-Beta)" (has registered parenthetical) -> Rule 3 matches -> LINK gateway_router_beta
    w54_doc1 = {
        "doc_id": "world_r3r1_arm4b_01_doc_1",
        "source_id": "network_migration_log",
        "mention": "Edge Gateway Alpha Reserve Bay",
        "context": "Failover route configured on Edge Gateway Alpha Reserve Bay for backup ingress.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_01_doc_1"] = {
        "world_id": "world_r3r1_arm4b_01",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    w54_doc2 = {
        "doc_id": "world_r3r1_arm4b_01_doc_2",
        "source_id": "router_telemetry",
        "mention": "Edge Gateway Alpha Reserve Bay (Router-Beta)",
        "context": "Edge Gateway Alpha Reserve Bay (Router-Beta) confirms active packet forwarding across all backup routes.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_01_doc_2"] = {
        "world_id": "world_r3r1_arm4b_01",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "LINK",
        "expected_target": "gateway_router_beta",
        "resolvable": True,
    }
    worlds.append({"world_id": "world_r3r1_arm4b_01", "arm": "ARM4B_DISCONFIRMATION", "docs": [w54_doc1, w54_doc2]})

    # Case 2: Candidate-bearing Doc1 DEFER -> Doc2 Retarget
    w55_doc1 = {
        "doc_id": "world_r3r1_arm4b_02_doc_1",
        "source_id": "compute_audit",
        "mention": "Unverified Node Alpha",
        "context": "Telemetry probe logged on Unverified Node Alpha during maintenance window.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_02_doc_1"] = {
        "world_id": "world_r3r1_arm4b_02",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    w55_doc2 = {
        "doc_id": "world_r3r1_arm4b_02_doc_2",
        "source_id": "compute_telemetry",
        "mention": "Compute Cluster Beta",
        "context": "Node resolved to Compute Cluster Beta following physical topology verification.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_02_doc_2"] = {
        "world_id": "world_r3r1_arm4b_02",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "LINK",
        "expected_target": "compute_cluster_beta",
        "resolvable": True,
    }
    worlds.append({"world_id": "world_r3r1_arm4b_02", "arm": "ARM4B_DISCONFIRMATION", "docs": [w55_doc1, w55_doc2]})

    # Case 3: Candidate-bearing Doc1 DEFER -> Doc2 Retarget
    w56_doc1 = {
        "doc_id": "world_r3r1_arm4b_03_doc_1",
        "source_id": "storage_audit",
        "mention": "Proposed Tier Array",
        "context": "Initial snapshot logged on Proposed Tier Array.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_03_doc_1"] = {
        "world_id": "world_r3r1_arm4b_03",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    w56_doc2 = {
        "doc_id": "world_r3r1_arm4b_03_doc_2",
        "source_id": "storage_telemetry",
        "mention": "SAN-Alpha",
        "context": "Volume blocks persisted to SAN-Alpha.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_03_doc_2"] = {
        "world_id": "world_r3r1_arm4b_03",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "LINK",
        "expected_target": "storage_array_alpha",
        "resolvable": True,
    }
    worlds.append({"world_id": "world_r3r1_arm4b_03", "arm": "ARM4B_DISCONFIRMATION", "docs": [w56_doc1, w56_doc2]})

    # Case 4: Candidate_target=null Doc1 DEFER -> Doc2 Existing Resolution
    w57_doc1 = {
        "doc_id": "world_r3r1_arm4b_04_doc_1",
        "source_id": "network_note",
        "mention": "Pending Router Port",
        "context": "Traffic diverted to pending router port without interface mapping.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_04_doc_1"] = {
        "world_id": "world_r3r1_arm4b_04",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    w57_doc2 = {
        "doc_id": "world_r3r1_arm4b_04_doc_2",
        "source_id": "network_telemetry",
        "mention": "Gateway Router Alpha",
        "context": "Port binding confirmed active on Gateway Router Alpha.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_04_doc_2"] = {
        "world_id": "world_r3r1_arm4b_04",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "LINK",
        "expected_target": "gateway_router_alpha",
        "resolvable": True,
    }
    worlds.append({"world_id": "world_r3r1_arm4b_04", "arm": "ARM4B_DISCONFIRMATION", "docs": [w57_doc1, w57_doc2]})

    # Case 5: Candidate_target=null Doc1 DEFER -> Doc2 Existing Resolution
    w58_doc1 = {
        "doc_id": "world_r3r1_arm4b_05_doc_1",
        "source_id": "cluster_note",
        "mention": "Ambiguous Server Blade",
        "context": "Telemetry packet received from ambiguous server blade lacking rack ID.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_05_doc_1"] = {
        "world_id": "world_r3r1_arm4b_05",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    w58_doc2 = {
        "doc_id": "world_r3r1_arm4b_05_doc_2",
        "source_id": "cluster_telemetry",
        "mention": "Compute Cluster Alpha",
        "context": "Chassis identifier confirmed belonging to Compute Cluster Alpha.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_05_doc_2"] = {
        "world_id": "world_r3r1_arm4b_05",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "LINK",
        "expected_target": "compute_cluster_alpha",
        "resolvable": True,
    }
    worlds.append({"world_id": "world_r3r1_arm4b_05", "arm": "ARM4B_DISCONFIRMATION", "docs": [w58_doc1, w58_doc2]})

    # Case 6: Nullable Doc1 DEFER -> Doc2 Novel Provisional Resolution
    w59_doc1 = {
        "doc_id": "world_r3r1_arm4b_06_doc_1",
        "source_id": "telemetry_draft",
        "mention": "Uncommissioned Sensor Mesh",
        "context": "Early test packet received from uncommissioned sensor mesh.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_06_doc_1"] = {
        "world_id": "world_r3r1_arm4b_06",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    w59_doc2 = {
        "doc_id": "world_r3r1_arm4b_06_doc_2",
        "source_id": "commissioning_service",
        "mention": "Sensor Mesh Omega",
        "context": "Official deployment notice: Sensor Mesh Omega (SMO) is now active in production.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_06_doc_2"] = {
        "world_id": "world_r3r1_arm4b_06",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "CREATE_PROVISIONAL",
        "expected_target": "prov_sensor_mesh_omega",
        "resolvable": True,
    }
    worlds.append({"world_id": "world_r3r1_arm4b_06", "arm": "ARM4B_DISCONFIRMATION", "docs": [w59_doc1, w59_doc2]})

    # Case 7: Candidate-bearing DEFER -> Confirmation lifecycle test
    # Doc 1: "Unverified Host Pool" (no sub-ID, no parenthetical) -> DEFER (hypothesis created)
    # Doc 2: "Unverified Host Pool (Cluster-Beta)" (has registered parenthetical) -> Rule 3 matches -> LINK compute_cluster_beta
    w60_doc1 = {
        "doc_id": "world_r3r1_arm4b_07_doc_1",
        "source_id": "precheck_log",
        "mention": "Unverified Host Pool",
        "context": "Pre-check scan on Unverified Host Pool awaiting signature.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_07_doc_1"] = {
        "world_id": "world_r3r1_arm4b_07",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "DEFER",
        "expected_target": None,
        "resolvable": False,
    }
    w60_doc2 = {
        "doc_id": "world_r3r1_arm4b_07_doc_2",
        "source_id": "signature_authority",
        "mention": "Unverified Host Pool (Cluster-Beta)",
        "context": "Signature validated: Unverified Host Pool (Cluster-Beta) confirmed active within Cluster-Beta.",
        "arm": "ARM4B_DISCONFIRMATION",
    }
    gold_manifest["world_r3r1_arm4b_07_doc_2"] = {
        "world_id": "world_r3r1_arm4b_07",
        "arm": "ARM4B_DISCONFIRMATION",
        "action": "LINK",
        "expected_target": "compute_cluster_beta",
        "resolvable": True,
    }
    worlds.append({"world_id": "world_r3r1_arm4b_07", "arm": "ARM4B_DISCONFIRMATION", "docs": [w60_doc1, w60_doc2]})

    assert len(worlds) == 60, f"Expected 60 worlds, got {len(worlds)}"
    assert len(gold_manifest) == 120, f"Expected 120 decisions in gold manifest, got {len(gold_manifest)}"

    resolvable_count = sum(1 for g in gold_manifest.values() if g.get("resolvable", False))
    assert resolvable_count == 97, f"Expected exactly 97 resolvable decisions, got {resolvable_count}"

    return worlds, gold_manifest
