#!/usr/bin/env python3
"""
Generate comprehensive skill inventory across all directories.

Creates skill index in various formats:
- Markdown (default) — Human-readable documentation
- JSON — Machine-readable for tooling
- CSV — Spreadsheet compatible

Usage:
    python generate-skill-index.py [--format markdown|json|csv] [--output FILE]

Examples:
    python generate-skill-index.py
    python generate-skill-index.py --format json
    python generate-skill-index.py --format json --output skills.json
"""

import os
import sys
import json
import csv
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Get repository root
# Resolve REPO_ROOT = two levels up from this script (SkillsFramework/scripts/ -> repo root)
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

MASTER_DIR = REPO_ROOT / "skills_master"
STAGING_DIR = REPO_ROOT / "skills_staging"
DEVTESTING_DIR = REPO_ROOT / "skills_devtesting"
CONVERSIONS_DIR = REPO_ROOT / "skills_conversions"


class SkillIndexGenerator:
    """Generate skill inventory."""

    def __init__(self):
        self.skills_by_status = {
            "production": [],
            "staging": [],
            "development": [],
            "agent-specific": {},
        }
        self.total_skills = 0
        self.errors = []

    def scan_directory(self, directory: Path, status: str) -> List[Dict]:
        """Scan directory for skills."""
        skills = []

        if not directory.exists():
            return skills

        for skill_dir in sorted(directory.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_data = self._parse_skill(skill_dir, status)
            if skill_data:
                skills.append(skill_data)
                self.total_skills += 1

        return skills

    def _parse_skill(self, skill_dir: Path, status: str) -> Optional[Dict]:
        """Parse skill metadata."""
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            return None

        try:
            with open(skill_md, "r") as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Cannot read {skill_dir.name}: {e}")
            return None

        # Parse YAML
        metadata = {}
        if content.startswith("---"):
            try:
                end_index = content.index("---", 3)
                fm_raw = content[3:end_index].strip()
                metadata = yaml.safe_load(fm_raw) or {}
            except Exception as e:
                self.errors.append(f"Cannot parse {skill_dir.name}: {e}")
                return None

        # Count files
        file_count = sum(1 for f in skill_dir.rglob("*") if f.is_file())
        subdirs = [d.name for d in skill_dir.iterdir() if d.is_dir()]

        # Get modification time
        try:
            mtime = datetime.fromtimestamp(skill_md.stat().st_mtime).strftime("%Y-%m-%d")
        except:
            mtime = "unknown"

        return {
            "name": metadata.get("name", skill_dir.name),
            "display_name": skill_dir.name,
            "description": metadata.get("description", "")[:100],
            "status": status,
            "path": str(skill_dir.relative_to(REPO_ROOT)),
            "files": file_count,
            "subdirs": subdirs,
            "last_modified": mtime,
            "has_examples": (skill_dir / "examples").exists() or (skill_dir / "EXAMPLES.md").exists(),
            "has_reference": (skill_dir / "reference").exists() or (skill_dir / "REFERENCE.md").exists(),
            "has_scripts": (skill_dir / "scripts").exists(),
        }

    def scan_all(self):
        """Scan all skill directories."""
        self.skills_by_status["production"] = self.scan_directory(MASTER_DIR, "production")
        self.skills_by_status["staging"] = self.scan_directory(STAGING_DIR, "staging")
        self.skills_by_status["development"] = self.scan_directory(DEVTESTING_DIR, "development")

        # Scan agent-specific conversions
        if CONVERSIONS_DIR.exists():
            for agent_dir in CONVERSIONS_DIR.iterdir():
                if agent_dir.is_dir():
                    agent_name = agent_dir.name
                    self.skills_by_status["agent-specific"][agent_name] = \
                        self.scan_directory(agent_dir, f"agent-specific-{agent_name}")

    def generate_markdown(self) -> str:
        """Generate Markdown index."""
        lines = [
            "# Skills Repository Index",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Skills:** {self.total_skills}",
            "",
            "---",
            "",
        ]

        # Summary
        lines.extend([
            "## Summary",
            "",
            "| Status | Count |",
            "|--------|-------|",
            f"| Production (master) | {len(self.skills_by_status['production'])} |",
            f"| Staging | {len(self.skills_by_status['staging'])} |",
            f"| Development | {len(self.skills_by_status['development'])} |",
            "",
        ])

        # Production skills
        lines.extend(self._markdown_section("Production Skills", self.skills_by_status["production"]))

        # Staging skills
        if self.skills_by_status["staging"]:
            lines.extend(self._markdown_section("Staging Skills", self.skills_by_status["staging"]))

        # Development skills
        if self.skills_by_status["development"]:
            lines.extend(self._markdown_section("Development Skills", self.skills_by_status["development"]))

        # Agent-specific
        for agent_name, skills in self.skills_by_status["agent-specific"].items():
            if skills:
                lines.extend(self._markdown_section(f"{agent_name.title()} Variants", skills))

        # Errors
        if self.errors:
            lines.extend([
                "## Errors",
                "",
            ])
            for err in self.errors:
                lines.append(f"- {err}")

        return "\n".join(lines)

    def _markdown_section(self, title: str, skills: List[Dict]) -> List[str]:
        """Generate markdown section for skills."""
        lines = [
            f"## {title}",
            "",
            "| Name | Description | Files | Status |",
            "|------|-------------|-------|--------|",
        ]

        for skill in skills:
            features = []
            if skill["has_examples"]:
                features.append("📚 examples")
            if skill["has_reference"]:
                features.append("📖 ref")
            if skill["has_scripts"]:
                features.append("🔧 scripts")

            feature_str = " ".join(features) if features else "—"

            desc = skill["description"][:60].replace("|", "\\|")
            lines.append(f"| `{skill['name']}` | {desc}... | {skill['files']} | {feature_str} |")

        lines.append("")
        return lines

    def generate_json(self) -> str:
        """Generate JSON index."""
        output = {
            "generated": datetime.now().isoformat(),
            "total_skills": self.total_skills,
            "summary": {
                "production": len(self.skills_by_status["production"]),
                "staging": len(self.skills_by_status["staging"]),
                "development": len(self.skills_by_status["development"]),
                "agent_specific": {k: len(v) for k, v in self.skills_by_status["agent-specific"].items()},
            },
            "skills": {
                "production": self.skills_by_status["production"],
                "staging": self.skills_by_status["staging"],
                "development": self.skills_by_status["development"],
                "agent_specific": self.skills_by_status["agent-specific"],
            },
            "errors": self.errors,
        }

        return json.dumps(output, indent=2)

    def generate_csv(self) -> str:
        """Generate CSV index."""
        lines = []
        fieldnames = ["name", "status", "description", "path", "files", "subdirs", "last_modified", "examples", "reference", "scripts"]

        # CSV header
        lines.append(",".join(fieldnames))

        # Collect all skills
        all_skills = []
        for skills in [
            self.skills_by_status["production"],
            self.skills_by_status["staging"],
            self.skills_by_status["development"],
        ]:
            all_skills.extend(skills)

        for agent_name, skills in self.skills_by_status["agent-specific"].items():
            all_skills.extend(skills)

        # Write skills
        for skill in sorted(all_skills, key=lambda s: (s["status"], s["name"])):
            row = [
                skill["name"],
                skill["status"],
                skill["description"].replace('"', '""'),  # Escape quotes
                skill["path"],
                str(skill["files"]),
                ";".join(skill["subdirs"]),
                skill["last_modified"],
                "Yes" if skill["has_examples"] else "No",
                "Yes" if skill["has_reference"] else "No",
                "Yes" if skill["has_scripts"] else "No",
            ]
            lines.append(',"'.join(f'"{v}"' for v in row))

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate skill inventory index",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate-skill-index.py
  python generate-skill-index.py --format json
  python generate-skill-index.py --format json --output skills.json
        """,
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json", "csv"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)",
    )

    args = parser.parse_args()

    # Generate index
    generator = SkillIndexGenerator()
    generator.scan_all()

    # Format output
    if args.format == "json":
        output = generator.generate_json()
    elif args.format == "csv":
        output = generator.generate_csv()
    else:
        output = generator.generate_markdown()

    # Write output
    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"✅ Generated {args.format} index: {args.output}")
        except Exception as e:
            print(f"❌ Error writing output: {e}")
            return 1
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
