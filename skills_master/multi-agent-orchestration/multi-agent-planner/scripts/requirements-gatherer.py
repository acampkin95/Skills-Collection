"""
Requirements Gatherer Module

Collects and structures project requirements including:
- Stakeholder analysis
- Functional requirements
- Non-functional requirements
- Constraints identification
- Assumption documentation
- Priority classification (MoSCoW)
"""

import json
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path


class Priority(Enum):
    """MoSCoW priority classification"""
    MUST_HAVE = "Must Have"
    SHOULD_HAVE = "Should Have"
    COULD_HAVE = "Could Have"
    WONT_HAVE = "Won't Have"


class StakeholderType(Enum):
    """Types of stakeholders"""
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    KEY = "Key"
    EXTERNAL = "External"


class RequirementType(Enum):
    """Types of functional requirements"""
    BUSINESS = "Business"
    USER = "User"
    SYSTEM = "System"
    DATA = "Data"
    INTERFACE = "Interface"
    SECURITY = "Security"


@dataclass
class Stakeholder:
    """Represents a project stakeholder"""
    name: str
    role: str
    type: StakeholderType
    interests: List[str] = field(default_factory=list)
    influence: int = 5  # 1-10 scale
    impact: int = 5  # 1-10 scale
    concerns: List[str] = field(default_factory=list)
    communication_preference: str = "email"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role,
            "type": self.type.value,
            "interests": self.interests,
            "influence": self.influence,
            "impact": self.impact,
            "concerns": self.concerns,
            "communication_preference": self.communication_preference
        }


@dataclass
class FunctionalRequirement:
    """Represents a functional requirement"""
    id: str
    title: str
    description: str
    requirement_type: RequirementType
    priority: Priority
    source_stakeholder: str
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    status: str = "pending"
    estimated_effort: str = "unknown"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "requirement_type": self.requirement_type.value,
            "priority": self.priority.value,
            "source_stakeholder": self.source_stakeholder,
            "dependencies": self.dependencies,
            "acceptance_criteria": self.acceptance_criteria,
            "use_cases": self.use_cases,
            "status": self.status,
            "estimated_effort": self.estimated_effort
        }


@dataclass
class NonFunctionalRequirement:
    """Represents a non-functional requirement"""
    id: str
    category: str
    name: str
    description: str
    target_value: str
    priority: Priority
    measurement_criteria: str
    current_state: str = "unknown"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "description": self.description,
            "target_value": self.target_value,
            "priority": self.priority.value,
            "measurement_criteria": self.measurement_criteria,
            "current_state": self.current_state
        }


@dataclass
class Constraint:
    """Represents a project constraint"""
    id: str
    type: str
    description: str
    impact: str
    mitigation_strategy: str = ""
    is_blocker: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "impact": self.impact,
            "mitigation_strategy": self.mitigation_strategy,
            "is_blocker": self.is_blocker
        }


@dataclass
class Assumption:
    """Represents a project assumption"""
    id: str
    statement: str
    rationale: str
    impact: str
    owner: str
    validated: bool = False
    validation_method: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "statement": self.statement,
            "rationale": self.rationale,
            "impact": self.impact,
            "owner": self.owner,
            "validated": self.validated,
            "validation_method": self.validation_method
        }


@dataclass
class RequirementsCollection:
    """Container for all requirements data"""
    project_name: str
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    stakeholders: List[Dict] = field(default_factory=list)
    functional_requirements: List[Dict] = field(default_factory=list)
    non_functional_requirements: List[Dict] = field(default_factory=list)
    constraints: List[Dict] = field(default_factory=list)
    assumptions: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "project_name": self.project_name,
            "version": self.version,
            "created_at": self.created_at,
            "stakeholders": self.stakeholders,
            "functional_requirements": self.functional_requirements,
            "non_functional_requirements": self.non_functional_requirements,
            "constraints": self.constraints,
            "assumptions": self.assumptions
        }


class RequirementsGatherer:
    """Main class for requirements gathering operations"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.stakeholders: List[Stakeholder] = []
        self.functional_requirements: List[FunctionalRequirement] = []
        self.non_functional_requirements: List[NonFunctionalRequirement] = []
        self.constraints: List[Constraint] = []
        self.assumptions: List[Assumption] = []

    def add_stakeholder(self, stakeholder: Stakeholder) -> None:
        """Add a stakeholder to the collection"""
        self.stakeholders.append(stakeholder)

    def add_functional_requirement(self, req: FunctionalRequirement) -> None:
        """Add a functional requirement"""
        self.functional_requirements.append(req)

    def add_non_functional_requirement(self, req: NonFunctionalRequirement) -> None:
        """Add a non-functional requirement"""
        self.non_functional_requirements.append(req)

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint"""
        self.constraints.append(constraint)

    def add_assumption(self, assumption: Assumption) -> None:
        """Add an assumption"""
        self.assumptions.append(assumption)

    def get_must_have_requirements(self) -> List[FunctionalRequirement]:
        """Get all MUST_HAVE priority requirements"""
        return [r for r in self.functional_requirements if r.priority == Priority.MUST_HAVE]

    def get_priority_summary(self) -> dict:
        """Get summary of requirements by priority"""
        summary = {p: 0 for p in Priority}
        for req in self.functional_requirements:
            summary[req.priority] += 1
        return {p.value: count for p, count in summary.items()}

    def get_stakeholder_matrix(self) -> List[Dict]:
        """Generate stakeholder influence/impact matrix"""
        return [
            {
                "name": s.name,
                "role": s.role,
                "influence": s.influence,
                "impact": s.impact,
                "classification": self._classify_stakeholder(s.influence, s.impact)
            }
            for s in self.stakeholders
        ]

    def _classify_stakeholder(self, influence: int, impact: int) -> str:
        """Classify stakeholder based on influence and impact"""
        if influence >= 7 and impact >= 7:
            return "Key Player"
        elif influence >= 7:
            return "Keep Satisfied"
        elif impact >= 7:
            return "Keep Informed"
        else:
            return "Monitor"

    def export_to_yaml(self, filepath: str) -> None:
        """Export requirements to YAML file"""
        collection = RequirementsCollection(
            project_name=self.project_name,
            stakeholders=[s.to_dict() for s in self.stakeholders],
            functional_requirements=[r.to_dict() for r in self.functional_requirements],
            non_functional_requirements=[r.to_dict() for r in self.non_functional_requirements],
            constraints=[c.to_dict() for c in self.constraints],
            assumptions=[a.to_dict() for a in self.assumptions]
        )
        with open(filepath, 'w') as f:
            yaml.dump(collection.to_dict(), f, default_flow_style=False, sort_keys=False)

    def export_to_json(self, filepath: str) -> None:
        """Export requirements to JSON file"""
        collection = RequirementsCollection(
            project_name=self.project_name,
            stakeholders=[s.to_dict() for s in self.stakeholders],
            functional_requirements=[r.to_dict() for r in self.functional_requirements],
            non_functional_requirements=[r.to_dict() for r in self.non_functional_requirements],
            constraints=[c.to_dict() for c in self.constraints],
            assumptions=[a.to_dict() for a in self.assumptions]
        )
        with open(filepath, 'w') as f:
            json.dump(collection.to_dict(), f, indent=2)

    def import_from_yaml(self, filepath: str) -> None:
        """Import requirements from YAML file"""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        self._load_data(data)

    def import_from_json(self, filepath: str) -> None:
        """Import requirements from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        self._load_data(data)

    def _load_data(self, data: dict) -> None:
        """Load data from dictionary"""
        self.project_name = data.get('project_name', self.project_name)
        # Would implement full loading logic here
        # Simplified for brevity

    def generate_report(self) -> str:
        """Generate a summary report"""
        report = []
        report.append(f"Requirements Report for: {self.project_name}")
        report.append("=" * 60)
        report.append(f"\nStakeholders: {len(self.stakeholders)}")
        report.append(f"Functional Requirements: {len(self.functional_requirements)}")
        report.append(f"Non-Functional Requirements: {len(self.non_functional_requirements)}")
        report.append(f"Constraints: {len(self.constraints)}")
        report.append(f"Assumptions: {len(self.assumptions)}")

        report.append("\nPriority Distribution:")
        for priority, count in self.get_priority_summary().items():
            report.append(f"  {priority}: {count}")

        report.append("\nStakeholder Matrix:")
        for s in self.get_stakeholder_matrix():
            report.append(f"  {s['name']} ({s['role']}): {s['classification']}")

        return "\n".join(report)


def validate_requirement_data(data: Dict) -> Tuple[bool, List[str]]:
    """Validate requirement data"""
    errors = []

    if not data.get('id'):
        errors.append("Requirement must have an ID")
    if not data.get('title'):
        errors.append("Requirement must have a title")
    if not data.get('description'):
        errors.append("Requirement must have a description")

    return len(errors) == 0, errors


if __name__ == "__main__":
    # Example usage
    gatherer = RequirementsGatherer("Multi-Agent Planner")

    # Add a stakeholder
    stakeholder = Stakeholder(
        name="Project Manager",
        role="Project Lead",
        type=StakeholderType.KEY,
        interests=["Timeline", "Budget", "Quality"],
        influence=8,
        impact=8
    )
    gatherer.add_stakeholder(stakeholder)

    # Add a functional requirement
    req = FunctionalRequirement(
        id="FR-001",
        title="Agent Task Delegation",
        description="System must support automatic task delegation to agents",
        requirement_type=RequirementType.SYSTEM,
        priority=Priority.MUST_HAVE,
        source_stakeholder="Project Manager",
        acceptance_criteria=["Tasks delegated within 5 seconds", "Success rate > 95%"]
    )
    gatherer.add_functional_requirement(req)

    # Export and report
    gatherer.export_to_json("/tmp/requirements.json")
    print(gatherer.generate_report())
