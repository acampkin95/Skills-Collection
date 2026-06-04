#!/usr/bin/env python3
"""Validate Firecrawl router skills and their local references."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ROUTERS: dict[Path, set[str]] = {
    ROOT / "firecrawl" / "SKILL.md": {
        "firecrawl-search",
        "firecrawl-scrape",
        "firecrawl-map",
        "firecrawl-crawl",
        "firecrawl-interact",
        "firecrawl-download",
        "firecrawl-parse",
        "firecrawl-agent",
        "firecrawl-cli-installation",
        "firecrawl-security",
        "firecrawl-build",
    },
    ROOT / "firecrawl-build" / "SKILL.md": {
        "firecrawl-build-onboarding",
        "firecrawl-build-search",
        "firecrawl-build-scrape",
        "firecrawl-build-interact",
    },
}

EXPECTED_LINKS: dict[Path, list[str]] = {
    ROOT / "firecrawl" / "SKILL.md": ["../firecrawl-build/SKILL.md"],
    ROOT / "firecrawl-build" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-agent" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-cli-installation" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-crawl" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-download" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-interact" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-map" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-parse" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-scrape" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-search" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-security" / "SKILL.md": ["../firecrawl/SKILL.md"],
    ROOT / "firecrawl-build-onboarding" / "SKILL.md": ["../firecrawl-build/SKILL.md"],
    ROOT / "firecrawl-build-search" / "SKILL.md": ["../firecrawl-build/SKILL.md"],
    ROOT / "firecrawl-build-scrape" / "SKILL.md": ["../firecrawl-build/SKILL.md"],
    ROOT / "firecrawl-build-interact" / "SKILL.md": ["../firecrawl-build/SKILL.md"],
}

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TABLE_TARGET_RE = re.compile(r"^\|[^\n]*\|\s*`([^`]+)`\s*\|", re.M)
NAME_RE = re.compile(r"^name:\s*(\S+)$", re.M)


def resolve_link(source: Path, target: str) -> Path | None:
    if target.startswith(("http://", "https://", "mailto:")):
        return None
    if target.startswith("#"):
        return None
    if re.fullmatch(r"[A-Za-z0-9_-]+", target):
        return None
    cleaned = target.split("#", 1)[0].split("?", 1)[0]
    return (source.parent / cleaned).resolve()


def validate_file(path: Path, expected_name: str | None = None) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing file: {path.relative_to(ROOT)}"]

    text = path.read_text()
    if expected_name is not None:
        match = NAME_RE.search(text)
        if not match:
            errors.append(f"missing name frontmatter in {path.relative_to(ROOT)}")
        elif match.group(1) != expected_name:
            errors.append(
                f"name mismatch in {path.relative_to(ROOT)}: {match.group(1)} != {expected_name}"
            )

    for target in LINK_RE.findall(text):
        resolved = resolve_link(path, target)
        if resolved is not None and not resolved.exists():
            errors.append(
                f"broken link in {path.relative_to(ROOT)}: {target} -> {resolved.relative_to(ROOT) if resolved.is_relative_to(ROOT) else resolved}"
            )

    for expected in EXPECTED_LINKS.get(path, []):
        if expected not in text:
            errors.append(f"missing backlink in {path.relative_to(ROOT)}: {expected}")

    return errors


def validate_router(path: Path, expected_targets: set[str]) -> list[str]:
    errors: list[str] = validate_file(path, path.parent.name)
    if not path.exists():
        return errors

    text = path.read_text()
    found = set(TABLE_TARGET_RE.findall(text))
    missing = expected_targets - found
    extra = found - expected_targets
    if missing:
        errors.append(f"missing router targets in {path.relative_to(ROOT)}: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected router targets in {path.relative_to(ROOT)}: {sorted(extra)}")

    for target in expected_targets:
        target_path = ROOT / target / "SKILL.md"
        if not target_path.exists():
            errors.append(f"missing routed skill: {target_path.relative_to(ROOT)}")

    return errors


def main() -> int:
    errors: list[str] = []
    for path, expected in ROUTERS.items():
        errors.extend(validate_router(path, expected))

    # Validate the leaf files we expect to be routed from the master skills.
    leafs = [
        ROOT / "firecrawl-cli-installation" / "SKILL.md",
        ROOT / "firecrawl-search" / "SKILL.md",
        ROOT / "firecrawl-scrape" / "SKILL.md",
        ROOT / "firecrawl-map" / "SKILL.md",
        ROOT / "firecrawl-crawl" / "SKILL.md",
        ROOT / "firecrawl-download" / "SKILL.md",
        ROOT / "firecrawl-interact" / "SKILL.md",
        ROOT / "firecrawl-agent" / "SKILL.md",
        ROOT / "firecrawl-parse" / "SKILL.md",
        ROOT / "firecrawl-security" / "SKILL.md",
        ROOT / "firecrawl-build-onboarding" / "SKILL.md",
        ROOT / "firecrawl-build-search" / "SKILL.md",
        ROOT / "firecrawl-build-scrape" / "SKILL.md",
        ROOT / "firecrawl-build-interact" / "SKILL.md",
    ]
    for path in leafs:
        errors.extend(validate_file(path, path.parent.name))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Firecrawl router validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
