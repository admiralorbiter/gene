"""Independent Benchmark Oracle (Stage 7A.1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from gene.benchmarks.ingress_120.generator import IngressTestCase


@dataclass(frozen=True)
class CaseOracleExpectation:
    """Expected normative outcome for a benchmark world."""
    case_id: str
    expected_admission_status: str  # "ADMIT" | "DEFER" | "REJECT"
    is_admissible_ground_truth: bool
    is_inadmissible_opportunity: bool
    # Failure opportunity labels
    is_wrong_binding_risk: bool
    is_ambiguity_collapse_risk: bool
    is_novel_mislinking_risk: bool
    is_unauthorized_promotion_risk: bool
    # Condition-specific flags
    is_authorized_direct_source: bool
    is_resolved_binding: bool
    expected_candidate_fact_triple: tuple[str, str, str] | None


class BenchmarkOracle:
    """Pure, independent oracle computing ground truth expectations without importing ingress engine."""

    @staticmethod
    def evaluate_case(case: IngressTestCase) -> CaseOracleExpectation:
        is_auth_direct = (case.source_role_form == "DIRECT_OBSERVATION" and case.is_authenticated)
        is_resolvable_binding = case.binding_condition in ("EXACT_CANONICAL", "SURFACE_ALIAS", "ROLE_DISTRACTOR")
        is_admissible = is_auth_direct and is_resolvable_binding

        if is_admissible:
            expected_status = "ADMIT"
            expected_fact = (case.gold_subject_id, case.predicate_name, case.gold_object_id)
        elif is_auth_direct and case.binding_condition in ("CANDIDATE_COLLISION", "NOVEL_ENTITY"):
            expected_status = "DEFER"
            expected_fact = None
        else:  # Unauthorized or unauthenticated
            expected_status = "REJECT"
            expected_fact = None

        is_inadmissible = not is_admissible
        is_wrong_bind = is_inadmissible and case.binding_condition == "CANDIDATE_COLLISION"
        is_ambig = is_inadmissible and case.binding_condition == "CANDIDATE_COLLISION"
        is_novel = is_inadmissible and case.binding_condition == "NOVEL_ENTITY"
        is_unauth = is_inadmissible and (case.source_role_form == "ATTRIBUTED_REPORT" or not case.is_authenticated)

        return CaseOracleExpectation(
            case_id=case.case_id,
            expected_admission_status=expected_status,
            is_admissible_ground_truth=is_admissible,
            is_inadmissible_opportunity=is_inadmissible,
            is_wrong_binding_risk=is_wrong_bind,
            is_ambiguity_collapse_risk=is_ambig,
            is_novel_mislinking_risk=is_novel,
            is_unauthorized_promotion_risk=is_unauth,
            is_authorized_direct_source=is_auth_direct,
            is_resolved_binding=is_resolvable_binding,
            expected_candidate_fact_triple=expected_fact,
        )
