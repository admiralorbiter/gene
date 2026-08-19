"""Procedural deterministic generator for synthetic worlds and clean/mutated pairs."""

from __future__ import annotations

import random
from gene.config import WorldGenConfig
from gene.worlds.oracle import Oracle
from gene.worlds.schema import Fact, Mutation, Rule, World, compute_fact_id


# Fictional entity names strictly decoupled from real-world entities
PERSON_NAMES = [
    "NERIN", "TAL", "SOREN", "KIRA", "ORIN", "VAEL", "MIRA", "JAXON",
    "ELYA", "DARIN", "KAEL", "LYRA", "THENEN", "SELIS", "VANE", "CYRA"
]

STATION_NAMES = [
    "VELORA", "AEGIS", "CYGNUS", "SOLARIS", "NEXUS", "ORION", "VANGUARD",
    "ZEPHYR", "KESTREL", "HYPERION", "VALKYRIE", "OBERON"
]

SECTOR_NAMES = [
    "SECTOR_ALPHA", "SECTOR_BETA", "SECTOR_GAMMA", "SECTOR_DELTA",
    "SECTOR_EPSILON", "SECTOR_ZETA", "SECTOR_KAPPA", "SECTOR_SIGMA"
]

PROTOCOL_NAMES = [
    "PROTOCOL_AMBER", "PROTOCOL_GREEN", "PROTOCOL_COBALT", "PROTOCOL_SILVER",
    "PROTOCOL_CRIMSON", "PROTOCOL_ONYX", "PROTOCOL_JADE"
]

TEAM_NAMES = [
    "UNIT_RAVEN", "UNIT_PHOENIX", "UNIT_HYDRA", "UNIT_TITAN",
    "UNIT_SPECTER", "UNIT_VORTEX"
]

YEAR_NAMES = ["2142", "2155", "2168", "2174", "2183", "2191", "2204"]


class WorldGenerator:
    """Procedural generator for deterministic synthetic worlds."""

    @classmethod
    def generate(cls, seed: int, config: WorldGenConfig | None = None) -> World:
        """Generate a fully validated canonical synthetic world from a random seed."""
        cfg = config or WorldGenConfig(seed=seed)
        rng = random.Random(seed)

        # 1. Sample entities
        people = rng.sample(PERSON_NAMES, min(cfg.num_people, len(PERSON_NAMES)))
        stations = rng.sample(STATION_NAMES, min(cfg.num_stations, len(STATION_NAMES)))
        sectors = rng.sample(SECTOR_NAMES, min(cfg.num_sectors, len(SECTOR_NAMES)))
        protocols = rng.sample(PROTOCOL_NAMES, min(cfg.num_protocols, len(PROTOCOL_NAMES)))
        teams = rng.sample(TEAM_NAMES, min(cfg.num_teams, len(TEAM_NAMES)))
        years = rng.sample(YEAR_NAMES, min(len(stations), len(YEAR_NAMES)))

        entities = {
            "people": sorted(people),
            "stations": sorted(stations),
            "sectors": sorted(sectors),
            "protocols": sorted(protocols),
            "teams": sorted(teams),
            "years": sorted(years),
        }

        # 2. Build acyclic reporting hierarchy for people
        # First person is top commander; everyone else reports to an earlier person in the sequence
        reporting_chain: dict[str, str] = {}
        for idx in range(1, len(people)):
            supervisor = rng.choice(people[:idx])
            reporting_chain[people[idx]] = supervisor

        # 3. Generate source facts
        facts: list[Fact] = []

        # Station facts: manager, sector, year
        for idx, station in enumerate(stations):
            manager = people[idx % len(people)]
            sector = rng.choice(sectors)
            year = years[idx % len(years)]

            facts.append(Fact(subject=station, predicate="manager", object=manager, source_type="generated"))
            facts.append(Fact(subject=station, predicate="located_in", object=sector, source_type="generated"))
            facts.append(Fact(subject=station, predicate="opened_in", object=year, source_type="generated"))

        # Reporting facts
        for person, supervisor in reporting_chain.items():
            facts.append(Fact(subject=person, predicate="reports_to", object=supervisor, source_type="generated"))

        # Team membership and leads
        for idx, team in enumerate(teams):
            lead = people[idx % len(people)]
            facts.append(Fact(subject=team, predicate="team_lead", object=lead, source_type="generated"))

        for person in people:
            team = rng.choice(teams)
            facts.append(Fact(subject=person, predicate="member_of", object=team, source_type="generated"))

        # 4. Generate structured derivation rules
        # Rule A: If ?station manager ?person AND ?person reports_to <TopSupervisor> => ?station uses_protocol <ProtocolA>
        rules: list[Rule] = []
        top_supervisor = people[0]
        protocol_a = protocols[0]
        protocol_b = protocols[1] if len(protocols) > 1 else protocols[0]

        rules.append(
            Rule(
                rule_id="RULE_STATION_PROTOCOL_SUPERVISOR",
                antecedents=[
                    ("?station", "manager", "?person"),
                    ("?person", "reports_to", top_supervisor),
                ],
                consequent=("?station", "uses_protocol", protocol_a),
                depth=1,
                description=f"Stations whose manager reports directly to {top_supervisor} use {protocol_a}",
            )
        )

        # Rule B: If ?station located_in <TargetSector> => ?station uses_protocol <ProtocolB>
        target_sector = sectors[0]
        rules.append(
            Rule(
                rule_id="RULE_SECTOR_SECURITY_PROTOCOL",
                antecedents=[
                    ("?station", "located_in", target_sector),
                ],
                consequent=("?station", "uses_protocol", protocol_b),
                depth=1,
                description=f"Stations located in {target_sector} use {protocol_b}",
            )
        )

        world_id = f"world_{seed:04d}"
        return World(
            world_id=world_id,
            world_seed=seed,
            entities=entities,
            facts=facts,
            rules=rules,
            mutation=None,
        )

    @classmethod
    def generate_paired(cls, seed: int, config: WorldGenConfig | None = None) -> tuple[World, World, Mutation]:
        """Generate a clean world and a paired mutated world differing in exactly one source fact."""
        clean_world = cls.generate(seed, config)
        rng = random.Random(seed + 9999)

        # Find candidate source facts suitable for mutation (e.g., station managers that affect derivations)
        manager_facts = [f for f in clean_world.facts if f.predicate == "manager"]
        target_fact = rng.choice(manager_facts)

        # Pick an alternative manager not currently assigned to this station
        available_people = [p for p in clean_world.entities["people"] if p != target_fact.object]
        new_manager = rng.choice(available_people)

        mutated_fact = Fact(
            subject=target_fact.subject,
            predicate=target_fact.predicate,
            object=new_manager,
            truth_value=True,
            source_type="mutated",
        )

        mutation_id = f"mut_{clean_world.world_id}_{target_fact.fact_id}"
        mutation = Mutation(
            mutation_id=mutation_id,
            world_id=clean_world.world_id,
            true_fact=target_fact,
            mutated_fact=mutated_fact,
            mutation_type="attribute_swap",
        )

        # Clean world has mutation recorded as the designated mutation
        clean_with_mut_spec = clean_world.model_copy(update={"mutation": mutation})

        # Mutated world replaces target_fact with mutated_fact
        mutated_facts = [
            mutated_fact if f.fact_id == target_fact.fact_id else f
            for f in clean_world.facts
        ]

        mutated_world = World(
            world_id=f"{clean_world.world_id}_mutated",
            world_seed=seed,
            world_version=clean_world.world_version,
            entities=clean_world.entities,
            facts=mutated_facts,
            rules=clean_world.rules,
            mutation=mutation,
        )

        return clean_with_mut_spec, mutated_world, mutation
