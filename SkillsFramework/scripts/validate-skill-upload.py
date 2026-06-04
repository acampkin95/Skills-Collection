#!/usr/bin/env python3
"""
Validate skill before moving from skills_devtesting to skills_staging.

Checks:
- SKILL.md exists and is parseable
- YAML frontmatter is valid
- Metadata requirements (name, description)
- File structure and references
- No syntax errors
- No name conflicts with existing skills

Usage:
    python validate-skill-upload.py [skill-name] [--dry-run] [--verbose]
    python validate-skill-upload.py all [--dry-run]

Examples:
    python validate-skill-upload.py my-skill-name
    python validate-skill-upload.py my-skill-name --verbose
    python validate-skill-upload.py all
"""

import os
import sys
import re
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Optional

# Get repository root (where this script lives)
# Resolve REPO_ROOT = two levels up from this script (SkillsFramework/scripts/ -> repo root)
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

DEVTESTING_DIR = REPO_ROOT / "skills_devtesting"
STAGING_DIR = REPO_ROOT / "skills_staging"
MASTER_DIR = REPO_ROOT / "skills_master"

# Validation rules
NAME_PATTERN = r"^[a-z0-9][a-z0-9-]*$"
NAME_MIN_LENGTH = 3
NAME_MAX_LENGTH = 64
DESC_MAX_LENGTH = 1024

FORBIDDEN_WORDS = {"anthropic", "claude"}


class SkillValidator:
    """Validate a skill directory structure and metadata."""

    def __init__(self, skill_name: str, verbose: bool = False):
        self.skill_name = skill_name
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.info = []
        self.skill_path = DEVTESTING_DIR / skill_name
        self.skill_md_path = self.skill_path / "SKILL.md"

    def log(self, level: str, message: str):
        """Log a validation message."""
        if level == "error":
            self.errors.append(message)
        elif level == "warning":
            self.warnings.append(message)
        elif level == "info":
            self.info.append(message)

    def validate(self) -> bool:
        """Run all validation checks. Returns True if valid."""
        if not self._check_exists():
            return False

        self._check_skill_md()
        self._check_metadata()
        self._check_structure()
        self._check_references()
        self._check_conflicts()

        return len(self.errors) == 0

    def _check_exists(self) -> bool:
        """Check if skill directory exists."""
        if not self.skill_path.exists():
            self.log("error", f"Skill directory not found: {self.skill_path}")
            return False

        if not self.skill_path.is_dir():
            self.log("error", f"Not a directory: {self.skill_path}")
            return False

        if not self.skill_md_path.exists():
            self.log("error", f"SKILL.md not found in {self.skill_path}")
            return False

        self.log("info", f"Skill directory exists: {self.skill_path}")
        return True

    def _check_skill_md(self):
        """Parse and validate SKILL.md."""
        try:
            with open(self.skill_md_path, "r") as f:
                content = f.read()
        except Exception as e:
            self.log("error", f"Cannot read SKILL.md: {e}")
            return

        if not content.startswith("---"):
            self.log("error", "SKILL.md must start with --- (YAML frontmatter)")
            return

        # Find end of frontmatter
        try:
            end_index = content.index("---", 3)
            frontmatter_raw = content[3:end_index].strip()
            body = content[end_index + 3:].lstrip("\n")
        except ValueError:
            self.log("error", "SKILL.md frontmatter not properly closed (missing second ---)")
            return

        # Parse YAML
        try:
            self.metadata = yaml.safe_load(frontmatter_raw) or {}
        except yaml.YAMLError as e:
            self.log("error", f"YAML frontmatter parsing failed: {e}")
            return

        self.log("info", "SKILL.md frontmatter is valid YAML")

        # Check body is not empty
        if not body or not body.strip():
            self.log("warning", "SKILL.md body is empty")

    def _check_metadata(self):
        """Validate name and description fields."""
        if not hasattr(self, "metadata"):
            return

        # Check name
        name = self.metadata.get("name", "")
        if not name:
            self.log("error", "Missing required field: name")
        else:
            self._validate_name(name)

        # Check description
        description = self.metadata.get("description", "")
        if not description:
            self.log("error", "Missing required field: description")
        else:
            self._validate_description(description)

        # Check for only name and description
        allowed_fields = {"name", "description"}
        extra_fields = set(self.metadata.keys()) - allowed_fields
        if extra_fields:
            self.log("warning", f"Extra metadata fields (will be removed): {', '.join(extra_fields)}")

    def _validate_name(self, name: str):
        """Validate skill name."""
        # Length check
        if len(name) < NAME_MIN_LENGTH:
            self.log("error", f"Name too short (min {NAME_MIN_LENGTH}): {name}")
        elif len(name) > NAME_MAX_LENGTH:
            self.log("error", f"Name too long (max {NAME_MAX_LENGTH}): {name}")

        # Pattern check
        if not re.match(NAME_PATTERN, name):
            self.log("error", f"Name must contain only lowercase letters, numbers, and hyphens: {name}")

        # Forbidden words
        for word in FORBIDDEN_WORDS:
            if word in name.lower():
                self.log("error", f"Name cannot contain '{word}': {name}")

        # XML tags check
        if "<" in name or ">" in name:
            self.log("error", f"Name cannot contain XML tags: {name}")

        if self.verbose:
            self.log("info", f"Name validated: {name}")

    def _validate_description(self, description: str):
        """Validate skill description."""
        # Length check
        if len(description) > DESC_MAX_LENGTH:
            self.log("error", f"Description too long (max {DESC_MAX_LENGTH} chars): {len(description)} chars")

        # XML tags check
        if "<" in description or ">" in description:
            self.log("error", "Description cannot contain XML tags")

        # Third person check
        first_person = {"i can", "i will", "i provide", "i help", "i create"}
        second_person = {"you can", "you will", "you should", "you provide"}

        desc_lower = description.lower()
        for phrase in first_person:
            if phrase in desc_lower:
                self.log("warning", f"Description uses first person (should be third): '{phrase}'")
                break

        for phrase in second_person:
            if phrase in desc_lower:
                self.log("warning", f"Description uses second person (should be third): '{phrase}'")
                break

        if self.verbose:
            self.log("info", f"Description length: {len(description)} chars")

    def _check_structure(self):
        """Validate directory structure."""
        # Check for common subdirectories
        expected_subdirs = ["reference", "references", "examples", "scripts"]
        found_subdirs = []

        for subdir in expected_subdirs:
            subdir_path = self.skill_path / subdir
            if subdir_path.exists() and subdir_path.is_dir():
                found_subdirs.append(subdir)

        if found_subdirs:
            self.log("info", f"Found subdirectories: {', '.join(found_subdirs)}")

        # Check for files
        files = list(self.skill_path.glob("*"))
        file_count = len(files)
        self.log("info", f"Skill contains {file_count} items")

        # Check for expected patterns
        file_names = [f.name for f in files if f.is_file()]
        if "README.md" in file_names:
            self.log("info", "README.md found (good practice)")

    def _check_references(self):
        """Validate file references in SKILL.md."""
        try:
            with open(self.skill_md_path, "r") as f:
                content = f.read()
        except Exception:
            return

        # Extract markdown links: [text](path)
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        links = re.findall(link_pattern, content)

        if not links and self.verbose:
            self.log("info", "No file references found in SKILL.md")

        missing_refs = []
        for text, path in links:
            # Skip external links and anchors
            if path.startswith(("http://", "https://", "#")):
                continue

            ref_path = self.skill_path / path
            if not ref_path.exists():
                missing_refs.append(f"{text} → {path}")
                self.log("error", f"Referenced file not found: {path}")

        if links and not missing_refs:
            self.log("info", f"All {len(links)} file references exist")

    def _check_conflicts(self):
        """Check for name conflicts with existing skills."""
        if not hasattr(self, "metadata"):
            return

        name = self.metadata.get("name", "")
        if not name:
            return

        # Check master
        if (MASTER_DIR / name).exists():
            self.log("warning", f"Skill already exists in master: {name}")

        # Check staging
        if (STAGING_DIR / name).exists():
            self.log("warning", f"Skill already exists in staging: {name}")

    def report(self) -> str:
        """Generate validation report."""
        lines = [
            f"\n{'='*70}",
            f"Validation Report: {self.skill_name}",
            f"{'='*70}\n",
        ]

        # Status
        if self.errors:
            status = "❌ FAILED"
        elif self.warnings:
            status = "⚠️  WARNINGS"
        else:
            status = "✅ PASSED"

        lines.append(f"Status: {status}\n")

        # Errors
        if self.errors:
            lines.append("Errors:")
            for err in self.errors:
                lines.append(f"  ❌ {err}")
            lines.append("")

        # Warnings
        if self.warnings:
            lines.append("Warnings:")
            for warn in self.warnings:
                lines.append(f"  ⚠️  {warn}")
            lines.append("")

        # Info (only in verbose mode)
        if self.verbose and self.info:
            lines.append("Info:")
            for info in self.info:
                lines.append(f"  ℹ️  {info}")
            lines.append("")

        # Summary
        lines.append(f"Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        lines.append(f"{'='*70}\n")

        return "\n".join(lines)


def validate_skill(skill_name: str, verbose: bool = False) -> bool:
    """Validate a single skill."""
    validator = SkillValidator(skill_name, verbose)
    is_valid = validator.validate()
    print(validator.report())
    return is_valid


def validate_all(verbose: bool = False) -> int:
    """Validate all skills in devtesting."""
    if not DEVTESTING_DIR.exists():
        print(f"Error: {DEVTESTING_DIR} not found")
        return 1

    skills = [d.name for d in DEVTESTING_DIR.iterdir() if d.is_dir()]

    if not skills:
        print(f"No skills found in {DEVTESTING_DIR}")
        return 0

    print(f"\nValidating {len(skills)} skills in {DEVTESTING_DIR}\n")

    passed = 0
    failed = 0

    for skill_name in sorted(skills):
        validator = SkillValidator(skill_name, verbose)
        if validator.validate():
            print(f"✅ {skill_name}")
            passed += 1
        else:
            print(f"❌ {skill_name}")
            if validator.errors:
                for err in validator.errors:
                    print(f"   {err}")
            failed += 1

    print(f"\n{'='*70}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*70}\n")

    return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Validate skills before promoting to staging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate-skill-upload.py my-skill-name
  python validate-skill-upload.py my-skill-name --verbose
  python validate-skill-upload.py all
        """,
    )

    parser.add_argument(
        "skill_name",
        nargs="?",
        default="all",
        help="Skill name to validate, or 'all' for all skills",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed validation info",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without making changes",
    )

    args = parser.parse_args()

    if args.skill_name == "all":
        return validate_all(verbose=args.verbose)
    else:
        is_valid = validate_skill(args.skill_name, verbose=args.verbose)
        return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
