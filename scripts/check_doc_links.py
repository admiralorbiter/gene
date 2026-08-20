"""Script to check and sanitize documentation links.

Ensures that:
1. Zero machine-specific absolute file:/// URLs exist in public markdown files.
2. Relative markdown links point to files that actually exist.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys


def find_link_issues(root_dir: Path) -> list[str]:
    """Scan markdown files for bad links or broken relative references."""
    issues = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    md_files = list(root_dir.glob("*.md")) + list((root_dir / "docs").rglob("*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            issues.append(f"Failed to read {md_file}: {e}")
            continue

        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            url = match.group(2).strip()

            # Reject local file:/// URIs
            if url.startswith("file:///"):
                issues.append(f"{md_file.relative_to(root_dir)}: Absolute local link found -> {url}")
                continue

            # Skip web URLs or anchors
            if url.startswith("http://") or url.startswith("https://") or url.startswith("#"):
                continue

            # Strip query / fragment
            clean_url = url.split("#")[0].split("?")[0]
            if not clean_url:
                continue

            # Resolve relative link relative to md_file.parent
            target_path = (md_file.parent / clean_url).resolve()
            if not target_path.exists():
                issues.append(f"{md_file.relative_to(root_dir)}: Broken relative link -> {url} (resolved to {target_path})")

    return issues


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    issues = find_link_issues(root)
    if issues:
        print(f"Found {len(issues)} link issues:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("All documentation links are clean and relative!")
