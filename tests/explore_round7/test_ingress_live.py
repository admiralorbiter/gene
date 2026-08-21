"""Unit tests for Stage 7B Live Ingress benchmark geometry and parsing (Mock Mode)."""

from gene.benchmarks.ingress_live.generator import generate_52_live_cases
from gene.benchmarks.ingress_live.models import LiveNeuralExtraction
from gene.benchmarks.ingress_live.prompts import format_live_ingress_prompt
from gene.benchmarks.ingress_live.runner import parse_model_json_response


def test_52_live_cases_geometry():
    cases = generate_52_live_cases()
    assert len(cases) == 52

    primary = [c for c in cases if c.case_type == "PRIMARY_FACTORIAL"]
    cb = [c for c in cases if c.case_type == "COUNTERBALANCED_ORDER"]
    canaries = [c for c in cases if c.case_type == "CANARY_REPLAY"]

    assert len(primary) == 32
    assert len(cb) == 16
    assert len(canaries) == 4

    # Verify counterbalanced slot distribution
    slot_counts = {}
    for c in cb:
        slot_counts[c.gold_slot_position] = slot_counts.get(c.gold_slot_position, 0) + 1
    assert slot_counts == {0: 4, 1: 4, 2: 4, 3: 4}


def test_json_parsing_and_extraction():
    raw_response = """```json
    {
        "subject_span": "Server 1",
        "predicate_span": "device_status",
        "object_span": "Operational",
        "t_valid_start": 5.0,
        "t_valid_end": null,
        "selected_subject_candidate": "Server_Node_1",
        "selected_object_candidate": "Value_Operational",
        "is_subject_novel": false,
        "is_object_novel": false,
        "extracted_claim_type": "FACTUAL_OBSERVATION",
        "reasoning": "Extracted exact telemetry."
    }
    ```"""
    ext = parse_model_json_response(raw_response)
    assert ext.subject_span == "Server 1"
    assert ext.predicate_span == "device_status"
    assert ext.object_span == "Operational"
    assert ext.t_valid_start == 5.0
    assert ext.t_valid_end is None
    assert ext.selected_subject_candidate == "Server_Node_1"
    assert ext.selected_object_candidate == "Value_Operational"
    assert ext.is_subject_novel is False
    assert ext.extracted_claim_type == "FACTUAL_OBSERVATION"
