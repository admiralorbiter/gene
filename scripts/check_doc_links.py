"""Script to check and sanitize documentation and web asset links.

Ensures that:
1. Zero machine-specific absolute file:/// URLs exist in public markdown, HTML, or SVG files.
2. Relative links and asset references point to files that actually exist.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys


def find_link_issues(root_dir: Path) -> list[str]:
    """Scan markdown, html, and svg files for bad links or broken relative references."""
    issues = []
    md_link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    html_src_href_pattern = re.compile(r'(?:src|href)=["\']([^"\']+)["\']')

    doc_files = (
        list(root_dir.glob("*.md"))
        + list((root_dir / "docs").rglob("*.md"))
        + list((root_dir / "docs").rglob("*.html"))
        + list((root_dir / "docs").rglob("*.svg"))
    )

    for doc_file in doc_files:
        try:
            content = doc_file.read_text(encoding="utf-8")
        except Exception as e:
            issues.append(f"Failed to read {doc_file}: {e}")
            continue

        # Check markdown links
        if doc_file.suffix == ".md":
            for match in md_link_pattern.finditer(content):
                url = match.group(2).strip()

                if url.startswith("file:///"):
                    issues.append(f"{doc_file.relative_to(root_dir)}: Absolute local link found -> {url}")
                    continue

                if url.startswith("http://") or url.startswith("https://") or url.startswith("#") or url.startswith("mailto:"):
                    continue

                clean_url = url.split("#")[0].split("?")[0]
                if not clean_url:
                    continue

                target_path = (doc_file.parent / clean_url).resolve()
                if not target_path.exists():
                    issues.append(f"{doc_file.relative_to(root_dir)}: Broken relative link -> {url}")

        # Check HTML / SVG asset references
        if doc_file.suffix in (".html", ".svg"):
            for match in html_src_href_pattern.finditer(content):
                url = match.group(1).strip()

                if url.startswith("file:///"):
                    issues.append(f"{doc_file.relative_to(root_dir)}: Absolute local link in HTML/SVG -> {url}")
                    continue

                if url.startswith("http://") or url.startswith("https://") or url.startswith("#") or url.startswith("data:") or url.startswith("javascript:"):
                    continue

                clean_url = url.split("#")[0].split("?")[0]
                if not clean_url:
                    continue

                target_path = (doc_file.parent / clean_url).resolve()
                if not target_path.exists():
                    issues.append(f"{doc_file.relative_to(root_dir)}: Broken HTML/SVG reference -> {url}")

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
        print("All documentation, HTML, and SVG links and asset references are authentic and relative!")
