#!/usr/bin/env python3
"""
macOS: Xcode and iOS development tools.

Provides Xcode command line tools management and iOS development utilities.
"""

import subprocess
import shutil
import os
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class XcodeSDK:
    """Information about an Xcode SDK."""
    name: str
    path: str
    version: str
    platform: str


@dataclass
class XcodeTool:
    """Information about an Xcode command line tool."""
    name: str
    path: str
    version: Optional[str]


class XcodeError(Exception):
    """Exception raised for Xcode operations."""
    pass


def is_xcode_installed() -> bool:
    """
    Check if Xcode is installed.

    Returns:
        True if Xcode is installed
    """
    return shutil.which('xcodebuild') is not None


def is_xcode_cli_installed() -> bool:
    """
    Check if Xcode command line tools are installed.

    Returns:
        True if CLI tools are installed
    """
    result = subprocess.run(
        ['xcode-select', '-p'],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def install_cli_tools() -> bool:
    """
    Install Xcode command line tools.

    Returns:
        True if installation succeeded
    """
    try:
        result = subprocess.run(
            ['xcode-select', '--install'],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        return False


def get_xcode_path() -> Optional[str]:
    """
    Get the active Xcode path.

    Returns:
        Path to active Xcode, or None
    """
    result = subprocess.run(
        ['xcode-select', '-p'],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        path = result.stdout.strip()
        # Navigate up to Xcode app
        return str(Path(path).parent.parent.parent)

    return None


def set_xcode_path(path: str) -> bool:
    """
    Set the active Xcode path.

    Args:
        path: Path to Xcode app

    Returns:
        True if setting succeeded
    """
    try:
        result = subprocess.run(
            ['xcode-select', '-s', path],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        return False


def list_xcodes() -> List[Dict[str, str]]:
    """
    List available Xcode installations.

    Returns:
        List of dictionaries with 'path' and 'version'
    """
    xcodes = []

    # Check /Applications
    apps_dir = Path('/Applications')
    if apps_dir.exists():
        for item in apps_dir.iterdir():
            if item.name.startswith('Xcode') and item.name.endswith('.app'):
                version = item.name.replace('Xcode ', '').replace('.app', '')
                xcodes.append({
                    'name': item.name,
                    'path': str(item),
                    'version': version,
                })

    # Check ~/Applications
    home_apps = Path.home() / 'Applications'
    if home_apps.exists():
        for item in home_apps.iterdir():
            if item.name.startswith('Xcode') and item.name.endswith('.app'):
                version = item.name.replace('Xcode ', '').replace('.app', '')
                xcodes.append({
                    'name': item.name,
                    'path': str(item),
                    'version': version,
                })

    return xcodes


def list_sdks() -> List[XcodeSDK]:
    """
    List available Xcode SDKs.

    Returns:
        List of XcodeSDK objects
    """
    if not is_xcode_installed():
        raise XcodeError("Xcode is not installed")

    sdks = []

    result = subprocess.run(
        ['xcodebuild', '-showsdks'],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return []

    for line in result.stdout.split('\n'):
        if 'SDK' in line:
            match = re.search(r'([-a-zA-Z0-9.]+)\s+\(([-a-zA-Z0-9.]+)\):\s+(.+)', line)
            if match:
                platform = match.group(1)
                version = match.group(2)
                path = match.group(3)

                # Extract just the SDK name
                name_match = re.search(r'([-a-zA-Z0-9.]+)\.sdk', path)
                name = name_match.group(1) if name_match else platform

                sdks.append(XcodeSDK(
                    name=name,
                    path=path,
                    version=version,
                    platform=platform,
                ))

    return sdks


def get_active_sdk() -> Optional[XcodeSDK]:
    """
    Get the active SDK for building.

    Returns:
        XcodeSDK object, or None
    """
    result = subprocess.run(
        ['xcrun', '--sdk', 'macosx', '--show-sdk-path'],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        path = result.stdout.strip()
        sdk_name = Path(path).stem

        return XcodeSDK(
            name=sdk_name,
            path=path,
            version='',
            platform='macOS',
        )

    return None


def build_project(
    project_path: str,
    scheme: Optional[str] = None,
    configuration: str = 'Debug',
    destination: Optional[str] = None,
    clean: bool = False,
) -> Dict[str, Any]:
    """
    Build an Xcode project or workspace.

    Args:
        project_path: Path to .xcodeproj or .xcworkspace
        scheme: Build scheme (auto-detected if not provided)
        configuration: Build configuration
        destination: Build destination
        clean: Clean before building

    Returns:
        Dictionary with build results
    """
    args = ['xcodebuild']

    if clean:
        args.append('clean')

    args.extend([
        'build',
        '-project', project_path,
        '-configuration', configuration,
    ])

    if scheme:
        args.extend(['-scheme', scheme])

    if destination:
        args.extend(['-destination', destination])
    else:
        args.extend(['-destination', 'generic/platform=macOS'])

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=1800,
    )

    return {
        'success': result.returncode == 0,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode,
    }


def run_tests(
    project_path: str,
    scheme: str,
    destination: Optional[str] = None,
    only_test: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run Xcode tests.

    Args:
        project_path: Path to project
        scheme: Test scheme
        destination: Test destination
        only_test: Specific test to run

    Returns:
        Dictionary with test results
    """
    args = [
        'xcodebuild',
        'test',
        '-project', project_path,
        '-scheme', scheme,
    ]

    if destination:
        args.extend(['-destination', destination])
    else:
        args.extend(['-destination', 'platform=macOS'])

    if only_test:
        args.extend(['-only-testing:', only_test])

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=1800,
    )

    return {
        'success': result.returncode == 0,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode,
    }


def list_simulators() -> List[Dict[str, Any]]:
    """
    List available iOS/macOS simulators.

    Returns:
        List of simulator information dictionaries
    """
    result = subprocess.run(
        ['xcrun', 'simctl', 'list', '--json'],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return []

    import json
    data = json.loads(result.stdout)

    simulators = []
    for runtime, devices in data.get('devices', {}).items():
        for device in devices:
            simulators.append({
                'name': device.get('name', ''),
                'udid': device.get('udid', ''),
                'runtime': runtime,
                'is_available': device.get('isAvailable', False),
                'device_type': device.get('deviceType', ''),
            })

    return simulators


def get_swift_version() -> Optional[str]:
    """
    Get the installed Swift version.

    Returns:
        Swift version string, or None
    """
    result = subprocess.run(
        ['swift', '--version'],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        match = re.search(r'Swift version ([\d.]+)', result.stdout)
        if match:
            return match.group(1)

    return None


def get_xcode_version() -> Optional[str]:
    """
    Get the active Xcode version.

    Returns:
        Xcode version string, or None
    """
    result = subprocess.run(
        ['xcodebuild', '-version'],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        match = re.search(r'Xcode (\d+\.\d+)', result.stdout)
        if match:
            return match.group(1)

    return None


def notarize_app(
    app_path: str,
    bundle_id: str,
    apple_id: Optional[str] = None,
    password: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Submit an app for notarization.

    Args:
        app_path: Path to the .app or .zip
        bundle_id: Bundle identifier
        apple_id: Apple ID for authentication
        password: App-specific password

    Returns:
        Dictionary with notarization status
    """
    # Check for existing altool
    altool_path = shutil.which('altool') or shutil.which('xcrun altool')

    if not altool_path:
        raise XcodeError("altool not found. Install Xcode CLI tools.")

    args = [
        'xcrun', 'altool',
        '--notarize-app',
        '--primary-bundle-id', bundle_id,
        '--file', app_path,
        '--username', apple_id or os.environ.get('APPLE_ID', ''),
        '--password', password or os.environ.get('APPLE_APP_PASSWORD', ''),
    ]

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=600,
    )

    return {
        'success': result.returncode == 0,
        'output': result.stdout,
        'errors': result.stderr,
    }


if __name__ != "__main__":
    pass
