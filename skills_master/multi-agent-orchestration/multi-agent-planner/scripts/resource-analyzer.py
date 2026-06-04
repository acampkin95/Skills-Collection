"""
Resource Analyzer Module

Analyzes project resources including:
- Skills inventory
- Tool inventory
- Time estimation
- Cost analysis
- Technology stack analysis
- Integration requirements
"""

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path


class SkillLevel(Enum):
    """Skill proficiency levels"""
    EXPERT = "Expert"
    ADVANCED = "Advanced"
    INTERMEDIATE = "Intermediate"
    BEGINNER = "Beginner"
    NONE = "None"


class ResourceStatus(Enum):
    """Resource availability status"""
    AVAILABLE = "Available"
    BUSY = "Busy"
    UNAVAILABLE = "Unavailable"
    PENDING = "Pending"


class IntegrationType(Enum):
    """Types of integrations"""
    API = "API"
    DATABASE = "Database"
    MESSAGING = "Messaging"
    FILE = "File Transfer"
    AUTH = "Authentication"
    MONITORING = "Monitoring"


@dataclass
class Skill:
    """Represents a skill with proficiency level"""
    name: str
    category: str
    level: SkillLevel
    years_experience: float = 0.0
    certifications: List[str] = field(default_factory=list)
    last_used: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "level": self.level.value,
            "years_experience": self.years_experience,
            "certifications": self.certifications,
            "last_used": self.last_used
        }


@dataclass
class TeamMember:
    """Represents a team member resource"""
    name: str
    role: str
    skills: List[Skill] = field(default_factory=list)
    availability_hours_per_week: float = 40.0
    hourly_rate: float = 0.0
    status: ResourceStatus = ResourceStatus.AVAILABLE
    start_date: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role,
            "skills": [s.to_dict() for s in self.skills],
            "availability_hours_per_week": self.availability_hours_per_week,
            "hourly_rate": self.hourly_rate,
            "status": self.status.value,
            "start_date": self.start_date
        }


@dataclass
class Tool:
    """Represents a tool resource"""
    name: str
    category: str
    version: str = ""
    license_type: str = "Open Source"
    cost_per_month: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    is_installed: bool = False
    documentation_url: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "version": self.version,
            "license_type": self.license_type,
            "cost_per_month": self.cost_per_month,
            "dependencies": self.dependencies,
            "is_installed": self.is_installed,
            "documentation_url": self.documentation_url
        }


@dataclass
class Technology:
    """Represents a technology in the stack"""
    name: str
    category: str
    purpose: str
    version: str = ""
    alternatives: List[str] = field(default_factory=list)
    risk_level: str = "Low"
    maintenance_responsibility: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "purpose": self.purpose,
            "version": self.version,
            "alternatives": self.alternatives,
            "risk_level": self.risk_level,
            "maintenance_responsibility": self.maintenance_responsibility
        }


@dataclass
class Integration:
    """Represents an integration requirement"""
    id: str
    name: str
    integration_type: IntegrationType
    source_system: str
    target_system: str
    frequency: str = "On Demand"
    data_format: str = "JSON"
    authentication_method: str = ""
    status: str = "pending"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "integration_type": self.integration_type.value,
            "source_system": self.source_system,
            "target_system": self.target_system,
            "frequency": self.frequency,
            "data_format": self.data_format,
            "authentication_method": self.authentication_method,
            "status": self.status
        }


@dataclass
class TaskEstimate:
    """Represents a time estimate for a task"""
    task_name: str
    task_id: str
    optimistic_hours: float = 0.0
    nominal_hours: float = 0.0
    pessimistic_hours: float = 0.0
    assigned_to: str = ""
    dependencies: List[str] = field(default_factory=list)

    def get_expected_hours(self) -> float:
        """Calculate PERT expected time"""
        return (self.optimistic_hours + 4 * self.nominal_hours + self.pessimistic_hours) / 6

    def get_standard_deviation(self) -> float:
        """Calculate standard deviation for risk analysis"""
        return (self.pessimistic_hours - self.optimistic_hours) / 6

    def to_dict(self) -> Dict:
        return {
            "task_name": self.task_name,
            "task_id": self.task_id,
            "optimistic_hours": self.optimistic_hours,
            "nominal_hours": self.nominal_hours,
            "pessimistic_hours": self.pessimistic_hours,
            "expected_hours": self.get_expected_hours(),
            "std_deviation": self.get_standard_deviation(),
            "assigned_to": self.assigned_to,
            "dependencies": self.dependencies
        }


@dataclass
class CostItem:
    """Represents a cost item"""
    category: str
    description: str
    estimated_cost: float
    actual_cost: float = 0.0
    is_recurring: bool = False
    frequency: str = ""
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "description": self.description,
            "estimated_cost": self.estimated_cost,
            "actual_cost": self.actual_cost,
            "is_recurring": self.is_recurring,
            "frequency": self.frequency,
            "notes": self.notes
        }


@dataclass
class ResourceAnalysis:
    """Container for resource analysis data"""
    project_name: str
    analysis_date: str = field(default_factory=lambda: datetime.now().isoformat())
    team: List[Dict] = field(default_factory=list)
    tools: List[Dict] = field(default_factory=list)
    technologies: List[Dict] = field(default_factory=list)
    integrations: List[Dict] = field(default_factory=list)
    task_estimates: List[Dict] = field(default_factory=list)
    cost_items: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "project_name": self.project_name,
            "analysis_date": self.analysis_date,
            "team": self.team,
            "tools": self.tools,
            "technologies": self.technologies,
            "integrations": self.integrations,
            "task_estimates": self.task_estimates,
            "cost_items": self.cost_items
        }


class ResourceAnalyzer:
    """Main class for resource analysis operations"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.team: List[TeamMember] = []
        self.tools: List[Tool] = []
        self.technologies: List[Technology] = []
        self.integrations: List[Integration] = []
        self.task_estimates: List[TaskEstimate] = []
        self.cost_items: List[CostItem] = []

    # Team Management
    def add_team_member(self, member: TeamMember) -> None:
        self.team.append(member)

    def get_team_skill_matrix(self) -> Dict:
        """Generate skill coverage matrix"""
        all_skills = set()
        for member in self.team:
            for skill in member.skills:
                all_skills.add(skill.name)

        matrix = {}
        for skill_name in all_skills:
            matrix[skill_name] = {
                "count": 0,
                "experts": 0,
                "members": []
            }
            for member in self.team:
                for skill in member.skills:
                    if skill.name == skill_name:
                        matrix[skill_name]["count"] += 1
                        if skill.level == SkillLevel.EXPERT:
                            matrix[skill_name]["experts"] += 1
                        matrix[skill_name]["members"].append(member.name)

        return matrix

    def identify_skill_gaps(self, required_skills: List[str]) -> List[Dict]:
        """Identify missing skills in the team"""
        skill_matrix = self.get_team_skill_matrix()
        gaps = []
        for skill in required_skills:
            if skill not in skill_matrix or skill_matrix[skill]["count"] == 0:
                gaps.append({
                    "skill": skill,
                    "status": "Missing",
                    "recommendation": "Hire or train team member"
                })
            elif skill_matrix[skill]["experts"] == 0:
                gaps.append({
                    "skill": skill,
                    "status": "No Expert",
                    "recommendation": "Consider external expertise"
                })
        return gaps

    def get_team_capacity(self) -> Dict:
        """Calculate total team capacity"""
        total_hours = sum(m.availability_hours_per_week for m in self.team)
        available_members = sum(1 for m in self.team if m.status == ResourceStatus.AVAILABLE)
        return {
            "total_members": len(self.team),
            "available_members": available_members,
            "total_weekly_hours": total_hours,
            "estimated_monthly_hours": total_hours * 4.33
        }

    # Tool Management
    def add_tool(self, tool: Tool) -> None:
        self.tools.append(tool)

    def get_tool_inventory(self) -> List[Dict]:
        return [t.to_dict() for t in self.tools]

    def get_tool_cost_summary(self) -> Dict:
        total_monthly = sum(t.cost_per_month for t in self.tools)
        by_category = {}
        for tool in self.tools:
            if tool.category not in by_category:
                by_category[tool.category] = 0.0
            by_category[tool.category] += tool.cost_per_month
        return {
            "total_monthly_cost": total_monthly,
            "by_category": by_category,
            "total_annual_cost": total_monthly * 12
        }

    # Technology Management
    def add_technology(self, tech: Technology) -> None:
        self.technologies.append(tech)

    def get_technology_stack(self) -> Dict:
        by_category = {}
        for tech in self.technologies:
            if tech.category not in by_category:
                by_category[tech.category] = []
            by_category[tech.category].append(tech.to_dict())
        return by_category

    def identify_technology_risks(self) -> List[Dict]:
        risks = []
        for tech in self.technologies:
            if tech.risk_level == "High":
                risks.append({
                    "technology": tech.name,
                    "category": tech.category,
                    "risk": "High maintenance/obsolescence risk",
                    "recommendation": f"Monitor {tech.name} and evaluate alternatives: {', '.join(tech.alternatives)}"
                })
        return risks

    # Integration Management
    def add_integration(self, integration: Integration) -> None:
        self.integrations.append(integration)

    def get_integration_summary(self) -> Dict:
        by_type = {}
        for integration in self.integrations:
            int_type = integration.integration_type.value
            if int_type not in by_type:
                by_type[int_type] = {"count": 0, "pending": 0, "complete": 0}
            by_type[int_type]["count"] += 1
            if integration.status == "complete":
                by_type[int_type]["complete"] += 1
            else:
                by_type[int_type]["pending"] += 1
        return by_type

    # Time Estimation
    def add_task_estimate(self, estimate: TaskEstimate) -> None:
        self.task_estimates.append(estimate)

    def get_schedule_summary(self) -> Dict:
        if not self.task_estimates:
            return {"total_expected_hours": 0, "critical_path": []}

        total_hours = sum(e.get_expected_hours() for e in self.task_estimates)

        # Find critical path (simplified - longest dependency chain)
        critical_path = self._calculate_critical_path()

        return {
            "total_expected_hours": total_hours,
            "critical_path": critical_path,
            "total_optimistic_hours": sum(e.optimistic_hours for e in self.task_estimates),
            "total_pessimistic_hours": sum(e.pessimistic_hours for e in self.task_estimates)
        }

    def _calculate_critical_path(self) -> List[str]:
        """Calculate critical path based on dependencies"""
        if not self.task_estimates:
            return []

        # Simple topological sort based implementation
        task_dict = {e.task_id: e for e in self.task_estimates}
        path = []

        def get_longest_path(task_id, visited=None):
            if visited is None:
                visited = set()
            if task_id in visited:
                return []
            visited.add(task_id)

            task = task_dict.get(task_id)
            if not task:
                return [task_id]

            if not task.dependencies:
                return [task_id]

            longest = []
            for dep in task.dependencies:
                dep_path = get_longest_path(dep, visited.copy())
                if len(dep_path) > len(longest):
                    longest = dep_path

            return longest + [task_id]

        # Start with tasks that have no dependents
        all_ids = set(e.task_id for e in self.task_estimates)
        has_dependent = set()
        for e in self.task_estimates:
            has_dependent.update(e.dependencies)

        roots = all_ids - has_dependent
        if not roots:
            roots = [list(all_ids)[0]]

        return get_longest_path(list(roots)[0])

    # Cost Analysis
    def add_cost_item(self, item: CostItem) -> None:
        self.cost_items.append(item)

    def get_cost_summary(self) -> Dict:
        total_estimated = sum(c.estimated_cost for c in self.cost_items)
        total_actual = sum(c.actual_cost for c in self.cost_items)

        by_category = {}
        for item in self.cost_items:
            if item.category not in by_category:
                by_category[item.category] = {"estimated": 0, "actual": 0}
            by_category[item.category]["estimated"] += item.estimated_cost
            by_category[item.category]["actual"] += item.actual_cost

        return {
            "total_estimated": total_estimated,
            "total_actual": total_actual,
            "by_category": by_category,
            "variance": total_estimated - total_actual
        }

    def get_burn_rate_analysis(self) -> Dict:
        """Analyze cost burn rate"""
        cost_summary = self.get_cost_summary()
        schedule = self.get_schedule_summary()

        total_hours = schedule.get("total_expected_hours", 0)
        daily_rate = 8  # Assuming 8 hour days

        if total_hours > 0:
            estimated_days = total_hours / daily_rate
            daily_burn = cost_summary["total_estimated"] / estimated_days if estimated_days > 0 else 0
        else:
            daily_burn = 0

        return {
            "total_budget": cost_summary["total_estimated"],
            "daily_burn_rate": daily_burn,
            "estimated_duration_days": total_hours / daily_rate if total_hours > 0 else 0
        }

    # Export/Import
    def export_to_yaml(self, filepath: str) -> None:
        analysis = ResourceAnalysis(
            project_name=self.project_name,
            team=[m.to_dict() for m in self.team],
            tools=[t.to_dict() for t in self.tools],
            technologies=[tech.to_dict() for tech in self.technologies],
            integrations=[i.to_dict() for i in self.integrations],
            task_estimates=[e.to_dict() for e in self.task_estimates],
            cost_items=[c.to_dict() for c in self.cost_items]
        )
        with open(filepath, 'w') as f:
            yaml.dump(analysis.to_dict(), f, default_flow_style=False, sort_keys=False)

    def export_to_json(self, filepath: str) -> None:
        analysis = ResourceAnalysis(
            project_name=self.project_name,
            team=[m.to_dict() for m in self.team],
            tools=[t.to_dict() for t in self.tools],
            technologies=[tech.to_dict() for tech in self.technologies],
            integrations=[i.to_dict() for i in self.integrations],
            task_estimates=[e.to_dict() for e in self.task_estimates],
            cost_items=[c.to_dict() for c in self.cost_items]
        )
        with open(filepath, 'w') as f:
            json.dump(analysis.to_dict(), f, indent=2)

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

    def generate_report(self) -> str:
        """Generate comprehensive resource analysis report"""
        report = []
        report.append(f"Resource Analysis Report for: {self.project_name}")
        report.append("=" * 70)

        # Team Summary
        team_capacity = self.get_team_capacity()
        report.append("\n[TEAM CAPACITY]")
        report.append(f"  Total Members: {team_capacity['total_members']}")
        report.append(f"  Available: {team_capacity['available_members']}")
        report.append(f"  Weekly Hours: {team_capacity['total_weekly_hours']}")
        report.append(f"  Monthly Hours: {team_capacity['estimated_monthly_hours']}")

        # Skill Gaps
        all_skills = set()
        for member in self.team:
            for skill in member.skills:
                all_skills.add(skill.name)

        # Tool Inventory
        tool_cost = self.get_tool_cost_summary()
        report.append("\n[TOOL COSTS]")
        report.append(f"  Monthly: ${tool_cost['total_monthly_cost']:,.2f}")
        report.append(f"  Annual: ${tool_cost['total_annual_cost']:,.2f}")

        # Technology
        tech_risks = self.identify_technology_risks()
        if tech_risks:
            report.append("\n[TECHNOLOGY RISKS]")
            for risk in tech_risks:
                report.append(f"  {risk['technology']}: {risk['recommendation']}")

        # Schedule
        schedule = self.get_schedule_summary()
        report.append("\n[SCHEDULE ESTIMATE]")
        report.append(f"  Total Hours: {schedule['total_expected_hours']:.1f}")
        report.append(f"  Critical Path: {' -> '.join(schedule['critical_path'])}")

        # Cost
        cost = self.get_cost_summary()
        burn = self.get_burn_rate_analysis()
        report.append("\n[COST ANALYSIS]")
        report.append(f"  Total Budget: ${cost['total_estimated']:,.2f}")
        report.append(f"  Daily Burn Rate: ${burn['daily_burn_rate']:,.2f}")

        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    analyzer = ResourceAnalyzer("Multi-Agent Planner")

    # Add team member
    developer = TeamMember(
        name="Alex",
        role="Senior Developer",
        availability_hours_per_week=40,
        hourly_rate=150
    )
    developer.skills.append(Skill("Python", "Programming", SkillLevel.EXPERT, 8))
    developer.skills.append(Skill("Docker", "DevOps", SkillLevel.ADVANCED, 4))
    analyzer.add_team_member(developer)

    # Add tool
    analyzer.add_tool(Tool(
        name="Docker",
        category="DevOps",
        license_type="Open Source",
        is_installed=True
    ))

    # Add task estimate
    analyzer.add_task_estimate(TaskEstimate(
        task_name="Setup Development Environment",
        task_id="TASK-001",
        optimistic_hours=2,
        nominal_hours=4,
        pessimistic_hours=8
    ))

    # Add cost
    analyzer.add_cost_item(CostItem(
        category="Infrastructure",
        description="Cloud hosting",
        estimated_cost=500,
        is_recurring=True,
        frequency="monthly"
    ))

    print(analyzer.generate_report())
