"""Unit tests for deterministic natural-language renderer."""

from __future__ import annotations

from gene.worlds.renderer import NaturalLanguageRenderer
from gene.worlds.schema import Fact, Rule


def test_render_fact():
    f1 = Fact(subject="VELORA", predicate="manager", object="NERIN")
    rendered1 = NaturalLanguageRenderer.render_fact(f1)
    assert "Nerin" in rendered1
    assert "Velora" in rendered1
    assert "station manager" in rendered1

    f2 = Fact(subject="VELORA", predicate="uses_protocol", object="PROTOCOL_GREEN")
    rendered2 = NaturalLanguageRenderer.render_fact(f2)
    assert "Velora" in rendered2
    assert "Protocol Green" in rendered2


def test_render_rule():
    rule = Rule(
        rule_id="R1",
        antecedents=[
            ("?station", "manager", "?person"),
            ("?person", "reports_to", "TAL"),
        ],
        consequent=("?station", "uses_protocol", "PROTOCOL_GREEN"),
        depth=1,
    )
    rendered = NaturalLanguageRenderer.render_rule(rule)
    assert "Operational Policy: If" in rendered
    assert "then" in rendered
    assert "Protocol Green" in rendered


def test_render_task_prompt():
    prompt = NaturalLanguageRenderer.render_task_prompt("VELORA", "manager")
    assert prompt == "Who is the station manager of Velora?"

    prompt2 = NaturalLanguageRenderer.render_task_prompt("VELORA", "uses_protocol")
    assert prompt2 == "Which security protocol does Velora operate under?"
