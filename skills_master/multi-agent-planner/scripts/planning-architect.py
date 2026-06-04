#!/usr/bin/env python3
"""
Multi-Agent Planning Architect

Core planning logic for project architecture, milestone decomposition,
roadmap generation, dependency mapping, timeline estimation, and risk assessment.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json


class PhaseType(Enum):
    """Types of project phases."""
    DISCOVERY = "discovery"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"


class RiskLevel(Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """Represents a single task in the project plan."""
    name: str
    description: str
    duration_days: int
    dependencies: List[str] = field(default_factory=list)
    assigned_role: Optional[str] = None
    priority: int = 1
    phase: Optional[str] = None
    status: str = "pending"
    estimated_effort_hours: float = 0.0
    resources_required: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "duration_days": self.duration_days,
            "dependencies": self.dependencies,
            "assigned_role": self.assigned_role,
            "priority": self.priority,
            "phase": self.phase,
            "status": self.status,
            "estimated_effort_hours": self.estimated_effort_hours,
            "resources_required": self.resources_required
        }


@dataclass
class Milestone:
    """Represents a project milestone."""
    name: str
    description: str
    target_date: Optional[datetime]
    tasks: List[Task] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    completion_criteria: List[str] = field(default_factory=list)
    status: str = "pending"
    progress_percentage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "tasks": [t.to_dict() for t in self.tasks],
            "dependencies": self.dependencies,
            "completion_criteria": self.completion_criteria,
            "status": self.status,
            "progress_percentage": self.progress_percentage
        }


@dataclass
class Dependency:
    """Represents a dependency between tasks or milestones."""
    source: str
    target: str
    dependency_type: str = "finish_to_start"
    lag_days: int = 0
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "dependency_type": self.dependency_type,
            "lag_days": self.lag_days,
            "description": self.description
        }


@dataclass
class Risk:
    """Represents a project risk."""
    id: str
    name: str
    description: str
    level: RiskLevel
    probability: float  # 0.0 to 1.0
    impact: str  # "low", "medium", "high"
    category: str
    mitigation_strategy: str = ""
    contingency_plan: str = ""
    owner: Optional[str] = None
    status: str = "identified"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level.value,
            "probability": self.probability,
            "impact": self.impact,
            "category": self.category,
            "mitigation_strategy": self.mitigation_strategy,
            "contingency_plan": self.contingency_plan,
            "owner": self.owner,
            "status": self.status
        }

    @property
    def risk_score(self) -> float:
        """Calculate risk score (probability * impact severity)."""
        impact_scores = {"low": 1, "medium": 2, "high": 3}
        return self.probability * impact_scores.get(self.impact, 1)


@dataclass
class ArchitecturePattern:
    """Represents an architecture pattern recommendation."""
    name: str
    description: str
    applicable_scenarios: str
    pros: List[str]
    cons: List[str]
    complexity: str
    scalability: str
    maintainability: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "applicable_scenarios": self.applicable_scenarios,
            "pros": self.pros,
            "cons": self.cons,
            "complexity": self.complexity,
            "scalability": self.scalability,
            "maintainability": self.maintainability
        }


class PlanningArchitect:
    """
    Core planning architect for multi-agent project planning.

    Features:
    - Project architecture templates
    - Milestone decomposition
    - Roadmap generation
    - Dependency mapping
    - Timeline estimation
    - Risk assessment
    """

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.tasks: Dict[str, Task] = {}
        self.milestones: Dict[str, Milestone] = {}
        self.dependencies: List[Dependency] = []
        self.risks: Dict[str, Risk] = {}
        self.architecture_patterns: List[ArchitecturePattern] = []
        self.project_start_date: Optional[datetime] = None
        self.project_end_date: Optional[datetime] = None

    def add_task(self, task: Task) -> None:
        """Add a task to the project plan."""
        self.tasks[task.name] = task

    def add_milestone(self, milestone: Milestone) -> None:
        """Add a milestone to the project plan."""
        self.milestones[milestone.name] = milestone

    def add_dependency(self, dependency: Dependency) -> None:
        """Add a dependency between tasks or milestones."""
        self.dependencies.append(dependency)

    def add_risk(self, risk: Risk) -> None:
        """Add a risk to the project risk register."""
        self.risks[risk.id] = risk

    def set_project_timeline(self, start_date: datetime, end_date: datetime) -> None:
        """Set the overall project timeline."""
        self.project_start_date = start_date
        self.project_end_date = end_date

    def decompose_milestones(self, goals: List[str]) -> List[Milestone]:
        """
        Decompose project goals into milestones.

        Args:
            goals: List of high-level project goals

        Returns:
            List of decomposed milestones
        """
        milestone_templates = {
            "discovery": Milestone(
                name="Discovery Complete",
                description="Requirements gathering and initial analysis",
                target_date=None,
                completion_criteria=[
                    "Requirements document approved",
                    "Stakeholder alignment confirmed",
                    "Initial risk assessment complete"
                ]
            ),
            "design": Milestone(
                name="Design Complete",
                description="Architecture and design finalized",
                target_date=None,
                completion_criteria=[
                    "Technical architecture approved",
                    "Design documents reviewed",
                    "Technical debt assessment complete"
                ]
            ),
            "development": Milestone(
                name="Development Complete",
                description="Core development work finished",
                target_date=None,
                completion_criteria=[
                    "All features implemented",
                    "Code review passed",
                    "Unit test coverage met"
                ]
            ),
            "testing": Milestone(
                name="Testing Complete",
                description="All testing phases finished",
                target_date=None,
                completion_criteria=[
                    "Integration tests passed",
                    "Performance benchmarks met",
                    "Security audit complete"
                ]
            ),
            "deployment": Milestone(
                name="Deployment Complete",
                description="Production deployment successful",
                target_date=None,
                completion_criteria=[
                    "Production deployment verified",
                    "Monitoring active",
                    "Rollback plan tested"
                ]
            )
        }

        for goal in goals:
            # Create goal-specific milestones
            for phase in ["discovery", "design", "development", "testing", "deployment"]:
                if phase in milestone_templates:
                    ms = milestone_templates[phase]
                    new_ms = Milestone(
                        name=f"{ms.name} - {goal}",
                        description=f"{ms.description} for {goal}",
                        target_date=None,
                        completion_criteria=ms.completion_criteria.copy()
                    )
                    self.add_milestone(new_ms)

        return list(self.milestones.values())

    def generate_roadmap(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Generate a project roadmap from tasks.

        Args:
            tasks: List of project tasks

        Returns:
            Roadmap dictionary with phases and timeline
        """
        phases = {}

        for task in tasks:
            phase = task.phase or "general"
            if phase not in phases:
                phases[phase] = {
                    "tasks": [],
                    "total_duration": 0,
                    "total_effort": 0.0
                }

            phases[phase]["tasks"].append(task.to_dict())
            phases[phase]["total_duration"] += task.duration_days
            phases[phase]["total_effort"] += task.estimated_effort_hours

        # Calculate timeline
        timeline = []
        current_date = self.project_start_date or datetime.now()

        for phase_name, phase_data in phases.items():
            phase_start = current_date
            phase_end = current_date + timedelta(days=phase_data["total_duration"])

            timeline.append({
                "phase": phase_name,
                "start_date": phase_start.isoformat(),
                "end_date": phase_end.isoformat(),
                "duration_days": phase_data["total_duration"],
                "tasks_count": len(phase_data["tasks"]),
                "effort_hours": phase_data["total_effort"]
            })

            current_date = phase_end

        return {
            "project": self.project_name,
            "total_duration_days": sum(p["duration_days"] for p in timeline),
            "phases": timeline,
            "milestones": [m.to_dict() for m in self.milestones.values()]
        }

    def map_dependencies(self) -> Dict[str, List[str]]:
        """
        Map task dependencies for critical path analysis.

        Returns:
            Dictionary mapping task names to their dependencies
        """
        dependency_map = {}

        for dep in self.dependencies:
            if dep.source not in dependency_map:
                dependency_map[dep.source] = []
            dependency_map[dep.source].append({
                "target": dep.target,
                "type": dep.dependency_type,
                "lag_days": dep.lag_days
            })

        # Also include dependencies from tasks
        for task_name, task in self.tasks.items():
            if task.dependencies:
                dependency_map[task_name] = [
                    {"target": d, "type": "finish_to_start", "lag_days": 0}
                    for d in task.dependencies
                ]

        return dependency_map

    def calculate_critical_path(self) -> List[str]:
        """
        Calculate the critical path of the project.

        Returns:
            List of task names in critical path order
        """
        # Simple critical path calculation based on task dependencies and durations
        task_durations = {name: task.duration_days for name, task in self.tasks.items()}
        dependencies = self.map_dependencies()

        # Build dependency graph
        graph = {name: set() for name in self.tasks}
        for task_name, deps in dependencies.items():
            for dep in deps:
                if dep["target"] in graph:
                    graph[dep["target"]].add(task_name)

        # Calculate earliest start and finish times
        earliest_start = {}
        earliest_finish = {}

        def calculate_earliest(task: str):
            if task in earliest_start:
                return earliest_finish[task]

            max_finish = 0
            for dep in graph.get(task, []):
                finish = calculate_earliest(dep)
                max_finish = max(max_finish, finish)

            earliest_start[task] = max_finish
            earliest_finish[task] = max_finish + task_durations.get(task, 1)
            return earliest_finish[task]

        for task in self.tasks:
            calculate_earliest(task)

        # Find critical path by following longest path
        critical_path = []
        current = max(earliest_finish, key=earliest_finish.get) if earliest_finish else None

        while current:
            critical_path.insert(0, current)
            predecessors = [t for t, deps in dependencies.items()
                          if any(d["target"] == current for d in deps)]
            if predecessors:
                current = max(predecessors, key=lambda x: earliest_start.get(x, 0))
            else:
                current = None

        return critical_path

    def estimate_timeline(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Estimate project timeline with buffers.

        Args:
            tasks: List of project tasks

        Returns:
            Timeline estimation with buffers
        """
        base_duration = sum(task.duration_days for task in tasks)

        # Apply risk-based buffers
        risk_buffer = sum(
            (r.risk_score * 0.1) for r in self.risks.values()
            if r.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )

        # Add contingency buffer (typically 15-20%)
        contingency_buffer = base_duration * 0.2

        # Complexity multiplier based on task count and dependencies
        complexity_factor = 1 + (len(tasks) / 100) * 0.1

        estimated_duration = int(base_duration * complexity_factor + contingency_buffer)

        return {
            "base_duration_days": base_duration,
            "risk_buffer_days": int(base_duration * risk_buffer) if risk_buffer > 0 else 0,
            "contingency_days": contingency_buffer,
            "complexity_factor": complexity_factor,
            "estimated_total_days": estimated_duration,
            "start_date": self.project_start_date.isoformat() if self.project_start_date else None,
            "end_date": (self.project_start_date + timedelta(days=estimated_duration)).isoformat()
                       if self.project_start_date else None
        }

    def assess_risks(self) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment.

        Returns:
            Risk assessment report
        """
        risk_by_category = {}
        risk_by_level = {level: [] for level in RiskLevel}

        for risk in self.risks.values():
            # Group by category
            if risk.category not in risk_by_category:
                risk_by_category[risk.category] = []
            risk_by_category[risk.category].append(risk.to_dict())

            # Group by level
            risk_by_level[risk.level].append(risk.name)

        # Calculate overall risk score
        total_score = sum(r.risk_score for r in self.risks.values())
        avg_score = total_score / len(self.risks) if self.risks else 0

        overall_risk = "low"
        if avg_score > 2.0:
            overall_risk = "critical"
        elif avg_score > 1.5:
            overall_risk = "high"
        elif avg_score > 1.0:
            overall_risk = "medium"

        return {
            "total_risks": len(self.risks),
            "overall_risk_level": overall_risk,
            "average_risk_score": round(avg_score, 2),
            "risks_by_category": {k: len(v) for k, v in risk_by_category.items()},
            "risks_by_level": {k.value: len(v) for k, v in risk_by_level.items()},
            "critical_risks": [r.to_dict() for r in self.risks.values()
                             if r.level == RiskLevel.CRITICAL],
            "high_risks": [r.to_dict() for r in self.risks.values()
                          if r.level == RiskLevel.HIGH]
        }

    def recommend_architecture_pattern(
        self,
        requirements: Dict[str, Any]
    ) -> List[ArchitecturePattern]:
        """
        Recommend architecture patterns based on requirements.

        Args:
            requirements: Project requirements dictionary

        Returns:
            List of recommended architecture patterns ranked by fit
        """
        patterns = [
            ArchitecturePattern(
                name="Microservices",
                description="Distributed system architecture with independently deployable services",
                适用场景="Large-scale applications requiring scalability and independent deployment",
                pros=[
                    "Independent scaling and deployment",
                    "Technology flexibility per service",
                    "Improved fault isolation",
                    "Easier to understand and maintain larger systems"
                ],
                cons=[
                    "Increased complexity in distribution",
                    "Network latency between services",
                    "Data consistency challenges",
                    "Operational overhead"
                ],
                complexity="high",
                scalability="excellent",
                maintainability="medium"
            ),
            ArchitecturePattern(
                name="Monolithic",
                description="Single unified application with all components tightly coupled",
                适用场景="Small to medium applications with simple requirements",
                pros=[
                    "Simple development and deployment",
                    "Good performance (no network calls)",
                    "Easier debugging and testing",
                    "Lower operational overhead"
                ],
                cons=[
                    "Difficult to scale individual components",
                    "Technology lock-in",
                    "Codebase becomes unwieldy over time",
                    "Long deployment cycles"
                ],
                complexity="low",
                scalability="limited",
                maintainability="decreases with size"
            ),
            ArchitecturePattern(
                name="Event-Driven",
                description="Architecture based on event production and consumption",
                适用场景="Systems requiring real-time processing and loose coupling",
                pros=[
                    "Loose coupling between components",
                    "Easy to add new event handlers",
                    "Good for real-time systems",
                    "Scalable message processing"
                ],
                cons=[
                    "Eventual consistency",
                    "Complex event ordering",
                    "Debugging challenges",
                    "Message broker dependency"
                ],
                complexity="medium",
                scalability="excellent",
                maintainability="medium"
            ),
            ArchitecturePattern(
                name="Layered (N-Tier)",
                description="Separation of concerns through distinct layers",
                适用场景="Traditional business applications with clear separation of concerns",
                pros=[
                    "Clear separation of concerns",
                    "Easy to understand and maintain",
                    "Good for team organization",
                    "Established patterns and practices"
                ],
                cons=[
                    "Potential performance overhead",
                    "Layers can become rigid",
                    "Tight coupling between adjacent layers",
                    "Not ideal for distributed systems"
                ],
                complexity="low",
                scalability="good",
                maintainability="good"
            ),
            ArchitecturePattern(
                name="CQRS",
                description="Command Query Responsibility Segregation",
                适用场景="Systems with complex read/write patterns and scalability needs",
                pros=[
                    "Optimized read and write models",
                    "Scalable read and write independently",
                    "Better security for commands",
                    "Flexible data models"
                ],
                cons=[
                    "Increased complexity",
                    "Eventual consistency",
                    "Learning curve",
                    "Infrastructure requirements"
                ],
                complexity="high",
                scalability="excellent",
                maintainability="medium"
            )
        ]

        # Score patterns based on requirements
        scored_patterns = []
        for pattern in patterns:
            score = 0

            # Check scalability requirements
            if requirements.get("scalability_needed", False):
                if pattern.scalability in ["excellent", "good"]:
                    score += 2

            # Check team size
            team_size = requirements.get("team_size", 5)
            if team_size > 10 and pattern.complexity == "low":
                score -= 1  # Low complexity may not suit large teams
            elif team_size < 5 and pattern.complexity == "high":
                score -= 2

            # Check timeline constraints
            timeline_months = requirements.get("timeline_months", 3)
            if timeline_months < 3 and pattern.complexity == "high":
                score -= 2
            elif timeline_months > 12 and pattern.complexity == "low":
                score -= 1

            # Real-time requirements
            if requirements.get("real_time", False) and pattern.name == "Event-Driven":
                score += 3

            scored_patterns.append((pattern, score))

        # Sort by score
        scored_patterns.sort(key=lambda x: x[1], reverse=True)

        self.architecture_patterns = [p for p, _ in scored_patterns]
        return [p for p, _ in scored_patterns]

    def generate_project_plan(self) -> Dict[str, Any]:
        """
        Generate comprehensive project plan.

        Returns:
            Complete project plan with all components
        """
        return {
            "project_name": self.project_name,
            "timeline": self.estimate_timeline(list(self.tasks.values())),
            "roadmap": self.generate_roadmap(list(self.tasks.values())),
            "critical_path": self.calculate_critical_path(),
            "dependency_map": self.map_dependencies(),
            "risk_assessment": self.assess_risks(),
            "architecture_recommendations": [p.to_dict() for p in self.architecture_patterns],
            "milestones": [m.to_dict() for m in self.milestones.values()],
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "total_tasks": len(self.tasks),
            "total_milestones": len(self.milestones),
            "total_risks": len(self.risks)
        }

    def export_plan(self, filepath: str) -> None:
        """Export project plan to JSON file."""
        plan = self.generate_project_plan()
        with open(filepath, 'w') as f:
            json.dump(plan, f, indent=2, default=str)


def create_project_plan(
    project_name: str,
    goals: List[str],
    requirements: Dict[str, Any],
    known_risks: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a complete project plan.

    Args:
        project_name: Name of the project
        goals: List of project goals
        requirements: Project requirements
        known_risks: Optional list of known risks

    Returns:
        Complete project plan
    """
    planner = PlanningArchitect(project_name)

    # Decompose milestones from goals
    planner.decompose_milestones(goals)

    # Recommend architecture patterns
    planner.recommend_architecture_pattern(requirements)

    # Add risks if provided
    if known_risks:
        for risk_data in known_risks:
            risk = Risk(
                id=risk_data.get("id", f"risk_{len(planner.risks)}"),
                name=risk_data["name"],
                description=risk_data["description"],
                level=RiskLevel(risk_data["level"]),
                probability=risk_data["probability"],
                impact=risk_data["impact"],
                category=risk_data["category"],
                mitigation_strategy=risk_data.get("mitigation_strategy", ""),
                contingency_plan=risk_data.get("contingency_plan", "")
            )
            planner.add_risk(risk)

    # Set project timeline if provided
    if "start_date" in requirements:
        planner.set_project_timeline(
            requirements["start_date"],
            requirements.get("end_date", requirements["start_date"])
        )

    return planner.generate_project_plan()


if __name__ == "__main__":
    # Example usage
    plan = create_project_plan(
        project_name="Example Project",
        goals=["Build API", "Create UI", "Deploy to Production"],
        requirements={
            "scalability_needed": True,
            "team_size": 5,
            "timeline_months": 6,
            "real_time": False
        },
        known_risks=[
            {
                "id": "risk_1",
                "name": "Resource Constraints",
                "description": "Key team members may be unavailable",
                "level": "medium",
                "probability": 0.4,
                "impact": "high",
                "category": "resource",
                "mitigation_strategy": "Cross-train team members",
                "contingency_plan": "Adjust timeline and scope"
            }
        ]
    )

    print(json.dumps(plan, indent=2))
