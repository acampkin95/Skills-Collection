```markdown
# Complete Agent Skills Authoring Guide

## 1. Core Architecture

### What are Agent Skills?
Agent Skills are modular, reusable capabilities that extend Claude's functionality. They package instructions, metadata, and optional resources (scripts, templates) that Claude automatically uses when relevant. Unlike prompts (conversation-level instructions for one-off tasks), Skills load on-demand and eliminate the need to repeatedly provide the same guidance across multiple conversations.

### Three-Tier Progressive Disclosure Architecture

| Level | When Loaded | Token Cost | Content |
|-------|------------|------------|---------|
| **Level 1: Metadata** | Always (at startup) | ~100 tokens per Skill | `name` and `description` from YAML frontmatter |
| **Level 2: Instructions** | When Skill is triggered | Under 5k tokens | SKILL.md body with instructions and guidance |
| **Level 3+: Resources** | As needed | Effectively unlimited | Bundled files executed via bash without loading contents into context |

### How Skills Work (The Filesystem Model)
Skills run in a code execution environment where Claude has filesystem access, bash commands, and code execution capabilities. Skills exist as directories on a virtual machine, and Claude interacts with them using bash commands.

**Loading process:**
1. **Startup:** System prompt includes metadata (name + description) from all Skills
2. **User request triggers Skill:** Claude uses bash to read SKILL.md from the filesystem
3. **As needed:** Claude reads additional files (FORMS.md, REFERENCE.md) or executes scripts

**Key benefits of the architecture:**
- **On-demand file access:** Claude reads only needed files; the rest consume zero tokens
- **Efficient script execution:** Script code never enters context; only output consumes tokens
- **No practical limit on bundled content:** Files don't consume context until accessed

---

## 2. Skill Structure Requirements

### YAML Frontmatter
Every Skill requires a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---
# Your Skill Name
## Instructions
[Clear, step-by-step guidance for Claude to follow]
## Examples
[Concrete examples of using this Skill]
```

### Field Requirements

**`name`:**
- Maximum 64 characters
- Must contain only lowercase letters, numbers, and hyphens
- Cannot contain XML tags
- Cannot contain reserved words: "anthropic", "claude"

**`description`:**
- Must be non-empty
- Maximum 1024 characters
- Cannot contain XML tags
- Should describe both what the Skill does and when to use it

### Required Beta Headers (API)
- `code-execution-2025-08-25` - Skills run in the code execution container
- `skills-2025-10-02` - Enables Skills functionality
- `files-api-2025-04-14` - Required for uploading/downloading files

---

## 3. Core Authoring Principles

### Principle 1: Concise is Key
**Default assumption:** Claude is already very smart. Only add context Claude doesn't already have.

Challenge each piece of information:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

**Good example (~50 tokens):**
```markdown
## Extract PDF text
Use pdfplumber for text extraction:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

**Bad example (~150 tokens):**
```markdown
## Extract PDF text
PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but
pdfplumber is recommended because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...
```

### Principle 2: Set Appropriate Degrees of Freedom

| Freedom Level | When to Use | How to Write | Example |
|--------------|-------------|--------------|---------|
| **High** (text instructions) | Multiple approaches valid, decisions depend on context | Give general direction, trust Claude's judgment | "Analyze code structure, check for bugs, suggest improvements" |
| **Medium** (pseudocode with parameters) | Preferred pattern exists, some variation acceptable | Provide template with customization options | "Use this template and customize as needed" |
| **Low** (specific scripts, few/no parameters) | Operations are fragile, consistency critical | Provide exact commands, "do not modify" | "Run exactly: `python scripts/migrate.py --verify --backup`" |

**Analogy:** Claude is a robot exploring a path:
- **Narrow bridge with cliffs on both sides:** There's only one safe way forward (low freedom)
- **Open field with no hazards:** Many paths lead to success (high freedom)

### Principle 3: Test with All Models You Plan to Use
- **Claude Haiku** (fast, economical): Does the Skill provide enough guidance?
- **Claude Sonnet** (balanced): Is the Skill clear and efficient?
- **Claude Opus** (powerful reasoning): Does the Skill avoid over-explaining?

---

## 4. Naming Conventions

### Best Practices
Use consistent naming patterns. **Gerund form (verb + -ing)** is preferred as it clearly describes the activity or capability.

**Good examples:**
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`
- `writing-documentation`

**Acceptable alternatives:**
- Noun phrases: `pdf-processing`, `spreadsheet-analysis`
- Action-oriented: `process-pdfs`, `analyze-spreadsheets`

**Avoid:**
- Vague names: `helper`, `utils`, `tools`
- Overly generic: `documents`, `data`, `files`
- Reserved words: `anthropic-helper`, `claude-tools`
- Inconsistent patterns within your skill collection

---

## 5. Writing Effective Descriptions

### Critical Rules
1. **Always write in third person.** The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.
   - ✅ "Processes Excel files and generates reports"
   - ❌ "I can help you process Excel files"
   - ❌ "You can use this to process Excel files"

2. **Be specific and include key terms.** Include both what the Skill does and specific triggers/contexts for when to use it.

### Effective Examples

**PDF Processing skill:**
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Excel Analysis skill:**
```yaml
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Git Commit Helper skill:**
```yaml
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

**Avoid:**
```yaml
description: Helps with documents
description: Processes data
description: Does stuff with files
```

---

## 6. Progressive Disclosure Patterns

### Keep SKILL.md Under 500 Lines
Split content into separate files when approaching this limit.

### Complete Skill Directory Example
```text
pdf/
├── SKILL.md              # Main instructions (loaded when triggered)
├── FORMS.md              # Form-filling guide (loaded as needed)
├── reference.md          # API reference (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    ├── analyze_form.py   # Utility script (executed, not loaded)
    ├── fill_form.py      # Form filling script
    └── validate.py       # Validation script
```

### Pattern 1: High-Level Guide with References
```markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files.
---
# PDF Processing
## Quick start
Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
## Advanced features
**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

### Pattern 2: Domain-Specific Organization
```text
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

```markdown
# SKILL.md
# BigQuery Data Analysis
## Available datasets
**Finance**: Revenue, ARR, billing → See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline, accounts → See [reference/sales.md](reference/sales.md)
**Product**: API usage, features, adoption → See [reference/product.md](reference/product.md)
**Marketing**: Campaigns, attribution, email → See [reference/marketing.md](reference/marketing.md)
```

### Pattern 3: Conditional Details
```markdown
# DOCX Processing
## Creating documents
Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).
## Editing documents
For simple edits, modify the XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

### Critical Rule: Avoid Deeply Nested References
Keep all references **one level deep from SKILL.md**. All reference files should link directly from SKILL.md.

- ❌ SKILL.md → advanced.md → details.md
- ✅ SKILL.md → advanced.md, reference.md, examples.md

### Structure Long Reference Files with Table of Contents
For files >100 lines, include a table of contents at the top:
```markdown
# API Reference
## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples
## Authentication and setup
...
```

---

## 7. Workflows and Feedback Loops

### Use Workflows for Complex Tasks
Break complex operations into clear, sequential steps. For complex workflows, provide a **checklist** that Claude can copy and check off:

```markdown
## PDF form filling workflow
Copy this checklist and check off items as you complete them:
```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```
```

### Implement Feedback Loops
**Common pattern:** Run validator → fix errors → repeat

**With code:**
```markdown
## Document editing process
1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python ooxml/scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python ooxml/scripts/pack.py unpacked_dir/ output.docx`
```

**Without code (reference document):**
```markdown
## Content review process
1. Draft your content following the guidelines in STYLE_GUIDE.md
2. Review against the checklist:
   - Check terminology consistency
   - Verify examples follow the standard format
   - Confirm all required sections are present
3. If issues found:
   - Note each issue with specific section reference
   - Revise the content
   - Review the checklist again
4. Only proceed when all requirements are met
5. Finalize and save the document
```

---

## 8. Content Guidelines

### Avoid Time-Sensitive Information
**Bad example (will become wrong):**
```markdown
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.
```

**Good example (use "old patterns" section):**
```markdown
## Current method
Use the v2 API endpoint: `api.example.com/v2/messages`
## Old patterns

```

### Use Consistent Terminology
Choose one term and use it throughout the Skill:
- ✅ "API endpoint" (always), "field" (always), "extract" (always)
- ❌ Mixing "API endpoint", "URL", "API route", "path"
- ❌ Mixing "extract", "pull", "get", "retrieve"

---

## 9. Common Patterns

### Template Pattern (Strict)
```markdown
## Report structure
ALWAYS use this exact template structure:
```markdown
# [Analysis Title]
## Executive summary
[One-paragraph overview of key findings]
## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data
## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
```

### Template Pattern (Flexible)
```markdown
## Report structure
Here is a sensible default format, but use your best judgment based on the analysis:
```markdown
# [Analysis Title]
## Executive summary
[Overview]
## Key findings
[Adapt sections based on what you discover]
## Recommendations
[Tailor to the specific context]
```
```

### Examples Pattern
```markdown
## Commit message format
Generate commit messages following these examples:
**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication
Add login endpoint and token validation middleware
```
**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion
Use UTC timestamps consistently across report generation
```
Follow this style: type(scope): brief description, then detailed explanation.
```

### Conditional Workflow Pattern
```markdown
## Document modification workflow
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below
2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   - Export to .docx format
3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete
```

---

## 10. Anti-Patterns to Avoid

| Anti-Pattern | Instead Do |
|-------------|------------|
| Windows-style paths (`scripts\helper.py`) | Forward slashes: `scripts/helper.py` |
| Offering too many options (4+ libraries) | Provide a default with one escape hatch |
| Deep nesting (SKILL.md → a.md → b.md) | Keep all references one level from SKILL.md |
| Vague Skill names (`helper`, `utils`) | Specific names: `pdf-processing` |
| Over-explaining basic concepts | Assume Claude knows PDFs, libraries, etc. |
| Time-sensitive content (dates, version cutoffs) | Use "Current method" + "Old patterns" section |
| Inconsistent terminology | Choose one term per concept and stick with it |
| First/second person in descriptions | Always write in third person |

---

## 11. Advanced: Skills with Executable Code

### Solve, Don't Punt
Handle error conditions explicitly rather than punting to Claude:

**Good example:**
```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, "w") as f:
            f.write("")
        return ""
    except PermissionError:
        print(f"Cannot access {path}, using default")
        return ""
```

**Bad example (punts to Claude):**
```python
def process_file(path):
    # Just fail and let Claude figure it out
    return open(path).read()
```

### Document Configuration Values (No Voodoo Constants)
**Good example:**
```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30
# Three retries balances reliability vs speed
# Most intermittent failures resolve by the second retry
MAX_RETRIES = 3
```

**Bad example:**
```python
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

### Make Execution Intent Clear
- **"Run `analyze_form.py` to extract fields"** = execute the script
- **"See `analyze_form.py` for the extraction algorithm"** = read as reference

### Create Verifiable Intermediate Outputs (Plan-Validate-Execute)
For complex, open-ended tasks, add an intermediate plan file:
1. **Create a plan file:** `changes.json` with all intended modifications
2. **Validate with a script:** `python validate_changes.py changes.json`
3. **Execute only if validation passes:** `python apply_changes.py changes.json`
4. **Verify final output:** `python verify_output.py output.pdf`

### Package Dependencies
- **claude.ai:** Can install packages from npm and PyPI, pull from GitHub
- **Claude API:** No network access, no runtime package installation
- **Claude Code:** Full network access

Always list required packages in SKILL.md and verify availability in the [code execution tool documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool).

### MCP Tool References
Always use fully qualified names: `ServerName:tool_name`

- ✅ `BigQuery:bigquery_schema`
- ✅ `GitHub:create_issue`
- ❌ `bigquery_schema` (may fail with multiple MCP servers)

### Avoid Assuming Tools are Installed
- ❌ "Use the pdf library to process the file."
- ✅ "Install required package: `pip install pypdf`. Then use it: `from pypdf import PdfReader`"

---

## 12. Where Skills Work

| Surface | Pre-built Skills | Custom Skills | Sharing Model |
|---------|-----------------|---------------|---------------|
| **Claude API** | ✅ Yes | ✅ Yes | Workspace-wide |
| **Claude Code** | ❌ No | ✅ Yes | Filesystem-based (~/.claude/skills/ or .claude/skills/) |
| **Claude.ai** | ✅ Yes | ✅ Yes | Individual user only |

### Critical Limitation: No Cross-Surface Sync
Skills uploaded to one surface are **not** automatically available on others:
- Skills uploaded to Claude.ai must be separately uploaded to the API
- Skills uploaded via the API are not available on Claude.ai
- Claude Code Skills are filesystem-based and separate from both

---

## 13. Runtime Environment Constraints

| Environment | Network Access | Package Installation |
|-------------|---------------|---------------------|
| **Claude API** | ❌ No network access | ❌ No runtime package installation |
| **Claude Code** | ✅ Full network access | ✅ Can install, but should use local packages |
| **Claude.ai** | Varies by user/admin settings | ✅ Can install from npm/PyPI |

---

## 14. Evaluation and Iteration Process

### Build Evaluations First (Before Writing Extensive Docs)
1. **Identify gaps:** Run Claude on representative tasks without a Skill. Document specific failures
2. **Create evaluations:** Build three scenarios that test these gaps
3. **Establish baseline:** Measure Claude's performance without the Skill
4. **Write minimal instructions:** Create just enough content to address the gaps and pass evaluations
5. **Iterate:** Execute evaluations, compare against baseline, and refine

**Evaluation structure example:**
```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using an appropriate library",
    "Extracts text content from all pages",
    "Saves the extracted text to output.txt in a clear format"
  ]
}
```

### Develop Iteratively with Claude
Use two Claude instances:
- **Claude A** (expert): Helps design and refine the Skill
- **Claude B** (agent): Tests the Skill in real tasks

**Process:**
1. Complete a task without a Skill (note what you repeatedly provide)
2. Identify the reusable pattern
3. Ask Claude A to create the Skill (Claude understands the format natively)
4. Review for conciseness
5. Improve information architecture
6. Test with Claude B on similar tasks
7. Observe Claude B's behavior and bring insights back to Claude A
8. Iterate based on real usage, not assumptions

### Observe How Claude Navigates Skills
Watch for:
- **Unexpected exploration paths:** Does Claude read files in an unexpected order?
- **Missed connections:** Does Claude fail to follow references to important files?
- **Overreliance on certain sections:** Should that content be in SKILL.md instead?
- **Ignored content:** If Claude never accesses a bundled file, is it unnecessary?

---

## 15. Security Considerations

- **Use only from trusted sources** (self-created or Anthropic-provided)
- **Audit thoroughly:** Review all files: SKILL.md, scripts, images, and other resources
- **Look for unusual patterns:** Unexpected network calls, file access patterns, operations that don't match the Skill's stated purpose
- **External sources are risky:** Skills that fetch data from external URLs pose particular risk
- **Tool misuse:** Malicious Skills can invoke tools (file operations, bash commands) in harmful ways
- **Data exposure:** Skills with access to sensitive data could leak information
- **Treat like installing software:** Be especially careful in production systems with access to sensitive data

---

## 16. Data Retention

- Agent Skills is **not** eligible for Zero Data Retention (ZDR)
- Skill definitions and execution data are retained according to standard data retention policy

---

## 17. Complete Pre-Flight Checklist

### Core Quality
- [ ] Description is specific and includes key terms
- [ ] Description includes both what the Skill does and when to use it
- [ ] Description is written in third person
- [ ] SKILL.md body is under 500 lines
- [ ] Additional details are in separate files (if needed)
- [ ] No time-sensitive information (or in "old patterns" section)
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract
- [ ] File references are one level deep (from SKILL.md)
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps with checklists where appropriate
- [ ] Appropriate degree of freedom set for each operation

### Code and Scripts
- [ ] Scripts solve problems rather than punt to Claude
- [ ] Error handling is explicit and helpful
- [ ] No "voodoo constants" (all values justified)
- [ ] Required packages listed in instructions and verified as available
- [ ] Scripts have clear documentation
- [ ] No Windows-style paths (all forward slashes)
- [ ] Validation/verification steps for critical operations
- [ ] Feedback loops included for quality-critical tasks
- [ ] MCP tools use fully qualified names (ServerName:tool_name)
- [ ] No assumptions about tool/package availability

### Testing
- [ ] At least three evaluations created
- [ ] Tested with Haiku, Sonnet, and Opus (if using multiple models)
- [ ] Tested with real usage scenarios (not just test cases)
- [ ] Team feedback incorporated (if applicable)
- [ ] Claude's navigation patterns observed and iterations made

### Metadata Compliance
- [ ] `name` field is max 64 characters
- [ ] `name` uses only lowercase letters, numbers, and hyphens
- [ ] `name` contains no XML tags
- [ ] `name` does not contain "anthropic" or "claude"
- [ ] `description` is non-empty and max 1024 characters
- [ ] `description` contains no XML tags
```

---

## 18. Available Pre-Built Agent Skills

| Skill | ID | Purpose |
|-------|-----|---------|
| **PowerPoint** | `pptx` | Create presentations, edit slides, analyze presentation content |
| **Excel** | `xlsx` | Create spreadsheets, analyze data, generate reports with charts |
| **Word** | `docx` | Create documents, edit content, format text |
| **PDF** | `pdf` | Generate formatted PDF documents and reports |

### Open-Source Skills
- **Claude API Skill:** Provides Claude with up-to-date API reference material, SDK documentation, and best practices for 8 programming languages. Bundled with Claude Code and available from the [skills repository](https://github.com/anthropics/skills).

---

## 19. Resources and Next Steps

### Official Documentation
- [Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Get Started with Agent Skills (Quickstart)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart)
- [Use Skills with the Claude API](https://platform.claude.com/docs/en/build-with-claude/skills-guide)
- [Use Skills in Claude Code](https://code.claude.com/docs/en/skills)
- [Skills Cookbook](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction)
- [Open-Source Skills Repository](https://github.com/anthropics/skills)

### Engineering Blog
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### Claude.ai Help Center
- [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [How to create custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Teach Claude your way of working using Skills](https://support.claude.com/en/articles/12580051-teach-claude-your-way-of-working-using-skills)

### Code Execution Environment
- [Code Execution Tool Documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) (for available packages)
```

---

This guide merges all the guidance from the Agent Skills overview, best practices documentation, and technical specifications into one comprehensive reference. It covers architecture, naming, descriptions, progressive disclosure, workflows, content guidelines, anti-patterns, code best practices, evaluation strategies, security, and a complete pre-flight checklist.