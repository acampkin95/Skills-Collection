#!/usr/bin/env python3
"""
Validate every skill in the repository against schema/skill.schema.json.

This is the repo-wide CI gate: it walks skills_master, skills_staging, and
skills_devtesting (the authored/generated tiers — see README's "Source of
Truth" section) and checks each SKILL.md for schema-valid frontmatter,
directory/name consistency, cross-skill name collisions within a tier, and
a best-effort scan for obviously-committed secrets.

skills_conversions/ is excluded: those .skill files are packaged output of
SkillsFramework/package-skills.sh, not authored source, and are validated
by regenerating them rather than by this script.

Usage:
    python SkillsFramework/scripts/validate_skills.py
    python SkillsFramework/scripts/validate_skills.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "skill.schema.json"

TIERS = ["skills_master", "skills_staging", "skills_devtesting"]

# Directories that live alongside skills but are not themselves skills
# (internal notes, audit output, etc). Keep this list short and explicit
# rather than guessing — anything added here should be a deliberate call,
# not a way to silence a real missing-SKILL.md bug.
NON_SKILL_DIRS = {
    ("skills_staging", "learned"),
    ("skills_staging", "reports"),
}

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
STATUS_VALUES = {"experimental", "staging", "stable", "deprecated"}
RISK_VALUES = {"low", "medium", "high"}
FS_VALUES = {"none", "read", "write"}
SHELL_NET_VALUES = {"none", "restricted", "full"}

# Best-effort secret patterns. Not a substitute for gitleaks/trufflehog in
# CI — this catches the obvious, common shapes so a contributor gets fast
# local feedback before a real scanner runs.
SECRET_PATTERNS = [
    # Real PEM blocks have base64 body lines after the header; a bare
    # header string (e.g. inside a secrets-scanner's own pattern list)
    # does not, so require body content to follow within a short window.
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----\s*\n\s*[A-Za-z0-9+/]{30,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("OpenAI-style key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
]

# Obvious placeholders (repeated filler chars) that would otherwise match
# the patterns above, e.g. `sk-xxxxxxxxxxxxxxxxxxxx` in setup docs. A real
# key has high character diversity in its body; a placeholder doesn't.
def looks_like_placeholder(matched_text, min_tail=10, max_unique=2):
    tail = matched_text[-min_tail:]
    return len(set(tail)) <= max_unique


class Finding:
    def __init__(self, level, path, message):
        self.level = level  # "error" or "warning"
        self.path = path
        self.message = message

    def __str__(self):
        return f"[{self.level.upper()}] {self.path}: {self.message}"


def load_schema_field_names():
    """Read schema/skill.schema.json to know which frontmatter keys are declared."""
    import json

    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    return set(schema.get("properties", {}).keys()), schema.get("additionalProperties", True)


def validate_frontmatter(fm, skill_dir_name, known_fields, findings, path):
    name = fm.get("name")
    desc = fm.get("description")

    if not name:
        findings.append(Finding("error", path, "missing required field: name"))
    else:
        if not isinstance(name, str) or not NAME_PATTERN.match(name):
            findings.append(Finding("error", path, f"name '{name}' is not kebab-case"))
        if name != skill_dir_name:
            findings.append(
                Finding("error", path, f"name '{name}' does not match directory '{skill_dir_name}'")
            )

    if not desc:
        findings.append(Finding("error", path, "missing required field: description"))
    elif not isinstance(desc, str) or len(desc) > 1024:
        findings.append(Finding("error", path, f"description exceeds 1024 chars ({len(desc)})"))

    version = fm.get("version")
    if version is not None and not VERSION_PATTERN.match(str(version)):
        findings.append(Finding("error", path, f"version '{version}' is not semver (x.y.z)"))

    status = fm.get("status")
    if status is not None and status not in STATUS_VALUES:
        findings.append(Finding("error", path, f"status '{status}' not one of {sorted(STATUS_VALUES)}"))

    risk = fm.get("risk")
    if risk is not None and risk not in RISK_VALUES:
        findings.append(Finding("error", path, f"risk '{risk}' not one of {sorted(RISK_VALUES)}"))

    permissions = fm.get("permissions")
    if isinstance(permissions, dict):
        fs = permissions.get("filesystem")
        if fs is not None and fs not in FS_VALUES:
            findings.append(Finding("error", path, f"permissions.filesystem '{fs}' invalid"))
        for key in ("shell", "network"):
            val = permissions.get(key)
            if val is not None and val not in SHELL_NET_VALUES:
                findings.append(Finding("error", path, f"permissions.{key} '{val}' invalid"))

    for key in fm.keys():
        if key not in known_fields:
            findings.append(Finding("warning", path, f"undeclared frontmatter field: {key}"))


def scan_for_secrets(text, path, findings):
    for label, pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match and not looks_like_placeholder(match.group(0)):
            findings.append(Finding("error", path, f"possible {label} found in file content"))


def validate_skill(skill_dir, known_fields, findings):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        findings.append(Finding("error", skill_dir, "missing SKILL.md"))
        return

    text = skill_md.read_text(errors="replace")
    if not text.startswith("---"):
        findings.append(Finding("error", skill_md, "SKILL.md has no YAML frontmatter"))
        return

    parts = text.split("---", 2)
    if len(parts) < 3:
        findings.append(Finding("error", skill_md, "malformed frontmatter delimiters"))
        return

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        findings.append(Finding("error", skill_md, f"invalid YAML: {e}"))
        return

    validate_frontmatter(fm, skill_dir.name, known_fields, findings, skill_md)

    for md_file in skill_dir.rglob("*"):
        if md_file.is_file() and md_file.suffix in {".md", ".py", ".sh", ".env", ".json", ".yml", ".yaml"}:
            scan_for_secrets(md_file.read_text(errors="replace"), md_file, findings)


def validate_tier(tier_name, findings, name_registry):
    tier_dir = REPO_ROOT / tier_name
    if not tier_dir.exists():
        return

    known_fields, _ = load_schema_field_names()
    seen_in_tier = {}

    for skill_dir in sorted(p for p in tier_dir.iterdir() if p.is_dir()):
        if (tier_name, skill_dir.name) in NON_SKILL_DIRS:
            continue

        pre_count = len(findings)
        validate_skill(skill_dir, known_fields, findings)

        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            text = skill_md.read_text(errors="replace")
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                    name = fm.get("name")
                    if name:
                        if name in seen_in_tier:
                            findings.append(
                                Finding(
                                    "error",
                                    skill_md,
                                    f"duplicate name '{name}' also used by {seen_in_tier[name]} "
                                    f"within {tier_name}/",
                                )
                            )
                        else:
                            seen_in_tier[name] = skill_dir.name
                except yaml.YAMLError:
                    pass

        if len(findings) == pre_count:
            name_registry.setdefault(tier_name, []).append(skill_dir.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="Also print warnings")
    args = parser.parse_args()

    if not SCHEMA_PATH.exists():
        print(f"ERROR: schema not found at {SCHEMA_PATH}", file=sys.stderr)
        return 1

    findings = []
    name_registry = {}
    for tier in TIERS:
        validate_tier(tier, findings, name_registry)

    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    for f in errors:
        print(f)
    if args.verbose:
        for f in warnings:
            print(f)

    total_skills = sum(len(v) for v in name_registry.values())
    print(f"\nValidated {total_skills} skills across {len(TIERS)} tiers.")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)"
          + ("" if args.verbose else " (run with --verbose to see warnings)"))

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
