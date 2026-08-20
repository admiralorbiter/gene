from __future__ import annotations

import json
from pathlib import Path
import sys
import pytest

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from scripts.generate_results_manifest import generate_manifest


def test_manifest_generation_and_schema():
    """Verify that manifest generation produces valid data matching the schema."""
    manifest = generate_manifest()
    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["project"] == "GENE (Genealogical Epistemic Network Experiments)"

    experiments = manifest["canonical_experiments"]
    assert "exp0" in experiments
    assert "exp1a" in experiments
    assert "exp1b_a" in experiments
    assert "exp1b_b1c" in experiments
    assert "exp1b_c1b" in experiments
    assert "exp1b_c2a" in experiments
    assert "exp1b_c2b" in experiments

    # Check key numerical invariants
    assert experiments["exp0"]["causal_necessity_calibrated"] == 1.0
    assert experiments["exp1a"]["transmission_fidelity_tau"] == 1.0
    assert experiments["exp1b_b1c"]["p_active_given_complete_path"] == 1.0
    assert experiments["exp1b_b1c"]["p_active_given_broken_path"] == 0.0
    assert experiments["exp1b_c1b"]["operating_point_tpr90_fpr10"]["lineage_quarantine"]["selectivity_S"] == 0.8
    assert experiments["exp1b_c2b"]["mu_expression_overall"] == 0.3
    assert experiments["exp1b_c2b"]["mu_heritable_overall"] == 0.0


def test_claim_ledger_integrity():
    """Verify that all claims in claim_ledger.json are complete, valid, and resolve to existing reports."""
    root_dir = Path(__file__).resolve().parent.parent
    ledger_path = root_dir / "data" / "claim_ledger.json"
    assert ledger_path.exists(), "data/claim_ledger.json must exist"

    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    assert ledger["ledger_version"] == "1.0.0"
    claims = ledger["claims"]
    assert len(claims) >= 8

    required_fields = [
        "claim_id",
        "headline",
        "claim_text",
        "evidence_class",
        "model_tested",
        "configurations_and_worlds",
        "sample_size",
        "primary_metric",
        "frozen_db",
        "execution_commit",
        "formal_report",
        "scope_limitations",
        "mgs_thematic_quote",
    ]

    for claim in claims:
        for field in required_fields:
            assert field in claim, f"Claim {claim.get('claim_id')} missing field {field}"
            assert claim[field], f"Claim {claim.get('claim_id')} has empty field {field}"

        # Verify formal report file exists
        report_path = root_dir / claim["formal_report"]
        assert report_path.exists(), f"Report {claim['formal_report']} for claim {claim['claim_id']} does not exist"

        # Verify frozen database exists
        db_path = root_dir / claim["frozen_db"]
        assert db_path.exists(), f"Database {claim['frozen_db']} for claim {claim['claim_id']} does not exist"

        # Verify MGS quote structure
        quote_obj = claim["mgs_thematic_quote"]
        assert "speaker" in quote_obj and "quote" in quote_obj
