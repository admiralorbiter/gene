"""Next-Generation Matrix and Transmission Metrics Engine.

Tracks multi-generation lineage transmissions (G0 -> G1 -> G2):
- Computes direct generational reproduction rates R_F (founder) and R_S (semantic parent).
- Computes epistemic transmissibility tau_S and ancestral allele fidelities F_1, F_2.
- Builds the empirical Next-Generation / Mean Progeny Matrix M in R^{3x3} for {S, E, C}.
- Handles partial row identifiability explicitly (unobserved rows marked N/A; spectral radius rho(M) computed only when all rows identified).
"""

from __future__ import annotations

import json
from typing import Any, Literal
from pydantic import BaseModel, Field


TYPES = ["semantic", "epistemic", "control"]


class TransmissionEvent(BaseModel):
    """An individual parent-to-child generational transmission observation."""
    parent_node_id: str
    child_node_id: str
    parent_generation: int
    child_generation: int
    parent_phenotype: str  # "founder", "semantic", "epistemic", "control", "healthy", etc.
    child_phenotype: str   # "semantic", "epistemic", "control", "repaired", "extinct", etc.
    ancestral_allele_fidelity: float | None = None


class NextGenMatrixSummary(BaseModel):
    """Summary of multi-type progeny transitions and transmission rates."""
    # Direct Generational Metrics
    founder_reproduction_R_F: float
    semantic_parent_reproduction_R_S: float
    epistemic_transmissibility_tau_S: float
    
    # Ancestral Allele Fidelities
    fidelity_G1_F1: float
    fidelity_G2_F2: float
    
    # Next-Generation / Progeny Matrix
    row_status: dict[str, Literal["observed", "unobserved"]]
    progeny_matrix: dict[str, dict[str, float | None]]
    spectral_radius: float | None = None  # N/A if any row unobserved
    
    # Counts
    founder_count: int
    g1_semantic_parents: int
    g1_epistemic_parents: int
    g1_control_parents: int
    g2_infected_children: int
    g2_repaired_children: int
    g2_extinct_children: int


class NextGenMatrixEngine:
    """Computes transmission statistics and multi-type branching matrices from transmission logs."""

    def __init__(self):
        self.events: list[TransmissionEvent] = []

    def record_transmission(
        self,
        parent_node_id: str,
        child_node_id: str,
        parent_gen: int,
        child_gen: int,
        parent_phenotype: str,
        child_phenotype: str,
        ancestral_allele_fidelity: float | None = None,
    ) -> None:
        """Log a parent-to-child transmission event."""
        self.events.append(TransmissionEvent(
            parent_node_id=parent_node_id,
            child_node_id=child_node_id,
            parent_generation=parent_gen,
            child_generation=child_gen,
            parent_phenotype=parent_phenotype,
            child_phenotype=child_phenotype,
            ancestral_allele_fidelity=ancestral_allele_fidelity,
        ))

    def compute_summary(
        self,
        founder_count: int = 1,
        g1_evaluations: list[Any] | None = None,
        g2_evaluations: list[Any] | None = None,
    ) -> NextGenMatrixSummary:
        """Calculate complete transmission metrics and empirical progeny matrix."""
        # 1. G0 -> G1 Founder Transmission (R_F)
        g1_events = [e for e in self.events if e.parent_generation == 0 and e.child_generation == 1]
        g1_infected = [e for e in g1_events if e.child_phenotype in TYPES]
        r_f = len(g1_infected) / founder_count if founder_count > 0 else 0.0

        # 2. G1 -> G2 Progeny Transitions
        g2_events = [e for e in self.events if e.parent_generation == 1 and e.child_generation == 2]
        
        # Count parent nodes in G1
        g1_sem_parents = {e.parent_node_id for e in g2_events if e.parent_phenotype == "semantic"}
        g1_epi_parents = {e.parent_node_id for e in g2_events if e.parent_phenotype == "epistemic"}
        g1_ctl_parents = {e.parent_node_id for e in g2_events if e.parent_phenotype == "control"}

        num_sem_parents = len(g1_sem_parents)
        num_epi_parents = len(g1_epi_parents)
        num_ctl_parents = len(g1_ctl_parents)

        # Offspring counts from semantic parents
        sem_events = [e for e in g2_events if e.parent_phenotype == "semantic"]
        sem_to_sem = len([e for e in sem_events if e.child_phenotype == "semantic"])
        sem_to_epi = len([e for e in sem_events if e.child_phenotype == "epistemic"])
        sem_to_ctl = len([e for e in sem_events if e.child_phenotype == "control"])
        
        total_infected_from_sem = sem_to_sem + sem_to_epi + sem_to_ctl
        r_s = total_infected_from_sem / num_sem_parents if num_sem_parents > 0 else 0.0
        
        # Epistemic transmissibility tau_S: P(infected child | exposed)
        tau_s = total_infected_from_sem / len(sem_events) if len(sem_events) > 0 else 0.0

        # Build Progeny Matrix
        row_status: dict[str, Literal["observed", "unobserved"]] = {}
        matrix: dict[str, dict[str, float | None]] = {
            "semantic": {"semantic": None, "epistemic": None, "control": None},
            "epistemic": {"semantic": None, "epistemic": None, "control": None},
            "control": {"semantic": None, "epistemic": None, "control": None},
        }

        # S-row
        if num_sem_parents > 0:
            row_status["semantic"] = "observed"
            matrix["semantic"]["semantic"] = sem_to_sem / num_sem_parents
            matrix["semantic"]["epistemic"] = sem_to_epi / num_sem_parents
            matrix["semantic"]["control"] = sem_to_ctl / num_sem_parents
        else:
            row_status["semantic"] = "unobserved"

        # E-row
        if num_epi_parents > 0:
            row_status["epistemic"] = "observed"
            epi_events = [e for e in g2_events if e.parent_phenotype == "epistemic"]
            matrix["epistemic"]["semantic"] = len([e for e in epi_events if e.child_phenotype == "semantic"]) / num_epi_parents
            matrix["epistemic"]["epistemic"] = len([e for e in epi_events if e.child_phenotype == "epistemic"]) / num_epi_parents
            matrix["epistemic"]["control"] = len([e for e in epi_events if e.child_phenotype == "control"]) / num_epi_parents
        else:
            row_status["epistemic"] = "unobserved"

        # C-row
        if num_ctl_parents > 0:
            row_status["control"] = "observed"
            ctl_events = [e for e in g2_events if e.parent_phenotype == "control"]
            matrix["control"]["semantic"] = len([e for e in ctl_events if e.child_phenotype == "semantic"]) / num_ctl_parents
            matrix["control"]["epistemic"] = len([e for e in ctl_events if e.child_phenotype == "epistemic"]) / num_ctl_parents
            matrix["control"]["control"] = len([e for e in ctl_events if e.child_phenotype == "control"]) / num_ctl_parents
        else:
            row_status["control"] = "unobserved"

        # Spectral radius only if all rows observed
        spectral_radius: float | None = None
        if all(status == "observed" for status in row_status.values()):
            try:
                import numpy as np
                m_arr = np.array([
                    [matrix["semantic"]["semantic"], matrix["semantic"]["epistemic"], matrix["semantic"]["control"]],
                    [matrix["epistemic"]["semantic"], matrix["epistemic"]["epistemic"], matrix["epistemic"]["control"]],
                    [matrix["control"]["semantic"], matrix["control"]["epistemic"], matrix["control"]["control"]],
                ], dtype=float)
                eigvals = np.linalg.eigvals(m_arr)
                spectral_radius = float(np.max(np.abs(eigvals)))
            except Exception:
                pass

        # 3. Ancestral Allele Fidelities F_1, F_2
        g1_fidelities = [e.ancestral_allele_fidelity for e in g1_events if e.ancestral_allele_fidelity is not None]
        f1 = sum(g1_fidelities) / len(g1_fidelities) if g1_fidelities else 1.0

        g2_fidelities = [e.ancestral_allele_fidelity for e in g2_events if e.ancestral_allele_fidelity is not None]
        f2 = sum(g2_fidelities) / len(g2_fidelities) if g2_fidelities else 1.0

        return NextGenMatrixSummary(
            founder_reproduction_R_F=r_f,
            semantic_parent_reproduction_R_S=r_s,
            epistemic_transmissibility_tau_S=tau_s,
            fidelity_G1_F1=f1,
            fidelity_G2_F2=f2,
            row_status=row_status,
            progeny_matrix=matrix,
            spectral_radius=spectral_radius,
            founder_count=founder_count,
            g1_semantic_parents=num_sem_parents,
            g1_epistemic_parents=num_epi_parents,
            g1_control_parents=num_ctl_parents,
            g2_infected_children=len([e for e in g2_events if e.child_phenotype in TYPES]),
            g2_repaired_children=len([e for e in g2_events if e.child_phenotype == "repaired"]),
            g2_extinct_children=len([e for e in g2_events if e.child_phenotype == "extinct"]),
        )
