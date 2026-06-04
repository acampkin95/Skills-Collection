# Checkpointing Best Practices

This document covers state management strategies for AI-assisted development, including checkpoint creation, restoration, and recovery procedures.

## Overview

Checkpointing is essential for:
- Long-running agent operations
- Recovery from failures
- State comparison and debugging
- Progress preservation across sessions

## Checkpoint Strategies

### 1. Strategic Checkpoint Schedule

**Frequency Guidelines:**

| Operation Type | Checkpoint Interval | Trigger Events |
|---------------|---------------------|----------------|
| Code generation | Every file or major change | File completion |
| Complex refactor | Every 3-5 subtasks | Milestone reached |
| Debugging session | Every significant discovery | Root cause found |
| Long computation | Every 10-30 minutes | Iteration complete |
| Before risky operation | Immediate | Before any `rm` or rewrite |

**Implementation:**
```python
from scripts.checkpoint_manager import CheckpointManager

manager = CheckpointManager({
    "storage_path": "./checkpoints",
    "auto_checkpoint_interval": 300,  # 5 minutes
    "max_checkpoints": 50,
    "retention_days": 7
})

# Create manual checkpoint before risky operation
checkpoint = manager.create_checkpoint(
    name="pre-refactor-user-service",
    checkpoint_type="refactor",
    state={
        "files_modified": ["user.py", "auth.py"],
        "test_results": {"passed": 45, "failed": 2},
        "progress": "50%"
    },
    description="State before user service refactor",
    tags=["refactor", "user-service", "pre-change"]
)
```

### 2. State Serialization

**What to Include:**

```python
complete_state = {
    # Source code state
    "files": {
        "path/to/file.py": {
            "content": "...",
            "checksum": "abc123",
            "last_modified": "2024-01-01T00:00:00Z"
        }
    },

    # Task state
    "current_task": {
        "id": "task-123",
        "name": "Implement feature X",
        "status": "in_progress",
        "progress": 0.75
    },

    # Agent context
    "context": {
        "goals": ["goal1", "goal2"],
        "completed_items": [...],
        "pending_items": [...],
        "decisions": [{"decision": "...", "rationale": "..."}]
    },

    # Test state
    "tests": {
        "last_run": "2024-01-01T00:00:00Z",
        "results": {...},
        "coverage": 85.5
    },

    # External state
    "external_apis": {...},
    "database_state": {...}
}
```

**Handling Non-Serializable Objects:**

```python
class StateSerializer:
    def prepare_for_serialization(self, obj):
        if hasattr(obj, '__dict__'):
            return {
                "_type": type(obj).__name__,
                "_data": self.prepare_for_serialization(vars(obj))
            }
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        elif callable(obj):
            return {"_callable": type(obj).__name__}
        else:
            return obj
```

### 3. Checkpoint Chain Management

Create checkpoint chains for complex operations:

```python
# Create initial checkpoint
initial = manager.create_checkpoint(
    name="feature-start",
    checkpoint_type="feature",
    state=initial_state,
    description="Starting point for new feature"
)

# Create progress checkpoints
progress1 = manager.create_checkpoint(
    name="feature-phase1-done",
    checkpoint_type="feature",
    state=state_after_phase1,
    parent_id=initial.id,
    description="Phase 1 complete"
)

# Final checkpoint
complete = manager.create_checkpoint(
    name="feature-complete",
    checkpoint_type="feature",
    state=final_state,
    parent_id=progress1.id,
    description="Feature implementation complete"
)

# Get the full chain
chain = manager.get_checkpoint_chain(complete.id)
for cp in chain:
    print(f"{cp.created_at}: {cp.name}")
```

### 4. Restoration Procedures

**Full Restore:**
```python
success, state = manager.restore_checkpoint(checkpoint_id)

if success:
    # Apply restored state
    for file_path, file_data in state.get("files", {}).items():
        write_file(file_path, file_data["content"])

    # Restore task state
    restore_task_state(state.get("current_task", {}))

    # Restore context
    restore_context(state.get("context", {}))
```

**Selective Restore:**
```python
# Restore only specific files
success, state = manager.restore_checkpoint(checkpoint_id)
if success:
    for file_path in ["user.py", "auth.py"]:
        if file_path in state["files"]:
            write_file(file_path, state["files"][file_path]["content"])
```

### 5. Comparison and Diff

```python
# Compare two checkpoints
diff = manager.compare_checkpoints(
    checkpoint_id1="cp-abc123",
    checkpoint_id2="cp-xyz789"
)

print(f"Added: {diff['summary']['added']}")
print(f"Removed: {diff['summary']['removed']}")
print(f"Changed: {diff['summary']['changed']}")

# View specific changes
for change in diff['changed_keys']:
    print(f"  {change['key']}:")
    print(f"    Old: {change['old_value']}")
    print(f"    New: {change['new_value']}")
```

## Recovery Procedures

### 1. Agent Failure Recovery

```python
def recover_from_failure(agent_id, checkpoint_id):
    """Recover agent state after failure."""
    # Restore from checkpoint
    success, state = checkpoint_manager.restore_checkpoint(checkpoint_id)

    if not success:
        # Fallback to earlier checkpoint
        checkpoints = checkpoint_manager.list_checkpoints()
        if checkpoints:
            success, state = checkpoint_manager.restore_checkpoint(
                checkpoints[-1].id
            )

    # Reinitialize agent with restored state
    agent = AgentCoordinator()
    agent.restore_state(state)

    # Resume task
    agent.resume_task(state.get("current_task_id"))

    return agent
```

### 2. Emergency Rollback

```python
def emergency_rollback(project_root, target_checkpoint):
    """Roll back to a known good state."""
    # Get checkpoint state
    success, state = checkpoint_manager.restore_checkpoint(target_checkpoint)

    if not success:
        raise Exception("Cannot restore checkpoint")

    # Identify files to restore
    files_to_restore = []
    for path, data in state.get("files", {}).items():
        full_path = os.path.join(project_root, path)
        files_to_restore.append((full_path, data["content"]))

    # Create backup of current state first
    backup_name = f"pre-rollback-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    backup_cp = checkpoint_manager.create_checkpoint(
        name=backup_name,
        checkpoint_type="rollback-backup",
        state=get_current_state(),
        description="State before emergency rollback"
    )

    # Apply restored files
    for path, content in files_to_restore:
        with open(path, 'w') as f:
            f.write(content)

    return backup_cp
```

### 3. Session Recovery

```python
def recover_session(session_id):
    """Recover a development session."""
    session_manager = SessionManager()
    session = session_manager.resume_session(session_id)

    # Get latest checkpoint
    checkpoints = checkpoint_manager.list_checkpoints(
        checkpoint_type="session",
        tags=[session_id]
    )

    if checkpoints:
        latest = checkpoints[0]
        success, state = checkpoint_manager.restore_checkpoint(latest.id)

        if success:
            # Restore context
            session.context = state.get("context", {})

            # Restore open files
            session.context.open_files = state.get("open_files", [])

            # Restore task queue
            session.context.task_queue = state.get("task_queue", [])

    return session
```

## Best Practices

### 1. Naming Conventions

```python
# Checkpoint naming pattern
patterns = {
    "feature_start": "feature-{feature_name}-start",
    "phase_complete": "feature-{feature_name}-phase-{phase_number}",
    "pre_refactor": "pre-refactor-{component_name}",
    "post_refactor": "post-refactor-{component_name}",
    "session_save": "session-{session_id}-{timestamp}"
}
```

### 2. Metadata Requirements

```python
checkpoint.metadata = {
    "project": "my-project",
    "version": "1.0.0",
    "agent_id": "agent-abc123",
    "created_during": "feature/fix/refactor/investigation",
    "user_notification": True,
    "auto_generated": False,
    "requires_review": True,  # For important checkpoints
    "related_issue": "JIRA-123"
}
```

### 3. Storage Management

```python
# Automatic cleanup
manager._enforce_retention_limit()

# Manual archive old checkpoints
manager.archive_checkpoint(old_checkpoint_id)

# Export for backup
manager.export_checkpoint(checkpoint_id, "/backup/path/checkpoint.json.gz")
```

### 4. Monitoring

```python
# Get checkpoint statistics
stats = manager.get_statistics()
print(f"Total checkpoints: {stats['total_checkpoints']}")
print(f"Total size: {stats['total_size_mb']} MB")
print(f"By type: {stats['by_type']}")

# Check for stale checkpoints
stale = [cp for cp in manager.checkpoints.values()
         if (datetime.now() - cp.created_at).days > 7]
```

## Anti-Patterns to Avoid

1. **Too Few Checkpoints:** Long gaps between saves
2. **Too Many Checkpoints:** Storage bloat, hard to find important ones
3. **No Naming Convention:** Impossible to find the right checkpoint
4. **Missing Validation:** Restoring corrupt checkpoints
5. **No Backup Before Restore:** Losing work if restore fails

## See Also

- [Agent Patterns](agent-patterns.md)
- [Session Management](../scripts/session-manager.py)
- [Workflow Orchestration](../scripts/workflow-orchestrator.py)
