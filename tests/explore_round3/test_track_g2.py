"""Preflight tests for Track G2: Clean Non-Destructive Support Immunity."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest


def build_track_g2_prompt(station: str, arm: str, geometry: str) -> tuple[str, list[str], str]:
    """Clean G2 prompt with ZERO auxiliary count leaks and explicit unrevoked baseline."""
    rules = (
        "RULES:\n"
        f"1. manager({station}, person) AND reports_to(person, S1) AND authorized(S1) -> uses_protocol({station}, PROTO_X7)\n"
        f"2. sector_lead({station}, person) AND reports_to(person, S2) AND authorized(S2) -> uses_protocol({station}, PROTO_X7)\n"
        "3. If an authority is REVOKED or UNAUTHORIZED, all deductions passing through that authority are invalid.\n"
        "4. If all supporting paths are revoked, protocol is UNKNOWN."
    )

    if arm == "unrevoked_baseline":
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            "- MEM_03: STATUS: Authority of S1 is VALID and ACTIVE.",
            f"- MEM_04: Vael is sector lead of {station}.",
            "- MEM_05: Vael directly reports to S2.",
            "- MEM_06: STATUS: Authority of S2 is VALID and ACTIVE.",
        ]
        expected = "PROTO_X7"
    elif arm == "revoke_path1":
        # S1 revoked; S2 valid -> Survives if independent!
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            "- MEM_03: STATUS: Authority of S1 is REVOKED and INVALID.",
            f"- MEM_04: Vael is sector lead of {station}.",
            "- MEM_05: Vael directly reports to S2.",
            "- MEM_06: STATUS: Authority of S2 is VALID and ACTIVE.",
        ]
        expected = "PROTO_X7" if geometry == "independent" else "UNKNOWN"
    elif arm == "revoke_shared":
        # S1 revoked; second path also passes through S1
        memories = [
            f"- MEM_01: Nerin is manager of {station}.",
            "- MEM_02: Nerin directly reports to S1.",
            "- MEM_03: STATUS: Authority of S1 is REVOKED and INVALID.",
            f"- MEM_04: Vael is sector lead of {station}.",
            "- MEM_05: Vael directly reports to S1.",
            "- MEM_06: STATUS: Authority of S1 is REVOKED and INVALID.",
        ]
        expected = "UNKNOWN"
    else:
        raise ValueError(f"Unknown arm: {arm}")

    prompt = (
        f"{rules}\n\n"
        "RETRIEVED EVIDENCE:\n"
        + "\n".join(memories)
        + f"\n\nQUESTION: What security protocol is currently authorized for station {station}?\n"
        "Return strictly JSON matching this schema:\n"
        '{"station": "STATION_NAME", "protocol": "PROTOCOL_NAME_OR_UNKNOWN", "evidence_status": "sufficient|insufficient"}'
    )

    forbidden = ["PROTO_X7", "PROTO_Q2"]
    return prompt, forbidden, expected


def test_track_g2_zero_auxiliary_count_leak():
    """Verify that Track G2 prompt schema contains no auxiliary numeric counts or answer leaks."""
    prompt, forbidden, expected = build_track_g2_prompt("VELORA", "revoke_path1", "independent")
    schema_section = prompt[prompt.find("schema"):]
    assert "surviving_paths_count" not in schema_section
    assert "0" not in schema_section
    assert "1" not in schema_section


def test_track_g2_positive_baseline_control():
    """Verify that unrevoked baseline arm produces PROTO_X7 expectation and unrevoked evidence."""
    prompt, _, expected = build_track_g2_prompt("VELORA", "unrevoked_baseline", "independent")
    assert expected == "PROTO_X7"
    assert "REVOKED and INVALID" not in prompt
    assert "VALID and ACTIVE" in prompt
