#!/usr/bin/env python3
"""
Checkpoint Manager - Save and restore agent state.

This module provides capabilities for:
- Creating checkpoints with metadata
- Restoring from checkpoints
- Comparing checkpoint states
- Automatic checkpoint scheduling
"""

import gzip
import hashlib
import json
import logging
import os
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from threading import Thread, Lock

logger = logging.getLogger(__name__)


class CheckpointStatus(Enum):
    """Status of a checkpoint."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    CORRUPTED = "corrupted"


@dataclass
class Checkpoint:
    """Represents a saved checkpoint."""
    id: str
    name: str
    description: str
    checkpoint_type: str
    created_at: datetime
    created_by: str
    state: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    status: CheckpointStatus = CheckpointStatus.ACTIVE
    parent_id: Optional[str] = None
    size_bytes: int = 0
    checksum: str = ""
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "checkpoint_type": self.checkpoint_type,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "state_keys": list(self.state.keys()),
            "metadata": self.metadata,
            "tags": self.tags,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class CheckpointConfig:
    """Configuration for checkpoint manager."""
    storage_path: str = "./checkpoints"
    max_checkpoints: int = 50
    auto_checkpoint_interval: int = 300  # seconds
    compression: bool = True
    encryption: bool = False
    retention_days: int = 7
    enable_scheduling: bool = True


class CheckpointManager:
    """
    Manages checkpoints for agent state persistence.

    Provides checkpoint creation, restoration, comparison, and automatic
    scheduling for long-running operations.
    """

    def __init__(self, config: Optional[CheckpointConfig] = None):
        self.config = config or CheckpointConfig()
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.current_state: Dict[str, Any] = {}
        self._lock = Lock()
        self._scheduler_thread: Optional[Thread] = None
        self._scheduled_checkpoints: Dict[str, datetime] = {}

        # Ensure storage directory exists
        Path(self.config.storage_path).mkdir(parents=True, exist_ok=True)

        # Load existing checkpoints
        self._load_existing_checkpoints()

    def _load_existing_checkpoints(self) -> None:
        """Load existing checkpoints from storage."""
        checkpoint_dir = Path(self.config.storage_path)

        for cp_file in checkpoint_dir.glob("*.json.gz"):
            try:
                with gzip.open(cp_file, 'rt') as f:
                    data = json.load(f)
                    checkpoint = self._dict_to_checkpoint(data)
                    if checkpoint:
                        self.checkpoints[checkpoint.id] = checkpoint
            except Exception as e:
                logger.error(f"Failed to load checkpoint {cp_file}: {e}")

        logger.info(f"Loaded {len(self.checkpoints)} existing checkpoints")

    def _dict_to_checkpoint(self, data: Dict[str, Any]) -> Optional[Checkpoint]:
        """Convert dictionary to Checkpoint object."""
        try:
            return Checkpoint(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                checkpoint_type=data["checkpoint_type"],
                created_at=datetime.fromisoformat(data["created_at"]),
                created_by=data["created_by"],
                state={},  # State loaded separately
                metadata=data.get("metadata", {}),
                tags=data.get("tags", []),
                status=CheckpointStatus(data.get("status", "active")),
                parent_id=data.get("parent_id"),
                size_bytes=data.get("size_bytes", 0),
                checksum=data.get("checksum", ""),
                expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
            )
        except Exception as e:
            logger.error(f"Error converting dict to checkpoint: {e}")
            return None

    def create_checkpoint(
        self,
        name: str,
        checkpoint_type: str,
        state: Dict[str, Any],
        description: str = "",
        created_by: str = "system",
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """
        Create a new checkpoint.

        Args:
            name: Human-readable name
            checkpoint_type: Type of checkpoint (e.g., "task", "session")
            state: State data to save
            description: Optional description
            created_by: Who/what created this checkpoint
            tags: Optional tags for organization
            parent_id: Parent checkpoint ID for chains
            metadata: Optional additional metadata

        Returns:
            Created Checkpoint instance
        """
        with self._lock:
            checkpoint_id = f"cp-{uuid.uuid4().hex[:12]}"

            # Prepare state for storage
            state_copy = self._prepare_state(state)

            # Calculate checksum
            state_json = json.dumps(state_copy, sort_keys=True, default=str)
            checksum = hashlib.sha256(state_json.encode()).hexdigest()

            # Calculate size
            size_bytes = len(state_json.encode())

            # Determine expiration
            expires_at = datetime.now() + timedelta(days=self.config.retention_days)

            checkpoint = Checkpoint(
                id=checkpoint_id,
                name=name,
                description=description,
                checkpoint_type=checkpoint_type,
                created_at=datetime.now(),
                created_by=created_by,
                state=state_copy,
                tags=tags or [],
                parent_id=parent_id,
                size_bytes=size_bytes,
                checksum=checksum,
                expires_at=expires_at,
                metadata=metadata or {}
            )

            # Save to storage
            self._save_checkpoint(checkpoint)

            # Add to memory
            self.checkpoints[checkpoint_id] = checkpoint

            # Update current state
            self.current_state = state_copy

            # Enforce retention limit
            self._enforce_retention_limit()

            logger.info(f"Created checkpoint {checkpoint_id}: {name}")
            return checkpoint

    def _prepare_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare state for storage (handle non-serializable objects)."""
        prepared = {}

        for key, value in state.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                prepared[key] = value
            elif isinstance(value, list):
                prepared[key] = [
                    self._prepare_state_item(item)
                    for item in value
                ]
            elif isinstance(value, dict):
                prepared[key] = {k: self._prepare_state_item(v) for k, v in value.items()}
            elif hasattr(value, '__dict__'):
                prepared[key] = {
                    "_type": type(value).__name__,
                    "_data": self._prepare_state(vars(value))
                }
            else:
                prepared[key] = str(value)

        return prepared

    def _prepare_state_item(self, item: Any) -> Any:
        """Prepare a single state item."""
        if isinstance(item, (str, int, float, bool, type(None))):
            return item
        elif isinstance(item, dict):
            return self._prepare_state(item)
        elif hasattr(item, '__dict__'):
            return {
                "_type": type(item).__name__,
                "_data": self._prepare_state(vars(item))
            }
        else:
            return str(item)

    def _save_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to disk."""
        checkpoint_dir = Path(self.config.storage_path)

        # Create checkpoint data
        data = {
            "id": checkpoint.id,
            "name": checkpoint.name,
            "description": checkpoint.description,
            "checkpoint_type": checkpoint.checkpoint_type,
            "created_at": checkpoint.created_at.isoformat(),
            "created_by": checkpoint.created_by,
            "state": checkpoint.state,
            "metadata": checkpoint.metadata,
            "tags": checkpoint.tags,
            "status": checkpoint.status.value,
            "parent_id": checkpoint.parent_id,
            "size_bytes": checkpoint.size_bytes,
            "checksum": checkpoint.checksum,
            "expires_at": checkpoint.expires_at.isoformat() if checkpoint.expires_at else None
        }

        # Save with compression
        filename = f"{checkpoint.id}.json.gz"
        filepath = checkpoint_dir / filename

        with gzip.open(filepath, 'wt', compresslevel=6) as f:
            json.dump(data, f, indent=2, default=str)

        logger.debug(f"Saved checkpoint to {filepath}")

    def restore_checkpoint(
        self,
        checkpoint_id: str,
        verify_checksum: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Restore state from a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore
            verify_checksum: Whether to verify checksum integrity

        Returns:
            Tuple of (success, state)
        """
        with self._lock:
            if checkpoint_id not in self.checkpoints:
                logger.error(f"Checkpoint {checkpoint_id} not found")
                return False, {}

            checkpoint = self.checkpoints[checkpoint_id]

            # Verify checksum if requested
            if verify_checksum:
                state_json = json.dumps(checkpoint.state, sort_keys=True, default=str)
                calculated_checksum = hashlib.sha256(state_json.encode()).hexdigest()

                if calculated_checksum != checkpoint.checksum:
                    logger.error(f"Checkpoint {checkpoint_id} checksum mismatch")
                    checkpoint.status = CheckpointStatus.CORRUPTED
                    return False, {}

            logger.info(f"Restored checkpoint {checkpoint_id}: {checkpoint.name}")
            return True, checkpoint.state

    def compare_checkpoints(
        self,
        checkpoint_id1: str,
        checkpoint_id2: str
    ) -> Dict[str, Any]:
        """
        Compare two checkpoints.

        Args:
            checkpoint_id1: First checkpoint ID
            checkpoint_id2: Second checkpoint ID

        Returns:
            Comparison results
        """
        if checkpoint_id1 not in self.checkpoints or checkpoint_id2 not in self.checkpoints:
            return {"error": "One or both checkpoints not found"}

        cp1 = self.checkpoints[checkpoint_id1]
        cp2 = self.checkpoints[checkpoint_id2]

        # Find differences
        all_keys = set(cp1.state.keys()) | set(cp2.state.keys())
        added = set(cp2.state.keys()) - set(cp1.state.keys())
        removed = set(cp1.state.keys()) - set(cp2.state.keys())
        changed = []
        unchanged = []

        for key in all_keys:
            if key in added or key in removed:
                continue

            val1 = json.dumps(cp1.state[key], sort_keys=True, default=str)
            val2 = json.dumps(cp2.state[key], sort_keys=True, default=str)

            if val1 != val2:
                changed.append({
                    "key": key,
                    "old_value": cp1.state[key],
                    "new_value": cp2.state[key]
                })
            else:
                unchanged.append(key)

        return {
            "checkpoint1": {
                "id": cp1.id,
                "name": cp1.name,
                "created_at": cp1.created_at.isoformat()
            },
            "checkpoint2": {
                "id": cp2.id,
                "name": cp2.name,
                "created_at": cp2.created_at.isoformat()
            },
            "time_difference": str(cp2.created_at - cp1.created_at),
            "summary": {
                "total_keys": len(all_keys),
                "added": len(added),
                "removed": len(removed),
                "changed": len(changed),
                "unchanged": len(unchanged)
            },
            "added_keys": list(added),
            "removed_keys": list(removed),
            "changed_keys": changed,
            "unchanged_keys": unchanged
        }

    def list_checkpoints(
        self,
        checkpoint_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Checkpoint]:
        """
        List available checkpoints with optional filtering.

        Args:
            checkpoint_type: Filter by type
            tags: Filter by tags (any match)
            limit: Maximum results

        Returns:
            List of matching checkpoints
        """
        results = []

        for checkpoint in self.checkpoints.values():
            if checkpoint.status == CheckpointStatus.ARCHIVED:
                continue

            # Filter by type
            if checkpoint_type and checkpoint.checkpoint_type != checkpoint_type:
                continue

            # Filter by tags
            if tags:
                if not any(tag in checkpoint.tags for tag in tags):
                    continue

            results.append(checkpoint)

        # Sort by creation date (newest first)
        results.sort(key=lambda cp: cp.created_at, reverse=True)

        return results[:limit]

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to delete

        Returns:
            True if deleted
        """
        with self._lock:
            if checkpoint_id not in self.checkpoints:
                return False

            checkpoint = self.checkpoints[checkpoint_id]

            # Delete file
            filepath = Path(self.config.storage_path) / f"{checkpoint_id}.json.gz"
            if filepath.exists():
                filepath.unlink()

            # Remove from memory
            del self.checkpoints[checkpoint_id]

            logger.info(f"Deleted checkpoint {checkpoint_id}")
            return True

    def archive_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Archive a checkpoint (mark as archived, keep file).

        Args:
            checkpoint_id: ID of checkpoint to archive

        Returns:
            True if archived
        """
        with self._lock:
            if checkpoint_id not in self.checkpoints:
                return False

            self.checkpoints[checkpoint_id].status = CheckpointStatus.ARCHIVED
            logger.info(f"Archived checkpoint {checkpoint_id}")
            return True

    def _enforce_retention_limit(self) -> None:
        """Remove oldest checkpoints if over limit."""
        if len(self.checkpoints) <= self.config.max_checkpoints:
            return

        # Sort by creation date
        sorted_cps = sorted(
            self.checkpoints.values(),
            key=lambda cp: cp.created_at
        )

        # Remove oldest
        to_remove = len(self.checkpoints) - self.config.max_checkpoints
        for cp in sorted_cps[:to_remove]:
            self.delete_checkpoint(cp.id)

    def start_auto_checkpointing(
        self,
        name_prefix: str,
        checkpoint_type: str,
        interval_seconds: Optional[int] = None
    ) -> None:
        """
        Start automatic checkpoint scheduling.

        Args:
            name_prefix: Prefix for checkpoint names
            checkpoint_type: Type of checkpoints
            interval_seconds: Checkpoint interval (default from config)
        """
        if not self.config.enable_scheduling:
            logger.warning("Auto checkpointing is disabled in config")
            return

        interval = interval_seconds or self.config.auto_checkpoint_interval

        def scheduler_loop():
            while True:
                import time
                time.sleep(interval)

                checkpoint_name = f"{name_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                self.create_checkpoint(
                    name=checkpoint_name,
                    checkpoint_type=checkpoint_type,
                    state=self.current_state.copy(),
                    description=f"Auto checkpoint",
                    tags=["auto", name_prefix]
                )

        self._scheduler_thread = Thread(target=scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        logger.info(f"Started auto checkpointing every {interval} seconds")

    def stop_auto_checkpointing(self) -> None:
        """Stop automatic checkpoint scheduling."""
        if self._scheduler_thread:
            self._scheduler_thread = None
            logger.info("Stopped auto checkpointing")

    def get_checkpoint_chain(self, checkpoint_id: str) -> List[Checkpoint]:
        """
        Get the chain of checkpoints leading to this one.

        Args:
            checkpoint_id: Starting checkpoint ID

        Returns:
            List of checkpoints from earliest to current
        """
        chain = []
        current_id = checkpoint_id

        while current_id and current_id in self.checkpoints:
            cp = self.checkpoints[current_id]
            chain.insert(0, cp)
            current_id = cp.parent_id

        return chain

    def export_checkpoint(self, checkpoint_id: str, path: str) -> bool:
        """
        Export a checkpoint to a file.

        Args:
            checkpoint_id: ID of checkpoint to export
            path: Destination path

        Returns:
            True if exported successfully
        """
        if checkpoint_id not in self.checkpoints:
            return False

        checkpoint = self.checkpoints[checkpoint_id]

        # Copy the file
        src = Path(self.config.storage_path) / f"{checkpoint_id}.json.gz"
        dst = Path(path)

        if src.exists():
            shutil.copy2(src, dst)
            logger.info(f"Exported checkpoint {checkpoint_id} to {path}")
            return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        total_size = sum(cp.size_bytes for cp in self.checkpoints.values())
        by_type = {}
        for cp in self.checkpoints.values():
            by_type[cp.checkpoint_type] = by_type.get(cp.checkpoint_type, 0) + 1

        return {
            "total_checkpoints": len(self.checkpoints),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_type": by_type,
            "storage_path": self.config.storage_path
        }


def main():
    """CLI entry point for checkpoint manager."""
    import argparse

    parser = argparse.ArgumentParser(description="Checkpoint Manager CLI")
    parser.add_argument("--path", default="./checkpoints", help="Checkpoint storage path")
    parser.add_argument("command", choices=[
        "create", "list", "restore", "compare", "delete", "stats"
    ])

    args = parser.parse_args()

    config = CheckpointConfig(storage_path=args.path)
    manager = CheckpointManager(config)

    if args.command == "create":
        name = input("Checkpoint name: ")
        ctype = input("Type: ")
        print("Enter state as JSON (empty for {}):")
        state_input = input().strip()
        state = json.loads(state_input) if state_input else {}

        cp = manager.create_checkpoint(name, ctype, state)
        print(f"Created checkpoint: {cp.id}")

    elif args.command == "list":
        checkpoints = manager.list_checkpoints()
        for cp in checkpoints:
            print(f"{cp.id} | {cp.name} | {cp.checkpoint_type} | {cp.created_at}")

    elif args.command == "restore":
        cp_id = input("Checkpoint ID: ")
        success, state = manager.restore_checkpoint(cp_id)
        if success:
            print("Restored state:")
            print(json.dumps(state, indent=2))
        else:
            print("Restore failed")

    elif args.command == "compare":
        cp1 = input("First checkpoint ID: ")
        cp2 = input("Second checkpoint ID: ")
        result = manager.compare_checkpoints(cp1, cp2)
        print(json.dumps(result, indent=2))

    elif args.command == "delete":
        cp_id = input("Checkpoint ID: ")
        if manager.delete_checkpoint(cp_id):
            print("Deleted checkpoint")
        else:
            print("Checkpoint not found")

    elif args.command == "stats":
        print(json.dumps(manager.get_statistics(), indent=2))


if __name__ == "__main__":
    main()
