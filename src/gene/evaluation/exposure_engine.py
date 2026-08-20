"""Exposure and Transmission Opportunity Engine for Experiment 1B.

Tracks physical transmission opportunities across varying contact rates X:
- Explicitly separates Parent Population from Transmission Opportunities, ensuring
  unbiased R_S calculation when exposure p < 1.0 (retaining zero-exposure parents in denominator).
- Factorizes reproduction: R_S = X * tau_S * W.
- Tracks Clean Answer Coverage C_clean(p) along the Uniform-Thinning Frontier: R_S = 2 * C_clean.
- Measures Spontaneous / De-Novo Mutation Rate (mu_de_novo) on unexposed contexts to distinguish
  transmitted infection from unprompted errors.
- Provides counterbalanced task-identity rotation schedules across worlds.
"""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


# Counterbalanced task-identity exposure schedules across 4 micro-worlds
# Predicates: [G2.1: transit_route, G2.2: resource_tier, G2.3: audit_frequency, G2.4: access_level]
BALANCED_EXPOSURE_MASKS: dict[float, list[list[bool]]] = {
    0.00: [
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
    ],
    0.25: [
        [True, False, False, False],  # World 1: transit_route
        [False, True, False, False],  # World 2: resource_tier
        [False, False, True, False],  # World 3: audit_frequency
        [False, False, False, True],  # World 4: access_level
    ],
    0.50: [
        [True, False, True, False],   # World 1: route + audit
        [False, True, False, True],   # World 2: resource + access
        [True, True, False, False],   # World 3: route + resource
        [False, False, True, True],   # World 4: audit + access
    ],
    0.75: [
        [True, True, True, False],    # World 1: masked access
        [True, True, False, True],    # World 2: masked audit
        [True, False, True, True],    # World 3: masked resource
        [False, True, True, True],    # World 4: masked route
    ],
    1.00: [
        [True, True, True, True],
        [True, True, True, True],
        [True, True, True, True],
        [True, True, True, True],
    ],
}


def get_exposure_mask(exposure_p: float, world_idx: int) -> list[bool]:
    """Retrieve the counterbalanced task-identity exposure mask for a given dose and world index."""
    dose_key = round(exposure_p, 2)
    schedules = BALANCED_EXPOSURE_MASKS.get(dose_key)
    if not schedules:
        raise ValueError(f"Unknown exposure dose: {exposure_p}")
    return schedules[world_idx % len(schedules)]


# Backward-compatible static alias
EXPOSURE_MASKS = {
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
    """Summary of transmission, answer coverage, and de-novo mutations at a specific exposure dose p."""
    exposure_p: float
    
    # Population & Opportunity Counts
    total_parents: int
    total_opportunities: int
    exposed_opportunities: int
    unexposed_opportunities: int
    
    # Generated & Written Infected Children (Separating Transmitted from De-Novo)
    infected_children_generated: int = 0  # Transmitted infected generated on exposed opportunities
    transmitted_infected_generated: int = 0
    transmitted_infected_written: int = 0
    denovo_infected_written: int = 0
    infected_children_written: int = 0    # Total infected written (transmitted + de-novo)
    
    # Factorized Physical Parameters
    contact_rate_X: float
    epistemic_transmissibility_tau_S: float | None = None
    write_admission_W_hat: float | None = None  # W_hat = transmitted_written / transmitted_generated (strictly <= 1.0)
    write_admission_W_policy: float = 1.0
    reproduction_number_R_S: float              # Primary lineage transmission reproduction number R_trans
    reproduction_number_R_trans: float = 0.0
    reproduction_number_R_total_corruption: float = 0.0
    
    # Clean Arm Coverage Metrics (Reject-Option Framework)
    clean_opportunities: int
    clean_correct_derived: int
    clean_abstained_when_masked: int
    clean_coverage_C: float | None = None
    clean_utility_U: float | None = None  # Alias for backward compatibility
    
    # Spontaneous / De-Novo Mutation & Unsupported Concrete Rates on Unexposed Opportunities
    unexposed_false_children_emitted: int = 0
    unexposed_concrete_children_emitted: int = 0
    mu_de_novo: float = 0.0
    mu_unsupported_concrete: float = 0.0
    
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
        """Compute transmission metrics, clean coverage, and de-novo mutations at a given exposure dose p."""
        # 1. Filter opportunities for this exposure level
        opps = [o for o in self.opportunities if abs(o.exposure_p - exposure_p) < 1e-4]
        
        # 2. Infected Arm Metrics (G1 Semantic Parents -> G2 Children)
        inf_opps = [o for o in opps if o.arm == "infected" and o.parent_phenotype == "semantic"]
        
        # Total distinct semantic parents active in this condition (G1)
        sem_parent_ids = {p.parent_node_id for p in self.parents.values() if p.arm == "infected" and p.parent_phenotype == "semantic" and p.parent_generation == 1}
        condition_parents = [p for p in self.parents.values() if p.parent_node_id in {o.parent_node_id for o in inf_opps} and p.arm == "infected" and p.parent_phenotype == "semantic"]
        num_parents = len(condition_parents) if condition_parents else len(sem_parent_ids)
        
        tot_opps = len(inf_opps)
        exp_opps = len([o for o in inf_opps if o.is_exposed])
        unexp_opps = tot_opps - exp_opps
        
        # Transmitted infected children (strictly from EXPOSED opportunities)
        gen_inf_trans = len([o for o in inf_opps if o.is_exposed and o.is_generated and o.child_phenotype in ("semantic", "epistemic", "control")])
        wri_inf_trans = len([o for o in inf_opps if o.is_exposed and o.is_written and o.child_phenotype in ("semantic", "epistemic", "control")])
        
        # De-novo infected children (from UNEXPOSED opportunities)
        wri_inf_denovo = len([o for o in inf_opps if not o.is_exposed and o.is_written and o.child_phenotype in ("semantic", "epistemic", "control")])
        total_wri_inf = wri_inf_trans + wri_inf_denovo

        # Spontaneous / De-Novo mutations on unexposed opportunities:
        # false concrete claims when unexposed (i.e. failed to abstain)
        unexp_false = len([o for o in inf_opps if not o.is_exposed and o.is_generated and o.child_phenotype in ("semantic", "epistemic", "control", "de_novo_error")])
        mu_de_novo = (unexp_false / unexp_opps) if unexp_opps > 0 else 0.0

        # Unsupported concrete outputs on unexposed opportunities:
        # ANY concrete output when evidence withheld (whether false or lucky guess)
        unexp_concrete = len([o for o in inf_opps if not o.is_exposed and (o.is_generated or o.child_phenotype != "extinct")])
        mu_unsupported_concrete = (unexp_concrete / unexp_opps) if unexp_opps > 0 else 0.0

        # Physical parameter calculations
        contact_x = exp_opps / num_parents if num_parents > 0 else 0.0
        tau_s = (gen_inf_trans / exp_opps) if exp_opps > 0 else None
        w_hat = (wri_inf_trans / gen_inf_trans) if gen_inf_trans > 0 else None
        
        r_trans = (wri_inf_trans / num_parents) if num_parents > 0 else 0.0
        r_total_corruption = (total_wri_inf / num_parents) if num_parents > 0 else 0.0
        r_s = r_trans  # Primary lineage transmission reproduction number

        # Fidelity across exposed G2 infected children
        fidelities = [o.ancestral_allele_fidelity for o in inf_opps if o.is_exposed and o.ancestral_allele_fidelity is not None]
        f2 = (sum(fidelities) / len(fidelities)) if fidelities else None

        # 3. Clean Arm Metrics
        clean_opps = [o for o in opps if o.arm == "clean"]
        tot_clean = len(clean_opps)
        clean_correct = len([o for o in clean_opps if o.is_exposed and o.child_phenotype == "healthy"])
        clean_abstained_masked = len([o for o in clean_opps if not o.is_exposed and o.child_phenotype in ("extinct", "healthy") and not o.is_generated])
        
        # Clean Coverage C_clean(p): fraction of tasks where ground truth was derived
        c_clean = clean_correct / tot_clean if tot_clean > 0 else None

        return ExposureDoseSummary(
            exposure_p=exposure_p,
            total_parents=num_parents,
            total_opportunities=tot_opps,
            exposed_opportunities=exp_opps,
            unexposed_opportunities=unexp_opps,
            infected_children_generated=gen_inf_trans,
            transmitted_infected_generated=gen_inf_trans,
            transmitted_infected_written=wri_inf_trans,
            denovo_infected_written=wri_inf_denovo,
            infected_children_written=total_wri_inf,
            contact_rate_X=contact_x,
            epistemic_transmissibility_tau_S=tau_s,
            write_admission_W_hat=w_hat,
            write_admission_W_policy=1.0,
            reproduction_number_R_S=r_s,
            reproduction_number_R_trans=r_trans,
            reproduction_number_R_total_corruption=r_total_corruption,
            clean_opportunities=tot_clean,
            clean_correct_derived=clean_correct,
            clean_abstained_when_masked=clean_abstained_masked,
            clean_coverage_C=c_clean,
            clean_utility_U=c_clean,
            unexposed_false_children_emitted=unexp_false,
            unexposed_concrete_children_emitted=unexp_concrete,
            mu_de_novo=mu_de_novo,
            mu_unsupported_concrete=mu_unsupported_concrete,
            ancestral_fidelity_F2=f2,
        )
