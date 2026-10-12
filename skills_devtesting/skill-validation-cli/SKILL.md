---
name: skill-validation-cli
description: Runs the repository skill validator (SkillsFramework/scripts/validate_skills.py) to check SKILL.md frontmatter, names, descriptions, relative links, Python and shell script syntax, and secret-shaped strings across skill tiers. Use when validating a new or edited skill, fixing skill validation errors, running the skill CI check locally, or deciding whether a skill is ready to promote from devtesting to staging or master.
version: 1.0.0
status: experimental
reviewed: "2026-10-12"
metadata:
  interface: "cli"
---

# Skill validation (CLI)

Checks every skill directory directly under `skills_master/`, `skills_staging/` and `skills_devtesting/`. It is the same check CI runs on pull requests.

## Quick start

Run from the repository root:

```bash
python3 SkillsFramework/scripts/validate_skills.py            # errors only
python3 SkillsFramework/scripts/validate_skills.py --verbose  # errors and warnings
python3 SkillsFramework/scripts/validate_skills.py --strict   # warnings fail too
python3 SkillsFramework/scripts/validate_skills.py --json     # summary line for tooling
```

Install the only dependency with `pip install pyyaml`.

## Reading the output

- `[ERROR]` lines always fail the run (exit code 1).
- `[WARN]` lines are shown with `--verbose`; `--strict` turns them into failures.
- The summary reports discovered skills per tier and the number of nested `SKILL.md` copies.
- Exit code 2 means the schema file is missing or unreadable.

To check one skill, filter the output by its path:

```bash
python3 SkillsFramework/scripts/validate_skills.py --verbose | grep "skills_devtesting/my-skill/"
```

## Fixing common findings

| Finding | Fix |
|---|---|
| `name ... does not match folder` | Make the `name:` value equal the directory name exactly. |
| `name contains reserved word 'claude'` or `'anthropic'` | Rename the skill. API and claude.ai uploads reject these words. |
| `description ... over 1024 characters` | Shorten to what the skill does and when to use it. Keep the trigger phrases. |
| `description contains XML-like tags` | Write the component or tag name in plain words. |
| `broken relative link` | Point the link at a file that exists, or replace it with plain text if the file is not bundled. |
| `python syntax error` / `shell syntax error` | Fix the reported line. The validator compiles scripts without running them. |
| `possible ... found in file content` | Replace the value with an obvious placeholder. Rotate the credential if it was real. |
| `description is not third person` | Rewrite starting with the skill's capability rather than "I" or "You". |
| `description has no trigger phrase` | Add the words a user would say, for example "Use when ...". |
| `Claude Code-only field` | Remove it from the portable source, or keep it in a Claude Code adapter. |
| `nested SKILL.md is not discovered` | Claude Code does not load nested skills. Move the content to a top-level skill or to `references/`. |
| `metadata.interface is 'cli' but name lacks '-cli'` | Rename the skill so it ends in `-cli`, or remove the interface marker. |

## What it does not check

The validator checks structure and syntax. It does not check whether a skill triggers for the right requests or whether its instructions work. Use `evaluating-agent-skills-cli` for trigger precision and recall and for execution tests.

## Related

- Authoring rules: `docs/authoring/advanced-skill-development.md` in the repository.
- Schema: `schema/skill.schema.json`.
