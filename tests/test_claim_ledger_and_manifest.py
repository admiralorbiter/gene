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
    manifest = generate_manifest(write=False)
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

    assert ledger["ledger_version"] == "3.0.0"
    claims = ledger["claims"]
    assert len(claims) >= 15
    claim_ids = [c["claim_id"] for c in claims]
    assert len(claim_ids) == len(set(claim_ids)), "Claim IDs must be strictly unique"

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
            commit_ref = src["execution_commit"]
            if commit_ref and not commit_ref.startswith("deterministic"):
                # Resolve tag, branch, or SHA to 40-char commit SHA
                res = subprocess.run(
                    ["git", "rev-parse", f"{commit_ref}^{{commit}}"],
                    cwd=root_dir,
                    capture_output=True,
                    text=True,
                )
                assert res.returncode == 0, f"Commit reference '{commit_ref}' in {claim['claim_id']} does not resolve in Git!"
                resolved_sha = res.stdout.strip()

                # If results_commit is provided, resolve and verify results tree binding
                binding_ref = src.get("results_commit", commit_ref)
                if binding_ref and not binding_ref.startswith("deterministic"):
                    res_b = subprocess.run(
                        ["git", "rev-parse", f"{binding_ref}^{{commit}}"],
                        cwd=root_dir,
                        capture_output=True,
                        text=True,
                    )
                    assert res_b.returncode == 0, f"Results commit reference '{binding_ref}' in {claim['claim_id']} does not resolve in Git!"
                    resolved_b_sha = res_b.stdout.strip()
                    art_git_path = src["artifact"].replace("\\", "/")
                    res_show = subprocess.run(
                        ["git", "show", f"{resolved_b_sha}:{art_git_path}"],
                        cwd=root_dir,
                        capture_output=True,
                    )
                    is_git_tracked = src.get("git_tracked", True)
                    if is_git_tracked:
                        assert res_show.returncode == 0, (
                            f"git show {resolved_b_sha}:{art_git_path} failed for {claim['claim_id']}: {res_show.stderr}"
                        )
                    if res_show.returncode == 0:
                        blob_raw = res_show.stdout
                        blob_lf = blob_raw.replace(b"\r\n", b"\n")
                        blob_crlf = blob_lf.replace(b"\n", b"\r\n")
                        expected_sha = src["artifact_sha256"].lower()
                        
                        raw_sha = hashlib.sha256(blob_raw).hexdigest()
                        lf_sha = hashlib.sha256(blob_lf).hexdigest()
                        crlf_sha = hashlib.sha256(blob_crlf).hexdigest()
                        
                        matched = expected_sha in [raw_sha, lf_sha, crlf_sha]
                        assert matched, (
                            f"Git commit binding mismatch for {claim['claim_id']} ({src['artifact']} at {binding_ref} / {resolved_b_sha}): "
                            f"expected {expected_sha}, git show produced (raw={raw_sha}, lf={lf_sha}, crlf={crlf_sha})"
                        )

            # Check disk checksum if artifact is a tracked data file on disk
            art_disk_path = root_dir / src["artifact"]
            if art_disk_path.exists() and src["artifact"].startswith("data/"):
                actual_disk_sha = compute_sha256(art_disk_path)
                assert actual_disk_sha.lower() == src["artifact_sha256"].lower(), (
                    f"Disk checksum mismatch for {claim['claim_id']} ({src['artifact']}): "
                    f"expected {src['artifact_sha256']}, got {actual_disk_sha}"
                )
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
        
    assert ledger_data["claims"] == atlas_data["claims"], "docs/atlas/data/claims.json does not deeply match data/claim_ledger.json"


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
