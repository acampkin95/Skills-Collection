#!/usr/bin/env python3
"""
Agent Coordinator - Multi-agent coordination and task distribution.

This module provides comprehensive capabilities for:
- Agent lifecycle management (create, monitor, terminate)
- Task queue with priorities
- Agent communication and message passing
- Resource allocation tracking
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle states."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class AgentCapability:
    """Represents an agent capability or skill."""
    name: str
    level: int = 1  # 1-10 proficiency level
    weight: float = 1.0  # Importance weight for task matching


@dataclass
class Agent:
    """Represents an AI agent in the system."""
    id: str
    name: str
    capabilities: List[AgentCapability]
    status: AgentStatus = AgentStatus.PENDING
    current_task: Optional[str] = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability."""
        return any(c.name == capability_name for c in self.capabilities)

    def get_capability_level(self, capability_name: str) -> int:
        """Get proficiency level for a capability."""
        for cap in self.capabilities:
            if cap.name == capability_name:
                return cap.level
        return 0


@dataclass
class Task:
    """Represents a task to be assigned to an agent."""
    id: str
    name: str
    description: str
    priority: TaskPriority
    required_capabilities: List[str]
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def can_start(self, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies are completed."""
        return all(dep in completed_tasks for dep in self.dependencies)


@dataclass
class Message:
    """Represents a message between agents."""
    id: str
    sender_id: str
    receiver_id: str
    message_type: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    priority: TaskPriority = TaskPriority.MEDIUM
    requires_response: bool = False
    response_deadline: Optional[datetime] = None


class AgentCoordinator:
    """
    Central coordinator for multi-agent systems.

    Manages agent lifecycle, task distribution, and inter-agent communication.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: Set[str] = set()
        self.messages: List[Message] = []
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.resource_pool: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.event_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

        # Configuration
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 10)
        self.task_timeout = self.config.get('task_timeout', 3600)  # seconds
        self.heartbeat_interval = self.config.get('heartbeat_interval', 30)

    def create_agent(
        self,
        name: str,
        capabilities: List[str],
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Create a new agent with specified capabilities.

        Args:
            name: Human-readable name for the agent
            capabilities: List of capability names
            agent_id: Optional custom ID (auto-generated if not provided)
            metadata: Optional additional metadata

        Returns:
            Created Agent instance
        """
        with self._lock:
            agent_id = agent_id or f"agent-{uuid.uuid4().hex[:8]}"

            agent_capabilities = [
                AgentCapability(name=cap, level=5) for cap in capabilities
            ]

            agent = Agent(
                id=agent_id,
                name=name,
                capabilities=agent_capabilities,
                status=AgentStatus.INITIALIZING,
                metadata=metadata or {}
            )

            self.agents[agent_id] = agent
            self._log_event("agent_created", {"agent_id": agent_id, "name": name})

            logger.info(f"Created agent {agent_id}: {name} with capabilities {capabilities}")
            return agent

    def terminate_agent(self, agent_id: str, reason: str = "explicit_request") -> bool:
        """
        Terminate an agent gracefully.

        Args:
            agent_id: ID of the agent to terminate
            reason: Reason for termination

        Returns:
            True if agent was terminated, False if not found
        """
        with self._lock:
            if agent_id not in self.agents:
                return False

            agent = self.agents[agent_id]
            agent.status = AgentStatus.TERMINATED
            agent.completed_at = datetime.now()

            self._log_event("agent_terminated", {
                "agent_id": agent_id,
                "name": agent.name,
                "reason": reason
            })

            logger.info(f"Terminated agent {agent_id}: {agent.name}")
            return True

    def add_task(
        self,
        name: str,
        description: str,
        priority: TaskPriority,
        required_capabilities: List[str],
        dependencies: Optional[List[str]] = None,
        estimated_duration: Optional[timedelta] = None,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Add a task to the queue.

        Args:
            name: Task name
            description: Task description
            priority: Task priority
            required_capabilities: Capabilities needed to execute
            dependencies: Task IDs this task depends on
            estimated_duration: Expected duration
            input_data: Input data for the task
            metadata: Additional metadata

        Returns:
            Created Task instance
        """
        task_id = f"task-{uuid.uuid4().hex[:8]}"

        task = Task(
            id=task_id,
            name=name,
            description=description,
            priority=priority,
            required_capabilities=required_capabilities,
            dependencies=dependencies or [],
            estimated_duration=estimated_duration,
            input_data=input_data,
            metadata=metadata or {}
        )

        self.tasks[task_id] = task
        self.task_queue.append(task)
        self._log_event("task_added", {"task_id": task_id, "name": name, "priority": priority.value})

        logger.info(f"Added task {task_id}: {name} with priority {priority.value}")
        return task

    def _find_best_agent(self, task: Task) -> Optional[Agent]:
        """
        Find the best agent for a task based on capabilities and availability.

        Args:
            task: Task to assign

        Returns:
            Best matching Agent or None
        """
        eligible_agents = []

        for agent in self.agents.values():
            # Skip agents that are terminated or failed
            if agent.status in (AgentStatus.TERMINATED, AgentStatus.FAILED):
                continue

            # Check capabilities
            has_all = all(
                agent.has_capability(cap)
                for cap in task.required_capabilities
            )
            if not has_all:
                continue

            # Calculate match score
            score = sum(
                agent.get_capability_level(cap)
                for cap in task.required_capabilities
            ) / len(task.required_capabilities)

            # Factor in current workload
            workload_penalty = 1.0
            if agent.current_task:
                workload_penalty = 0.5  # Reduce score for busy agents

            eligible_agents.append((agent, score * workload_penalty))

        if not eligible_agents:
            return None

        # Sort by score and return best
        eligible_agents.sort(key=lambda x: x[1], reverse=True)
        return eligible_agents[agent][0] if eligible_agents else None

    def assign_task(self, task_id: str, agent_id: Optional[str] = None) -> bool:
        """
        Assign a task to an agent.

        Args:
            task_id: ID of the task to assign
            agent_id: Specific agent to assign to (auto-select if None)

        Returns:
            True if assignment successful
        """
        with self._lock:
            if task_id not in self.tasks:
                return False

            task = self.tasks[task_id]

            if task.assigned_agent:
                logger.warning(f"Task {task_id} already assigned to {task.assigned_agent}")
                return False

            if agent_id:
                if agent_id not in self.agents:
                    return False
                agent = self.agents[agent_id]
            else:
                agent = self._find_best_agent(task)

            if not agent:
                logger.warning(f"No suitable agent found for task {task_id}")
                return False

            # Assign task
            agent.current_task = task_id
            agent.status = AgentStatus.WORKING
            agent.started_at = datetime.now()
            task.assigned_agent = agent_id or agent.id
            task.status = "assigned"
            task.started_at = datetime.now()

            self._log_event("task_assigned", {
                "task_id": task_id,
                "agent_id": agent.id,
                "agent_name": agent.name
            })

            logger.info(f"Assigned task {task_id} to agent {agent.id}")
            return True

    def complete_task(
        self,
        task_id: str,
        output_data: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task
            output_data: Task output
            success: Whether task succeeded

        Returns:
            True if task was completed
        """
        with self._lock:
            if task_id not in self.tasks:
                return False

            task = self.tasks[task_id]
            task.status = "completed" if success else "failed"
            task.completed_at = datetime.now()
            task.output_data = output_data

            if task.started_at:
                task.actual_duration = datetime.now() - task.started_at

            self.completed_tasks.add(task_id)

            # Update agent
            if task.assigned_agent and task.assigned_agent in self.agents:
                agent = self.agents[task.assigned_agent]
                agent.current_task = None
                agent.status = AgentStatus.IDLE if success else AgentStatus.FAILED
                agent.completed_at = datetime.now()

            self._log_event("task_completed", {
                "task_id": task_id,
                "success": success,
                "duration": str(task.actual_duration) if task.actual_duration else None
            })

            logger.info(f"Completed task {task_id} with status: {task.status}")
            return True

    def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: str,
        content: Any,
        requires_response: bool = False,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> Message:
        """
        Send a message from one agent to another.

        Args:
            sender_id: Sending agent ID
            receiver_id: Receiving agent ID
            message_type: Type of message
            content: Message content
            requires_response: Whether response is required
            priority: Message priority

        Returns:
            Created Message instance
        """
        message = Message(
            id=f"msg-{uuid.uuid4().hex[:8]}",
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            priority=priority,
            requires_response=requires_response
        )

        self.messages.append(message)

        # Deliver to receiver
        if receiver_id in self.agents:
            self.agents[receiver_id].messages.append({
                "id": message.id,
                "type": message_type,
                "content": content,
                "from": sender_id,
                "timestamp": message.timestamp.isoformat()
            })

        # Trigger handlers
        self._dispatch_message(message)

        logger.info(f"Message from {sender_id} to {receiver_id}: {message_type}")
        return message

    def register_message_handler(
        self,
        message_type: str,
        handler: Callable[[Message], None]
    ) -> None:
        """Register a handler for a message type."""
        self.message_handlers[message_type].append(handler)

    def _dispatch_message(self, message: Message) -> None:
        """Dispatch a message to all registered handlers."""
        for handler in self.message_handlers.get(message.message_type, []):
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of an agent."""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        return {
            "id": agent.id,
            "name": agent.name,
            "status": agent.status.value,
            "current_task": agent.current_task,
            "capabilities": [c.name for c in agent.capabilities],
            "assigned_at": agent.assigned_at.isoformat() if agent.assigned_at else None,
            "started_at": agent.started_at.isoformat() if agent.started_at else None,
            "message_count": len(agent.messages)
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """Get status of the task queue."""
        by_priority = defaultdict(int)
        for task in self.task_queue:
            by_priority[task.priority.value] += 1

        return {
            "total_queued": len(self.task_queue),
            "by_priority": dict(by_priority),
            "completed": len(self.completed_tasks),
            "total_tasks": len(self.tasks)
        }

    def get_project_status(self) -> Dict[str, Any]:
        """Get overall project status."""
        agent_stats = {
            "total": len(self.agents),
            "by_status": defaultdict(int)
        }
        for agent in self.agents.values():
            agent_stats["by_status"][agent.status.value] += 1

        return {
            "agents": agent_stats,
            "tasks": self.get_queue_status(),
            "events": len(self.event_history)
        }

    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event to the event history."""
        self.event_history.append({
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })

    def export_state(self) -> Dict[str, Any]:
        """Export current coordinator state."""
        return {
            "agents": {
                aid: {
                    "id": a.id,
                    "name": a.name,
                    "status": a.status.value,
                    "capabilities": [c.name for c in a.capabilities],
                    "current_task": a.current_task
                }
                for aid, a in self.agents.items()
            },
            "tasks": {
                tid: {
                    "id": t.id,
                    "name": t.name,
                    "status": t.status,
                    "priority": t.priority.value,
                    "assigned_agent": t.assigned_agent
                }
                for tid, t in self.tasks.items()
            },
            "queue_length": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "event_count": len(self.event_history)
        }

    def import_state(self, state: Dict[str, Any]) -> None:
        """Import coordinator state from exported data."""
        # This is a simplified implementation
        # In practice, you'd want more robust state restoration
        logger.warning("State import is experimental - may not restore all state")


def main():
    """CLI entry point for agent coordinator."""
    import argparse

    parser = argparse.ArgumentParser(description="Agent Coordinator CLI")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--create-agent", nargs=2, metavar=("NAME", "CAPS"),
                        help="Create a new agent")
    parser.add_argument("--list-agents", action="store_true",
                        help="List all agents")
    parser.add_argument("--status", action="store_true",
                        help="Show project status")

    args = parser.parse_args()

    coordinator = AgentCoordinator()

    if args.create_agent:
        name, caps = args.create_agent
        capabilities = caps.split(",")
        agent = coordinator.create_agent(name, capabilities)
        print(f"Created agent: {agent.id}")

    if args.list_agents:
        for agent in coordinator.agents.values():
            print(f"{agent.id}: {agent.name} ({agent.status.value})")

    if args.status:
        status = coordinator.get_project_status()
        print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
