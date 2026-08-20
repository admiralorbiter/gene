"""Deterministic Epistemic Renderer.

Renders natural language texts deterministically from structured PremiseNode and RuleSpec fields.
Transforms structure first, renders text second.
"""

from __future__ import annotations

from gene.experiments.epistemic_ir import EpistemicState, PremiseNode, QueryContract, RuleSpec


class EpistemicRenderer:
    """Renders structured epistemic nodes and rules into uniform natural language."""

    @staticmethod
    def render_premise(node: PremiseNode) -> str:
        """Render premise text deterministically from structured fields."""
        if node.predicate == "has_role":
            role_str = node.role.replace("_", " ") if node.role else "personnel"
            return f"{node.subject} is {role_str} of {node.entity}."
        elif node.predicate == "reports_to":
            return f"{node.subject} reports to {node.target_value}."
        elif node.predicate == "station_operates_protocol":
            return f"Station {node.entity} operates under protocol {node.target_value}."
        else:
            return f"{node.subject} {node.predicate} {node.target_value or ''}."

    @staticmethod
    def render_rule(rule: RuleSpec) -> str:
        """Render formal rule text deterministically."""
        if rule.rule_id == "rule_manager_s1":
            return "If a person is manager of a station and reports to sector lead S1, the station operates under protocol PROTO_X7."
        elif rule.rule_id == "rule_sector_lead_s2":
            return "If a person is sector lead of a station and reports to sector lead S2, the station operates under protocol PROTO_X7."
        elif rule.rule_id == "rule_sector_lead_s1":
            return "If a person is sector lead of a station and reports to sector lead S1, the station operates under protocol PROTO_X7."
        elif rule.rule_id == "rule_opaque_q7_s1":
            return "If a person is ROLE_Q7 of a station and reports to sector lead S1, the station operates under protocol PROTO_X7."
        elif rule.rule_id == "rule_opaque_m2_s2":
            return "If a person is ROLE_M2 of a station and reports to sector lead S2, the station operates under protocol PROTO_X7."
        else:
            return f"RULE ({rule.rule_id}): {' AND '.join(rule.antecedent_predicates)} => {rule.consequent_predicate}."

    @classmethod
    def render_state(cls, state: EpistemicState) -> EpistemicState:
        """Re-render all premise and rule texts across an EpistemicState."""
        for node in state.premises.values():
            node.rendered_text = cls.render_premise(node)
        for rule in state.rules.values():
            rule.rendered_text = cls.render_rule(rule)
        return state
