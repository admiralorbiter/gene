"""Deterministic natural-language renderer for GENE facts, rules, and tasks."""

from __future__ import annotations

from typing import Any
from gene.worlds.schema import Fact, Rule, Task


class NaturalLanguageRenderer:
    """Deterministic natural language renderer for world triples and inference rules."""

    @classmethod
    def render_fact(cls, fact: Fact | tuple[str, str, str]) -> str:
        """Render an atomic triple into a clear, natural English sentence."""
        subj, pred, obj = fact.triple if isinstance(fact, Fact) else fact
        subj_clean = subj.replace("_", " ").title() if not subj.startswith("?") else subj
        obj_clean = obj.replace("_", " ").title() if not obj.startswith("?") else obj

        pred_lower = pred.lower()
        if pred_lower == "manager":
            return f"{obj_clean} serves as the station manager of {subj_clean}."
        elif pred_lower == "reports_to":
            return f"{subj_clean} directly reports to {obj_clean}."
        elif pred_lower == "located_in":
            return f"{subj_clean} is located in sector {obj_clean}."
        elif pred_lower == "opened_in":
            return f"{subj_clean} was commissioned in the year {obj}."
        elif pred_lower == "uses_protocol":
            return f"{subj_clean} operates under the {obj_clean} security protocol."
        elif pred_lower == "member_of":
            return f"{subj_clean} is an active member of unit {obj_clean}."
        elif pred_lower == "team_lead":
            return f"{obj_clean} is the designated lead of unit {subj_clean}."
        else:
            return f"{subj_clean} has {pred_lower} relationship with {obj_clean}."

    @classmethod
    def render_rule(cls, rule: Rule) -> str:
        """Render a derivation rule into natural English premise-conclusion form."""
        antecedent_texts = [cls.render_fact(clause) for clause in rule.antecedents]
        consequent_text = cls.render_fact(rule.consequent)
        joined_antecedents = " and ".join(antecedent_texts)
        return f"Operational Policy: If {joined_antecedents}, then {consequent_text}"

    @classmethod
    def render_task_prompt(cls, subject: str, predicate: str) -> str:
        """Render a query prompt asking for the object of (subject, predicate)."""
        subj_clean = subject.replace("_", " ").title()
        pred_lower = predicate.lower()

        if pred_lower == "manager":
            return f"Who is the station manager of {subj_clean}?"
        elif pred_lower == "reports_to":
            return f"Who does {subj_clean} directly report to?"
        elif pred_lower == "located_in":
            return f"Which sector is {subj_clean} located in?"
        elif pred_lower == "opened_in":
            return f"In what year was {subj_clean} commissioned?"
        elif pred_lower == "uses_protocol":
            return f"Which security protocol does {subj_clean} operate under?"
        elif pred_lower == "member_of":
            return f"Which unit is {subj_clean} a member of?"
        elif pred_lower == "team_lead":
            return f"Who is the lead of unit {subj_clean}?"
        else:
            return f"What is the {pred_lower} of {subj_clean}?"
