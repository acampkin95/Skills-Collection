#!/usr/bin/env python3
"""
macOS: LaunchAgent and LaunchDaemon management.

Provides configuration, installation, and management of launchd services.
"""

import subprocess
import os
import plistlib
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from enum import Enum


class LaunchdType(Enum):
    """Type of launchd item."""
    AGENT = "Agent"
    DAEMON = "Daemon"


class LaunchdState(Enum):
    """State of a launchd item."""
    LOADED = "loaded"
    UNLOADED = "unloaded"
    UNKNOWN = "unknown"


@dataclass
class LaunchdItem:
    """Information about a launchd item."""
    label: str
    path: str
    type: LaunchdType
    state: LaunchdState
    disabled: bool
    description: str = ""
    run_at_load: bool = False
    keep_alive: bool = False
    start_interval: Optional[int] = None
    program: Optional[str] = None
    program_arguments: List[str] = field(default_factory=list)
    working_directory: Optional[str] = None
    environment_variables: Dict[str, str] = field(default_factory=dict)
    stdout_path: Optional[str] = None
    stderr_path: Optional[str] = None


class LaunchdError(Exception):
    """Exception raised for launchd operations."""
    pass


def _run_launchctl(args: List[str], user: bool = True) -> subprocess.CompletedProcess:
    """
    Run a launchctl command.

    Args:
        args: Arguments to pass to launchctl
        user: Run as current user (vs root)

    Returns:
        CompletedProcess result
    """
    cmd = ['launchctl'] + args

    # Set environment for GUI access if needed
    env = os.environ.copy()
    if user:
        env['DBUS_LAUNCHD_SESSION_BUS_ADDRESS'] = \
            env.get('DBUS_LAUNCHD_SESSION_BUS_ADDRESS', '')

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
        return result
    except subprocess.TimeoutExpired:
        raise LaunchdError("launchctl command timed out")


def list_loaded(user: bool = True) -> List[Dict[str, str]]:
    """
    List loaded launchd items.

    Args:
        user: List user items (vs system)

    Returns:
        List of loaded item dictionaries
    """
    if user:
        result = _run_launchctl(['list'])
    else:
        result = _run_launchctl(['list', '-'], user=False)

    items = []

    for line in result.stdout.strip().split('\n'):
        if line and not line.startswith('"'):
            # Parse: PID   Status   Label
            parts = line.split(None, 2)
            if len(parts) >= 3:
                pid = parts[0] if parts[0] != '-' else None
                status = parts[1]
                label = parts[2].strip('"')

                items.append({
                    'label': label,
                    'pid': pid,
                    'status': status,
                })

    return items


def load(plist_path: str, user: bool = True, enable: bool = True) -> bool:
    """
    Load a launchd item.

    Args:
        plist_path: Path to .plist file
        user: Load for current user
        enable: Enable the item

    Returns:
        True if loading succeeded
    """
    args = ['load']

    if enable:
        args.append('-w')  # Enable and keep enabled

    args.append(plist_path)

    try:
        result = _run_launchctl(args, user=user)
        return result.returncode == 0
    except LaunchdError:
        return False


def unload(plist_path: str, user: bool = True) -> bool:
    """
    Unload a launchd item.

    Args:
        plist_path: Path to .plist file
        user: Unload for current user

    Returns:
        True if unloading succeeded
    """
    args = ['unload', plist_path]

    try:
        result = _run_launchctl(args, user=user)
        return result.returncode == 0
    except LaunchdError:
        return False


def start(label: str, user: bool = True) -> bool:
    """
    Start a loaded launchd item.

    Args:
        label: The label of the item
        user: Run as current user

    Returns:
        True if starting succeeded
    """
    try:
        result = _run_launchctl(['start', label], user=user)
        return result.returncode == 0
    except LaunchdError:
        return False


def stop(label: str, user: bool = True) -> bool:
    """
    Stop a loaded launchd item.

    Args:
        label: The label of the item
        user: Run as current user

    Returns:
        True if stopping succeeded
    """
    try:
        result = _run_launchctl(['stop', label], user=user)
        return result.returncode == 0
    except LaunchdError:
        return False


def status(label: str, user: bool = True) -> Dict[str, Any]:
    """
    Get the status of a launchd item.

    Args:
        label: The label of the item
        user: Check for current user

    Returns:
        Dictionary with status information
    """
    loaded = list_loaded(user=user)
    loaded_items = {item['label']: item for item in loaded}

    if label in loaded_items:
        return {
            'loaded': True,
            'running': loaded_items[label]['pid'] != '-',
            'pid': loaded_items[label]['pid'],
            'status': loaded_items[label]['status'],
        }
    else:
        return {
            'loaded': False,
            'running': False,
            'pid': None,
            'status': None,
        }


def remove_disabled_flag(plist_path: str) -> bool:
    """
    Remove the disabled flag from a plist.

    Args:
        plist_path: Path to .plist file

    Returns:
        True if flag was removed
    """
    try:
        with open(plist_path, 'rb') as f:
            data = plistlib.load(f)

        if 'Disabled' in data:
            del data['Disabled']

        with open(plist_path, 'wb') as f:
            plistlib.dump(data, f)

        return True
    except Exception as e:
        return False


def set_disabled_flag(plist_path: str, disabled: bool = True) -> bool:
    """
    Set or remove the disabled flag in a plist.

    Args:
        plist_path: Path to .plist file
        disabled: Whether to disable

    Returns:
        True if flag was set
    """
    try:
        with open(plist_path, 'rb') as f:
            data = plistlib.load(f)

        data['Disabled'] = disabled

        with open(plist_path, 'wb') as f:
            plistlib.dump(data, f)

        return True
    except Exception as e:
        return False


def parse_plist(plist_path: str) -> Dict[str, Any]:
    """
    Parse a launchd plist file.

    Args:
        plist_path: Path to .plist file

    Returns:
        Dictionary with plist contents
    """
    try:
        with open(plist_path, 'rb') as f:
            return plistlib.load(f)
    except Exception as e:
        raise LaunchdError(f"Failed to parse plist: {e}")


def create_plist(
    label: str,
    program: Optional[str] = None,
    program_arguments: Optional[List[str]] = None,
    run_at_load: bool = False,
    keep_alive: bool = False,
    start_interval: Optional[int] = None,
    working_directory: Optional[str] = None,
    environment_variables: Optional[Dict[str, str]] = None,
    stdout_path: Optional[str] = None,
    stderr_path: Optional[str] = None,
    launch_only_once: bool = False,
    keep_alive_exit_timeout: Optional[int] = None,
    watch_paths: Optional[List[str]] = None,
    queue_directories: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a launchd plist dictionary.

    Args:
        label: Unique identifier for the job
        program: Program to run (alternative to program_arguments)
        program_arguments: Arguments to the program
        run_at_load: Run immediately when loaded
        keep_alive: Restart if process exits
        start_interval: Run every N seconds
        working_directory: Working directory
        environment_variables: Environment variables
        stdout_path: Path for stdout
        stderr_path: Path for stderr
        launch_only_once: Only launch once
        keep_alive_exit_timeout: Exit timeout for keep-alive
        watch_paths: Paths to watch for changes
        queue_directories: Directories to monitor

    Returns:
        Dictionary suitable for plistlib.dump
    """
    plist = {
        'Label': label,
    }

    if program:
        plist['Program'] = program

    if program_arguments:
        plist['ProgramArguments'] = program_arguments

    if run_at_load:
        plist['RunAtLoad'] = True

    if keep_alive:
        plist['KeepAlive'] = True
        if keep_alive_exit_timeout:
            plist['KeepAlive'] = {'SuccessfulExit': False}

    if start_interval:
        plist['StartInterval'] = start_interval

    if working_directory:
        plist['WorkingDirectory'] = working_directory

    if environment_variables:
        plist['EnvironmentVariables'] = environment_variables

    if stdout_path:
        plist['StandardOutPath'] = stdout_path

    if stderr_path:
        plist['StandardErrorPath'] = stderr_path

    if launch_only_once:
        plist['LaunchOnlyOnce'] = True

    if watch_paths:
        plist['WatchPaths'] = watch_paths

    if queue_directories:
        plist['QueueDirectories'] = queue_directories

    return plist


def write_plist(plist_path: str, plist_data: Dict[str, Any]) -> bool:
    """
    Write a plist file.

    Args:
        plist_path: Path to write
        plist_data: Dictionary to write

    Returns:
        True if writing succeeded
    """
    try:
        Path(plist_path).parent.mkdir(parents=True, exist_ok=True)

        with open(plist_path, 'wb') as f:
            plistlib.dump(plist_data, f)

        return True
    except Exception as e:
        return False


def bootstrap(user: bool = True) -> bool:
    """
    Bootstrap the launchd domain.

    Args:
        user: Bootstrap user domain

    Returns:
        True if bootstrap succeeded
    """
    try:
        if user:
            result = _run_launchctl(['bootstrap', 'gui/$(id -u)', \
                    os.path.expanduser('~/Library/LaunchAgents')])
        else:
            result = _run_launchctl(['bootstrap', 'system', \
                    '/Library/LaunchDaemons'], user=False)
        return result.returncode == 0
    except LaunchdError:
        return False


def get_user_agents_dir() -> Path:
    """
    Get the user LaunchAgents directory.

    Returns:
        Path to ~/Library/LaunchAgents
    """
    return Path.home() / 'Library' / 'LaunchAgents'


def get_system_agents_dir() -> Path:
    """
    Get the system-wide LaunchAgents directory.

    Returns:
        Path to /Library/LaunchAgents
    """
    return Path('/Library/LaunchAgents')


def get_daemons_dir() -> Path:
    """
    Get the system Daemons directory.

    Returns:
        Path to /Library/LaunchDaemons
    """
    return Path('/Library/LaunchDaemons')


def find_user_plists() -> List[Path]:
    """
    Find all user LaunchAgent plist files.

    Returns:
        List of plist paths
    """
    agents_dir = get_user_agents_dir()

    if not agents_dir.exists():
        return []

    plists = []
    for item in agents_dir.glob('*.plist'):
        plists.append(item)

    return plists


def reload_plist(plist_path: str, user: bool = True) -> bool:
    """
    Reload a plist (unload then load).

    Args:
        plist_path: Path to the plist
        user: Reload for current user

    Returns:
        True if reload succeeded
    """
    success = unload(plist_path, user=user)
    if not success:
        return False

    # Brief pause to ensure cleanup
    time.sleep(0.5)

    return load(plist_path, user=user)
