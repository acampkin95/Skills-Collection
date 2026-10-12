#!/usr/bin/env python3
"""
macOS: System information and diagnostics.

Gathers system information, hardware details, and diagnostic data.
"""

import subprocess
import os
import re
import json
import plistlib
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class HardwareInfo:
    """System hardware information."""
    model_name: str
    model_identifier: str
    chip: str
    cpu_cores: int
    cpu_threads: int
    memory_gb: float
    boot_rom_version: str
    smc_version: str


@dataclass
class SoftwareInfo:
    """System software information."""
    os_name: str
    os_version: str
    os_build: str
    kernel_version: str
    boot_time: str
    uptime_seconds: float
    secure_boot: bool


@dataclass
class DiskInfo:
    """Disk information."""
    device: str
    size_gb: float
    free_gb: float
    mount_point: str
    filesystem: str
    smart_status: str


@dataclass
class NetworkInfo:
    """Network interface information."""
    interface: str
    ip_address: Optional[str]
    mac_address: Optional[str]
    status: str
    mtu: int


@dataclass
class ProcessInfo:
    """Process information."""
    pid: int
    name: str
    command: str
    cpu_percent: float
    memory_mb: float


class SystemInfoError(Exception):
    """Exception raised for system info operations."""
    pass


def _run_command(
    args: List[str],
    timeout: int = 30,
) -> subprocess.CompletedProcess:
    """
    Run a system command.

    Args:
        args: Command arguments
        timeout: Command timeout

    Returns:
        CompletedProcess result
    """
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result
    except subprocess.TimeoutExpired:
        raise SystemInfoError(f"Command timed out: {' '.join(args)}")


def get_hardware_info() -> HardwareInfo:
    """
    Get hardware information.

    Returns:
        HardwareInfo object
    """
    # Get model info
    result = _run_command(['sysctl', '-n', 'hw.model'])
    model_identifier = result.stdout.strip()

    # Get model name
    result = _run_command(['sw_vers', '-productName'])
    os_name = result.stdout.strip()

    # Get chip info (Apple Silicon)
    result = _run_command(['sysctl', '-n', 'machdep.cpu.brand_string'])
    chip = result.stdout.strip()

    # Get CPU cores
    result = _run_command(['sysctl', '-n', 'hw.ncpu'])
    cpu_cores = int(result.stdout.strip())

    # Get logical cores
    result = _run_command(['sysctl', '-n', 'hw.physicalcpu'])
    physical_cores = int(result.stdout.strip())

    # Get memory
    result = _run_command(['sysctl', '-n', 'hw.memsize'])
    memory_bytes = int(result.stdout.strip())
    memory_gb = memory_bytes / (1024 ** 3)

    # Get boot ROM and SMC versions
    result = _run_command(['system_profiler', 'SPHardwareDataType', '-json'])
    try:
        data = json.loads(result.stdout)
        hw_data = data.get('SPHardwareDataType', [{}])[0]
        boot_rom = hw_data.get('Boot_ROM_Version', '')
        smc = hw_data.get('SMC_Version', '')
    except (json.JSONDecodeError, IndexError):
        boot_rom = ''
        smc = ''

    return HardwareInfo(
        model_name='Mac',
        model_identifier=model_identifier,
        chip=chip,
        cpu_cores=physical_cores,
        cpu_threads=cpu_cores,
        memory_gb=round(memory_gb, 2),
        boot_rom_version=boot_rom,
        smc_version=smc,
    )


def get_software_info() -> SoftwareInfo:
    """
    Get software information.

    Returns:
        SoftwareInfo object
    """
    # OS name
    result = _run_command(['sw_vers', '-productName'])
    os_name = result.stdout.strip()

    # OS version
    result = _run_command(['sw_vers', '-productVersion'])
    os_version = result.stdout.strip()

    # OS build
    result = _run_command(['sw_vers', '-buildVersion'])
    os_build = result.stdout.strip()

    # Kernel version
    result = _run_command(['uname', '-r'])
    kernel_version = result.stdout.strip()

    # Uptime
    result = _run_command(['uptime'])
    match = re.search(r'up (.+?),', result.stdout)
    boot_time = match.group(1) if match else 'unknown'

    # Uptime in seconds
    result = _run_command(['sysctl', '-n', 'kern.boottime'])
    match = re.search(r'\{ sec = (\d+)', result.stdout)
    if match:
        boot_epoch = int(match.group(1))
        import time
        uptime = time.time() - boot_epoch
    else:
        uptime = 0

    # Secure boot status
    result = _run_command(['spctl', 'status'])
    secure_boot = 'enabled' in result.stdout.lower() or \
                  'require' in result.stdout.lower()

    return SoftwareInfo(
        os_name=os_name,
        os_version=os_version,
        os_build=os_build,
        kernel_version=kernel_version,
        boot_time=boot_time,
        uptime_seconds=uptime,
        secure_boot=secure_boot,
    )


def get_disks() -> List[DiskInfo]:
    """
    Get disk information.

    Returns:
        List of DiskInfo objects
    """
    disks = []

    # Use diskutil list
    result = _run_command(['diskutil', 'list', '-plist'])
    try:
        data = plistlib.loads(result.stdout.encode())

        for disk in data.get('AllDisks', []):
            info_result = _run_command(['diskutil', 'info', '-plist', disk])

            try:
                info_data = plistlib.loads(info_result.stdout.encode())

                size_bytes = info_data.get('DiskSize', 0)
                free_bytes = info_data.get('FreeSpace', 0)

                disks.append(DiskInfo(
                    device=info_data.get('DeviceIdentifier', ''),
                    size_gb=round(size_bytes / (1024 ** 3), 2),
                    free_gb=round(free_bytes / (1024 ** 3), 2),
                    mount_point=info_data.get('MountPoint', ''),
                    filesystem=info_data.get('FilesystemType', ''),
                    smart_status=info_data.get('SMARTStatus', 'Unknown'),
                ))
            except Exception as e:
                continue

    except Exception as e:
        pass

    return disks


def get_battery_info() -> Dict[str, Any]:
    """
    Get battery information.

    Returns:
        Dictionary with battery status
    """
    result = _run_command(['pmset', '-g', 'battery'])

    info = {
        'connected': False,
        'charging': False,
        'percentage': 0,
        'time_remaining': None,
        'health': 'Unknown',
    }

    for line in result.stdout.split('\n'):
        if 'AC' in line:
            info['connected'] = True
        if 'charging' in line.lower():
            info['charging'] = True
        match = re.search(r'(\d+)%', line)
        if match:
            info['percentage'] = int(match.group(1))

    return info


def get_network_info() -> List[NetworkInfo]:
    """
    Get network interface information.

    Returns:
        List of NetworkInfo objects
    """
    interfaces = []

    result = _run_command(['ifconfig'])

    current_interface = None
    current_info = {}

    for line in result.stdout.split('\n'):
        if line and not line.startswith(' ') and not line.startswith('\t'):
            if current_interface and current_info:
                interfaces.append(NetworkInfo(**current_info))

            current_interface = line.rstrip(':')
            current_info = {
                'interface': current_interface,
                'ip_address': None,
                'mac_address': None,
                'status': 'unknown',
                'mtu': 0,
            }
        elif current_interface:
            if 'inet ' in line:
                match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    current_info['ip_address'] = match.group(1)
            elif 'ether ' in line:
                match = re.search(r'ether ([0-9a-f:]+)', line)
                if match:
                    current_info['mac_address'] = match.group(1)
            elif 'status: ' in line:
                match = re.search(r'status: (\w+)', line)
                if match:
                    current_info['status'] = match.group(1)

    if current_interface and current_info:
        interfaces.append(NetworkInfo(**current_info))

    return [i for i in interfaces if i.ip_address]


def get_top_processes(limit: int = 10) -> List[ProcessInfo]:
    """
    Get top processes by CPU usage.

    Args:
        limit: Maximum number of processes

    Returns:
        List of ProcessInfo objects
    """
    result = _run_command(['ps', 'aux', '-r', '-c', '-o', \
                           'pid,comm,%cpu,%mem,args'])

    processes = []
    for line in result.stdout.split('\n')[1:limit+1]:
        if line:
            parts = line.split()
            if len(parts) >= 5:
                try:
                    processes.append(ProcessInfo(
                        pid=int(parts[0]),
                        name=parts[1],
                        command=' '.join(parts[4:]) if len(parts) > 4 else '',
                        cpu_percent=float(parts[2]),
                        memory_mb=float(parts[3]),
                    ))
                except (ValueError, IndexError):
                    continue

    return processes


def get_logged_in_users() -> List[Dict[str, str]]:
    """
    Get list of logged in users.

    Returns:
        List of user information dictionaries
    """
    result = _run_command(['who', '-H'])

    users = []
    for line in result.stdout.split('\n')[1:]:
        if line:
            parts = line.split()
            if len(parts) >= 3:
                users.append({
                    'user': parts[0],
                    'terminal': parts[1],
                    'date': parts[2],
                    'time': parts[3],
                })

    return users


def get_running_services() -> List[Dict[str, str]]:
    """
    Get running system services.

    Returns:
        List of service information
    """
    result = _run_command(['launchctl', 'list'])

    services = []
    for line in result.stdout.split('\n')[1:]:
        if line and not line.startswith('"'):
            parts = line.split(None, 2)
            if len(parts) >= 3:
                pid = parts[0] if parts[0] != '-' else None
                services.append({
                    'label': parts[2].strip('"') if len(parts) > 2 else '',
                    'pid': pid,
                    'status': parts[1],
                })

    return services


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.

    Returns:
        Dictionary with all system info
    """
    hardware = get_hardware_info()
    software = get_software_info()
    disks = get_disks()
    network = get_network_info()
    battery = get_battery_info()

    return {
        'hardware': hardware.__dict__,
        'software': software.__dict__,
        'disks': [d.__dict__ for d in disks],
        'network': [n.__dict__ for n in network],
        'battery': battery,
        'timestamp': subprocess.run(
            ['date', '+%Y-%m-%d %H:%M:%S'],
            capture_output=True,
            text=True,
        ).stdout.strip(),
    }


def run_diagnostics() -> Dict[str, Any]:
    """
    Run system diagnostics.

    Returns:
        Dictionary with diagnostic results
    """
    diagnostics = {
        'storage': {'status': 'ok', 'details': None},
        'memory': {'status': 'ok', 'details': None},
        'network': {'status': 'ok', 'details': None},
        'battery': {'status': 'ok', 'details': None},
        'security': {'status': 'ok', 'details': None},
    }

    # Check storage
    disks = get_disks()
    for disk in disks:
        if disk.free_gb < 5:  # Less than 5GB free
            diagnostics['storage'] = {
                'status': 'warning',
                'details': f'Low disk space on {disk.mount_point}: \
                           {disk.free_gb:.1f}GB free',
            }
            break

    # Check memory pressure
    result = _run_command(['vm_stat'])
    free_pages = 0
    total_pages = 0
    for line in result.stdout.split('\n'):
        if 'Pages free:' in line:
            match = re.search(r'(\d+)', line)
            if match:
                free_pages = int(match.group(1))
        elif 'Pages speculative:' in line:
            match = re.search(r'(\d+)', line)
            if match:
                free_pages += int(match.group(1))
        elif 'Pages total:' in line:
            match = re.search(r'(\d+)', line)
            if match:
                total_pages = int(match.group(1))

    if total_pages > 0 and free_pages / total_pages < 0.1:
        diagnostics['memory'] = {
            'status': 'warning',
            'details': 'Low available memory',
        }

    # Check network
    network = get_network_info()
    if not any(n.status == 'active' for n in network):
        diagnostics['network'] = {
            'status': 'error',
            'details': 'No active network connection',
        }

    # Check battery
    battery = get_battery_info()
    if battery['percentage'] < 20 and not battery['charging']:
        diagnostics['battery'] = {
            'status': 'warning',
            'details': f'Battery at {battery["percentage"]}%',
        }

    # Check security
    if not software.secure_boot:
        diagnostics['security'] = {
            'status': 'warning',
            'details': 'Secure boot may not be fully enabled',
        }

    return diagnostics


if __name__ != "__main__":
    pass
