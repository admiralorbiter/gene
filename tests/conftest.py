"""Shared test fixtures for GENE tests, including hand-authored golden worlds."""

from __future__ import annotations

import pytest
from gene.worlds.schema import Fact, Rule, World, Mutation


@pytest.fixture
def golden_world() -> World:
    """A hand-authored minimal golden world with known deterministic derivations.
    
    Structure:
    - Stations: VELORA
    - People: NERIN, TAL, SOREN
    - Facts:
        manager(VELORA, NERIN)
        reports_to(NERIN, TAL)
        located_in(VELORA, SECTOR_K)
    - Rules:
        If manager(?s, ?p) and reports_to(?p, TAL) -> uses_protocol(?s, PROTOCOL_GREEN)
        If located_in(?s, SECTOR_K) -> uses_protocol(?s, PROTOCOL_AMBER)
    - Expected Derivations:
        uses_protocol(VELORA, PROTOCOL_GREEN) supported by {manager(VELORA, NERIN), reports_to(NERIN, TAL)}
        uses_protocol(VELORA, PROTOCOL_AMBER) supported by {located_in(VELORA, SECTOR_K)}
    """
    f1 = Fact(subject="VELORA", predicate="manager", object="NERIN", source_type="generated")
    f2 = Fact(subject="NERIN", predicate="reports_to", object="TAL", source_type="generated")
    f3 = Fact(subject="VELORA", predicate="located_in", object="SECTOR_K", source_type="generated")

    r1 = Rule(
        rule_id="RULE_GOLDEN_GREEN",
        antecedents=[
            ("?station", "manager", "?person"),
            ("?person", "reports_to", "TAL"),
        ],
        consequent=("?station", "uses_protocol", "PROTOCOL_GREEN"),
        depth=1,
        description="Stations with managers reporting to TAL use GREEN protocol",
    )

    r2 = Rule(
        rule_id="RULE_GOLDEN_AMBER",
        antecedents=[
            ("?station", "located_in", "SECTOR_K"),
        ],
        consequent=("?station", "uses_protocol", "PROTOCOL_AMBER"),
        depth=1,
        description="Stations in SECTOR_K use AMBER protocol",
    )

    mutation = Mutation(
        mutation_id="mut_golden_001",
        world_id="world_golden",
        true_fact=f1,
        mutated_fact=Fact(subject="VELORA", predicate="manager", object="SOREN", source_type="mutated"),
        mutation_type="attribute_swap",
    )

    return World(
        world_id="world_golden",
        world_seed=42,
        entities={
            "people": ["NERIN", "TAL", "SOREN"],
            "stations": ["VELORA"],
            "sectors": ["SECTOR_K"],
            "protocols": ["PROTOCOL_GREEN", "PROTOCOL_AMBER"],
        },
        facts=[f1, f2, f3],
        rules=[r1, r2],
        mutation=mutation,
    )
