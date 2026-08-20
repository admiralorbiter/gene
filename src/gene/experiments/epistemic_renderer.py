"""Deterministic Epistemic Renderer (v2.1).

Renders natural language texts deterministically from structured PremiseNode and RuleSpec fields.
Transforms structure first, renders text second. Zero hardcoded rule_id lookups.
"""

from __future__ import annotations

from gene.experiments.epistemic_ir import (
    EpistemicState,
    PremiseNode,
    QueryContract,
    RuleAntecedent,
    RuleSpec,
)


class EpistemicRenderer:
    """Renders structured epistemic nodes and rules into uniform natural language."""

    @staticmethod
    def format_role_token(role: str | None) -> str:
        """Format role token for natural language rendering."""
        if not role:
            return "personnel"
        if role.startswith("ROLE_"):
            return role  # Preserve exact synthetic opaque token e.g. ROLE_Q7
        return role.replace("_", " ")

    @classmethod
    def render_premise(cls, node: PremiseNode) -> str:
        """Render premise text deterministically from structured fields."""
        if node.predicate == "has_role":
            role_str = cls.format_role_token(node.role)
            return f"{node.subject} is {role_str} of {node.entity}."
        elif node.predicate == "reports_to":
            return f"{node.subject} reports to {node.target_value}."
        elif node.predicate == "station_operates_protocol":
            return f"Station {node.entity} operates under protocol {node.target_value}."
        elif node.predicate == "neutral_fact":
            return f"Archive record logs {node.subject} on duty at {node.entity}."
        else:
            return f"{node.subject} {node.predicate} {node.target_value or ''}."

    @classmethod
    def render_rule(cls, rule: RuleSpec) -> str:
        """Render formal rule text deterministically from structured RuleAntecedent fields.
        
        Zero hardcoded rule_id branching!
        """
        clauses = []
        for ant in rule.antecedents:
            if ant.predicate == "has_role":
                role_str = cls.format_role_token(ant.subject_role)
                clauses.append(f"a person is {role_str} of a station")
            elif ant.predicate == "reports_to":
                clauses.append(f"reports to {ant.target_value}")
            else:
                clauses.append(f"{ant.predicate}({ant.subject_role or ''}, {ant.target_value or ''})")

        conditions_str = " and ".join(clauses)
        return f"If {conditions_str}, the station operates under protocol {rule.consequent_protocol}."

    @classmethod
    def render_state(cls, state: EpistemicState) -> EpistemicState:
        """Re-render all premise and rule texts across an EpistemicState."""
        for node in state.premises.values():
            node.rendered_text = cls.render_premise(node)
        for rule in state.rules.values():
            rule.rendered_text = cls.render_rule(rule)
        return state
