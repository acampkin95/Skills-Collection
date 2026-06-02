#!/usr/bin/env python3
"""
Promote validated skill from skills_staging to skills_master (production).

This script:
- Validates skill meets all production requirements
- Creates backup of any replaced skill
- Moves skill to master directory
- Updates INDEX.md in master
- Logs change in CHANGELOG.md
- Optionally creates agent-specific copies

Usage:
    python promote-skill-production.py [skill-name] [--dry-run] [--auto-conversions]

Examples:
    python promote-skill-production.py my-skill-name --dry-run
    python promote-skill-production.py my-skill-name
    python promote-skill-production.py my-skill-name --auto-conversions
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import yaml

# Get repository root
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent

STAGING_DIR = REPO_ROOT / "skills_staging"
MASTER_DIR = REPO_ROOT / "skills_master"
ARCHIVE_DIR = REPO_ROOT / ".archive"
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"

# Agent-specific conversion directories
CONVERSIONS_DIR = REPO_ROOT / "skills_conversions"
AGENT_DIRS = {
    "claude": CONVERSIONS_DIR / "claude",
    "codex": CONVERSIONS_DIR / "codex",
    "opencode": CONVERSIONS_DIR / "opencode",
    "pi": CONVERSIONS_DIR / "pi",
}


class SkillPromoter:
    """Promote skill from staging to production."""

    def __init__(self, skill_name: str, dry_run: bool = False, auto_conversions: bool = False):
        self.skill_name = skill_name
        self.dry_run = dry_run
        self.auto_conversions = auto_conversions
        self.staging_path = STAGING_DIR / skill_name
        self.master_path = MASTER_DIR / skill_name
        self.errors = []
        self.warnings = []
        self.info = []

    def log(self, level: str, message: str):
        """Log a message."""
        if level == "error":
            self.errors.append(message)
        elif level == "warning":
            self.warnings.append(message)
        else:
            self.info.append(message)

    def promote(self) -> bool:
        """Execute promotion. Returns True if successful."""
        # Pre-flight checks
        if not self._check_staging_exists():
            return False

        if not self._validate_metadata():
            return False

        # Check for existing skill
        if self._check_master_exists():
            if not self._backup_existing():
                return False

        # Perform promotion
        if not self.dry_run:
            if not self._copy_to_master():
                return False

            self._update_changelog()
            self._update_index()

            if self.auto_conversions:
                self._create_agent_conversions()

        return True

    def _check_staging_exists(self) -> bool:
        """Check if skill exists in staging."""
        if not self.staging_path.exists():
            self.log("error", f"Skill not found in staging: {self.staging_path}")
            return False

        skill_md = self.staging_path / "SKILL.md"
        if not skill_md.exists():
            self.log("error", f"SKILL.md not found: {skill_md}")
            return False

        self.log("info", f"Staging skill found: {self.staging_path}")
        return True

    def _validate_metadata(self) -> bool:
        """Validate skill metadata."""
        skill_md = self.staging_path / "SKILL.md"

        try:
            with open(skill_md, "r") as f:
                content = f.read()
        except Exception as e:
            self.log("error", f"Cannot read SKILL.md: {e}")
            return False

        # Extract YAML
        if not content.startswith("---"):
            self.log("error", "SKILL.md must start with YAML frontmatter")
            return False

        try:
            end_index = content.index("---", 3)
            frontmatter_raw = content[3:end_index].strip()
            metadata = yaml.safe_load(frontmatter_raw) or {}
        except Exception as e:
            self.log("error", f"Failed to parse YAML: {e}")
            return False

        # Check required fields
        if "name" not in metadata:
            self.log("error", "Missing required field: name")
            return False

        if "description" not in metadata:
            self.log("error", "Missing required field: description")
            return False

        # Check name matches
        if metadata["name"] != self.skill_name:
            self.log("error", f"Skill name mismatch: {metadata['name']} != {self.skill_name}")
            return False

        self.log("info", f"Metadata validated for: {metadata['name']}")
        self.metadata = metadata
        return True

    def _check_master_exists(self) -> bool:
        """Check if skill already exists in master."""
        if self.master_path.exists():
            self.log("warning", f"Skill already exists in master: {self.master_path}")
            return True
        return False

    def _backup_existing(self) -> bool:
        """Backup existing skill before replacing."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"{self.skill_name}-backup-{timestamp}"
        backup_path = ARCHIVE_DIR / backup_name

        try:
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            shutil.move(str(self.master_path), str(backup_path))
            self.log("info", f"Backed up existing skill: {backup_path}")
            return True
        except Exception as e:
            self.log("error", f"Failed to backup existing skill: {e}")
            return False

    def _copy_to_master(self) -> bool:
        """Copy skill from staging to master."""
        try:
            MASTER_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copytree(str(self.staging_path), str(self.master_path))
            self.log("info", f"Promoted skill to master: {self.master_path}")
            return True
        except Exception as e:
            self.log("error", f"Failed to copy to master: {e}")
            return False

    def _create_agent_conversions(self):
        """Create agent-specific copies if applicable."""
        for agent_name, agent_dir in AGENT_DIRS.items():
            agent_skill_path = agent_dir / self.skill_name

            try:
                agent_dir.mkdir(parents=True, exist_ok=True)
                if agent_skill_path.exists():
                    shutil.rmtree(str(agent_skill_path))
                shutil.copytree(str(self.master_path), str(agent_skill_path))
                self.log("info", f"Created agent-specific copy for {agent_name}")
            except Exception as e:
                self.log("warning", f"Failed to create {agent_name} conversion: {e}")

    def _update_changelog(self):
        """Update CHANGELOG.md with promotion."""
        try:
            # Read existing changelog
            if CHANGELOG_PATH.exists():
                with open(CHANGELOG_PATH, "r") as f:
                    existing = f.read()
            else:
                existing = "# Changelog\n\n"

            # Format new entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"""## [{timestamp}] PROMOTED TO PRODUCTION

**Skill:** `{self.skill_name}`  
**Name:** {self.metadata.get('name', 'N/A')}  
**Description:** {self.metadata.get('description', 'N/A')[:100]}...  
**Source:** skills_staging → skills_master  
**Status:** ✅ Production Ready

"""

            # Prepend new entry after header
            if "# Changelog" in existing:
                parts = existing.split("# Changelog\n", 1)
                updated = parts[0] + "# Changelog\n\n" + entry + parts[1]
            else:
                updated = "# Changelog\n\n" + entry + existing

            with open(CHANGELOG_PATH, "w") as f:
                f.write(updated)

            self.log("info", f"Updated CHANGELOG.md")
        except Exception as e:
            self.log("warning", f"Failed to update CHANGELOG.md: {e}")

    def _update_index(self):
        """Update INDEX.md in master directory."""
        try:
            index_path = MASTER_DIR / "INDEX.md"

            # Generate current index
            skills = sorted([d.name for d in MASTER_DIR.iterdir() if d.is_dir()])

            header = "# Master Skills Index\n\n"
            header += f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"Total Skills: {len(skills)}\n\n"

            header += "| Name | Description | Updated |\n"
            header += "|------|-------------|----------|\n"

            lines = [header]

            for skill in skills:
                skill_md = MASTER_DIR / skill / "SKILL.md"
                if skill_md.exists():
                    try:
                        with open(skill_md, "r") as f:
                            content = f.read()
                        if "---" in content:
                            fm_end = content.index("---", 3)
                            fm = yaml.safe_load(content[3:fm_end].strip()) or {}
                            desc = fm.get("description", "")[:50]
                            mtime = datetime.fromtimestamp(skill_md.stat().st_mtime).strftime("%Y-%m-%d")
                            lines.append(f"| `{skill}` | {desc}... | {mtime} |\n")
                    except Exception:
                        pass

            with open(index_path, "w") as f:
                f.writelines(lines)

            self.log("info", f"Updated INDEX.md with {len(skills)} skills")
        except Exception as e:
            self.log("warning", f"Failed to update INDEX.md: {e}")

    def report(self) -> str:
        """Generate promotion report."""
        lines = [
            f"\n{'='*70}",
            f"Promotion Report: {self.skill_name}",
            f"{'='*70}\n",
        ]

        # Mode
        mode = "DRY RUN" if self.dry_run else "EXECUTION"
        lines.append(f"Mode: {mode}\n")

        # Status
        if self.errors:
            status = "❌ FAILED"
        elif self.warnings:
            status = "⚠️  COMPLETED WITH WARNINGS"
        else:
            status = "✅ SUCCESS"

        lines.append(f"Status: {status}\n")

        # Metadata
        if hasattr(self, "metadata"):
            lines.append("Metadata:")
            lines.append(f"  Name: {self.metadata.get('name', 'N/A')}")
            lines.append(f"  Description: {self.metadata.get('description', 'N/A')[:80]}...")
            lines.append("")

        # Paths
        lines.append("Paths:")
        lines.append(f"  From: {self.staging_path}")
        lines.append(f"  To:   {self.master_path}")
        lines.append("")

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

        # Info
        if self.info:
            lines.append("Actions:")
            for info in self.info:
                lines.append(f"  ℹ️  {info}")
            lines.append("")

        lines.append(f"{'='*70}\n")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Promote validated skill from staging to production",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python promote-skill-production.py my-skill-name --dry-run
  python promote-skill-production.py my-skill-name
  python promote-skill-production.py my-skill-name --auto-conversions
        """,
    )

    parser.add_argument(
        "skill_name",
        help="Skill name to promote from staging to master",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without making changes",
    )

    parser.add_argument(
        "--auto-conversions",
        action="store_true",
        help="Automatically create agent-specific copies",
    )

    args = parser.parse_args()

    promoter = SkillPromoter(args.skill_name, dry_run=args.dry_run, auto_conversions=args.auto_conversions)
    success = promoter.promote()
    print(promoter.report())

    return 0 if success and not promoter.errors else 1


if __name__ == "__main__":
    sys.exit(main())
