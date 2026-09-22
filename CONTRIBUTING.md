# Contributing

This repository is a curated collection of Agent Skills. The rules below
exist to keep `skills_master/` trustworthy as the canonical, production
source — see the "Source of Truth & Directory Lifecycle" section of the
[README](README.md#source-of-truth--directory-lifecycle) for what each
directory is for before you start.

## Adding a new skill

```bash
mkdir skills_devtesting/my-new-skill
cat > skills_devtesting/my-new-skill/SKILL.md << 'EOF'
---
name: my-new-skill
description: What this skill does and when to use it.
---
# My New Skill
## Instructions
...
EOF
```

1. Develop and test it locally in `skills_devtesting/`.
2. Validate it:
   ```bash
   python SkillsFramework/scripts/validate_skills.py --verbose
   ```
3. Move it to `skills_staging/` for review, then promote it to
   `skills_master/` with `SkillsFramework/scripts/promote-skill-production.py`.

## Skill metadata requirements

Every `SKILL.md` needs YAML frontmatter that validates against
[`schema/skill.schema.json`](schema/skill.schema.json). At minimum:

```yaml
---
name: skill-name
description: What this skill does and when to use it.
---
```

- `name`: kebab-case, matches the directory name exactly.
- `description`: third person, states both what the skill does and when to
  use it, ≤1024 characters.

Optional fields (`version`, `status`, `risk`, `permissions`, `category`,
`tags`, `requires_confirmation`, ...) are documented in the schema. Use
`risk: high` and `requires_confirmation: true` for any skill whose
instructions involve destructive actions, credentials, or infrastructure
changes — see [SECURITY.md](SECURITY.md).

## Before opening a pull request

Run the same check CI runs:

```bash
pip install pyyaml
python SkillsFramework/scripts/validate_skills.py --verbose
```

A pull request is expected to pass:

- `validate_skills.py` — schema-valid frontmatter, unique names within each
  tier, no obvious committed secrets.
- The gitleaks secret scan in CI.

## Regenerating generated files

Never hand-edit `skills.json`, `docs/catalogue.md`, or anything under
`skills_conversions/`. Regenerate them instead:

```bash
python SkillsFramework/scripts/generate-skill-index.py --format json --output skills.json
python SkillsFramework/scripts/generate-skill-index.py --format markdown --output docs/catalogue.md
./SkillsFramework/package-skills.sh
```

## Reporting issues

Use GitHub Issues for bugs and skill requests. Do not include real
credentials, private infrastructure details, or personal data in an issue —
see [SECURITY.md](SECURITY.md).
