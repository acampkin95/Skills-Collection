---
name: integrating-agent-skills-api
description: Attaches Agent Skills to Claude API requests through code execution and the container.skills parameter, including custom skill versions, upload limits, and pause_turn handling. Use when calling the Claude Messages API with skills, uploading a custom skill bundle, pinning a skill version for production, retrieving generated files, or debugging a skill request that fails or pauses.
version: 1.0.0
status: experimental
reviewed: "2026-10-12"
---

# Integrating Agent Skills with the Claude API

Facts below were checked against the Anthropic skills guide on 2026-10-12. Re-check the page before coding, because limits and endpoints change.

## Verified facts

- Skills attach through the `container` parameter. The code execution tool must be enabled.
- Each skill entry has a required `type` (`anthropic` or `custom`) and `skill_id`, and an optional `version`. Pass `"latest"` to follow the newest version.
- Up to 20 skills per request.
- A custom skill upload must be under 30 MB uncompressed.
- Custom skill IDs start with `skill_`. Custom version IDs start with `skver_`. Retain the IDs the API returns; do not construct them.
- A new version is a complete snapshot. Upload the full file set each time. Files you omit are not carried over, and the `name` in the new `SKILL.md` must match the existing skill.
- Generated files appear as `file_id` values in code execution results. Retrieve metadata with `GET /v1/files/{file_id}` and content with `GET /v1/files/{file_id}/content`.
- `stop_reason: "pause_turn"` means a long skill operation paused. Send the response `content` back as an assistant turn in the same container (`container.id`) and repeat until the stop reason changes. The guide's examples cap this at 10 retries.
- The guide's examples use `anthropic-version: 2023-06-01` and no beta header.

## Request skeleton

```json
{
  "model": "<model id supported by code execution>",
  "max_tokens": 4096,
  "container": {
    "skills": [
      {"type": "anthropic", "skill_id": "pptx", "version": "latest"},
      {"type": "custom", "skill_id": "skill_<returned id>", "version": "latest"}
    ]
  },
  "tools": [{"type": "code_execution_20250825", "name": "code_execution"}],
  "messages": [{"role": "user", "content": "<task>"}]
}
```

Check the model list for code execution before using a model id. The guide does not name a model in its example.

## Procedure

1. Validate the bundle first with `skill-validation-cli` and run the discovery checks in `evaluating-agent-skills-cli`.
2. Upload the complete bundle. Store the returned `skill_id` and `skver_` version ID.
3. For production, pin the tested `skver_` version rather than `"latest"`.
4. Supply only the skills the task needs; each extra entry adds another skill to the request.
5. Keep `container.id` between turns when you need the execution state to persist.
6. Loop on `pause_turn` with a fixed retry cap. Handle every other stop reason explicitly.
7. Download generated files and check their bytes independently before you report them.
8. Log request IDs, skill and version IDs, and stop reasons. Never log credentials.

## Limits of this skill

- The skills guide does not state whether a code execution container can reach the network. Do not design a skill that needs network access at run time unless you test it.
- Do not assume a skill can install packages at run time. Supply dependencies in the bundle or state them as prerequisites.
- SDK method names and wrapper types change between releases. Check the installed SDK before copying code; this skill does not pin one.
