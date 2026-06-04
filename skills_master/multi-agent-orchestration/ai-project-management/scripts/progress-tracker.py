#!/usr/bin/env python3
"""
Progress Tracker - Track project progress with metrics and dashboards.

This module provides capabilities for:
- Milestone tracking
- Burndown charts
- Velocity metrics
- Reporting and dashboards
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from statistics import mean, stdev

logger = logging.getLogger(__name__)


class MilestoneStatus(Enum):
    """Status of a milestone."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class MetricType(Enum):
    """Types of metrics."""
    VELOCITY = "velocity"
    BURN_DOWN = "burndown"
    CYCLE_TIME = "cycle_time"
    LEAD_TIME = "lead_time"
    THROUGHPUT = "throughput"
    QUALITY = "quality"
    EFFORT = "effort"


@dataclass
class Milestone:
    """Represents a project milestone."""
    id: str
    name: str
    description: str
    status: MilestoneStatus
    created_at: datetime
    target_date: Optional[datetime]
    completed_at: Optional[datetime]
    tasks: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tasks": self.tasks,
            "completion_percentage": self.completion_percentage,
            "priority": self.priority,
            "metadata": self.metadata
        }


@dataclass
class ProgressEntry:
    """Represents a progress update entry."""
    id: str
    timestamp: datetime
    milestone_id: Optional[str]
    task_id: Optional[str]
    completed_items: int
    remaining_items: int
    notes: str
    contributed_by: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "milestone_id": self.milestone_id,
            "task_id": self.task_id,
            "completed_items": self.completed_items,
            "remaining_items": self.remaining_items,
            "notes": self.notes,
            "contributed_by": self.contributed_by
        }


@dataclass
class SprintMetrics:
    """Metrics for a sprint or time period."""
    sprint_id: str
    start_date: datetime
    end_date: datetime
    planned_points: int
    completed_points: int
    velocity: float
    cycle_time_avg: float
    throughput: int
    quality_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sprint_id": self.sprint_id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "planned_points": self.planned_points,
            "completed_points": self.completed_points,
            "velocity": self.velocity,
            "cycle_time_avg": self.cycle_time_avg,
            "throughput": self.throughput,
            "quality_score": self.quality_score
        }


class ProgressTracker:
    """
    Comprehensive progress tracking system.

    Tracks milestones, calculates metrics, and generates reports.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.milestones: Dict[str, Milestone] = {}
        self.progress_entries: List[ProgressEntry] = []
        self.sprint_history: List[SprintMetrics] = []
        self.task_status: Dict[str, Dict[str, Any]] = {}

        # Historical data for trend analysis
        self.velocity_history: List[float] = []
        self.cycle_time_history: List[float] = []

    def create_milestone(
        self,
        name: str,
        description: str,
        target_date: Optional[datetime] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Milestone:
        """Create a new milestone."""
        import uuid

        milestone = Milestone(
            id=f"ms-{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            status=MilestoneStatus.PENDING,
            created_at=datetime.now(),
            target_date=target_date,
            completed_at=None,
            priority=priority,
            metadata=metadata or {}
        )

        self.milestones[milestone.id] = milestone
        logger.info(f"Created milestone: {milestone.name}")
        return milestone

    def update_milestone(
        self,
        milestone_id: str,
        status: Optional[MilestoneStatus] = None,
        completion_percentage: Optional[float] = None,
        task_ids: Optional[List[str]] = None
    ) -> bool:
        """Update milestone status and progress."""
        if milestone_id not in self.milestones:
            return False

        milestone = self.milestones[milestone_id]

        if status:
            milestone.status = status
            if status == MilestoneStatus.COMPLETED:
                milestone.completion_percentage = 100.0
                milestone.completed_at = datetime.now()

        if completion_percentage is not None:
            milestone.completion_percentage = min(100.0, max(0.0, completion_percentage))

        if task_ids:
            milestone.tasks.extend(task_ids)

        # Update status based on completion
        if milestone.completion_percentage >= 100 and milestone.status != MilestoneStatus.COMPLETED:
            milestone.status = MilestoneStatus.COMPLETED
            milestone.completed_at = datetime.now()

        logger.info(f"Updated milestone {milestone_id}: {milestone.completion_percentage}%")
        return True

    def log_progress(
        self,
        milestone_id: Optional[str] = None,
        task_id: Optional[str] = None,
        completed_items: int = 0,
        remaining_items: int = 0,
        notes: str = "",
        contributed_by: str = "system"
    ) -> ProgressEntry:
        """Log a progress update."""
        import uuid

        entry = ProgressEntry(
            id=f"pe-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            milestone_id=milestone_id,
            task_id=task_id,
            completed_items=completed_items,
            remaining_items=remaining_items,
            notes=notes,
            contributed_by=contributed_by
        )

        self.progress_entries.append(entry)

        # Update task status
        if task_id:
            if task_id not in self.task_status:
                self.task_status[task_id] = {"completed_items": 0, "remaining_items": 0}
            self.task_status[task_id]["completed_items"] += completed_items
            self.task_status[task_id]["remaining_items"] += remaining_items

        # Update milestone if provided
        if milestone_id and milestone_id in self.milestones:
            ms = self.milestones[milestone_id]
            total = completed_items + remaining_items
            if total > 0:
                ms.completion_percentage = (completed_items / total) * 100

        logger.info(f"Logged progress: +{completed_items} items")
        return entry

    def get_milestone_status(self, milestone_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a milestone."""
        if milestone_id not in self.milestones:
            return None

        ms = self.milestones[milestone_id]

        # Calculate days remaining
        days_remaining = None
        if ms.target_date and ms.status not in (MilestoneStatus.COMPLETED, MilestoneStatus.CANCELLED):
            days_remaining = (ms.target_date - datetime.now()).days

        return {
            "id": ms.id,
            "name": ms.name,
            "status": ms.status.value,
            "progress": ms.completion_percentage,
            "tasks_count": len(ms.tasks),
            "target_date": ms.target_date.isoformat() if ms.target_date else None,
            "days_remaining": days_remaining,
            "is_on_track": days_remaining is None or days_remaining > 0 or ms.completion_percentage >= 100
        }

    def get_project_status(self) -> Dict[str, Any]:
        """Get overall project status."""
        if not self.milestones:
            return {"message": "No milestones defined"}

        total = len(self.milestones)
        completed = sum(1 for m in self.milestones.values() if m.status == MilestoneStatus.COMPLETED)
        in_progress = sum(1 for m in self.milestones.values() if m.status == MilestoneStatus.IN_PROGRESS)
        blocked = sum(1 for m in self.milestones.values() if m.status == MilestoneStatus.BLOCKED)

        avg_completion = mean(m.completion_percentage for m in self.milestones.values()) if self.milestones else 0

        # Overall progress
        total_progress = sum(m.completion_percentage for m in self.milestones.values()) / total if total > 0 else 0

        return {
            "total_milestones": total,
            "completed": completed,
            "in_progress": in_progress,
            "blocked": blocked,
            "pending": total - completed - in_progress - blocked,
            "overall_progress": round(total_progress, 1),
            "average_completion": round(avg_completion, 1),
            "progress_entries": len(self.progress_entries)
        }

    def generate_burndown(
        self,
        start_date: datetime,
        end_date: datetime,
        total_effort: float
    ) -> Dict[str, Any]:
        """
        Generate burndown chart data.

        Args:
            start_date: Tracking start date
            end_date: Target end date
            total_effort: Total effort units (story points, hours, etc.)

        Returns:
            Burndown chart data
        """
        # Calculate ideal burndown
        total_days = (end_date - start_date).days
        ideal_daily_burn = total_effort / total_days if total_days > 0 else 0

        # Get actual progress
        entries_in_range = [
            e for e in self.progress_entries
            if start_date <= e.timestamp <= end_date
        ]

        # Group by date
        daily_progress = defaultdict(int)
        for entry in entries_in_range:
            date_key = entry.timestamp.date().isoformat()
            daily_progress[date_key] += entry.completed_items

        # Build burndown data
        burndown_data = []
        cumulative = total_effort
        current_date = start_date

        while current_date <= end_date:
            date_key = current_date.date().isoformat()
            ideal_remaining = total_effort - (ideal_daily_burn * ((current_date - start_date).days))
            actual_completed = sum(v for d, v in daily_progress.items() if d <= date_key)
            actual_remaining = total_effort - actual_completed

            burndown_data.append({
                "date": date_key,
                "ideal_remaining": round(max(0, ideal_remaining), 2),
                "actual_remaining": round(max(0, actual_remaining), 2),
                "completed_today": daily_progress.get(date_key, 0)
            })

            current_date += timedelta(days=1)

        # Calculate metrics
        actual_completed = sum(daily_progress.values())
        percent_complete = (actual_completed / total_effort * 100) if total_effort > 0 else 0
        expected_completed = ideal_daily_burn * ((datetime.now() - start_date).days) if datetime.now() > start_date else 0
        velocity = actual_completed / max(1, (datetime.now() - start_date).days) if datetime.now() > start_date else 0

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_effort": total_effort,
            "data": burndown_data,
            "metrics": {
                "percent_complete": round(percent_complete, 1),
                "actual_completed": actual_completed,
                "expected_completed": round(expected_completed, 2),
                "current_velocity": round(velocity, 2),
                "is_on_track": actual_completed >= expected_completed * 0.9
            }
        }

    def record_sprint_metrics(
        self,
        sprint_id: str,
        start_date: datetime,
        end_date: datetime,
        planned_points: int,
        completed_points: int,
        cycle_times: List[float],
        quality_score: float = 1.0
    ) -> SprintMetrics:
        """Record metrics for a completed sprint."""
        metrics = SprintMetrics(
            sprint_id=sprint_id,
            start_date=start_date,
            end_date=end_date,
            planned_points=planned_points,
            completed_points=completed_points,
            velocity=completed_points,
            cycle_time_avg=mean(cycle_times) if cycle_times else 0,
            throughput=completed_points,
            quality_score=quality_score
        )

        self.sprint_history.append(metrics)

        # Update historical data
        self.velocity_history.append(completed_points)
        if cycle_times:
            self.cycle_time_history.extend(cycle_times)

        return metrics

    def get_velocity_metrics(self) -> Dict[str, Any]:
        """Calculate velocity and throughput metrics."""
        if not self.velocity_history:
            return {"message": "No velocity data available"}

        velocities = self.velocity_history

        # Last N sprints for trend
        window = min(len(velocities), 5)
        recent = velocities[-window:]
        older = velocities[:-window] if len(velocities) > window else []

        return {
            "total_sprints": len(velocities),
            "current_velocity": round(velocities[-1], 1) if velocities else 0,
            "average_velocity": round(mean(velocities), 1),
            "velocity_std_dev": round(stdev(velocities), 2) if len(velocities) > 1 else 0,
            "recent_velocity_avg": round(mean(recent), 1),
            "velocity_trend": self._calculate_trend(velocities),
            "throughput": sum(velocities),
            "sprint_capacity": round(mean(recent) * 1.1, 1)  # 10% buffer
        }

    def _calculate_trend(self, data: List[float]) -> str:
        """Calculate trend direction."""
        if len(data) < 2:
            return "stable"

        recent = data[-3:]
        older = data[:-3] if len(data) > 3 else data[:1]

        if not older:
            return "stable"

        recent_avg = mean(recent)
        older_avg = mean(older)

        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def get_cycle_time_metrics(self) -> Dict[str, Any]:
        """Calculate cycle time metrics."""
        if not self.cycle_time_history:
            return {"message": "No cycle time data available"}

        cycle_times = self.cycle_time_history

        return {
            "average_cycle_time": round(mean(cycle_times), 1),
            "min_cycle_time": min(cycle_times),
            "max_cycle_time": max(cycle_times),
            "cycle_time_std_dev": round(stdev(cycle_times), 2) if len(cycle_times) > 1 else 0,
            "p50": sorted(cycle_times)[int(len(cycle_times) * 0.5)],
            "p90": sorted(cycle_times)[int(len(cycle_times) * 0.9)] if cycle_times else 0
        }

    def generate_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive project dashboard."""
        return {
            "generated_at": datetime.now().isoformat(),
            "project_status": self.get_project_status(),
            "velocity": self.get_velocity_metrics(),
            "cycle_time": self.get_cycle_time_metrics(),
            "milestones": [
                self.get_milestone_status(ms_id)
                for ms_id in list(self.milestones.keys())[:5]
            ],
            "recent_progress": [
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat(),
                    "completed": e.completed_items,
                    "contributed_by": e.contributed_by
                }
                for e in sorted(self.progress_entries, key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }

    def export_report(self, format: str = "json") -> str:
        """Export project report."""
        data = self.generate_dashboard()

        if format == "json":
            return json.dumps(data, indent=2)
        elif format == "markdown":
            return self._generate_markdown_report(data)
        else:
            return json.dumps(data, indent=2)

    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate markdown report."""
        lines = [
            "# Project Progress Report",
            f"Generated: {data['generated_at']}",
            "",
            "## Project Status",
            f"- Overall Progress: {data['project_status']['overall_progress']}%",
            f"- Milestones: {data['project_status']['completed']}/{data['project_status']['total_milestones']} completed",
            "",
            "## Velocity Metrics",
            f"- Average Velocity: {data['velocity']['average_velocity']}",
            f"- Current Velocity: {data['velocity']['current_velocity']}",
            f"- Trend: {data['velocity']['velocity_trend']}",
            "",
            "## Cycle Time",
            f"- Average: {data['cycle_time']['average_cycle_time']} hours",
            f"- P90: {data['cycle_time']['p90']} hours",
            ""
        ]

        return "\n".join(lines)


def main():
    """CLI entry point for progress tracker."""
    import argparse

    parser = argparse.ArgumentParser(description="Progress Tracker CLI")
    parser.add_argument("command", choices=["status", "dashboard", "burndown", "report"])

    args = parser.parse_args()

    tracker = ProgressTracker()

    if args.command == "status":
        print(json.dumps(tracker.get_project_status(), indent=2))

    elif args.command == "dashboard":
        print(json.dumps(tracker.generate_dashboard(), indent=2))

    elif args.command == "burndown":
        start = datetime.now() - timedelta(days=7)
        end = datetime.now() + timedelta(days=7)
        bd = tracker.generate_burndown(start, end, total_effort=100)
        print(json.dumps(bd, indent=2))

    elif args.command == "report":
        print(tracker.export_report(format="markdown"))


if __name__ == "__main__":
    main()
