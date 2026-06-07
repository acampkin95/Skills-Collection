#!/usr/bin/env python3
"""
oui-sync.py — Convert skills_master skills to Open WebUI and upload to AI01.

Reads skills from skills_master/, converts SKILL.md format to Open WebUI's
SkillForm format, validates, and uploads via the /api/v1/skills REST API.

Usage:
    # Dry run — validate and show what would happen
    python3 oui-sync.py --dry-run

    # Sync all skills (create new, update changed, skip unchanged)
    python3 oui-sync.py

    # Sync specific skills only
    python3 oui-sync.py --skills firecrawl,critical-thinking,structured-thinking

    # Delete skills on OUI that don't exist in skills_master
    python3 oui-sync.py --prune

    # Export skills to JSON files (no upload)
    python3 oui-sync.py --export-dir /tmp/oui-skills

Requirements:
    - OWUI_URL env var (e.g. export OWUI_URL=http://your-openwebui:3000)
    - OWUI_API_KEY env var (e.g. sk-...)
    - requests library (pip install requests)
    - PyYAML library (pip install pyyaml)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests
import yaml

# Fix #8: Regex-based frontmatter parsing (avoids matching --- inside YAML values)


# ─── Configuration ───────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_MASTER = REPO_ROOT / "skills_master"

# Open WebUI connection — Fix #3: no hardcoded IP default
OWUI_URL = os.environ.get("OWUI_URL", "")
OWUI_API_KEY = os.environ.get("OWUI_API_KEY", "")

# Skills to skip (CLI-only, agent-specific, not useful in OUI)
SKIP_SKILLS = {
    # CLI/agent-specific skills that don't apply to OUI chat
    "claude-code",       # Claude Code CLI specific
    "crewai-setup",      # CLI framework setup
    "sftp",              # CLI file transfer
    "proxmox-admin",     # Server admin CLI
    "ovhcloud-dedicated",  # API admin
    "open-webui-admin",  # Self-referential
    "cloudapi",          # Alias only
}

# Fix #5: no content limit — OUI stores in PostgreSQL TEXT (unlimited)


# ─── Skill Conversion ────────────────────────────────────────────────────────

def parse_skill_md(skill_path: Path) -> Optional[dict]:
    """Parse a SKILL.md file into structured data."""
    try:  # Fix #6: wrap file I/O in try/except
        content = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    except (OSError, PermissionError) as e:
        print(f"  ⚠ Cannot read {skill_path.name}/SKILL.md: {e}")
        return None

    # Fix #8: regex-based frontmatter parsing
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?', content, re.DOTALL)
    if not m:
        return None

    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None

    if not fm or "name" not in fm:
        return None

    # Body is everything after the second ---
    body_end = m.end()
    body = content[body_end:].strip() if body_end < len(content) else ""

    # Merge references/ content into body for OUI (it's a single content field)
    refs_dir = skill_path / "references"
    if refs_dir.is_dir():
        ref_parts = []
        for ref_file in sorted(refs_dir.glob("*.md")):
            try:  # Fix #6: wrap ref file reads too
                ref_content = ref_file.read_text(encoding="utf-8").strip()
            except (OSError, PermissionError):
                continue
            if ref_content:
                ref_parts.append(f"\n\n---\n\n## {ref_file.stem.replace('-', ' ').title()}\n\n{ref_content}")
        if ref_parts:
            body += "".join(ref_parts)

    # Fix #5: no truncation — upload full content

    return {
        "name": fm["name"],
        "description": fm.get("description", ""),
        "version": fm.get("version", ""),
        "reviewed": fm.get("reviewed", ""),
        "content": body,
    }


def convert_to_oui(skill_data: dict) -> dict:
    """Convert a skills_master skill to Open WebUI SkillForm format.

    OUI SkillForm:
        id: str          — slug-based ID (lowercase, hyphens)
        name: str        — display name
        description: str — trigger description
        content: str     — full skill content (markdown)
        meta: dict       — {tags: [...]}
        is_active: bool
    """
    name = skill_data["name"]

    # Generate stable ID from name (OUI uses name as slug)
    skill_id = name.lower().replace(" ", "-").replace("_", "-")
    # Remove any non-alphanumeric except hyphens
    skill_id = re.sub(r"[^a-z0-9-]", "", skill_id)

    return {
        "id": skill_id,
        "name": name,
        "description": skill_data["description"],
        "content": skill_data["content"],
        "meta": {"tags": []},
        "is_active": True,
    }


def _content_hash(content: str) -> str:
    """Stable hash of content for change detection."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


# ─── Validation ──────────────────────────────────────────────────────────────

def validate_oui_skill(skill: dict) -> list[str]:
    """Validate an OUI skill before upload. Returns list of issues."""
    issues = []

    if not skill["id"]:
        issues.append("Missing id")
    if not skill["name"]:
        issues.append("Missing name")
    if not skill["description"]:
        issues.append("Missing description")
    if not skill["content"]:
        issues.append("Missing content")

    if len(skill["description"]) > 500:
        issues.append(f"Description too long ({len(skill['description'])} chars, max 500)")

    return issues


# ─── Open WebUI API Client ───────────────────────────────────────────────────

class OWUIClient:
    """Minimal client for Open WebUI Skills API."""

    def __init__(self, url: str, api_key: str, timeout: int = 30):
        self.url = url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        r = requests.request(
            method,
            f"{self.url}{path}",
            headers=self.headers,
            timeout=self.timeout,
            **kwargs,
        )
        return r

    def list_skills(self) -> list[dict]:
        r = self._request("GET", "/api/v1/skills/")
        r.raise_for_status()
        return r.json()

    def get_skill(self, skill_id: str) -> Optional[dict]:
        r = self._request("GET", f"/api/v1/skills/id/{skill_id}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def create_skill(self, skill: dict) -> dict:
        r = self._request("POST", "/api/v1/skills/create", json=skill)
        r.raise_for_status()
        return r.json()

    def update_skill(self, skill_id: str, skill: dict) -> dict:
        r = self._request("POST", f"/api/v1/skills/id/{skill_id}/update", json=skill)
        r.raise_for_status()
        return r.json()

    def delete_skill(self, skill_id: str) -> bool:
        r = self._request("DELETE", f"/api/v1/skills/id/{skill_id}/delete")
        r.raise_for_status()
        return r.json()

    def health(self) -> bool:
        try:
            r = requests.get(f"{self.url}/health", timeout=5)
            return r.json().get("status", False)
        except Exception:
            return False


# ─── Main Sync Logic ─────────────────────────────────────────────────────────

def discover_skills(skills_filter: Optional[list[str]] = None) -> list[Path]:
    """Find all skill directories in skills_master."""
    skills = []
    for d in sorted(SKILLS_MASTER.iterdir()):
        if not d.is_dir():
            continue
        if d.name.startswith("."):
            continue
        if (d / "SKILL.md").exists():
            if skills_filter and d.name not in skills_filter:
                continue
            skills.append(d)
    return skills


def sync(
    dry_run: bool = False,
    prune: bool = False,
    skills_filter: Optional[list[str]] = None,
    export_dir: Optional[str] = None,
):
    """Main sync function."""
    # Discover local skills
    local_skills = discover_skills(skills_filter)
    print(f"Discovered {len(local_skills)} skills in skills_master")

    # Parse and convert
    converted = []
    skipped = []
    for sp in local_skills:
        parsed = parse_skill_md(sp)
        if not parsed:
            print(f"  ⚠ Could not parse: {sp.name}")
            continue

        if sp.name in SKIP_SKILLS:
            skipped.append(sp.name)
            continue

        oui = convert_to_oui(parsed)
        issues = validate_oui_skill(oui)
        if issues:
            print(f"  ⚠ Validation issues for {sp.name}: {', '.join(issues)}")
            continue

        converted.append({**oui, "_path": sp})

    print(f"Converted: {len(converted)}, Skipped: {len(skipped)} ({', '.join(skipped) if skipped else 'none'})")

    # Export mode — just write JSON files
    if export_dir:
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        for s in converted:
            out = export_path / f"{s['id']}.json"
            payload = {k: v for k, v in s.items() if not k.startswith("_")}
            out.write_text(json.dumps(payload, indent=2))
            print(f"  📄 Exported: {s['name']} → {out}")
        print(f"\nExported {len(converted)} skills to {export_dir}")
        return

    # Fix #3: require OWUI_URL
    if not OWUI_URL:
        print("ERROR: OWUI_URL env var not set (e.g. http://host:3000)", file=sys.stderr)
        sys.exit(1)

    if not OWUI_API_KEY:
        print("ERROR: OWUI_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    client = OWUIClient(OWUI_URL, OWUI_API_KEY)

    if not client.health():
        print(f"ERROR: Cannot reach Open WebUI at {OWUI_URL}", file=sys.stderr)
        sys.exit(1)

    print(f"Connected to Open WebUI at {OWUI_URL}")

    # Fix #1: --prune + --skills guard
    if prune and skills_filter:
        print("ERROR: --prune and --skills cannot be used together (would delete unfiltered skills)", file=sys.stderr)
        sys.exit(1)

    # Get existing skills
    try:
        remote_skills = client.list_skills()
    except Exception as e:
        print(f"ERROR: Failed to list remote skills: {e}", file=sys.stderr)
        sys.exit(1)

    remote_map = {s["name"]: s for s in remote_skills}
    print(f"Remote skills: {len(remote_map)}")

    # Sync
    created = 0
    updated = 0
    unchanged = 0
    errors = []
    auth_failed = False

    for skill in converted:
        if auth_failed:  # Fix #7: short-circuit on auth failure
            break

        name = skill["name"]
        payload = {k: v for k, v in skill.items() if not k.startswith("_")}

        if name in remote_map:
            # Fix #2: real change detection via get_skill
            remote = remote_map[name]
            if dry_run:
                print(f"  🔄 Would update: {name}")
                updated += 1
            else:
                try:
                    # Fetch full skill to compare content
                    remote_full = client.get_skill(remote["id"])
                    if remote_full and _content_hash(remote_full.get("content", "")) == _content_hash(payload["content"]):
                        unchanged += 1
                        continue
                    client.update_skill(remote["id"], payload)
                    print(f"  🔄 Updated: {name}")
                    updated += 1
                except requests.exceptions.HTTPError as e:
                    if e.response is not None and e.response.status_code in (401, 403):
                        print(f"  🚫 Auth failed: {e.response.status_code}. Aborting.")
                        auth_failed = True
                        errors.append(f"auth:{e.response.status_code}")
                    else:
                        print(f"  ❌ Failed to update {name}: {e}")
                        errors.append(f"update:{name}:{e}")
        else:
            # New skill — create
            if dry_run:
                print(f"  ✨ Would create: {name}")
                created += 1
            else:
                try:
                    client.create_skill(payload)
                    print(f"  ✨ Created: {name}")
                    created += 1
                except requests.exceptions.HTTPError as e:
                    if e.response is not None and e.response.status_code in (401, 403):
                        print(f"  🚫 Auth failed: {e.response.status_code}. Aborting.")
                        auth_failed = True
                        errors.append(f"auth:{e.response.status_code}")
                    else:
                        print(f"  ❌ Failed to create {name}: {e}")
                        errors.append(f"create:{name}:{e}")

    # Prune remote skills not in local
    if prune and not auth_failed:
        local_names = {s["name"] for s in converted}
        for name, remote in remote_map.items():
            if name not in local_names:
                if dry_run:
                    print(f"  🗑️ Would delete: {name}")
                else:
                    try:
                        client.delete_skill(remote["id"])
                        print(f"  🗑️ Deleted: {name}")
                    except Exception as e:
                        print(f"  ❌ Failed to delete {name}: {e}")
                        errors.append(f"delete:{name}:{e}")

    # Summary
    print(f"\n{'DRY RUN — ' if dry_run else ''}Sync Results:")
    print(f"  Created:   {created}")
    print(f"  Updated:   {updated}")
    print(f"  Unchanged: {unchanged}")
    if prune:
        print(f"  Pruned:    see above")
    if errors:
        print(f"  Errors:    {len(errors)}")
        for e in errors:
            print(f"    {e}")
    else:
        print(f"  ✅ No errors")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert skills_master to Open WebUI skills and upload to AI01"
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and show changes without uploading")
    parser.add_argument("--prune", action="store_true", help="Delete remote skills not in skills_master")
    parser.add_argument("--skills", type=str, help="Comma-separated list of skill names to sync")
    parser.add_argument("--export-dir", type=str, help="Export skills as JSON files instead of uploading")
    parser.add_argument("--url", type=str, default=None, help="Override OWUI_URL")
    args = parser.parse_args()

    global OWUI_URL, OWUI_API_KEY
    if args.url:
        OWUI_URL = args.url

    skills_filter = [s.strip() for s in args.skills.split(",")] if args.skills else None

    sync(
        dry_run=args.dry_run,
        prune=args.prune,
        skills_filter=skills_filter,
        export_dir=args.export_dir,
    )


if __name__ == "__main__":
    main()
