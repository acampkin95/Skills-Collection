#!/usr/bin/env python3
"""Batch cleanup of skill frontmatter to meet Claude Code framework spec.
Keeps only `name` and `description` in YAML frontmatter.
Cleans aggressive "ALWAYS USE" language from descriptions.
"""

import os
import re
import yaml
import sys

SKILLS_DIR = "/sessions/dazzling-relaxed-babbage/mnt/skills"
SKIP = {"learned", "logs", "cleanup_skills.py"}
# Skills already cleaned in previous pass
ALREADY_DONE = {"deepinfra-ocr", "biome-linting", "bun-runtime", "clerk", "sonar-scanner"}

def parse_skill(path):
    """Parse SKILL.md into frontmatter dict and body string."""
    with open(path, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        return None, content

    # Find second ---
    end = content.index('---', 3)
    fm_raw = content[3:end].strip()
    body = content[end+3:].lstrip('\n')

    try:
        fm = yaml.safe_load(fm_raw)
    except:
        return None, content

    return fm, body

def clean_description(desc):
    """Clean aggressive trigger language from description."""
    if not desc:
        return desc

    # Normalize whitespace
    desc = ' '.join(desc.split())

    # Replace "ALWAYS USE THIS SKILL when any of the following appear:" patterns
    patterns = [
        r'ALWAYS USE THIS SKILL when any of the following appear:\s*',
        r'ALWAYS USE THIS SKILL when:\s*',
        r'ALWAYS USE THIS SKILL when\s+',
        r'Also triggers on:\s*',
    ]

    for p in patterns:
        desc = re.sub(p, 'Use this skill when ', desc, flags=re.IGNORECASE)

    # Clean up double "Use this skill when Use this skill when"
    desc = re.sub(r'(Use this skill when\s*){2,}', 'Use this skill when ', desc)

    # Clean up quoted trigger lists like "implement authentication", "clerk integration"
    # Convert them to natural language
    desc = re.sub(r'"([^"]+)"(?:,\s*)?', r'\1, ', desc)

    # Clean trailing commas and periods
    desc = re.sub(r',\s*\.', '.', desc)
    desc = re.sub(r',\s*$', '.', desc)
    desc = re.sub(r'\.\s*\.', '.', desc)

    # Trim
    desc = desc.strip()
    if not desc.endswith('.'):
        desc += '.'

    return desc

def rebuild_frontmatter(fm):
    """Build clean YAML frontmatter with only name and description."""
    name = fm.get('name', '')
    desc = fm.get('description', '')

    if isinstance(desc, str):
        desc = clean_description(desc)

    # Build manually to avoid yaml.dump formatting issues
    lines = ['---']
    lines.append(f'name: {name}')
    lines.append(f'description: {desc}')
    lines.append('---')

    return '\n'.join(lines)

def process_skill(skill_dir):
    """Process a single skill directory."""
    skill_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_path):
        return None

    fm, body = parse_skill(skill_path)
    if fm is None:
        return "SKIP: no valid frontmatter"

    # Check if already clean (only name and description)
    extra_keys = set(fm.keys()) - {'name', 'description'}
    needs_desc_clean = False
    desc = fm.get('description', '')
    if isinstance(desc, str) and 'ALWAYS USE' in desc.upper():
        needs_desc_clean = True

    if not extra_keys and not needs_desc_clean:
        return "CLEAN: already compliant"

    # Rebuild
    new_fm = rebuild_frontmatter(fm)
    new_content = new_fm + '\n\n' + body

    with open(skill_path, 'w') as f:
        f.write(new_content)

    changes = []
    if extra_keys:
        changes.append(f"removed: {', '.join(sorted(extra_keys))}")
    if needs_desc_clean:
        changes.append("cleaned description")

    return f"FIXED: {'; '.join(changes)}"

def main():
    results = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        if entry in SKIP:
            continue
        if entry in ALREADY_DONE:
            results.append((entry, "SKIP: already updated"))
            continue

        full = os.path.join(SKILLS_DIR, entry)
        if not os.path.isdir(full):
            continue

        result = process_skill(full)
        if result:
            results.append((entry, result))

    # Print report
    print(f"\n{'='*60}")
    print(f"Skill Cleanup Report")
    print(f"{'='*60}\n")

    fixed = 0
    clean = 0
    skipped = 0

    for name, status in results:
        icon = "✅" if "FIXED" in status else "⏭️" if "SKIP" in status else "✓" if "CLEAN" in status else "⚠️"
        print(f"  {icon} {name:40s} {status}")
        if "FIXED" in status:
            fixed += 1
        elif "CLEAN" in status:
            clean += 1
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"  Fixed: {fixed} | Already clean: {clean} | Skipped: {skipped}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
