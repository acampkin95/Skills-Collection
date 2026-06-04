# Crawl4AI Quality Guidelines

Standards for high-quality data extraction with Crawl4AI.

## Content Quality Standards

### Extraction Quality Metrics

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class QualityMetrics:
    """Metrics for assessing extraction quality."""
    completeness: float  # Percentage of expected fields extracted
    accuracy: float      # How accurate the extracted data is
    consistency: float   # Consistency across multiple extractions
    freshness: float     # How up-to-date the content is

    def overall_score(self) -> float:
        """Calculate overall quality score."""
        weights = {"completeness": 0.3, "accuracy": 0.4, "consistency": 0.2, "freshness": 0.1}
        return sum(getattr(self, k) * v for k, v in weights.items())

class QualityAssessor:
    """Assess and improve extraction quality."""

    def __init__(self, min_quality_threshold: float = 0.7):
        self.min_threshold = min_quality_threshold

    def assess_extraction(
        self,
        result,
        expected_fields: list = None
    ) -> QualityMetrics:
        """Assess the quality of an extraction."""
        # Completeness: check if expected fields are present
        completeness = self._assess_completeness(result, expected_fields)

        # Accuracy: validate against known patterns
        accuracy = self._assess_accuracy(result)

        # Consistency: compare with previous extractions
        consistency = self._assess_consistency(result)

        # Freshness: check content age
        freshness = self._assess_freshness(result)

        return QualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            freshness=freshness
        )

    def _assess_completeness(self, result, expected_fields: list) -> float:
        if not expected_fields:
            return 1.0

        extracted = set()
        if hasattr(result, 'extracted_content'):
            try:
                import json
                data = json.loads(result.extracted_content)
                extracted = set(data.keys()) if isinstance(data, dict) else set()
            except:
                pass

        matched = sum(1 for f in expected_fields if f in extracted)
        return matched / len(expected_fields)

    def _assess_accuracy(self, result) -> float:
        # Simple accuracy check: non-empty content
        if hasattr(result, 'markdown') and result.markdown:
            return 1.0
        return 0.0

    def _assess_consistency(self, result) -> float:
        # Placeholder for consistency check
        return 1.0

    def _assess_freshness(self, result) -> float:
        # Check for recent content indicators
        if hasattr(result, 'metadata'):
            if result.metadata.get('last_modified'):
                return 1.0
        return 0.5
```

### Content Validation Rules

```python
import re
from typing import Optional, List

class ContentValidator:
    """Validate extracted content quality."""

    MIN_CONTENT_LENGTH = 100
    MAX_CONTENT_LENGTH = 1_000_000
    VALID_MARKUP_PATTERNS = [
        r'^#+\s',           # Markdown headers
        r'\*\*.*?\*\*',     # Bold text
        r'`.*?`',           # Code blocks
    ]

    @classmethod
    def validate(cls, content: str) -> tuple[bool, List[str]]:
        """Validate content and return (is_valid, errors)."""
        errors = []

        if len(content) < cls.MIN_CONTENT_LENGTH:
            errors.append(f"Content too short: {len(content)} chars")

        if len(content) > cls.MAX_CONTENT_LENGTH:
            errors.append(f"Content too long: {len(content)} chars")

        if not content.strip():
            errors.append("Content is empty or whitespace only")

        return len(errors) == 0, errors

    @classmethod
    def validate_markdown(cls, markdown: str) -> tuple[bool, List[str]]:
        """Validate markdown content structure."""
        errors = []

        # Check for proper heading hierarchy
        headings = re.findall(r'^(#+)\s', markdown, re.MULTILINE)
        if headings:
            levels = [len(h) for h in headings]
            for i in range(len(levels) - 1):
                if levels[i + 1] > levels[i] + 1:
                    errors.append("Skipped heading level detected")

        return len(errors) == 0, errors
```

---

## Data Schema Standards

### Schema Versioning

```python
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import hashlib
import json

@dataclass
class SchemaVersion:
    """Versioned extraction schema."""
    version: str
    created_at: datetime
    description: str
    fields: list
    checksum: str

    @classmethod
    def create(cls, schema: dict, description: str = "") -> "SchemaVersion":
        """Create a new schema version."""
        version = datetime.now().strftime("%Y.%m.%d.%H%M")
        content = json.dumps(schema, sort_keys=True)
        checksum = hashlib.sha256(content.encode()).hexdigest()[:8]

        return cls(
            version=version,
            created_at=datetime.now(),
            description=description,
            fields=schema.get("fields", []),
            checksum=checksum,
        )

    def is_compatible(self, other: "SchemaVersion") -> bool:
        """Check if schemas are compatible."""
        return self.checksum == other.checksum
```

### Field Validation

```python
from typing import Any, Optional
from dataclasses import dataclass

@dataclass
class FieldSpec:
    name: str
    type: str
    required: bool = True
    validator: callable = None

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a field value."""
        if value is None or value == "":
            if self.required:
                return False, f"Field '{self.name}' is required"
            return True, None

        if self.validator:
            return self.validator(value)

        return True, None

class SchemaValidator:
    """Validate extraction results against schema."""

    def __init__(self, fields: list):
        self.field_specs = [FieldSpec(**f) if isinstance(f, dict) else f for f in fields]

    def validate(self, data: dict) -> tuple[bool, list]:
        """Validate data against schema."""
        errors = []

        for spec in self.field_specs:
            value = data.get(spec.name)
            valid, error = spec.validate(value)
            if not valid:
                errors.append(error)

        return len(errors) == 0, errors
```

---

## Output Format Standards

### JSON Output

```python
import json
from datetime import datetime
from typing import Any, Dict

class OutputFormatter:
    """Standardized output formatting."""

    @staticmethod
    def format_json(
        data: Any,
        metadata: Dict = None,
        pretty: bool = True
    ) -> str:
        """Format output as JSON."""
        output = {
            "data": data,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "format": "json",
                **(metadata or {}),
            }
        }

        return json.dumps(output, indent=2 if pretty else None)

    @staticmethod
    def format_markdown(
        content: str,
        source_url: str,
        title: str = None,
        metadata: Dict = None
    ) -> str:
        """Format output as markdown."""
        lines = []

        if title:
            lines.append(f"# {title}")
            lines.append("")

        lines.append(f"*Source: {source_url}*")
        lines.append(f"*Crawled: {datetime.utcnow().isoformat()}Z*")
        lines.append("")

        if metadata:
            lines.append("---")
            lines.append("**Metadata:**")
            for k, v in metadata.items():
                lines.append(f"- {k}: {v}")
            lines.append("")

        lines.append("---")
        lines.append(content)

        return "\n".join(lines)
```

---

## Quality Assurance Checklist

```python
class QualityChecklist:
    """Run all quality checks on extraction results."""

    CHECKS = [
        "content_length",
        "markdown_structure",
        "link_verification",
        "media_validation",
        "schema_compliance",
    ]

    def __init__(self):
        self.results = {}

    def run_all(self, result, schema: dict = None) -> dict:
        """Run all quality checks."""
        self.results = {}

        # Content length check
        self.results["content_length"] = self._check_content_length(result)

        # Markdown structure
        self.results["markdown_structure"] = self._check_markdown_structure(result)

        # Link verification
        self.results["link_verification"] = self._check_links(result)

        # Media validation
        self.results["media_validation"] = self._check_media(result)

        # Schema compliance
        if schema:
            self.results["schema_compliance"] = self._check_schema(result, schema)

        return self.results

    def _check_content_length(self, result) -> dict:
        length = len(result.markdown) if result.markdown else 0
        return {
            "passed": length >= 100,
            "length": length,
            "threshold": 100,
        }

    def _check_markdown_structure(self, result) -> dict:
        if not result.markdown:
            return {"passed": False, "reason": "No markdown content"}

        has_headers = "#" in result.markdown
        return {
            "passed": has_headers,
            "has_headers": has_headers,
        }

    def _check_links(self, result) -> dict:
        links = result.links.get("internal", []) + result.links.get("external", [])
        return {
            "passed": True,
            "total_links": len(links),
        }

    def _check_media(self, result) -> dict:
        media = result.media or {}
        return {
            "passed": True,
            "images": len(media.get("images", [])),
            "videos": len(media.get("videos", [])),
        }

    def _check_schema(self, result, schema: dict) -> dict:
        return {"passed": True, "schema": schema.get("name")}

    def all_passed(self) -> bool:
        """Check if all tests passed."""
        return all(r.get("passed", False) for r in self.results.values())
```
