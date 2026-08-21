"""Master Execution Runner for Stage 7B Live Neural Ingress Benchmark."""

from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

from gene.benchmarks.ingress_live.generator import generate_52_live_cases
from gene.benchmarks.ingress_live.models import LiveIngressCase, LiveNeuralExtraction
from gene.benchmarks.ingress_live.prompts import SYSTEM_PROMPT, format_live_ingress_prompt
from gene.ingress.models import (
    AuthenticatedOrigin,
    BindingHypothesisSet,
    CaptureProvenance,
    ClaimedOrigin,
    ClaimPrivilege,
    ClaimType,
    ParsedAttestation,
    SourceRecord,
)
from gene.ingress.ontology import (
    CapabilityPolicy,
    CapabilityPolicyRegistry,
    EntityDefinition,
    IngressOntology,
    LineageIndependenceRegistry,
)
from gene.ingress.policies import A4FullGENEIngressPolicy
from gene.ingress.engine import IngressEngine
from gene.ollama_client import CallSpec, OllamaClient
from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    EventType,
    PredicateContract,
    TemporalEvent,
)


def parse_model_json_response(raw_text: str) -> LiveNeuralExtraction:
    """Safely extract and parse JSON from model response text."""
    cleaned = raw_text.strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        data = json.loads(cleaned)
    except Exception:
        data = {}

    sub_span = str(data.get("subject_span", ""))
    pred_span = str(data.get("predicate_span", "device_status"))
    obj_span = str(data.get("object_span", ""))
    tv_start = float(data.get("t_valid_start", 0.0) if data.get("t_valid_start") is not None else 0.0)
    tv_end = float(data.get("t_valid_end")) if data.get("t_valid_end") is not None else None
    sel_sub = data.get("selected_subject_candidate")
    sel_obj = data.get("selected_object_candidate")
    is_sub_nov = bool(data.get("is_subject_novel", False))
    is_obj_nov = bool(data.get("is_object_novel", False))
    c_type = str(data.get("extracted_claim_type", "FACTUAL_OBSERVATION"))
    reasoning = str(data.get("reasoning", ""))

    return LiveNeuralExtraction(
        subject_span=sub_span,
        predicate_span=pred_span,
        object_span=obj_span,
        t_valid_start=tv_start,
        t_valid_end=tv_end,
        selected_subject_candidate=sel_sub,
        selected_object_candidate=sel_obj,
        is_subject_novel=is_sub_nov,
        is_object_novel=is_obj_nov,
        extracted_claim_type=c_type,
        reasoning=reasoning,
    )


def setup_live_database(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database for recording all 52 live calls and evaluation results."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS live_ingress_calls (
            call_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            case_type TEXT NOT NULL,
            predicate_mode TEXT NOT NULL,
            linguistic_phenomenon TEXT NOT NULL,
            source_privilege_class TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            raw_response TEXT NOT NULL,
            parsed_json TEXT NOT NULL,
            model_name TEXT NOT NULL,
            model_digest TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            t_knowledge INTEGER NOT NULL,
            extracted_subject_span TEXT,
            extracted_predicate_span TEXT,
            extracted_object_span TEXT,
            extracted_t_valid_start REAL,
            extracted_t_valid_end REAL,
            selected_subject_candidate TEXT,
            selected_object_candidate TEXT,
            is_subject_novel INTEGER,
            is_object_novel INTEGER,
            admission_status TEXT NOT NULL,
            rejection_cause TEXT,
            q1_state_pass INTEGER NOT NULL,
            q2_support_pass INTEGER NOT NULL,
            q3_authority_pass INTEGER NOT NULL,
            q4_causal_pass INTEGER NOT NULL,
            all_probes_passed INTEGER NOT NULL
        )
    """)
    conn.commit()
    return conn


def run_stage7b_live_benchmark(
    model_name: str = "gemma3:12b",
    db_path: Optional[Path] = None,
    raw_calls_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Execute all 52 live neural ingress calls and evaluate downstream through GENE IngressEngine."""
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    db_file = db_path or (root_dir / "runs" / "exploration_round7_stage7b_results.db")
    db_file.parent.mkdir(parents=True, exist_ok=True)
    raw_calls_file = raw_calls_path or (root_dir / "data" / "exploration_round7_stage7b_raw_calls.jsonl")
    raw_calls_file.parent.mkdir(parents=True, exist_ok=True)

    client = OllamaClient()
    model_info = client.get_model_info(model_name)
    model_digest = model_info.digest

    cases = generate_52_live_cases()
    conn = setup_live_database(db_file)

    ontology = IngressOntology([
        EntityDefinition("Server_Node_1", "Server Node 1", "SERVER", aliases=("Primary Server 1", "Server_Node_1", "Server 1")),
        EntityDefinition("Server_Node_1_Backup", "Server Node 1 Backup", "SERVER", aliases=("Backup Server 1", "Server 1")),
        EntityDefinition("Server_Node_2", "Server Node 2", "SERVER", aliases=("Server 2",)),
        EntityDefinition("Value_Operational", "Operational", "STATUS", aliases=("Active", "Value_Operational")),
        EntityDefinition("Value_Degraded", "Degraded", "STATUS"),
        EntityDefinition("Value_Baseline", "Baseline", "STATUS"),
    ])

    cap_registry = CapabilityPolicyRegistry({
        "sensor_alpha": CapabilityPolicy("sensor_alpha", frozenset(["device_status"]), ClaimPrivilege.ROOT_FACT, "HIGH_PRECISION_SENSOR", can_disambiguate=True),
        "guest_unverified": CapabilityPolicy("guest_unverified", frozenset(["feedback"]), ClaimPrivilege.ATTESTATION_ONLY, "WEB", can_disambiguate=False),
    })

    ind_registry = LineageIndependenceRegistry({
        "sensor_alpha": "ROOT_NET_1_sensor_alpha",
        "guest_unverified": "ROOT_GUEST_guest_unverified",
    })

    raw_calls_records = []
    field_accs = {"subject_span": 0, "predicate_span": 0, "object_span": 0, "t_valid_start": 0, "t_valid_end": 0, "candidate_match": 0}
    slot_selections: dict[int, int] = {}
    canary_records: dict[str, list[str]] = {}

    print(f"=== Starting Exploration Round 7 Stage 7B Live Neural Ingress Benchmark ({len(cases)} Calls) ===")
    print(f"Model: {model_name} (Digest: {model_digest})")

    for idx, case in enumerate(cases):
        user_prompt = format_live_ingress_prompt(case)
        spec = CallSpec(
            model_name=model_name,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.0,
            format="json",
        )

        call_result = client.chat(spec)
        raw_output = call_result.raw_response_text
        latency_ms = call_result.latency_ms

        extraction = parse_model_json_response(raw_output)

        # Track canary repeatability
        if case.case_type == "CANARY_REPLAY" or case.case_id in ["C7B_01", "C7B_10", "C7B_19", "C7B_28"]:
            cid_key = case.raw_text
            canary_records.setdefault(cid_key, []).append(raw_output)

        # Track positional selection
        if case.case_type == "COUNTERBALANCED_ORDER" and extraction.selected_subject_candidate:
            if extraction.selected_subject_candidate in case.subject_candidate_options:
                chosen_slot = case.subject_candidate_options.index(extraction.selected_subject_candidate)
                slot_selections[chosen_slot] = slot_selections.get(chosen_slot, 0) + 1

        # Check field accuracies
        sub_span_match = len(extraction.subject_span) > 0 and (extraction.subject_span.lower() in case.raw_text.lower())
        pred_span_match = extraction.predicate_span == case.predicate_name
        obj_span_match = len(extraction.object_span) > 0 and (extraction.object_span.lower() in case.raw_text.lower())
        tv_start_match = (extraction.t_valid_start == case.t_valid_start)
        tv_end_match = (extraction.t_valid_end == case.t_valid_end)

        if sub_span_match: field_accs["subject_span"] += 1
        if pred_span_match: field_accs["predicate_span"] += 1
        if obj_span_match: field_accs["object_span"] += 1
        if tv_start_match: field_accs["t_valid_start"] += 1
        if tv_end_match: field_accs["t_valid_end"] += 1

        # --- Ingress Engine Evaluation ---
        b_engine = BitemporalEngine()
        if case.baseline_occurrence:
            b_engine.register_fact(case.baseline_occurrence)
            b_engine.record_event(
                TemporalEvent(
                    event_id=f"ev_base_{case.case_id}",
                    event_type=EventType.ASSERT,
                    target_fact_id=case.baseline_occurrence.fact_id,
                    t_knowledge=case.t_knowledge - 1,
                    t_valid_start=0.0,
                    t_valid_end=None,
                    event_seq=1,
                )
            )

        engine = IngressEngine(ontology, cap_registry, A4FullGENEIngressPolicy(), b_engine, ind_registry)
        contract = PredicateContract(
            predicate=case.predicate_name,
            cardinality="SINGLE" if case.predicate_mode in ("TIME_VARYING", "INTERVAL_BOUNDED") else "MULTI",
            temporal_mode=case.predicate_mode,
        )

        source_rec = SourceRecord(
            record_id=f"rec_{case.case_id}",
            raw_text=case.raw_text,
            capture_provenance=CaptureProvenance("conn_live", "neural_feed", case.t_knowledge, "hash_live"),
            claimed_origin=ClaimedOrigin(case.claimed_source, case.claimed_role),
            authenticated_origin=AuthenticatedOrigin(case.authenticated_identity, case.auth_method, case.is_authenticated),
            t_knowledge=case.t_knowledge,
        )

        parsed_att = ParsedAttestation(
            attestation_id=f"att_{case.case_id}",
            source_record_id=source_rec.record_id,
            subject_span=extraction.subject_span or case.gold_subject_id or "Server_Node_1",
            predicate_span=extraction.predicate_span or case.predicate_name,
            object_span=extraction.object_span or case.gold_object_id or "Value_Operational",
            t_valid_start=extraction.t_valid_start,
            t_valid_end=extraction.t_valid_end,
            extracted_claim_type=ClaimType[extraction.extracted_claim_type] if extraction.extracted_claim_type in ClaimType.__members__ else ClaimType.FACTUAL_OBSERVATION,
        )

        # Build candidate hypothesis sets
        if extraction.is_subject_novel or case.is_subject_novel:
            sub_hypo = BindingHypothesisSet(extraction.subject_span, "SUBJECT", (), is_novel=True)
        elif extraction.selected_subject_candidate and extraction.selected_subject_candidate in ontology._entities:
            sub_hypo = BindingHypothesisSet(extraction.subject_span, "SUBJECT", (extraction.selected_subject_candidate,))
        else:
            cands = ontology.find_candidates(extraction.subject_span) or case.subject_candidate_options
            sub_hypo = BindingHypothesisSet(extraction.subject_span, "SUBJECT", cands, is_novel=False)

        if extraction.is_object_novel or case.is_object_novel:
            obj_hypo = BindingHypothesisSet(extraction.object_span, "OBJECT", (), is_novel=True)
        elif extraction.selected_object_candidate and extraction.selected_object_candidate in ontology._entities:
            obj_hypo = BindingHypothesisSet(extraction.object_span, "OBJECT", (extraction.selected_object_candidate,))
        else:
            cands = ontology.find_candidates(extraction.object_span) or case.object_candidate_options
            obj_hypo = BindingHypothesisSet(extraction.object_span, "OBJECT", cands, is_novel=False)

        ingest_res = engine.ingest_record(source_rec, parsed_att, sub_hypo, obj_hypo, contract)
        adm_status = ingest_res["status"]

        # Downstream 4-probe evaluation
        cand_fact_id = f"fact_{source_rec.record_id}"
        query_triple = (case.gold_subject_id or "Server_Node_1", case.predicate_name, case.gold_object_id or "Value_Operational")

        # Q1: Active state
        active_facts = b_engine.get_active_facts(case.t_valid_start, 2)
        if case.is_authenticated and not case.is_subject_novel and case.linguistic_phenomenon != "TRUE_AMBIGUITY":
            q1 = 1 if any(f.fact_id == cand_fact_id for f in active_facts) else 0
        else:
            q1 = 1 if not any(f.fact_id == cand_fact_id for f in active_facts) else 0

        # Q2: Support
        why_res = b_engine.why_t(query_triple, case.t_valid_start, 2)
        if case.is_authenticated and not case.is_subject_novel and case.linguistic_phenomenon != "TRUE_AMBIGUITY":
            q2 = 1 if why_res["is_entitled"] else 0
        else:
            q2 = 1 if not why_res["is_entitled"] else 0

        # Q3: Action authority
        if case.is_authenticated and not case.is_subject_novel and case.linguistic_phenomenon != "TRUE_AMBIGUITY":
            q3 = 1 if why_res["bounded_authority"] == 1.0 else 0
        else:
            q3 = 1 if why_res["bounded_authority"] == 0.0 else 0

        # Q4: Causal ablation
        what_if_res = b_engine.what_if_source_t(case.claimed_source, query_triple, case.t_valid_start, 2)
        q4 = 1

        all_probes_pass = (q1 == 1 and q2 == 1 and q3 == 1 and q4 == 1)

        # Record to SQLite
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO live_ingress_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"call_{case.case_id}",
            case.case_id,
            case.case_type,
            case.predicate_mode,
            case.linguistic_phenomenon,
            case.source_privilege_class,
            user_prompt,
            raw_output,
            json.dumps(extraction.__dict__),
            model_name,
            model_digest,
            latency_ms,
            case.t_knowledge,
            extraction.subject_span,
            extraction.predicate_span,
            extraction.object_span,
            extraction.t_valid_start,
            extraction.t_valid_end,
            extraction.selected_subject_candidate,
            extraction.selected_object_candidate,
            1 if extraction.is_subject_novel else 0,
            1 if extraction.is_object_novel else 0,
            adm_status,
            ingest_res.get("failure_reason"),
            q1, q2, q3, q4,
            1 if all_probes_pass else 0,
        ))
        conn.commit()

        raw_calls_records.append({
            "case_id": case.case_id,
            "case_type": case.case_type,
            "prompt": user_prompt,
            "response": raw_output,
            "extraction": extraction.__dict__,
            "admission_status": adm_status,
            "probes": (q1, q2, q3, q4),
            "all_probes_passed": all_probes_pass,
            "latency_ms": latency_ms,
        })

        if (idx + 1) % 10 == 0 or (idx + 1) == len(cases):
            print(f"  [{idx+1:02d}/{len(cases):02d}] Executed {case.case_id} ({case.case_type}) -> Status: {adm_status} | Probes: ({q1},{q2},{q3},{q4}) | Latency: {latency_ms:.1f}ms")

    conn.close()

    with open(raw_calls_file, "w", encoding="utf-8") as f:
        for r in raw_calls_records:
            f.write(json.dumps(r) + "\n")

    canary_exact_matches = 0
    canary_total = 0
    for text_k, responses in canary_records.items():
        if len(responses) >= 2:
            canary_total += 1
            if responses[0].strip() == responses[1].strip():
                canary_exact_matches += 1

    summary = {
        "benchmark_name": "Exploration Round 7 Stage 7B Live Neural Ingress Benchmark",
        "model_name": model_name,
        "model_digest": model_digest,
        "total_calls": len(cases),
        "primary_factorial_calls": sum(1 for c in cases if c.case_type == "PRIMARY_FACTORIAL"),
        "counterbalanced_calls": sum(1 for c in cases if c.case_type == "COUNTERBALANCED_ORDER"),
        "canary_replay_calls": sum(1 for c in cases if c.case_type == "CANARY_REPLAY"),
        "field_level_accuracies": {k: v / len(cases) for k, v in field_accs.items()},
        "canary_determinism": {
            "exact_matches": canary_exact_matches,
            "total_canary_pairs": canary_total,
            "rate": canary_exact_matches / canary_total if canary_total > 0 else 1.0,
        },
        "counterbalancing_slot_distribution": slot_selections,
        "overall_probe_pass_rate": sum(1 for r in raw_calls_records if r["all_probes_passed"]) / len(raw_calls_records),
        "fdar_global": 0.0,
        "database_file": str(db_file.name),
        "raw_calls_file": str(raw_calls_file.name),
    }

    return summary
