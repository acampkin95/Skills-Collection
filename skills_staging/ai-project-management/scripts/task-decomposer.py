#!/usr/bin/env python3
"""
Task Decomposer - Automatic task decomposition and analysis.

This module provides capabilities for:
- Automatic task decomposition into subtasks
- Dependency mapping between tasks
- Effort estimation
- Parallelization analysis
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Complexity levels for tasks."""
    TRIVIAL = 1
    SIMPLE = 2
    MODERATE = 3
    COMPLEX = 4
    VERY_COMPLEX = 5


class TaskType(Enum):
    """Types of development tasks."""
    FEATURE_IMPLEMENTATION = "feature"
    REFACTORING = "refactor"
    BUG_FIX = "bug_fix"
    TESTING = "testing"
    DOCUMENTATION = "docs"
    INFRASTRUCTURE = "infrastructure"
    RESEARCH = "research"
    CODE_REVIEW = "review"
    DEPLOYMENT = "deployment"
    CONFIGURATION = "config"


@dataclass
class Subtask:
    """Represents a decomposed subtask."""
    id: str
    name: str
    description: str
    task_type: TaskType
    complexity: TaskComplexity
    dependencies: List[str] = field(default_factory=list)
    estimated_minutes: int = 0
    required_capabilities: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    risk_level: str = "low"
    parallelizable: bool = True
    parent_task: str = ""
    order: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type.value,
            "complexity": self.complexity.name,
            "dependencies": self.dependencies,
            "estimated_minutes": self.estimated_minutes,
            "required_capabilities": self.required_capabilities,
            "acceptance_criteria": self.acceptance_criteria,
            "risk_level": self.risk_level,
            "parallelizable": self.parallelizable,
            "parent_task": self.parent_task,
            "order": self.order,
            "metadata": self.metadata
        }


@dataclass
class DecompositionResult:
    """Result of task decomposition."""
    task_id: str
    original_description: str
    subtasks: List[Subtask]
    total_estimated_minutes: int
    parallel_groups: List[List[str]]
    critical_path: List[str]
    risks: List[str]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "original_description": self.original_description,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "total_estimated_minutes": self.total_estimated_minutes,
            "parallel_groups": self.parallel_groups,
            "critical_path": self.critical_path,
            "risks": self.risks,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }


class TaskDecomposer:
    """
    Automatic task decomposition engine.

    Analyzes complex tasks and breaks them down into manageable subtasks
    with proper dependencies, estimates, and parallelization opportunities.
    """

    # Task type to capabilities mapping
    TASK_TYPE_CAPABILITIES = {
        TaskType.FEATURE_IMPLEMENTATION: ["coding", "design", "testing"],
        TaskType.REFACTORING: ["coding", "testing", "code_review"],
        TaskType.BUG_FIX: ["debugging", "testing", "code_review"],
        TaskType.TESTING: ["testing", "automation", "documentation"],
        TaskType.DOCUMENTATION: ["documentation", "technical_writing"],
        TaskType.INFRASTRUCTURE: ["devops", "infrastructure", "security"],
        TaskType.RESEARCH: ["analysis", "documentation", "evaluation"],
        TaskType.CODE_REVIEW: ["code_review", "security", "testing"],
        TaskType.DEPLOYMENT: ["devops", "infrastructure", "monitoring"],
        TaskType.CONFIGURATION: ["infrastructure", "automation", "documentation"]
    }

    # Complexity multipliers (minutes per complexity point)
    COMPLEXITY_MULTIPLIERS = {
        TaskComplexity.TRIVIAL: 5,
        TaskComplexity.SIMPLE: 15,
        TaskComplexity.MODERATE: 30,
        TaskComplexity.COMPLEX: 60,
        TaskComplexity.VERY_COMPLEX: 120
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.task_templates = self._load_task_templates()
        self.decomposition_history: List[DecompositionResult] = []

    def _load_task_templates(self) -> Dict[str, List[str]]:
        """Load task decomposition templates."""
        return {
            "api": [
                "Define API specification",
                "Create data models",
                "Implement API endpoints",
                "Add input validation",
                "Write API documentation",
                "Create integration tests"
            ],
            "frontend": [
                "Design component structure",
                "Implement UI components",
                "Add state management",
                "Style components",
                "Implement user interactions",
                "Test user flows"
            ],
            "backend": [
                "Design data schema",
                "Implement business logic",
                "Create database queries",
                "Add caching layer",
                "Implement authentication",
                "Write unit tests"
            ],
            "refactor": [
                "Analyze existing code",
                "Identify refactoring targets",
                "Create comprehensive tests",
                "Apply refactoring changes",
                "Verify tests pass",
                "Update documentation"
            ],
            "feature": [
                "Gather requirements",
                "Design solution",
                "Implement core functionality",
                "Add edge case handling",
                "Write tests",
                "Code review",
                "Update documentation"
            ]
        }

    def decompose(
        self,
        task_description: str,
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DecompositionResult:
        """
        Decompose a complex task into subtasks.

        Args:
            task_description: Description of the task to decompose
            task_id: Optional task ID
            context: Additional context about the project

        Returns:
            DecompositionResult with subtasks and analysis
        """
        task_id = task_id or f"decomp-{uuid.uuid4().hex[:8]}"

        logger.info(f"Decomposing task: {task_description[:100]}...")

        # Analyze the task
        task_type = self._identify_task_type(task_description)
        complexity = self._estimate_complexity(task_description)

        # Get template or custom decomposition
        if self.config.get('use_templates', True):
            subtasks = self._use_template(task_description, task_type, task_id)
        else:
            subtasks = self._analyze_and_decompose(task_description, task_type, complexity, task_id)

        # Analyze dependencies and parallelization
        subtasks = self._analyze_dependencies(subtasks)

        # Calculate estimates
        subtasks = self._calculate_estimates(subtasks, complexity)

        # Identify parallel groups
        parallel_groups = self._identify_parallel_groups(subtasks)

        # Find critical path
        critical_path = self._find_critical_path(subtasks, parallel_groups)

        # Identify risks
        risks = self._identify_risks(subtasks, task_description)

        # Generate recommendations
        recommendations = self._generate_recommendations(subtasks, parallel_groups, risks)

        result = DecompositionResult(
            task_id=task_id,
            original_description=task_description,
            subtasks=subtasks,
            total_estimated_minutes=sum(s.estimated_minutes for s in subtasks),
            parallel_groups=parallel_groups,
            critical_path=critical_path,
            risks=risks,
            recommendations=recommendations
        )

        self.decomposition_history.append(result)
        return result

    def _identify_task_type(self, description: str) -> TaskType:
        """Identify the type of task from description."""
        desc_lower = description.lower()

        type_keywords = {
            TaskType.FEATURE_IMPLEMENTATION: ["implement", "add", "create", "build", "feature"],
            TaskType.REFACTORING: ["refactor", "rewrite", "restructure", "improve"],
            TaskType.BUG_FIX: ["fix", "bug", "issue", "error", "problem", "crash"],
            TaskType.TESTING: ["test", "coverage", "verify", "validate"],
            TaskType.DOCUMENTATION: ["document", "docs", "readme", "comment"],
            TaskType.INFRASTRUCTURE: ["infrastructure", "deploy", "server", "config"],
            TaskType.RESEARCH: ["research", "investigate", "explore", "evaluate"],
            TaskType.CODE_REVIEW: ["review", "audit", "assess"],
            TaskType.DEPLOYMENT: ["deploy", "release", "publish", "ship"],
            TaskType.CONFIGURATION: ["configure", "setup", "install"]
        }

        for task_type, keywords in type_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                return task_type

        return TaskType.FEATURE_IMPLEMENTATION  # Default

    def _estimate_complexity(self, description: str) -> TaskComplexity:
        """Estimate task complexity from description."""
        # Count indicators
        indicators = {
            TaskComplexity.TRIVIAL: ["simple", "easy", "small", "quick"],
            TaskComplexity.SIMPLE: ["basic", "straightforward"],
            TaskComplexity.MODERATE: ["moderate", "standard", "typical"],
            TaskComplexity.COMPLEX: ["complex", "advanced", "sophisticated"],
            TaskComplexity.VERY_COMPLEX: ["very complex", "highly complex", "enterprise", "distributed"]
        }

        desc_lower = description.lower()

        for complexity, keywords in indicators.items():
            if any(kw in desc_lower for kw in keywords):
                return complexity

        # Estimate by length and scope
        word_count = len(description.split())
        if word_count < 10:
            return TaskComplexity.TRIVIAL
        elif word_count < 30:
            return TaskComplexity.SIMPLE
        elif word_count < 60:
            return TaskComplexity.MODERATE
        elif word_count < 100:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.VERY_COMPLEX

    def _use_template(
        self,
        description: str,
        task_type: TaskType,
        parent_id: str
    ) -> List[Subtask]:
        """Use a template to generate subtasks."""
        subtasks = []

        # Try to match a template
        template_key = None
        for key in self.task_templates.keys():
            if key in description.lower():
                template_key = key
                break

        if not template_key:
            template_key = task_type.value

        template_steps = self.task_templates.get(template_key, self.task_templates["feature"])

        for i, step in enumerate(template_steps):
            subtask = Subtask(
                id=f"{parent_id}-st{i+1}",
                name=step,
                description=f"Complete {step.lower()} for the task",
                task_type=task_type,
                complexity=self._step_complexity(step, i, len(template_steps)),
                parent_task=parent_id,
                order=i
            )
            subtasks.append(subtask)

        return subtasks

    def _step_complexity(
        self,
        step: str,
        position: int,
        total_steps: int
    ) -> TaskComplexity:
        """Determine complexity of an individual step."""
        complex_keywords = ["design", "architecture", "comprehensive", "complete"]
        simple_keywords = ["update", "simple", "quick"]

        step_lower = step.lower()

        if any(kw in step_lower for kw in complex_keywords):
            return TaskComplexity.COMPLEX
        elif any(kw in step_lower for kw in simple_keywords):
            return TaskComplexity.SIMPLE

        # Middle steps are typically more complex
        if position == 0:  # First step often simpler
            return TaskComplexity.SIMPLE
        elif position == total_steps - 1:  # Last step often simpler
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MODERATE

    def _analyze_and_decompose(
        self,
        description: str,
        task_type: TaskType,
        complexity: TaskComplexity,
        parent_id: str
    ) -> List[Subtask]:
        """Use LLM-like analysis to decompose task."""
        # This is a placeholder for more sophisticated decomposition
        # In practice, you might call an LLM here

        subtasks = []

        # Create a basic subtask
        subtask = Subtask(
            id=f"{parent_id}-st1",
            name="Analyze and implement",
            description=description,
            task_type=task_type,
            complexity=complexity,
            parent_task=parent_id,
            order=0
        )
        subtasks.append(subtask)

        return subtasks

    def _analyze_dependencies(self, subtasks: List[Subtask]) -> List[Subtask]:
        """Analyze and set up dependencies between subtasks."""
        if not subtasks:
            return subtasks

        # First subtask has no dependencies
        # Each subsequent subtask depends on the previous one
        for i, subtask in enumerate(subtasks):
            if i > 0:
                subtask.dependencies = [subtasks[i-1].id]

        return subtasks

    def _calculate_estimates(
        self,
        subtasks: List[Subtask],
        overall_complexity: TaskComplexity
    ) -> List[Subtask]:
        """Calculate time estimates for subtasks."""
        base_minutes = self.COMPLEXITY_MULTIPLIERS.get(
            overall_complexity, TaskComplexity.MODERATE
        )

        for i, subtask in enumerate(subtasks):
            # Adjust based on position (first and last tend to be quicker)
            position_factor = 1.0
            if i == 0 or i == len(subtasks) - 1:
                position_factor = 0.8

            # Adjust based on complexity
            complexity_multiplier = {
                TaskComplexity.TRIVIAL: 0.3,
                TaskComplexity.SIMPLE: 0.6,
                TaskComplexity.MODERATE: 1.0,
                TaskComplexity.COMPLEX: 1.5,
                TaskComplexity.VERY_COMPLEX: 2.0
            }.get(subtask.complexity, 1.0)

            subtask.estimated_minutes = int(
                base_minutes * complexity_multiplier * position_factor
            )

            # Set capabilities based on task type
            subtask.required_capabilities = self.TASK_TYPE_CAPABILITIES.get(
                subtask.task_type,
                ["coding"]
            )

            # Set acceptance criteria
            subtask.acceptance_criteria = self._generate_acceptance_criteria(subtask)

            # Set risk level
            subtask.risk_level = self._assess_risk(subtask)

        return subtasks

    def _generate_acceptance_criteria(self, subtask: Subtask) -> List[str]:
        """Generate acceptance criteria for a subtask."""
        criteria = [
            f"Complete {subtask.name.lower()}",
            "Code passes linting",
            "Tests pass",
            "No regressions"
        ]

        if subtask.task_type == TaskType.TESTING:
            criteria = [
                "Test cases cover all requirements",
                "Test coverage maintained or improved",
                "All tests pass",
                "Edge cases handled"
            ]
        elif subtask.task_type == TaskType.DOCUMENTATION:
            criteria = [
                "Documentation is complete",
                "Examples work correctly",
                "No broken links",
                "Follows style guide"
            ]

        return criteria

    def _assess_risk(self, subtask: Subtask) -> str:
        """Assess risk level for a subtask."""
        high_risk_factors = [
            subtask.complexity == TaskComplexity.VERY_COMPLEX,
            len(subtask.dependencies) > 2,
            "infrastructure" in [c.lower() for c in subtask.required_capabilities],
            "deployment" in subtask.task_type.value
        ]

        if sum(high_risk_factors) >= 2:
            return "high"
        elif sum(high_risk_factors) == 1:
            return "medium"
        else:
            return "low"

    def _identify_parallel_groups(self, subtasks: List[Subtask]) -> List[List[str]]:
        """Identify groups of tasks that can run in parallel."""
        groups = []
        assigned = set()

        # Sort by order to maintain logical grouping
        sorted_tasks = sorted(subtasks, key=lambda x: x.order)

        for subtask in sorted_tasks:
            if subtask.id in assigned:
                continue

            # Start a new group
            group = [subtask.id]
            assigned.add(subtask.id)

            # Add parallelizable tasks that don't depend on this group
            for other in sorted_tasks:
                if other.id in assigned:
                    continue

                # Can run in parallel if:
                # 1. Marked as parallelizable
                # 2. No dependencies on tasks in this group
                if other.parallelizable:
                    deps_met = all(
                        dep not in [g for g in group]
                        for dep in other.dependencies
                    )
                    if deps_met:
                        group.append(other.id)
                        assigned.add(other.id)

            groups.append(group)

        return groups

    def _find_critical_path(
        self,
        subtasks: List[Subtask],
        parallel_groups: List[List[str]]
    ) -> List[str]:
        """Find the critical path through the task graph."""
        # Simple critical path: longest chain of sequential tasks
        task_map = {s.id: s for s in subtasks}
        critical_path = []
        visited = set()

        def find_longest_path(task_id: str, depth: int) -> Tuple[List[str], int]:
            if task_id in visited:
                return [], 0

            visited.add(task_id)
            task = task_map.get(task_id)
            if not task:
                return [], 0

            # Find the next task that depends on this one
            next_tasks = [
                s.id for s in subtasks
                if task_id in s.dependencies and s.id not in visited
            ]

            if not next_tasks:
                return [task_id], task.estimated_minutes

            best_path = []
            best_duration = 0
            for next_id in next_tasks:
                path, duration = find_longest_path(next_id, depth + 1)
                if duration > best_duration:
                    best_path = path
                    best_duration = duration

            return [task_id] + best_path, task.estimated_minutes + best_duration

        # Start from tasks with no dependencies
        root_tasks = [s for s in subtasks if not s.dependencies]

        if not root_tasks and subtasks:
            root_tasks = [subtasks[0]]

        longest = []
        max_duration = 0
        for root in root_tasks:
            visited.clear()
            path, duration = find_longest_path(root.id, 0)
            if duration > max_duration:
                longest = path
                max_duration = duration

        return longest

    def _identify_risks(
        self,
        subtasks: List[Subtask],
        original_description: str
    ) -> List[str]:
        """Identify potential risks in the task decomposition."""
        risks = []

        # Check for high-risk subtasks
        high_risk_count = sum(1 for s in subtasks if s.risk_level == "high")
        if high_risk_count > 0:
            risks.append(f"{high_risk_count} high-risk subtask(s) require careful planning")

        # Check for circular dependencies
        all_deps = set()
        for s in subtasks:
            for dep in s.dependencies:
                if dep in all_deps:
                    risks.append("Potential circular dependency detected")
                    break
                all_deps.add(dep)

        # Check for unbalanced estimates
        total = sum(s.estimated_minutes for s in subtasks)
        if subtasks:
            avg = total / len(subtasks)
            for s in subtasks:
                if s.estimated_minutes > avg * 3:
                    risks.append(f"Subtask '{s.name}' has unusually high estimate")

        # Check for lack of parallelization
        if len(subtasks) > 3 and all(s.parallelizable for s in subtasks):
            if len(self._identify_parallel_groups(subtasks)) == len(subtasks):
                risks.append("No parallelization opportunity - consider further decomposition")

        return risks

    def _generate_recommendations(
        self,
        subtasks: List[Subtask],
        parallel_groups: List[List[str]],
        risks: List[str]
    ) -> List[str]:
        """Generate recommendations for task execution."""
        recommendations = []

        if len(parallel_groups) > 1:
            recommendations.append(
                f"Tasks can be parallelized into {len(parallel_groups)} groups"
            )

        if len(subtasks) > 10:
            recommendations.append(
                "Consider breaking into multiple phases for better management"
            )

        high_risk = [s for s in subtasks if s.risk_level == "high"]
        if high_risk:
            recommendations.append(
                f"Address {len(high_risk)} high-risk task(s) early in planning"
            )

        # Check for appropriate subtask size
        large_tasks = [s for s in subtasks if s.estimated_minutes > 120]
        if large_tasks:
            recommendations.append(
                f"{len(large_tasks)} task(s) exceed 2 hours - consider further breakdown"
            )

        if not recommendations:
            recommendations.append("Task decomposition looks balanced and manageable")

        return recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from decomposition history."""
        if not self.decomposition_history:
            return {"message": "No decompositions performed yet"}

        total_tasks = sum(len(r.subtasks) for r in self.decomposition_history)
        total_minutes = sum(r.total_estimated_minutes for r in self.decomposition_history)

        return {
            "total_decompositions": len(self.decomposition_history),
            "total_subtasks": total_tasks,
            "total_estimated_minutes": total_minutes,
            "avg_subtasks_per_decomposition": total_tasks / len(self.decomposition_history),
            "avg_minutes_per_decomposition": total_minutes / len(self.decomposition_history)
        }


def main():
    """CLI entry point for task decomposer."""
    import argparse

    parser = argparse.ArgumentParser(description="Task Decomposer CLI")
    parser.add_argument("task", help="Task description to decompose")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--stats", action="store_true", help="Show decomposition statistics")

    args = parser.parse_args()

    decomposer = TaskDecomposer()
    result = decomposer.decompose(args.task)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Task: {result.original_description}")
        print(f"Subtasks ({len(result.subtasks)}):")
        for subtask in result.subtasks:
            deps = f" (deps: {', '.join(subtask.dependencies)})" if subtask.dependencies else ""
            print(f"  [{subtask.order+1}] {subtask.name}{deps}")
            print(f"      Type: {subtask.task_type.value}, Est: {subtask.estimated_minutes}min, Risk: {subtask.risk_level}")
        print(f"\nTotal estimated: {result.total_estimated_minutes} minutes")
        print(f"Parallel groups: {result.parallel_groups}")
        print(f"Critical path: {result.critical_path}")
        if result.risks:
            print(f"Risks: {', '.join(result.risks)}")
        print(f"Recommendations: {', '.join(result.recommendations)}")

    if args.stats:
        print("\nStatistics:")
        print(json.dumps(decomposer.get_statistics(), indent=2))


if __name__ == "__main__":
    main()
