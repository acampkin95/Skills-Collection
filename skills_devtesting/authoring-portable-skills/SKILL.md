---
name: authoring-portable-skills
description: Designs, writes and packages portable Agent Skills, covering scope and design briefs, description engineering for discovery, progressive disclosure into references and scripts, deterministic helpers, and a Claude Code adapter for runtime-only fields. Use when creating a new skill, splitting an oversized SKILL.md, rewriting a skill description that is not triggering, or preparing a skill release.
version: 1.0.0
status: experimental
reviewed: "2026-10-12"
---

# Authoring portable skills

Build the smallest reliable workflow that meets the user's request, then prove it works. Separate three kinds of statement in your notes: documented capability, recommended practice, and local convention.

## 1. Write a design brief first

```yaml
outcome: "<one principal result>"
target_runtime: "<product and tested version>"
inputs:
  required: ["<what must be supplied>"]
  optional: ["<what can be inferred>"]
outputs: ["<artefacts and their format>"]
boundaries:
  permitted: ["<actions the skill may take>"]
  excluded: ["<actions it must not take>"]
failure_policy: "<what to stop, preserve and report>"
```

Split capabilities that have different triggers, permissions or completion conditions into separate skills. Keep steps together when they must share one output contract.

## 2. Write the description for discovery

Use this recipe: name the concrete result, name the objects or formats, add the phrases users actually say, and add a scope exclusion only if a neighbour skill would otherwise collide.

```yaml
description: >-
  Reviews proposed database schema changes and produces a migration readiness
  report. Use when evaluating migrations, checking schema-change risk, or
  preparing a rollout review. Excludes executing production migrations.
```

Write in third person. Keep the description under 1024 characters. Treat it as an interface: a change to it changes which requests select the skill.

## 3. Structure the bundle

```text
my-skill/
  SKILL.md          routing, steps, constraints, completion (keep under 500 lines)
  references/       detail loaded on condition; one level deep from SKILL.md
  scripts/          deterministic checks and transforms; executed, not read
  assets/           templates and fixed resources
```

- Link each reference with a condition: "Read `references/failure-modes.md` if validation fails."
- Put a table of contents at the top of any reference longer than 100 lines.
- Store each schema or fact in one canonical file and link to it. Do not copy it into several skills.
- Use forward slashes in paths.

## 4. Make helper scripts deterministic

- Take explicit inputs; write structured output to stdout and diagnostics to stderr; return meaningful exit codes.
- Validate input before any mutation. Support a dry-run mode for anything consequential.
- Do not interpolate untrusted arguments into shell strings. Pass argument arrays.
- Keep dependencies minimal and list them in the skill.
- Test failure paths, not only the happy path.

## 5. Keep portable and runtime-specific behaviour apart

Upload targets (API and claude.ai) accept only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Claude Code also reads `when_to_use`, `disable-model-invocation`, `user-invocable`, `argument-hint`, `arguments`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths` and `shell`. Keep the portable source free of the Claude Code-only fields. If you need them, keep them in a separate Claude Code adapter and validate both. Do not strip behavioural fields silently and call the result equivalent.

Claude Code also supports substitutions such as `$ARGUMENTS` and `${CLAUDE_SKILL_DIR}` in the body. Do not rely on them in a portable skill.

## 6. Evaluate before you release

Test discovery with positive, paraphrased, ambiguous and negative prompts. Test execution with normal, malformed, oversized and adversarial inputs. Use the `evaluating-agent-skills-cli` skill to score discovery. Record the model and runtime you tested. Never report a skill as production-ready because it packaged successfully.

## 7. Release checklist

- [ ] Name matches folder; no reserved words; description rules met
- [ ] Body under 500 lines or split into references
- [ ] Every referenced file exists
- [ ] Runtime-only fields confined to the adapter
- [ ] Scripts compile and have been run against fixtures
- [ ] No secrets, private fixtures or generated files in the bundle
- [ ] Discovery results and at least one execution case recorded
- [ ] Version bumped; changed triggers, outputs, privileges or runtimes called out as compatibility-sensitive
- [ ] Rollback path: previous tested version kept available

## Reference

This skill condenses the engineering reference kept in the repository at `docs/authoring/advanced-skill-development.md`. The rules needed to act on this skill are written out above, so it does not depend on that file at run time.
