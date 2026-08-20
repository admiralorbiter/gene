"""Preflight tests for Track A2: Dynamic Memory Repair."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.dynamic_repair import DynamicMemoryStore, DynamicRepairMetrics


def test_dynamic_memory_store_policies(tmp_path: Path):
    """Verify state transitions and exact metric tracking across the 3 repair policies."""
    db_file = tmp_path / "test_dynamic.db"
    store = DynamicMemoryStore(db_file)

    # Populate initial infected DAG: G0 (TAL) -> G1 (PROTO_Q2) -> G2 (ROUTE_BETA)
    store.insert_node("mem_g0_root", "VELORA", "founder", "TAL", [])
    store.insert_node("mem_g1_protocol", "VELORA", "protocol", "PROTO_Q2", ["mem_g0_root"])
    store.insert_node("mem_g2_route", "VELORA", "route", "ROUTE_BETA", ["mem_g1_protocol"])

    # 1. Test Policy 1: Root Overwrite
    m1 = store.update_root_overwrite("mem_g0_root", "KIRA")
    assert m1.policy == "root_overwrite"
    assert m1.nodes_inspected == 1
    assert m1.claims_recomputed == 0

    # 2. Test Policy 3: Lazy Mark Dirty
    m3 = store.update_lazy_revalidate_mark_dirty("mem_g0_root", "KIRA")
    assert m3.policy == "lazy_revalidation"
    assert m3.support_sets_invalidated == 2
    assert m3.claims_recomputed == 0

    # 3. Test Policy 2: Eager Repair
    m2 = store.update_eager_repair("mem_g0_root", "KIRA")
    assert m2.policy == "eager_repair"
    assert m2.claims_recomputed == 2
