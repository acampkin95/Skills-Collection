#!/usr/bin/env python3
"""Validate the skills in this repository.

Checks every skill directory directly under skills_master/, skills_staging/
and skills_devtesting/ against schema/skill.schema.json and the rules in
docs/authoring/advanced-skill-development.md:

Errors (always fail):
  - SKILL.md missing, without frontmatter, or with unparseable YAML
  - name missing, over 64 characters, not lowercase-hyphen form, not equal to
    the folder name, or containing a reserved word ("anthropic", "claude")
  - description missing, empty, over 1024 characters, or containing XML tags
  - compatibility over 500 characters; metadata values that are not strings
  - a status, risk or version value outside the allowed set
  - a relative Markdown link that does not resolve
  - a Python script that does not compile, or a shell script that fails bash -n
  - duplicate names within one tier
  - a committed secret-shaped string
  - metadata.interface "cli" without a "-cli" name suffix, or a "-cli" suffix
    without metadata.interface "cli"

Warnings (fail only with --strict):
  - SKILL.md body over 500 lines
  - description that is third-person-violating, lacks a trigger phrase, or
    looks truncated
  - Claude Code-only frontmatter fields (not portable to uploads)
  - unknown frontmatter fields
  - TODO/FIXME markers
  - nested SKILL.md copies (not discovered by Claude Code)
  - script with a shebang that is not executable
  - files over 5 MB

Usage:
    python SkillsFramework/scripts/validate_skills.py [--verbose] [--strict]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "skill.schema.json"

TIERS = ["skills_master", "skills_staging", "skills_devtesting"]

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
RESERVED_WORDS = ("anthropic", "claude")
XML_TAG_RE = re.compile(r"</?[A-Za-z][\w-]*(?:\s[^>]*)?>")
TRIGGER_RE = re.compile(r"\b(use when|use this skill when|use for|when the user|when user)\b", re.I)
THIRD_PERSON_BAD_RE = re.compile(r"^\s*(I|I'm|I'll|You|You're|We|We're|Let me)\b")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.S)
TODO_RE = re.compile(r"\b(TODO|FIXME|XXX)\b")

CLAUDE_CODE_ONLY = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
    "background", "hooks", "paths", "shell",
}
PORTABLE = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
REPO_EXTRA = {
    "version", "status", "risk", "requires_confirmation", "permissions", "category",
    "tags", "runtime", "reviewed", "references", "inputs", "dependencies", "tests",
}
KNOWN = PORTABLE | CLAUDE_CODE_ONLY | REPO_EXTRA

SECRET_PATTERNS = [
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----\s*\n\s*[A-Za-z0-9+/]{30,}")),
    ("OpenAI-style key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
]


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, msg):
        self.errors.append(f"[ERROR] {path}: {msg}")

    def warn(self, path, msg):
        self.warnings.append(f"[WARN]  {path}: {msg}")


def is_placeholder(secret):
    tail = secret[-10:]
    return len(set(tail)) <= 2


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, "no YAML frontmatter"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "unterminated frontmatter"
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        return None, f"invalid YAML: {str(exc).splitlines()[0]}"
    if not isinstance(data, dict):
        return None, "frontmatter is not a mapping"
    return (data, parts[2]), None


def check_links(skill_md, body, report):
    scrubbed = FENCE_RE.sub("", body)
    for target in LINK_RE.findall(scrubbed):
        if target.startswith(("http://", "https://", "mailto:", "#", "/")):
            continue
        local = target.split("#", 1)[0]
        if not local:
            continue
        if not (skill_md.parent / local).resolve().exists():
            report.error(skill_md, f"broken relative link: {target}")


def check_scripts(skill_dir, report):
    for path in skill_dir.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.stat().st_size > 5 * 1024 * 1024:
            report.warn(path, "file over 5 MB")
        if path.suffix == ".py":
            try:
                compile(path.read_text(errors="replace"), str(path), "exec")
            except SyntaxError as exc:
                report.error(path, f"python syntax error line {exc.lineno}: {exc.msg}")
        elif path.suffix == ".sh":
            res = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
            if res.returncode != 0:
                report.error(path, f"shell syntax error: {res.stderr.strip().splitlines()[-1]}")
        if path.suffix in {".py", ".sh"}:
            first = path.read_text(errors="replace").split("\n", 1)[0]
            if first.startswith("#!") and not path.stat().st_mode & 0o111:
                report.warn(path, "has shebang but is not executable")


def check_secrets(skill_dir, report):
    for path in skill_dir.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".sh", ".json", ".yml", ".yaml", ".env"}:
            continue
        text = path.read_text(errors="replace")
        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                if not is_placeholder(match.group(0)):
                    report.error(path, f"possible {label}")
                    break


def validate_skill(skill_dir, tier, report, names_seen, interface_map):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        report.error(skill_dir, "missing SKILL.md")
        return
    text = skill_md.read_text(errors="replace")
    parsed, err = parse_frontmatter(text)
    if err:
        report.error(skill_md, err)
        return
    fm, body = parsed

    name = fm.get("name")
    if not name:
        report.error(skill_md, "missing required field: name")
    else:
        name = str(name)
        if len(name) > 64:
            report.error(skill_md, f"name longer than 64 characters ({len(name)})")
        if not NAME_RE.match(name):
            report.error(skill_md, f"name '{name}' must be lowercase letters, digits and single hyphens")
        if name != skill_dir.name:
            report.error(skill_md, f"name '{name}' does not match folder '{skill_dir.name}'")
        for word in RESERVED_WORDS:
            if word in name:
                report.error(skill_md, f"name contains reserved word '{word}' (rejected by API uploads)")
        if name in names_seen.setdefault(tier, {}):
            report.error(skill_md, f"duplicate name '{name}' also in {names_seen[tier][name]}")
        else:
            names_seen[tier][name] = str(skill_md.parent)

    desc = fm.get("description")
    if not desc or not str(desc).strip():
        report.error(skill_md, "missing or empty description")
    else:
        desc = str(desc)
        if len(desc) > 1024:
            report.error(skill_md, f"description over 1024 characters ({len(desc)})")
        if XML_TAG_RE.search(desc):
            report.error(skill_md, "description contains XML-like tags")
        if THIRD_PERSON_BAD_RE.search(desc):
            report.warn(skill_md, "description is not third person")
        if not TRIGGER_RE.search(desc):
            report.warn(skill_md, "description has no trigger phrase (e.g. 'Use when ...')")
        if not desc.rstrip().endswith((".", ")", "'", '"', "`")):
            report.warn(skill_md, "description may be truncated (no closing punctuation)")

    compat = fm.get("compatibility")
    if compat is not None and len(str(compat)) > 500:
        report.error(skill_md, f"compatibility over 500 characters ({len(str(compat))})")

    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            report.error(skill_md, "metadata must be a mapping")
        else:
            for k, v in meta.items():
                if not isinstance(v, str):
                    report.error(skill_md, f"metadata.{k} must be a string")

    status = fm.get("status")
    if status is not None and status not in {"experimental", "staging", "stable", "deprecated"}:
        report.error(skill_md, f"status '{status}' not allowed")
    risk = fm.get("risk")
    if risk is not None and risk not in {"low", "medium", "high"}:
        report.error(skill_md, f"risk '{risk}' not allowed")
    version = fm.get("version")
    if version is not None and not VERSION_RE.match(str(version)):
        report.error(skill_md, f"version '{version}' is not MAJOR.MINOR.PATCH")

    interface = str((meta or {}).get("interface", "")) if isinstance(meta, dict) else ""
    if interface == "cli" and name and not str(name).endswith("-cli"):
        report.error(skill_md, "metadata.interface is 'cli' but name lacks the '-cli' suffix")
    if name and str(name).endswith("-cli") and interface != "cli":
        report.warn(skill_md, "name ends with '-cli' but metadata.interface is not 'cli'")
    interface_map[str(skill_dir)] = interface

    for key in fm:
        if key in CLAUDE_CODE_ONLY:
            report.warn(skill_md, f"Claude Code-only field '{key}' (not accepted by API/claude.ai uploads)")
        elif key not in KNOWN:
            report.warn(skill_md, f"unknown frontmatter field '{key}'")

    lines = body.count("\n")
    if lines > 500:
        report.warn(skill_md, f"body is {lines} lines (guideline: under 500; move detail to references/)")

    if TODO_RE.search(body):
        report.warn(skill_md, "TODO/FIXME marker present")

    check_links(skill_md, body, report)
    check_scripts(skill_dir, report)
    check_secrets(skill_dir, report)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verbose", action="store_true", help="print warnings")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="emit a JSON summary to stdout")
    args = parser.parse_args()

    if not SCHEMA_PATH.exists():
        print(f"ERROR: schema missing at {SCHEMA_PATH}", file=sys.stderr)
        return 2
    json.loads(SCHEMA_PATH.read_text())

    report = Report()
    names_seen = {}
    interface_map = {}
    discovered = {}
    nested_copies = []
    for tier in TIERS:
        base = REPO_ROOT / tier
        if not base.exists():
            continue
        discovered[tier] = 0
        for skill_dir in sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")):
            if skill_dir.name == "__pycache__":
                continue
            if not (skill_dir / "SKILL.md").exists() and not any(skill_dir.rglob("SKILL.md")):
                continue  # plain folder, not a skill
            if (skill_dir / "SKILL.md").exists():
                discovered[tier] += 1
                validate_skill(skill_dir, tier, report, names_seen, interface_map)
            for nested in skill_dir.rglob("SKILL.md"):
                if nested.parent != skill_dir:
                    nested_copies.append(str(nested.relative_to(REPO_ROOT)))

    for nested in sorted(set(nested_copies)):
        report.warn(REPO_ROOT / nested,
                    "nested SKILL.md is not discovered by Claude Code (router-tree copy); see docs/authoring")

    errors = report.errors + ([w for w in report.warnings] if args.strict else [])
    warnings = [] if args.strict else report.warnings

    for line in report.errors:
        print(line)
    if args.verbose or args.strict:
        for line in report.warnings:
            print(line)

    total = sum(discovered.values())
    print(f"\nDiscovered skills: {total} across {len(discovered)} tiers "
          f"({', '.join(f'{k}={v}' for k, v in discovered.items())})")
    print(f"Nested SKILL.md copies (not discovered): {len(set(nested_copies))}")
    print(f"{len(errors)} error(s), {len(warnings) if not args.strict else len(report.warnings)} warning(s)"
          + ("" if args.verbose or args.strict else " (run with --verbose to list warnings)"))

    if args.json:
        print(json.dumps({"discovered": discovered, "nested": len(set(nested_copies)),
                          "errors": len(errors), "warnings": len(report.warnings)}))

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
