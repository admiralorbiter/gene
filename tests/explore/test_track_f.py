"""Unit tests for Track F: Reported-Lineage Identifier Equivariance."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from scripts.explore.run_track_f_id_equivariance import (
    MAPPINGS,
    build_track_f_prompt,
    unmap_cited_ids,
)


def test_id_mappings_bijective_invertibility():
    """Verify that all mappings are strictly bijective and distinct."""
    for m_key, mapping in MAPPINGS.items():
        assert len(mapping) == 3
        # Unique values
        values = list(mapping.values())
        assert len(set(values)) == 3

        # Invertible
        inv = {v: k for k, v in mapping.items()}
        for k, v in mapping.items():
            assert inv[v] == k


def test_unmapping_logic():
    """Verify unmapping of exact and distractor IDs."""
    mapping = MAPPINGS["semantic_natural"]
    inv = {v: k for k, v in mapping.items()}

    # Exact citation
    exact = unmap_cited_ids(["KAVO_ARCHIVE", "RILEN_LOG"], inv)
    assert exact == {"parent_mgr", "parent_sup"}

    # Distractor citation
    with_dist = unmap_cited_ids(["KAVO_ARCHIVE", "TEPA_DOC"], inv)
    assert with_dist == {"parent_mgr", "distractor"}

    # Unknown ID
    unknown = unmap_cited_ids(["FOO_BAR"], inv)
    assert unknown == {"UNKNOWN_ID:FOO_BAR"}
