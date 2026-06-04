#!/usr/bin/env python3
"""
macOS: Homebrew package management.

Provides Homebrew installation, upgrade, and management capabilities.
"""

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class BrewPackage:
    """Information about a Homebrew package."""
    name: str
    version: str
    installed: bool
    description: str
    outdated: bool = False


class BrewError(Exception):
    """Exception raised for Homebrew operations."""
    pass


def is_available() -> bool:
    """
    Check if Homebrew is installed.

    Returns:
        True if Homebrew is installed
    """
    return shutil.which('brew') is not None


def _run_brew(args: List[str]) -> subprocess.CompletedProcess:
    """
    Run a Homebrew command.

    Args:
        args: Arguments to pass to brew

    Returns:
        CompletedProcess result
    """
    cmd = ['brew'] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            raise BrewError(f"brew {' '.join(args)} failed: {result.stderr}")

        return result

    except subprocess.TimeoutExpired:
        raise BrewError(f"brew {' '.join(args)} timed out")


def list_installed(formulae: bool = True, casks: bool = True) -> List[BrewPackage]:
    """
    List installed Homebrew packages.

    Args:
        formulae: Include Homebrew formulae
        casks: Include Homebrew casks

    Returns:
        List of BrewPackage objects
    """
    args = ['list', '--versions']

    if formulae and not casks:
        args.append('--formulae')
    elif casks and not formulae:
        args.append('--casks')
    else:
        args.extend(['--formulae', '--casks'])

    result = _run_brew(args)

    packages = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                version = parts[1]
                description = ' '.join(parts[2:]) if len(parts) > 2 else ''

                packages.append(BrewPackage(
                    name=name,
                    version=version,
                    installed=True,
                    description=description,
                ))

    return packages


def install(package_name: str, formula: bool = True, \
            options: Optional[List[str]] = None) -> bool:
    """
    Install a Homebrew package.

    Args:
        package_name: Name of package to install
        formula: Treat as formula (vs cask)
        options: Additional brew install options

    Returns:
        True if installation succeeded
    """
    args = ['install']

    if options:
        args.extend(options)

    args.append(package_name)

    try:
        _run_brew(args)
        return True
    except BrewError:
        return False


def uninstall(package_name: str, formula: bool = True, \
              force: bool = False) -> bool:
    """
    Uninstall a Homebrew package.

    Args:
        package_name: Name of package to uninstall
        formula: Treat as formula (vs cask)
        force: Force uninstall

    Returns:
        True if uninstallation succeeded
    """
    args = ['uninstall']

    if force:
        args.append('--force')

    args.append(package_name)

    try:
        _run_brew(args)
        return True
    except BrewError:
        return False


def upgrade(package_name: Optional[str] = None) -> bool:
    """
    Upgrade Homebrew packages.

    Args:
        package_name: Specific package to upgrade, or None for all

    Returns:
        True if upgrade succeeded
    """
    args = ['upgrade']

    if package_name:
        args.append(package_name)

    try:
        _run_brew(args)
        return True
    except BrewError:
        return False


def search(query: str, formula: bool = True, cask: bool = True) -> List[str]:
    """
    Search for Homebrew packages.

    Args:
        query: Search query
        formula: Search formulae
        cask: Search casks

    Returns:
        List of package names
    """
    args = ['search', query]

    if formula and not cask:
        args.append('--formulae')
    elif cask and not formula:
        args.append('--casks')

    result = _run_brew(args)

    packages = []
    for line in result.stdout.strip().split('\n'):
        if line and not line.startswith('==>'):
            packages.append(line.strip())

    return packages


def info(package_name: str, formula: bool = True) -> Dict[str, Any]:
    """
    Get information about a package.

    Args:
        package_name: Name of package
        formula: Treat as formula

    Returns:
        Dictionary with package information
    """
    args = ['info']

    if formula:
        args.append('--formulae')
    else:
        args.append('--casks')

    args.append(package_name)

    result = _run_brew(args)

    info_dict = {
        'name': package_name,
        'description': '',
        'versions': [],
        'homepage': '',
        'dependencies': [],
    }

    lines = result.stdout.split('\n')
    for line in lines:
        if line.startswith('==> '):
            info_dict['description'] = line[4:]
        elif 'homepage:' in line.lower():
            info_dict['homepage'] = line.split(': ', 1)[-1].strip()

    return info_dict


def outdated() -> List[Dict[str, str]]:
    """
    List outdated packages.

    Returns:
        List of dicts with 'name', 'current_version', 'latest_version'
    """
    result = _run_brew(['outdated', '--format=json'])

    try:
        data = json.loads(result.stdout)
        return data
    except (json.JSONDecodeError, KeyError) as e:
        # Fallback to parsing text output
        outdated_list = []
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('==>'):
                parts = line.split()
                if len(parts) >= 3:
                    outdated_list.append({
                        'name': parts[0],
                        'current_version': parts[1],
                        'latest_version': parts[2],
                    })
        return outdated_list


def cleanup(dry_run: bool = True) -> List[str]:
    """
    Clean up old Homebrew installations.

    Args:
        dry_run: Just show what would be cleaned

    Returns:
        List of items that would be/were cleaned
    """
    args = ['cleanup', '--prune=all']

    if dry_run:
        args.append('--dry-run')

    result = _run_brew(args)

    items = []
    for line in result.stdout.strip().split('\n'):
        if line.strip() and not line.startswith('==>'):
            items.append(line.strip())

    return items


def doctor() -> Dict[str, Any]:
    """
    Run Homebrew doctor check.

    Returns:
        Dictionary with warnings and errors
    """
    result = _run_brew(['doctor'])

    return {
        'success': result.returncode == 0,
        'output': result.stdout,
        'warnings': [],
        'errors': [],
    }


def update() -> bool:
    """
    Update Homebrew and all formulae.

    Returns:
        True if update succeeded
    """
    try:
        _run_brew(['update'])
        return True
    except BrewError:
        return False


def autoremove() -> int:
    """
    Remove unused dependencies.

    Returns:
        Number of packages removed
    """
    result = _run_brew(['autoremove'])

    # Parse output for count
    match = re.search(r'Removing (\d+) packages?', result.stdout)
    if match:
        return int(match.group(1))
    return 0


def get_cask_path(cask_name: str) -> Optional[str]:
    """
    Get the installation path for a cask.

    Args:
        cask_name: Name of the cask

    Returns:
        Path to installed application, or None
    """
    info_result = _run_brew(['info', '--cask', cask_name])

    for line in info_result.stdout.split('\n'):
        if '/Applications/' in line or '~/Applications/' in line:
            path = line.strip()
            path = os.path.expanduser(path)
            return path

    return None


if __name__ != "__main__":
    pass
