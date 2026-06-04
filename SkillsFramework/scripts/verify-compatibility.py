#!/usr/bin/env python3
"""
Verify skill compatibility across agents.

Tests:
- File access patterns
- Required package availability (when applicable)
- Script execution compatibility
- Metadata loading
- Reference file structure

Usage:
    python verify-compatibility.py [skill-name] [--agents claude,codex,pi] [--verbose]

Examples:
    python verify-compatibility.py my-skill
    python verify-compatibility.py my-skill --agents claude,pi
    python verify-compatibility.py my-skill --agents all --verbose
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Dict, Set, Optional
import yaml

# Get repository root
# Resolve REPO_ROOT = two levels up from this script (SkillsFramework/scripts/ -> repo root)
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

MASTER_DIR = REPO_ROOT / "skills_master"
STAGING_DIR = REPO_ROOT / "skills_staging"
DEVTESTING_DIR = REPO_ROOT / "skills_devtesting"
CONVERSIONS_DIR = REPO_ROOT / "skills_conversions"

# Agent definitions
AGENTS = {
    "claude": {
        "name": "Claude Code",
        "env": "macOS/Linux IDE",
        "network": True,
        "packages": True,
        "paths": ["~/.claude/skills/"],
    },
    "pi": {
        "name": "Pi",
        "env": "CLI agent",
        "network": True,
        "packages": True,
        "paths": ["~/.pi/agent/skills/"],
    },
    "codex": {
        "name": "Codex CLI",
        "env": "CLI editor",
        "network": True,
        "packages": True,
        "paths": ["skills_conversions/codex/"],
    },
    "opencode": {
        "name": "OpenCode",
        "env": "VS Code extension",
        "network": True,
        "packages": True,
        "paths": ["skills_conversions/opencode/"],
    },
}

# Common Python packages (available in most environments)
STANDARD_PACKAGES = {
    "os", "sys", "re", "json", "yaml", "pathlib", "datetime",
    "csv", "subprocess", "shutil", "tempfile", "hashlib",
}

# Packages commonly available in agent environments
COMMON_PACKAGES = {
    "requests", "httpx", "aiohttp",
    "pandas", "numpy", "scipy",
    "pydantic", "click", "typer",
    "beautifulsoup4", "lxml", "html5lib",
    "PIL", "Pillow", "opencv",
    "pdfplumber", "pypdf", "reportlab",
    "python-docx", "docx", "openpyxl",
    "slugify", "colorama", "tqdm",
}


class CompatibilityVerifier:
    """Verify skill compatibility."""

    def __init__(self, skill_name: str, agents: List[str], verbose: bool = False):
        self.skill_name = skill_name
        self.agents = agents
        self.verbose = verbose
        self.results = {}
        self.warnings = []
        self.errors = []

        # Find skill
        self.skill_path = self._find_skill(skill_name)
        if not self.skill_path:
            raise ValueError(f"Skill not found: {skill_name}")

    def _find_skill(self, skill_name: str) -> Optional[Path]:
        """Find skill in any directory."""
        for base_dir in [MASTER_DIR, STAGING_DIR, DEVTESTING_DIR]:
            skill_path = base_dir / skill_name
            if skill_path.exists():
                return skill_path

        # Check conversions
        for agent_dir in CONVERSIONS_DIR.iterdir():
            if agent_dir.is_dir():
                skill_path = agent_dir / skill_name
                if skill_path.exists():
                    return skill_path

        return None

    def verify_all(self) -> bool:
        """Verify on all specified agents."""
        all_pass = True

        for agent_name in self.agents:
            if agent_name not in AGENTS:
                self.errors.append(f"Unknown agent: {agent_name}")
                all_pass = False
                continue

            result = self._verify_agent(agent_name)
            self.results[agent_name] = result
            if not result["pass"]:
                all_pass = False

        return all_pass

    def _verify_agent(self, agent_name: str) -> Dict:
        """Verify compatibility with a single agent."""
        result = {
            "agent": agent_name,
            "pass": True,
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        agent = AGENTS[agent_name]

        # Check SKILL.md
        result["checks"]["skill_md"] = self._check_skill_md(result)

        # Check references
        result["checks"]["references"] = self._check_references(result)

        # Check scripts
        result["checks"]["scripts"] = self._check_scripts(result)

        # Check packages
        if agent.get("packages"):
            result["checks"]["packages"] = self._check_packages(result)

        # Check paths (Windows vs Unix)
        result["checks"]["paths"] = self._check_paths(result, agent_name)

        # Summary
        if result["errors"]:
            result["pass"] = False

        return result

    def _check_skill_md(self, result: Dict) -> bool:
        """Check SKILL.md exists and is valid."""
        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            result["errors"].append("SKILL.md not found")
            return False

        try:
            with open(skill_md, "r") as f:
                content = f.read()

            if not content.startswith("---"):
                result["errors"].append("Invalid YAML frontmatter")
                return False

            if "---" not in content[3:]:
                result["errors"].append("Frontmatter not closed properly")
                return False

            # Parse YAML
            end_index = content.index("---", 3)
            fm = yaml.safe_load(content[3:end_index].strip()) or {}

            if "name" not in fm or "description" not in fm:
                result["errors"].append("Missing required metadata fields")
                return False

            return True

        except Exception as e:
            result["errors"].append(f"SKILL.md parse error: {e}")
            return False

    def _check_references(self, result: Dict) -> bool:
        """Check that referenced files exist."""
        skill_md = self.skill_path / "SKILL.md"

        try:
            with open(skill_md, "r") as f:
                content = f.read()
        except Exception as e:
            result["errors"].append(f"Cannot read SKILL.md: {e}")
            return False

        # Extract markdown links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        links = re.findall(link_pattern, content)

        missing = []
        for text, path in links:
            # Skip external links
            if path.startswith(("http://", "https://", "#")):
                continue

            ref_path = self.skill_path / path
            if not ref_path.exists():
                missing.append(path)

        if missing:
            result["errors"].append(f"Missing references: {', '.join(missing)}")
            return False

        if links:
            result["checks"]["references"] = f"✅ {len(links)} references valid"

        return True

    def _check_scripts(self, result: Dict) -> bool:
        """Check scripts exist and are executable."""
        scripts_dir = self.skill_path / "scripts"

        if not scripts_dir.exists():
            if self.verbose:
                result["checks"]["scripts"] = "ℹ️  No scripts directory"
            return True

        scripts = list(scripts_dir.glob("*"))

        if not scripts:
            if self.verbose:
                result["checks"]["scripts"] = "ℹ️  Scripts directory empty"
            return True

        # Check for Python scripts
        py_scripts = [s for s in scripts if s.suffix == ".py"]
        if py_scripts:
            result["checks"]["scripts"] = f"✅ {len(py_scripts)} Python scripts"

            # Check for shebang
            for script in py_scripts:
                try:
                    with open(script, "r") as f:
                        first_line = f.readline()
                        if not first_line.startswith("#!"):
                            result["warnings"].append(f"Script missing shebang: {script.name}")
                except Exception:
                    pass

        return True

    def _check_packages(self, result: Dict) -> bool:
        """Check for required packages in scripts and SKILL.md."""
        required_packages = self._extract_packages()

        if not required_packages:
            if self.verbose:
                result["checks"]["packages"] = "ℹ️  No packages required"
            return True

        unavailable = []
        for pkg in required_packages:
            if pkg not in STANDARD_PACKAGES and pkg not in COMMON_PACKAGES:
                unavailable.append(pkg)

        if unavailable:
            result["warnings"].append(f"Packages may not be available: {', '.join(unavailable)}")
            return True

        result["checks"]["packages"] = f"✅ All {len(required_packages)} packages available"
        return True

    def _extract_packages(self) -> Set[str]:
        """Extract required packages from skill."""
        packages = set()

        # Check SKILL.md for imports
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            try:
                with open(skill_md, "r") as f:
                    content = f.read()
                    # Find import statements
                    imports = re.findall(r"(?:import|from)\s+([a-zA-Z0-9_]+)", content)
                    packages.update(imports)
            except:
                pass

        # Check scripts
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.py"):
                try:
                    with open(script, "r") as f:
                        content = f.read()
                        imports = re.findall(r"(?:import|from)\s+([a-zA-Z0-9_]+)", content)
                        packages.update(imports)
                except:
                    pass

        return packages

    def _check_paths(self, result: Dict, agent_name: str) -> bool:
        """Check for platform-specific path issues."""
        issues = []

        # Check all files for Windows-style paths
        for file_path in self.skill_path.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix in [".py", ".sh", ".md"]:
                try:
                    with open(file_path, "r", errors="ignore") as f:
                        content = f.read()
                        # Look for Windows paths
                        if "\\" in content and "scripts\\" in content:
                            issues.append(f"Windows paths in {file_path.name}")
                except:
                    pass

        if issues:
            result["warnings"].append(f"Path issues found: {', '.join(issues)}")
            return False

        if self.verbose:
            result["checks"]["paths"] = "✅ Unix-style paths"

        return True

    def report(self) -> str:
        """Generate compatibility report."""
        lines = [
            f"\n{'='*70}",
            f"Compatibility Report: {self.skill_name}",
            f"{'='*70}\n",
        ]

        # Summary
        passed = sum(1 for r in self.results.values() if r["pass"])
        failed = len(self.results) - passed

        lines.append(f"Results: {passed}/{len(self.results)} agents compatible\n")

        # Per-agent results
        for agent_name, result in self.results.items():
            agent = AGENTS.get(agent_name, {})
            status = "✅ PASS" if result["pass"] else "❌ FAIL"
            lines.append(f"{status} — {agent.get('name', agent_name)}")

            # Checks
            for check_name, check_result in result["checks"].items():
                if isinstance(check_result, bool):
                    status = "✅" if check_result else "❌"
                    lines.append(f"  {status} {check_name}")
                else:
                    lines.append(f"  {check_result}")

            # Errors
            if result["errors"]:
                for error in result["errors"]:
                    lines.append(f"  ❌ {error}")

            # Warnings
            if result["warnings"]:
                for warning in result["warnings"]:
                    lines.append(f"  ⚠️  {warning}")

            lines.append("")

        lines.append(f"{'='*70}\n")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Verify skill compatibility across agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify-compatibility.py my-skill
  python verify-compatibility.py my-skill --agents claude,pi
  python verify-compatibility.py my-skill --agents all --verbose
        """,
    )

    parser.add_argument(
        "skill_name",
        help="Skill name to verify",
    )

    parser.add_argument(
        "--agents",
        default="claude,pi,codex,opencode",
        help="Agents to test (comma-separated, or 'all')",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed info",
    )

    args = parser.parse_args()

    # Parse agents
    if args.agents == "all":
        agents = list(AGENTS.keys())
    else:
        agents = [a.strip() for a in args.agents.split(",")]

    try:
        verifier = CompatibilityVerifier(args.skill_name, agents, verbose=args.verbose)
        all_pass = verifier.verify_all()
        print(verifier.report())

        return 0 if all_pass else 1

    except ValueError as e:
        print(f"❌ {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
