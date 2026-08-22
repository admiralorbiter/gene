"""Fresh Sealed 60-World Evaluation Benchmark Generator for CONTRACT-R8-8C-R2.
Seed: 2357947788 (0x8C8C8C8C).
Generates 60 sealed worlds (120 decisions) across 5 sub-arms.
"""

from typing import Any, Dict, List, Tuple


def get_stage8c_r2_base_registry() -> Dict[str, Any]:
    """Canonical base registry pre-seeded before evaluation."""
    return {
        "compute_cluster_1": {
            "canonical_name": "Compute Cluster 1",
            "status": "CANONICAL",
            "aliases": ["CC-1", "CC1", "Cluster 1", "Compute-1"],
        },
        "compute_cluster_4": {
            "canonical_name": "Compute Cluster 4",
            "status": "CANONICAL",
            "aliases": ["CC-4", "CC4", "Cluster 4", "Compute-4"],
        },
        "storage_array_alpha": {
            "canonical_name": "Storage Array Alpha",
            "status": "CANONICAL",
            "aliases": ["SAN-Alpha", "Array Alpha", "Storage-Alpha", "SAN-A"],
        },
        "storage_array_beta": {
            "canonical_name": "Storage Array Beta",
            "status": "CANONICAL",
            "aliases": ["SAN-Beta", "Array Beta", "Storage-Beta", "SAN-B"],
        },
        "tensor_pod_3": {
            "canonical_name": "Tensor Pod 3",
            "status": "CANONICAL",
            "aliases": ["TP-3", "TP3", "Pod 3", "Tensor-3"],
        },
        "aurora_node_7": {
            "canonical_name": "Aurora Node 7",
            "status": "CANONICAL",
            "aliases": ["AN-7", "AN7", "Aurora 7", "Node-7"],
        },
    }


def generate_stage8c_r2_worlds() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Generates 60 fresh evaluation worlds across 5 sub-arms ($N=120$ decisions) and gold manifest."""
    worlds = []
    gold_manifest = {}

    # -------------------------------------------------------------------------
    # Arm 1: Unseen Novel Hardware Systems (Worlds 1..15 = 30 Decisions)
    # -------------------------------------------------------------------------
    novel_systems = [
        ("Vector Core Alpha", "VCA", "Next-gen vector processing array"),
        ("Hydra Node 4", "HN-4", "High-density multi-GPU compute node"),
        ("Prism Switch 9", "PS-9", "Optical fabric interconnect switch"),
        ("Nexus Blade 7", "NB-7", "Modular enterprise blade server"),
        ("Titan Pod 2", "TPod-2", "Accelerated machine learning cluster"),
        ("Apex Fabric 5", "AF-5", "Ultra-low latency spine switch matrix"),
        ("Solaris Array 8", "SA-8", "All-flash NVMe tier-0 storage array"),
        ("Zenith Node 1", "ZN-1", "High-memory NUMA database server"),
        ("Chrono Switch 3", "CS-3", "Precision time protocol switch unit"),
        ("Vortex Rack 6", "VR-6", "Liquid-cooled high performance rack"),
        ("Spectra Cluster 11", "SC-11", "Specialized distributed raytracing cluster"),
        ("Aegis Unit 4", "AU-4", "Hardware security module enclave appliance"),
        ("Pulsar Blade 12", "PB-12", "Real-time stream telemetry aggregation blade"),
        ("Krypton Node 5", "KN-5", "Confidential compute enclave host"),
        ("Helios Pod 7", "HP-7", "Solar-powered edge AI inference module"),
    ]

    for idx, (name, alias, desc) in enumerate(novel_systems, start=1):
        wid = f"world_{idx:02d}_arm1"
        prov_target_id = f"prov_{name.lower().replace(' ', '_')}"
        doc1 = {
            "doc_id": f"doc_{idx:02d}_1",
            "source_id": f"source_arm1_ingest_{idx:02d}",
            "mention": name,
            "context": f"Hardware provisioning notice: Initial deployment of {name} ({desc}) initiated in datacenter hall B.",
        }
        doc2 = {
            "doc_id": f"doc_{idx:02d}_2",
            "source_id": f"source_arm1_audit_{idx:02d}",
            "mention": alias,
            "context": f"Network telemetry update: Secondary interface telemetry active on {alias} ({name}).",
        }
        worlds.append({"world_id": wid, "arm": "ARM1_NOVEL", "documents": [doc1, doc2]})
        gold_manifest[f"doc_{idx:02d}_1"] = {
            "action": "CREATE_PROVISIONAL",
            "expected_target": prov_target_id,
            "durable": True,
            "arm": "ARM1",
            "existence_established": True,
            "resolvable": True,
        }
        gold_manifest[f"doc_{idx:02d}_2"] = {
            "action": "LINK",
            "expected_target": prov_target_id,
            "durable": True,
            "arm": "ARM1",
            "existence_established": True,
            "resolvable": True,
        }

    # -------------------------------------------------------------------------
    # Arm 2: Morphological & Syntactic Known Aliases (Worlds 16..30 = 30 Decisions)
    # -------------------------------------------------------------------------
    known_alias_cases = [
        ("CC-1", "compute_cluster_1", "Compute Cluster 1", "Telemetry log: Routine memory scrub completed on CC-1."),
        ("SAN-Alpha", "storage_array_alpha", "Storage Array Alpha", "Storage report: Volume migration on SAN-Alpha completed successfully."),
        ("TP-3", "tensor_pod_3", "Tensor Pod 3", "Job scheduler: Distributed training batch allocated to TP-3."),
        ("AN-7", "aurora_node_7", "Aurora Node 7", "Node telemetry: Thermal sensors on AN-7 within nominal limits."),
        ("CC-4", "compute_cluster_4", "Compute Cluster 4", "Cluster health: Secondary node in CC-4 rejoined quorum."),
        ("SAN-Beta", "storage_array_beta", "Storage Array Beta", "Backup stream: Snapshot replication initiated on SAN-Beta."),
        ("CC1", "compute_cluster_1", "Compute Cluster 1", "Interface update: Link aggregation bonded on CC1 port 2."),
        ("Cluster 1", "compute_cluster_1", "Compute Cluster 1", "Compute dispatch: Cluster 1 scheduled for kernel patch."),
        ("Array Alpha", "storage_array_alpha", "Storage Array Alpha", "Storage audit: Array Alpha LUN 04 verified online."),
        ("Pod 3", "tensor_pod_3", "Tensor Pod 3", "Compute audit: Pod 3 GPU utilization averaged 94%."),
        ("Aurora 7", "aurora_node_7", "Aurora Node 7", "System log: Aurora 7 booted with UEFI secure image."),
        ("Cluster 4", "compute_cluster_4", "Compute Cluster 4", "Maintenance alert: Cluster 4 scheduled maintenance window closed."),
        ("SAN-B", "storage_array_beta", "Storage Array Beta", "Fibre channel alert: SAN-B zone 3 switch failover tested."),
        ("Compute-1", "compute_cluster_1", "Compute Cluster 1", "Metric collector: Compute-1 power draw 1.4kW."),
        ("Node-7", "aurora_node_7", "Aurora Node 7", "Ingress feed: Node-7 primary ethernet interface link up 100GbE."),
    ]

    for idx, (alias, canon_id, canon_name, ctx) in enumerate(known_alias_cases, start=16):
        wid = f"world_{idx:02d}_arm2"
        doc1 = {
            "doc_id": f"doc_{idx:02d}_1",
            "source_id": f"source_arm2_ingest_{idx:02d}",
            "mention": alias,
            "context": ctx,
        }
        doc2 = {
            "doc_id": f"doc_{idx:02d}_2",
            "source_id": f"source_arm2_audit_{idx:02d}",
            "mention": canon_name,
            "context": f"Audit verification log: Confirmed state reconciliation for {canon_name}.",
        }
        worlds.append({"world_id": wid, "arm": "ARM2_KNOWN_ALIAS", "documents": [doc1, doc2]})
        gold_manifest[f"doc_{idx:02d}_1"] = {
            "action": "LINK",
            "expected_target": canon_id,
            "durable": True,
            "arm": "ARM2",
            "existence_established": True,
            "resolvable": True,
        }
        gold_manifest[f"doc_{idx:02d}_2"] = {
            "action": "LINK",
            "expected_target": canon_id,
            "durable": True,
            "arm": "ARM2",
            "existence_established": True,
            "resolvable": True,
        }

    # -------------------------------------------------------------------------
    # Arm 3: Grounded Structural Partitions (Worlds 31..45 = 30 Decisions)
    # -------------------------------------------------------------------------
    partition_cases = [
        ("Compute Cluster 1 Partition 1-A", "CC1 Partition 1-A", "compute_cluster_1", "Hardware partition 1-A established inside Compute Cluster 1."),
        ("Storage Array Alpha Blade 2", "SAN-Alpha Blade 2", "storage_array_alpha", "Storage Array Alpha Blade 2 dedicated to fast caching pool."),
        ("Aurora Node 7 Enclosure 3", "AN-7 Enclosure 3", "aurora_node_7", "Aurora Node 7 Enclosure 3 sub-chassis power supply swapped."),
        ("Tensor Pod 3 Slice B1", "TP-3 Slice B1", "tensor_pod_3", "Tensor Pod 3 Slice B1 reserved for low-latency batch jobs."),
        ("Compute Cluster 4 Sub-Rack 1", "CC4 Sub-Rack 1", "compute_cluster_4", "Compute Cluster 4 Sub-Rack 1 cabling inspection complete."),
        ("Storage Array Beta LUN-09", "SAN-Beta LUN-09", "storage_array_beta", "Storage Array Beta LUN-09 formatted with block volume tier."),
        ("Compute Cluster 1 Partition 2-C", "CC1 Partition 2-C", "compute_cluster_1", "Partition 2-C on Compute Cluster 1 allocated to tenant gamma."),
        ("Aurora Node 7 Socket 0", "AN-7 Socket 0", "aurora_node_7", "CPU microcode updated on Aurora Node 7 Socket 0."),
        ("Tensor Pod 3 Tray 4", "TP-3 Tray 4", "tensor_pod_3", "GPU Tray 4 in Tensor Pod 3 reported memory parity error cleared."),
        ("Compute Cluster 4 Node 12", "CC-4 Node 12", "compute_cluster_4", "Compute Cluster 4 Node 12 added to local cluster ring."),
        ("Storage Array Alpha Shelf 1", "SAN-Alpha Shelf 1", "storage_array_alpha", "Storage Array Alpha Shelf 1 drive replacement completed."),
        ("Storage Array Beta Volume Pool 3", "SAN-Beta Pool 3", "storage_array_beta", "Volume Pool 3 on Storage Array Beta capacity expanded."),
        ("Compute Cluster 1 Blade 5", "CC-1 Blade 5", "compute_cluster_1", "Compute Cluster 1 Blade 5 network interface re-flashed."),
        ("Aurora Node 7 PCI-e Switch 1", "AN-7 Switch 1", "aurora_node_7", "PCI-e Switch 1 in Aurora Node 7 operating at Gen5 speeds."),
        ("Tensor Pod 3 Sub-Unit 1-Alpha", "TP-3 Sub-Unit 1-Alpha", "tensor_pod_3", "Tensor Pod 3 Sub-Unit 1-Alpha power delivery stabilized."),
    ]

    for idx, (name, alias, parent_id, ctx) in enumerate(partition_cases, start=31):
        wid = f"world_{idx:02d}_arm3"
        prov_target_id = f"prov_{name.lower().replace(' ', '_').replace('-', '_')}"
        doc1 = {
            "doc_id": f"doc_{idx:02d}_1",
            "source_id": f"source_arm3_ingest_{idx:02d}",
            "mention": name,
            "context": ctx,
        }
        doc2 = {
            "doc_id": f"doc_{idx:02d}_2",
            "source_id": f"source_arm3_audit_{idx:02d}",
            "mention": alias,
            "context": f"Audit verification log: Component telemetry for {alias} ({name}) validated.",
        }
        worlds.append({"world_id": wid, "arm": "ARM3_PARTITION", "documents": [doc1, doc2]})
        gold_manifest[f"doc_{idx:02d}_1"] = {
            "action": "CREATE_PROVISIONAL",
            "expected_target": prov_target_id,
            "durable": True,
            "must_not_link": [parent_id],
            "arm": "ARM3",
            "existence_established": True,
            "resolvable": True,
        }
        gold_manifest[f"doc_{idx:02d}_2"] = {
            "action": "LINK",
            "expected_target": prov_target_id,
            "durable": True,
            "arm": "ARM3",
            "existence_established": True,
            "resolvable": True,
        }

    # -------------------------------------------------------------------------
    # Arm 4A: Adversarial Existence Negatives & Permanent Deferrals (Worlds 46..53 = 16 Decisions)
    # -------------------------------------------------------------------------
    permanent_ambiguity_cases = [
        # Bare generic nouns (Worlds 46..49)
        ("The System", "The System", "Telemetry notice: Performance diagnostics initiated on The System.", "Operations log: Diagnostics ongoing across The System.", False),
        ("The Unit", "The Unit", "Alert dispatch: Thermal threshold warning triggered on The Unit.", "Facility log: Cooling fans throttled up on The Unit.", False),
        ("Primary Host", "Primary Host", "Network trace: ARP broadcast transmitted from Primary Host.", "Routing table: Gateway response received by Primary Host.", False),
        ("Backup Node", "Backup Node", "Storage log: Snapshot replication stream queued for Backup Node.", "Backup report: Synchronization completed on Backup Node.", False),

        # Ungrounded structural markers lacking discriminating sub-IDs (Worlds 50..51)
        ("Tensor Pod Three Sub-Unit", "Tensor Pod Three Sub-Unit", "Power telemetry: Voltage regulated on Tensor Pod Three Sub-Unit.", "Power log: Steady power draw verified on Tensor Pod Three Sub-Unit.", False),
        ("SAN Alpha Unit", "SAN Alpha Unit", "Maintenance notice: Cable dress inspection scheduled for SAN Alpha Unit.", "Maintenance report: Inspection completed on SAN Alpha Unit.", False),

        # Conditional / Negated / Simulated existence blockers (Worlds 52..53)
        ("Proposed Cluster Delta", "Proposed Cluster Delta", "Architecture proposal: Concept design for proposed Cluster Delta submitted for review.", "Planning stub: Simulation model for future Cluster Delta testing underway.", False),
        ("Replica Node Omega", "Replica Node Omega", "Virtual replica notice: Testing stub deployment cancelled for simulated Replica Node Omega.", "Lab memo: Pure virtual replica of Replica Node Omega archived.", False),
    ]

    for idx, (m1, m2, ctx1, ctx2, exist_flag) in enumerate(permanent_ambiguity_cases, start=46):
        wid = f"world_{idx:02d}_arm4a"
        doc1 = {
            "doc_id": f"doc_{idx:02d}_1",
            "source_id": f"source_arm4a_ingest_{idx:02d}",
            "mention": m1,
            "context": ctx1,
        }
        doc2 = {
            "doc_id": f"doc_{idx:02d}_2",
            "source_id": f"source_arm4a_audit_{idx:02d}",
            "mention": m2,
            "context": ctx2,
        }
        worlds.append({"world_id": wid, "arm": "ARM4A_PERMANENT_DEFERRAL", "documents": [doc1, doc2]})
        gold_manifest[f"doc_{idx:02d}_1"] = {
            "action": "DEFER",
            "expected_target": None,
            "durable": False,
            "arm": "ARM4A",
            "existence_established": exist_flag,
            "resolvable": False,
        }
        gold_manifest[f"doc_{idx:02d}_2"] = {
            "action": "DEFER",
            "expected_target": None,
            "durable": False,
            "arm": "ARM4A",
            "existence_established": exist_flag,
            "resolvable": False,
        }

    # -------------------------------------------------------------------------
    # Arm 4B: Evidence Accumulation & Disconfirmation (Worlds 54..60 = 14 Decisions)
    # -------------------------------------------------------------------------
    # 7 Worlds:
    # 3 Candidate-bearing disconfirmations -> retarget (Worlds 54..56)
    # 2 Nullable -> existing resolution (Worlds 57..58)
    # 1 Nullable -> novel provisional resolution (World 59)
    # 1 Candidate-bearing confirmation (World 60)
    clarifying_cases = [
        # Candidate-bearing disconfirmation -> retarget to existing canonical (3 worlds)
        (
            54,
            "Cluster 1 Secondary Enclave",
            "Cluster 1 Secondary Enclave (CC-4)",
            "compute_cluster_4",
            "compute_cluster_1",
            "RETARGET",
            "Configuration trace: Secondary compute capacity allocated on Cluster 1 Secondary Enclave.",
            "Audit verification log: Detailed hardware audit confirms Cluster 1 Secondary Enclave (CC-4) is physically provisioned in Compute Cluster 4, not Cluster 1.",
        ),
        (
            55,
            "SAN Alpha Mirror Pool",
            "SAN Alpha Mirror Pool (SAN-Beta)",
            "storage_array_beta",
            "storage_array_alpha",
            "RETARGET",
            "Storage trace: Replication target configured for SAN Alpha Mirror Pool.",
            "Topology reconciliation report: Verification reveals SAN Alpha Mirror Pool (SAN-Beta) is physically hosted on Storage Array Beta.",
        ),
        (
            56,
            "Tensor Pod 3 Auxiliary Ring",
            "Tensor Pod 3 Auxiliary Ring (AN-7)",
            "aurora_node_7",
            "tensor_pod_3",
            "RETARGET",
            "Interconnect trace: High-bandwidth queue opened on Tensor Pod 3 Auxiliary Ring.",
            "Hardware discovery audit: Interface trace establishes Tensor Pod 3 Auxiliary Ring (AN-7) terminates on Aurora Node 7 chassis.",
        ),

        # Nullable candidate -> existing canonical resolution (2 worlds)
        (
            57,
            "High Throughput Compute Grid",
            "High Throughput Compute Grid (CC-1)",
            "compute_cluster_1",
            None,
            "RESOLVE_EXISTING",
            "Job trace: Unspecified workload queued on High Throughput Compute Grid.",
            "Verification manifest: Confirmed High Throughput Compute Grid (CC-1) resolves to Compute Cluster 1.",
        ),
        (
            58,
            "Primary Enterprise San Fabric",
            "Primary Enterprise San Fabric (SAN-Alpha)",
            "storage_array_alpha",
            None,
            "RESOLVE_EXISTING",
            "Storage monitor: Ingress IOPS recorded on Primary Enterprise San Fabric.",
            "Storage audit: Primary Enterprise San Fabric (SAN-Alpha) verified as Storage Array Alpha.",
        ),

        # Nullable candidate -> novel provisional entity (1 world)
        (
            59,
            "Edge Router Gamma",
            "Edge Router Gamma",
            "prov_edge_router_gamma",
            None,
            "RESOLVE_NOVEL",
            "Network alert: BGP route flap observed on Edge Router Gamma.",
            "Commissioning document: Hardware deployment notice confirms newly installed standalone system Edge Router Gamma in PoP 4.",
        ),

        # Candidate-bearing confirmation (1 world)
        (
            60,
            "Cluster 1 Backup",
            "Cluster 1 Backup (CC-1)",
            "compute_cluster_1",
            "compute_cluster_1",
            "CONFIRM",
            "Disaster recovery log: Standby compute capacity allocated on Cluster 1 Backup.",
            "Verification report: System audit confirms Cluster 1 Backup (CC-1) active in secondary zone.",
        ),
    ]

    for (idx, m1, m2, final_target, initial_guess, mode, ctx1, ctx2) in clarifying_cases:
        wid = f"world_{idx:02d}_arm4b"
        doc1 = {
            "doc_id": f"doc_{idx:02d}_1",
            "source_id": f"source_arm4b_ingest_{idx:02d}",
            "mention": m1,
            "context": ctx1,
        }
        doc2 = {
            "doc_id": f"doc_{idx:02d}_2",
            "source_id": f"source_arm4b_audit_{idx:02d}",
            "mention": m2,
            "context": ctx2,
        }
        worlds.append({"world_id": wid, "arm": "ARM4B_DISCONFIRMATION", "documents": [doc1, doc2]})

        # Doc 1 is ALWAYS deferred
        gold_manifest[f"doc_{idx:02d}_1"] = {
            "action": "DEFER",
            "expected_target": None,
            "durable": False,
            "arm": "ARM4B",
            "initial_guess": initial_guess,
            "existence_established": True,
            "resolvable": False,
        }

        # Doc 2 resolves
        action = "CREATE_PROVISIONAL" if mode == "RESOLVE_NOVEL" else "LINK"
        gold_manifest[f"doc_{idx:02d}_2"] = {
            "action": action,
            "expected_target": final_target,
            "durable": True,
            "arm": "ARM4B",
            "mode": mode,
            "existence_established": True,
            "resolvable": True,
        }

    return worlds, gold_manifest
