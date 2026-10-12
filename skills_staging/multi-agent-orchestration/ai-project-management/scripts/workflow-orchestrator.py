#!/usr/bin/env python3
"""
Workflow Orchestrator - Define and execute workflows.

This module provides capabilities for:
- Workflow definition (YAML/JSON)
- Step execution with dependencies
- Error handling and recovery
- Workflow visualization
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Types of workflow steps."""
    TASK = "task"
    APPROVAL = "approval"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"


@dataclass
class WorkflowStep:
    """Represents a step in a workflow."""
    id: str
    name: str
    step_type: StepType
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    status_message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "step_type": self.step_type.value,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "status_message": self.status_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "output": self.output,
            "error": str(self.error) if self.error else None
        }


@dataclass
class Workflow:
    """Represents a workflow definition."""
    id: str
    name: str
    description: str
    version: str
    steps: Dict[str, WorkflowStep]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)

    def get_execution_order(self) -> List[str]:
        """Get steps in execution order (topological sort)."""
        visited = set()
        order = []

        def visit(step_id: str):
            if step_id in visited:
                return
            visited.add(step_id)

            step = self.steps.get(step_id)
            if step:
                for dep in step.dependencies:
                    visit(dep)
                order.append(step_id)

        # Find roots (steps with no dependencies or dependencies outside workflow)
        for step_id, step in self.steps.items():
            if not step.dependencies or all(d not in self.steps for d in step.dependencies):
                visit(step_id)

        # Add remaining
        for step_id in self.steps:
            visit(step_id)

        return order

    def get_ready_steps(self, completed_steps: Set[str]) -> List[str]:
        """Get steps ready to execute (dependencies met)."""
        ready = []
        for step_id, step in self.steps.items():
            if step.status != StepStatus.PENDING:
                continue
            if all(dep in completed_steps for dep in step.dependencies):
                ready.append(step_id)
        return ready

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "steps": {k: v.to_dict() for k, v in self.steps.items()},
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat()
        }


@dataclass
class ExecutionContext:
    """Context passed during workflow execution."""
    workflow_id: str
    execution_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    step_outputs: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "variables": self.variables,
            "artifacts": self.artifacts,
            "step_outputs": self.step_outputs,
            "started_at": self.started_at.isoformat()
        }


@dataclass
class ExecutionResult:
    """Result of a workflow execution."""
    workflow_id: str
    execution_id: str
    status: str
    completed_steps: List[str]
    failed_step: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    outputs: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "status": self.status,
            "completed_steps": self.completed_steps,
            "failed_step": self.failed_step,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "outputs": self.outputs
        }


class WorkflowOrchestrator:
    """
    Orchestrates workflow execution.

    Manages workflow definitions, step execution, error handling,
    and provides visualization of workflow state.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.workflows: Dict[str, Workflow] = {}
        self.execution_history: List[ExecutionResult] = []
        self.step_handlers: Dict[StepType, Callable] = {}
        self.execution_lock: bool = False

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default step handlers."""
        self.step_handlers[StepType.TASK] = self._handle_task_step
        self.step_handlers[StepType.CONDITION] = self._handle_condition_step
        self.step_handlers[StepType.NOTIFICATION] = self._handle_notification_step

    def register_handler(
        self,
        step_type: StepType,
        handler: Callable[[WorkflowStep, ExecutionContext], Dict[str, Any]]
    ) -> None:
        """Register a custom handler for a step type."""
        self.step_handlers[step_type] = handler

    def load_workflow(self, path: str) -> Workflow:
        """Load a workflow from a JSON or YAML file."""
        filepath = Path(path)

        if filepath.suffix == '.json':
            with open(filepath) as f:
                data = json.load(f)
        elif filepath.suffix in ('.yaml', '.yml'):
            import yaml
            with open(filepath) as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

        return self._parse_workflow_data(data)

    def _parse_workflow_data(self, data: Dict[str, Any]) -> Workflow:
        """Parse workflow data into Workflow object."""
        steps = {}
        for step_data in data.get('steps', []):
            step = WorkflowStep(
                id=step_data['id'],
                name=step_data['name'],
                step_type=StepType(step_data['step_type']),
                config=step_data.get('config', {}),
                dependencies=step_data.get('dependencies', []),
                max_retries=step_data.get('max_retries', 3)
            )
            steps[step.id] = step

        return Workflow(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            steps=steps,
            metadata=data.get('metadata', {})
        )

    def create_workflow(
        self,
        name: str,
        description: str = "",
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """Create a new workflow definition."""
        import uuid

        workflow = Workflow(
            id=f"wf-{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            version=version,
            steps={},
            metadata=metadata or {}
        )

        self.workflows[workflow.id] = workflow
        return workflow

    def add_step(
        self,
        workflow_id: str,
        step_id: str,
        name: str,
        step_type: StepType,
        config: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        max_retries: int = 3
    ) -> Optional[WorkflowStep]:
        """Add a step to a workflow."""
        if workflow_id not in self.workflows:
            return None

        step = WorkflowStep(
            id=step_id,
            name=name,
            step_type=step_type,
            config=config or {},
            dependencies=dependencies or [],
            max_retries=max_retries
        )

        self.workflows[workflow_id].steps[step_id] = step
        self.workflows[workflow_id].modified_at = datetime.now()
        return step

    def execute(
        self,
        workflow_id: str,
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None
    ) -> ExecutionResult:
        """
        Execute a workflow.

        Args:
            workflow_id: ID of workflow to execute
            variables: Input variables
            context: Pre-existing execution context

        Returns:
            ExecutionResult with outcome
        """
        import uuid

        if workflow_id not in self.workflows:
            return ExecutionResult(
                workflow_id=workflow_id,
                execution_id=f"exec-{uuid.uuid4().hex[:8]}",
                status="failed",
                completed_steps=[],
                error_message="Workflow not found"
            )

        workflow = self.workflows[workflow_id]

        # Create execution context
        if context is None:
            exec_context = ExecutionContext(
                workflow_id=workflow_id,
                execution_id=f"exec-{uuid.uuid4().hex[:8]}",
                variables=variables or {}
            )
        else:
            exec_context = context
            exec_context.execution_id = f"exec-{uuid.uuid4().hex[:8]}"

        # Initialize result
        result = ExecutionResult(
            workflow_id=workflow_id,
            execution_id=exec_context.execution_id,
            status="running",
            completed_steps=[]
        )

        # Get execution order
        execution_order = workflow.get_execution_order()
        completed = set()
        failed_step_id = None

        logger.info(f"Executing workflow {workflow_id} with {len(execution_order)} steps")

        # Execute steps in order
        for step_id in execution_order:
            step = workflow.steps[step_id]

            # Check if step should run
            if step.status == StepStatus.SKIPPED:
                continue

            # Check dependencies
            if not all(dep in completed for dep in step.dependencies):
                logger.warning(f"Step {step_id} skipped - dependencies not met")
                continue

            # Execute step
            try:
                step.status = StepStatus.RUNNING
                step.started_at = datetime.now()

                handler = self.step_handlers.get(step.step_type)
                if handler:
                    output = handler(step, exec_context)
                    step.output = output
                    exec_context.step_outputs[step_id] = output
                else:
                    step.output = {}
                    logger.warning(f"No handler for step type {step.step_type}")

                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now()
                completed.add(step_id)
                result.completed_steps.append(step_id)

                logger.info(f"Step {step_id} completed successfully")

            except Exception as e:
                step.error = str(e)
                step.status_message = str(e)

                if step.retry_count < step.max_retries:
                    step.retry_count += 1
                    step.status = StepStatus.PENDING
                    logger.info(f"Step {step_id} failed, retry {step.retry_count}/{step.max_retries}")
                else:
                    step.status = StepStatus.FAILED
                    failed_step_id = step_id
                    result.failed_step = step_id
                    result.error_message = str(e)
                    result.status = "failed"
                    break

        # Finalize result
        result.completed_at = datetime.now()
        if result.started_at:
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()

        if not failed_step_id:
            result.status = "completed"
            result.outputs = exec_context.step_outputs

        self.execution_history.append(result)
        return result

    def _handle_task_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle a task step execution."""
        # This would integrate with your actual task execution system
        config = step.config

        # Simulate task execution
        command = config.get('command', '')
        script = config.get('script', '')

        if command:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=config.get('timeout', 300)
            )
            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        if script:
            # Execute Python script
            local_vars = {'context': context, 'step': step}
            exec(script, {}, local_vars)
            return local_vars.get('result', {})

        return {"message": "Task step executed"}

    def _handle_condition_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle a condition step."""
        condition = step.config.get('condition', '')
        variables = context.variables

        # Evaluate condition
        try:
            # Simple condition evaluation
            if '==' in condition:
                left, right = condition.split('==')
                result = str(eval(left.strip(), variables)) == str(right.strip())
            elif '!=' in condition:
                left, right = condition.split('!=')
                result = str(eval(left.strip(), variables)) != str(right.strip())
            elif '>' in condition:
                left, right = condition.split('>')
                result = float(eval(left.strip(), variables)) > float(right.strip())
            elif '<' in condition:
                left, right = condition.split('<')
                result = float(eval(left.strip(), variables)) < float(right.strip())
            elif 'in' in condition:
                left, right = condition.split('in')
                result = eval(left.strip(), variables) in eval(right.strip(), variables)
            else:
                result = bool(eval(condition, variables))
        except Exception as e:
            result = False
            step.status_message = f"Condition evaluation failed: {e}"

        return {"condition_met": result, "condition": condition}

    def _handle_notification_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle a notification step."""
        # This would integrate with notification systems
        return {"message": "Notification sent", "type": step.config.get('type', 'info')}

    def validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Validate a workflow definition."""
        if workflow_id not in self.workflows:
            return {"valid": False, "error": "Workflow not found"}

        workflow = self.workflows[workflow_id]
        errors = []
        warnings = []

        # Check for circular dependencies
        execution_order = workflow.get_execution_order()
        if len(execution_order) != len(workflow.steps):
            errors.append("Circular dependency detected")

        # Check for missing dependencies
        for step_id, step in workflow.steps.items():
            for dep in step.dependencies:
                if dep not in workflow.steps:
                    errors.append(f"Step {step_id} depends on missing step {dep}")

        # Check for unreachable steps
        completed = set()
        for step_id in execution_order:
            step = workflow.steps[step_id]
            if not all(d in completed for d in step.dependencies) and step.dependencies:
                warnings.append(f"Step {step_id} may have unmet dependencies")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "step_count": len(workflow.steps)
        }

    def generate_visualization(self, workflow_id: str) -> Dict[str, Any]:
        """Generate workflow visualization data."""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        workflow = self.workflows[workflow_id]

        nodes = []
        edges = []

        for step_id, step in workflow.steps.items():
            nodes.append({
                "id": step_id,
                "label": step.name,
                "type": step.step_type.value,
                "status": step.status.value
            })

            for dep in step.dependencies:
                edges.append({
                    "from": dep,
                    "to": step_id
                })

        return {
            "workflow": workflow.name,
            "nodes": nodes,
            "edges": edges,
            "execution_order": workflow.get_execution_order()
        }

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current execution status of a workflow."""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        workflow = self.workflows[workflow_id]

        status_counts = defaultdict(int)
        for step in workflow.steps.values():
            status_counts[step.status.value] += 1

        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": status_counts,
            "total_steps": len(workflow.steps),
            "progress": (status_counts['completed'] / len(workflow.steps) * 100) if workflow.steps else 0
        }


def main():
    """CLI entry point for workflow orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Orchestrator CLI")
    parser.add_argument("command", choices=["list", "execute", "validate", "visualize"])

    args = parser.parse_args()

    orchestrator = WorkflowOrchestrator()

    if args.command == "list":
        for wf_id, wf in orchestrator.workflows.items():
            print(f"{wf_id}: {wf.name} ({len(wf.steps)} steps)")

    elif args.command == "execute":
        wf_id = input("Workflow ID: ")
        result = orchestrator.execute(wf_id)
        print(json.dumps(result.to_dict(), indent=2))

    elif args.command == "validate":
        wf_id = input("Workflow ID: ")
        print(json.dumps(orchestrator.validate_workflow(wf_id), indent=2))

    elif args.command == "visualize":
        wf_id = input("Workflow ID: ")
        print(json.dumps(orchestrator.generate_visualization(wf_id), indent=2))


if __name__ == "__main__":
    main()
