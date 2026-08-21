"""Stage 6C Dataset & Manifest Generator.

Generates the balanced 12-case Natural Language Factual Observation benchmark
spanning 4 Predicate Contracts x 4 Temporal Update Scenarios with gold extractions,
gold state transitions, and gold downstream entitlement closures.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


def generate_stage6c_cases() -> list[dict]:
    cases = [
        # Case 1: TIME_VARYING Forward Update
        {
            "case_id": "C6C_01",
            "predicate_mode": "time_varying",
            "update_scenario": "forward_update",
            "natural_language_text": "Effective at cycle 10, Agent Alice was upgraded to clearance level Gamma.",
            "predicate_contract": {
                "predicate": "clearance",
                "cardinality": "SINGLE",
                "temporal_mode": "TIME_VARYING",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_01_init", "subject": "Agent_Alice", "predicate": "clearance", "object": "Value_Alpha", "t_valid_start": 0.0, "t_valid_end": None, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
                {"fact_id": "occ_C6C_01_aux", "subject": "Protocol_Omega", "predicate": "requires_clearance", "object": "Value_Gamma", "t_valid_start": 0.0, "t_valid_end": None, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_auth", "head": ["Agent_Alice", "authorized_for", "Protocol_Omega"], "body": [["Agent_Alice", "clearance", "Value_Gamma"], ["Protocol_Omega", "requires_clearance", "Value_Gamma"]]},
            ],
            "query": ["Agent_Alice", "authorized_for", "Protocol_Omega"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_GAMMA"],
            },
            "gold_extraction": {
                "subject": "Agent_Alice",
                "predicate": "clearance",
                "object": "Value_Gamma",
                "t_valid_start": 10.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_01_in", "secondary_fact_id": None, "t_valid_start": 10.0, "t_valid_end": None},
                {"event_type": "SUPERSEDES", "target_fact_id": "occ_C6C_01_in", "secondary_fact_id": "occ_C6C_01_init", "t_valid_start": 10.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 12.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 2: TIME_VARYING Retroactive Correction
        {
            "case_id": "C6C_02",
            "predicate_mode": "time_varying",
            "update_scenario": "retroactive_correction",
            "natural_language_text": "Correction: as of cycle 2, Agent Bob was assigned the role of Auditor, replacing the earlier report.",
            "predicate_contract": {
                "predicate": "role",
                "cardinality": "SINGLE",
                "temporal_mode": "TIME_VARYING",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_02_init", "subject": "Agent_Bob", "predicate": "role", "object": "Value_Analyst", "t_valid_start": 0.0, "t_valid_end": None, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_audit", "head": ["Agent_Bob", "duty", "ComplianceAudit"], "body": [["Agent_Bob", "role", "Value_Auditor"]]},
            ],
            "query": ["Agent_Bob", "duty", "ComplianceAudit"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_AUDIT"],
            },
            "gold_extraction": {
                "subject": "Agent_Bob",
                "predicate": "role",
                "object": "Value_Auditor",
                "t_valid_start": 2.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_02_in", "secondary_fact_id": None, "t_valid_start": 2.0, "t_valid_end": None},
                {"event_type": "SUPERSEDES", "target_fact_id": "occ_C6C_02_in", "secondary_fact_id": "occ_C6C_02_init", "t_valid_start": 2.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 4.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 3: TIME_VARYING Contemporaneous Dispute
        {
            "case_id": "C6C_03",
            "predicate_mode": "time_varying",
            "update_scenario": "contemporaneous_dispute",
            "natural_language_text": "At cycle 0, Field Sensor Alpha reported Server Node 1 status as Operational.",
            "predicate_contract": {
                "predicate": "status",
                "cardinality": "SINGLE",
                "temporal_mode": "TIME_VARYING",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_03_init", "subject": "Server_Node_1", "predicate": "status", "object": "Value_Degraded", "t_valid_start": 0.0, "t_valid_end": None, "source_id": "source_beta", "origin_id": "origin_sensor_2", "lineage_roots": ["R_BETA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_route", "head": ["Server_Node_1", "traffic", "RouteNormal"], "body": [["Server_Node_1", "status", "Value_Operational"]]},
            ],
            "query": ["Server_Node_1", "traffic", "RouteNormal"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_ALPHA"],
            },
            "gold_extraction": {
                "subject": "Server_Node_1",
                "predicate": "status",
                "object": "Value_Operational",
                "t_valid_start": 0.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_03_in", "secondary_fact_id": None, "t_valid_start": 0.0, "t_valid_end": None},
                {"event_type": "CONTRADICTS", "target_fact_id": "occ_C6C_03_in", "secondary_fact_id": "occ_C6C_03_init", "t_valid_start": 0.0, "t_valid_end": float("inf")},
            ],
            "evaluation_coordinates": {"t_valid": 0.0, "t_knowledge": 1},
            "expected_entitlement": False,
        },

        # Case 4: TIME_VARYING Recurrence / Reinstatement
        {
            "case_id": "C6C_04",
            "predicate_mode": "time_varying",
            "update_scenario": "recurrence_reinstatement",
            "natural_language_text": "At cycle 15, Agent Alice returned to Sector 7.",
            "predicate_contract": {
                "predicate": "zone",
                "cardinality": "SINGLE",
                "temporal_mode": "TIME_VARYING",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_04_init", "subject": "Agent_Alice", "predicate": "zone", "object": "Value_Sector7", "t_valid_start": 0.0, "t_valid_end": 5.0, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_sec", "head": ["Agent_Alice", "mission_assigned", "Sector7Patrol"], "body": [["Agent_Alice", "zone", "Value_Sector7"]]},
            ],
            "query": ["Agent_Alice", "mission_assigned", "Sector7Patrol"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_ALPHA"],
            },
            "gold_extraction": {
                "subject": "Agent_Alice",
                "predicate": "zone",
                "object": "Value_Sector7",
                "t_valid_start": 15.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_04_in", "secondary_fact_id": None, "t_valid_start": 15.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 16.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 5: ADDITIVE Forward Addition
        {
            "case_id": "C6C_05",
            "predicate_mode": "additive",
            "update_scenario": "forward_update",
            "natural_language_text": "At cycle 4, Engineer Dave acquired proficiency in Cryptography.",
            "predicate_contract": {
                "predicate": "certified_skill",
                "cardinality": "MULTI",
                "temporal_mode": "ADDITIVE",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_05_init", "subject": "Engineer_Dave", "predicate": "certified_skill", "object": "Value_Python", "t_valid_start": 0.0, "t_valid_end": None, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_lead", "head": ["Engineer_Dave", "role_qualified", "CryptoArchitect"], "body": [["Engineer_Dave", "certified_skill", "Value_Python"], ["Engineer_Dave", "certified_skill", "Value_Cryptography"]]},
            ],
            "query": ["Engineer_Dave", "role_qualified", "CryptoArchitect"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_CRYPTO"],
            },
            "gold_extraction": {
                "subject": "Engineer_Dave",
                "predicate": "certified_skill",
                "object": "Value_Cryptography",
                "t_valid_start": 4.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_05_in", "secondary_fact_id": None, "t_valid_start": 4.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 5.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 6: ADDITIVE Retroactive Addition
        {
            "case_id": "C6C_06",
            "predicate_mode": "additive",
            "update_scenario": "retroactive_correction",
            "natural_language_text": "Backfilled training log: as of cycle 1, Engineer Dave also held certification in NetworkSecurity.",
            "predicate_contract": {
                "predicate": "certified_skill",
                "cardinality": "MULTI",
                "temporal_mode": "ADDITIVE",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_06_init", "subject": "Engineer_Dave", "predicate": "certified_skill", "object": "Value_Python", "t_valid_start": 0.0, "t_valid_end": None, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_secguard", "head": ["Engineer_Dave", "role_qualified", "SecurityAuditor"], "body": [["Engineer_Dave", "certified_skill", "Value_Python"], ["Engineer_Dave", "certified_skill", "Value_NetworkSecurity"]]},
            ],
            "query": ["Engineer_Dave", "role_qualified", "SecurityAuditor"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_NETSEC"],
            },
            "gold_extraction": {
                "subject": "Engineer_Dave",
                "predicate": "certified_skill",
                "object": "Value_NetworkSecurity",
                "t_valid_start": 1.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_06_in", "secondary_fact_id": None, "t_valid_start": 1.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 2.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 7: ADDITIVE Contemporaneous Addition
        {
            "case_id": "C6C_07",
            "predicate_mode": "additive",
            "update_scenario": "contemporaneous_addition",
            "natural_language_text": "At cycle 0, Security Team reported Agent Carol was equipped with QuantumKey.",
            "predicate_contract": {
                "predicate": "authorized_tool",
                "cardinality": "MULTI",
                "temporal_mode": "ADDITIVE",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_07_init", "subject": "Agent_Carol", "predicate": "authorized_tool", "object": "Value_BioScanner", "t_valid_start": 0.0, "t_valid_end": None, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_ops", "head": ["Agent_Carol", "clearance_tier", "TacticalOps"], "body": [["Agent_Carol", "authorized_tool", "Value_BioScanner"], ["Agent_Carol", "authorized_tool", "Value_QuantumKey"]]},
            ],
            "query": ["Agent_Carol", "clearance_tier", "TacticalOps"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_beta",
                "origin_id": "origin_sensor_2",
                "lineage_roots": ["R_QKEY"],
            },
            "gold_extraction": {
                "subject": "Agent_Carol",
                "predicate": "authorized_tool",
                "object": "Value_QuantumKey",
                "t_valid_start": 0.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_07_in", "secondary_fact_id": None, "t_valid_start": 0.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 0.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 8: ADDITIVE Reassertion / Renewal
        {
            "case_id": "C6C_08",
            "predicate_mode": "additive",
            "update_scenario": "reassertion_renewal",
            "natural_language_text": "At cycle 12, Engineer Dave renewed certification in PythonArchitecture.",
            "predicate_contract": {
                "predicate": "certified_skill",
                "cardinality": "MULTI",
                "temporal_mode": "ADDITIVE",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_08_init", "subject": "Engineer_Dave", "predicate": "certified_skill", "object": "Value_PythonArchitecture", "t_valid_start": 0.0, "t_valid_end": 5.0, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_arch", "head": ["Engineer_Dave", "status", "ActiveArchitect"], "body": [["Engineer_Dave", "certified_skill", "Value_PythonArchitecture"]]},
            ],
            "query": ["Engineer_Dave", "status", "ActiveArchitect"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_ALPHA"],
            },
            "gold_extraction": {
                "subject": "Engineer_Dave",
                "predicate": "certified_skill",
                "object": "Value_PythonArchitecture",
                "t_valid_start": 12.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_08_in", "secondary_fact_id": None, "t_valid_start": 12.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 14.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 9: EPISODIC Forward Point Event
        {
            "case_id": "C6C_09",
            "predicate_mode": "episodic",
            "update_scenario": "forward_point_event",
            "natural_language_text": "At cycle 8, Agent Eve accessed Terminal Vault 4.",
            "predicate_contract": {
                "predicate": "logged_access",
                "cardinality": "MULTI",
                "temporal_mode": "EPISODIC",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_09_init", "subject": "Agent_Eve", "predicate": "logged_access", "object": "Value_Vault1", "t_valid_start": 2.0, "t_valid_end": None, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_vaults", "head": ["Agent_Eve", "audit_flag", "DualVaultVisitor"], "body": [["Agent_Eve", "logged_access", "Value_Vault1"], ["Agent_Eve", "logged_access", "Value_Vault4"]]},
            ],
            "query": ["Agent_Eve", "audit_flag", "DualVaultVisitor"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_VAULT4"],
            },
            "gold_extraction": {
                "subject": "Agent_Eve",
                "predicate": "logged_access",
                "object": "Value_Vault4",
                "t_valid_start": 8.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_09_in", "secondary_fact_id": None, "t_valid_start": 8.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 8.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 10: EPISODIC Retroactive Point Event
        {
            "case_id": "C6C_10",
            "predicate_mode": "episodic",
            "update_scenario": "retroactive_point_event",
            "natural_language_text": "Forensic discovery: at cycle 3, a critical threshold breach occurred at Gateway 2.",
            "predicate_contract": {
                "predicate": "audit_alert",
                "cardinality": "MULTI",
                "temporal_mode": "EPISODIC",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": None,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_10_init", "subject": "Gateway_2", "predicate": "monitored", "object": "Value_True", "t_valid_start": 0.0, "t_valid_end": None, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_breach", "head": ["Gateway_2", "security_tier", "Compromised"], "body": [["Gateway_2", "audit_alert", "Value_ThresholdBreach"]]},
            ],
            "query": ["Gateway_2", "security_tier", "Compromised"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_ALERT"],
            },
            "gold_extraction": {
                "subject": "Gateway_2",
                "predicate": "audit_alert",
                "object": "Value_ThresholdBreach",
                "t_valid_start": 3.0,
                "t_valid_end": None,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_10_in", "secondary_fact_id": None, "t_valid_start": 3.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 3.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 11: INTERVAL_BOUNDED Forward Interval
        {
            "case_id": "C6C_11",
            "predicate_mode": "interval_bounded",
            "update_scenario": "forward_update",
            "natural_language_text": "Beginning at cycle 5 and valid until cycle 10, Vehicle 9 is leased to Transport Unit 3.",
            "predicate_contract": {
                "predicate": "active_lease",
                "cardinality": "SINGLE",
                "temporal_mode": "INTERVAL_BOUNDED",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": 5.0,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_11_init", "subject": "Vehicle_9", "predicate": "active_lease", "object": "Value_TransportUnit1", "t_valid_start": 0.0, "t_valid_end": 5.0, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_lease", "head": ["Vehicle_9", "assigned_mission", "TransportMissionAlpha"], "body": [["Vehicle_9", "active_lease", "Value_TransportUnit3"]]},
            ],
            "query": ["Vehicle_9", "assigned_mission", "TransportMissionAlpha"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_alpha",
                "origin_id": "origin_sensor_1",
                "lineage_roots": ["R_LEASE3"],
            },
            "gold_extraction": {
                "subject": "Vehicle_9",
                "predicate": "active_lease",
                "object": "Value_TransportUnit3",
                "t_valid_start": 5.0,
                "t_valid_end": 10.0,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_11_in", "secondary_fact_id": None, "t_valid_start": 5.0, "t_valid_end": 10.0},
                {"event_type": "SUPERSEDES", "target_fact_id": "occ_C6C_11_in", "secondary_fact_id": "occ_C6C_11_init", "t_valid_start": 5.0, "t_valid_end": None},
            ],
            "evaluation_coordinates": {"t_valid": 7.0, "t_knowledge": 1},
            "expected_entitlement": True,
        },

        # Case 12: INTERVAL_BOUNDED Contemporaneous Dispute
        {
            "case_id": "C6C_12",
            "predicate_mode": "interval_bounded",
            "update_scenario": "contemporaneous_dispute",
            "natural_language_text": "At cycle 0 for 5 cycles, Fleet Log Beta recorded Vehicle 9 assigned to Transport Unit 4.",
            "predicate_contract": {
                "predicate": "active_lease",
                "cardinality": "SINGLE",
                "temporal_mode": "INTERVAL_BOUNDED",
                "conflict_policy": "ISOLATE_CONTEMPORANEOUS_DISPUTES",
                "default_duration": 5.0,
            },
            "initial_facts": [
                {"fact_id": "occ_C6C_12_init", "subject": "Vehicle_9", "predicate": "active_lease", "object": "Value_TransportUnit1", "t_valid_start": 0.0, "t_valid_end": 5.0, "source_id": "source_alpha", "origin_id": "origin_sensor_1", "lineage_roots": ["R_ALPHA"]},
            ],
            "initial_rules": [
                {"rule_id": "r_lease4", "head": ["Vehicle_9", "assigned_mission", "TransportMissionBeta"], "body": [["Vehicle_9", "active_lease", "Value_TransportUnit4"]]},
            ],
            "query": ["Vehicle_9", "assigned_mission", "TransportMissionBeta"],
            "trusted_metadata": {
                "t_knowledge": 1,
                "source_id": "source_beta",
                "origin_id": "origin_sensor_2",
                "lineage_roots": ["R_LEASE4"],
            },
            "gold_extraction": {
                "subject": "Vehicle_9",
                "predicate": "active_lease",
                "object": "Value_TransportUnit4",
                "t_valid_start": 0.0,
                "t_valid_end": 5.0,
            },
            "gold_transitions": [
                {"event_type": "ASSERT", "target_fact_id": "occ_C6C_12_in", "secondary_fact_id": None, "t_valid_start": 0.0, "t_valid_end": 5.0},
                {"event_type": "CONTRADICTS", "target_fact_id": "occ_C6C_12_in", "secondary_fact_id": "occ_C6C_12_init", "t_valid_start": 0.0, "t_valid_end": float("inf")},
            ],
            "evaluation_coordinates": {"t_valid": 2.0, "t_knowledge": 1},
            "expected_entitlement": False,
        },
    ]
    return cases


def main() -> None:
    cases = generate_stage6c_cases()
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    jsonl_path = data_dir / "exploration_round6_stage6c_cases.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    hasher = hashlib.sha256()
    hasher.update(jsonl_path.read_bytes())
    cases_sha = hasher.hexdigest()

    manifest = {
        "manifest_version": "1.0.0",
        "stage": "Exploration Round 6 Stage 6C",
        "assay_name": "Neural Semantic Observation Extraction & Upward Error Migration Assay",
        "dataset_file": jsonl_path.name,
        "dataset_sha256": cases_sha,
        "total_cases": len(cases),
        "predicate_modes_covered": ["time_varying", "additive", "episodic", "interval_bounded"],
        "update_scenarios_covered": ["forward_update", "retroactive_correction", "contemporaneous_dispute", "recurrence_reinstatement", "contemporaneous_addition", "reassertion_renewal", "forward_point_event", "retroactive_point_event"],
        "pinned_model": "gemma3:12b",
        "pinned_digest": "f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a",
        "call_budget": {
            "arm_n1_direct_transition": 12,
            "arm_n2_observation_extraction": 12,
            "replay_canaries": 4,
            "arm_c0_oracle_ceiling": 0,
            "total_live_calls": 28,
        },
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    manifest_path = data_dir / "exploration_round6_stage6c_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(cases)} Stage 6C cases -> {jsonl_path}")
    print(f"Generated Stage 6C manifest -> {manifest_path} (SHA256: {cases_sha})")


if __name__ == "__main__":
    main()
