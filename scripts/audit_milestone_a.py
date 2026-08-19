"""Milestone A verification script: Audit 10 procedural worlds and verify all invariants."""

from __future__ import annotations

import sys
from gene.worlds.generator import WorldGenerator
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.tasks import TaskGenerator


def audit_milestone_a(num_worlds: int = 10) -> bool:
    print(f"============================================================")
    print(f"       GENE MILESTONE A AUDIT: {num_worlds} PROCEDURAL WORLDS")
    print(f"============================================================")

    all_passed = True

    for i in range(num_worlds):
        seed = 1000 + i * 17
        print(f"\n--- [World {i+1}/{num_worlds}] Seed: {seed} ---")

        # 1. Test Seed Reproducibility
        w1 = WorldGenerator.generate(seed)
        w2 = WorldGenerator.generate(seed)
        if w1.validation_hash() != w2.validation_hash() or w1.canonical_json() != w2.canonical_json():
            print(f"  [FAIL] Seed reproducibility failed for seed {seed}")
            all_passed = False
            continue
        print(f"  [PASS] Deterministic World Hash: {w1.validation_hash()[:16]}...")

        # 2. Test Clean/Mutated Paired Invariant
        clean_w, mut_w, mutation = WorldGenerator.generate_paired(seed)
        clean_ids = {f.fact_id for f in clean_w.facts}
        mut_ids = {f.fact_id for f in mut_w.facts}
        clean_diff = clean_ids - mut_ids
        mut_diff = mut_ids - clean_ids

        if len(clean_diff) != 1 or len(mut_diff) != 1:
            print(f"  [FAIL] Pair invariant failed: clean_diff={len(clean_diff)}, mut_diff={len(mut_diff)}")
            all_passed = False
            continue
        if list(clean_diff)[0] != mutation.true_fact.fact_id or list(mut_diff)[0] != mutation.mutated_fact.fact_id:
            print(f"  [FAIL] Mutation spec does not match fact set difference")
            all_passed = False
            continue
        print(f"  [PASS] Clean/Mutated pair invariant: strictly 1 fact mutated ({mutation.true_fact.triple} -> {mutation.mutated_fact.triple})")

        # 3. Test Oracle Closure & Support Path Recovery
        oracle = Oracle(clean_w)
        tasks = TaskGenerator.generate_all_tasks(clean_w, oracle)
        d0_tasks = [t for t in tasks if t.reasoning_depth == 0]
        d1_tasks = [t for t in tasks if t.reasoning_depth == 1]

        print(f"  [INFO] Closure Facts: {len(oracle.closure_facts)} (Source: {len(clean_w.facts)}, Derived: {len(oracle.closure_facts) - len(clean_w.facts)})")
        print(f"  [INFO] Benchmark Tasks: {len(tasks)} (D0: {len(d0_tasks)}, D1: {len(d1_tasks)})")

        for task in tasks:
            truth = oracle.evaluate_claim(task.target_fact)
            if truth != TruthStatus.TRUE:
                print(f"  [FAIL] Task {task.task_id} evaluated to {truth}, expected TRUE")
                all_passed = False
            if not task.valid_support_path_ids:
                print(f"  [FAIL] Task {task.task_id} has empty support paths")
                all_passed = False

        print(f"  [PASS] All {len(tasks)} tasks have unambiguous TRUE oracle ground truth & recoverable support paths.")

    print(f"\n============================================================")
    if all_passed:
        print(f"  ALL {num_worlds} WORLDS PASSED MILESTONE A VERIFICATION!")
    else:
        print(f"  VERIFICATION FAILED ON ONE OR MORE INVARIANTS.")
    print(f"============================================================\n")

    return all_passed


if __name__ == "__main__":
    success = audit_milestone_a(10)
    sys.exit(0 if success else 1)
