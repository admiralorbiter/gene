"""Forward-chaining deterministic inference oracle, rule-inclusive support-path tracker, and WorldValidator."""

from __future__ import annotations

from enum import Enum
from typing import Any
from gene.worlds.schema import Fact, Rule, World, compute_fact_id


class TruthStatus(str, Enum):
    """Mechanically determined truth status of a claim relative to oracle world."""
    TRUE = "true"
    FALSE = "false"
    UNSUPPORTED = "unsupported"
    CONTRADICTION = "contradiction"


class DerivationNode:
    """Node in the derivation DAG tracking both parent facts and the inference rule used."""
    def __init__(self, fact: Fact, rule: Rule | None = None, parent_nodes: list[DerivationNode] | None = None):
        self.fact = fact
        self.rule = rule
        self.parent_nodes = parent_nodes or []

    def get_minimal_support_sets(self) -> set[frozenset[str]]:
        """Compute all minimal sets of base source fact IDs and rule IDs supporting this derivation."""
        if not self.parent_nodes:
            # Base source fact
            return {frozenset([self.fact.fact_id])}

        # For derived fact, combine Cartesian product of parent support sets and include rule ID
        parent_sets_list = [p.get_minimal_support_sets() for p in self.parent_nodes]
        combined: set[frozenset[str]] = {frozenset()}
        for p_sets in parent_sets_list:
            next_combined = set()
            for current in combined:
                for p_set in p_sets:
                    next_combined.add(current | p_set)
            combined = next_combined

        # Add the inference rule itself as an essential member of the support set
        if self.rule:
            rule_set = frozenset([self.rule.rule_id])
            combined = {c | rule_set for c in combined}

        return combined


class Oracle:
    """Immutable ground-truth oracle and forward-chaining engine."""

    # Declared functional (single-valued) relations where (S, P, O1) and (S, P, O2) are contradictory if O1 != O2
    FUNCTIONAL_PREDICATES: set[str] = {
        "manager",
        "reports_to",
        "located_in",
        "opened_in",
        "uses_protocol",
        "team_lead",
        "security_clearance",
        "transit_route",
        "resource_tier",
        "audit_frequency",
        "access_level",
    }

    def __init__(self, world: World):
        self.world = world
        self.source_facts: dict[str, Fact] = {f.fact_id: f for f in world.facts}
        self.rules: list[Rule] = list(world.rules)
        self.closure_facts: dict[str, Fact] = {}
        self.derivation_trees: dict[str, list[DerivationNode]] = {}
        self.functional_conflicts: list[str] = []
        self._compute_closure()

    def _compute_closure(self) -> None:
        """Compute the full forward-chaining deductive closure and derivation DAGs."""
        # Initialize with source facts
        for f in self.world.facts:
            self.closure_facts[f.fact_id] = f
            node = DerivationNode(fact=f, rule=None, parent_nodes=[])
            self.derivation_trees.setdefault(f.fact_id, []).append(node)

        changed = True
        max_iterations = 20
        iteration = 0

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            for rule in self.rules:
                matched_bindings = self._match_antecedents(rule.antecedents)

                for binding, parent_facts in matched_bindings:
                    c_subj = self._substitute(rule.consequent[0], binding)
                    c_pred = self._substitute(rule.consequent[1], binding)
                    c_obj = self._substitute(rule.consequent[2], binding)

                    # Check functional conflict with existing closure facts
                    if c_pred.lower() in self.FUNCTIONAL_PREDICATES:
                        for existing_fact in self.closure_facts.values():
                            if (
                                existing_fact.subject.upper() == c_subj.upper()
                                and existing_fact.predicate.lower() == c_pred.lower()
                                and existing_fact.object.upper() != c_obj.upper()
                                and existing_fact.truth_value
                            ):
                                conflict_msg = (
                                    f"Functional conflict on ({c_subj}, {c_pred}): "
                                    f"Existing='{existing_fact.object}', New='{c_obj}' from Rule '{rule.rule_id}'"
                                )
                                if conflict_msg not in self.functional_conflicts:
                                    self.functional_conflicts.append(conflict_msg)

                    fact_id = compute_fact_id(c_subj, c_pred, c_obj)
                    if fact_id not in self.closure_facts:
                        derived_fact = Fact(
                            subject=c_subj,
                            predicate=c_pred,
                            object=c_obj,
                            truth_value=True,
                            source_type="derived",
                            fact_id=fact_id,
                        )
                        self.closure_facts[fact_id] = derived_fact
                        changed = True

                    # Add derivation tree node
                    parent_nodes = []
                    for pf in parent_facts:
                        p_node = self.derivation_trees[pf.fact_id][0]
                        parent_nodes.append(p_node)

                    d_node = DerivationNode(
                        fact=self.closure_facts[fact_id],
                        rule=rule,
                        parent_nodes=parent_nodes,
                    )
                    self.derivation_trees.setdefault(fact_id, []).append(d_node)

    def _match_antecedents(
        self, antecedents: list[tuple[str, str, str]]
    ) -> list[tuple[dict[str, str], list[Fact]]]:
        """Find all variable bindings matching all antecedent clauses simultaneously."""
        results: list[tuple[dict[str, str], list[Fact]]] = [({}, [])]

        for clause in antecedents:
            new_results = []
            for binding, matched_facts in results:
                for fact in self.closure_facts.values():
                    if not fact.truth_value:
                        continue
                    new_b = self._unify_clause(clause, fact.triple, binding)
                    if new_b is not None:
                        new_results.append((new_b, matched_facts + [fact]))
            results = new_results

        return results

    @staticmethod
    def _unify_clause(
        pattern: tuple[str, str, str],
        target: tuple[str, str, str],
        binding: dict[str, str],
    ) -> dict[str, str] | None:
        """Attempt to unify pattern clause with target triple given current bindings."""
        current_b = dict(binding)
        for p_elem, t_elem in zip(pattern, target):
            if p_elem.startswith("?"):
                var_name = p_elem
                if var_name in current_b:
                    if current_b[var_name] != t_elem:
                        return None
                else:
                    current_b[var_name] = t_elem
            else:
                if p_elem.upper() != t_elem.upper():
                    return None
        return current_b

    @staticmethod
    def _substitute(element: str, binding: dict[str, str]) -> str:
        """Substitute variable binding into element if variable, else return element."""
        if element.startswith("?"):
            return binding.get(element, element)
        return element

    def get_support_paths(self, fact_id: str) -> list[list[str]]:
        """Get all minimal valid support paths (as sorted lists of base fact IDs and rule IDs) for a fact."""
        if fact_id not in self.derivation_trees:
            return []
        all_sets: set[frozenset[str]] = set()
        for node in self.derivation_trees[fact_id]:
            all_sets.update(node.get_minimal_support_sets())
        return [sorted(list(s)) for s in sorted(all_sets, key=lambda s: (len(s), sorted(s)))]

    def evaluate_triple(self, subject: str, predicate: str, obj: str) -> TruthStatus:
        """Evaluate the truth status of an atomic proposition."""
        target_id = compute_fact_id(subject, predicate, obj)
        if target_id in self.closure_facts:
            return TruthStatus.TRUE if self.closure_facts[target_id].truth_value else TruthStatus.FALSE

        norm_subj = subject.strip().upper()
        norm_pred = predicate.strip().lower()
        norm_obj = obj.strip().upper()

        if norm_pred in self.FUNCTIONAL_PREDICATES:
            for f in self.closure_facts.values():
                if f.subject.upper() == norm_subj and f.predicate.lower() == norm_pred:
                    if f.object.upper() != norm_obj and f.truth_value:
                        return TruthStatus.FALSE

        return TruthStatus.UNSUPPORTED

    def evaluate_claim(self, claim: Fact) -> TruthStatus:
        """Evaluate a Fact object against the oracle."""
        return self.evaluate_triple(claim.subject, claim.predicate, claim.object)

    def get_canonical_answers(self, subject: str, predicate: str) -> list[str]:
        """Retrieve all canonical objects for a (subject, predicate) query."""
        norm_subj = subject.strip().upper()
        norm_pred = predicate.strip().lower()
        answers = []
        for f in self.closure_facts.values():
            if f.subject.upper() == norm_subj and f.predicate.lower() == norm_pred and f.truth_value:
                answers.append(f.object)
        return answers


class WorldValidator:
    """Validator ensuring worlds have no functional contradictions and unambiguous task ground truth."""

    @classmethod
    def validate_world(cls, world: World, oracle: Oracle | None = None) -> list[str]:
        """Return list of validation errors found in world, empty list if world is strictly valid."""
        orc = oracle or Oracle(world)
        errors: list[str] = []

        # 1. Check functional conflicts in closure
        if orc.functional_conflicts:
            errors.extend(orc.functional_conflicts)

        # 2. Check that functional predicates on known entities have at most one answer
        station_names = world.entities.get("stations", [])
        for station in station_names:
            protocols = orc.get_canonical_answers(station, "uses_protocol")
            if len(protocols) > 1:
                errors.append(f"Ambiguous uses_protocol for station '{station}': {protocols}")

            managers = orc.get_canonical_answers(station, "manager")
            if len(managers) > 1:
                errors.append(f"Ambiguous manager for station '{station}': {managers}")

        return errors
