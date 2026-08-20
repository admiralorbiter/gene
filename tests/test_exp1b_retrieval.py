"""Deterministic Unit & Invariant Tests for Experiment 1B-B Scored Retriever & Oracle Coupling."""

import pytest
from gene.evaluation.dual_oracle import DualOracle
from gene.memory.scored_retriever import BM25ScoredRetriever, tokenize
from gene.memory.store import MemoryNode
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.schema import Fact, World


def test_tokenize_normalization():
    """Verify that tokenizer normalizes and extracts alphanumeric tokens correctly."""
    tokens = tokenize("Station VELORA uses_protocol PROTO_Q2.")
    assert tokens == ["station", "velora", "uses_protocol", "proto_q2"]


def test_dual_oracle_d_ctx_requires_both_g1_premises():
    """Verify that DualOracle evaluates D_ctx=1 when both Fact A and Founder are present, and D_ctx=0 if either is missing."""
    bundle = generate_exp1_branching_world(world_seed=1001, rotation_idx=0, mutated_supervisor="TAL")
    task = bundle.g1_tasks[0]  # Protocol inference task
    
    # Premise 1: Station Manager (Fact A)
    fact_a = [f for f in bundle.mutated_world.facts if f.predicate == "manager"][0]
    # Premise 2: Reports To (Founder Fact)
    fact_founder = bundle.mutated_founder_fact
    
    mutated_val = bundle.allele_decoder.get("TAL", {}).get("protocol", "PROTO_Q2")
    
    # 1. BOTH premises present in context world -> D_ctx must be 1
    ctx_world_both = World(
        world_id="ctx_both",
        world_seed=1001,
        world_version="v2",
        facts=[fact_a, fact_founder],
        rules=bundle.g1_rules,
    )
    oracle_both = DualOracle(
        canonical_world=bundle.clean_world,
        context_world=ctx_world_both,
        ancestral_seed_allele="TAL",
        allele_decoder=bundle.allele_decoder,
    )
    res_both = oracle_both.evaluate_response(
        raw_text='{"evidence_status": "sufficient", "answer": {"subject": "' + bundle.station + '", "predicate": "protocol", "object": "' + mutated_val + '"}}',
        parsed_json={"evidence_status": "sufficient", "answer": {"subject": bundle.station, "predicate": "protocol", "object": mutated_val}},
        task=task,
        has_infected_ancestry=True,
    )
    assert res_both.context_derivability == 1, "D_ctx must be 1 when both support premises are retrieved"
    assert res_both.phenotype == "semantic"

    # 2. Missing Founder -> D_ctx must be 0
    ctx_world_no_founder = World(
        world_id="ctx_no_founder",
        world_seed=1001,
        world_version="v2",
        facts=[fact_a],
        rules=bundle.g1_rules,
    )
    oracle_no_founder = DualOracle(
        canonical_world=bundle.clean_world,
        context_world=ctx_world_no_founder,
        ancestral_seed_allele="TAL",
        allele_decoder=bundle.allele_decoder,
    )
    res_no_founder = oracle_no_founder.evaluate_response(
        raw_text='{"evidence_status": "sufficient", "answer": {"subject": "' + bundle.station + '", "predicate": "protocol", "object": "' + mutated_val + '"}}',
        parsed_json={"evidence_status": "sufficient", "answer": {"subject": bundle.station, "predicate": "protocol", "object": mutated_val}},
        task=task,
        has_infected_ancestry=True,
    )
    assert res_no_founder.context_derivability == 0, "D_ctx must be 0 when founder premise is missing"

    # 3. Missing Fact A -> D_ctx must be 0
    ctx_world_no_a = World(
        world_id="ctx_no_a",
        world_seed=1001,
        world_version="v2",
        facts=[fact_founder],
        rules=bundle.g1_rules,
    )
    oracle_no_a = DualOracle(
        canonical_world=bundle.clean_world,
        context_world=ctx_world_no_a,
        ancestral_seed_allele="TAL",
        allele_decoder=bundle.allele_decoder,
    )
    res_no_a = oracle_no_a.evaluate_response(
        raw_text='{"evidence_status": "sufficient", "answer": {"subject": "' + bundle.station + '", "predicate": "protocol", "object": "' + mutated_val + '"}}',
        parsed_json={"evidence_status": "sufficient", "answer": {"subject": bundle.station, "predicate": "protocol", "object": mutated_val}},
        task=task,
        has_infected_ancestry=True,
    )
    assert res_no_a.context_derivability == 0, "D_ctx must be 0 when Fact A is missing"


def test_paired_arm_stable_tie_breaking():
    """Verify that paired candidate slots receive identical ranking order regardless of allele string (KIRA vs TAL)."""
    retriever = BM25ScoredRetriever()

    # Zero lexical overlap query
    query = "What is the emergency beacon frequency of Sector 9?"

    clean_founder = MemoryNode(
        node_id="node_clean_founder_kira",
        run_id="run_clean",
        world_id="world_1",
        generation=0,
        locus_id="locus_reports_to",
        node_type="source",
        natural_text="Lyra directly reports to Kira.",
        structured_json={},
    )

    infected_founder = MemoryNode(
        node_id="node_inf_founder_tal",
        run_id="run_inf",
        world_id="world_1",
        generation=0,
        locus_id="locus_reports_to",
        node_type="source",
        natural_text="Lyra directly reports to Tal.",
        structured_json={},
    )

    distractor = MemoryNode(
        node_id="node_dist_1",
        run_id="run_clean",
        world_id="world_1",
        generation=0,
        locus_id="locus_dist_1",
        node_type="source",
        natural_text="Depot Zeta operates refueling bay 3.",
        structured_json={},
    )

    res_clean = retriever.rank(query=query, candidate_nodes=[clean_founder, distractor], top_k=2)
    res_inf = retriever.rank(query=query, candidate_nodes=[infected_founder, distractor], top_k=2)

    # Both clean and infected founders occupy the EXACT same retrieval rank
    assert res_clean.all_evaluated_candidates[0].paired_slot_id == res_inf.all_evaluated_candidates[0].paired_slot_id
    assert res_clean.all_evaluated_candidates[0].retrieval_rank == res_inf.all_evaluated_candidates[0].retrieval_rank


def test_hard_negatives_lexical_competition():
    """Verify that hard negatives with entity overlap score higher than easy clutter."""
    retriever = BM25ScoredRetriever()

    query = "Which security protocol does station Hyperion operate under?"

    # Hard negative: mentions Hyperion and protocol, but wrong relation
    hard_neg = MemoryNode(
        node_id="hard_neg_1",
        run_id="run_1",
        world_id="world_1",
        generation=0,
        locus_id="locus_hard_1",
        node_type="source",
        natural_text="Station Hyperion emergency_protocol is PROTO_DELTA.",
        structured_json={},
    )

    # Easy clutter: unrelated station and predicate
    easy_clutter = MemoryNode(
        node_id="easy_clutter_1",
        run_id="run_1",
        world_id="world_1",
        generation=0,
        locus_id="locus_easy_1",
        node_type="source",
        natural_text="Outpost Alpha radiation_shielding is REINFORCED.",
        structured_json={},
    )

    res = retriever.rank(query=query, candidate_nodes=[easy_clutter, hard_neg], top_k=2)
    assert res.all_evaluated_candidates[0].memory_id == "hard_neg_1"
    assert res.all_evaluated_candidates[0].bm25_score > res.all_evaluated_candidates[1].bm25_score


def test_surface_area_feedback_scaling():
    """Verify that scaling N_lineage descendants expands top-k lineage occupancy monotonically."""
    retriever = BM25ScoredRetriever()
    query = "Find information regarding Station VELORA operations and security."

    clean_nodes = [
        MemoryNode(
            node_id=f"clean_{i}",
            run_id="run_1",
            world_id="world_1",
            generation=0,
            locus_id=f"locus_clean_{i}",
            node_type="source",
            natural_text=f"Facility {i} operates standard maintenance cycle {i}.",
            structured_json={},
        )
        for i in range(10)
    ]

    # Test N_lineage in [0, 1, 3]
    for n_lineage in [0, 1, 3]:
        inf_nodes = [
            MemoryNode(
                node_id=f"inf_{i}",
                run_id="run_1",
                world_id="world_1",
                generation=1,
                locus_id=f"locus_inf_{i}",
                node_type="derived",
                natural_text=f"Station VELORA derived claim {i}.",
                structured_json={},
            )
            for i in range(n_lineage)
        ]
        inf_ids = {n.node_id for n in inf_nodes}
        res = retriever.rank(
            query=query,
            candidate_nodes=clean_nodes + inf_nodes,
            top_k=4,
            infected_node_ids=inf_ids,
        )
        assert res.num_infected_in_top_k == min(n_lineage, 4)


