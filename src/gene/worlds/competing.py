"""D1-C Competing-Consequent Micro-World Generator and Assay Battery.

Generates controlled micro-worlds with:
- 3 matched competing rules with opaque protocol consequents (PROTO_X7, PROTO_Q2, PROTO_M9).
- Standard ontology orientation: manager(STATION, PERSON) and reports_to(PERSON, SUPERVISOR).
- Systematic supervisor-to-protocol rotations (0, 1, 2) and rule-order permutations (0..5).
- Paired ecology derivation: Ecology S derives from the exact same world by masking foil rules.
- Clean ID hygiene (no double-prefixed fact IDs).
- Predeclared 10-intervention biological assay specifications:
  * Knockouts (Fact A, Fact B, Active Rule, Foil Rule)
  * Epistasis / Double Knockout (Fact A + Fact B)
  * Directional Mutations (B -> Tal -> Q2, B -> Mira -> M9)
  * Unmatched Mutation (B -> Soren -> UNKNOWN)
  * Rescue (Tal -> Kira -> X7)
  * Sham No-op & Distractor controls
"""

from __future__ import annotations

import itertools
from typing import Any, Literal
from pydantic import BaseModel

from gene.evaluation.interventions import InterventionSpec, InterventionType
from gene.worlds.schema import Fact, Rule, Task, World, compute_fact_id


OPAQUE_PROTOCOLS = ["PROTO_X7", "PROTO_Q2", "PROTO_M9"]
SUPERVISORS = ["KIRA", "TAL", "MIRA"]
UNMATCHED_SUPERVISOR = "SOREN"

STATIONS = ["VELORA", "KESTREL", "HYPERION", "VANGUARD"]
MANAGERS = ["NERIN", "KAEL", "LYRA", "VANCE"]


class CompetingWorldBundle(BaseModel):
    """Complete bundle containing a D1-C/D1-S world, primary task, and predeclared intervention battery."""
    world: World
    task: Task
    target_protocol: str
    active_rule: Rule
    foil_rules: list[Rule]
    fact_a: Fact  # station manager: manager(station, person)
    fact_b: Fact  # reports_to: reports_to(person, supervisor)
    distractor_fact: Fact
    sup_to_proto: dict[str, str]
    ecology: Literal["S", "C"] = "C"
    interventions: list[InterventionSpec]


def generate_d1_c_world(
    world_seed: int = 42,
    rotation_idx: int = 0,
    rule_perm_idx: int = 0,
    ecology: Literal["S", "C"] = "C",
) -> CompetingWorldBundle:
    """Generate a deterministic micro-world with rotated mappings, permuted rules, and matched ecology."""
    # Rotate supervisor -> protocol mapping
    # Rotation 0: Kira->X7, Tal->Q2, Mira->M9
    # Rotation 1: Kira->M9, Tal->X7, Mira->Q2
    # Rotation 2: Kira->Q2, Tal->M9, Mira->X7
    protos = OPAQUE_PROTOCOLS[rotation_idx % 3:] + OPAQUE_PROTOCOLS[:rotation_idx % 3]
    sup_to_proto = {sup: proto for sup, proto in zip(SUPERVISORS, protos)}

    # Standard entity assignments
    station = STATIONS[world_seed % len(STATIONS)]
    manager = MANAGERS[world_seed % len(MANAGERS)]
    target_supervisor = SUPERVISORS[0]  # Kira
    target_protocol = sup_to_proto[target_supervisor]

    # Construct facts with standard orientation: manager(STATION, PERSON)
    fact_a = Fact(
        subject=station,
        predicate="manager",
        object=manager,
        truth_value=True,
        source_type="generated",
        fact_id=compute_fact_id(station, "manager", manager),
    )
    fact_b = Fact(
        subject=manager,
        predicate="reports_to",
        object=target_supervisor,
        truth_value=True,
        source_type="generated",
        fact_id=compute_fact_id(manager, "reports_to", target_supervisor),
    )

    # Distractor facts
    distractor_station = STATIONS[(world_seed + 1) % len(STATIONS)]
    distractor_fact_1 = Fact(
        subject=distractor_station,
        predicate="located_in",
        object="SECTOR_ALPHA",
        truth_value=True,
        source_type="generated",
        fact_id=compute_fact_id(distractor_station, "located_in", "SECTOR_ALPHA"),
    )
    distractor_fact_2 = Fact(
        subject=distractor_station,
        predicate="opened_in",
        object="2188",
        truth_value=True,
        source_type="generated",
        fact_id=compute_fact_id(distractor_station, "opened_in", "2188"),
    )

    base_facts = [fact_a, fact_b, distractor_fact_1, distractor_fact_2]

    # Construct 3 competing rules with standard antecedents: (?station, manager, ?person), (?person, reports_to, sup)
    rules_dict: dict[str, Rule] = {}
    for sup, proto in sup_to_proto.items():
        r = Rule(
            rule_id=f"RULE_PROTOCOL_{sup}_{proto}",
            antecedents=[
                ("?station", "manager", "?person"),
                ("?person", "reports_to", sup),
            ],
            consequent=("?station", "uses_protocol", proto),
            depth=1,
            description=f"Operational Policy: If ?person serves as the station manager of ?station and ?person directly reports to {sup.title()}, then ?station operates under {proto}.",
        )
        rules_dict[sup] = r

    active_rule = rules_dict[target_supervisor]
    foil_rules = [r for sup, r in rules_dict.items() if sup != target_supervisor]

    # Permute rule orderings
    rule_perms = list(itertools.permutations(list(rules_dict.values())))
    permuted_rules = list(rule_perms[rule_perm_idx % len(rule_perms)])

    # Select rules based on ecology:
    # Ecology C: all 3 competing rules
    # Ecology S: only active rule (derived by masking foil rules)
    world_rules = permuted_rules if ecology == "C" else [active_rule]

    world_id = f"world_d1_{ecology.lower()}_{world_seed:04d}_r{rotation_idx}_p{rule_perm_idx}"
    world = World(
        world_id=world_id,
        world_seed=world_seed,
        world_version="v2_competing",
        facts=base_facts,
        rules=world_rules,
        mutation=None,
    )

    # Primary D1 Task
    target_fact = Fact(
        subject=station,
        predicate="uses_protocol",
        object=target_protocol,
        truth_value=True,
        source_type="derived",
        fact_id=compute_fact_id(station, "uses_protocol", target_protocol),
    )
    task = Task(
        task_id=f"task_d1_{ecology.lower()}_{world_id}_{station.lower()}_uses_protocol",
        world_id=world_id,
        query_type="rule_inference",
        target_fact=target_fact,
        reasoning_depth=1,
        prompt=f"Which security protocol does {station.replace('_', ' ').title()} operate under?",
        expected_answer=target_protocol,
        valid_support_path_ids=[[fact_a.fact_id, fact_b.fact_id, active_rule.rule_id]],
    )

    # -------------------------------------------------------------
    # Predeclared Biological Intervention Battery
    # -------------------------------------------------------------
    interventions: list[InterventionSpec] = [
        # 1. No-op Sham Replay
        InterventionSpec(
            intervention_id="noop_sham",
            intervention_type=InterventionType.NOOP,
            target_node_ids=[],
            expected_counterfactual_object=target_protocol,
            expected_evidence_status="sufficient",
            description="Baseline identical sham replay",
        ),
        # 2. Knockout Fact A (station manager)
        InterventionSpec(
            intervention_id="ko_fact_a",
            intervention_type=InterventionType.KNOCKOUT,
            target_node_ids=[fact_a.fact_id],
            expected_counterfactual_object="UNKNOWN",
            expected_evidence_status="insufficient",
            description="Knockout premise Fact A (station manager)",
        ),
        # 3. Knockout Fact B (reports_to)
        InterventionSpec(
            intervention_id="ko_fact_b",
            intervention_type=InterventionType.KNOCKOUT,
            target_node_ids=[fact_b.fact_id],
            expected_counterfactual_object="UNKNOWN",
            expected_evidence_status="insufficient",
            description="Knockout premise Fact B (reports to supervisor)",
        ),
        # 4. Knockout Active Rule
        InterventionSpec(
            intervention_id="ko_rule_active",
            intervention_type=InterventionType.KNOCKOUT,
            target_node_ids=[active_rule.rule_id],
            expected_counterfactual_object="UNKNOWN",
            expected_evidence_status="insufficient",
            description="Knockout active deduction rule",
        ),
    ]

    # In Ecology C, add foil rule knockout control
    if ecology == "C" and foil_rules:
        interventions.append(
            InterventionSpec(
                intervention_id="ko_rule_foil",
                intervention_type=InterventionType.CONTROL_DISTRACTOR,
                target_node_ids=[foil_rules[0].rule_id],
                expected_counterfactual_object=target_protocol,
                expected_evidence_status="sufficient",
                description="Knockout inactive competing foil rule",
            )
        )

    # 6. Epistasis / Double Knockout (Fact A + Fact B)
    interventions.append(
        InterventionSpec(
            intervention_id="epistasis_double_ko",
            intervention_type=InterventionType.EPISTASIS,
            target_node_ids=[fact_a.fact_id, fact_b.fact_id],
            expected_counterfactual_object="UNKNOWN",
            expected_evidence_status="insufficient",
            description="Joint double knockout of Fact A and Fact B",
        )
    )

    # Mutations: In Ecology C they steer to competing rules; in Ecology S they are unmapped (expected UNKNOWN)
    interventions.extend([
        # 7. Directional Mutation 1 (reports_to Kira -> Tal)
        InterventionSpec(
            intervention_id="mut_redirect_tal",
            intervention_type=InterventionType.MUTATION,
            target_node_ids=[fact_b.fact_id],
            mutated_facts=[Fact(subject=manager, predicate="reports_to", object="TAL", truth_value=True, source_type="mutated", fact_id=compute_fact_id(manager, "reports_to", "TAL"))],
            mutated_memories={fact_b.fact_id: f"{manager.title()} directly reports to Tal."},
            expected_counterfactual_object=sup_to_proto["TAL"] if ecology == "C" else "UNKNOWN",
            expected_evidence_status="sufficient" if ecology == "C" else "insufficient",
            description=f"Semantic mutation: reports to Tal -> {sup_to_proto['TAL'] if ecology == 'C' else 'UNKNOWN'}",
        ),
        # 8. Directional Mutation 2 (reports_to Kira -> Mira)
        InterventionSpec(
            intervention_id="mut_redirect_mira",
            intervention_type=InterventionType.MUTATION,
            target_node_ids=[fact_b.fact_id],
            mutated_facts=[Fact(subject=manager, predicate="reports_to", object="MIRA", truth_value=True, source_type="mutated", fact_id=compute_fact_id(manager, "reports_to", "MIRA"))],
            mutated_memories={fact_b.fact_id: f"{manager.title()} directly reports to Mira."},
            expected_counterfactual_object=sup_to_proto["MIRA"] if ecology == "C" else "UNKNOWN",
            expected_evidence_status="sufficient" if ecology == "C" else "insufficient",
            description=f"Semantic mutation: reports to Mira -> {sup_to_proto['MIRA'] if ecology == 'C' else 'UNKNOWN'}",
        ),
        # 9. Unmatched Mutation (reports_to Kira -> Soren -> UNKNOWN)
        InterventionSpec(
            intervention_id="mut_unmatched_soren",
            intervention_type=InterventionType.MUTATION,
            target_node_ids=[fact_b.fact_id],
            mutated_facts=[Fact(subject=manager, predicate="reports_to", object=UNMATCHED_SUPERVISOR, truth_value=True, source_type="mutated", fact_id=compute_fact_id(manager, "reports_to", UNMATCHED_SUPERVISOR))],
            mutated_memories={fact_b.fact_id: f"{manager.title()} directly reports to Soren."},
            expected_counterfactual_object="UNKNOWN",
            expected_evidence_status="insufficient",
            description="Unmatched semantic mutation: reports to Soren -> UNKNOWN (Abstention Test)",
        ),
        # 10. Rescue (Tal -> Kira -> X7)
        InterventionSpec(
            intervention_id="rescue_tal_to_kira",
            intervention_type=InterventionType.RESCUE,
            target_node_ids=[fact_b.fact_id],
            mutated_facts=[fact_b],  # Restores original Fact B
            mutated_memories={fact_b.fact_id: f"{manager.title()} directly reports to {target_supervisor.title()}."},
            rescue_source_call_id="mut_redirect_tal",
            expected_counterfactual_object=target_protocol,
            expected_evidence_status="sufficient",
            description=f"Rescue intervention: restore reports to {target_supervisor.title()} -> {target_protocol}",
        ),
        # 11. Distractor Fact Removal
        InterventionSpec(
            intervention_id="ko_distractor_fact",
            intervention_type=InterventionType.CONTROL_DISTRACTOR,
            target_node_ids=[distractor_fact_1.fact_id],
            expected_counterfactual_object=target_protocol,
            expected_evidence_status="sufficient",
            description="Control removal of non-rule distractor fact",
        ),
    ])

    return CompetingWorldBundle(
        world=world,
        task=task,
        target_protocol=target_protocol,
        active_rule=active_rule,
        foil_rules=foil_rules,
        fact_a=fact_a,
        fact_b=fact_b,
        distractor_fact=distractor_fact_1,
        sup_to_proto=sup_to_proto,
        ecology=ecology,
        interventions=interventions,
    )
