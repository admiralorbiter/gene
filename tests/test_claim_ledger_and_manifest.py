"""Tests for canonical results manifest and claim ledger integrity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pytest

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from scripts.generate_results_manifest import generate_manifest


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 hex digest of a local file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_manifest_generation_and_schema():
    """Verify that manifest generation produces valid data matching the schema."""
    manifest = generate_manifest()
    assert manifest["manifest_version"] == "2.0.0"
    assert manifest["project"] == "GENE (Genealogical Epistemic Network Experiments)"
    assert "T" in manifest["generated_at"]  # Dynamic ISO timestamp

    experiments = manifest["canonical_experiments"]
    assert "exp0" in experiments
    assert "exp1a" in experiments
    assert "exp1b_a" in experiments
    assert "exp1b_b1c" in experiments
    assert "exp1b_c1b" in experiments
    assert "exp1b_c2a" in experiments
    assert "exp1b_c2b" in experiments

    # Check key numerical invariants
    sub_exp0 = experiments["exp0"]["sub_experiments"]
    assert sub_exp0["exp0_a_observability_audit"]["causal_necessity_calibrated"] == 1.0
    assert sub_exp0["exp0_b_factorial_calibration"]["cell_4_causal_tests"] == 66

    assert experiments["exp1a"]["transmission_fidelity_tau"] == 1.0

    # Galton-Watson closed form math
    ext_probs = experiments["exp1b_a"]["analytical_extinction_probabilities"]
    assert ext_probs["critical_boundary_p0.50"] == 1.0
    assert ext_probs["supercritical_p0.60"] == 0.44444
    assert ext_probs["supercritical_p0.75"] == 0.11111

    assert experiments["exp1b_b1c"]["p_active_given_complete_path"] == 1.0
    assert experiments["exp1b_b1c"]["p_active_given_broken_path"] == 0.0

    # C1b at canonical top_k = 6
    c1b_k6 = experiments["exp1b_c1b"]["canonical_operating_point_k6_tpr90_fpr10"]
    assert c1b_k6["lineage_quarantine"]["selectivity_S"] == 0.8
    assert c1b_k6["signal_blind_uniform_thinning"]["selectivity_S"] == -0.0

    assert experiments["exp1b_c2b"]["mu_expression_overall"] == 0.3
    assert experiments["exp1b_c2b"]["mu_heritable_overall"] == 0.0


def test_claim_ledger_multi_source_integrity():
    """Verify that all claims in claim_ledger.json are complete, valid, and resolve to existing reports."""
    ledger_path = root_dir / "data" / "claim_ledger.json"
    assert ledger_path.exists(), "data/claim_ledger.json must exist"

    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    assert ledger["ledger_version"] == "2.0.0"
    claims = ledger["claims"]
    assert len(claims) >= 8

    required_claim_fields = [
        "claim_id",
        "claim_status",
        "headline",
        "claim_text",
        "evidence_sources",
        "scope_limitations",
        "replication_status",
    ]

    required_source_fields = [
        "experiment",
        "evidence_class",
        "artifact",
        "artifact_sha256",
        "execution_commit",
        "model",
        "n_calls",
        "n_evaluations",
        "unit_of_analysis",
        "formal_report",
        "primary_metric",
    ]

    for claim in claims:
        for field in required_claim_fields:
            assert field in claim, f"Claim {claim.get('claim_id')} missing field {field}"

        sources = claim["evidence_sources"]
        assert len(sources) >= 1, f"Claim {claim['claim_id']} must have at least one evidence source"

        for src in sources:
            for field in required_source_fields:
                assert field in src, f"Source in claim {claim['claim_id']} missing {field}"

            # Verify formal report file exists
            report_path = root_dir / src["formal_report"]
            assert report_path.exists(), f"Report {src['formal_report']} for claim {claim['claim_id']} does not exist"

            # Verify execution_commit resolves in git
            commit_hash = src["execution_commit"]
            if commit_hash and len(commit_hash) == 40 and not commit_hash.startswith("deterministic"):
                res = subprocess.run(
                    ["git", "cat-file", "-e", f"{commit_hash}^{{commit}}"],
                    cwd=root_dir,
                    capture_output=True,
                )
                assert res.returncode == 0, f"Commit {commit_hash} in {claim['claim_id']} does not resolve in Git!"

            # If artifact is a .db file, verify it exists and checksum matches
            if src["artifact"].endswith(".db"):
                db_path = root_dir / src["artifact"]
                assert db_path.exists(), f"Database {src['artifact']} for claim {claim['claim_id']} does not exist"
                actual_sha = compute_sha256(db_path)
                assert actual_sha.lower() == src["artifact_sha256"].lower(), (
                    f"SHA256 mismatch for {src['artifact']} in {claim['claim_id']}: expected {src['artifact_sha256']}, got {actual_sha}"
                )
            elif src["artifact"].endswith(".jsonl") or src["artifact"].endswith(".json"):
                art_path = root_dir / src["artifact"]
                if art_path.exists():
                    actual_sha = compute_sha256(art_path)
                    assert actual_sha.lower() == src["artifact_sha256"].lower(), (
                        f"SHA256 mismatch for {src['artifact']} in {claim['claim_id']}: expected {src['artifact_sha256']}, got {actual_sha}"
                    )


def test_atlas_claims_sync() -> None:
    """Verify that docs/atlas/data/claims.json exactly mirrors data/claim_ledger.json."""
    ledger_path = root_dir / "data" / "claim_ledger.json"
    atlas_path = root_dir / "docs" / "atlas" / "data" / "claims.json"
    assert ledger_path.exists() and atlas_path.exists()
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger_data = json.load(f)
    with open(atlas_path, "r", encoding="utf-8") as f:
        atlas_data = json.load(f)
        
    assert len(ledger_data["claims"]) == len(atlas_data["claims"])
    for l_claim, a_claim in zip(ledger_data["claims"], atlas_data["claims"]):
        assert l_claim["claim_id"] == a_claim["claim_id"]
        assert l_claim["headline"] == a_claim["headline"]


def test_epigraphs_file_integrity():
    """Verify that docs/design/epigraphs.json is well-structured."""
    epigraphs_path = root_dir / "docs" / "design" / "epigraphs.json"
    assert epigraphs_path.exists(), "docs/design/epigraphs.json must exist"

    with open(epigraphs_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "epigraphs" in data
    assert len(data["epigraphs"]) >= 8
    for ep in data["epigraphs"]:
        assert "speaker" in ep
        assert "source" in ep
        assert "text" in ep
        assert "theme" in ep
