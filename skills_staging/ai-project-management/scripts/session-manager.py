#!/usr/bin/env python3
"""
Session Manager - Manage development sessions.

This module provides capabilities for:
- Session creation and resumption
- Context preservation
- Activity logging
- Session analytics
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Status of a development session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"


@dataclass
class SessionContext:
    """Context preserved across sessions."""
    goals: List[str] = field(default_factory=list)
    current_work: str = ""
    recent_changes: List[Dict[str, Any]] = field(default_factory=list)
    open_files: List[str] = field(default_factory=list)
    task_queue: List[str] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goals": self.goals,
            "current_work": self.current_work,
            "recent_changes": self.recent_changes,
            "open_files": self.open_files,
            "task_queue": self.task_queue,
            "decisions": self.decisions,
            "notes": self.notes,
            "custom_data": self.custom_data
        }


@dataclass
class ActivityEntry:
    """Activity log entry."""
    id: str
    timestamp: datetime
    activity_type: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "activity_type": self.activity_type,
            "description": self.description,
            "metadata": self.metadata,
            "duration_seconds": self.duration_seconds
        }


@dataclass
class DevelopmentSession:
    """Represents a development session."""
    id: str
    name: str
    project: str
    status: SessionStatus
    created_at: datetime
    started_at: Optional[datetime]
    last_activity_at: datetime
    ended_at: Optional[datetime]
    context: SessionContext
    activities: List[ActivityEntry] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "project": self.project,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_activity_at": self.last_activity_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "context": self.context.to_dict(),
            "activity_count": len(self.activities),
            "metadata": self.metadata
        }

    def get_duration(self) -> Optional[timedelta]:
        """Get session duration."""
        end = self.ended_at or datetime.now()
        if self.started_at:
            return end - self.started_at
        return None


class SessionManager:
    """
    Manages development sessions with context preservation.

    Provides session creation, resumption, activity tracking, and analytics.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sessions: Dict[str, DevelopmentSession] = {}
        self.active_session: Optional[str] = None
        self._lock = Lock()

        # Storage configuration
        self.storage_path = Path(self.config.get('storage_path', './sessions'))
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Activity categories
        self.activity_categories = [
            'coding',
            'testing',
            'debugging',
            'review',
            'documentation',
            'research',
            'planning',
            'deployment',
            'communication',
            'other'
        ]

        # Load existing sessions
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load sessions from storage."""
        session_dir = self.storage_path

        for session_file in session_dir.glob("*.json"):
            try:
                with open(session_file) as f:
                    data = json.load(f)
                    session = self._dict_to_session(data)
                    if session:
                        self.sessions[session.id] = session
            except Exception as e:
                logger.error(f"Failed to load session {session_file}: {e}")

        logger.info(f"Loaded {len(self.sessions)} sessions")

    def _dict_to_session(self, data: Dict[str, Any]) -> Optional[DevelopmentSession]:
        """Convert dictionary to DevelopmentSession."""
        try:
            context = SessionContext(**data.get('context', {}))
            return DevelopmentSession(
                id=data['id'],
                name=data['name'],
                project=data['project'],
                status=SessionStatus(data.get('status', 'active')),
                created_at=datetime.fromisoformat(data['created_at']),
                started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
                last_activity_at=datetime.fromisoformat(data['last_activity_at']),
                ended_at=datetime.fromisoformat(data['ended_at']) if data.get('ended_at') else None,
                context=context,
                activities=[],
                metadata=data.get('metadata', {})
            )
        except Exception as e:
            logger.error(f"Error converting dict to session: {e}")
            return None

    def create_session(
        self,
        name: str,
        project: str,
        goals: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DevelopmentSession:
        """
        Create a new development session.

        Args:
            name: Session name
            project: Project name
            goals: Optional list of session goals
            metadata: Optional metadata

        Returns:
            Created DevelopmentSession
        """
        with self._lock:
            session = DevelopmentSession(
                id=f"session-{uuid.uuid4().hex[:8]}",
                name=name,
                project=project,
                status=SessionStatus.ACTIVE,
                created_at=datetime.now(),
                started_at=datetime.now(),
                last_activity_at=datetime.now(),
                ended_at=None,
                context=SessionContext(goals=goals or []),
                metadata=metadata or {}
            )

            self.sessions[session.id] = session
            self.active_session = session.id

            logger.info(f"Created session: {session.id} - {name}")
            return session

    def resume_session(self, session_id: str) -> Optional[DevelopmentSession]:
        """
        Resume a previous session.

        Args:
            session_id: ID of session to resume

        Returns:
            Resumed session or None
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Update session status
        session.status = SessionStatus.ACTIVE
        session.last_activity_at = datetime.now()

        self.active_session = session_id
        logger.info(f"Resumed session: {session_id}")
        return session

    def pause_session(self) -> Optional[DevelopmentSession]:
        """Pause the active session."""
        if not self.active_session:
            return None

        session = self.sessions[self.active_session]
        session.status = SessionStatus.PAUSED
        session.last_activity_at = datetime.now()

        logger.info(f"Paused session: {session.id}")
        return session

    def end_session(self, summary: Optional[str] = None) -> Optional[DevelopmentSession]:
        """End the active session."""
        if not self.active_session:
            return None

        session = self.sessions[self.active_session]
        session.status = SessionStatus.COMPLETED
        session.ended_at = datetime.now()
        session.last_activity_at = datetime.now()

        if summary:
            session.context.notes = summary

        # Save session
        self._save_session(session)

        self.active_session = None
        logger.info(f"Ended session: {session.id}")
        return session

    def log_activity(
        self,
        activity_type: str,
        description: str,
        duration_seconds: float = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ActivityEntry]:
        """
        Log an activity in the current session.

        Args:
            activity_type: Type of activity
            description: Activity description
            duration_seconds: Time spent
            metadata: Additional metadata

        Returns:
            Created ActivityEntry or None
        """
        if not self.active_session:
            logger.warning("No active session")
            return None

        session = self.sessions[self.active_session]

        entry = ActivityEntry(
            id=f"act-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            activity_type=activity_type,
            description=description,
            duration_seconds=duration_seconds,
            metadata=metadata or {}
        )

        session.activities.append(entry)
        session.last_activity_at = datetime.now()

        return entry

    def update_context(
        self,
        goals: Optional[List[str]] = None,
        current_work: Optional[str] = None,
        open_files: Optional[List[str]] = None,
        task_queue: Optional[List[str]] = None,
        decisions: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
        **custom_data
    ) -> bool:
        """
        Update the session context.

        Args:
            goals: Session goals
            current_work: Current work item
            open_files: List of open files
            task_queue: Pending tasks
            decisions: Key decisions made
            notes: Session notes
            **custom_data: Custom context data

        Returns:
            True if updated
        """
        if not self.active_session:
            return False

        session = self.sessions[self.active_session]

        if goals:
            session.context.goals = goals
        if current_work:
            session.context.current_work = current_work
        if open_files:
            session.context.open_files = open_files
        if task_queue:
            session.context.task_queue = task_queue
        if decisions:
            session.context.decisions.extend(decisions)
        if notes:
            session.context.notes = notes

        # Update custom data
        session.context.custom_data.update(custom_data)

        session.last_activity_at = datetime.now()
        return True

    def add_decision(
        self,
        decision: str,
        rationale: str,
        alternatives: Optional[List[str]] = None
    ) -> bool:
        """Add a key decision to the session context."""
        if not self.active_session:
            return False

        session = self.sessions[self.active_session]
        session.context.decisions.append({
            "decision": decision,
            "rationale": rationale,
            "alternatives": alternatives or [],
            "timestamp": datetime.now().isoformat()
        })

        return True

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a session."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        duration = session.get_duration()

        # Calculate activity breakdown
        activity_breakdown = {}
        for entry in session.activities:
            activity_breakdown[entry.activity_type] = activity_breakdown.get(
                entry.activity_type, 0
            ) + entry.duration_seconds

        return {
            "id": session.id,
            "name": session.name,
            "project": session.project,
            "status": session.status.value,
            "duration": str(duration) if duration else None,
            "duration_seconds": duration.total_seconds() if duration else 0,
            "goals": session.context.goals,
            "current_work": session.context.current_work,
            "activity_count": len(session.activities),
            "activity_breakdown": activity_breakdown,
            "decisions_made": len(session.context.decisions),
            "open_files": session.context.open_files,
            "pending_tasks": session.context.task_queue,
            "notes": session.context.notes
        }

    def get_active_session(self) -> Optional[DevelopmentSession]:
        """Get the currently active session."""
        if not self.active_session:
            return None
        return self.sessions.get(self.active_session)

    def list_sessions(
        self,
        project: Optional[str] = None,
        status: Optional[SessionStatus] = None,
        limit: int = 20
    ) -> List[DevelopmentSession]:
        """List sessions with optional filtering."""
        results = []

        for session in self.sessions.values():
            if project and session.project != project:
                continue
            if status and session.status != status:
                continue
            results.append(session)

        # Sort by last activity (most recent first)
        results.sort(key=lambda s: s.last_activity_at, reverse=True)

        return results[:limit]

    def get_session_analytics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a session."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        duration = session.get_duration()

        # Activity analysis
        total_duration = sum(e.duration_seconds for e in session.activities)
        activity_types = {}

        for entry in session.activities:
            if entry.activity_type not in activity_types:
                activity_types[entry.activity_type] = {
                    "count": 0,
                    "total_seconds": 0,
                    "entries": []
                }
            activity_types[entry.activity_type]["count"] += 1
            activity_types[entry.activity_type]["total_seconds"] += entry.duration_seconds

        # Time distribution
        hourly_distribution = [0] * 24
        for entry in session.activities:
            hourly_distribution[entry.timestamp.hour] += entry.duration_seconds

        return {
            "session_id": session_id,
            "name": session.name,
            "duration_hours": duration.total_seconds() / 3600 if duration else 0,
            "total_activity_seconds": total_duration,
            "activity_types": {
                k: {
                    "count": v["count"],
                    "hours": round(v["total_seconds"] / 3600, 2)
                }
                for k, v in activity_types.items()
            },
            "hourly_distribution": hourly_distribution,
            "goals_completed": len([g for g in session.context.goals if g.startswith("[x]")]),
            "goals_total": len(session.context.goals),
            "decisions_recorded": len(session.context.decisions)
        }

    def generate_report(
        self,
        session_id: str,
        format: str = "markdown"
    ) -> Optional[str]:
        """Generate a session report."""
        analytics = self.get_session_analytics(session_id)
        summary = self.get_session_summary(session_id)

        if not analytics or not summary:
            return None

        if format == "markdown":
            return self._generate_markdown_report(summary, analytics)
        elif format == "json":
            return json.dumps({"summary": summary, "analytics": analytics}, indent=2)
        else:
            return json.dumps({"summary": summary, "analytics": analytics}, indent=2)

    def _generate_markdown_report(
        self,
        summary: Dict[str, Any],
        analytics: Dict[str, Any]
    ) -> str:
        """Generate markdown report."""
        lines = [
            f"# Session Report: {summary['name']}",
            "",
            f"**Project:** {summary['project']}",
            f"**Duration:** {summary['duration'] or 'N/A'}",
            f"**Status:** {summary['status']}",
            "",
            "## Goals",
        ]

        if summary['goals']:
            for goal in summary['goals']:
                lines.append(f"- {goal}")
        else:
            lines.append("_No goals defined_")

        lines.extend([
            "",
            "## Activity Summary",
            f"- **Total Activities:** {summary['activity_count']}",
            f"- **Decisions Recorded:** {summary['decisions_made']}",
            "",
            "### Time by Activity Type"
        ])

        for activity_type, data in analytics.get('activity_types', {}).items():
            lines.append(f"- {activity_type}: {data['hours']} hours ({data['count']} entries)")

        lines.extend([
            "",
            "## Key Decisions"
        ])

        # This would need full session access - simplified
        lines.append(f"{summary['decisions_made']} decisions recorded")

        lines.extend([
            "",
            "## Notes",
            summary.get('notes', '_No notes_')
        ])

        return "\n".join(lines)

    def _save_session(self, session: DevelopmentSession) -> None:
        """Save session to storage."""
        filepath = self.storage_path / f"{session.id}.json"

        with open(filepath, 'w') as f:
            json.dump(session.to_dict(), f, indent=2, default=str)

    def auto_save(self) -> None:
        """Auto-save all active sessions."""
        for session_id, session in self.sessions.items():
            if session.status == SessionStatus.ACTIVE:
                self._save_session(session)


def main():
    """CLI entry point for session manager."""
    import argparse

    parser = argparse.ArgumentParser(description="Session Manager CLI")
    parser.add_argument("command", choices=[
        "create", "list", "resume", "pause", "end", "summary", "report"
    ])

    args = parser.parse_args()

    manager = SessionManager()

    if args.command == "create":
        name = input("Session name: ")
        project = input("Project: ")
        goals = input("Goals (comma-separated): ").split(",")
        session = manager.create_session(name, project, [g.strip() for g in goals if g.strip()])
        print(f"Created session: {session.id}")

    elif args.command == "list":
        for session in manager.list_sessions():
            print(f"{session.id} | {session.name} | {session.status.value}")

    elif args.command == "resume":
        session_id = input("Session ID: ")
        session = manager.resume_session(session_id)
        if session:
            print(f"Resumed: {session.name}")
        else:
            print("Session not found")

    elif args.command == "pause":
        session = manager.pause_session()
        if session:
            print(f"Paused: {session.name}")

    elif args.command == "end":
        summary = input("Session summary: ")
        session = manager.end_session(summary)
        if session:
            print(f"Ended: {session.name}")

    elif args.command == "summary":
        session_id = input("Session ID: ")
        print(json.dumps(manager.get_session_summary(session_id), indent=2))

    elif args.command == "report":
        session_id = input("Session ID: ")
        print(manager.generate_report(session_id, format="markdown"))


if __name__ == "__main__":
    main()
