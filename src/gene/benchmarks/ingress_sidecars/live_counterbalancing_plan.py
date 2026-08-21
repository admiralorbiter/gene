"""Live Assay Candidate Option Counterbalancing Plan (Thread D)."""

import itertools
from typing import Any


def generate_candidate_permutations_plan() -> list[dict[str, Any]]:
    """Generate deterministic 4-slot candidate option schedules for the 16 live assay hard cases.
    
    Ensures the gold candidate appears equally in ordinal positions 0, 1, 2, 3 across cases
    to prevent candidate-position bias (Agnus-style counterbalancing).
    """
    cases_schedule = []
    # 16 cases: 4 modes x 4 phenomena
    # 4 ordinal slots: 0, 1, 2, 3 (each slot tested exactly 4 times)
    slots = [0, 1, 2, 3] * 4

    for case_idx, gold_pos in enumerate(slots):
        cases_schedule.append({
            "case_id": f"C7_LIVE_{case_idx:02d}",
            "gold_slot_position": gold_pos,
            "distractor_slots": [i for i in range(4) if i != gold_pos],
        })

    return cases_schedule
