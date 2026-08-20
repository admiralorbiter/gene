"""Dual-Oracle and 5D Epistemic State Vector Evaluator.

Evaluates model claims against two simultaneous oracles:
1. T* (Canonical Ground-Truth Oracle): Evaluates truth against canonical clean world W*.
2. D_t^ctx (Context-Local Derivability Oracle): Evaluates derivability strictly against prompt-exposed memories.

Classifies the 5D state vector (T*, D_t^ctx, A, E, K) into formal informational phenotypes:
- Healthy (H): (1, 1, 1, 1, 1) without infected ancestry.
- Repaired (R): (1, 1, 1, 1, 1) with infected ancestry.
- Pure Semantic Infection (S): (0, 1, 1, 1, 1) [Globally false, locally perfect].
- Epistemic Infection (E): (0, 0, 0, 0, 1) [False sufficiency judgment].
- Control Infection (C): (0, 0, 0, 1, 0) [Detection-to-action split].
- Extinct: Abstention / UNKNOWN (no active claim admitted).
"""

from __future__ import annotations

import json
from typing import Any, Literal
from pydantic import BaseModel, Field

from gene.worlds.oracle import Oracle, TruthStatus
from gene.worlds.schema import Fact, Task, World


InfectionPhenotype = Literal[
    "healthy", "semantic", "epistemic", "control", "repaired",
    "extinct", "de_novo_error", "clean_abstention", "contract_failure"
]


class DualOracleEvaluation(BaseModel):
    """Complete dual-oracle evaluation result with 5D state vector and phenotype."""
    raw_response_text: str
    raw_object: str | None
    normalized_object: str
    raw_evidence_status: str | None
    is_contract_consistent: bool
    
    # Dual Oracle Truth & Derivability
    canonical_truth: int | None = None  # T* (1 = True in W*, 0 = False in W*, None = N/A for abstentions)
    canonical_truth_status: str  # TruthStatus string
    context_derivability: int  # D_t^ctx (1 = Derivable from exposed context, 0 = Underivable)
    context_truth_status: str
    
    # 3 Diagnostic Metrics
    A_correct: int  # Local behavioral correctness (1 = matches D_t^ctx warranted object, 0 = incorrect)
    E_correct: int  # Epistemic status correctness (1 = matches D_t^ctx answerability, 0 = incorrect)
    K_consistent: int  # Contract consistency (1 = consistent, 0 = split)
    
    state_vector: tuple[int | None, int, int, int, int]  # (T*, D, A, E, K)
    phenotype: InfectionPhenotype
    
    # Ancestral Allele Tracking
    decoded_ancestor: str | None = None
    ancestral_allele_fidelity: float | None = None
    has_infected_ancestry: bool = False


class DualOracle:
    """Evaluates claims against both canonical truth and prompt-exposed local context."""

    def __init__(
        self,
        canonical_world: World,
        context_world: World,
        ancestral_seed_allele: str | None = None,
        allele_decoder: dict[str, str] | None = None,
    ):
        self.canonical_world = canonical_world
        self.context_world = context_world
        self.canonical_oracle = Oracle(canonical_world)
        self.context_oracle = Oracle(context_world)
        self.ancestral_seed_allele = ancestral_seed_allele
        self.allele_decoder = allele_decoder or {}

    def evaluate_response(
        self,
        raw_text: str,
        parsed_json: dict[str, Any] | None,
        task: Task,
        has_infected_ancestry: bool = False,
    ) -> DualOracleEvaluation:
        """Evaluate a model output against both canonical truth and context derivability."""
        # 1. Parse raw fields
        raw_obj_str = "UNKNOWN"
        raw_ev = "insufficient"

        if parsed_json and isinstance(parsed_json, dict):
            raw_ev = str(parsed_json.get("evidence_status", "insufficient")).strip().lower()
            ans_block = parsed_json.get("answer")
            if isinstance(ans_block, dict):
                raw_obj_val = ans_block.get("object")
                if raw_obj_val is not None:
                    raw_obj_str = str(raw_obj_val).strip()

        norm_obj = raw_obj_str.strip().upper().replace(" ", "_")
        if norm_obj in ("UNKNOWN", "NONE", "", "UNKNOWN_OR_UNSUPPORTED") or norm_obj.startswith("UNKNOWN"):
            norm_obj = "UNKNOWN"
            is_unknown = True
        else:
            is_unknown = False
        if raw_ev in ("insufficient", "conflicting"):
            k_val = 1 if is_unknown else 0
        elif raw_ev == "sufficient":
            k_val = 1 if not is_unknown else 0
        else:
            k_val = 0

        subj = task.target_fact.subject
        pred = task.target_fact.predicate

        # 3. Evaluate Canonical Truth T* (None for abstentions)
        if is_unknown:
            t_star = None
            t_star_status = TruthStatus.UNSUPPORTED
        else:
            t_star_status = self.canonical_oracle.evaluate_triple(subj, pred, norm_obj)
            t_star = 1 if t_star_status == TruthStatus.TRUE else 0

        # 4. Evaluate Context Derivability D_t^ctx
        d_ctx_status = self.context_oracle.evaluate_triple(subj, pred, norm_obj)
        
        # Check if context oracle entails ANY valid object for (subj, pred)
        context_warranted_obj: str | None = None
        for f in self.context_oracle.closure_facts.values():
            if f.subject.upper() == subj.upper() and f.predicate.lower() == pred.lower() and f.truth_value:
                context_warranted_obj = f.object.upper().replace(" ", "_")
                break

        d_ctx = 1 if (context_warranted_obj is not None and d_ctx_status == TruthStatus.TRUE) else 0

        # 5. Diagnostic A: Local Behavioral Correctness
        if context_warranted_obj is not None:
            a_val = 1 if norm_obj == context_warranted_obj else 0
        else:
            a_val = 1 if is_unknown else 0

        # 6. Diagnostic E: Status Correctness
        expected_ev = "sufficient" if context_warranted_obj is not None else "insufficient"
        e_val = 1 if raw_ev == expected_ev else 0

        state_vector = (t_star, d_ctx, a_val, e_val, k_val)

        # 7. Classify Infection Phenotype
        if is_unknown:
            if e_val == 1 and k_val == 1:
                phenotype: InfectionPhenotype = "extinct"
            else:
                phenotype = "contract_failure"
        elif state_vector == (1, 1, 1, 1, 1):
            phenotype = "repaired" if has_infected_ancestry else "healthy"
        elif state_vector == (0, 1, 1, 1, 1):
            phenotype = "semantic"
        elif e_val == 0 and k_val == 1:
            phenotype = "epistemic"
        elif k_val == 0:
            phenotype = "control"
        else:
            phenotype = "de_novo_error"

        # 8. Ancestral Allele Fidelity
        decoded_sup: str | None = self.allele_decoder.get(norm_obj)
        fidelity: float | None = None
        if self.ancestral_seed_allele and decoded_sup:
            fidelity = 1.0 if decoded_sup == self.ancestral_seed_allele else 0.0

        return DualOracleEvaluation(
            raw_response_text=raw_text,
            raw_object=raw_obj_str,
            normalized_object=norm_obj,
            raw_evidence_status=raw_ev,
            is_contract_consistent=(k_val == 1),
            canonical_truth=t_star,
            canonical_truth_status=str(t_star_status),
            context_derivability=d_ctx,
            context_truth_status=str(d_ctx_status),
            A_correct=a_val,
            E_correct=e_val,
            K_consistent=k_val,
            state_vector=state_vector,
            phenotype=phenotype,
            decoded_ancestor=decoded_sup,
            ancestral_allele_fidelity=fidelity,
            has_infected_ancestry=has_infected_ancestry,
        )
