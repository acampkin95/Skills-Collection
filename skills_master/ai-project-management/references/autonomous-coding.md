# Autonomous Coding Guidelines

This document outlines safety boundaries, approval workflows, and emergency procedures for autonomous AI coding operations.

## Overview

Autonomous coding enables AI agents to operate with minimal human intervention while maintaining safety, quality, and control.

## Safety Boundaries

### 1. Restricted Operations

These operations require explicit human approval:

| Operation | Risk Level | Approval Required |
|-----------|------------|-------------------|
| `rm -rf` or destructive delete | CRITICAL | Always |
| Database schema changes | HIGH | Always |
| Production deployments | HIGH | Always |
| Secret/key modifications | HIGH | Always |
| Security configuration | HIGH | Always |
| User data access | MEDIUM | Conditional |
| External API calls | LOW | Logging only |
| Code changes | LOW | Automated review |

### 2. Boundary Enforcement

```python
# core/safety/safety_boundary.py
from enum import Enum
from dataclasses import dataclass

class OperationRisk(Enum):
    SAFE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class SafetyBoundary:
    RESTRICTED_PATTERNS = [
        r'rm\s+-rf\s+',
        r'drop\s+table',
        r'delete\s+from\s+.*\s+where',
        r'exec\s*\(',
        r'subprocess.*shell=True',
        r'os\.system\s*\('
    ]

    def evaluate_operation(self, operation: str, context: dict) -> OperationRisk:
        """Evaluate risk level of an operation."""
        # Check for restricted patterns
        import re
        for pattern in self.RESTRICTED_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return OperationRisk.CRITICAL

        # Check context-specific risks
        if context.get('environment') == 'production':
            if any(keyword in operation.lower() for keyword in ['delete', 'drop', 'truncate']):
                return OperationRisk.CRITICAL

        # Default to safe
        return OperationRisk.SAFE

    def block_operation(self, operation: str, risk: OperationRisk) -> bool:
        """Block operation if risk is too high."""
        if risk.value >= OperationRisk.HIGH.value:
            raise SafetyViolationError(
                f"Operation blocked due to high risk ({risk.name})",
                operation=operation,
                risk_level=risk
            )
        return True
```

### 3. Sandbox Execution

```python
# core/safety/sandbox.py
class Sandbox:
    """Execute operations in isolated environment."""

    def __init__(self, environment="test"):
        self.environment = environment
        self.restrictions = self._load_restrictions()

    def _load_restrictions(self):
        return {
            "file_system": {
                "allowed_paths": ["/project/src", "/project/tests"],
                "read_only_paths": ["/project/tests"],
                "blocked_paths": ["/etc", "/usr", "/var/log", "/root"]
            },
            "network": {
                "allowed_hosts": ["localhost", "test.example.com"],
                "blocked_ports": [22, 3306, 5432, 6379]
            },
            "process": {
                "max_cpu_time": 60,
                "max_memory": 500 * 1024 * 1024,  # 500MB
                "allowed_commands": ["python", "pytest", "ruff", "mypy"]
            }
        }

    def execute(self, command: str) -> ExecutionResult:
        """Execute command in sandbox."""
        # Validate command
        if not self._is_command_allowed(command):
            raise SandboxViolationError("Command not allowed in sandbox")

        # Run with restrictions
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            timeout=self.restrictions["process"]["max_cpu_time"],
            cwd="/project"
        )

        return ExecutionResult(
            returncode=result.returncode,
            stdout=result.stdout.decode(),
            stderr=result.stderr.decode()
        )
```

## Human-in-the-Loop Patterns

### 1. Approval Workflow

```python
# core/approval/approval_workflow.py
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class ApprovalType(Enum):
    CODE_CHANGE = "code_change"
    DEPLOYMENT = "deployment"
    DATA_ACCESS = "data_access"
    EXTERNAL_CALL = "external_call"
    SCHEMA_CHANGE = "schema_change"

@dataclass
class ApprovalRequest:
    id: str
    approval_type: ApprovalType
    description: str
    requester: str
    created_at: datetime
    status: str = "pending"
    approver: str = None
    approved_at: datetime = None
    comments: str = None
    payload: dict = None

class ApprovalWorkflow:
    def __init__(self, config):
        self.config = config
        self.pending_approvals: Dict[str, ApprovalRequest] = {}

    def create_request(
        self,
        approval_type: ApprovalType,
        description: str,
        requester: str,
        payload: dict = None
    ) -> ApprovalRequest:
        """Create approval request."""
        request = ApprovalRequest(
            id=f"apr-{uuid.uuid4().hex[:8]}",
            approval_type=approval_type,
            description=description,
            requester=requester,
            created_at=datetime.now(),
            payload=payload
        )

        self.pending_approvals[request.id] = request

        # Send notification
        self._notify_approvers(request)

        return request

    def approve(self, request_id: str, approver: str, comments: str = None):
        """Approve a request."""
        if request_id not in self.pending_approvals:
            raise RequestNotFoundError(request_id)

        request = self.pending_approvals[request_id]
        request.status = "approved"
        request.approver = approver
        request.approved_at = datetime.now()
        request.comments = comments

        # Execute approved action
        self._execute_approved_action(request)

        return request

    def _notify_approvers(self, request: ApprovalRequest):
        """Send notification to approvers."""
        # Integration with Slack, email, etc.
        pass
```

### 2. Parallel Approval

```python
# For changes affecting multiple teams
class ParallelApprovalWorkflow(ApprovalWorkflow):
    def create_multi_team_request(
        self,
        teams: List[str],
        description: str,
        requester: str
    ) -> MultiTeamRequest:
        """Create request requiring approval from multiple teams."""
        request = MultiTeamRequest(
            id=f"mtr-{uuid.uuid4().hex[:8]}",
            teams=teams,
            description=description,
            requester=requester,
            approvals={team: "pending" for team in teams}
        )

        for team in teams:
            self._notify_team(team, request)

        return request

    def check_complete(self, request_id: str) -> bool:
        """Check if all teams have approved."""
        request = self.pending_approvals[request_id]
        return all(status == "approved" for status in request.approvals.values())
```

### 3. Time-Limited Approvals

```python
class TimeLimitedApproval:
    """Approvals that expire after a time limit."""

    def __init__(self, default_timeout_minutes=60):
        self.default_timeout = default_timeout_minutes

    def create_expiring_request(
        self,
        approval_type: ApprovalType,
        description: str,
        requester: str,
        timeout_minutes: int = None
    ) -> ExpiringRequest:
        """Create approval with expiration."""
        timeout = timeout_minutes or self.default_timeout

        request = ExpiringRequest(
            id=f"apr-{uuid.uuid4().hex[:8]}",
            approval_type=approval_type,
            description=description,
            requester=requester,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=timeout),
            status="pending"
        )

        # Schedule expiration check
        self._schedule_expiration(request)

        return request

    def _schedule_expiration(self, request: ExpiringRequest):
        """Schedule automatic expiration."""
        import threading
        timer = threading.Timer(
            (request.expires_at - datetime.now()).total_seconds(),
            self._expire_request,
            args=[request.id]
        )
        timer.start()
```

## Emergency Stop Procedures

### 1. Emergency Stop Switch

```python
# core/emergency/emergency_stop.py
class EmergencyStop:
    """Emergency stop mechanism for all agent operations."""

    _instance = None
    _stop_requested = False
    _stop_reason = None
    _authorized_stoppers = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def add_authorized_stopper(cls, user_id: str):
        """Add user authorized to trigger emergency stop."""
        cls._authorized_stoppers.add(user_id)

    @classmethod
    def emergency_stop(cls, user_id: str, reason: str = "Unknown"):
        """Immediately stop all agent operations."""
        if user_id not in cls._authorized_stoppers:
            raise UnauthorizedError(f"User {user_id} not authorized for emergency stop")

        cls._stop_requested = True
        cls._stop_reason = reason

        # Log the stop
        cls._log_stop(user_id, reason)

        # Signal all agents to stop
        cls._signal_agents_to_stop()

        return StopConfirmation(
            stopped_at=datetime.now(),
            stopped_by=user_id,
            reason=reason
        )

    @classmethod
    def check_stop_requested(cls) -> bool:
        """Check if emergency stop was requested."""
        return cls._stop_requested

    @classmethod
    def reset(cls):
        """Reset emergency stop (after addressing issue)."""
        cls._stop_requested = False
        cls._stop_reason = None

    @classmethod
    def _signal_agents_to_stop(cls):
        """Signal all running agents to stop."""
        # Implementation depends on agent infrastructure
        pass
```

### 2. Graceful Shutdown Protocol

```python
# core/emergency/graceful_shutdown.py
class GracefulShutdown:
    """Graceful shutdown for agent operations."""

    def __init__(self, agent_coordinator):
        self.coordinator = agent_coordinator
        self.shutdown_sequence = []

    def initiate_shutdown(self, reason: str):
        """Initiate graceful shutdown sequence."""
        # Step 1: Log current state
        self._log_state()

        # Step 2: Complete current atomic operations
        self._complete_current_operations()

        # Step 3: Save checkpoints
        self._create_shutdown_checkpoints()

        # Step 4: Notify stakeholders
        self._notify_stakeholders(reason)

        # Step 5: Terminate agents
        self._terminate_agents()

    def _complete_current_operations(self):
        """Allow current operations to complete."""
        for agent in self.coordinator.get_active_agents():
            if agent.current_task and agent.current_task.atomic:
                # Wait for completion
                agent.wait_for_completion(timeout=300)
            else:
                # Save partial work and stop
                self._save_partial_progress(agent)
```

### 3. Rollback Protocol

```python
# core/emergency/rollback_protocol.py
class RollbackProtocol:
    """Protocol for rolling back agent changes."""

    def __init__(self, checkpoint_manager):
        self.checkpoint_manager = checkpoint_manager

    def initiate_rollback(
        self,
        checkpoint_id: str,
        scope: str = "all",
        reason: str = "Emergency rollback"
    ) -> RollbackResult:
        """Execute rollback to a previous checkpoint."""
        # Step 1: Verify checkpoint exists
        checkpoint = self.checkpoint_manager.get_checkpoint(checkpoint_id)
        if not checkpoint:
            raise CheckpointNotFoundError(checkpoint_id)

        # Step 2: Create backup of current state
        backup = self.checkpoint_manager.create_checkpoint(
            name=f"pre-rollback-{datetime.now().isoformat()}",
            checkpoint_type="rollback-backup",
            state=self._capture_current_state()
        )

        # Step 3: Apply rollback
        success = self._apply_rollback(checkpoint, scope)

        if success:
            return RollbackResult(
                success=True,
                checkpoint_id=checkpoint_id,
                backup_id=backup.id,
                reason=reason
            )
        else:
            # Attempt restore from backup
            self._restore_backup(backup)
            return RollbackResult(
                success=False,
                checkpoint_id=checkpoint_id,
                backup_id=backup.id,
                reason="Rollback failed, restored to backup"
            )
```

## Autonomous Operation Limits

### 1. Operation Limits

```python
# core/limits/operation_limits.py
@dataclass
class OperationLimits:
    max_file_modifications: int = 10
    max_files_per_commit: int = 20
    max_total_changes: int = 500
    max_run_duration_hours: int = 8
    max_approvals_before_review: int = 5
    max_cost_per_session: float = 10.0
    max_concurrent_operations: int = 3

class LimitEnforcer:
    def __init__(self, limits: OperationLimits):
        self.limits = limits
        self.current_usage = defaultdict(int)

    def check_limits(self, operation_type: str) -> LimitCheckResult:
        """Check if operation is within limits."""
        if self.current_usage[operation_type] >= getattr(
            self.limits, f"max_{operation_type}", float('inf')
        ):
            return LimitCheckResult(
                allowed=False,
                reason=f"Limit reached for {operation_type}",
                current=self.current_usage[operation_type]
            )

        return LimitCheckResult(allowed=True)

    def record_operation(self, operation_type: str, count: int = 1):
        """Record operation for limit tracking."""
        self.current_usage[operation_type] += count
```

### 2. Cost Limits

```python
# core/limits/cost_limits.py
class CostLimitEnforcer:
    def __init__(self, max_cost: float = 10.0):
        self.max_cost = max_cost
        self.current_cost = 0.0

    def estimate_cost(self, operation: str) -> float:
        """Estimate cost of an operation."""
        cost_estimates = {
            "code_generation": 0.01,
            "code_review": 0.02,
            "refactor": 0.05,
            "deployment": 0.10
        }
        return cost_estimates.get(operation, 0.01)

    def pre_execution_check(self, operation: str) -> bool:
        """Check if operation can proceed within budget."""
        estimated = self.estimate_cost(operation)
        if self.current_cost + estimated > self.max_cost:
            raise CostLimitExceededError(
                f"Would exceed cost limit: {self.current_cost + estimated} > {self.max_cost}"
            )
        return True

    def record_cost(self, operation: str, actual_cost: float):
        """Record actual cost after operation."""
        self.current_cost += actual_cost
```

## Audit Trail

```python
# core/audit/audit_trail.py
class AuditTrail:
    """Comprehensive audit logging for autonomous operations."""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.entries = []

    def log(self, event_type: str, details: dict):
        """Log an audit event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "agent_id": self._get_agent_id(),
            "session_id": self._get_session_id()
        }

        self.entries.append(entry)
        self._persist_entry(entry)

    def log_approval_request(self, request: ApprovalRequest):
        """Log approval request."""
        self.log("approval_request", {
            "request_id": request.id,
            "type": request.approval_type.value,
            "description": request.description,
            "requester": request.requester
        })

    def log_approval_decision(self, request: ApprovalRequest, decision: str):
        """Log approval decision."""
        self.log("approval_decision", {
            "request_id": request.id,
            "decision": decision,
            "approver": request.approver,
            "comments": request.comments
        })

    def log_operation(self, operation: str, details: dict):
        """Log operation execution."""
        self.log("operation_executed", {
            "operation": operation,
            **details
        })

    def export_audit_report(self, start_date: datetime, end_date: datetime) -> str:
        """Export audit report for date range."""
        filtered = [
            e for e in self.entries
            if start_date <= datetime.fromisoformat(e["timestamp"]) <= end_date
        ]

        return json.dumps(filtered, indent=2)
```

## Best Practices

1. **Fail-Safe Defaults:** Start with restrictive, expand as needed
2. **Double-Verify Critical:** Always verify destructive operations
3. **Log Everything:** Comprehensive audit trail
4. **Regular Reviews:** Periodic review of autonomous operations
5. **Incident Response:** Clear procedures for issues
6. **Training:** Ensure operators understand safety procedures

## See Also

- [Agent Patterns](agent-patterns.md)
- [Checkpoint Management](checkpointing.md)
- [Quality Gates](quality-gate.py)
