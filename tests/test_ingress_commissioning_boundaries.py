"""Unit tests for literal commissioning keyword boundaries and hypothesis accumulation."""

import pytest
from gene.benchmarks.r8_stage8c_r3_r1.runner import (
    EpistemicIngressSessionR3R1,
    contains_literal_phrase,
)
from gene.benchmarks.r8_stage8c_r3_r1.worlds import get_stage8c_r3_r1_base_registry


def test_contains_literal_phrase_boundary_isolation():
    # 1. allocated vs unallocated
    assert contains_literal_phrase("node allocated to production rack", "allocated") is True
    assert contains_literal_phrase("unallocated compute node", "allocated") is False
    assert contains_literal_phrase("Inventory check: Unallocated Compute Node located in staging rack.", "allocated") is False

    # 2. commissioning vs decommissioning
    assert contains_literal_phrase("commissioning completed successfully", "commissioning") is True
    assert contains_literal_phrase("decommissioning completed yesterday", "commissioning") is False

    # 3. active in production vs inactive in production
    assert contains_literal_phrase("system is active in production tier", "active in production") is True
    assert contains_literal_phrase("system is inactive in production tier", "active in production") is False

    # 4. deployment vs redeployment
    assert contains_literal_phrase("initial deployment underway", "deployment") is True
    assert contains_literal_phrase("automated redeployment triggered", "deployment") is False


def test_production_session_unallocated_compute_node_defers():
    """Verifies that the production session sends World 5 Doc 1 through DEFER

    and initializes a world-local hypothesis rather than falsely creating a provisional entity.
    """
    base_reg = get_stage8c_r3_r1_base_registry()
    session = EpistemicIngressSessionR3R1(base_reg, world_id="world_r3r1_arm4b_05")

    # Doc 1
    doc1_decision = session.process_mention(
        doc_id="world_r3r1_arm4b_05_doc_1",
        source_id="src_eng_r3r1_a4b_5_1",
        mention="Unallocated Compute Node",
        context="Inventory check: Unallocated Compute Node located in staging rack.",
        neural_proposal={"candidate_action": "DEFER", "target_entity_id": None},
    )

    assert doc1_decision["action"] == "DEFER"
    assert doc1_decision["target_id"] is None
    assert "prov_unallocated_compute_node" not in session.durable_registry

    # Verify hypothesis ledger entry created
    hypo = session.hypothesis_ledger.get("world_r3r1_arm4b_05")
    assert hypo is not None
    assert hypo["status"] == "UNRESOLVED"
    assert hypo["surface_form"] == "Unallocated Compute Node"
    assert len(hypo["evidence_history"]) == 1

    # Doc 2 (Parenthetical disambiguation)
    doc2_decision = session.process_mention(
        doc_id="world_r3r1_arm4b_05_doc_2",
        source_id="src_eng_r3r1_a4b_5_2",
        mention="Unallocated Compute Node (Cluster-Alpha)",
        context="Provisioning log: Unallocated Compute Node (Cluster-Alpha) assigned to primary compute tier.",
        neural_proposal={"candidate_action": "LINK_EXISTING", "target_entity_id": "compute_cluster_alpha"},
    )

    assert doc2_decision["action"] == "LINK"
    assert doc2_decision["target_id"] == "compute_cluster_alpha"

    # Verify hypothesis ledger resolved
    assert hypo["status"] == "RESOLVED_EXISTING"
    assert hypo["resolved_target"] == "compute_cluster_alpha"
    assert hypo["resolving_doc_id"] == "world_r3r1_arm4b_05_doc_2"
    assert len(hypo["evidence_history"]) == 2
