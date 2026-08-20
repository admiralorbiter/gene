"""Deterministic Unit & Invariant Tests for Experiment 1A Branching Transmission."""

import pytest
from gene.evaluation.dual_oracle import DualOracle, DualOracleEvaluation
from gene.evaluation.next_gen_matrix import NextGenMatrixEngine
from gene.worlds.exp1_branching import generate_exp1_branching_world
from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, Task, World, compute_fact_id


def test_oracle_functional_predicates_falsification():
    """Verify that all Exp 1 functional predicates evaluate to FALSE (not UNSUPPORTED) on incorrect alternatives."""
    bundle = generate_exp1_branching_world(world_seed=42, rotation_idx=0)
    clean_oracle = Oracle(bundle.clean_world)
    station = bundle.station

    # Clean supervisor is Kira -> PROTO_X7, CLEARANCE_OMEGA, ROUTE_HYPERLANE, TIER_PRIORITY, AUDIT_WEEKLY, ACCESS_UNRESTRICTED
    assert clean_oracle.evaluate_triple(station, "uses_protocol", "PROTO_X7") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "uses_protocol", "PROTO_Q2") == TruthStatus.FALSE  # Functional falsification!
    
    assert clean_oracle.evaluate_triple(station, "security_clearance", "CLEARANCE_OMEGA") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "security_clearance", "CLEARANCE_SIGMA") == TruthStatus.FALSE

    assert clean_oracle.evaluate_triple(station, "transit_route", "ROUTE_HYPERLANE") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "transit_route", "ROUTE_ORBITAL_SLIP") == TruthStatus.FALSE

    assert clean_oracle.evaluate_triple(station, "resource_tier", "TIER_PRIORITY") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "resource_tier", "TIER_STANDARD") == TruthStatus.FALSE

    assert clean_oracle.evaluate_triple(station, "audit_frequency", "AUDIT_WEEKLY") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "audit_frequency", "AUDIT_MONTHLY") == TruthStatus.FALSE

    assert clean_oracle.evaluate_triple(station, "access_level", "ACCESS_UNRESTRICTED") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "access_level", "ACCESS_ESCORT_ONLY") == TruthStatus.FALSE


def test_exp1_clean_world_multi_gen_closure():
    """Verify that clean world derives ground truth across all 3 generations."""
    bundle = generate_exp1_branching_world(world_seed=42, rotation_idx=0)
    clean_oracle = Oracle(bundle.clean_world)
    station = bundle.station

    # G1 derivations
    assert clean_oracle.evaluate_triple(station, "uses_protocol", "PROTO_X7") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "security_clearance", "CLEARANCE_OMEGA") == TruthStatus.TRUE

    # G2 derivations
    assert clean_oracle.evaluate_triple(station, "transit_route", "ROUTE_HYPERLANE") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "resource_tier", "TIER_PRIORITY") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "audit_frequency", "AUDIT_WEEKLY") == TruthStatus.TRUE
    assert clean_oracle.evaluate_triple(station, "access_level", "ACCESS_UNRESTRICTED") == TruthStatus.TRUE


def test_exp1_mutated_world_local_derivability_vs_canonical_truth():
    """Verify that mutated world derives local claims that evaluate to FALSE against canonical clean world."""
    bundle = generate_exp1_branching_world(world_seed=42, rotation_idx=0)
    clean_oracle = Oracle(bundle.clean_world)
    mut_oracle = Oracle(bundle.mutated_world)
    station = bundle.station

    # Mutated world has Tal -> PROTO_Q2, CLEARANCE_SIGMA, ROUTE_ORBITAL_SLIP, TIER_STANDARD, AUDIT_MONTHLY, ACCESS_ESCORT_ONLY
    # Locally derivable in mutated world:
    assert mut_oracle.evaluate_triple(station, "uses_protocol", "PROTO_Q2") == TruthStatus.TRUE
    assert mut_oracle.evaluate_triple(station, "security_clearance", "CLEARANCE_SIGMA") == TruthStatus.TRUE
    assert mut_oracle.evaluate_triple(station, "transit_route", "ROUTE_ORBITAL_SLIP") == TruthStatus.TRUE
    assert mut_oracle.evaluate_triple(station, "resource_tier", "TIER_STANDARD") == TruthStatus.TRUE
    assert mut_oracle.evaluate_triple(station, "audit_frequency", "AUDIT_MONTHLY") == TruthStatus.TRUE
    assert mut_oracle.evaluate_triple(station, "access_level", "ACCESS_ESCORT_ONLY") == TruthStatus.TRUE

    # BUT globally FALSE in canonical clean world:
    assert clean_oracle.evaluate_triple(station, "uses_protocol", "PROTO_Q2") == TruthStatus.FALSE
    assert clean_oracle.evaluate_triple(station, "security_clearance", "CLEARANCE_SIGMA") == TruthStatus.FALSE
    assert clean_oracle.evaluate_triple(station, "transit_route", "ROUTE_ORBITAL_SLIP") == TruthStatus.FALSE
    assert clean_oracle.evaluate_triple(station, "resource_tier", "TIER_STANDARD") == TruthStatus.FALSE
    assert clean_oracle.evaluate_triple(station, "audit_frequency", "AUDIT_MONTHLY") == TruthStatus.FALSE
    assert clean_oracle.evaluate_triple(station, "access_level", "ACCESS_ESCORT_ONLY") == TruthStatus.FALSE


def test_exp1_generational_firewall():
    """Verify that G2 task contexts maintain strict generational isolation from G0 founders and G1 rules."""
    bundle = generate_exp1_branching_world(world_seed=42, rotation_idx=0)
    station = bundle.station

    # Simulate admitted G1 protocol claim
    admitted_g1_protocol = Fact(
        subject=station,
        predicate="uses_protocol",
        object="PROTO_Q2",
        truth_value=True,
        source_type="derived",
        locus_id="locus_station_protocol",
    )

    # Filter G2.1 context (transit_route)
    g2_tmpl = bundle.g2_task_templates[0]
    g2_rules = [r for r in bundle.g2_rules if g2_tmpl["rules_filter"](r)]
    g2_context_facts = [admitted_g1_protocol] + [bundle.clean_world.facts[2]]  # distractor

    # Check Firewall Invariants:
    # 1. No reports_to or manager facts in G2 context
    assert not any(f.predicate in ("reports_to", "manager") for f in g2_context_facts)
    # 2. No G1 rules in G2 context
    assert not any(r.rule_id.startswith("RULE_G1_") for r in g2_rules)
    # 3. Exactly 3 competing G2 rules
    assert len(g2_rules) == 3


def test_dual_oracle_phenotype_classifications():
    """Verify that DualOracle correctly classifies the 5D state vector into all informational phenotypes."""
    bundle = generate_exp1_branching_world(world_seed=42, rotation_idx=0)
    station = bundle.station

    # Local context with PROTO_Q2 admitted
    admitted_g1_protocol = Fact(
        subject=station,
        predicate="uses_protocol",
        object="PROTO_Q2",
        truth_value=True,
        source_type="derived",
    )
    g2_tmpl = bundle.g2_task_templates[0]
    g2_rules = [r for r in bundle.g2_rules if g2_tmpl["rules_filter"](r)]
    context_world = World(
        world_id="test_ctx",
        world_seed=42,
        world_version="v2",
        facts=[admitted_g1_protocol],
        rules=g2_rules,
    )

    dual_oracle = DualOracle(
        canonical_world=bundle.clean_world,
        context_world=context_world,
        ancestral_seed_allele="TAL",
        allele_decoder=bundle.allele_decoder,
    )

    dummy_task = Task(
        task_id="test_g2_route",
        world_id=bundle.clean_world.world_id,
        query_type="rule_inference",
        target_fact=Fact(subject=station, predicate="transit_route", object="ROUTE_HYPERLANE"),
        reasoning_depth=2,
        prompt="Which transit route?",
        expected_answer="ROUTE_HYPERLANE",
        valid_support_path_ids=[],
    )

    # 1. Pure Semantic Infection (T*=0, D=1, A=1, E=1, K=1)
    res_sem = dual_oracle.evaluate_response(
        raw_text='{"evidence_status": "sufficient", "answer": {"subject": "VELORA", "predicate": "transit_route", "object": "Route Orbital Slip"}}',
        parsed_json={"evidence_status": "sufficient", "answer": {"subject": "VELORA", "predicate": "transit_route", "object": "Route Orbital Slip"}},
        task=dummy_task,
        has_infected_ancestry=True,
    )
    assert res_sem.phenotype == "semantic"
    assert res_sem.state_vector == (0, 1, 1, 1, 1)
    assert res_sem.ancestral_allele_fidelity == 1.0

    # 2. Epistemic Infection (T*=0, D=0, A=0, E=0, K=1) -> Model forces wrong answer without context support
    # Context with empty facts
    empty_context_world = World(world_id="test_empty", world_seed=42, world_version="v2", facts=[], rules=g2_rules)
    dual_oracle_empty = DualOracle(canonical_world=bundle.clean_world, context_world=empty_context_world, ancestral_seed_allele="TAL", allele_decoder=bundle.allele_decoder)
    res_epi = dual_oracle_empty.evaluate_response(
        raw_text='{"evidence_status": "sufficient", "answer": {"subject": "VELORA", "predicate": "transit_route", "object": "Route Direct Vector"}}',
        parsed_json={"evidence_status": "sufficient", "answer": {"subject": "VELORA", "predicate": "transit_route", "object": "Route Direct Vector"}},
        task=dummy_task,
        has_infected_ancestry=True,
    )
    assert res_epi.phenotype == "epistemic"
    assert res_epi.state_vector == (0, 0, 0, 0, 1)

    # 3. Control Failure (T*=0, D=0, A=0, E=1, K=0) -> Flags insufficient but emits token
    res_ctl = dual_oracle_empty.evaluate_response(
        raw_text='{"evidence_status": "insufficient", "answer": {"subject": "VELORA", "predicate": "transit_route", "object": "Route Direct Vector"}}',
        parsed_json={"evidence_status": "insufficient", "answer": {"subject": "VELORA", "predicate": "transit_route", "object": "Route Direct Vector"}},
        task=dummy_task,
        has_infected_ancestry=True,
    )
    assert res_ctl.phenotype == "control"
    assert res_ctl.state_vector == (0, 0, 0, 1, 0)

    # 4. Extinct (UNKNOWN abstention)
    res_ext = dual_oracle_empty.evaluate_response(
        raw_text='{"evidence_status": "insufficient", "answer": {"subject": "VELORA", "predicate": "transit_route", "object": "UNKNOWN"}}',
        parsed_json={"evidence_status": "insufficient", "answer": {"subject": "VELORA", "predicate": "transit_route", "object": "UNKNOWN"}},
        task=dummy_task,
        has_infected_ancestry=True,
    )
    assert res_ext.phenotype == "extinct"


def test_allele_decoding_and_fidelity():
    """Verify that all descendant symbols correctly decode to ancestral supervisor alleles."""
    bundle = generate_exp1_branching_world(world_seed=42, rotation_idx=0)
    decoder = bundle.allele_decoder

    # Kira symbols (clean founder)
    assert decoder["PROTO_X7"] == "KIRA"
    assert decoder["CLEARANCE_OMEGA"] == "KIRA"
    assert decoder["ROUTE_HYPERLANE"] == "KIRA"
    assert decoder["TIER_PRIORITY"] == "KIRA"
    assert decoder["AUDIT_WEEKLY"] == "KIRA"
    assert decoder["ACCESS_UNRESTRICTED"] == "KIRA"

    # Tal symbols (infected founder)
    assert decoder["PROTO_Q2"] == "TAL"
    assert decoder["CLEARANCE_SIGMA"] == "TAL"
    assert decoder["ROUTE_ORBITAL_SLIP"] == "TAL"
    assert decoder["TIER_STANDARD"] == "TAL"
    assert decoder["AUDIT_MONTHLY"] == "TAL"
    assert decoder["ACCESS_ESCORT_ONLY"] == "TAL"


def test_next_gen_matrix_partial_identifiability():
    """Verify that NextGenMatrixEngine correctly computes S-row and marks unobserved rows as N/A."""
    engine = NextGenMatrixEngine()

    # G0 -> G1 founder transmissions: 1 founder -> 2 semantic G1 children
    engine.record_transmission("node_F0", "node_G1_1", parent_gen=0, child_gen=1, parent_phenotype="founder", child_phenotype="semantic", ancestral_allele_fidelity=1.0)
    engine.record_transmission("node_F0", "node_G1_2", parent_gen=0, child_gen=1, parent_phenotype="founder", child_phenotype="semantic", ancestral_allele_fidelity=1.0)

    # G1 -> G2 semantic parent transmissions: 2 semantic parents -> 4 semantic G2 children
    engine.record_transmission("node_G1_1", "node_G2_1", parent_gen=1, child_gen=2, parent_phenotype="semantic", child_phenotype="semantic", ancestral_allele_fidelity=1.0)
    engine.record_transmission("node_G1_1", "node_G2_2", parent_gen=1, child_gen=2, parent_phenotype="semantic", child_phenotype="semantic", ancestral_allele_fidelity=1.0)
    engine.record_transmission("node_G1_2", "node_G2_3", parent_gen=1, child_gen=2, parent_phenotype="semantic", child_phenotype="semantic", ancestral_allele_fidelity=1.0)
    engine.record_transmission("node_G1_2", "node_G2_4", parent_gen=1, child_gen=2, parent_phenotype="semantic", child_phenotype="semantic", ancestral_allele_fidelity=1.0)

    summary = engine.compute_summary(founder_count=1)

    assert summary.founder_reproduction_R_F == 2.0
    assert summary.semantic_parent_reproduction_R_S == 2.0
    assert summary.epistemic_transmissibility_tau_S == 1.0
    assert summary.fidelity_G1_F1 == 1.0
    assert summary.fidelity_G2_F2 == 1.0

    # Row status: S is observed, E and C are unobserved
    assert summary.row_status["semantic"] == "observed"
    assert summary.row_status["epistemic"] == "unobserved"
    assert summary.row_status["control"] == "unobserved"

    # Spectral radius must be None (N/A) because E and C are unobserved!
    assert summary.spectral_radius is None
    assert summary.progeny_matrix["semantic"]["semantic"] == 2.0
    assert summary.progeny_matrix["semantic"]["epistemic"] == 0.0
    assert summary.progeny_matrix["semantic"]["control"] == 0.0
