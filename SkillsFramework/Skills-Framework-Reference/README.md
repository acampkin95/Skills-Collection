# skills-ref

Reference library for Agent Skills.

> **Note:** This library is intended for demonstration purposes only. It is not meant to be used in production.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Agent Prompt Integration](#agent-prompt-integration)
- [Creating a Skill](#creating-a-skill)
- [Testing Skills](#testing-skills)
- [Versioning](#versioning)
- [JSON Schema](#json-schema)
- [License](#license)

## Installation

### macOS / Linux

Using pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Or using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
source .venv/bin/activate
```

### Windows

Using pip (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

Using pip (Command Prompt):

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .
```

Or using [uv](https://docs.astral.sh/uv/):

```powershell
uv sync
.venv\Scripts\Activate.ps1
```

After installation, the `skills-ref` executable will be available on your `PATH` (within the activated virtual environment).

## Usage

### CLI

```bash
# Validate a skill
skills-ref validate path/to/skill

# Read skill properties (outputs JSON)
skills-ref read-properties path/to/skill

# Generate <available_skills> XML for agent prompts
skills-ref to-prompt path/to/skill-a path/to/skill-b
```

### Python API

```python
from pathlib import Path
from skills_ref import validate, read_properties, to_prompt

# Validate a skill directory
problems = validate(Path("my-skill"))
if problems:
    print("Validation errors:", problems)

# Read skill properties
props = read_properties(Path("my-skill"))
print(f"Skill: {props.name} - {props.description}")

# Generate prompt for available skills
prompt = to_prompt([Path("skill-a"), Path("skill-b")])
print(prompt)
```

## Agent Prompt Integration

Use `to-prompt` to generate the suggested `<available_skills>` XML block for your agent's system prompt. This format is recommended for Anthropic's models, but Skill Clients may choose to format it differently based on the model being used.

```xml
<available_skills>
<skill>
<name>
my-skill
</name>
<description>
What this skill does and when to use it
</description>
<location>
/path/to/my-skill/SKILL.md
</location>
</skill>
</available_skills>
```

The `<location>` element tells the agent where to find the full skill instructions.

## Creating a Skill

Skills are self-contained packages with a `SKILL.md` file at minimum. The frontmatter defines metadata, and the markdown body contains instructions.

### Minimum Structure

```
my-skill/
└── SKILL.md
```

### Complete Example with Bundled Resources

```
my-skill/
├── SKILL.md              # Required: skill metadata and instructions
├── scripts/              # Optional: executable code (Python, Bash, JavaScript)
│   ├── helper.py
│   └── setup.sh
├── references/           # Optional: documentation loaded into context
│   └── api-docs.md
└── assets/               # Optional: static files (templates, config, images)
    └── template.json
```

### SKILL.md Format

```yaml
---
name: my-skill-name           # Required: 1-64 chars, kebab-case, matches directory
description: A clear description of what the skill does and when to use it  # Required: 1-1024 chars
version: "1.0.0"              # Optional: skill format version (recommended)
license: MIT                  # Optional: license identifier
compatibility: Requires Python 3.11+  # Optional: 1-500 chars
allowed-tools: Bash(jq:*) Bash(git:*)  # Optional: tool patterns required
metadata:                     # Optional: arbitrary key-value pairs
  author: Your Name
  category: development
---
# My Skill Name

Introduction and overview of what this skill does.

## When to Use

- Use this skill when you need to...
- This skill is appropriate for...

## Guidelines

- Follow these rules when using the skill
- Keep instructions clear and actionable
- Provide examples where helpful

## Examples

```python
# Example usage
result = helper_function()
```

## Limitations

- Known limitations or edge cases
- What this skill cannot do
```

### Field Reference

| Field | Required | Length | Validation |
|-------|----------|--------|------------|
| `name` | Yes | 1-64 chars | lowercase, kebab-case, matches directory |
| `description` | Yes | 1-1024 chars | plain text description |
| `version` | No | - | Semantic versioning recommended |
| `license` | No | - | SPDX identifier |
| `compatibility` | No | 1-500 chars | Human-readable requirements |
| `allowed-tools` | No | - | Tool patterns (experimental) |
| `metadata` | No | - | Arbitrary key-value pairs |

### Example: Simple Skill

**`hello-world/SKILL.md`**
```yaml
---
name: hello-world
description: Responds with a friendly greeting
---
# Hello World Skill

A simple skill that demonstrates basic structure.

## When to Use

When the user asks for a greeting or wants to test skill functionality.

## Response Format

Respond with a friendly greeting including the user's name if provided.

## Examples

- User: "Say hello" → Response: "Hello there!"
- User: "Hello, Alice" → Response: "Hello, Alice! Nice to meet you!"
```

### Example: Complex Skill with Scripts

**`data-processor/SKILL.md`**
```yaml
---
name: data-processor
description: Processes and transforms CSV data files
compatibility: Requires Python 3.9+ with pandas
allowed-tools: Bash(python:*) Read(.*)
metadata:
  author: Data Team
  version: "2.1.0"
---
# Data Processor Skill

Process, transform, and analyze CSV data files.

## When to Use

- Loading and parsing CSV files
- Data cleaning and transformation
- Generating summary statistics
- Exporting data to different formats

## Guidelines

1. Always validate input files exist before processing
2. Handle missing values gracefully
3. Report processing errors clearly
4. Use pandas for efficient data operations

## Available Operations

- `load_csv(path)` - Load a CSV file into a DataFrame
- `clean_data(df)` - Apply standard cleaning transformations
- `summarize(df)` - Generate summary statistics
- `export_csv(df, path)` - Save DataFrame to CSV
- `export_json(df, path)` - Save DataFrame to JSON

## Error Handling

- File not found: "Error: File not found at {path}"
- Parse error: "Error: Could not parse CSV - {details}"
- Processing error: "Error during processing - {details}"
```

## Testing Skills

Use the `skills-ref validate` command to ensure your skill meets all requirements.

### Basic Validation

```bash
# Validate a single skill
skills-ref validate path/to/my-skill

# Validate multiple skills
skills-ref validate skill-a/ skill-b/ skill-c/
```

### Integration with Test Frameworks

Create test files to automate skill validation:

**`tests/test_my_skill.py`**
```python
"""Test suite for my-skill."""
from pathlib import Path
from skills_ref import validate, read_properties

SKILL_PATH = Path(__file__).parent.parent / "my-skill"

def test_skill_validates():
    """Skill must pass all validation rules."""
    errors = validate(SKILL_PATH)
    assert errors == [], f"Skill validation failed: {errors}"

def test_skill_has_required_fields():
    """Skill must have name and description."""
    props = read_properties(SKILL_PATH)
    assert props.name == "my-skill"
    assert len(props.description) > 0

def test_skill_description_length():
    """Description must be within limits."""
    props = read_properties(SKILL_PATH)
    assert len(props.description) <= 1024
```

### Running Tests

```bash
# Run skill-specific tests
pytest tests/test_my_skill.py -v

# Run all skill validations
pytest tests/ -v

# CI/CD integration
if errors := validate(SKILL_PATH):
    print(f"::error::Skill validation failed: {errors}")
    exit(1)
```

### Test Patterns

| Pattern | Purpose | Example |
|---------|---------|---------|
| Validation test | Ensure skill meets format requirements | `assert validate(skill) == []` |
| Properties test | Verify metadata fields | `assert props.name == expected` |
| Content test | Check instruction quality | `assert "## Examples" in content` |
| Integration test | Test with actual agent use | Simulate skill activation |

### Continuous Integration

**`.github/workflows/validate-skills.yml`**
```yaml
name: Validate Skills
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install skills-ref
        run: pip install -e .
      - name: Validate all skills
        run: |
          for skill in skills/*/; do
            errors=$(skills-ref validate "$skill")
            if [ -n "$errors" ]; then
              echo "::error title=Validation failed::$skill: $errors"
              exit 1
            fi
          done
```

## Versioning

The skill format uses semantic versioning. The `version` field in frontmatter indicates the SKILL.md format version, not your skill's functional version.

### Format Versions

| Version | Status | Description |
|---------|--------|-------------|
| `1.0.0` | Current | Initial specification |
| `1.1.0` | Planned | Additional frontmatter fields |

### Version Field

Include a version field for future compatibility:

```yaml
---
name: my-skill
description: A clear description
version: "1.0.0"  # SKILL.md format version
---
```

### Backward Compatibility

- Skills without a `version` field are assumed to be `1.0.0`
- New optional fields are added without breaking existing skills
- Required fields remain required in all `1.x` versions
- Breaking changes require a `2.0.0` version increment

### Deprecation Policy

- Features are deprecated with warnings for at least 6 months
- Removed features are documented with migration guides
- Major version bumps indicate breaking changes

### Migration Guide

**Migrating from 1.0.0 to 1.1.0 (when available)**

1. Add `version: "1.1.0"` to frontmatter
2. Review new optional fields for applicability
3. Update documentation as needed
4. Run `skills-ref validate` to verify

## JSON Schema

A JSON Schema is available for editor integration and validation:

**`schema/skill-properties.json`**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Skill Properties",
  "description": "Frontmatter properties for a SKILL.md file",
  "type": "object",
  "required": ["name", "description"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9]*(-[a-z0-9]+)*$",
      "minLength": 1,
      "maxLength": 64,
      "description": "Skill name in kebab-case"
    },
    "description": {
      "type": "string",
      "minLength": 1,
      "maxLength": 1024,
      "description": "What the skill does and when to use it"
    },
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "SKILL.md format version (semantic versioning)"
    },
    "license": {
      "type": "string",
      "description": "SPDX license identifier"
    },
    "compatibility": {
      "type": "string",
      "maxLength": 500,
      "description": "Compatibility requirements"
    },
    "allowed-tools": {
      "type": "string",
      "description": "Tool patterns required by the skill"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": { "type": "string" },
      "description": "Arbitrary key-value pairs"
    }
  }
}
```

### Using JSON Schema

**VS Code configuration (`.vscode/settings.json`)**
```json
{
  "yaml.schemas": {
    "schema/skill-properties.json": "**/SKILL.md"
  }
}
```

**Python validation with jsonschema**
```python
from jsonschema import validate, ValidationError
import json

schema = json.load(open("schema/skill-properties.json"))

# Validate frontmatter
try:
    validate(instance=frontmatter, schema=schema)
    print("Valid!")
except ValidationError as e:
    print(f"Invalid: {e.message}")
```

### Schema Validation vs skills-ref

| Aspect | JSON Schema | skills-ref validate |
|--------|-------------|---------------------|
| Frontmatter validation | Yes | Yes |
| Directory name matching | No | Yes |
| File existence check | No | Yes |
| Editor integration | Yes | No |
| CLI convenience | No | Yes |

Use both for comprehensive validation: JSON Schema during editing, `skills-ref validate` before commit.

Apache 2.0
