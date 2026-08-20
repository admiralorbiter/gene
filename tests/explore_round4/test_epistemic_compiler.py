"""Tests for EpistemicIR, Transformations, and Context Compiler."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.epistemic_ir import EpistemicIR, PremiseNode, SupportEnvironment
from gene.experiments.transformations import (
    PermutationTransform,
    RoleEquivarianceTransform,
    SupportAugmentationTransform,
)
from gene.experiments.context_compiler import EpistemicContextCompiler


def build_sample_recombinant_ir() -> EpistemicIR:
    premises = {
        "A": PremiseNode(premise_id="A", text="Nerin is manager of VELORA", role="manager", subject="VELORA", root_id="R1"),
        "B": PremiseNode(premise_id="B", text="Nerin reports to sector lead S1", role="reports_to_S1", subject="VELORA", root_id="R1"),
        "D": PremiseNode(premise_id="D", text="Vael is sector lead of VELORA", role="sector_lead", subject="VELORA", root_id="R2"),
        "E": PremiseNode(premise_id="E", text="Vael reports to sector lead S2", role="reports_to_S2", subject="VELORA", root_id="R2"),
    }
    envs = [
        SupportEnvironment(path_id="path_AB", required_premise_ids=["A", "B"]),
        SupportEnvironment(path_id="path_DE", required_premise_ids=["D", "E"]),
    ]
    return EpistemicIR(
        target_station="VELORA",
        target_claim="station_operates_protocol(VELORA, PROTO_X7)",
        expected_protocol="PROTO_X7",
        premises=premises,
        support_environments=envs,
        invalidated_roots=[],
        query_question="What protocol is authorized for VELORA?",
    )


def test_epistemic_ir_support_survival_and_invalidation():
    ir = build_sample_recombinant_ir()
    assert ir.is_formally_entitled()
    assert len(ir.get_surviving_support_environments()) == 2

    # Invalidate root R1 -> Path AB collapses, Path DE survives
    ir.invalidated_roots.append("R1")
    surviving = ir.get_surviving_support_environments()
    assert len(surviving) == 1
    assert surviving[0].path_id == "path_DE"
    assert ir.is_formally_entitled()

    # Invalidate root R2 -> Both collapse
    ir.invalidated_roots.append("R2")
    assert not ir.is_formally_entitled()
    assert len(ir.get_surviving_support_environments()) == 0


def test_permutation_transformation():
    ir = build_sample_recombinant_ir()
    perms = PermutationTransform.generate_all_permutations(ir)
    assert len(perms) == 24  # 4! = 24


def test_role_equivariance_and_anonymization():
    ir = build_sample_recombinant_ir()
    
    # Swap manager <-> sector_lead
    swapped = RoleEquivarianceTransform.swap_role_slots(ir, "manager", "sector_lead")
    assert "sector_lead" in swapped.premises["A"].text
    assert "manager" in swapped.premises["D"].text

    # Anonymize to opaque synthetic roles
    anonymized = RoleEquivarianceTransform.anonymize_roles(
        ir, {"manager": "ROLE_Q7", "sector_lead": "ROLE_M2"}
    )
    assert "ROLE_Q7" in anonymized.premises["A"].text
    assert "ROLE_M2" in anonymized.premises["D"].text

    # Rotate station entity VELORA -> KESTREL
    rotated = RoleEquivarianceTransform.rotate_station_entity(ir, "VELORA", "KESTREL")
    assert rotated.target_station == "KESTREL"
    assert "KESTREL" in rotated.premises["A"].text
    assert "KESTREL" in rotated.query_question


def test_context_compiler_all_backends():
    ir = build_sample_recombinant_ir()

    for backend in ["raw_flat", "canonical_support_blocks", "lineage_deduplicated", "support_certificate"]:
        compiler = EpistemicContextCompiler(backend=backend)
        prompt = compiler.compile(ir)
        assert "QUESTION: What protocol is authorized for VELORA?" in prompt
        assert "Return strictly JSON" in prompt
        if backend == "raw_flat":
            assert "RETRIEVED EPISODIC EVIDENCE:" in prompt
        elif backend == "canonical_support_blocks":
            assert "EPISTEMIC SUPPORT PATHWAYS:" in prompt
        elif backend == "lineage_deduplicated":
            assert "GENEALOGICALLY DEDUPLICATED ROOTS:" in prompt
        elif backend == "support_certificate":
            assert "EPISTEMIC AUDIT CERTIFICATE:" in prompt
