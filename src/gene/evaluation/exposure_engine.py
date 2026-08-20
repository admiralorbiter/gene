"""Exposure and Transmission Opportunity Engine for Experiment 1B.

Tracks physical transmission opportunities across varying contact rates X:
- Explicitly separates Parent Population from Transmission Opportunities, ensuring
  unbiased R_S calculation when exposure p < 1.0 (retaining zero-exposure parents in denominator).
- Factorizes reproduction: R_S = X * tau_S * W.
- Simultaneously tracks Clean Cognitive Utility U_clean(p) and abstention correctness on masked tasks.
"""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

EXPOSURE_MASKS: dict[float, list[bool]] = {
    0.00: [False, False, False, False],
    0.25: [True, False, False, False],
    0.50: [True, False, True, False],
    0.75: [True, True, True, False],
    1.00: [True, True, True, True],
}


class TransmissionOpportunity(BaseModel):
    """An individual physical transmission opportunity."""
    opportunity_id: str
    run_id: str
    world_id: str
    arm: Literal["clean", "infected"]
    exposure_p: float
    parent_generation: int
    child_generation: int
    parent_node_id: str
    parent_locus_id: str
    parent_phenotype: str
    child_task_id: str
    target_predicate: str
    is_exposed: bool
    is_generated: bool
    is_written: bool
    child_node_id: str | None = None
    child_phenotype: str
    ancestral_allele_fidelity: float | None = None


class ParentRecord(BaseModel):
    """A registered parent node in the active population."""
    parent_node_id: str
    parent_generation: int
    parent_phenotype: str
    arm: Literal["clean", "infected"]


class ExposureDoseSummary(BaseModel):
    """Summary of transmission and cognitive utility at a specific exposure dose p."""
    exposure_p: float
    
    # Population & Opportunity Counts
    total_parents: int
    total_opportunities: int
    exposed_opportunities: int
    infected_children_generated: int
    infected_children_written: int
    
    # Factorized Physical Parameters
    contact_rate_X: float
    epistemic_transmissibility_tau_S: float | None = None
    write_admission_W: float | None = None
    reproduction_number_R_S: float
    
    # Clean Arm Utility Metrics
    clean_opportunities: int
    clean_correct_derived: int
    clean_abstained_when_masked: int
    clean_utility_U: float | None = None
    
    # Fidelity
    ancestral_fidelity_F2: float | None = None


class ExposureEngine:
    """Manages transmission opportunity tracking and calculates factorized transmission metrics."""

    def __init__(self):
        self.parents: dict[str, ParentRecord] = {}
        self.opportunities: list[TransmissionOpportunity] = []

    def register_parent(
        self,
        parent_node_id: str,
        parent_gen: int,
        parent_phenotype: str,
        arm: Literal["clean", "infected"],
    ) -> None:
        """Register a parent node in the population."""
        self.parents[parent_node_id] = ParentRecord(
            parent_node_id=parent_node_id,
            parent_generation=parent_gen,
            parent_phenotype=parent_phenotype,
            arm=arm,
        )

    def record_opportunity(
        self,
        opportunity_id: str,
        run_id: str,
        world_id: str,
        arm: Literal["clean", "infected"],
        exposure_p: float,
        parent_gen: int,
        child_gen: int,
        parent_node_id: str,
        parent_locus_id: str,
        parent_phenotype: str,
        child_task_id: str,
        target_predicate: str,
        is_exposed: bool,
        is_generated: bool,
        is_written: bool,
        child_node_id: str | None = None,
        child_phenotype: str = "extinct",
        ancestral_allele_fidelity: float | None = None,
    ) -> TransmissionOpportunity:
        """Record an individual transmission opportunity."""
        opp = TransmissionOpportunity(
            opportunity_id=opportunity_id,
            run_id=run_id,
            world_id=world_id,
            arm=arm,
            exposure_p=exposure_p,
            parent_generation=parent_gen,
            child_generation=child_gen,
            parent_node_id=parent_node_id,
            parent_locus_id=parent_locus_id,
            parent_phenotype=parent_phenotype,
            child_task_id=child_task_id,
            target_predicate=target_predicate,
            is_exposed=is_exposed,
            is_generated=is_generated,
            is_written=is_written,
            child_node_id=child_node_id,
            child_phenotype=child_phenotype,
            ancestral_allele_fidelity=ancestral_allele_fidelity,
        )
        self.opportunities.append(opp)
        return opp

    def compute_summary(self, exposure_p: float) -> ExposureDoseSummary:
        """Compute transmission metrics and clean utility at a given exposure dose p."""
        # 1. Filter opportunities for this exposure level
        opps = [o for o in self.opportunities if abs(o.exposure_p - exposure_p) < 1e-4]
        
        # 2. Infected Arm Metrics (G1 Semantic Parents -> G2 Children)
        inf_opps = [o for o in opps if o.arm == "infected" and o.parent_phenotype == "semantic"]
        
        # Total distinct semantic parents active in this condition (G1)
        sem_parent_ids = {p.parent_node_id for p in self.parents.values() if p.arm == "infected" and p.parent_phenotype == "semantic" and p.parent_generation == 1}
        # Filter infected semantic parents associated with this condition
        condition_parents = [p for p in self.parents.values() if p.parent_node_id in {o.parent_node_id for o in inf_opps} and p.arm == "infected" and p.parent_phenotype == "semantic"]
        num_parents = len(condition_parents) if condition_parents else len(sem_parent_ids)
        
        tot_opps = len(inf_opps)
        exp_opps = len([o for o in inf_opps if o.is_exposed])
        
        # Generated infected children from exposed opportunities
        gen_inf = len([o for o in inf_opps if o.is_exposed and o.is_generated and o.child_phenotype in ("semantic", "epistemic", "control")])
        # Written infected children
        wri_inf = len([o for o in inf_opps if o.is_written and o.child_phenotype in ("semantic", "epistemic", "control")])

        # Physical parameter calculations
        contact_x = exp_opps / num_parents if num_parents > 0 else 0.0
        tau_s = gen_inf / exp_opps if exp_opps > 0 else None
        w_rate = wri_inf / gen_inf if gen_inf > 0 else (1.0 if exp_opps == 0 else None)
        r_s = wri_inf / num_parents if num_parents > 0 else 0.0

        # Fidelity across exposed G2 infected children
        fidelities = [o.ancestral_allele_fidelity for o in inf_opps if o.is_exposed and o.ancestral_allele_fidelity is not None]
        f2 = (sum(fidelities) / len(fidelities)) if fidelities else None

        # 3. Clean Arm Metrics
        clean_opps = [o for o in opps if o.arm == "clean"]
        tot_clean = len(clean_opps)
        clean_correct = len([o for o in clean_opps if o.is_exposed and o.child_phenotype == "healthy"])
        clean_abstained_masked = len([o for o in clean_opps if not o.is_exposed and o.child_phenotype in ("extinct", "healthy") and not o.is_generated])
        
        # Clean Utility U(p): fraction of tasks where ground truth was successfully derived
        u_clean = clean_correct / tot_clean if tot_clean > 0 else None

        return ExposureDoseSummary(
            exposure_p=exposure_p,
            total_parents=num_parents,
            total_opportunities=tot_opps,
            exposed_opportunities=exp_opps,
            infected_children_generated=gen_inf,
            infected_children_written=wri_inf,
            contact_rate_X=contact_x,
            epistemic_transmissibility_tau_S=tau_s,
            write_admission_W=w_rate,
            reproduction_number_R_S=r_s,
            clean_opportunities=tot_clean,
            clean_correct_derived=clean_correct,
            clean_abstained_when_masked=clean_abstained_masked,
            clean_utility_U=u_clean,
            ancestral_fidelity_F2=f2,
        )
