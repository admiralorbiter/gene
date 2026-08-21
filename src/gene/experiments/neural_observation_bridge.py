"""Exploration Round 6 Stage 6C: Neural Semantic Observation Extraction & Upward Error Migration Harness.

Implements the 28-call live neural assay testing whether neural models reliably extract
structured observations from natural language for a formal epistemic runtime, comparing:
- Arm N1: End-to-End Direct Transition Emission
- Arm N2: Modular Structured Observation Extraction + GENE Epistemic Kernel
- Arm C0: Deterministic Oracle Extraction Ceiling
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from gene.supersession_engine import (
    BitemporalEngine,
    BitemporalFact,
    BitemporalRule,
    EventType,
    Observation,
    PredicateContract,
    TemporalEvent,
    adjudicate_observation,
)

STAGE6C_SYSTEM_PROMPT_N1 = """You are a formal epistemic state adjudicator.
You are given a natural language sentence describing an observed change, the current memory state facts, and the predicate ontology contract.
Your task is to determine the exact formal state transition event batch in structured JSON.

Allowed event types:
- ASSERT: introduce a new occurrence node.
- SUPERSEDES: replace a prior active occurrence node starting at t_valid_start.
- CONTRADICTS: record a contemporaneous disagreement between independent sources.
- RETRACT: remove an occurrence node from validity.

Return ONLY a valid JSON object matching this schema:
{
  "events": [
    {
      "event_type": "ASSERT|SUPERSEDES|CONTRADICTS|RETRACT",
      "target_fact_id": "occ_ID_in",
      "secondary_fact_id": "occ_ID_prior" or null,
      "t_valid_start": float,
      "t_valid_end": float or null
    }
  ]
}"""

STAGE6C_SYSTEM_PROMPT_N2 = """You are a factual observation extractor.
You are given a natural language sentence.
Your task is to extract strictly the factual proposition and valid-time interval in structured JSON.
Do NOT perform memory management, supersession reasoning, or state transitions. Extract only what is asserted in the text.

Return ONLY a valid JSON object matching this schema:
{
  "subject": "Exact entity name (e.g. Agent_Alice)",
  "predicate": "Exact predicate name (e.g. clearance)",
  "object": "Exact value/object name (e.g. Value_Gamma)",
  "t_valid_start": float (e.g. 10.0),
  "t_valid_end": float or null (e.g. null if continuous, float if bounded interval)
}"""


def build_user_prompt_n1(case: dict[str, Any]) -> str:
    init_facts_str = "\n".join([
        f"- ID: {f['fact_id']} | ({f['subject']}, {f['predicate']}, {f['object']}) | t_valid=[{f['t_valid_start']}, {f['t_valid_end'] or 'inf'}) | source={f['source_id']}"
        for f in case["initial_facts"]
    ])
    contract = case["predicate_contract"]
    contract_str = f"Predicate: {contract['predicate']}, Cardinality: {contract['cardinality']}, TemporalMode: {contract['temporal_mode']}, ConflictPolicy: {contract['conflict_policy']}"

    return f"""Current Memory Facts:
{init_facts_str}

Predicate Contract:
{contract_str}

Incoming Natural Language Observation (assigned new occurrence ID: occ_{case['case_id']}_in):
"{case['natural_language_text']}"

Determine the formal transition event batch for occ_{case['case_id']}_in in JSON."""


def build_user_prompt_n2(case: dict[str, Any]) -> str:
    contract = case["predicate_contract"]
    return f"""Natural Language Observation:
"{case['natural_language_text']}"

Target Predicate: {contract['predicate']} (Mode: {contract['temporal_mode']})

Extract the structured observation tuple in JSON."""


class Stage6CBridgeRunner:
    """Orchestrates Stage 6C execution, deterministic adjudication, and SQLite logging."""

    def __init__(
        self,
        db_path: Path,
        manifest_path: Path,
        client_fn: Callable[[str, str], str],
        model_name: str = "gemma3:12b",
        model_digest: str = "f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a",
        ollama_version: str = "unknown",
        git_commit: str = "unknown",
    ):
        self.db_path = db_path
        self.manifest_path = manifest_path
        self.client_fn = client_fn
        self.model_name = model_name
        self.model_digest = model_digest
        self.ollama_version = ollama_version
        self.git_commit = git_commit
        self.cases: list[dict[str, Any]] = []

        self._load_manifest()
        self._init_db()

    def _load_manifest(self) -> None:
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        cases_file = self.manifest_path.parent / manifest["dataset_file"]
        self.cases = [json.loads(line) for line in open(cases_file, "r", encoding="utf-8") if line.strip()]

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                model_name TEXT,
                model_digest TEXT,
                ollama_version TEXT,
                git_commit TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS stage6c_calls (
                call_id TEXT PRIMARY KEY,
                run_id TEXT,
                case_id TEXT,
                arm TEXT,
                phase TEXT,
                system_prompt TEXT,
                user_prompt TEXT,
                raw_response TEXT,
                parsed_json TEXT,
                latency_ms REAL,
                created_at TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(run_id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS stage6c_evaluations (
                eval_id TEXT PRIMARY KEY,
                call_id TEXT,
                case_id TEXT,
                arm TEXT,
                extraction_correct INTEGER,
                layer_a_transition_correct INTEGER,
                layer_b_state_correct INTEGER,
                layer_c_entitled_actual INTEGER,
                layer_c_entitled_expected INTEGER,
                layer_c_entitlement_correct INTEGER,
                support_fidelity_correct INTEGER,
                error_origin TEXT,
                created_at TEXT,
                FOREIGN KEY(call_id) REFERENCES stage6c_calls(call_id)
            )
        """)
        conn.commit()
        conn.close()

    def run_all(self, run_id: str | None = None) -> dict[str, Any]:
        run_id = run_id or f"run_6c_{int(time.time())}"
        created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, self.model_name, self.model_digest, self.ollama_version, self.git_commit, created_at)
        )
        conn.commit()

        call_idx = 0
        evaluations = []

        # ======================================================================
        # 1. ARM N1: Direct Neural Transition Emission (12 calls)
        # ======================================================================
        for case in self.cases:
            call_idx += 1
            call_id = f"call_{run_id}_n1_{case['case_id']}"
            sys_p = STAGE6C_SYSTEM_PROMPT_N1
            usr_p = build_user_prompt_n1(case)

            t0 = time.perf_counter()
            raw_resp = self.client_fn(sys_p, usr_p)
            lat = (time.perf_counter() - t0) * 1000.0

            try:
                parsed = json.loads(raw_resp)
            except Exception:
                parsed = {"events": []}

            c.execute(
                "INSERT INTO stage6c_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (call_id, run_id, case["case_id"], "arm_n1_direct_transition", "main", sys_p, usr_p, raw_resp, json.dumps(parsed), lat, created_at)
            )

            # Evaluate Arm N1
            eval_res = self._evaluate_arm_n1(case, parsed, call_id)
            evaluations.append(eval_res)
            c.execute(
                "INSERT INTO stage6c_evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (eval_res["eval_id"], call_id, case["case_id"], "arm_n1_direct_transition",
                 eval_res["extraction_correct"], eval_res["layer_a_transition_correct"],
                 eval_res["layer_b_state_correct"], eval_res["layer_c_entitled_actual"],
                 eval_res["layer_c_entitled_expected"], eval_res["layer_c_entitlement_correct"],
                 eval_res["support_fidelity_correct"], eval_res["error_origin"], created_at)
            )
            conn.commit()

        # ======================================================================
        # 2. ARM N2: Modular Observation Extraction (12 calls)
        # ======================================================================
        for case in self.cases:
            call_idx += 1
            call_id = f"call_{run_id}_n2_{case['case_id']}"
            sys_p = STAGE6C_SYSTEM_PROMPT_N2
            usr_p = build_user_prompt_n2(case)

            t0 = time.perf_counter()
            raw_resp = self.client_fn(sys_p, usr_p)
            lat = (time.perf_counter() - t0) * 1000.0

            try:
                parsed = json.loads(raw_resp)
            except Exception:
                parsed = {}

            c.execute(
                "INSERT INTO stage6c_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (call_id, run_id, case["case_id"], "arm_n2_modular_extraction", "main", sys_p, usr_p, raw_resp, json.dumps(parsed), lat, created_at)
            )

            eval_res = self._evaluate_arm_n2(case, parsed, call_id)
            evaluations.append(eval_res)
            c.execute(
                "INSERT INTO stage6c_evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (eval_res["eval_id"], call_id, case["case_id"], "arm_n2_modular_extraction",
                 eval_res["extraction_correct"], eval_res["layer_a_transition_correct"],
                 eval_res["layer_b_state_correct"], eval_res["layer_c_entitled_actual"],
                 eval_res["layer_c_entitled_expected"], eval_res["layer_c_entitlement_correct"],
                 eval_res["support_fidelity_correct"], eval_res["error_origin"], created_at)
            )
            conn.commit()

        # ======================================================================
        # 3. REPLAY CANARIES (4 calls for Arm N2)
        # ======================================================================
        canary_case_ids = ["C6C_01", "C6C_05", "C6C_09", "C6C_11"]
        canary_matches_raw = 0
        canary_matches_semantic = 0

        for cid in canary_case_ids:
            case = next(c for c in self.cases if c["case_id"] == cid)
            call_idx += 1
            call_id = f"call_{run_id}_canary_{cid}"
            sys_p = STAGE6C_SYSTEM_PROMPT_N2
            usr_p = build_user_prompt_n2(case)

            raw_resp = self.client_fn(sys_p, usr_p)
            try:
                parsed = json.loads(raw_resp)
            except Exception:
                parsed = {}

            c.execute(
                "INSERT INTO stage6c_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (call_id, run_id, cid, "arm_n2_canary", "canary", sys_p, usr_p, raw_resp, json.dumps(parsed), 0.0, created_at)
            )

            # Compare to initial run
            orig_call = c.execute(
                "SELECT raw_response, parsed_json FROM stage6c_calls WHERE run_id=? AND case_id=? AND arm='arm_n2_modular_extraction'",
                (run_id, cid)
            ).fetchone()
            if orig_call:
                if orig_call[0].strip() == raw_resp.strip():
                    canary_matches_raw += 1
                if json.loads(orig_call[1]) == parsed:
                    canary_matches_semantic += 1

        conn.commit()
        conn.close()

        # ======================================================================
        # 4. COMPUTE AGGREGATE SUMMARY
        # ======================================================================
        n1_evals = [e for e in evaluations if e["arm"] == "arm_n1_direct_transition"]
        n2_evals = [e for e in evaluations if e["arm"] == "arm_n2_modular_extraction"]

        summary = {
            "stage": "Exploration Round 6 Stage 6C",
            "run_id": run_id,
            "total_calls": call_idx,
            "canary_determinism": {
                "total_canaries": len(canary_case_ids),
                "raw_string_matches": canary_matches_raw,
                "raw_determinism_rate": canary_matches_raw / len(canary_case_ids),
                "semantic_json_matches": canary_matches_semantic,
                "semantic_determinism_rate": canary_matches_semantic / len(canary_case_ids),
            },
            "arm_n1_direct_transition": self._summarize_arm(n1_evals),
            "arm_n2_modular_extraction": self._summarize_arm(n2_evals),
        }
        return summary

    def _summarize_arm(self, evals: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(evals)
        if n == 0:
            return {}
        ext_acc = sum(1 for e in evals if e["extraction_correct"]) / n
        tr_acc = sum(1 for e in evals if e["layer_a_transition_correct"]) / n
        st_acc = sum(1 for e in evals if e["layer_b_state_correct"]) / n
        ent_acc = sum(1 for e in evals if e["layer_c_entitlement_correct"]) / n
        supp_acc = sum(1 for e in evals if e["support_fidelity_correct"]) / n

        # Attribution
        err_origins: dict[str, int] = {}
        for e in evals:
            if not e["layer_c_entitlement_correct"]:
                err_origins[e["error_origin"]] = err_origins.get(e["error_origin"], 0) + 1

        return {
            "total_cases": n,
            "layer_0_extraction_accuracy": round(ext_acc, 4),
            "layer_a_transition_fidelity": round(tr_acc, 4),
            "layer_b_premise_state_fidelity": round(st_acc, 4),
            "layer_c_support_fidelity": round(supp_acc, 4),
            "layer_c_entitlement_accuracy": round(ent_acc, 4),
            "error_origin_breakdown": err_origins,
        }

    def _evaluate_arm_n1(self, case: dict[str, Any], parsed: dict[str, Any], call_id: str) -> dict[str, Any]:
        # Arm N1 directly emits events
        raw_events = parsed.get("events", [])
        norm_actual = [
            (e.get("event_type"), e.get("target_fact_id"), e.get("secondary_fact_id"), round(float(e["t_valid_start"]), 4) if e.get("t_valid_start") is not None else None, round(float(e["t_valid_end"]), 4) if e.get("t_valid_end") is not None else None)
            for e in raw_events
        ]
        norm_expected = [
            (e["event_type"], e["target_fact_id"], e.get("secondary_fact_id"), round(float(e["t_valid_start"]), 4) if e.get("t_valid_start") is not None else None, round(float(e["t_valid_end"]), 4) if e.get("t_valid_end") is not None else None)
            for e in case["gold_transitions"]
        ]
        tr_correct = (norm_actual == norm_expected)

        # Build engine to evaluate resulting state
        engine = BitemporalEngine(cautious_conflicts=True)
        for i, f in enumerate(case["initial_facts"]):
            engine.register_fact(BitemporalFact(f["fact_id"], f["subject"], f["predicate"], f["object"], roots=frozenset(f["lineage_roots"]), source_id=f["source_id"]))
            engine.record_event(TemporalEvent(f"ev_{f['fact_id']}", EventType.ASSERT, t_knowledge=0, event_seq=i, t_valid_start=f["t_valid_start"], t_valid_end=f["t_valid_end"], target_fact_id=f["fact_id"]))
        for r in case["initial_rules"]:
            engine.register_rule(BitemporalRule(r["rule_id"], tuple(r["head"]), tuple(tuple(b) for b in r["body"])))

        # Register incoming fact node
        in_fid = f"occ_{case['case_id']}_in"
        engine.register_fact(BitemporalFact(in_fid, case["initial_facts"][0]["subject"], case["initial_facts"][0]["predicate"], case["gold_extraction"]["object"]))

        # Apply emitted events
        seq = 0
        for ev in raw_events:
            try:
                engine.record_event(TemporalEvent(
                    event_id=f"ev_n1_{case['case_id']}_{seq}",
                    event_type=EventType(ev["event_type"]),
                    t_knowledge=1,
                    event_seq=seq,
                    t_valid_start=float(ev["t_valid_start"]),
                    t_valid_end=float(ev["t_valid_end"]) if ev.get("t_valid_end") is not None else None,
                    target_fact_id=ev.get("target_fact_id", in_fid),
                    secondary_fact_id=ev.get("secondary_fact_id"),
                ))
                seq += 1
            except Exception:
                pass

        eval_tv = case["evaluation_coordinates"]["t_valid"]
        eval_tk = case["evaluation_coordinates"]["t_knowledge"]
        active_fids = {f.fact_id for f in engine.get_active_facts(eval_tv, eval_tk)}
        supp = engine.compute_temporal_support(tuple(case["query"]), eval_tv, eval_tk)

        # Expected oracle state
        orc_engine = self._build_oracle_engine(case)
        orc_active_fids = {f.fact_id for f in orc_engine.get_active_facts(eval_tv, eval_tk)}
        orc_supp = orc_engine.compute_temporal_support(tuple(case["query"]), eval_tv, eval_tk)

        st_correct = (active_fids == orc_active_fids)
        supp_correct = (supp == orc_supp)
        actual_ent = len(supp) > 0
        expected_ent = case["expected_entitlement"]
        ent_correct = (actual_ent == expected_ent)

        err_origin = "NONE"
        if not ent_correct:
            if not tr_correct:
                err_origin = "TRANSITION_EMISSION_ERROR"
            elif not st_correct:
                err_origin = "PREMISE_STATE_ERROR"
            else:
                err_origin = "SUPPORT_DERIVATION_ERROR"

        return {
            "eval_id": f"eval_{call_id}",
            "arm": "arm_n1_direct_transition",
            "case_id": case["case_id"],
            "extraction_correct": 0,  # N/A for N1
            "layer_a_transition_correct": 1 if tr_correct else 0,
            "layer_b_state_correct": 1 if st_correct else 0,
            "layer_c_entitled_actual": 1 if actual_ent else 0,
            "layer_c_entitled_expected": 1 if expected_ent else 0,
            "layer_c_entitlement_correct": 1 if ent_correct else 0,
            "support_fidelity_correct": 1 if supp_correct else 0,
            "error_origin": err_origin,
        }

    def _evaluate_arm_n2(self, case: dict[str, Any], parsed: dict[str, Any], call_id: str) -> dict[str, Any]:
        gold_ext = case["gold_extraction"]
        ext_match = (
            parsed.get("subject") == gold_ext["subject"] and
            parsed.get("predicate") == gold_ext["predicate"] and
            parsed.get("object") == gold_ext["object"] and
            parsed.get("t_valid_start") == gold_ext["t_valid_start"] and
            parsed.get("t_valid_end") == gold_ext["t_valid_end"]
        )

        # Harness creates structured Observation
        in_fid = f"occ_{case['case_id']}_in"
        obs = Observation(
            subject=parsed.get("subject", ""),
            predicate=parsed.get("predicate", ""),
            obj=parsed.get("object", ""),
            t_valid_start=float(parsed.get("t_valid_start", 0.0)) if parsed.get("t_valid_start") is not None else 0.0,
            t_valid_end=float(parsed["t_valid_end"]) if parsed.get("t_valid_end") is not None else None,
            t_knowledge=case["trusted_metadata"]["t_knowledge"],
            source_id=case["trusted_metadata"]["source_id"],
            origin_id=case["trusted_metadata"]["origin_id"],
            lineage_roots=frozenset(case["trusted_metadata"]["lineage_roots"]),
            observation_id=case["case_id"],
        )

        engine = BitemporalEngine(cautious_conflicts=True)
        for i, f in enumerate(case["initial_facts"]):
            engine.register_fact(BitemporalFact(f["fact_id"], f["subject"], f["predicate"], f["object"], roots=frozenset(f["lineage_roots"]), source_id=f["source_id"]))
            engine.record_event(TemporalEvent(f"ev_{f['fact_id']}", EventType.ASSERT, t_knowledge=0, event_seq=i, t_valid_start=f["t_valid_start"], t_valid_end=f["t_valid_end"], target_fact_id=f["fact_id"]))
        for r in case["initial_rules"]:
            engine.register_rule(BitemporalRule(r["rule_id"], tuple(r["head"]), tuple(tuple(b) for b in r["body"])))

        engine.register_fact(BitemporalFact(in_fid, obs.subject, obs.predicate, obs.obj, roots=obs.lineage_roots, source_id=obs.source_id, origin_id=obs.origin_id))

        contract = PredicateContract(
            predicate=case["predicate_contract"]["predicate"],
            cardinality=case["predicate_contract"]["cardinality"],
            temporal_mode=case["predicate_contract"]["temporal_mode"],
            conflict_policy=case["predicate_contract"]["conflict_policy"],
            default_duration=case["predicate_contract"].get("default_duration"),
        )

        # Adjudicate observation using generalized production adjudicator
        events = adjudicate_observation(obs, engine, contract, new_fact_id=in_fid)
        for ev in events:
            engine.record_event(ev)

        norm_actual = [
            (e.event_type.value, e.target_fact_id, e.secondary_fact_id, round(float(e.t_valid_start), 4), round(float(e.t_valid_end), 4) if e.t_valid_end is not None else None)
            for e in events
        ]
        norm_expected = [
            (e["event_type"], e["target_fact_id"], e.get("secondary_fact_id"), round(float(e["t_valid_start"]), 4) if e.get("t_valid_start") is not None else None, round(float(e["t_valid_end"]), 4) if e.get("t_valid_end") is not None else None)
            for e in case["gold_transitions"]
        ]
        tr_correct = (norm_actual == norm_expected)

        eval_tv = case["evaluation_coordinates"]["t_valid"]
        eval_tk = case["evaluation_coordinates"]["t_knowledge"]
        active_fids = {f.fact_id for f in engine.get_active_facts(eval_tv, eval_tk)}
        supp = engine.compute_temporal_support(tuple(case["query"]), eval_tv, eval_tk)

        orc_engine = self._build_oracle_engine(case)
        orc_active_fids = {f.fact_id for f in orc_engine.get_active_facts(eval_tv, eval_tk)}
        orc_supp = orc_engine.compute_temporal_support(tuple(case["query"]), eval_tv, eval_tk)

        st_correct = (active_fids == orc_active_fids)
        supp_correct = (supp == orc_supp)
        actual_ent = len(supp) > 0
        expected_ent = case["expected_entitlement"]
        ent_correct = (actual_ent == expected_ent)

        err_origin = "NONE"
        if not ent_correct:
            if not ext_match:
                err_origin = "OBSERVATION_EXTRACTION_ERROR"
            elif not tr_correct:
                err_origin = "ADJUDICATION_ERROR"
            elif not st_correct:
                err_origin = "PREMISE_STATE_ERROR"
            else:
                err_origin = "SUPPORT_DERIVATION_ERROR"

        return {
            "eval_id": f"eval_{call_id}",
            "arm": "arm_n2_modular_extraction",
            "case_id": case["case_id"],
            "extraction_correct": 1 if ext_match else 0,
            "layer_a_transition_correct": 1 if tr_correct else 0,
            "layer_b_state_correct": 1 if st_correct else 0,
            "layer_c_entitled_actual": 1 if actual_ent else 0,
            "layer_c_entitled_expected": 1 if expected_ent else 0,
            "layer_c_entitlement_correct": 1 if ent_correct else 0,
            "support_fidelity_correct": 1 if supp_correct else 0,
            "error_origin": err_origin,
        }

    def _build_oracle_engine(self, case: dict[str, Any]) -> BitemporalEngine:
        engine = BitemporalEngine(cautious_conflicts=True)
        for i, f in enumerate(case["initial_facts"]):
            engine.register_fact(BitemporalFact(f["fact_id"], f["subject"], f["predicate"], f["object"], roots=frozenset(f["lineage_roots"]), source_id=f["source_id"]))
            engine.record_event(TemporalEvent(f"ev_{f['fact_id']}", EventType.ASSERT, t_knowledge=0, event_seq=i, t_valid_start=f["t_valid_start"], t_valid_end=f["t_valid_end"], target_fact_id=f["fact_id"]))
        for r in case["initial_rules"]:
            engine.register_rule(BitemporalRule(r["rule_id"], tuple(r["head"]), tuple(tuple(b) for b in r["body"])))

        in_fid = f"occ_{case['case_id']}_in"
        engine.register_fact(BitemporalFact(in_fid, case["gold_extraction"]["subject"], case["gold_extraction"]["predicate"], case["gold_extraction"]["object"], roots=frozenset(case["trusted_metadata"]["lineage_roots"]), source_id=case["trusted_metadata"]["source_id"]))

        seq = 0
        for tr in case["gold_transitions"]:
            engine.record_event(TemporalEvent(
                event_id=f"ev_orc_{case['case_id']}_{seq}",
                event_type=EventType(tr["event_type"]),
                t_knowledge=case["trusted_metadata"]["t_knowledge"],
                event_seq=seq,
                t_valid_start=float(tr["t_valid_start"]),
                t_valid_end=float(tr["t_valid_end"]) if tr.get("t_valid_end") is not None else None,
                target_fact_id=tr["target_fact_id"],
                secondary_fact_id=tr.get("secondary_fact_id"),
            ))
            seq += 1
        return engine
