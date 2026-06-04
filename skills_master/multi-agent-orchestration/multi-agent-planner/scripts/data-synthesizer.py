"""
Data Synthesizer Module

Synthesizes and analyzes project data including:
- Merge research findings
- Cross-reference validation
- Gap analysis
- Trend identification
- Recommendation generation
"""

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


@dataclass
class ResearchFinding:
    """Represents a research finding"""
    id: str
    topic: str
    finding: str
    source: str
    confidence: float  # 0-1
    relevance_score: float  # 0-1
    date_found: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "finding": self.finding,
            "source": self.source,
            "confidence": self.confidence,
            "relevance_score": self.relevance_score,
            "date_found": self.date_found,
            "tags": self.tags,
            "notes": self.notes
        }


@dataclass
class Gap:
    """Represents a gap in requirements or resources"""
    id: str
    category: str
    description: str
    severity: str  # High, Medium, Low
    impacted_areas: List[str] = field(default_factory=list)
    recommended_action: str = ""
    estimated_effort: str = "unknown"
    status: str = "open"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "impacted_areas": self.impacted_areas,
            "recommended_action": self.recommended_action,
            "estimated_effort": self.estimated_effort,
            "status": self.status
        }


@dataclass
class Trend:
    """Represents an identified trend"""
    id: str
    name: str
    description: str
    direction: str  # increasing, decreasing, stable
    evidence_count: int = 0
    impact_prediction: str = ""
    timeframe: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "direction": self.direction,
            "evidence_count": self.evidence_count,
            "impact_prediction": self.impact_prediction,
            "timeframe": self.timeframe
        }


@dataclass
class Recommendation:
    """Represents a recommendation"""
    id: str
    category: str
    title: str
    description: str
    priority: str  # High, Medium, Low
    rationale: str = ""
    dependencies: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    risks: List[str] = field(default_factory=list)
    status: str = "proposed"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "rationale": self.rationale,
            "dependencies": self.dependencies,
            "expected_outcome": self.expected_outcome,
            "risks": self.risks,
            "status": self.status
        }


@dataclass
class ValidationResult:
    """Represents a validation result"""
    check_id: str
    check_name: str
    status: str  # pass, fail, warning, info
    details: str = ""
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "status": self.status,
            "details": self.details,
            "evidence": self.evidence,
            "recommendations": self.recommendations
        }


@dataclass
class SynthesisReport:
    """Container for synthesis report"""
    project_name: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    findings: List[Dict] = field(default_factory=list)
    gaps: List[Dict] = field(default_factory=list)
    trends: List[Dict] = field(default_factory=list)
    recommendations: List[Dict] = field(default_factory=list)
    validations: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "project_name": self.project_name,
            "generated_at": self.generated_at,
            "findings": self.findings,
            "gaps": self.gaps,
            "trends": self.trends,
            "recommendations": self.recommendations,
            "validations": self.validations
        }


class DataSynthesizer:
    """Main class for data synthesis operations"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.findings: List[ResearchFinding] = []
        self.gaps: List[Gap] = []
        self.trends: List[Trend] = []
        self.recommendations: List[Recommendation] = []
        self.validations: List[ValidationResult] = []
        self.cross_references: Dict[str, List[str]] = {}

    # Research Findings
    def add_finding(self, finding: ResearchFinding) -> None:
        self.findings.append(finding)
        # Track topic references
        if finding.topic not in self.cross_references:
            self.cross_references[finding.topic] = []
        self.cross_references[finding.topic].append(finding.id)

    def get_findings_by_topic(self) -> Dict:
        """Group findings by topic"""
        by_topic = {}
        for finding in self.findings:
            if finding.topic not in by_topic:
                by_topic[finding.topic] = []
            by_topic[finding.topic].append(finding.to_dict())
        return by_topic

    def get_high_confidence_findings(self, threshold: float = 0.8) -> List[ResearchFinding]:
        """Get findings above confidence threshold"""
        return [f for f in self.findings if f.confidence >= threshold]

    def get_findings_summary(self) -> Dict:
        """Summarize findings"""
        if not self.findings:
            return {"total": 0, "by_topic": {}}

        by_topic = {}
        for finding in self.findings:
            if finding.topic not in by_topic:
                by_topic[finding.topic] = {"count": 0, "avg_confidence": 0}
            by_topic[finding.topic]["count"] += 1
            by_topic[finding.topic]["avg_confidence"] += finding.confidence

        # Calculate averages
        for topic in by_topic:
            count = by_topic[topic]["count"]
            by_topic[topic]["avg_confidence"] = by_topic[topic]["avg_confidence"] / count

        return {
            "total": len(self.findings),
            "by_topic": by_topic,
            "avg_confidence": sum(f.confidence for f in self.findings) / len(self.findings)
        }

    # Gap Analysis
    def add_gap(self, gap: Gap) -> None:
        self.gaps.append(gap)

    def get_gaps_by_severity(self) -> Dict:
        """Group gaps by severity"""
        by_severity = {"High": [], "Medium": [], "Low": []}
        for gap in self.gaps:
            by_severity[gap.severity].append(gap.to_dict())
        return by_severity

    def get_gaps_summary(self) -> Dict:
        """Summarize gaps"""
        by_category = {}
        for gap in self.gaps:
            if gap.category not in by_category:
                by_category[gap.category] = {"High": 0, "Medium": 0, "Low": 0, "total": 0}
            by_category[gap.category][gap.severity] += 1
            by_category[gap.category]["total"] += 1

        return {
            "total": len(self.gaps),
            "by_category": by_category,
            "open_count": sum(1 for g in self.gaps if g.status == "open"),
            "closed_count": sum(1 for g in self.gaps if g.status == "closed")
        }

    # Trend Analysis
    def add_trend(self, trend: Trend) -> None:
        self.trends.append(trend)

    def get_trends_summary(self) -> Dict:
        """Summarize trends"""
        return {
            "total": len(self.trends),
            "increasing": sum(1 for t in self.trends if t.direction == "increasing"),
            "decreasing": sum(1 for t in self.trends if t.direction == "decreasing"),
            "stable": sum(1 for t in self.trends if t.direction == "stable"),
            "by_evidence": sorted(
                [{"name": t.name, "evidence": t.evidence_count} for t in self.trends],
                key=lambda x: x["evidence"],
                reverse=True
            )
        }

    # Cross-Reference Validation
    def add_validation(self, validation: ValidationResult) -> None:
        self.validations.append(validation)

    def cross_reference_validate(self, source_ids: List[str], target_ids: List[str]) -> ValidationResult:
        """Check if source items reference target items"""
        missing = []
        found = []

        for source_id in source_ids:
            for target_id in target_ids:
                if f"[{target_id}]" in source_id or target_id in source_id:
                    found.append(target_id)
                else:
                    missing.append(target_id)

        status = "pass" if not missing else "fail" if len(missing) == len(target_ids) else "warning"

        return ValidationResult(
            check_id=f"XREF-{len(self.validations) + 1}",
            check_name="Cross-Reference Validation",
            status=status,
            details=f"Found: {len(found)}, Missing: {len(missing)}",
            evidence=found,
            recommendations=missing if missing else []
        )

    def validate_dependencies(self, requirements: list[dict], resources: list[dict]) -> List[ValidationResult]:
        """Validate that requirements have corresponding resources"""
        validations = []

        # Extract requirement skill needs
        skill_needs = set()
        for req in requirements:
            if "skill" in req:
                skill_needs.add(req["skill"])

        # Check resource availability
        available_skills = set()
        for resource in resources:
            if "skills" in resource:
                for skill in resource["skills"]:
                    available_skills.add(skill.get("name", skill) if isinstance(skill, dict) else skill)

        missing_skills = skill_needs - available_skills

        validations.append(ValidationResult(
            check_id="DEP-001",
            check_name="Skill Dependency Check",
            status="pass" if not missing_skills else "fail",
            details=f"Missing skills: {', '.join(missing_skills)}" if missing_skills else "All skill dependencies met",
            evidence=list(available_skills),
            recommendations=[f"Acquire skill: {s}" for s in missing_skills]
        ))

        return validations

    def get_validation_summary(self) -> Dict:
        """Summarize validation results"""
        return {
            "total": len(self.validations),
            "passed": sum(1 for v in self.validations if v.status == "pass"),
            "failed": sum(1 for v in self.validations if v.status == "fail"),
            "warnings": sum(1 for v in self.validations if v.status == "warning"),
            "informational": sum(1 for v in self.validations if v.status == "info"),
            "pass_rate": sum(1 for v in self.validations if v.status == "pass") / len(self.validations) if self.validations else 1.0
        }

    # Recommendations
    def add_recommendation(self, recommendation: Recommendation) -> None:
        self.recommendations.append(recommendation)

    def generate_recommendations_from_gaps(self) -> None:
        """Auto-generate recommendations to address gaps"""
        for gap in self.gaps:
            if gap.status == "open":
                recommendation = Recommendation(
                    id=f"REC-{len(self.recommendations) + 1:03d}",
                    category=gap.category,
                    title=f"Address {gap.severity} Gap: {gap.description[:50]}",
                    description=f"Implement solution to address {gap.category} gap: {gap.description}",
                    priority=gap.severity,
                    rationale=f"Gap severity is {gap.severity} and impacts: {', '.join(gap.impacted_areas)}",
                    expected_outcome=f"Resolution of {gap.category} gap",
                    dependencies=[]
                )
                self.add_recommendation(recommendation)

    def get_recommendations_summary(self) -> Dict:
        """Summarize recommendations"""
        by_priority = {"High": [], "Medium": [], "Low": []}
        for rec in self.recommendations:
            by_priority[rec.priority].append(rec.to_dict())

        return {
            "total": len(self.recommendations),
            "by_priority": by_priority,
            "proposed": sum(1 for r in self.recommendations if r.status == "proposed"),
            "approved": sum(1 for r in self.recommendations if r.status == "approved"),
            "implemented": sum(1 for r in self.recommendations if r.status == "implemented")
        }

    # Data Merging
    def merge_findings(self, other_findings: List[ResearchFinding]) -> None:
        """Merge findings from another source"""
        for finding in other_findings:
            # Check for duplicates
            existing = [f for f in self.findings if f.id == finding.id]
            if not existing:
                self.findings.append(finding)
            else:
                # Merge if new finding has higher confidence
                if finding.confidence > existing[0].confidence:
                    idx = self.findings.index(existing[0])
                    self.findings[idx] = finding

    def merge_gaps(self, other_gaps: List[Gap]) -> None:
        """Merge gaps from another source"""
        for gap in other_gaps:
            existing = [g for g in self.gaps if g.id == gap.id]
            if not existing:
                self.gaps.append(gap)

    # Synthesis Report Generation
    def generate_synthesis_report(self) -> SynthesisReport:
        """Generate comprehensive synthesis report"""
        return SynthesisReport(
            project_name=self.project_name,
            findings=[f.to_dict() for f in self.findings],
            gaps=[g.to_dict() for g in self.gaps],
            trends=[t.to_dict() for t in self.trends],
            recommendations=[r.to_dict() for r in self.recommendations],
            validations=[v.to_dict() for v in self.validations]
        )

    def export_to_yaml(self, filepath: str) -> None:
        report = self.generate_synthesis_report()
        with open(filepath, 'w') as f:
            yaml.dump(report.to_dict(), f, default_flow_style=False, sort_keys=False)

    def export_to_json(self, filepath: str) -> None:
        report = self.generate_synthesis_report()
        with open(filepath, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)

    def import_from_yaml(self, filepath: str) -> None:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        self._load_data(data)

    def import_from_json(self, filepath: str) -> None:
        with open(filepath, 'r') as f:
            data = json.load(f)
        self._load_data(data)

    def _load_data(self, data: dict) -> None:
        self.project_name = data.get('project_name', self.project_name)
        # Would implement full loading logic here

    def generate_report(self) -> str:
        """Generate human-readable synthesis report"""
        report = []
        report.append(f"Data Synthesis Report for: {self.project_name}")
        report.append("=" * 70)

        # Findings Summary
        findings_summary = self.get_findings_summary()
        report.append("\n[RESEARCH FINDINGS]")
        report.append(f"  Total Findings: {findings_summary['total']}")
        report.append(f"  Average Confidence: {findings_summary['avg_confidence']:.2%}")

        # Gaps Summary
        gaps_summary = self.get_gaps_summary()
        report.append("\n[GAP ANALYSIS]")
        report.append(f"  Total Gaps: {gaps_summary['total']}")
        report.append(f"  Open: {gaps_summary['open_count']}, Closed: {gaps_summary['closed_count']}")
        for category, data in gaps_summary.get("by_category", {}).items():
            report.append(f"    {category}: {data['total']} (H:{data['High']}, M:{data['Medium']}, L:{data['Low']})")

        # Trends Summary
        trends_summary = self.get_trends_summary()
        report.append("\n[TRENDS]")
        report.append(f"  Total Trends: {trends_summary['total']}")
        report.append(f"  Increasing: {trends_summary['increasing']}")
        report.append(f"  Decreasing: {trends_summary['decreasing']}")
        report.append(f"  Stable: {trends_summary['stable']}")

        # Validations Summary
        validation_summary = self.get_validation_summary()
        report.append("\n[VALIDATIONS]")
        report.append(f"  Total Checks: {validation_summary['total']}")
        report.append(f"  Passed: {validation_summary['passed']}")
        report.append(f"  Failed: {validation_summary['failed']}")
        report.append(f"  Pass Rate: {validation_summary['pass_rate']:.1%}")

        # Recommendations Summary
        rec_summary = self.get_recommendations_summary()
        report.append("\n[RECOMMENDATIONS]")
        report.append(f"  Total: {rec_summary['total']}")
        report.append(f"  High Priority: {len(rec_summary['by_priority'].get('High', []))}")
        report.append(f"  Medium Priority: {len(rec_summary['by_priority'].get('Medium', []))}")
        report.append(f"  Low Priority: {len(rec_summary['by_priority'].get('Low', []))}")

        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    synthesizer = DataSynthesizer("Multi-Agent Planner")

    # Add findings
    synthesizer.add_finding(ResearchFinding(
        id="FIND-001",
        topic="Agent Frameworks",
        finding="LangChain provides comprehensive agent orchestration",
        source="LangChain Documentation",
        confidence=0.9,
        relevance_score=0.85,
        tags=["framework", "orchestration"]
    ))

    # Add gaps
    synthesizer.add_gap(Gap(
        id="GAP-001",
        category="Skills",
        description="No expert in multi-agent coordination patterns",
        severity="High",
        impacted_areas=["Architecture", "Implementation"],
        recommended_action="Train or hire for multi-agent expertise"
    ))

    # Add trend
    synthesizer.add_trend(Trend(
        id="TREND-001",
        name="Agent Adoption",
        description="Increasing adoption of multi-agent systems in production",
        direction="increasing",
        evidence_count=15,
        impact_prediction="High demand for multi-agent skills"
    ))

    # Generate recommendations from gaps
    synthesizer.generate_recommendations_from_gaps()

    print(synthesizer.generate_report())
