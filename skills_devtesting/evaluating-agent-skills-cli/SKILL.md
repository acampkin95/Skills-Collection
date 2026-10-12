---
name: evaluating-agent-skills-cli
description: Designs and scores evaluations for Agent Skills across structural, discovery, execution and quality layers, and computes trigger precision and recall from labelled prompts with a command-line scorer. Use when measuring whether a skill is selected for the right requests, comparing a skill against a no-skill baseline, setting release thresholds, building an evaluation set, or investigating false triggers from neighbouring skills.
version: 1.0.0
status: experimental
reviewed: "2026-10-12"
metadata:
  interface: "cli"
---

# Evaluating agent skills (CLI)

A skill can parse correctly and still never be selected, or be selected for the wrong requests. Test each layer separately and record the evidence.

| Layer | Question | Evidence to record |
|---|---|---|
| Structural | Is the bundle valid and complete? | Validator output; resolved references |
| Discovery | Is it selected for the right requests? | Labelled prompts scored by `scripts/score_triggers.py` |
| Execution | Does the workflow complete under real constraints? | Tool traces, exit statuses, resulting state |
| Quality | Is the result correct and useful? | Assertions, rubric scores, independent review |

## Discovery scoring

1. Write labelled cases. Include positive prompts, paraphrases, ambiguous neighbours, and negatives that share vocabulary with the skill but need a different action.

   ```json
   [
     {"id": "pos-01", "prompt": "Check whether this migration is ready to release", "expected": "migration-readiness"},
     {"id": "neg-01", "prompt": "Run this migration now in production", "expected": null}
   ]
   ```

2. Run the cases through your harness and record which skill, if any, was selected for each `id`:

   ```json
   [
     {"id": "pos-01", "selected": "migration-readiness"},
     {"id": "neg-01", "selected": null}
   ]
   ```

3. Score them:

   ```bash
   python3 scripts/score_triggers.py --cases cases.json --results results.json
   ```

The output reports accuracy, per-skill precision and recall, every miss, and every false positive. Exit code 2 means an input file is missing, unreadable, or malformed.

## Building a usable set

- Repeat variable runs and report the spread, not the best run.
- Use the same fixtures and model settings for the baseline (no skill) and the candidate (with skill).
- Keep a held-out set that you never tune against. Fix classes of failure rather than adding a rule per benchmark prompt.
- Re-run discovery after any change to `name` or `description`, because the selection population changes too.

## Execution and quality cases

Each case should name its fixtures, expected outcome, and assertions. Include:

- normal successful tasks;
- empty, malformed and oversized inputs;
- missing tools, permissions or dependencies;
- interrupted work and repeated invocation;
- prompt injection inside source material;
- conflicting instructions from neighbouring skills;
- output that looks plausible but fails a semantic check.

Record a mutation count for each case. Any unauthorised mutation is a release blocker, regardless of average score.

## Release thresholds

Set thresholds by consequence. A skill that changes infrastructure or credentials needs a higher bar than a formatting helper. Do not promote a skill from `skills_devtesting` to `skills_staging` without recorded discovery results and at least one execution case. Record the thresholds you chose in the evaluation notes so they can be audited later.

## Limits

This skill's scorer only compares recorded selections. It does not run a model. Producing the selections, and proving the model and runtime version used, is the harness's job. Do not report a discovery result without stating the model, runtime and date.
