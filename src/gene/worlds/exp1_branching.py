"""Experiment 1A Multi-Generation Branching World Generator.

Generates paired clean and mutated micro-worlds for Experiment 1A (Controlled Branching Transmission):
- 3-generation genealogy: G0 (founder allele) -> G1 (2 child tasks) -> G2 (4 grandchild tasks).
- Branching factor b=2, strictly single-parent genealogy per task.
- Generational isolation / firewalling: G2 tasks see only the admitted G1 parent claim + depth-2 rules + clean distractors.
- Competing opaque consequents at all depths (Ecology C).
- Symbolic allele decoder for exact ancestral fidelity tracking (F_g).
"""

from __future__ import annotations

import itertools
from typing import Any, Literal
from pydantic import BaseModel

from gene.worlds.schema import Fact, Rule, Task, World, compute_fact_id


SUPERVISORS = ["KIRA", "TAL", "MIRA"]
STATIONS = ["VELORA", "KESTREL", "HYPERION", "VANGUARD"]
MANAGERS = ["NERIN", "KAEL", "LYRA", "VANCE"]

# Depth 1 Consequents (Rotated under rotation_idx)
PROTOCOLS = ["PROTO_X7", "PROTO_Q2", "PROTO_M9"]
CLEARANCES = ["CLEARANCE_OMEGA", "CLEARANCE_SIGMA", "CLEARANCE_DELTA"]

# Depth 2 Consequents (Rotated under rotation_idx)
ROUTES = ["ROUTE_HYPERLANE", "ROUTE_ORBITAL_SLIP", "ROUTE_DIRECT_VECTOR"]
RESOURCES = ["TIER_PRIORITY", "TIER_STANDARD", "TIER_RESTRICTED"]
AUDITS = ["AUDIT_WEEKLY", "AUDIT_MONTHLY", "AUDIT_QUARTERLY"]
ACCESSES = ["ACCESS_UNRESTRICTED", "ACCESS_ESCORT_ONLY", "ACCESS_ISOLATED"]


class BranchingWorldBundle(BaseModel):
    """Paired clean and mutated branching world bundle with 3-generation task suite."""
    clean_world: World
    mutated_world: World
    clean_founder_fact: Fact
    mutated_founder_fact: Fact
    station: str
    manager: str
    target_supervisor: str
    mutated_supervisor: str
    g1_tasks: list[Task]
    g2_task_templates: list[dict[str, Any]]
    g1_rules: list[Rule]
    g2_rules: list[Rule]
    allele_decoder: dict[str, str]


def generate_exp1_branching_world(
    world_seed: int = 42,
    rotation_idx: int = 0,
    rule_perm_idx: int = 0,
) -> BranchingWorldBundle:
    """Generate a paired clean/mutated 3-generation branching world bundle."""
    # Rotate consequents for supervisor mapping
    # Kira -> index 0, Tal -> index 1, Mira -> index 2
    r_idx = rotation_idx % 3
    r_protos = PROTOCOLS[r_idx:] + PROTOCOLS[:r_idx]
    r_clears = CLEARANCES[r_idx:] + CLEARANCES[:r_idx]
    r_routes = ROUTES[r_idx:] + ROUTES[:r_idx]
    r_res = RESOURCES[r_idx:] + RESOURCES[:r_idx]
    r_audits = AUDITS[r_idx:] + AUDITS[:r_idx]
    r_access = ACCESSES[r_idx:] + ACCESSES[:r_idx]

    sup_to_proto = {sup: proto for sup, proto in zip(SUPERVISORS, r_protos)}
    sup_to_clear = {sup: clear for sup, clear in zip(SUPERVISORS, r_clears)}
    proto_to_route = {proto: route for proto, route in zip(r_protos, r_routes)}
    proto_to_res = {proto: res for proto, res in zip(r_protos, r_res)}
    clear_to_audit = {clear: audit for clear, audit in zip(r_clears, r_audits)}
    clear_to_access = {clear: acc for clear, acc in zip(r_clears, r_access)}

    # Reverse allele decoder mapping any descendant symbol back to ancestral supervisor
    allele_decoder: dict[str, str] = {}
    for sup in SUPERVISORS:
        p = sup_to_proto[sup]
        c = sup_to_clear[sup]
        allele_decoder[p] = sup
        allele_decoder[c] = sup
        allele_decoder[proto_to_route[p]] = sup
        allele_decoder[proto_to_res[p]] = sup
        allele_decoder[clear_to_audit[c]] = sup
        allele_decoder[clear_to_access[c]] = sup

    station = STATIONS[world_seed % len(STATIONS)]
    manager = MANAGERS[world_seed % len(MANAGERS)]
    clean_supervisor = SUPERVISORS[0]   # KIRA
    mutated_supervisor = SUPERVISORS[1] # TAL

    # G0 Source facts
    fact_a = Fact(
        subject=station,
        predicate="manager",
        object=manager,
        truth_value=True,
        source_type="generated",
        fact_id=compute_fact_id(station, "manager", manager),
        locus_id="locus_station_manager",
    )
    clean_founder_fact = Fact(
        subject=manager,
        predicate="reports_to",
        object=clean_supervisor,
        truth_value=True,
        source_type="generated",
        fact_id=compute_fact_id(manager, "reports_to", clean_supervisor),
        locus_id="locus_manager_supervisor",
    )
    mutated_founder_fact = Fact(
        subject=manager,
        predicate="reports_to",
        object=mutated_supervisor,
        truth_value=True,
        source_type="mutated",
        fact_id=compute_fact_id(manager, "reports_to", mutated_supervisor),
        locus_id="locus_manager_supervisor",
    )

    # Distractor facts
    dist_station = STATIONS[(world_seed + 1) % len(STATIONS)]
    dist_fact_1 = Fact(
        subject=dist_station,
        predicate="located_in",
        object="SECTOR_ALPHA",
        truth_value=True,
        source_type="generated",
        fact_id=compute_fact_id(dist_station, "located_in", "SECTOR_ALPHA"),
        locus_id="locus_distractor_1",
    )
    dist_fact_2 = Fact(
        subject=dist_station,
        predicate="opened_in",
        object="2188",
        truth_value=True,
        source_type="generated",
        fact_id=compute_fact_id(dist_station, "opened_in", "2188"),
        locus_id="locus_distractor_2",
    )

    # -------------------------------------------------------------
    # Depth-1 Competing Rules (G0 -> G1)
    # -------------------------------------------------------------
    g1_rules: list[Rule] = []
    for sup in SUPERVISORS:
        # Rule 1: uses_protocol
        p = sup_to_proto[sup]
        g1_rules.append(Rule(
            rule_id=f"RULE_G1_PROTOCOL_{sup}_{p}",
            antecedents=[
                ("?station", "manager", "?person"),
                ("?person", "reports_to", sup),
            ],
            consequent=("?station", "uses_protocol", p),
            depth=1,
            description=f"Protocol Directive: If ?person manages ?station and ?person reports to {sup.title()}, then ?station operates under {p}.",
        ))
        # Rule 2: security_clearance
        c = sup_to_clear[sup]
        g1_rules.append(Rule(
            rule_id=f"RULE_G1_CLEARANCE_{sup}_{c}",
            antecedents=[
                ("?station", "manager", "?person"),
                ("?person", "reports_to", sup),
            ],
            consequent=("?station", "security_clearance", c),
            depth=1,
            description=f"Clearance Directive: If ?person manages ?station and ?person reports to {sup.title()}, then ?station is assigned {c}.",
        ))

    # -------------------------------------------------------------
    # Depth-2 Competing Rules (G1 -> G2)
    # -------------------------------------------------------------
    g2_rules: list[Rule] = []
    # From uses_protocol -> transit_route and resource_tier
    for proto in r_protos:
        r_out = proto_to_route[proto]
        res_out = proto_to_res[proto]
        g2_rules.append(Rule(
            rule_id=f"RULE_G2_ROUTE_{proto}_{r_out}",
            antecedents=[("?station", "uses_protocol", proto)],
            consequent=("?station", "transit_route", r_out),
            depth=2,
            description=f"Logistics Policy: If ?station operates under {proto}, its primary transit corridor is {r_out}.",
        ))
        g2_rules.append(Rule(
            rule_id=f"RULE_G2_RESOURCE_{proto}_{res_out}",
            antecedents=[("?station", "uses_protocol", proto)],
            consequent=("?station", "resource_tier", res_out),
            depth=2,
            description=f"Resource Policy: If ?station operates under {proto}, its resource allocation tier is {res_out}.",
        ))

    # From security_clearance -> audit_frequency and access_level
    for clear in r_clears:
        audit_out = clear_to_audit[clear]
        acc_out = clear_to_access[clear]
        g2_rules.append(Rule(
            rule_id=f"RULE_G2_AUDIT_{clear}_{audit_out}",
            antecedents=[("?station", "security_clearance", clear)],
            consequent=("?station", "audit_frequency", audit_out),
            depth=2,
            description=f"Audit Policy: If ?station holds {clear}, its mandatory compliance frequency is {audit_out}.",
        ))
        g2_rules.append(Rule(
            rule_id=f"RULE_G2_ACCESS_{clear}_{acc_out}",
            antecedents=[("?station", "security_clearance", clear)],
            consequent=("?station", "access_level", acc_out),
            depth=2,
            description=f"Access Policy: If ?station holds {clear}, its facility access level is {acc_out}.",
        ))

    # All rules combined for full world closures
    all_rules = g1_rules + g2_rules

    clean_world_id = f"world_exp1_clean_{world_seed:04d}_r{rotation_idx}"
    clean_world = World(
        world_id=clean_world_id,
        world_seed=world_seed,
        world_version="exp1_branching",
        facts=[fact_a, clean_founder_fact, dist_fact_1, dist_fact_2],
        rules=all_rules,
    )

    mut_world_id = f"world_exp1_mut_{world_seed:04d}_r{rotation_idx}"
    mut_world = World(
        world_id=mut_world_id,
        world_seed=world_seed,
        world_version="exp1_branching",
        facts=[fact_a, mutated_founder_fact, dist_fact_1, dist_fact_2],
        rules=all_rules,
    )

    # -------------------------------------------------------------
    # Generation 1 Tasks (2 tasks depending on Locus B)
    # -------------------------------------------------------------
    g1_tasks: list[Task] = [
        Task(
            task_id=f"task_exp1_g1_protocol_{station.lower()}",
            world_id=clean_world_id,
            query_type="rule_inference",
            target_fact=Fact(subject=station, predicate="uses_protocol", object=sup_to_proto[clean_supervisor]),
            reasoning_depth=1,
            prompt=f"Which security protocol does {station.replace('_', ' ').title()} operate under?",
            expected_answer=sup_to_proto[clean_supervisor],
            valid_support_path_ids=[[fact_a.fact_id, clean_founder_fact.fact_id, f"RULE_G1_PROTOCOL_{clean_supervisor}_{sup_to_proto[clean_supervisor]}"]],
        ),
        Task(
            task_id=f"task_exp1_g1_clearance_{station.lower()}",
            world_id=clean_world_id,
            query_type="rule_inference",
            target_fact=Fact(subject=station, predicate="security_clearance", object=sup_to_clear[clean_supervisor]),
            reasoning_depth=1,
            prompt=f"Which security clearance tier is assigned to {station.replace('_', ' ').title()}?",
            expected_answer=sup_to_clear[clean_supervisor],
            valid_support_path_ids=[[fact_a.fact_id, clean_founder_fact.fact_id, f"RULE_G1_CLEARANCE_{clean_supervisor}_{sup_to_clear[clean_supervisor]}"]],
        ),
    ]

    # -------------------------------------------------------------
    # Generation 2 Task Templates (4 tasks, 2 per G1 parent)
    # -------------------------------------------------------------
    g2_task_templates: list[dict[str, Any]] = [
        # G2.1: transit_route (depends on G1.1 protocol)
        {
            "task_id_suffix": "g2_1_route",
            "parent_predicate": "uses_protocol",
            "target_predicate": "transit_route",
            "prompt": f"Which primary transit route is designated for {station.replace('_', ' ').title()}?",
            "clean_expected": proto_to_route[sup_to_proto[clean_supervisor]],
            "mutated_expected": proto_to_route[sup_to_proto[mutated_supervisor]],
            "rules_filter": lambda r: r.rule_id.startswith("RULE_G2_ROUTE_"),
            "parent_locus_id": "locus_station_protocol",
            "target_locus_id": "locus_station_route",
        },
        # G2.2: resource_tier (depends on G1.1 protocol)
        {
            "task_id_suffix": "g2_2_resource",
            "parent_predicate": "uses_protocol",
            "target_predicate": "resource_tier",
            "prompt": f"Which resource allocation tier is assigned to {station.replace('_', ' ').title()}?",
            "clean_expected": proto_to_res[sup_to_proto[clean_supervisor]],
            "mutated_expected": proto_to_res[sup_to_proto[mutated_supervisor]],
            "rules_filter": lambda r: r.rule_id.startswith("RULE_G2_RESOURCE_"),
            "parent_locus_id": "locus_station_protocol",
            "target_locus_id": "locus_station_resource",
        },
        # G2.3: audit_frequency (depends on G1.2 clearance)
        {
            "task_id_suffix": "g2_3_audit",
            "parent_predicate": "security_clearance",
            "target_predicate": "audit_frequency",
            "prompt": f"What is the mandatory compliance audit frequency for {station.replace('_', ' ').title()}?",
            "clean_expected": clear_to_audit[sup_to_clear[clean_supervisor]],
            "mutated_expected": clear_to_audit[sup_to_clear[mutated_supervisor]],
            "rules_filter": lambda r: r.rule_id.startswith("RULE_G2_AUDIT_"),
            "parent_locus_id": "locus_station_clearance",
            "target_locus_id": "locus_station_audit",
        },
        # G2.4: access_level (depends on G1.2 clearance)
        {
            "task_id_suffix": "g2_4_access",
            "parent_predicate": "security_clearance",
            "target_predicate": "access_level",
            "prompt": f"Which security access level is enforced across {station.replace('_', ' ').title()}?",
            "clean_expected": clear_to_access[sup_to_clear[clean_supervisor]],
            "mutated_expected": clear_to_access[sup_to_clear[mutated_supervisor]],
            "rules_filter": lambda r: r.rule_id.startswith("RULE_G2_ACCESS_"),
            "parent_locus_id": "locus_station_clearance",
            "target_locus_id": "locus_station_access",
        },
    ]

    return BranchingWorldBundle(
        clean_world=clean_world,
        mutated_world=mut_world,
        clean_founder_fact=clean_founder_fact,
        mutated_founder_fact=mutated_founder_fact,
        station=station,
        manager=manager,
        target_supervisor=clean_supervisor,
        mutated_supervisor=mutated_supervisor,
        g1_tasks=g1_tasks,
        g2_task_templates=g2_task_templates,
        g1_rules=g1_rules,
        g2_rules=g2_rules,
        allele_decoder=allele_decoder,
    )
