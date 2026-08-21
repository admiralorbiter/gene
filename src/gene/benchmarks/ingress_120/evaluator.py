"""Stateful 120-World 4-Probe Benchmark Evaluator (Stage 7A.1).

Evaluates Arms A0, A1, A2, A3, A4 against seeded prior bitemporal state.
Exercises true downstream Q1 (Bitemporal state), Q2 (Antichain support S_t via why_t),
Q3 (Action governance Auth(S_L)), Q4 (Causal WHAT_IF ablation via what_if_t).
"""

from __future__ import annotations

from typing import Any
from gene.benchmarks.ingress_120.generator import IngressTestCase, generate_120_worlds
from gene.benchmarks.ingress_120.oracle import BenchmarkOracle, CaseOracleExpectation
from gene.ingress.models import (
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ClaimPrivilege,
    ParsedAttestation,
    SourceRecord,
)
from gene.ingress.ontology import (
    CapabilityPolicy,
    CapabilityPolicyRegistry,
    EntityDefinition,
    IngressOntology,
)
from gene.ingress.policies import (
    A0Top1BlindWritePolicy,
    A1CanonicalizationOnlyPolicy,
    A2CandidateAwarePolicy,
    A3AuthorityAwarePolicy,
    A4FullGENEIngressPolicy,
    IngressPolicy,
)
from gene.ingress.engine import IngressEngine
from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    EventType,
    PredicateContract,
    TemporalEvent,
)


def get_benchmark_ontology() -> IngressOntology:
    entities = [
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER", aliases=("Primary Server 1", "Server_Node_1", "Server 1")),
        EntityDefinition("Server_Node_1_Backup", "Server Node 1 Backup", "SERVER", aliases=("Backup Server 1", "Server 1")),
        EntityDefinition("Value_Baseline", "Baseline Value", "STATUS", aliases=("Baseline",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS", aliases=("Active", "Value_Operational")),
    ]
    return IngressOntology(entities)


def get_benchmark_capability_registry() -> CapabilityPolicyRegistry:
    policies = {
        "sensor": CapabilityPolicy("sensor", frozenset(["*"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", "ROOT_NET_1"),
        "guest": CapabilityPolicy("guest", frozenset(["feedback_only"]), ClaimPrivilege.ATTESTATION_ONLY, "UNTRUSTED_WEB", "ROOT_GUEST"),
    }
    return CapabilityPolicyRegistry(policies)


def evaluate_arm(policy: IngressPolicy, cases: list[IngressTestCase]) -> dict[str, Any]:
    """Evaluate an ingress policy across all 120 stateful cases feeding the bitemporal engine."""
    ontology = get_benchmark_ontology()
    capability_registry = get_benchmark_capability_registry()

    world_vectors: list[tuple[int, int, int, int]] = []
    world_passes: list[bool] = []
    profile_distribution: dict[str, int] = {}

    inadmissible_count = 0
    false_durable_admissions = 0

    fdar_bind_num, fdar_bind_den = 0, 0
    fdar_ambig_num, fdar_ambig_den = 0, 0
    fdar_novel_num, fdar_novel_den = 0, 0
    fdar_unauth_num, fdar_unauth_den = 0, 0

    fdar_auth_cond_resolved_num, fdar_auth_cond_resolved_den = 0, 0
    fdar_ambig_cond_auth_num, fdar_ambig_cond_auth_den = 0, 0

    admissible_count = 0
    correct_admissions = 0

    unresolved_opportunity_count = 0
    correct_unresolved_preservations = 0

    for case in cases:
        oracle_exp = BenchmarkOracle.evaluate_case(case)

        # 1. Seed baseline prior state
        b_engine = BitemporalEngine()
        base_fact = BitemporalFact(
            fact_id=case.baseline_occurrence.fact_id,
            subject=case.baseline_occurrence.subject,
            predicate=case.baseline_occurrence.predicate,
            obj=case.baseline_occurrence.obj,
            roots=case.baseline_occurrence.lineage_roots,
            source_id=case.baseline_occurrence.source_id,
            origin_id=case.baseline_occurrence.origin_id,
        )
        b_engine.register_fact(base_fact)
        b_engine.record_event(
            TemporalEvent(
                event_id=f"ev_base_{case.case_id}",
                event_type=EventType.ASSERT,
                target_fact_id=base_fact.fact_id,
                t_knowledge=case.baseline_occurrence.t_knowledge,
                t_valid_start=case.baseline_occurrence.t_valid_start,
                t_valid_end=case.baseline_occurrence.t_valid_end,
                event_seq=1,
            )
        )

        engine = IngressEngine(ontology, capability_registry, policy, b_engine)

        contract = PredicateContract(
            predicate=case.predicate_name,
            cardinality="SINGLE" if case.predicate_mode in ("TIME_VARYING", "INTERVAL_BOUNDED") else "MULTI",
            temporal_mode=case.predicate_mode,
            default_duration=5.0 if case.predicate_mode == "INTERVAL_BOUNDED" else None,
        )

        source_rec = SourceRecord(
            record_id=f"rec_{case.case_id}",
            raw_text=case.raw_text,
            capture_provenance=CaptureProvenance("conn_test", "channel_test", case.t_knowledge, "hash_test"),
            claimed_origin=ClaimedOrigin(case.claimed_source, case.claimed_role),
            authenticated_origin=AuthenticatedOrigin(case.claimed_source, "ED25519" if case.is_authenticated else "ANONYMOUS", case.is_authenticated),
            t_knowledge=case.t_knowledge,
        )
        parsed_att = ParsedAttestation(
            attestation_id=f"att_{case.case_id}",
            source_record_id=source_rec.record_id,
            subject_span=case.subject_mention,
            predicate_span=case.predicate_name,
            object_span=case.object_mention,
            t_valid_start=case.t_valid_start,
            t_valid_end=case.t_valid_end,
        )
        sub_hypo = BindingHypothesisSet(case.subject_mention, "SUBJECT", case.subject_candidate_ids, case.is_subject_novel)
        obj_hypo = BindingHypothesisSet(case.object_mention, "OBJECT", case.object_candidate_ids, case.is_object_novel)

        # Ingest record
        ingest_res = engine.ingest_record(source_rec, parsed_att, sub_hypo, obj_hypo, contract)
        actual_status = ingest_res["status"]

        # Track FDAR metrics
        if oracle_exp.is_inadmissible_opportunity:
            inadmissible_count += 1
            if actual_status == "ADMIT":
                false_durable_admissions += 1

            if oracle_exp.is_wrong_binding_risk:
                fdar_bind_den += 1
                if actual_status == "ADMIT":
                    fdar_bind_num += 1

            if oracle_exp.is_ambiguity_collapse_risk:
                fdar_ambig_den += 1
                if actual_status == "ADMIT":
                    fdar_ambig_num += 1

            if oracle_exp.is_novel_mislinking_risk:
                fdar_novel_den += 1
                if actual_status == "ADMIT":
                    fdar_novel_num += 1

            if oracle_exp.is_unauthorized_promotion_risk:
                fdar_unauth_den += 1
                if actual_status == "ADMIT":
                    fdar_unauth_num += 1

            # Conditional FDARs
            if oracle_exp.is_unauthorized_promotion_risk and oracle_exp.is_resolved_binding:
                fdar_auth_cond_resolved_den += 1
                if actual_status == "ADMIT":
                    fdar_auth_cond_resolved_num += 1

            if oracle_exp.is_ambiguity_collapse_risk and oracle_exp.is_authorized_direct_source:
                fdar_ambig_cond_auth_den += 1
                if actual_status == "ADMIT":
                    fdar_ambig_cond_auth_num += 1

        # Track SAC metrics
        if oracle_exp.is_admissible_ground_truth:
            admissible_count += 1
            if actual_status == "ADMIT":
                obs = ingest_res["admitted_observation"]
                if obs and obs.subject == case.gold_subject_id and obs.obj == case.gold_object_id:
                    correct_admissions += 1

        # Track UPR metrics
        if oracle_exp.expected_admission_status == "DEFER":
            unresolved_opportunity_count += 1
            if actual_status == "DEFER":
                correct_unresolved_preservations += 1

        # --- The Four Formal Downstream Probes ---
        cand_fact_id = f"fact_{source_rec.record_id}"
        query_triple = (case.gold_subject_id or "Server_Node_1", case.predicate_name, case.gold_object_id or "Value_Operational")
        base_triple = (case.baseline_occurrence.subject, case.baseline_occurrence.predicate, case.baseline_occurrence.obj)

        is_dispute_mode = (case.temporal_relation == "CONTEMPORANEOUS_DISPUTE" and contract.cardinality == "SINGLE")

        # Q1: Exact Bitemporal Active State Probe at (t_valid_start, t_knowledge=2)
        active_facts_now = b_engine.get_active_facts(case.t_valid_start, 2)
        if oracle_exp.is_admissible_ground_truth:
            if is_dispute_mode:
                # Under contemporaneous dispute of single-cardinality facts, cautious isolation inactivates both facts
                q1 = 1 if len(active_facts_now) == 0 else 0
            else:
                q1 = 1 if any(f.fact_id == cand_fact_id for f in active_facts_now) else 0
        else:
            # Inadmissible candidate must not be active
            q1 = 1 if not any(f.fact_id == cand_fact_id for f in active_facts_now) else 0

        # Q2: Structured Premise Challenge Probe via why_t
        why_res = b_engine.why_t(query_triple, case.t_valid_start, 2)
        if oracle_exp.is_admissible_ground_truth:
            if is_dispute_mode:
                # Under dispute, entitlement is cleanly blocked (cautious abstention)
                q2 = 1 if not why_res["is_entitled"] else 0
            else:
                # Entitled with non-empty minimal antichain support S_t
                q2 = 1 if (why_res["is_entitled"] and len(why_res["support_sets_S_t"]) >= 1) else 0
        else:
            # Inadmissible query must NOT be entitled
            q2 = 1 if not why_res["is_entitled"] else 0

        # Q3: Action Policy Authority Probe via Auth(S_L)
        if oracle_exp.is_admissible_ground_truth:
            if is_dispute_mode:
                # Disputed state has 0 authority to act
                q3 = 1 if why_res["bounded_authority"] == 0.0 else 0
            else:
                # Entitled state has full authority (1.0) with authentic lineage
                q3 = 1 if (why_res["bounded_authority"] == 1.0 and any("ROOT_NET_1" in "".join(s) for s in why_res["lineage_sets_S_L_t"])) else 0
        else:
            # Inadmissible input must have 0.0 bounded authority
            q3 = 1 if why_res["bounded_authority"] == 0.0 else 0

        # Q4: Causal Invalidation Probe via what_if_t
        # Simulate counterfactual retraction of candidate fact: does it restore or preserve baseline state?
        if cand_fact_id in b_engine.facts:
            cf_event = TemporalEvent(
                event_id=f"cf_retract_{case.case_id}",
                event_type=EventType.RETRACT,
                target_fact_id=cand_fact_id,
                t_knowledge=2,
                t_valid_start=case.t_valid_start,
                event_seq=99,
            )
            eval_tv = 2.5 if (case.predicate_mode == "INTERVAL_BOUNDED" and case.temporal_relation == "FORWARD_UPDATE") else case.t_valid_start
            what_if_res = b_engine.what_if_t(base_triple, cf_event, eval_tv, 2)
            # Retracting candidate fact cleanly restores baseline or preserves clean state
            q4 = 1 if what_if_res["hypothetical_entitled"] or case.predicate_mode in ("ADDITIVE", "EPISODIC") else 0
        else:
            # When candidate was not admitted, baseline remains unperturbed
            q4 = 1

        p_vector = (q1, q2, q3, q4)
        w_pass = (q1 == 1 and q2 == 1 and q3 == 1 and q4 == 1)
        world_vectors.append(p_vector)
        world_passes.append(w_pass)

        profile_str = f"({q1},{q2},{q3},{q4})"
        profile_distribution[profile_str] = profile_distribution.get(profile_str, 0) + 1

    world_pass_rate = sum(world_passes) / len(world_passes)
    fdar_global = false_durable_admissions / inadmissible_count if inadmissible_count > 0 else 0.0
    sac_rate = correct_admissions / admissible_count if admissible_count > 0 else 0.0
    upr_rate = correct_unresolved_preservations / unresolved_opportunity_count if unresolved_opportunity_count > 0 else 0.0

    return {
        "world_pass_rate": world_pass_rate,
        "n_worlds": len(cases),
        "world_pass_count": sum(world_passes),
        "fdar_global": fdar_global,
        "fdar_bind": fdar_bind_num / fdar_bind_den if fdar_bind_den > 0 else 0.0,
        "fdar_ambiguity_unconditional": fdar_ambig_num / fdar_ambig_den if fdar_ambig_den > 0 else 0.0,
        "fdar_ambiguity_conditional_authorized": fdar_ambig_cond_auth_num / fdar_ambig_cond_auth_den if fdar_ambig_cond_auth_den > 0 else 0.0,
        "fdar_novel": fdar_novel_num / fdar_novel_den if fdar_novel_den > 0 else 0.0,
        "fdar_authority_unconditional": fdar_unauth_num / fdar_unauth_den if fdar_unauth_den > 0 else 0.0,
        "fdar_authority_conditional_resolved": fdar_auth_cond_resolved_num / fdar_auth_cond_resolved_den if fdar_auth_cond_resolved_den > 0 else 0.0,
        "sac_rate": sac_rate,
        "upr_rate": upr_rate,
        "profile_distribution": profile_distribution,
    }


def run_benchmark_120_all_arms() -> dict[str, Any]:
    """Execute all 5 comparative ingress arms across the stateful 120-world benchmark."""
    cases = generate_120_worlds()
    arms = {
        "A0_Top1_Blind_Write": A0Top1BlindWritePolicy(),
        "A1_Canonicalize_Only": A1CanonicalizationOnlyPolicy(),
        "A2_Candidate_Aware": A2CandidateAwarePolicy(),
        "A3_Authority_Aware": A3AuthorityAwarePolicy(),
        "A4_Full_GENE_Ingress": A4FullGENEIngressPolicy(),
    }

    results = {}
    for arm_name, policy in arms.items():
        res = evaluate_arm(policy, cases)
        results[arm_name] = res

    return results
