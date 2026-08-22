"""Confirmatory Benchmark Worlds for Stage 8C-R3-R1 (CONTRACT-R8-8C-R3-R1).
Generates 60 genuinely lexically fresh synthetic worlds (120 sequential decisions) with PRNG seed 2718281828.
Includes a machine-verifiable freshness audit asserting disjointness with Stage 8C-R3 across Arms 1, 3, 4A, and 4B.
"""

import random
import re
from typing import Any, Dict, List, Set, Tuple


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

    # =========================================================================
    # ARM 1: Truly Fresh Novel Standalone Systems (15 Worlds, 30 Decisions)
    # Genuinely disjoint from R3 (e.g. Cryogenic Core, Spintronic Fabric, etc.)
    # =========================================================================
    arm1_novel_names = [
        "Cryogenic Core Sigma",
        "Spintronic Fabric Xi",
        "Topological Bus Mu",
        "Holographic Memory Lambda",
        "Coherent Coprocessor Tau",
        "Dielectric Interposer Nu",
        "Stochastic Matrix Engine Rho",
        "Superconducting Interconnect Psi",
        "Quantum Gateway Iota",
        "Ferroelectric Array Omicron",
        "Photon Routing Matrix Kappa",
        "Neuromorphic Lattice Upsilon",
        "Optoelectronic Module Chi",
        "Synaptic Mesh Zeta",
        "Silicon Photonic Interposer Delta",
    ]

    for i, name in enumerate(arm1_novel_names, start=1):
        wid = f"world_r3r1_arm1_{i:02d}"
        d1_id = f"{wid}_doc_1"
        d2_id = f"{wid}_doc_2"
        prov_target = f"prov_{name.lower().replace(' ', '_')}"

        doc1 = {
            "doc_id": d1_id,
            "source_id": f"src_eng_r3r1_a1_{i}_1",
            "mention": name,
            "context": f"Hardware provisioning notice: Initial deployment and commissioning of {name} is active in production.",
        }
        doc2 = {
            "doc_id": d2_id,
            "source_id": f"src_eng_r3r1_a1_{i}_2",
            "mention": name,
            "context": f"Operational log: Verification routine confirming {name} is active in production.",
        }

        worlds.append({"world_id": wid, "arm": "ARM1_NOVEL", "docs": [doc1, doc2]})

        gold_manifest[d1_id] = {
            "arm": "ARM1_NOVEL",
            "action": "CREATE_PROVISIONAL",
            "expected_target": prov_target,
            "resolvable": True,
        }
        gold_manifest[d2_id] = {
            "arm": "ARM1_NOVEL",
            "action": "LINK",
            "expected_target": prov_target,
            "resolvable": True,
        }

    # =========================================================================
    # ARM 2: Known Registered Systems via Aliases (15 Worlds, 30 Decisions)
    # =========================================================================
    arm2_cases = [
        ("Compute Cluster Alpha", "CCA", "Alpha Compute Pool", "compute_cluster_alpha"),
        ("Compute Cluster Beta", "CCB", "Beta Compute Pool", "compute_cluster_beta"),
        ("Storage Array Alpha", "SAN-Alpha", "Primary Storage Pool", "storage_array_alpha"),
        ("Storage Array Beta", "SAN-Beta", "Secondary Storage Pool", "storage_array_beta"),
        ("Gateway Router Alpha", "GRA", "Edge Gateway Alpha", "gateway_router_alpha"),
        ("Gateway Router Beta", "GRB", "Edge Gateway Beta", "gateway_router_beta"),
        ("Compute Cluster Alpha", "Cluster-Alpha", "Compute Cluster Alpha", "compute_cluster_alpha"),
        ("Compute Cluster Beta", "Cluster-Beta", "Compute Cluster Beta", "compute_cluster_beta"),
        ("Storage Array Alpha", "SAA", "Storage Array Alpha", "storage_array_alpha"),
        ("Storage Array Beta", "SAB", "Storage Array Beta", "storage_array_beta"),
        ("Gateway Router Alpha", "Router-Alpha", "Gateway Router Alpha", "gateway_router_alpha"),
        ("Gateway Router Beta", "Router-Beta", "Gateway Router Beta", "gateway_router_beta"),
        ("Compute Cluster Alpha", "Alpha Compute Pool", "CCA", "compute_cluster_alpha"),
        ("Storage Array Alpha", "Primary Storage Pool", "SAN-Alpha", "storage_array_alpha"),
        ("Gateway Router Beta", "Edge Gateway Beta", "GRB", "gateway_router_beta"),
    ]

    for i, (m1, m2, m3, target_id) in enumerate(arm2_cases, start=1):
        wid = f"world_r3r1_arm2_{i:02d}"
        d1_id = f"{wid}_doc_1"
        d2_id = f"{wid}_doc_2"

        doc1 = {
            "doc_id": d1_id,
            "source_id": f"src_eng_r3r1_a2_{i}_1",
            "mention": m1,
            "context": f"System status bulletin: Routing telemetry through {m1} under standard load.",
        }
        doc2 = {
            "doc_id": d2_id,
            "source_id": f"src_eng_r3r1_a2_{i}_2",
            "mention": m2,
            "context": f"Diagnostic inspection: Checking connectivity on {m2} to ensure reachability.",
        }

        worlds.append({"world_id": wid, "arm": "ARM2_KNOWN_ALIAS", "docs": [doc1, doc2]})

        gold_manifest[d1_id] = {
            "arm": "ARM2_KNOWN_ALIAS",
            "action": "LINK",
            "expected_target": target_id,
            "resolvable": True,
        }
        gold_manifest[d2_id] = {
            "arm": "ARM2_KNOWN_ALIAS",
            "action": "LINK",
            "expected_target": target_id,
            "resolvable": True,
        }

    # =========================================================================
    # ARM 3: Truly Fresh Structural Compositions with Discriminating Sub-IDs (15 Worlds, 30 Decisions)
    # Using fresh combinations: tray, lun, bay, socket, enclosure, slice with sub-identifiers (1..4, a..d)
    # =========================================================================
    arm3_templates = [
        ("Compute Cluster Alpha tray 1", "compute_cluster_alpha", "tray", "1", "prov_compute_cluster_alpha_tray_1"),
        ("Compute Cluster Alpha socket 2", "compute_cluster_alpha", "socket", "2", "prov_compute_cluster_alpha_socket_2"),
        ("Compute Cluster Beta enclosure a", "compute_cluster_beta", "enclosure", "a", "prov_compute_cluster_beta_enclosure_a"),
        ("Compute Cluster Beta slice b", "compute_cluster_beta", "slice", "b", "prov_compute_cluster_beta_slice_b"),
        ("Storage Array Alpha lun 1", "storage_array_alpha", "lun", "1", "prov_storage_array_alpha_lun_1"),
        ("Storage Array Alpha bay 3", "storage_array_alpha", "bay", "3", "prov_storage_array_alpha_bay_3"),
        ("Storage Array Beta lun 2", "storage_array_beta", "lun", "2", "prov_storage_array_beta_lun_2"),
        ("Storage Array Beta enclosure c", "storage_array_beta", "enclosure", "c", "prov_storage_array_beta_enclosure_c"),
        ("Gateway Router Alpha bay 1", "gateway_router_alpha", "bay", "1", "prov_gateway_router_alpha_bay_1"),
        ("Gateway Router Alpha socket d", "gateway_router_alpha", "socket", "d", "prov_gateway_router_alpha_socket_d"),
        ("Gateway Router Beta tray 2", "gateway_router_beta", "tray", "2", "prov_gateway_router_beta_tray_2"),
        ("Gateway Router Beta slice 4", "gateway_router_beta", "slice", "4", "prov_gateway_router_beta_slice_4"),
        ("Compute Cluster Alpha bay a", "compute_cluster_alpha", "bay", "a", "prov_compute_cluster_alpha_bay_a"),
        ("Storage Array Alpha tray b", "storage_array_alpha", "tray", "b", "prov_storage_array_alpha_tray_b"),
        ("Gateway Router Beta enclosure 1", "gateway_router_beta", "enclosure", "1", "prov_gateway_router_beta_enclosure_1"),
    ]

    for i, (mention, parent_id, marker, sub_id, prov_id) in enumerate(arm3_templates, start=1):
        wid = f"world_r3r1_arm3_{i:02d}"
        d1_id = f"{wid}_doc_1"
        d2_id = f"{wid}_doc_2"

        doc1 = {
            "doc_id": d1_id,
            "source_id": f"src_eng_r3r1_a3_{i}_1",
            "mention": mention,
            "context": f"Hardware allocation manifest: Provisioning structural sub-resource {mention} for dedicated workload.",
        }
        doc2 = {
            "doc_id": d2_id,
            "source_id": f"src_eng_r3r1_a3_{i}_2",
            "mention": mention,
            "context": f"Telemetry check: Monitoring utilization metrics on {mention} across continuous run.",
        }

        worlds.append({"world_id": wid, "arm": "ARM3_PARTITION", "docs": [doc1, doc2]})

        gold_manifest[d1_id] = {
            "arm": "ARM3_PARTITION",
            "action": "CREATE_PROVISIONAL",
            "expected_target": prov_id,
            "resolvable": True,
        }
        gold_manifest[d2_id] = {
            "arm": "ARM3_PARTITION",
            "action": "LINK",
            "expected_target": prov_id,
            "resolvable": True,
        }

    # =========================================================================
    # ARM 4A: Truly Fresh Permanent Adversarial Deferrals (8 Worlds, 16 Decisions)
    # Permanent unasserted / hypothetical / ambiguous mentions that must NEVER create entities or link
    # =========================================================================
    arm4a_adversarial_cases = [
        ("Ephemeral Cache Pool", "Proposal RFC-8801: Evaluating hypothetical Ephemeral Cache Pool for future tiering."),
        ("Uncommitted Fabric Gateway", "Engineering RFC: The uncommitted Fabric Gateway design remains under specification review."),
        ("Staged Test Accelerator", "Draft simulation model: Staged Test Accelerator parameters are mock instances for benchmarking."),
        ("Provisional Storage Mesh", "Architecture proposal: Proposed Provisional Storage Mesh has not received budget approval."),
        ("Hypothetical Micro-Node", "Discussion notes: Hypothetical Micro-Node architecture is pending feasibility review."),
        ("Simulated Border Switch", "Synthetic test harness: Simulated Border Switch telemetry is generated from mock scripts."),
        ("Draft Interconnect Bridge", "Specification draft: Draft Interconnect Bridge specification is rejected by standards board."),
        ("Unmapped Hardware Array", "Telemetry anomaly: Unmapped Hardware Array mention is an unspecified ephemeral event."),
    ]

    for i, (mention, context) in enumerate(arm4a_adversarial_cases, start=1):
        wid = f"world_r3r1_arm4a_{i:02d}"
        d1_id = f"{wid}_doc_1"
        d2_id = f"{wid}_doc_2"

        doc1 = {
            "doc_id": d1_id,
            "source_id": f"src_eng_r3r1_a4a_{i}_1",
            "mention": mention,
            "context": context,
        }
        doc2 = {
            "doc_id": d2_id,
            "source_id": f"src_eng_r3r1_a4a_{i}_2",
            "mention": mention,
            "context": f"Follow-up log: Re-evaluating {mention} under ongoing uncommitted exploration.",
        }

        worlds.append({"world_id": wid, "arm": "ARM4A_PERMANENT_DEFERRAL", "docs": [doc1, doc2]})

        gold_manifest[d1_id] = {
            "arm": "ARM4A_PERMANENT_DEFERRAL",
            "action": "DEFER",
            "expected_target": None,
            "resolvable": False,
        }
        gold_manifest[d2_id] = {
            "arm": "ARM4A_PERMANENT_DEFERRAL",
            "action": "DEFER",
            "expected_target": None,
            "resolvable": False,
        }

    # =========================================================================
    # ARM 4B: Truly Fresh Hypothesis Resolution & Precedence Cases (7 Worlds, 14 Decisions)
    # Genuinely fresh names exercising parenthetical resolution, disambiguation, and novel resolution
    # =========================================================================
    arm4b_cases = [
        # Case 1: Structural mention lacking sub-ID in Doc 1, resolved via registered parenthetical in Doc 2
        (
            "Storage Array Alpha Expansion Enclosure",
            "Engineering note: Inspecting Storage Array Alpha Expansion Enclosure for upcoming capacity review.",
            "Storage Array Alpha Expansion Enclosure (Primary Storage Pool)",
            "Maintenance log: Storage Array Alpha Expansion Enclosure (Primary Storage Pool) successfully synced.",
            "storage_array_alpha",
            "LINK",
        ),
        # Case 2: Ambiguous node in Doc 1, disambiguated to registered alias in Doc 2
        (
            "Unverified Host Pool",
            "Incident ticket: Unverified Host Pool reported degraded latency on interface 0.",
            "Unverified Host Pool (Cluster-Beta)",
            "Resolution log: Confirmed Unverified Host Pool refers to Cluster-Beta after routing check.",
            "compute_cluster_beta",
            "LINK",
        ),
        # Case 3: Structural blade lacking sub-ID in Doc 1, resolved to storage_array_beta in Doc 2
        (
            "Storage Array Beta Backup Bay",
            "Change ticket: Modifying configuration on Storage Array Beta Backup Bay.",
            "Storage Array Beta Backup Bay (SAN-Beta)",
            "Audit verification: Storage Array Beta Backup Bay (SAN-Beta) verified operational.",
            "storage_array_beta",
            "LINK",
        ),
        # Case 4: Ambiguous router port in Doc 1, resolved to gateway_router_alpha in Doc 2
        (
            "Pending Uplink Interface",
            "Network log: Pending Uplink Interface undergoing loopback testing.",
            "Router-Alpha",
            "Topology update: Pending Uplink Interface is now bound to Router-Alpha.",
            "gateway_router_alpha",
            "LINK",
        ),
        # Case 5: Ambiguous blade in Doc 1, resolved to compute_cluster_alpha in Doc 2
        (
            "Unallocated Server Blade",
            "Inventory check: Unallocated Server Blade located in staging rack.",
            "Cluster-Alpha",
            "Provisioning log: Unallocated Server Blade assigned to Cluster-Alpha.",
            "compute_cluster_alpha",
            "LINK",
        ),
        # Case 6: Uncommissioned module in Doc 1, officially commissioned as novel system in Doc 2
        (
            "Uncommissioned Photonic Transceiver",
            "Lab draft: Uncommissioned Photonic Transceiver under bench testing.",
            "Photonic Transceiver Omega",
            "Commissioning bulletin: Photonic Transceiver Omega is active in production.",
            "prov_photonic_transceiver_omega",
            "CREATE_PROVISIONAL",
        ),
        # Case 7: Unverified cluster in Doc 1, disambiguated to compute_cluster_beta in Doc 2
        (
            "Unconfirmed Compute Node",
            "Telemetry log: Unconfirmed Compute Node heartbeat observed on vlan 10.",
            "Beta Compute Pool",
            "Network audit: Unconfirmed Compute Node is part of Beta Compute Pool.",
            "compute_cluster_beta",
            "LINK",
        ),
    ]

    for i, (m1, c1, m2, c2, target_id, d2_action) in enumerate(arm4b_cases, start=1):
        wid = f"world_r3r1_arm4b_{i:02d}"
        d1_id = f"{wid}_doc_1"
        d2_id = f"{wid}_doc_2"

        doc1 = {"doc_id": d1_id, "source_id": f"src_eng_r3r1_a4b_{i}_1", "mention": m1, "context": c1}
        doc2 = {"doc_id": d2_id, "source_id": f"src_eng_r3r1_a4b_{i}_2", "mention": m2, "context": c2}

        worlds.append({"world_id": wid, "arm": "ARM4B_DISCONFIRMATION", "docs": [doc1, doc2]})

        # Doc 1 is ambiguous/unasserted -> DEFER
        gold_manifest[d1_id] = {
            "arm": "ARM4B_DISCONFIRMATION",
            "action": "DEFER",
            "expected_target": None,
            "resolvable": False,
        }
        # Doc 2 is resolvable
        gold_manifest[d2_id] = {
            "arm": "ARM4B_DISCONFIRMATION",
            "action": d2_action,
            "expected_target": target_id,
            "resolvable": True,
        }

    return worlds, gold_manifest


def normalize_audit_pair(mention: str, context: str) -> Tuple[str, str]:
    """Normalizes mention and context for rigorous disjointness audit."""
    m_norm = re.sub(r"[^a-z0-9]", "", mention.lower())
    c_norm = re.sub(r"[^a-z0-9]", "", context.lower())
    return m_norm, c_norm


def verify_r3r1_freshness_against_r3() -> Tuple[bool, Set[Tuple[str, str]]]:
    """Rigorous machine-verifiable freshness audit asserting disjointness

    between R3-R1 and frozen R3 across Arms 1, 3, 4A, and 4B.
    """
    from gene.benchmarks.r8_stage8c_r3.worlds import generate_stage8c_r3_worlds

    r3_worlds, _ = generate_stage8c_r3_worlds()
    r3r1_worlds, _ = generate_stage8c_r3_r1_worlds()

    r3_pairs: Set[Tuple[str, str]] = set()
    for w in r3_worlds:
        if w["arm"] in ("ARM1_NOVEL", "ARM3_PARTITION", "ARM4A_PERMANENT_DEFERRAL", "ARM4B_DISCONFIRMATION"):
            for d in w["docs"]:
                r3_pairs.add(normalize_audit_pair(d["mention"], d["context"]))

    r3r1_pairs: Set[Tuple[str, str]] = set()
    for w in r3r1_worlds:
        if w["arm"] in ("ARM1_NOVEL", "ARM3_PARTITION", "ARM4A_PERMANENT_DEFERRAL", "ARM4B_DISCONFIRMATION"):
            for d in w["docs"]:
                r3r1_pairs.add(normalize_audit_pair(d["mention"], d["context"]))

    overlap = r3r1_pairs.intersection(r3_pairs)
    is_fresh = (len(overlap) == 0)
    return is_fresh, overlap
